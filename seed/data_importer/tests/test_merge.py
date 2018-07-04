# !/usr/bin/env python
# encoding: utf-8
"""
:copyright (c) 2014 - 2018, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Department of Energy) and contributors. All rights reserved.  # NOQA
:author
"""
from datetime import datetime

from django.utils import timezone

from seed.data_importer.tasks import _match_properties_and_taxlots, save_state_match
from seed.landing.models import SEEDUser as User
from seed.models import (
    PropertyState,
    PropertyView,
    TaxLotState,
    ImportFile,
    ImportRecord,
    PropertyAuditLog,
    DATA_STATE_MAPPING,
    MERGE_STATE_MERGED,
    TaxLotProperty,
    TaxLotView,
)
from seed.test_helpers.fake import (
    FakeCycleFactory,
    FakePropertyFactory,
    FakePropertyStateFactory,
    FakeTaxLotStateFactory,
    FakeTaxLotViewFactory,
    FakePropertyViewFactory,
)
from seed.tests.util import DeleteModelsTestCase
from seed.utils.organizations import create_organization

COLUMNS_TO_SEND = [
    'project_id',
    'address_line_1',
    'city',
    'state_province',
    'postal_code',
    'pm_parent_property_id',
    # 'calculated_taxlot_ids',
    # 'primary',
    'extra_data_field',
    'jurisdiction_tax_lot_id'
]


# These tests mostly use V2.1 API except for when writing back to the API for updates
class PropertyViewTests(DeleteModelsTestCase):
    def setUp(self):
        user_details = {
            'username': 'test_user@demo.com',
            'password': 'test_pass',
            'email': 'test_user@demo.com'
        }
        self.user = User.objects.create_superuser(**user_details)
        self.org, self.org_user, _ = create_organization(self.user)
        self.cycle_factory = FakeCycleFactory(organization=self.org, user=self.user)
        self.cycle = self.cycle_factory.get_cycle(
            start=datetime(2010, 10, 10, tzinfo=timezone.get_current_timezone())
        )
        self.property_factory = FakePropertyFactory(organization=self.org)
        self.property_state_factory = FakePropertyStateFactory(organization=self.org)
        self.property_view_factory = FakePropertyViewFactory(organization=self.org, cycle=self.cycle)
        self.taxlot_state_factory = FakeTaxLotStateFactory(organization=self.org)
        self.taxlot_view_factory = FakeTaxLotViewFactory(organization=self.org, cycle=self.cycle)

        # create 10 addresses that are exactly the same
        import_record = ImportRecord.objects.create(super_organization=self.org)
        self.import_file = ImportFile.objects.create(
            import_record=import_record,
            cycle=self.cycle,
        )

    def test_match_properties_and_taxlots_with_address(self):
        # create an ImportFile for testing purposes. Seems like we would want to run this matching just on a
        # list of properties and taxlots.
        #
        # This emulates importing the following
        #   Address,                Jurisdiction Tax Lot
        #   742 Evergreen Terrace,  100;101;110;111

        lot_numbers = '100;101;110;111'
        for i in range(10):
            self.property_state_factory.get_property_state(
                address_line_1='742 Evergreen Terrace',
                lot_number=lot_numbers,
                import_file_id=self.import_file.id,
                data_state=DATA_STATE_MAPPING,
            )

        for lot_number in lot_numbers.split(';'):
            self.taxlot_state_factory.get_taxlot_state(
                address_line_1=None,
                jurisdiction_tax_lot_id=lot_number,
                import_file_id=self.import_file.id,
                data_state=DATA_STATE_MAPPING,
            )

        for ps in PropertyState.objects.filter(organization=self.org):
            print "%s -- %s -- %s" % (ps.lot_number, ps.import_file_id, ps.address_line_1)
            # pv = PropertyView.objects.get(state=ps, cycle=self.cycle)
            # TaxLotProperty.objects.filter()

        for tl in TaxLotState.objects.filter(organization=self.org):
            print "%s -- %s" % (tl.import_file_id, tl.jurisdiction_tax_lot_id)

        # for tlm in TaxLotProperty.objects.filter()
        _match_properties_and_taxlots(self.import_file.id)

        for pv in PropertyView.objects.filter(state__organization=self.org):
            print "%s -- %s" % (pv.state, pv.cycle)

        # should only have 1 PropertyView and 4 taxlot views
        self.assertEqual(PropertyView.objects.filter(state__organization=self.org).count(), 1)
        self.assertEqual(TaxLotView.objects.filter(state__organization=self.org).count(), 4)
        pv = PropertyView.objects.filter(state__organization=self.org).first()

        # there should be 4 relationships in the TaxLotProperty associated with view, one each for the taxlots defined
        self.assertEqual(TaxLotProperty.objects.filter(property_view_id=pv).count(), 4)

    def test_match_properties_and_taxlots_with_address_no_lot_number(self):
        # create an ImportFile for testing purposes. Seems like we would want to run this matching just on a
        # list of properties and taxlots.
        #
        # This emulates importing the following
        #   Address,                Jurisdiction Tax Lot
        #   742 Evergreen Terrace,  100
        #   742 Evergreen Terrace,  101
        #   742 Evergreen Terrace,  110
        #   742 Evergreen Terrace,  111

        lot_numbers = '100;101;110;111'
        for lot_number in lot_numbers.split(';'):
            self.property_state_factory.get_property_state(
                address_line_1='742 Evergreen Terrace',
                lot_number=lot_number,
                import_file_id=self.import_file.id,
                data_state=DATA_STATE_MAPPING,
            )

            self.taxlot_state_factory.get_taxlot_state(
                address_line_1=None,
                jurisdiction_tax_lot_id=lot_number,
                import_file_id=self.import_file.id,
                data_state=DATA_STATE_MAPPING,
            )

        for ps in PropertyState.objects.filter(organization=self.org):
            print "%s -- %s -- %s" % (ps.lot_number, ps.import_file_id, ps.address_line_1)

        for tl in TaxLotState.objects.filter(organization=self.org):
            print "%s -- %s" % (tl.import_file_id, tl.jurisdiction_tax_lot_id)

        _match_properties_and_taxlots(self.import_file.id)

        for pv in PropertyView.objects.filter(state__organization=self.org):
            print "%s -- %s" % (pv.state, pv.cycle)

        # should only have 1 PropertyView and 4 taxlot views
        self.assertEqual(PropertyView.objects.filter(state__organization=self.org).count(), 1)
        self.assertEqual(TaxLotView.objects.filter(state__organization=self.org).count(), 4)
        pv = PropertyView.objects.filter(state__organization=self.org).first()

        # there should be 4 relationships in the TaxLotProperty associated with view, one each for the taxlots defined
        self.assertEqual(TaxLotProperty.objects.filter(property_view_id=pv).count(), 4)

    def test_match_properties_and_taxlots_with_ubid(self):
        # create an ImportFile for testing purposes. Seems like we would want to run this matching just on a
        # list of properties and taxlots.
        #
        # This emulates importing the following
        #   UBID,    Jurisdiction Tax Lot
        #   ubid_100,     lot_1
        #   ubid_101,     lot_1
        #   ubid_110,     lot_1
        #   ubid_111,     lot_1

        ids = [('ubid_100', 'lot_1'), ('ubid_101', 'lot_1'), ('ubid_110', 'lot_1'), ('ubid_111', 'lot_1')]
        for id in ids:
            self.property_state_factory.get_property_state(
                no_default_data=True,
                ubid=id[0],
                lot_number=id[1],
                import_file_id=self.import_file.id,
                data_state=DATA_STATE_MAPPING,
            )

        self.taxlot_state_factory.get_taxlot_state(
            no_default_data=True,
            jurisdiction_tax_lot_id=ids[0][1],
            import_file_id=self.import_file.id,
            data_state=DATA_STATE_MAPPING,
        )

        for ps in PropertyState.objects.filter(organization=self.org):
            print "%s -- %s -- %s" % (ps.lot_number, ps.import_file_id, ps.ubid)
            # pv = PropertyView.objects.get(state=ps, cycle=self.cycle)
            # TaxLotProperty.objects.filter()

        for tl in TaxLotState.objects.filter(organization=self.org):
            print "%s -- %s" % (tl.import_file_id, tl.jurisdiction_tax_lot_id)

        # for tlm in TaxLotProperty.objects.filter()
        _match_properties_and_taxlots(self.import_file.id)

        for pv in PropertyView.objects.filter(state__organization=self.org):
            print "%s -- %s" % (pv.state.ubid, pv.cycle)

        # should only have 1 PropertyView and 4 taxlot views
        self.assertEqual(PropertyView.objects.filter(state__organization=self.org).count(), 4)
        self.assertEqual(TaxLotView.objects.filter(state__organization=self.org).count(), 1)
        tlv = TaxLotView.objects.filter(state__organization=self.org).first()

        # there should be 4 relationships in the TaxLotProperty associated with view, one each for the taxlots defined
        self.assertEqual(TaxLotProperty.objects.filter(taxlot_view_id=tlv).count(), 4)

    def test_match_properties_and_taxlots_with_custom_id(self):
        # create an ImportFile for testing purposes. Seems like we would want to run this matching just on a
        # list of properties and taxlots.
        #
        # This emulates importing the following
        #   Custom ID 1,    Jurisdiction Tax Lot
        #   custom_100,     lot_1
        #   custom_101,     lot_1
        #   custom_110,     lot_1
        #   custom_111,     lot_1
        ids = [('custom_100', 'lot_1'), ('custom_101', 'lot_1'), ('custom_110', 'lot_1'), ('custom_111', 'lot_1')]
        for id in ids:
            self.property_state_factory.get_property_state(
                no_default_data=True,
                custom_id_1=id[0],
                lot_number=id[1],
                import_file_id=self.import_file.id,
                data_state=DATA_STATE_MAPPING,
            )

        self.taxlot_state_factory.get_taxlot_state(
            no_default_data=True,
            jurisdiction_tax_lot_id=ids[0][1],
            import_file_id=self.import_file.id,
            data_state=DATA_STATE_MAPPING,
        )

        for ps in PropertyState.objects.filter(organization=self.org):
            print "%s -- %s -- %s" % (ps.lot_number, ps.import_file_id, ps.custom_id_1)
            # pv = PropertyView.objects.get(state=ps, cycle=self.cycle)
            # TaxLotProperty.objects.filter()

        for tl in TaxLotState.objects.filter(organization=self.org):
            print "%s -- %s" % (tl.import_file_id, tl.jurisdiction_tax_lot_id)

        # for tlm in TaxLotProperty.objects.filter()
        _match_properties_and_taxlots(self.import_file.id)

        for pv in PropertyView.objects.filter(state__organization=self.org):
            print "%s -- %s" % (pv.state, pv.cycle)

        # should only have 1 PropertyView and 4 taxlot views
        self.assertEqual(PropertyView.objects.filter(state__organization=self.org).count(), 4)
        self.assertEqual(TaxLotView.objects.filter(state__organization=self.org).count(), 1)
        tlv = TaxLotView.objects.filter(state__organization=self.org).first()

        # there should be 4 relationships in the TaxLotProperty associated with view, one each for the taxlots defined
        self.assertEqual(TaxLotProperty.objects.filter(taxlot_view_id=tlv).count(), 4)

    def test_save_state_match(self):
        # create a couple states to merge together
        ps_1 = self.property_state_factory.get_property_state(property_name="this should persist")
        ps_2 = self.property_state_factory.get_property_state(extra_data={"extra_1": "this should exist too"})

        merged_state = save_state_match(ps_1, ps_2)

        self.assertEqual(merged_state.merge_state, MERGE_STATE_MERGED)
        self.assertEqual(merged_state.property_name, ps_1.property_name)
        self.assertEqual(merged_state.extra_data['extra_1'], "this should exist too")

        # verify that the audit log is correct.
        pal = PropertyAuditLog.objects.get(organization=self.org, state=merged_state)
        self.assertEqual(pal.name, 'System Match')
        self.assertEqual(pal.parent_state1, ps_1)
        self.assertEqual(pal.parent_state2, ps_2)
        self.assertEqual(pal.description, 'Automatic Merge')

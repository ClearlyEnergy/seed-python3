# !/usr/bin/env python
# encoding: utf-8
"""
:copyright (c) 2014 - 2018, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Department of Energy) and contributors. All rights reserved.  # NOQA
:author
Tests related to sharing of data between users, orgs, suborgs, etc.
"""
import json

from django.core.urlresolvers import reverse_lazy
from django.test import TestCase

from seed.landing.models import SEEDUser as User
from seed.lib.superperms.orgs.models import (
    Organization,
    ROLE_OWNER,
    ROLE_MEMBER
)
from seed.models import (
    BuildingSnapshot
)


class SharingViewTests(TestCase):
    """
    Tests of the SEED search_buildings
    """

    def setUp(self):
        self.admin_details = {
            'username': 'test_user@demo.com',
            'password': 'test_pass',
            'email': 'test_user@demo.com',
            'show_shared_buildings': True
        }
        self.admin_user = User.objects.create_superuser(**self.admin_details)
        self.parent_org = Organization.objects.create(name='Parent')
        self.parent_org.add_member(self.admin_user, ROLE_OWNER)

        self.eng_user_details = {
            'username': 'eng_owner@demo.com',
            'password': 'eng_pass',
            'email': 'eng_owner@demo.com'
        }
        self.eng_user = User.objects.create_user(**self.eng_user_details)
        self.eng_org = Organization.objects.create(parent_org=self.parent_org,
                                                   name='Engineers')
        self.eng_org.add_member(self.eng_user, ROLE_OWNER)

        self.des_user_details = {
            'username': 'des_owner@demo.com',
            'password': 'des_pass',
            'email': 'des_owner@demo.com'
        }
        self.des_user = User.objects.create_user(**self.des_user_details)
        self.des_org = Organization.objects.create(parent_org=self.parent_org,
                                                   name='Designers')
        self.des_org.add_member(self.des_user, ROLE_MEMBER)

        # self._create_buildings()

    def _search_buildings(self, is_public=False):
        """
        Make a request of the search_buildings view and return the
        json-decoded body.
        """
        url = reverse_lazy("api:v1:search_buildings")
        if is_public:
            url = reverse_lazy("api:v1:public_search")
        post_data = {
            'filter_params': {},
            'number_per_page': BuildingSnapshot.objects.count(),
            'order_by': '',
            'page': 1,
            'q': '',
            'sort_reverse': False,
            'project_id': None,
        }

        response = self.client.post(
            url,
            content_type='application/json',
            data=json.dumps(post_data)
        )
        json_string = response.content
        return json.loads(json_string)

    def test_scenario(self):
        """
        Make sure setUp works.
        """
        self.assertTrue(self.des_org in self.parent_org.child_orgs.all())
        self.assertTrue(self.eng_org in self.parent_org.child_orgs.all())
        self.assertTrue(self.parent_org.is_owner(self.admin_user))
        self.assertFalse(self.parent_org.is_owner(self.eng_user))
        self.assertFalse(self.parent_org.is_owner(self.des_user))
        self.assertFalse(self.des_org.is_owner(self.des_user))
        self.assertTrue(self.des_org.is_member(self.des_user))
        self.assertTrue(self.eng_org.is_owner(self.eng_user))

    # @skip("Fix for new data model")
    # def test_public_viewer(self):
    #     """Public viewer requires no credentials, and should see public fields.

    #     In this case, only postal_code data.
    #     """
    #     results = self._search_buildings(is_public=True)

    #     fields = []

    #     for f in results['buildings']:
    #         fields.extend(list(f.keys()))

    #     fields = list(set(fields))

    #     self.assertListEqual(fields, ['postal_code'])

        # @skip("Fix for new data model")
        # def test_parent_viewer(self):
        #     """
        #     The admin user should be able to see all buildings with all fields.
        #     """
        #     self.client.login(**self.admin_details)
        #
        #     result = self._search_buildings()
        #
        #     self.assertEqual(result['status'], 'success')
        #     self.assertEqual(result['number_returned'],
        #                      BuildingSnapshot.objects.count())
        #     self.assertEqual(len(result['buildings']),
        #                      BuildingSnapshot.objects.count())
        #
        #     # parent org sees all fields on all buildings
        #     for b in result['buildings']:
        #         self.assertTrue(b['property_name'] in
        #                         ('ENG BUILDING', 'DES BUILDING', 'ADMIN BUILDING'))
        #         if b['property_name'] == 'ENG BUILDING':
        #             self.assertEqual(b['address_line_1'],
        #                              '100 Eng St')
        #         elif b['property_name'] == 'DES BUILDING':
        #             self.assertEqual(b['address_line_1'],
        #                              '100 Des St')
        #         elif b['property_name'] == 'ADMIN_BUILDING':
        #             self.assertEqual(b['address_line_1'],
        #                              '100 Admin St')
        #
        # @skip("Fix for new data model")
        # def test_suborg_view_not_shared(self):
        #     """
        #     A suborg user that does not have 'show_shared_buildings' set
        #     should only see their own suborg's buildings.
        #     """
        #     self.assertFalse(self.eng_user.show_shared_buildings)
        #     self.client.login(**self.eng_user_details)
        #     result = self._search_buildings()
        #
        #     self.assertEqual(result['status'], 'success')
        #
        #     expected_count = self.eng_org.building_snapshots.count()
        #     self.assertEqual(result['number_returned'],
        #                      expected_count)
        #     self.assertEqual(len(result['buildings']),
        #                      expected_count)
        #
        #     # eng org only sees own buildings
        #     for b in result['buildings']:
        #         self.assertEqual(b['property_name'], 'ENG BUILDING')
        #         self.assertEqual(b['address_line_1'], '100 Eng St')
        #
        # @skip("Fix for new data model")
        # def test_suborg_view_show_shared(self):
        #     """
        #     A suborg user with 'show_shared_buildings' set should see all buildings
        #     in the org tree, but only the shared fields for buildings outside
        #     the suborg.
        #     """
        #     self.des_user.show_shared_buildings = True
        #     self.des_user.save()
        #     self.client.login(**self.des_user_details)
        #     result = self._search_buildings()
        #
        #     self.assertEqual(result['status'], 'success')
        #
        #     expected_count = BuildingSnapshot.objects.count()
        #     self.assertEqual(result['number_returned'],
        #                      expected_count)
        #     self.assertEqual(len(result['buildings']),
        #                      expected_count)
        #
        #     # des org user should see shared fields
        #     for b in result['buildings']:
        #         # property_name is shared
        #         self.assertTrue(b['property_name'] in
        #                         ('ENG BUILDING', 'DES BUILDING', 'ADMIN BUILDING'))
        #         if b['property_name'] == 'ENG BUILDING':
        #             # address_line_1 is unshared
        #             self.assertTrue('address_line_1' not in b)
        #         elif b['property_name'] == 'DES BUILDING':
        #             self.assertEqual(b['address_line_1'],
        #                              '100 Des St')

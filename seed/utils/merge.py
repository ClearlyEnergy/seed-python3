# !/usr/bin/env python
# encoding: utf-8
"""
:copyright (c) 2014 - 2019, The Regents of the University of California,
through Lawrence Berkeley National Laboratory (subject to receipt of any
required approvals from the U.S. Department of Energy) and contributors.
All rights reserved.  # NOQA
:author
"""

from django.apps import apps
from django.db.models import Subquery

from helix.models import HELIXGreenAssessmentProperty, HelixMeasurement
from seed.lib.merging import merging
from seed.models import (
    AUDIT_IMPORT,
    Column,
    DATA_STATE_MATCHING,
    MERGE_STATE_MERGED,
    MERGE_STATE_UNKNOWN,
    GreenAssessmentURL,
    Note,
    Property,
    PropertyAuditLog,
    PropertyState,
    PropertyView,
    StatusLabel,
    TaxLot,
    TaxLotAuditLog,
    TaxLotState,
    TaxLotProperty,
    TaxLotView,
)
from seed.models.certification import GreenAssessmentPropertyAuditLog


def merge_states_with_views(state_ids, org_id, log_name, StateClass):
    """
    This merge ultimately ignores merge protection settings and orders merge
    priority -States by most recent AuditLog.

    Calling the submethods below without the 'ignore_merge_protection' flag or with
    it set to false is how to specify that merge protection settings should be
    used.
    """
    if StateClass == PropertyState:
        return merge_properties(state_ids, org_id, log_name, True)
    else:
        return merge_taxlots(state_ids, org_id, log_name, True)


def merge_properties(state_ids, org_id, log_name, ignore_merge_protection=False):
    index = 1
    merged_state = None
    while index < len(state_ids):
        # state 1 is the base, state 2 is merged on top of state 1
        # Use index 0 the first time through, merged_state from then on
        if index == 1:
            state_1 = PropertyState.objects.get(id=state_ids[index - 1])
        else:
            state_1 = merged_state
        state_2 = PropertyState.objects.get(id=state_ids[index])

        merged_state = _merge_log_states(org_id, state_1, state_2, log_name, ignore_merge_protection)

        views = PropertyView.objects.filter(state_id__in=[state_1.id, state_2.id])
        view_ids = list(views.values_list('id', flat=True))
        canonical_ids = list(views.values_list('property_id', flat=True))

        # Create new inventory record and associate it to a new view
        new_property = Property(organization_id=org_id)
        new_property.save()

        cycle_id = views.first().cycle_id
        new_view = PropertyView(
            cycle_id=cycle_id,
            state_id=merged_state.id,
            property_id=new_property.id
        )
        new_view.save()

        _copy_meters_in_order(state_1.id, state_2.id, new_property)
        _copy_propertyview_relationships(view_ids, new_view)

        # Delete canonical records that are NOT associated to other -Views.
        other_associated_views = PropertyView.objects.filter(property_id__in=canonical_ids).exclude(pk__in=view_ids)
        Property.objects \
            .filter(pk__in=canonical_ids) \
            .exclude(pk__in=Subquery(other_associated_views.values('property_id'))) \
            .delete()

        # Delete all -Views
        PropertyView.objects.filter(pk__in=view_ids).delete()

        index += 1

    return merged_state


def merge_taxlots(state_ids, org_id, log_name, ignore_merge_protection=False):
    index = 1
    merged_state = None
    while index < len(state_ids):
        # state 1 is the base, state 2 is merged on top of state 1
        # Use index 0 the first time through, merged_state from then on
        if index == 1:
            state_1 = TaxLotState.objects.get(id=state_ids[index - 1])
        else:
            state_1 = merged_state
        state_2 = TaxLotState.objects.get(id=state_ids[index])

        merged_state = _merge_log_states(org_id, state_1, state_2, log_name, ignore_merge_protection)

        views = TaxLotView.objects.filter(state_id__in=[state_1.id, state_2.id])
        view_ids = list(views.values_list('id', flat=True))
        canonical_ids = list(views.values_list('taxlot_id', flat=True))

        # Create new inventory record and associate it to a new view
        new_taxlot = TaxLot(organization_id=org_id)
        new_taxlot.save()

        cycle_id = views.first().cycle_id
        new_view = TaxLotView(
            cycle_id=cycle_id,
            state_id=merged_state.id,
            taxlot_id=new_taxlot.id
        )
        new_view.save()

        _copy_taxlotview_relationships(view_ids, new_view)

        # Delete canonical records that are NOT associated to other -Views.
        other_associated_views = TaxLotView.objects.filter(taxlot_id__in=canonical_ids).exclude(pk__in=view_ids)
        TaxLot.objects \
            .filter(pk__in=canonical_ids) \
            .exclude(pk__in=Subquery(other_associated_views.values('taxlot_id'))) \
            .delete()

        # Delete all -Views
        TaxLotView.objects.filter(pk__in=view_ids).delete()

        index += 1

    return merged_state


def _merge_log_states(org_id, state_1, state_2, log_name, ignore_merge_protection):
    if isinstance(state_1, PropertyState):
        StateClass = PropertyState
        AuditLogClass = PropertyAuditLog
    else:
        StateClass = TaxLotState
        AuditLogClass = TaxLotAuditLog
    priorities = Column.retrieve_priorities(org_id)
    merged_state = StateClass.objects.create(organization_id=org_id)
    merged_state = merging.merge_state(
        merged_state, state_1, state_2, priorities[StateClass.__name__], ignore_merge_protection
    )

    state_1_audit_log = AuditLogClass.objects.filter(state=state_1).first()
    state_2_audit_log = AuditLogClass.objects.filter(state=state_2).first()

    AuditLogClass.objects.create(
        organization_id=org_id,
        parent1=state_1_audit_log,
        parent2=state_2_audit_log,
        parent_state1=state_1,
        parent_state2=state_2,
        state=merged_state,
        name=log_name,
        description='Automatic Merge',
        import_filename=None,
        record_type=AUDIT_IMPORT
    )

    # Set the merged_state to merged
    merged_state.data_state = DATA_STATE_MATCHING
    merged_state.merge_state = MERGE_STATE_MERGED
    merged_state.save()
    state_1.merge_state = MERGE_STATE_UNKNOWN
    state_1.save()
    state_2.merge_state = MERGE_STATE_UNKNOWN
    state_2.save()

    return merged_state


def _copy_meters_in_order(state_1_id, state_2_id, new_property):
    # Add meters in the following order without regard for the source persisting.
    new_property.copy_meters(
        PropertyView.objects.get(state_id=state_1_id).property_id,
        source_persists=False
    )
    new_property.copy_meters(
        PropertyView.objects.get(state_id=state_2_id).property_id,
        source_persists=False
    )


def _copy_propertyview_relationships(view_ids, new_view):
    """
    Currently, PropertyView relationships include notes, labels, and pairings
    with TaxLotViews. Each of these are copied from given -View IDs and
    associated with a new PropertyView.
    """
    # Assign notes to the new view
    notes = list(Note.objects.values(
        'name', 'note_type', 'text', 'log_data', 'created', 'updated', 'organization_id', 'user_id'
    ).filter(property_view_id__in=view_ids).distinct())

    for note in notes:
        note['property_view'] = new_view
        n = Note(**note)
        n.save()
        # Correct the created and updated times to match the original note
        Note.objects.filter(id=n.id).update(created=note['created'],
                                            updated=note['updated'])

    # Assign certifications to the new view
    certifications = list(HELIXGreenAssessmentProperty.objects.values(
        'source', 'status', 'status_date', '_metric', '_rating', 'version', 'date', 'target_date', 'eligibility',
        '_expiration_date', 'extra_data', 'assessment_id', 'opt_out', 'reference_id', 'id',
    ).filter(view_id__in=view_ids).distinct())

    # gapauditlog_assessment, measurements
    for certification in certifications:
        old_certification_id = certification['id']
        certification['view'] = new_view
        del certification['id']
        c = HELIXGreenAssessmentProperty(**certification)
        c.save()

        # merge audit urls
        urls = GreenAssessmentURL.objects.filter(property_assessment_id=old_certification_id)
        for url in urls:
            url.property_assessment_id = c.id
            url.save()

        # merge audit logs
        audit = GreenAssessmentPropertyAuditLog.objects.filter(greenassessmentproperty_id=old_certification_id).last()
        audit.property_view_id = new_view.id
        audit.greenassessmentproperty_id = c.id
        audit.save()

        # merge measurements
        measurements = HelixMeasurement.objects.filter(assessment_property_id=old_certification_id)
        for measurement in measurements:
            measurement.assessment_property_id = c.id
            measurement.save()

    # Associate labels
    PropertyViewLabels = apps.get_model('seed', 'PropertyView_labels')
    label_ids = list(PropertyViewLabels.objects.filter(propertyview_id__in=view_ids).values_list('statuslabel_id', flat=True))
    new_view.labels.set(StatusLabel.objects.filter(pk__in=label_ids))

    # Associate pairs while deleting old relationships
    paired_view_ids = list(TaxLotProperty.objects.filter(property_view_id__in=view_ids)
                           .order_by('taxlot_view_id').distinct('taxlot_view_id')
                           .values_list('taxlot_view_id', flat=True))

    TaxLotProperty.objects.filter(property_view_id__in=view_ids).delete()
    for paired_view_id in paired_view_ids:
        TaxLotProperty(primary=True,
                       cycle_id=new_view.cycle_id,
                       property_view_id=new_view.id,
                       taxlot_view_id=paired_view_id).save()


def _copy_taxlotview_relationships(view_ids, new_view):
    """
    Currently, TaxLotView relationships include notes, labels, and pairings
    with PropertyViews. Each of these are copied from given -View IDs and
    associated with a new TaxLotView.
    """
    # Assign notes to the new view
    notes = list(Note.objects.values(
        'name', 'note_type', 'text', 'log_data', 'created', 'updated', 'organization_id', 'user_id'
    ).filter(taxlot_view_id__in=view_ids).distinct())

    for note in notes:
        note['taxlot_view'] = new_view
        n = Note(**note)
        n.save()
        # Correct the created and updated times to match the original note
        Note.objects.filter(id=n.id).update(created=note['created'],
                                            updated=note['updated'])

    # Associate labels
    TaxLotViewLabels = apps.get_model('seed', 'TaxLotView_labels')
    label_ids = list(TaxLotViewLabels.objects.filter(taxlotview_id__in=view_ids).values_list('statuslabel_id', flat=True))
    new_view.labels.set(StatusLabel.objects.filter(pk__in=label_ids))

    # Associate pairs while deleting old relationships
    paired_view_ids = list(TaxLotProperty.objects.filter(taxlot_view_id__in=view_ids)
                           .order_by('property_view_id').distinct('property_view_id')
                           .values_list('property_view_id', flat=True))

    TaxLotProperty.objects.filter(taxlot_view_id__in=view_ids).delete()
    for paired_view_id in paired_view_ids:
        TaxLotProperty(primary=True,
                       cycle_id=new_view.cycle_id,
                       property_view_id=paired_view_id,
                       taxlot_view_id=new_view.id).save()

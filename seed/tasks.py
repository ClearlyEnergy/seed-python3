# !/usr/bin/env python
# encoding: utf-8
"""
:copyright (c) 2014 - 2021, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Department of Energy) and contributors. All rights reserved.  # NOQA
:author
"""
from __future__ import absolute_import

import sys

from celery import chord, chain
from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.urls import reverse_lazy
from django.template import Template, Context, loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from seed.decorators import lock_and_track
from seed.lib.mcm.utils import batch
from seed.lib.progress_data.progress_data import ProgressData
from seed.lib.superperms.orgs.models import Organization
from seed.models import (
    Column,
    ColumnMapping,
    Cycle,
    DATA_STATE_MATCHING,
    Property,
    PropertyState,
    PropertyView,
    TaxLot,
    TaxLotState,
    TaxLotView
)


logger = get_task_logger(__name__)


def invite_new_user_to_seed(domain, email_address, token, user_pk, first_name):
    """Send invitation email to newly created user from the landing page.
    NOTE: this function is only used on the landing page because the user has not been assigned an organization
    domain -- The domain name of the running seed instance
    email_address -- The address to send the invitation to
    token -- generated by Django's default_token_generator
    user_pk -- primary key for this user record
    first_name -- First name of the new user
    new_user

    Returns: nothing
    """
    signup_url = reverse_lazy('landing:activate', kwargs={
        'uidb64': urlsafe_base64_encode(force_bytes(user_pk)),
        'token': token
    })

    context = {
        'email': email_address,
        'domain': domain,
        'protocol': 'https',
        'first_name': first_name,
        'signup_url': signup_url
    }

    subject = 'New SEED account'
    email_body = loader.render_to_string(
        'seed/account_create_email.html',
        context
    )
    send_mail(subject, email_body, settings.SERVER_EMAIL, [email_address])
    try:
        bcc_address = settings.SEED_ACCOUNT_CREATION_BCC
        new_subject = "{} ({})".format(subject, email_address)
        send_mail(new_subject, email_body, settings.SERVER_EMAIL, [bcc_address])
    except AttributeError:
        pass


@shared_task
def invite_to_seed(domain, email_address, token, organization, user_pk, first_name):
    """Send invitation email to newly created user.

    domain -- The domain name of the running seed instance
    email_address -- The address to send the invitation to
    token -- generated by Django's default_token_generator
    organization --  the organization user was invited to
    user_pk -- primary key for this user record
    first_name -- First name of the new user

    Returns: nothing
    """
    sign_up_url = Template("https://{{domain}}{{sign_up_url}}").render(Context({
        'domain': domain,
        'sign_up_url': reverse_lazy('landing:signup', kwargs={
            'uidb64': urlsafe_base64_encode(force_bytes(user_pk)),
            'token': token
        })
    }))

    content = Template(organization.new_user_email_content).render(Context({
        'first_name': first_name,
        'sign_up_link': sign_up_url
    }))

    body = Template("{{content}}\n\n{{signature}}").render(Context({
        'content': content,
        'signature': organization.new_user_email_signature
    }))

    send_mail(organization.new_user_email_subject, body, organization.new_user_email_from, [email_address])
    try:
        bcc_address = settings.SEED_ACCOUNT_CREATION_BCC
        new_subject = "{} ({})".format(organization.new_user_email_subject, email_address)
        send_mail(new_subject, body, organization.new_user_email_from, [bcc_address])
    except AttributeError:
        pass


@shared_task
def invite_to_organization(domain, new_user, requested_by, new_org):
    """Send invitation to a newly created organization.

    domain -- The domain name of the running seed instance
    email_address -- The address to send the invitation to
    token -- generated by Django's default_token_generator
    user_pk --primary key for this user record
    first_name -- First name of the new user

    Returns: nothing
    """
    context = {
        'new_user': new_user,
        'first_name': new_user.first_name,
        'domain': domain,
        'protocol': 'https',
        'new_org': new_org,
        'requested_by': requested_by,
    }

    subject = 'Your SEED account has been added to an organization'
    email_body = loader.render_to_string(
        'seed/account_org_added.html',
        context
    )
    send_mail(subject, email_body, settings.SERVER_EMAIL, [new_user.email])
    try:
        bcc_address = settings.SEED_ACCOUNT_CREATION_BCC
        new_subject = "{} ({})".format(subject, new_user.email)
        send_mail(new_subject, email_body, settings.SERVER_EMAIL, [bcc_address])
    except AttributeError:
        pass


def delete_organization(org_pk):
    """delete_organization_buildings"""
    progress_data = ProgressData(func_name='delete_organization', unique_id=org_pk)

    chain(
        delete_organization_inventory.si(org_pk, progress_data.key),
        _delete_organization_related_data.si(org_pk, progress_data.key),
        _finish_delete.si(None, org_pk, progress_data.key)
    )()

    return progress_data.result()


@shared_task
@lock_and_track
def _delete_organization_related_data(org_pk, prog_key):
    Organization.objects.get(pk=org_pk).delete()

    # TODO: Delete measures in BRICR branch

    progress_data = ProgressData.from_key(prog_key)
    return progress_data.result()


@shared_task
def _finish_delete(results, org_pk, prog_key):
    sys.setrecursionlimit(1000)

    progress_data = ProgressData.from_key(prog_key)
    return progress_data.finish_with_success()


@shared_task
def _finish_delete_column(results, column_id, prog_key):
    # Delete all mappings from raw column names to the mapped column, then delete the mapped column
    column = Column.objects.get(id=column_id)
    ColumnMapping.objects.filter(column_mapped=column).delete()
    column.delete()

    progress_data = ProgressData.from_key(prog_key)
    return progress_data.finish_with_success(
        f'Removed {column.column_name} from {progress_data.data["total_records"]} records')


@shared_task
@lock_and_track
def delete_organization_inventory(org_pk, prog_key=None, chunk_size=100, *args, **kwargs):
    """Deletes all properties & taxlots within an organization."""
    sys.setrecursionlimit(5000)  # default is 1000

    progress_data = ProgressData.from_key(prog_key) if prog_key else ProgressData(
        func_name='delete_organization_inventory', unique_id=org_pk)

    property_ids = list(
        Property.objects.filter(organization_id=org_pk).values_list('id', flat=True)
    )
    property_state_ids = list(
        PropertyState.objects.filter(organization_id=org_pk).values_list('id', flat=True)
    )
    taxlot_ids = list(
        TaxLot.objects.filter(organization_id=org_pk).values_list('id', flat=True)
    )
    taxlot_state_ids = list(
        TaxLotState.objects.filter(organization_id=org_pk).values_list('id', flat=True)
    )

    total = len(property_ids) + len(property_state_ids) + len(taxlot_ids) + len(taxlot_state_ids)

    if total == 0:
        return progress_data.finish_with_success('No inventory data to remove for organization')

    # total steps is the total number of properties divided by the chunk size
    progress_data.total = total / float(chunk_size)
    progress_data.save()

    tasks = []
    # we could also use .s instead of .subtask and not wrap the *args
    for del_ids in batch(property_ids, chunk_size):
        tasks.append(
            _delete_organization_property_chunk.subtask(
                (del_ids, progress_data.key, org_pk)
            )
        )
    for del_ids in batch(property_state_ids, chunk_size):
        tasks.append(
            _delete_organization_property_state_chunk.subtask(
                (del_ids, progress_data.key, org_pk)
            )
        )
    for del_ids in batch(taxlot_ids, chunk_size):
        tasks.append(
            _delete_organization_taxlot_chunk.subtask(
                (del_ids, progress_data.key, org_pk)
            )
        )
    for del_ids in batch(taxlot_state_ids, chunk_size):
        tasks.append(
            _delete_organization_taxlot_state_chunk.subtask(
                (del_ids, progress_data.key, org_pk)
            )
        )
    chord(tasks, interval=15)(_finish_delete.subtask([org_pk, progress_data.key]))

    return progress_data.result()


@shared_task
@lock_and_track
def delete_organization_cycle(cycle_pk, organization_pk, prog_key=None, chunk_size=100, *args, **kwargs):
    """Deletes an organization's cycle.

    This must be an async task b/c a cascading deletion can require the removal
    of many *States associated with an ImportFile, overwhelming the server.

    :param cycle_pk: int
    :param prog_key: str
    :param chunk_size: int
    :return: dict, from ProgressData.result()
    """
    progress_data = ProgressData.from_key(prog_key) if prog_key else ProgressData(
        func_name='delete_organization_cycle', unique_id=cycle_pk)

    has_inventory = (
        PropertyView.objects.filter(cycle_id=cycle_pk).exists()
        or TaxLotView.objects.filter(cycle_id=cycle_pk).exists()
    )
    if has_inventory:
        progress_data.finish_with_error('All PropertyView and TaxLotViews linked to the Cycle must be removed')
        return progress_data.result()

    property_state_ids = PropertyState.objects.filter(import_file__cycle_id=cycle_pk).values_list('id', flat=True)
    tax_lot_state_ids = TaxLotState.objects.filter(import_file__cycle_id=cycle_pk).values_list('id', flat=True)
    progress_data.total = (len(property_state_ids) + len(tax_lot_state_ids)) / chunk_size
    progress_data.save()

    tasks = []
    for chunk_ids in batch(property_state_ids, chunk_size):
        tasks.append(
            _delete_organization_property_state_chunk.si(
                chunk_ids, progress_data.key, organization_pk
            )
        )
    for chunk_ids in batch(tax_lot_state_ids, chunk_size):
        tasks.append(
            _delete_organization_taxlot_state_chunk.si(
                chunk_ids, progress_data.key, organization_pk
            )
        )

    chord(tasks, interval=15)(_finish_delete_cycle.si(cycle_pk, progress_data.key))

    return progress_data.result()


@shared_task
def _finish_delete_cycle(cycle_id, prog_key):
    # Finally delete the cycle
    cycle = Cycle.objects.get(id=cycle_id)
    cycle.delete()

    progress_data = ProgressData.from_key(prog_key)
    return progress_data.finish_with_success(
        f'Removed {cycle.name}')


@shared_task
@lock_and_track
def delete_organization_column(column_pk, org_pk, prog_key=None, chunk_size=100, *args, **kwargs):
    """Deletes an extra_data column from all merged property/taxlot states."""
    progress_data = ProgressData.from_key(prog_key) if prog_key else ProgressData(
        func_name='delete_organization_column', unique_id=column_pk)

    chain(
        _delete_organization_column_evaluate.subtask((column_pk, org_pk, progress_data.key, chunk_size)),
        _finish_delete_column.subtask([column_pk, progress_data.key])
    ).apply_async()

    return progress_data.result()


@shared_task
def _delete_organization_column_evaluate(column_pk, org_pk, prog_key, chunk_size, *args, **kwargs):
    """ Find -States with column to be deleted """
    column = Column.objects.get(id=column_pk, organization_id=org_pk)

    ids = []

    if column.table_name == 'PropertyState':
        ids = PropertyState.objects.filter(organization_id=org_pk, data_state=DATA_STATE_MATCHING,
                                           extra_data__has_key=column.column_name).values_list('id', flat=True)
    elif column.table_name == 'TaxLotState':
        ids = TaxLotState.objects.filter(organization_id=org_pk, data_state=DATA_STATE_MATCHING,
                                         extra_data__has_key=column.column_name).values_list('id', flat=True)

    progress_data = ProgressData.from_key(prog_key)
    total = len(ids)
    progress_data.total = total / float(chunk_size)
    progress_data.data['completed_records'] = 0
    progress_data.data['total_records'] = total
    progress_data.save()

    for chunk_ids in batch(ids, chunk_size):
        _delete_organization_column_chunk(
            chunk_ids, column.column_name, column.table_name, progress_data.key
        )


def _delete_organization_column_chunk(chunk_ids, column_name, table_name, prog_key, *args, **kwargs):
    """updates a list of ``chunk_ids`` and increments the cache"""

    if table_name == 'PropertyState':
        states = PropertyState.objects.filter(id__in=chunk_ids)
    else:
        states = TaxLotState.objects.filter(id__in=chunk_ids)

    with transaction.atomic():
        for state in states:
            del state.extra_data[column_name]
            state.save(update_fields=['extra_data', 'hash_object'])

    progress_data = ProgressData.from_key(prog_key)
    progress_data.step_with_counter()


@shared_task
def _delete_organization_property_chunk(del_ids, prog_key, org_pk, *args, **kwargs):
    """deletes a list of ``del_ids`` and increments the cache"""
    Property.objects.filter(organization_id=org_pk, pk__in=del_ids).delete()
    progress_data = ProgressData.from_key(prog_key)
    progress_data.step()


@shared_task
def _delete_organization_property_state_chunk(del_ids, prog_key, org_pk, *args,
                                              **kwargs):
    """deletes a list of ``del_ids`` and increments the cache"""
    PropertyState.objects.filter(pk__in=del_ids).delete()
    progress_data = ProgressData.from_key(prog_key)
    progress_data.step()


@shared_task
def _delete_organization_taxlot_chunk(del_ids, prog_key, org_pk, *args, **kwargs):
    """deletes a list of ``del_ids`` and increments the cache"""
    TaxLot.objects.filter(organization_id=org_pk, pk__in=del_ids).delete()
    progress_data = ProgressData.from_key(prog_key)
    progress_data.step()


@shared_task
def _delete_organization_taxlot_state_chunk(del_ids, prog_key, org_pk, *args, **kwargs):
    """deletes a list of ``del_ids`` and increments the cache"""
    TaxLotState.objects.filter(organization_id=org_pk, pk__in=del_ids).delete()
    progress_data = ProgressData.from_key(prog_key)
    progress_data.step()

# !/usr/bin/env python
# encoding: utf-8
"""
:copyright (c) 2014 - 2018, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Department of Energy) and contributors. All rights reserved.  # NOQA
:author
"""
import json
from unittest import skip

from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse_lazy
from django.test import TestCase

from seed.audit_logs.models import AuditLog, LOG, NOTE
from seed.factory import SEEDFactory
from seed.landing.models import SEEDUser as User
from seed.models import CanonicalBuilding
from seed.tests.util import FakeRequest
from seed.utils.organizations import create_organization


@skip('Need to remove these tests and the AuditLog Module')
class AuditLogModelTests(TestCase):

    def setUp(self):
        user_details = {
            'username': 'test_user@demo.com',
            'password': 'test_pass',
            'email': 'test_user@demo.com',
            'first_name': 'Johnny',
            'last_name': 'Energy',
        }
        self.user = User.objects.create_user(**user_details)
        self.org, _, _ = create_organization(self.user, 'my org')
        self.client.login(**user_details)
        self.fake_request = FakeRequest(user=self.user)
        # create BuildingSnapshot and CanonicalBuilding
        self.cb = CanonicalBuilding.objects.create(active=True)
        self.bs = SEEDFactory.building_snapshot(
            canonical_building=self.cb,
            property_name='ADMIN BUILDING',
            address_line_1='100 Admin St'
        )
        self.cb.canonical_snapshot = self.bs
        self.cb.save()
        # create AuditLog audit
        self.audit_log = AuditLog.objects.create(
            user=self.user,
            content_object=self.cb,
            audit_type=LOG,
            action='create_building',
            action_response={'status': 'success', 'building_id': self.cb.pk},
            action_note='user created a building',
            organization=self.org,
        )
        # create AuditLog note
        self.note_text = 'The building has a wonderfully low EUI'
        self.note = AuditLog.objects.create(
            user=self.user,
            content_object=self.cb,
            audit_type=NOTE,
            action='create_note',
            action_response={'status': 'success'},
            action_note=self.note_text,
            organization=self.org,
        )

    def test_model___unicode__(self):
        """tests the AuditLog inst. str or unicode"""
        self.assertEqual('Log <%s> (%s)' % (self.user, self.audit_log.pk), str(self.audit_log))
        self.assertEqual('Note <%s> (%s)' % (self.user, self.note.pk), str(self.note))

    def test_note(self):
        """tests note save"""
        note = AuditLog.objects.get(pk=self.note.pk)
        self.assertEqual(note.audit_type, NOTE)
        self.assertEqual(note.organization, self.org)
        self.assertEqual(note.action_note, self.note_text)
        self.assertEqual(note.user, self.user)

    def test_audit(self):
        """tests audit save"""
        audit_log = AuditLog.objects.get(pk=self.audit_log.pk)
        self.assertEqual(audit_log.audit_type, LOG)
        self.assertEqual(audit_log.organization, self.org)
        self.assertEqual(audit_log.action_note, 'user created a building')
        self.assertEqual(audit_log.user, self.user)
        self.assertEqual(audit_log.content_object, self.cb)

    def test_note_save(self):
        """notes should be able to save/update"""
        note = AuditLog.objects.get(pk=self.note.pk)
        note.action_note = 'EUI is average'
        note.save()
        note = AuditLog.objects.get(pk=self.note.pk)
        self.assertEqual(note.action_note, 'EUI is average')
        AuditLog.objects.filter(audit_type=NOTE).update(action_note='EUI OK')
        note = AuditLog.objects.get(pk=self.note.pk)
        self.assertEqual(note.action_note, 'EUI OK')

    def test_audit_save(self):
        """audit_log ``LOG`` should not be able to save/update"""
        # arrange
        audit_log = AuditLog.objects.get(pk=self.audit_log.pk)
        self.assertEqual(audit_log.action_note, 'user created a building')

        # act/assert save raises error
        audit_log.action_audit_log = 'EUI is average'
        with self.assertRaises(PermissionDenied) as error:
            audit_log.save()

        # assert
        self.assertEqual(
            str(error.exception),
            'AuditLogs cannot be edited, only notes'
        )
        audit_log = AuditLog.objects.get(pk=self.audit_log.pk)
        self.assertEqual(audit_log.action_note, 'user created a building')

    def test_audit_update(self):
        """audit_log ``LOG`` should not be able to save/update"""
        # arrange
        audit_log = AuditLog.objects.get(pk=self.audit_log.pk)
        self.assertEqual(audit_log.action_note, 'user created a building')

        # act
        AuditLog.objects.filter(audit_type=LOG).update(action_note='OK')

        # assert, that update did not affect audit_log
        audit_log = AuditLog.objects.get(pk=self.audit_log.pk)
        self.assertEqual(audit_log.action_note, 'user created a building')

    def test_generic_relation(self):
        """test CanonicalBuilding.audit_logs"""
        # arrange
        cb = CanonicalBuilding.objects.get(pk=self.cb.pk)

        # act
        audit_logs = cb.audit_logs.all()
        notes = cb.audit_logs.filter(audit_type=NOTE)
        logs = cb.audit_logs.filter(audit_type=LOG)

        # assert
        self.assertEqual(audit_logs.count(), 2)
        self.assertEqual(
            notes.first(),
            self.note
        )
        self.assertEqual(
            logs.first(),
            self.audit_log
        )

    def test_get_all_audit_logs_for_an_org(self):
        """gets all audit logs for an org"""
        audit_logs = AuditLog.objects.filter(organization=self.org)
        self.assertEqual(audit_logs.count(), 2)


@skip('Need to remove these tests and the AuditLog Module')
class AuditLogViewTests(TestCase):

    def setUp(self):
        user_details = {
            'username': 'test_user@demo.com',
            'password': 'test_pass',
            'email': 'test_user@demo.com',
            'first_name': 'Johnny',
            'last_name': 'Energy',
        }
        self.user = User.objects.create_user(**user_details)
        self.org, _, _ = create_organization(self.user, 'my org')
        self.client.login(**user_details)
        self.fake_request = FakeRequest(user=self.user)
        # create BuildingSnapshot and CanonicalBuilding
        self.cb = CanonicalBuilding.objects.create(active=True)
        self.bs = SEEDFactory.building_snapshot(
            canonical_building=self.cb,
            property_name='ADMIN BUILDING',
            address_line_1='100 Admin St'
        )
        self.cb.canonical_snapshot = self.bs
        self.cb.save()
        # create AuditLog audit
        self.audit_log = AuditLog.objects.create(
            user=self.user,
            content_object=self.cb,
            audit_type=LOG,
            action='create_building',
            action_response={'status': 'success', 'building_id': self.cb.pk},
            action_note='user created a building',
            organization=self.org,
        )
        # create AuditLog note
        self.note_text = 'The building has a wonderfully low EUI'
        self.note = AuditLog.objects.create(
            user=self.user,
            content_object=self.cb,
            audit_type=NOTE,
            action='create_note',
            action_response={'status': 'success'},
            action_note=self.note_text,
            organization=self.org,
        )

    def test_get_building_logs(self):
        """test the django view get_building_logs"""
        # act
        resp = self.client.get(
            reverse_lazy("audit_logs:get_building_logs"),
            {
                'organization_id': self.org.id,
                'building_id': self.cb.id
            },
            content_type='application/json',
        )
        data = json.loads(resp.content)

        # assert
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['audit_logs']), 2)
        self.assertEqual(data['audit_logs'], [
            {
                'action': 'create_note',
                'action_note': 'The building has a wonderfully low EUI',
                'action_response': {'status': 'success'},
                'audit_type': 'Note',
                'content_type': 'canonicalbuilding',
                'created': data['audit_logs'][0]['created'],
                'id': data['audit_logs'][0]['id'],
                'model': 'audit_logs.auditlog',
                'modified': data['audit_logs'][0]['modified'],
                'object_id': data['audit_logs'][0]['object_id'],
                'organization': {
                    'id': self.org.pk,
                    'name': self.org.name,
                },
                'pk': data['audit_logs'][0]['pk'],
                'user': {
                    'id': self.user.id,
                    'first_name': self.user.first_name,
                    'last_name': self.user.last_name,
                    'email': self.user.email,
                }
            },
            {
                'action': 'create_building',
                'action_note': 'user created a building',
                'action_response': {
                    'building_id': self.cb.pk, 'status': 'success'
                },
                'audit_type': 'Log',
                'content_type': 'canonicalbuilding',
                'created': data['audit_logs'][1]['created'],
                'id': data['audit_logs'][1]['id'],
                'model': 'audit_logs.auditlog',
                'modified': data['audit_logs'][1]['modified'],
                'object_id': data['audit_logs'][1]['object_id'],
                'organization': {
                    'id': self.org.pk,
                    'name': self.org.name,
                },
                'pk': data['audit_logs'][1]['pk'],
                'user': {
                    'id': self.user.id,
                    'first_name': self.user.first_name,
                    'last_name': self.user.last_name,
                    'email': self.user.email,
                }
            }
        ])

    def test_create_note(self):
        """tests create_note"""
        # act
        resp = self.client.post(
            reverse_lazy("audit_logs:create_note"),
            data=json.dumps({
                'organization_id': self.org.id,
                'building_id': self.cb.id,
                'action_note': 'test note',
            }),
            content_type='application/json',
        )
        data = json.loads(resp.content)

        # assert
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['audit_log']['audit_type'], 'Note')
        self.assertEqual(
            data['audit_log']['user'],
            {
                'first_name': self.user.first_name,
                'last_name': self.user.last_name,
                'email': self.user.email,
                'id': self.user.pk
            }
        )
        self.assertEqual(
            data['audit_log']['organization'],
            {
                'name': self.org.name,
                'id': self.org.pk
            }
        )
        self.assertEqual(
            data['audit_log']['action_note'],
            'test note'
        )
        audit_log = AuditLog.objects.first()
        self.assertEqual(data['audit_log'], audit_log.to_dict())
        self.assertEqual(audit_log.organization, self.org)
        self.assertEqual(audit_log.user, self.user)

    def test_update_note(self):
        """tests update_note"""
        # arrange
        self.assertEqual(self.note.action_note, self.note_text)
        update_note = 'what a nice building'
        self.assertNotEqual(self.note_text, update_note)
        original_modified = self.note.modified

        # act
        resp = self.client.put(
            reverse_lazy("audit_logs:update_note"),
            data=json.dumps({
                'organization_id': self.org.id,
                'building_id': self.cb.id,
                'audit_log_id': self.note.id,
                'action_note': update_note,
            }),
            content_type='application/json',
        )
        data = json.loads(resp.content)

        # assert
        self.assertEqual(data['status'], 'success')
        # check the resp note matches update note
        self.assertEqual(
            data['audit_log']['action_note'],
            update_note
        )
        # check the lastest audit_log is the note with the update
        audit_log = AuditLog.objects.first()
        self.assertEqual(audit_log.action_note, update_note)
        # check the modified field was updated
        self.assertNotEqual(audit_log.modified, original_modified)

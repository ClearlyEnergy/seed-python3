# !/usr/bin/env python
# encoding: utf-8
"""
:copyright (c) 2014 - 2021, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Department of Energy) and contributors. All rights reserved.  # NOQA
:author
"""
import logging

from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action

from seed.decorators import ajax_request_class
from seed.landing.models import SEEDUser as User, SEEDUser
from seed.lib.superperms.orgs.decorators import PERMS
from seed.lib.superperms.orgs.decorators import has_perm_class
from seed.lib.superperms.orgs.models import (
    ROLE_OWNER,
    ROLE_MEMBER,
    ROLE_VIEWER,
    Organization,
    OrganizationUser,
)
from seed.models.data_quality import Rule
from seed.tasks import (
    invite_to_seed,
)
from seed.utils.api import api_endpoint_class, OrgMixin
from seed.utils.api_schema import AutoSchemaHelper, swagger_auto_schema_org_query_param
from seed.utils.organizations import create_organization
from rest_framework.status import HTTP_400_BAD_REQUEST

_log = logging.getLogger(__name__)


def _get_js_role(role):
    """return the JS friendly role name for user
    :param role: role as defined in superperms.models
    :returns: (string) JS role name
    """
    roles = {
        ROLE_OWNER: 'owner',
        ROLE_VIEWER: 'viewer',
        ROLE_MEMBER: 'member',
    }
    return roles.get(role, 'viewer')


def _get_role_from_js(role):
    """return the OrganizationUser role_level from the JS friendly role name

    :param role: 'member', 'owner', or 'viewer'
    :returns: int role as defined in superperms.models
    """
    roles = {
        'owner': ROLE_OWNER,
        'viewer': ROLE_VIEWER,
        'member': ROLE_MEMBER,
    }
    return roles[role]


def _get_js_rule_type(data_type):
    """return the JS friendly data type name for the data data_quality rule

    :param data_type: data data_quality rule data type as defined in data_quality.models
    :returns: (string) JS data type name
    """
    return dict(Rule.DATA_TYPES).get(data_type)


def _get_rule_type_from_js(data_type):
    """return the Rules TYPE from the JS friendly data type

    :param data_type: 'string', 'number', 'date', or 'year'
    :returns: int data type as defined in data_quality.models
    """
    d = {v: k for k, v in dict(Rule.DATA_TYPES).items()}
    return d.get(data_type)


def _get_js_rule_severity(severity):
    """return the JS friendly severity name for the data data_quality rule

    :param severity: data data_quality rule severity as defined in data_quality.models
    :returns: (string) JS severity name
    """
    return dict(Rule.SEVERITY).get(severity)


def _get_severity_from_js(severity):
    """return the Rules SEVERITY from the JS friendly severity

    :param severity: 'error', or 'warning'
    :returns: int severity as defined in data_quality.models
    """
    d = {v: k for k, v in dict(Rule.SEVERITY).items()}
    return d.get(severity)


class EmailAndIDSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=100)
    user_id = serializers.IntegerField()


class ListUsersResponseSerializer(serializers.Serializer):
    users = EmailAndIDSerializer(many=True)


# this is used for swagger docs for some views below
user_response_schema = AutoSchemaHelper.schema_factory({
    'first_name': 'string',
    'last_name': 'string',
    'email': 'string',
    'api_key': 'string',
})


class UserViewSet(viewsets.ViewSet, OrgMixin):
    raise_exception = True

    def validate_request_user(self, pk, request):
        try:
            user = User.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return False, JsonResponse(
                {'status': 'error', 'message': "Could not find user with pk = " + str(pk)},
                status=status.HTTP_404_NOT_FOUND)
        if not user == request.user:
            return False, JsonResponse(
                {'status': 'error', 'message': "Cannot access user with pk = " + str(pk)},
                status=status.HTTP_403_FORBIDDEN)
        return True, user

    @swagger_auto_schema(
        manual_parameters=[AutoSchemaHelper.query_org_id_field()],
        request_body=AutoSchemaHelper.schema_factory(
            {
                'org_name': 'string',
                'first_name': 'string',
                'last_name': 'string',
                'role': 'string',
                'email': 'string',
            },
            required=['first_name', 'last_name', 'role', 'email'],
            description='An object containing meta data for a new user:\n'
                        '-org_name: New organization name if creating a new organization for this user\n'
                        '-first_name: First name of new user\n'
                        '-last_name: Last name of new user\n'
                        '-role: one of owner, member, or viewer\n'
                        '-email: Email address of the new user'
        ),
        responses={
            200: AutoSchemaHelper.schema_factory(
                {
                    'status': 'string',
                    'message': 'string',
                    'org': 'string',
                    'org_created': 'boolean',
                    'username': 'string',
                    'user_id': 'string',
                },
                description='Properties:\n'
                            '-org: name of new org (or existing org)\n'
                            '-org_created: true if new org created\n'
                            '-username: username of new user\n'
                            '-user_id: user id (pk) of new user'
            )
        }
    )
    @api_endpoint_class
    @ajax_request_class
    @has_perm_class('requires_owner')
    def create(self, request):
        """
        Creates a new SEED user.  One of 'organization_id' or 'org_name' is needed.
        Sends invitation email to the new user.
        """
        # WARNING: we aren't using the OrgMixin here to validate the organization
        # It is assumed the org authorization logic implemented in this view is
        # consistent with our permissions checking (has_perm_class decorator)
        body = request.data
        org_name = body.get('org_name')
        org_id = request.query_params.get('organization_id', None)
        if (org_name and org_id) or (not org_name and not org_id):
            return JsonResponse({
                'status': 'error',
                'message': 'Choose either an existing org or provide a new one'
            }, status=status.HTTP_409_CONFLICT)

        first_name = body['first_name']
        last_name = body['last_name']
        email = body['email']
        username = body['email']
        user, created = User.objects.get_or_create(username=username.lower())

        if org_id:
            org = Organization.objects.get(pk=org_id)
            org_created = False
        else:
            org, _, _ = create_organization(user, org_name)
            org_created = True

        # Add the user to the org.  If this is the org's first user,
        # the user becomes the owner/admin automatically.
        # see Organization.add_member()
        if not org.is_member(user):
            org.add_member(user)

        if body.get('role'):
            # check if this is a dict, if so, grab the value out of 'value'
            role = body['role']
            try:
                _get_role_from_js(role)
            except Exception:
                return JsonResponse({'status': 'error', 'message': 'valid arguments for role are [viewer, member, '
                                                                   'owner]'},
                                    status=status.HTTP_400_BAD_REQUEST)

            OrganizationUser.objects.filter(
                organization_id=org.pk,
                user_id=user.pk
            ).update(role_level=_get_role_from_js(role))

        if created:
            user.set_unusable_password()
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
        user.save()

        try:
            domain = request.get_host()
        except Exception:
            domain = 'seed-platform.org'
        invite_to_seed(domain, user.email, default_token_generator.make_token(user), org, user.pk, first_name)

        return JsonResponse({
            'status': 'success',
            'message': user.email,
            'org': org.name,
            'org_created': org_created,
            'username': user.username,
            'user_id': user.id
        })

    @swagger_auto_schema(
        responses={
            200: ListUsersResponseSerializer,
        }
    )
    @ajax_request_class
    @has_perm_class('requires_superuser')
    def list(self, request):
        """
        Retrieves all users' email addresses and IDs.
        Only usable by superusers.
        """
        users = []
        for user in User.objects.only('id', 'email'):
            users.append({'email': user.email, 'user_id': user.id})
        return JsonResponse({'users': users})

    @ajax_request_class
    @api_endpoint_class
    @action(detail=False, methods=['GET'])
    def current(self, request):
        """
        Returns the id (primary key) for the current user to allow it
        to be passed to other user related endpoints
        ---
        type:
            pk:
                description: Primary key for the current user
                required: true
                type: string
        """
        return JsonResponse({'pk': request.user.id})

    @swagger_auto_schema(
        manual_parameters=[AutoSchemaHelper.query_org_id_field()],
        request_body=AutoSchemaHelper.schema_factory(
            {
                'role': 'string',
            },
            description='new role for user',
        ),
    )
    @api_endpoint_class
    @ajax_request_class
    @has_perm_class('requires_owner')
    @action(detail=True, methods=['PUT'])
    def role(self, request, pk=None):
        """
        Updates a user's role within an organization.
        """
        body = request.data
        role = _get_role_from_js(body['role'])

        user_id = pk
        organization_id = self.get_organization(request)

        is_last_member = not OrganizationUser.objects.filter(
            organization_id=organization_id,
        ).exclude(user_id=user_id).exists()

        if is_last_member:
            return JsonResponse({
                'status': 'error',
                'message': 'an organization must have at least one member'
            }, status=status.HTTP_409_CONFLICT)

        is_last_owner = not OrganizationUser.objects.filter(
            organization_id=organization_id,
            role_level=ROLE_OWNER,
        ).exclude(user_id=user_id).exists()

        if is_last_owner:
            return JsonResponse({
                'status': 'error',
                'message': 'an organization must have at least one owner level member'
            }, status=status.HTTP_409_CONFLICT)

        OrganizationUser.objects.filter(
            user_id=user_id,
            organization_id=organization_id
        ).update(role_level=role)

        return JsonResponse({'status': 'success'})

    @swagger_auto_schema(
        responses={
            200: user_response_schema,
        }
    )
    @api_endpoint_class
    @ajax_request_class
    def retrieve(self, request, pk=None):
        """
        Retrieves the a user's first_name, last_name, email
        and api key if exists by user ID (pk).
        """

        ok, content = self.validate_request_user(pk, request)
        if ok:
            user = content
        else:
            return content
        return JsonResponse({
            'status': 'success',
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'api_key': user.api_key,
        })

    @ajax_request_class
    @action(detail=True, methods=['POST'])
    def generate_api_key(self, request, pk=None):
        """
        Generates a new API key
        ---
        parameter_strategy: replace
        parameters:
            - name: pk
              description: User ID / primary key
              type: integer
              required: true
              paramType: path
        type:
            status:
                description: success or error
                type: string
                required: true
            api_key:
                description: the new API key for this user
                type: string
                required: true
        """
        ok, content = self.validate_request_user(pk, request)
        if ok:
            user = content
        else:
            return content
        user.generate_key()
        return {
            'status': 'success',
            'api_key': User.objects.get(pk=pk).api_key
        }

    @swagger_auto_schema(
        request_body=AutoSchemaHelper.schema_factory({
            'first_name': 'string',
            'last_name': 'string',
            'email': 'string'
        }),
        description='An object containing meta data for a updated user: \n'
                    '- Required - first_name, last_name, email',
        responses={
            200: user_response_schema,
        }
    )
    @api_endpoint_class
    @ajax_request_class
    def update(self, request, pk=None):
        """
        Updates the user's first name, last name, and email
        """
        body = request.data
        ok, content = self.validate_request_user(pk, request)
        if ok:
            user = content
        else:
            return content
        json_user = body
        user.first_name = json_user.get('first_name')
        user.last_name = json_user.get('last_name')
        user.email = json_user.get('email')
        user.username = json_user.get('email')
        user.save()
        return JsonResponse({
            'status': 'success',
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'api_key': user.api_key,
        })

    @swagger_auto_schema(
        request_body=AutoSchemaHelper.schema_factory(
            {
                'current_password': 'string',
                'password_1': 'string',
                'password_2': 'string',
            },
            description='Fill in the current and new matching passwords'),
    )
    @ajax_request_class
    @action(detail=True, methods=['PUT'])
    def set_password(self, request, pk=None):
        """
        sets/updates a user's password, follows the min requirement of
        django password validation settings in config/settings/common.py
        """
        body = request.data
        ok, content = self.validate_request_user(pk, request)
        if ok:
            user = content
        else:
            return content
        current_password = body.get('current_password')
        p1 = body.get('password_1')
        p2 = body.get('password_2')
        if not user.check_password(current_password):
            return JsonResponse({'status': 'error', 'message': 'current password is not valid'},
                                status=status.HTTP_400_BAD_REQUEST)
        if p1 is None or p1 != p2:
            return JsonResponse({'status': 'error', 'message': 'entered password do not match'},
                                status=status.HTTP_400_BAD_REQUEST)
        try:
            validate_password(p2)
        except ValidationError as e:
            return JsonResponse({'status': 'error', 'message': e.messages[0]},
                                status=status.HTTP_400_BAD_REQUEST)
        user.set_password(p1)
        user.save()
        return JsonResponse({'status': 'success'})

    @ajax_request_class
    def get_actions(self, request):
        """returns all actions"""
        return {
            'status': 'success',
            'actions': list(PERMS.keys()),
        }

    @swagger_auto_schema(
        manual_parameters=[AutoSchemaHelper.query_org_id_field()],
        request_body=AutoSchemaHelper.schema_factory(
            {
                'actions': ['string'],
            },
            description='A list of actions to check: examples include (requires_parent_org_owner, '
                        'requires_owner, requires_member, requires_viewer, '
                        'requires_superuser, can_create_sub_org, can_remove_org)'
        ),
        responses={
            200: AutoSchemaHelper.schema_factory({
                'auth': {
                    'action_name': 'boolean'
                }
            })
        }
    )
    @ajax_request_class
    @action(detail=True, methods=['POST'])
    def is_authorized(self, request, pk=None):
        """
        Checks the auth for a given action, if user is the owner of the parent
        org then True is returned for each action
        """
        ok, content = self.validate_request_user(pk, request)
        if ok:
            user = content
        else:
            return content

        actions, org, error, message = self._parse_is_authenticated_params(request)
        if error:
            return JsonResponse({
                'status': 'error',
                'message': message
            }, status=status.HTTP_400_BAD_REQUEST)

        # If the only action requested is 'requires_superuser' no need to check an org affiliation
        if len(actions) == 1 and actions[0] == 'requires_superuser':
            return JsonResponse(
                {'status': 'success', 'auth': {'requires_superuser': user.is_superuser}})

        auth = self._try_parent_org_auth(user, org, actions)
        if auth:
            return JsonResponse({'status': 'success', 'auth': auth})

        try:
            ou = OrganizationUser.objects.get(user=user, organization=org)
        except OrganizationUser.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'user does not exist'})

        auth = {action: PERMS[action](ou) for action in actions}
        return JsonResponse({'status': 'success', 'auth': auth})

    def _parse_is_authenticated_params(self, request):
        """checks if the org exists and if the actions are present

        :param request: the request
        :returns: tuple (actions, org, error, message)
        """
        error = False
        message = ""
        body = request.data
        if not body.get('actions'):
            message = 'no actions to check'
            error = True

        # WARNING: we aren't using the OrgMixin here to validate the organization
        # It is assumed the org authorization logic implemented here is sufficient
        org_id = request.query_params.get('organization_id', None)
        if org_id == '':
            message = 'organization id is undefined'
            error = True
            org = None
        else:
            try:
                org = Organization.objects.get(pk=org_id)
            except Organization.DoesNotExist:
                message = 'organization does not exist'
                error = True
                org = None

        return body.get('actions'), org, error, message

    def _try_parent_org_auth(self, user, organization, actions):
        """checks the parent org for permissions, if the user is not the owner of
        the parent org, then None is returned.

        :param user: the request user
        :param organization: org to check its parent
        :param actions: list of str actions to check
        :returns: a dict of action permission resolutions or None
        """
        try:
            ou = OrganizationUser.objects.get(
                user=user,
                organization=organization.parent_org,
                role_level=ROLE_OWNER
            )
        except OrganizationUser.DoesNotExist:
            return None

        return {
            action: PERMS['requires_owner'](ou) for action in actions
        }

    @swagger_auto_schema(
        responses={
            200: AutoSchemaHelper.schema_factory({
                'show_shared_buildings': 'boolean'
            })
        }
    )
    @ajax_request_class
    @action(detail=True, methods=['GET'])
    def shared_buildings(self, request, pk=None):
        """
        Get the request user's ``show_shared_buildings`` attr
        """
        ok, content = self.validate_request_user(pk, request)
        if ok:
            user = content
        else:
            return content

        return JsonResponse({
            'status': 'success',
            'show_shared_buildings': user.show_shared_buildings,
        })

    @swagger_auto_schema_org_query_param
    @ajax_request_class
    @has_perm_class('requires_viewer')
    @action(detail=True, methods=['PUT'])
    def default_organization(self, request, pk=None):
        """
        Sets the user's default organization
        """
        ok, content = self.validate_request_user(pk, request)
        if ok:
            user = content
        else:
            return content
        user.default_organization_id = self.get_organization(request)
        user.save()
        return {'status': 'success'}

    @has_perm_class('requires_superuser')
    @ajax_request_class
    @action(detail=True, methods=['PUT'])
    def deactivate(self, request, pk=None):
        """
        Deactivates a user
        """
        try:
            user_id = pk
            user = SEEDUser.objects.get(
                id=user_id
            )
            user.deactivate_user()
            return JsonResponse({
                'status': 'successfully deactivated',
                'data': user.email
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'data': str(e),
            }, status=HTTP_400_BAD_REQUEST)
# !/usr/bin/env python
# encoding: utf-8
"""
SEED Platform (TM), Copyright (c) Alliance for Sustainable Energy, LLC, and other contributors.
See also https://github.com/seed-platform/seed/main/LICENSE.md
"""

from django.conf import settings
from rest_framework import authentication
from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from seed.landing.models import SEEDUser as User
from seed.lib.superperms.orgs.models import OrganizationUser
from helix.models import HELIXOrganization as Organization
from seed.utils.organizations import create_organization


class SEEDAuthentication(authentication.BaseAuthentication):
    """
    Django Rest Framework implementation of the `seed.utils.api.get_api_request_user` functionality
    to extract the User from the HTTP_AUTHORIZATION header using an API key.
    """

    def authenticate(self, request):
        header = User.process_header_request(request)
        if header is None:
            return User.process_query_request(request), None
        return header, None  # return None per base class

class SEEDKeyAuthentication:
    """
    Django Authentication implementation of the `seed.utils.api.get_api_request_user`
    functionality to extract the User from the HTTP_AUTHORIZATION header using an API
    key.
    """

    def authenticate(self, request, token=None):
        user = User.process_header_request(request)
        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

class SeedOpenIDAuthenticationBackend(OIDCAuthenticationBackend):
    def create_user(self, claims):
        if User.objects.filter(username=claims['email']).exists():
            return User.objects.get(username=claims['email'])
        user = User.objects.create_user(claims['email'].lower(), claims['email'], '')
        user.generate_key()
        organization = Organization.objects.filter(name=settings.OIDC_SEED_ORG)
        if organization.exists():
            organization = organization.get()
            OrganizationUser.objects.get_or_create(user=user, organization=organization)
        else:
            organization, _, user_added = create_organization(user, settings.OIDC_SEED_ORG)
        return user


class HELIXAuthentication:
    def authenticate(self, request):
        user = User.process_token_request(request)
        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

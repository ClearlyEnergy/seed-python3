# -*- coding: utf-8 -*-
"""
:copyright (c) 2014 - 2020, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Department of Energy) and contributors. All rights reserved.  # NOQA
:author
"""
from django.core.management.base import BaseCommand

from seed.lib.superperms.orgs.models import Organization
from seed.models import PropertyState

from helix.utils.address import normalize_address_str


class Command(BaseCommand):
    help = 'Updates normalized addresses'

    def add_arguments(self, parser):
        parser.add_argument('--org_id',
                            default=None,
                            help='Organization to update normalized addresses for',
                            action='store')

        parser.add_argument('--state_id',
                            default=None,
                            help='State to update normalized addresses for',
                            action='store')

    def handle(self, *args, **options):
        if options['org_id']:
            orgs = Organization.objects.filter(pk=options['org_id'])
        else:
            self.stdout.write("No organization passed in")

        if options['state_id']:
            properties = PropertyState.objects.filter(pk=options['state_id'])
            orgs = Organization.objects.filter(pk=properties.first().organization_id)
        else:
            properties = None

        for org in orgs:
            if properties is None:
                properties = PropertyState.objects.filter(organization=org)
            for prop in properties:
                if prop.address_line_1 is not None and prop.postal_code is not None:
                    normalized_address, extra_data = normalize_address_str(prop.address_line_1, prop.address_line_2, prop.postal_code, prop.extra_data)
                    self.stdout.write("ID: %s, Updating address from %s to %s" % (str(prop.id), prop.normalized_address, normalized_address))
                    prop.normalized_address = normalized_address
                    prop.extra_data = extra_data
                    prop.save()

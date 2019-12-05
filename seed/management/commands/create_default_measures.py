# -*- coding: utf-8 -*-
"""
:copyright (c) 2014 - 2018, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Department of Energy) and contributors. All rights reserved.  # NOQA
:author
"""
from django.core.management.base import BaseCommand

from seed.lib.superperms.orgs.models import Organization
from seed.models import Measure


class Command(BaseCommand):
    help = 'Creates the default measures of an organization if there are none'

    def add_arguments(self, parser):
        parser.add_argument('--org_id',
                            default=None,
                            help='Organization to add defaut measures',
                            action='store')

    def handle(self, *args, **options):
        if options['org_id']:
            orgs = Organization.objects.filter(pk=options['org_id'])
        else:
            orgs = Organization.objects.all().order_by('id')

        for org in orgs:
            self.stdout.write("Checking if organization %s has any measures" % org.id)
            if Measure.objects.filter(organization=org).count() == 0:
                self.stdout.write("  Organization has no measures, adding")
                Measure.populate_measures(org.id)
            else:
                self.stdout.write("  Organization already has measures, skipping")

# -*- coding: utf-8 -*-
"""
:copyright (c) 2014 - 2019, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Department of Energy) and contributors. All rights reserved.  # NOQA
:author
"""
from django.core.management.base import BaseCommand
from django.db.models import Q

from seed.lib.superperms.orgs.models import Organization
from seed.models import Column

class Command(BaseCommand):
    help = 'Updates the columns in the parent organization to include the ones in sub-organizations.'

    def add_arguments(self, parser):
        parser.add_argument('--org_id',
                            help='Organization of which to update columns',
                            default=None,
                            action='store')

    def handle(self, *args, **options):
        if options['org_id']:
            orgs = Organization.objects.filter(pk=options['org_id'])
        else:
            # Filter out sub-organizations
            orgs = Organization.objects.filter(parent_org=None).order_by('id')
        for org in orgs:
            self.stdout.write("Updating columns for organization %s" % org.id)
            sub_orgs = Organization.objects.filter(parent_org=org.pk)
            for sub_org in sub_orgs:
                columns = Column.objects.filter(organization=sub_org.pk)
                for column in columns:
                    if Column.objects.filter(organization=org.pk,
                                              column_name=column.column_name).count() > 0:
                        break
                    parent_col = Column.objects.get(pk=column.pk)
                    parent_col.pk = None
                    parent_col.organization = org
                    parent_col.save()
                    self.stdout.write("Column %s added" % parent_col.column_name)


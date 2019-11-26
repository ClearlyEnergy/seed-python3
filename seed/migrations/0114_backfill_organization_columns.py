# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, transaction


def fill(apps, schema_editor):
    Column = apps.get_model("seed", "Column")
    Organization = apps.get_model("orgs", "Organization")
    with transaction.atomic():
        orgs = Organization.objects.filter(parent_org=None).order_by('id')
        for org in orgs:
            sub_orgs = Organization.objects.filter(parent_org=org.pk)
            for sub_org in sub_orgs:
                columns = Column.objects.filter(organization=sub_org.pk)
                for column in columns:
                    if Column.objects.filter(organization=org.pk, column_name=column.column_name).count() > 0:
                        break
                    parent_col = Column.objects.get(pk=column.pk)
                    parent_col.pk = None
                    parent_col.organization = org
                    parent_col.save()


class Migration(migrations.Migration):

    dependencies = [
        ('seed', '0113_column_geocoding_order'),
    ]

    operations = [
        migrations.RunPython(fill)
    ]

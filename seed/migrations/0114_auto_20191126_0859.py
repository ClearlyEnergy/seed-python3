# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2019-11-26 16:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seed', '0113_column_geocoding_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='propertystate',
            name='county',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='propertystate',
            name='data_quality',
            field=models.IntegerField(blank=True, choices=[(1, 'Warning'), (2, 'Error')], null=True),
        ),
        migrations.AlterField(
            model_name='propertymeasure',
            name='application_scale',
            field=models.IntegerField(choices=[(1, 'Individual system'), (2, 'Multiple systems'), (3, 'Individual premise'), (4, 'Multiple premises'), (5, 'Entire facility'), (6, 'Entire site'), (7, 'Ground Mounted'), (8, 'Roof Mounted'), (8, 'Solar Canopy')], default=5),
        ),
        migrations.AlterUniqueTogether(
            name='propertymeasure',
            unique_together=set([]),
        ),
    ]

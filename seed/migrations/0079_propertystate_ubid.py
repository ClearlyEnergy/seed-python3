# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-12-15 15:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seed', '0078_auto_20171214_0846'),
    ]

    operations = [
        migrations.AddField(
            model_name='propertystate',
            name='ubid',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
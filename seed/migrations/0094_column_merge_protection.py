# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-08-24 17:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seed', '0093_auto_20180817_1112'),
    ]

    operations = [
        migrations.AddField(
            model_name='column',
            name='merge_protection',
            field=models.IntegerField(choices=[(0, b'Favor New'), (1, b'Favor Existing')], default=0),
        ),
    ]
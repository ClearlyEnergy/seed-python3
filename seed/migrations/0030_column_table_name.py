# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-08-31 15:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seed', '0029_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='column',
            name='table_name',
            field=models.CharField(blank=True, db_index=True, max_length=512),
        ),
    ]
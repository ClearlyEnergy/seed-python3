# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-07-29 18:37
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('seed', '0020_auto_20160725_1033'),
    ]

    operations = [
        migrations.CreateModel(
            name='PropertyAuditLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation_dat', models.DateTimeField()),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('childstate_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='propertyauditlog__childstate_id', to='seed.PropertyState')),
                ('parentstate_id1', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='propertyauditlog__parentstate_id1', to='seed.PropertyState')),
                ('parentstate_id2', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='propertyauditlog__parentstate_id2', to='seed.PropertyState')),
            ],
        ),
        migrations.CreateModel(
            name='TaxLotAuditLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation_date', models.DateTimeField()),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('childstate_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='taxlotauditlog__childstate_id', to='seed.TaxLotState')),
                ('parentstate_id1', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='taxlotauditlog__parentstate_id1', to='seed.TaxLotState')),
                ('parentstate_id2', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='taxlotauditlog__parentstate_id2', to='seed.TaxLotState')),
            ],
        ),
    ]
# Generated by Django 3.2.13 on 2022-08-05 00:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orgs', '0022_auto_20220711_1928'),
        ('seed', '0174_fix_ghg_columns'),
    ]

    operations = [
        migrations.CreateModel(
            name='FilterGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('inventory_type', models.IntegerField(choices=[(0, 'Property'), (1, 'Tax Lot')], default=0)),
                ('query_dict', models.JSONField(default=dict)),
                ('label_logic', models.IntegerField(choices=[(0, 'and'), (1, 'or'), (2, 'exclude')], default=0)),
                ('labels', models.ManyToManyField(to='seed.StatusLabel')),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='filter_groups', to='orgs.organization')),
            ],
            options={
                'ordering': ['id'],
                'unique_together': {('name', 'organization')},
            },
        ),
    ]
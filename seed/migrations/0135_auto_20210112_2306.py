# Generated by Django 2.2.13 on 2021-01-12 23:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seed', '0134_auto_20201217_2236'),
    ]

    operations = [
        migrations.AlterField(
            model_name='analysisoutputfile',
            name='content_type',
            field=models.IntegerField(choices=[(1, 'BuildingSync'), (100, 'PNG')]),
        ),
    ]

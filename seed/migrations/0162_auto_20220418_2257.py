# Generated by Django 3.2.12 on 2022-04-18 22:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seed', '0161_alter_inventorydocument_file_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='datalogger',
            name='is_occupied_data',
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='sensorreading',
            name='is_occupied',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]
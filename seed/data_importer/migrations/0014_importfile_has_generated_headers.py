# Generated by Django 2.2.13 on 2020-09-11 15:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_importer', '0013_importfile_raw_property_state_to_filename'),
    ]

    operations = [
        migrations.AddField(
            model_name='importfile',
            name='has_generated_headers',
            field=models.BooleanField(default=False),
        ),
    ]

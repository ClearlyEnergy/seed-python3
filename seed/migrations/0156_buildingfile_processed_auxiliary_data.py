# Generated by Django 3.2.7 on 2021-11-04 20:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seed', '0155_propertystate_egrid_subregion_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='buildingfile',
            name='processed_auxiliary_data',
            field=models.BooleanField(default=False),
        ),
    ]

# Generated by Django 3.2.7 on 2021-09-22 19:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seed', '0149_auto_20210922_1740'),
    ]

    operations = [
        migrations.AlterField(
            model_name='greenassessmentproperty',
            name='eligibility',
            field=models.BooleanField(null=True),
        ),
        migrations.AlterField(
            model_name='projectpropertyview',
            name='compliant',
            field=models.BooleanField(null=True),
        ),
        migrations.AlterField(
            model_name='projecttaxlotview',
            name='compliant',
            field=models.BooleanField(null=True),
        ),
    ]

# Generated by Django 3.2.14 on 2022-09-12 18:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seed', '0177_compliance_metric'),
    ]

    operations = [
        migrations.AlterField(
            model_name='compliancemetric',
            name='emission_metric_type',
            field=models.IntegerField(blank=True, choices=[(0, 'Target > Actual for Compliance'), (1, 'Actual > Target for Compliance')], null=True),
        ),
        migrations.AlterField(
            model_name='compliancemetric',
            name='energy_metric_type',
            field=models.IntegerField(blank=True, choices=[(0, 'Target > Actual for Compliance'), (1, 'Actual > Target for Compliance')], null=True),
        ),
    ]
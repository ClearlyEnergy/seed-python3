# Generated by Django 3.2.18 on 2023-04-27 15:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('seed', '0193_remove_null_taxlot_views'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taxlotview',
            name='taxlot',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='views', to='seed.taxlot'),
        ),
    ]
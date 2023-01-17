# Generated by Django 3.2.13 on 2022-05-11 18:29

from django.db import migrations, models, transaction
import django.db.models.deletion


def forwards(apps, schema_editor):
    DerivedColumn = apps.get_model("seed", "DerivedColumn")
    Column = apps.get_model("seed", "Column")

    with transaction.atomic():
        Column.objects.all().update(derived_column=None)

        table_name = {0: 'PropertyState', 1: 'TaxLotState'}
        for dc in DerivedColumn.objects.all():
            # create the column if it didn't exist, otherwise, just get it
            # to not create a new one.
            column_data = {
                "organization": dc.organization,
                "table_name": table_name[dc.inventory_type],
                "column_name": dc.name,
            }
            display_name = dc.name
            
            # check if the column name exists, if so, then increment the name
            for i_name in range(100):
                exists = Column.objects.filter(**column_data).exists()
                if not exists:
                    break
                else:
                    display_name = f"{dc.name} Derived {i_name + 1}"
                    # column name must equal the derived column name
                    column_data["column_name"] = display_name

            Column.objects.create(
                **column_data,
                derived_column=dc,
                display_name=display_name,
                column_description=display_name,
                is_extra_data=False
            )
            
            # now update the derived column's name
            dc.name = display_name
            dc.save()

class Migration(migrations.Migration):

    dependencies = [
        ('seed', '0169_auto_20220616_1028'),
    ]

    operations = [
        migrations.AddField(
            model_name='column',
            name='derived_column',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='seed.derivedcolumn'),
        ),
        migrations.RunPython(forwards),
    ]

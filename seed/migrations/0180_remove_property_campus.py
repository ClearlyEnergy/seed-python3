# Generated by Django 3.2.15 on 2022-11-13 19:45

from django.db import migrations


def remove_old_campus_column(apps, schema_editor):
    """Remove the existence of Property.campus"""
    Organization = apps.get_model("orgs", "Organization")

    for org in Organization.objects.all():
        print(f'processing organization: {org.id}:{org.name}')
        # find the problematic columns
        columns = org.column_set.filter(column_name='campus', table_name="Property")
        # find the newest column, and delete that one.
        if len(columns) >= 1:
            columns.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('seed', '0179_auto_20220916_0927'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='property',
            name='campus',
        ),
        migrations.RunPython(remove_old_campus_column),
    ]
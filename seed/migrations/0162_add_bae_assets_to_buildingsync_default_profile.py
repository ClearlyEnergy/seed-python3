# Generated by Django 3.2.12 on 2022-04-14 20:57

from django.db import migrations

from seed.lib.xml_mapping.mapper import default_buildingsync_profile_mappings


def recreate_default_bsync_presets(apps, schema_editor):
    """create a default BuildingSync column mapping preset for each organization"""
    Organization = apps.get_model("orgs", "Organization")

    # profile number for 'BuildingSync Default' profile is 1
    prof_type = 1

    for org in Organization.objects.all():
        bsync_mapping_name = 'BuildingSync v2.0 Defaults'
        # first find current BuildingSync mapping and delete
        profiles = org.columnmappingprofile_set.filter(profile_type=prof_type)

        for prof in profiles:
            prof.delete()

        # then recreate including BAE fields with updated "default_buildingsync_profile_mappings" method
        org.columnmappingprofile_set.create(
            name=bsync_mapping_name,
            mappings=default_buildingsync_profile_mappings(),
            profile_type=prof_type
        )


class Migration(migrations.Migration):

    dependencies = [
        ('seed', '0161_alter_inventorydocument_file_type'),
    ]

    operations = [
        migrations.RunPython(recreate_default_bsync_presets)
    ]

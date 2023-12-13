# Generated by Django 3.2.13 on 2022-06-16 17:28

from django.db import migrations


def add_new_bsync_mappings(apps, schema_editor):
    """create a default BuildingSync column mapping preset for each organization"""
    Organization = apps.get_model("orgs", "Organization")

    for org in Organization.objects.all():
        bsync_mapping_name = 'BuildingSync v2.0 Defaults'
        # first find current BuildingSync mapping, 'BuildingSync Default' profile is 1
        profiles = org.columnmappingprofile_set.filter(profile_type=1)
        # 'Audit Template Building Id' name matches the automatically generated field name from
        # the default_buildingsync_profile_mappings method.
        new_mappings = [
            {
                'from_field': '/auc:BuildingSync/auc:Facilities/auc:Facility/auc:Sites/auc:Site/auc:Buildings/auc:Building/auc:PremisesIdentifiers/auc:PremisesIdentifier[auc:IdentifierCustomName="Audit Template Building ID"]/auc:IdentifierValue',
                'from_field_value': 'text',
                'from_units': None,
                'to_table_name': 'PropertyState',
                'to_field': 'Audit Template Building Id',
            },
            {
                'from_field': '/auc:BuildingSync/auc:Facilities/auc:Facility/auc:Sites/auc:Site/auc:Buildings/auc:Building/auc:PremisesIdentifiers/auc:PremisesIdentifier[auc:IdentifierCustomName="Portfolio Manager Building ID"]/auc:IdentifierValue',
                'from_field_value': 'text',
                'from_units': None,
                'to_table_name': 'PropertyState',
                'to_field': 'pm_property_id',
            }
        ]

        for prof in profiles:
            for new_mapping in new_mappings:
                # verify that the new mapping does not already exist, only check the to_table_name
                # and to_field. We don't want to create two mappings to the same table/field.
                map_exist_check = [{'f': m['to_field'], 't': m['to_table_name']} for m in prof.mappings]
                if {'f': new_mapping['to_field'], 't': new_mapping['to_table_name']} in map_exist_check:
                    print(f"BuildingSync mapping already exists for {new_mapping['to_field']}, skipping")
                    continue
                else:
                    # add the mapping since it doesn't already exist
                    prof.mappings.append(new_mapping)

            prof.save()


class Migration(migrations.Migration):

    dependencies = [
        ('seed', '0168_datalogger_identifier'),
    ]

    operations = [
        migrations.RunPython(add_new_bsync_mappings),
    ]
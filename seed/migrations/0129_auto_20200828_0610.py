# Generated by Django 2.2.13 on 2020-08-28 13:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orgs', '0013_organization_comstock_enabled'),
        ('seed', '0128_auto_20200810_1731'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ColumnListSetting',
            new_name='ColumnListProfile',
        ),
        migrations.RenameModel(
            old_name='ColumnListSettingColumn',
            new_name='ColumnListProfileColumn',
        ),
        migrations.RenameField(
            model_name='columnlistprofile',
            old_name='settings_location',
            new_name='profile_location',
        ),
        migrations.RenameField(
            model_name='columnlistprofilecolumn',
            old_name='column_list_setting',
            new_name='column_list_profile',
        ),
        migrations.AlterField(
            model_name='columnlistprofile',
            name='columns',
            field=models.ManyToManyField(related_name='column_list_profiles', through='seed.ColumnListProfileColumn', to='seed.Column'),
        ),
        migrations.AlterField(
            model_name='columnlistprofile',
            name='profile_location',
            field=models.IntegerField(choices=[(0, 'List View Profile'), (1, 'Detail View Profile')], default=0),
        ),
    ]
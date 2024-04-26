# !/usr/bin/env python
# encoding: utf-8
"""
SEED Platform (TM), Copyright (c) Alliance for Sustainable Energy, LLC, and other contributors.
See also https://github.com/seed-platform/seed/main/LICENSE.md

:author Nicholas Long <nicholas.long@nrel.gov>
"""
from rest_framework import serializers

from seed.models import BuildingFile
from seed.serializers.base import ChoiceField

from django.conf import settings
from seed.utils.presigned_url import create_presigned_url


class BuildingFileSerializer(serializers.ModelSerializer):
    file_type = ChoiceField(choices=BuildingFile.BUILDING_FILE_TYPES)
    organization_id = serializers.IntegerField(allow_null=True, read_only=True)
    download_file = serializers.SerializerMethodField()

    class Meta:
        model = BuildingFile
        fields = '__all__'

    def get_download_file(self, obj):
        url = ""
        if settings.USE_S3 is True:
            url = create_presigned_url(settings.AWS_STORAGE_BUCKET_NAME, f"{obj.file}", 604800)
        else:
            url = "/api/v3/media/" + str(obj.filename)
        return url

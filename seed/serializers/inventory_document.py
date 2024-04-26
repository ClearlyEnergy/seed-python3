# !/usr/bin/env python
# encoding: utf-8
"""
SEED Platform (TM), Copyright (c) Alliance for Sustainable Energy, LLC, and other contributors.
See also https://github.com/seed-platform/seed/main/LICENSE.md

:author Katherine Fleming <katherine.fleming@nrel.gov>
"""
from rest_framework import serializers

from seed.models import InventoryDocument
from seed.serializers.base import ChoiceField
from seed.utils.presigned_url import create_presigned_url
from django.conf import settings


class InventoryDocumentSerializer(serializers.ModelSerializer):
    file_type = ChoiceField(choices=InventoryDocument.FILE_TYPES)
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = InventoryDocument
        fields = '__all__'

    def get_download_url(self, obj):
        url = ""
        if settings.USE_S3 is True:
            url = create_presigned_url(settings.AWS_STORAGE_BUCKET_NAME, f"{obj.file}", 604800)
        else:
            url = "/api/v3/media/" + str(obj.filename)
        return url
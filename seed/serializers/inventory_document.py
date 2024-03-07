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

import logging
import boto3
from botocore.exceptions import ClientError
from django.conf import settings


def create_presigned_url(bucket_name, object_name, expiration=604800):
    # Generate a presigned URL for the S3 object
    s3_client = boto3.client('s3', region_name=settings.AWS_DEFAULT_REGION)
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration,
                                                    HttpMethod='GET')
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response


class InventoryDocumentSerializer(serializers.ModelSerializer):
    file_type = ChoiceField(choices=InventoryDocument.FILE_TYPES)
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = InventoryDocument
        fields = '__all__'

    def get_download_url(self, obj):
        url = ""
        if settings.USE_S3 is True:
            url = create_presigned_url(settings.AWS_STORAGE_BUCKET_NAME, f"{obj.file}")
        else:
            url = "/api/v3/media/" + str(obj.filename)
        return url
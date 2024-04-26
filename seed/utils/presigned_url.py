from django.conf import settings
import boto3
import logging
from botocore.exceptions import ClientError


def create_presigned_url(bucket_name, object_name, expiration):
    # Generate a presigned URL for the S3 object
    s3_client = boto3.client('s3', region_name=settings.AWS_S3_REGION_NAME)
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response

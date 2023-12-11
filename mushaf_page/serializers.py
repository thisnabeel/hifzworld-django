from rest_framework import serializers
from .models import MushafPage
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist


from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.shortcuts import render
import boto3
from botocore.exceptions import NoCredentialsError
from decouple import config
class MushafPageSerializer(serializers.ModelSerializer):

    class Meta:
        model = MushafPage
        fields = '__all__'

    def get_s3_url(self, obj):
        s3 = boto3.client(
            's3',
            aws_access_key_id=config('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY'),
            region_name=config('AWS_REGION_NAME'),
            config=boto3.session.Config(signature_version='s3v4')
        )

        s3_url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': config("AWS_STORAGE_BUCKET_NAME"), 'Key': obj.image_s3_key},
            ExpiresIn=3600  # Set the expiration time for the URL in seconds (adjust as needed)
        )
        return s3_url

from django.db import models
from mushaf.models import Mushaf  # Import the Mushaf model
from .thirteen_liner_image_urls import IMAGE_URLS  # Import the array
import re

import requests
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.shortcuts import render
import boto3
from botocore.exceptions import NoCredentialsError
from decouple import config


class MushafPage(models.Model):
    # Primary key
    id = models.AutoField(primary_key=True)

    # Add other fields as needed
    page_number = models.IntegerField(default=-1) # Add the page number field
    image_url = models.CharField(max_length=255, default="null")  # Adjust the max length as needed
    image_s3_key = models.CharField(max_length=255, default="null")  # Adjust the max length as needed
    mushaf = models.ForeignKey(Mushaf, on_delete=models.CASCADE)  # Adjust on_delete as needed

    class Meta:
        app_label = 'mushaf_page'

    def __str__(self):
        return f"MushafPage {self.id}"

    def create_mushaf_pages(mushaf_id):
        try:
            mushaf = Mushaf.objects.get(id=mushaf_id)  # Ensure the Mushaf object exists
        except Mushaf.DoesNotExist:
            print(f"Mushaf with id {mushaf_id} does not exist.")
            return

        # Delete existing MushafPage objects for the given Mushaf
        MushafPage.objects.filter(mushaf_id=mushaf_id).delete()

        for index, url in enumerate(IMAGE_URLS):
            match = re.search(r'/L(\d+)\.GIF$', url)
            page_number = int(match.group(1))

            MushafPage.objects.create(
                mushaf=mushaf,
                page_number=page_number,
                image_url=url,
            )
            print(page_number, url)
    
    def saveMushafPages(mushaf_id):
        pages = MushafPage.objects.filter(mushaf_id=mushaf_id).order_by('page_number')
        for page in pages:
            # print(save_to_s3)
            save = MushafPage.save_to_s3(page)
            print(save)

        return

    def save_to_s3(page):
        # Replace 'YOUR_FILE_URL' with the actual URL of the file you want to download
        file_url = page.image_url
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
            }
            response = requests.get(file_url, headers=headers)
            response.raise_for_status()  # Raise an exception for bad responses (4xx and 5xx)
        except requests.exceptions.RequestException as e:
            print(f"Error downloading file from URL: {str(e)}")
            return HttpResponse(f"Error downloading file from URL: {str(e)}")

        if response.status_code == 200:
            # Replace 'your_bucket_name' and 'your_file_key' with your S3 bucket name and the desired file key
            bucket_name = 'hifzworld'
            file_name = f'{page.page_number}.gif'
            file_key = f'mushafs/{page.mushaf_id}/pages/{file_name}'

            # Upload the file to S3
            try:
                # s3 = boto3.client('s3')
                s3 = boto3.client(
                    's3',
                    aws_access_key_id=config('AWS_ACCESS_KEY_ID'),
                    aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY'),
                    region_name=config('AWS_REGION_NAME'),
                    config=boto3.session.Config(signature_version='s3v4')
                )
                
                # Use upload_fileobj instead of upload_file
                s3.upload_fileobj(ContentFile(response.content), bucket_name, file_key)
                # image_s3_key
                page.image_s3_key = file_key
                page.save()

                presigned_url = s3.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': bucket_name, 'Key': file_key},
                    ExpiresIn=3600  # Set the expiration time for the URL in seconds (adjust as needed)
                )

                # 
                print("Uploaded", {file_key})
                print("PreSignedUrl", presigned_url)
                return HttpResponse(f"File successfully uploaded to S3: {file_key}")
            except NoCredentialsError:
                print("No Creds")
                return HttpResponse("Credentials not available.")
            except Exception as e:
                print(f"Error uploading file to S3: {str(e)}")
                return HttpResponse(f"Error uploading file to S3: {str(e)}")
        else:
            print(f"Error downloading: {response.status_code}")
            return HttpResponse(f"Failed to download file from URL. Status code: {response.status_code}")

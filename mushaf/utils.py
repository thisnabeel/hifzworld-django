import os
import boto3
from django.core.files.base import ContentFile
from mushaf.models import Mushaf
from mushaf_page.models import MushafPage
from decouple import config
from botocore.exceptions import NoCredentialsError

def upload_mushaf_images(folder_path='13v2'):
    try:
        # Ensure the Mushaf object exists, create if not
        mushaf, created = Mushaf.objects.get_or_create(title=folder_path)

        # AWS S3 settings
        bucket_name = 'hifzworld'
        s3 = boto3.client(
            's3',
            aws_access_key_id=config('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY'),
            region_name=config('AWS_REGION_NAME'),
            config=boto3.session.Config(signature_version='s3v4')
        )

        # Delete existing pages for this Mushaf
        MushafPage.objects.filter(mushaf=mushaf).delete()

        # Process images in the specified folder
        image_files = sorted(
            [f for f in os.listdir(folder_path) if f.startswith('page_') and f.endswith('.png')],
            key=lambda x: int(x.split('_')[1].split('.')[0])
        )

        for image_file in image_files:
            page_number = int(image_file.split('_')[1].split('.')[0]) + 1  # Adjusting for mushaf page numbering
            file_path = os.path.join(folder_path, image_file)

            with open(file_path, 'rb') as img_file:
                file_content = img_file.read()
            
            s3_key = f'mushafs/{mushaf.id}/pages/{image_file}'
            try:
                s3.upload_fileobj(ContentFile(file_content), bucket_name, s3_key)
                
                # Create MushafPage record
                MushafPage.objects.create(
                    mushaf=mushaf,
                    page_number=page_number,
                    image_url=f'https://{bucket_name}.s3.amazonaws.com/{s3_key}',
                    image_s3_key=s3_key
                )

                print(f"Uploaded {image_file} to S3 as {s3_key}")

            except NoCredentialsError:
                print("AWS credentials not found.")
                return
            except Exception as e:
                print(f"Error uploading {image_file}: {e}")
                continue

        print(f"All images uploaded and pages created for Mushaf: {folder_path}")

    except Exception as e:
        print(f"Error processing mushaf images: {e}")

# Generated by Django 5.0 on 2023-12-11 10:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mushaf_page', '0003_mushafpage_image_saved_url'),
    ]

    operations = [
        migrations.RenameField(
            model_name='mushafpage',
            old_name='image_saved_url',
            new_name='image_s3_key',
        ),
    ]
# Generated by Django 5.0 on 2023-12-07 07:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mushaf', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='mushaf',
            name='title',
            field=models.CharField(default='null', max_length=255),
        ),
    ]

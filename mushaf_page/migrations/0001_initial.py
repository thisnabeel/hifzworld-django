# Generated by Django 5.0 on 2023-12-06 04:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('mushaf', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MushafPage',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('image_url', models.CharField(max_length=255)),
                ('mushaf', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mushaf.mushaf')),
            ],
        ),
    ]

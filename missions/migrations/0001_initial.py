# Generated by Django 5.0 on 2024-12-31 00:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MissionSet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('position', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Mission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.TextField()),
                ('verse_ref', models.CharField(max_length=255)),
                ('surah_number', models.IntegerField()),
                ('ayah_number', models.IntegerField()),
                ('position', models.IntegerField()),
                ('mission_set', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='missions', to='missions.missionset')),
            ],
        ),
    ]
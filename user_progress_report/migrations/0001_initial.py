# Generated by Django 5.0 on 2025-01-15 10:41

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('mushaf_page', '0005_mushafpage_verse_ref_end_mushafpage_verse_ref_start'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProgressReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('markings', models.IntegerField()),
                ('comment', models.TextField(blank=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('mushaf_page', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mushaf_page.mushafpage')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_progress_reports', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

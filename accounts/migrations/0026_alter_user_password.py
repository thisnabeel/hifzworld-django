# Generated by Django 5.0 on 2025-02-17 00:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0025_user_peer_id_alter_user_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='password',
            field=models.CharField(default='pbkdf2_sha256$720000$mDZLS5cYSu5PYp4tU9hDak$IAgAP84X1UU4msCL/6ZoMIDP0fcF2wEtN0uUY0aLeb4=', max_length=128),
        ),
    ]

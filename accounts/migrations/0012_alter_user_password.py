# Generated by Django 5.0 on 2023-12-16 15:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_alter_user_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='password',
            field=models.CharField(default='pbkdf2_sha256$720000$Sy8VRY72bg6Sjx3CbQjYYB$RxKYP4OY9cNU15ekCWrvNjaeaPOPopQT/4pNnajlIvc=', max_length=128),
        ),
    ]
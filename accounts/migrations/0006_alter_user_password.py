# Generated by Django 5.0 on 2023-12-12 04:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_alter_user_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='password',
            field=models.CharField(default='pbkdf2_sha256$720000$l9XEvsw7Qr8XQWMfujQZkk$6VuYGQRQdTfYVHRouDIGsCjLNxIhwQul22suQmDucBg=', max_length=128),
        ),
    ]

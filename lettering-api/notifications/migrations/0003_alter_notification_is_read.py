# Generated by Django 4.2.13 on 2024-06-18 13:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0002_notification_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='is_read',
            field=models.BooleanField(default=False),
        ),
    ]

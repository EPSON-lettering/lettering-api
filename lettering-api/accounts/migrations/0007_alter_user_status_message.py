# Generated by Django 4.2.13 on 2024-06-28 06:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_merge_0005_alter_user_status_message_0005_user_level'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='status_message',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]

# Generated by Django 4.2.13 on 2024-06-20 15:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_remove_user_printer_status_user_epson_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='status_message',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]

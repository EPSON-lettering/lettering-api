# Generated by Django 4.2.13 on 2024-06-13 09:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('letters', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='letter',
            name='image_url',
            field=models.FileField(null=True, upload_to='letters/'),
        ),
    ]

# Generated by Django 4.2.13 on 2024-06-14 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interests', '0003_interest_name_eng'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interest',
            name='image',
            field=models.FileField(null=True, upload_to='Interests/'),
        ),
    ]

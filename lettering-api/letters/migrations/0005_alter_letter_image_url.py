# Generated by Django 5.0.6 on 2024-06-22 11:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('letters', '0004_alter_letter_match_alter_letter_receiver_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='letter',
            name='image_url',
            field=models.CharField(),
        ),
    ]

# Generated by Django 5.0.6 on 2024-06-17 15:45

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("interests", "0005_question"),
    ]

    operations = [
        migrations.AddField(
            model_name="question",
            name="engText",
            field=models.TextField(default=None, null=True),
        ),
    ]
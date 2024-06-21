# Generated by Django 5.0.6 on 2024-06-21 15:02

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("printers", "0006_delete_epsonconnectemail"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="epsonconnectscandata",
            name="imagefile",
        ),
        migrations.RemoveField(
            model_name="epsonconnectscandata",
            name="letter",
        ),
        migrations.AddField(
            model_name="epsonconnectscandata",
            name="imageUrl",
            field=models.FileField(default=0, upload_to="letters/"),
            preserve_default=False,
        ),
    ]

# Generated by Django 4.2.13 on 2024-06-19 08:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('comments', '0001_initial'),
        ('letters', '0003_alter_letter_is_read'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('notifications', '0003_alter_notification_is_read'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='comment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='comments.comment'),
        ),
        migrations.AddField(
            model_name='notification',
            name='reply',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='comments.reply'),
        ),
        migrations.AddField(
            model_name='notification',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='notification',
            name='letter',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='letters.letter'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='type',
            field=models.CharField(choices=[('print_started', 'printStarted'), ('received', 'received'), ('comment', 'comment'), ('reply', 'reply')], max_length=30),
        ),
    ]

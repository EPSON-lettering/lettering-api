# Generated by Django 4.2.13 on 2024-06-17 08:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interests', '0005_question'),
        ('matching', '0002_alter_match_state_alter_match_withdraw_reason_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='provided_questions',
            field=models.ManyToManyField(blank=True, related_name='match_questions', to='interests.question'),
        ),
    ]

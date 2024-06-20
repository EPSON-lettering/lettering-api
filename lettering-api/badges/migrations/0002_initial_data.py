from django.db import migrations

def create_initial_badges(apps, schema_editor):
    Badge = apps.get_model('badges', 'Badge')
    BadgeStep = apps.get_model('badges', 'BadgeStep')

    badge1 = Badge.objects.create(name='편지의 제왕', description='편지를 n회 보낸 경우')
    BadgeStep.objects.create(badge=badge1, step_number=1, required_count=1)
    BadgeStep.objects.create(badge=badge1, step_number=2, required_count=3)
    BadgeStep.objects.create(badge=badge1, step_number=3, required_count=5)

    badge2 = Badge.objects.create(name='피드백 마스터', description='피드백을 n회 작성한 경우')
    BadgeStep.objects.create(badge=badge2, step_number=1, required_count=1)
    BadgeStep.objects.create(badge=badge2, step_number=2, required_count=5)
    BadgeStep.objects.create(badge=badge2, step_number=3, required_count=10)


class Migration(migrations.Migration):

    dependencies = [
        ('badges', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_initial_badges),
    ]

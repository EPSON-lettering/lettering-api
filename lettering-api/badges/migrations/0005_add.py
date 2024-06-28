from django.db import migrations

def create_initial_badges(apps, schema_editor):
    Badge = apps.get_model('badges', 'Badge')
    BadgeStep = apps.get_model('badges', 'BadgeStep')

    badge3 = Badge.objects.create(name='답장의 제왕', description='답장을 n회 보낸 경우')
    BadgeStep.objects.create(badge=badge3, step_number=1, required_count=1)
    BadgeStep.objects.create(badge=badge3, step_number=2, required_count=3)
    BadgeStep.objects.create(badge=badge3, step_number=3, required_count=5)

    badge4 = Badge.objects.create(name='꾸준학 학습자', description='n일 연속으로 편지를 보낸 경우')
    BadgeStep.objects.create(badge=badge4, step_number=1, required_count=3)
    BadgeStep.objects.create(badge=badge4, step_number=2, required_count=7)
    BadgeStep.objects.create(badge=badge4, step_number=3, required_count=10)


class Migration(migrations.Migration):

    dependencies = [
        ('badges', '0004_add'),
    ]

    operations = [
        migrations.RunPython(create_initial_badges),
    ]

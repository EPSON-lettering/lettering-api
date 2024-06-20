from django.db import models
from accounts.models import User

class Badge(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    icon = models.ImageField(upload_to='badge_icons/', null=True, blank=True)

    def __str__(self):
        return self.name

class BadgeStep(models.Model):
    badge = models.ForeignKey(Badge, related_name='steps', on_delete=models.CASCADE)
    step_number = models.IntegerField()
    required_count = models.IntegerField()

    class Meta:
        unique_together = ('badge', 'step_number')

    def __str__(self):
        return f'{self.badge.name} - 단계 {self.step_number}'

class UserBadge(models.Model):
    user = models.ForeignKey(User, related_name='user_badges', on_delete=models.CASCADE)
    badge = models.ForeignKey(Badge, related_name='user_badges', on_delete=models.CASCADE)
    step = models.ForeignKey(BadgeStep, related_name='user_badges', on_delete=models.CASCADE)
    progress = models.IntegerField(default=0)
    awarded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'badge', 'step')

    def __str__(self):
        return f'{self.user.nickname} - {self.badge.name} 단계 {self.step.step_number}'

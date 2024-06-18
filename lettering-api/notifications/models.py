from django.db import models
from letters.models import Letter


class Notification(models.Model):
    letter = models.ForeignKey(Letter, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=30, default='type')

from django.db import models
from letters.models import Letter
from accounts.models import User
from comments.models import Comment, Reply


class Notification(models.Model):
    TYPE_CHOICES = [
        ('print_started', 'printStarted'),
        ('received', 'received'),
        ('comment', 'comment'),
        ('reply', 'reply'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', default=1)
    letter = models.ForeignKey(Letter, on_delete=models.CASCADE, null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)
    reply = models.ForeignKey(Reply, on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=30, choices=TYPE_CHOICES)

from django.db import models
from accounts.models import User
from letters.models import Letter


class Comment(models.Model):
    COMMENT_TYPE_CHOICES = [
        ('feedback', '피드백'),
        ('chat', '채팅')
    ]
    letter = models.ForeignKey(Letter, related_name='comments', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='sent_comments', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_comments', on_delete=models.CASCADE)
    message = models.TextField(null=True, blank=True)
    image = models.CharField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=10, choices=COMMENT_TYPE_CHOICES)


class Reply(models.Model):
    comment = models.ForeignKey(Comment, related_name='replies', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='sent_replies', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_replies', on_delete=models.CASCADE)
    message = models.TextField()
    image = models.ImageField(upload_to='reply_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

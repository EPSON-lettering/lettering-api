from django.db import models
from accounts.models import User
from matching.models import Match


class Letter(models.Model):
    sender = models.ForeignKey(User, related_name='sent_letters', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_letters', on_delete=models.CASCADE)
    image_url = models.TextField()
    is_read = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)


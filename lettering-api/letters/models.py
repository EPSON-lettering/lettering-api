from django.db import models
from accounts.models import User
from matching.models import Match


class Letter(models.Model):
    sender = models.OneToOneField(User, related_name='sent_letters', on_delete=models.CASCADE)
    receiver = models.OneToOneField(User, related_name='received_letters', on_delete=models.CASCADE)
    image_url = models.FileField(upload_to='letters/', null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    match = models.OneToOneField(Match, on_delete=models.CASCADE)


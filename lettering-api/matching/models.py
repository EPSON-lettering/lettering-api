from django.db import models
from accounts.models import User, Language


class Match(models.Model):
    requester = models.ForeignKey(User, related_name='requested_matches', on_delete=models.CASCADE)
    acceptor = models.ForeignKey(User, related_name='accepted_matches', on_delete=models.CASCADE)
    native_lang = models.ForeignKey(Language, related_name='native_matches', on_delete=models.CASCADE)
    learning_lang = models.ForeignKey(Language, related_name='learning_matches', on_delete=models.CASCADE)
    state = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    withdraw_reason = models.TextField(null=True)
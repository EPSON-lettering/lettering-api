from django.db import models
from oauth.models import OauthUser
from django.utils import timezone


class Language(models.Model):
    lang_name = models.CharField(max_length=30)

    def __str__(self):
        return self.lang_name

class User(models.Model):
    oauth_id = models.ForeignKey(OauthUser, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=30)
    profile_image_url = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    withdraw_at = models.DateTimeField(null=True)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    printer_status = models.BooleanField()
    is_loggined = models.BooleanField()
    withdraw_reason = models.TextField(null=True)
    email = models.EmailField()

    def __str__(self):
        return self.nickname
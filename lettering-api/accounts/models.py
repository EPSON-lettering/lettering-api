from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
from oauth.models import OauthUser
from django.utils import timezone


class Language(models.Model):
    lang_name = models.CharField(max_length=30)

    def __str__(self):
        return self.lang_name


class User(AbstractBaseUser):
    USERNAME_FIELD = 'nickname'
    password = models.CharField(null=True)
    oauth = models.OneToOneField(OauthUser, on_delete=models.CASCADE, null=True, blank=True)
    nickname = models.CharField(max_length=30, unique=True)
    profile_image_url = models.FileField(upload_to='accounts/', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    withdraw_at = models.DateTimeField(null=True)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    epson_email: str = models.EmailField(null=True)
    is_loggined = models.BooleanField(default=False)
    withdraw_reason = models.TextField(null=True)
    email = models.EmailField()
    status_message = models.IntegerField(null=True, blank=True, default=0)
    level = models.IntegerField(default=1)
    none_profile_color = models.CharField(null=True, blank=True)

    def __str__(self):
        return self.nickname

    def change_letter_status(self, status):
        self.status_message = status.parse()
        self.save()

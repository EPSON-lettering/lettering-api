from django.db import models


class User(models.Model):
    id = models.IntegerField(primary_key=True)
    oauth_id = models.IntegerField()
    nickname = models.CharField(max_length=30,unique=True)
    profile_image_url = models.TextField(null=True)
    created_at = models.DateTimeField()
    withdraw_at = models.DateTimeField(null=True)
    language = models.IntegerField()
    printer_status = models.BooleanField()
    is_loggined = models.BooleanField()
    withdraw_reason = models.TextField(null=True)
    email = models.EmailField(null=True)
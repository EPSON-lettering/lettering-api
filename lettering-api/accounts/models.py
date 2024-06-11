from django.db import models

# Create your models here.
class User(models.Model):
    id = models.IntegerField(primary_key=True)
    oauth_id = models.IntegerField()
    nickname = models.CharField(max_length=30)
    profile_image_url = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField()
    withdraw_at = models.DateTimeField(null=True)
    language = models.IntegerField()
    printer_status = models.BooleanField()
    is_loggined = models.BooleanField()
    withdraw_reason = models.CharField(max_length=255, null=True)
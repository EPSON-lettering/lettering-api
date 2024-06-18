from django.db import models
from accounts.models import User


class EpsonConnectEmail(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    epsonEmail = User.epson_email


class EpsonConnectScanData(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    imagefile = models.ImageField(upload_to='letters/')

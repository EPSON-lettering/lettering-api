from django.db import models
from accounts.models import User
from letters.models import Letter


class EpsonConnectEmail(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    epsonEmail = User.epson_email


class EpsonConnectScanData(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    letter = models.ForeignKey(Letter, on_delete=models.CASCADE, default=1)
    imagefile = models.ImageField(upload_to='letters/')

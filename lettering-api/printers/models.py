from django.db import models
from accounts.models import User


class EpsonConnectEmail(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    deviceEmail = models.CharField(max_length=442)

    def __str__(self):
        return self.deviceEmail


class EpsonConnectScanData(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    imagefile = models.ImageField(upload_to='letters/')

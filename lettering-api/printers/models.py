from django.db import models
from accounts.models import User
from letters.models import Letter


class EpsonConnectScanData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    imageUrl = models.FileField(upload_to='letters/')

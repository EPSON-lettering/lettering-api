from django.db import models
from accounts.models import User
from letters.models import Letter


class EpsonConnectScanData(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    letter = models.ForeignKey(Letter, on_delete=models.CASCADE, default=1)
    imagefile = models.ImageField(upload_to='letters/')

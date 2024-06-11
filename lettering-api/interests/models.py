from django.db import models
from accounts.models import User


class Interest(models.Model):
    name = models.CharField(max_length=30)
    image = models.TextField()

    def __str__(self):
        return self.name


class UserInterest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    interest = models.ForeignKey(Interest, on_delete=models.CASCADE)


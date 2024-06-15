from django.db import models


class OauthUser(models.Model):
    provider = models.CharField(max_length=30)
    provider_id = models.TextField()

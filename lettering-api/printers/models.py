from django.db import models
from accounts.models import User
from letters.models import Letter


'''
    @deprecated 해당 모델을 활용할 수 없습니다. 
    전체적인 요구사항이 불일치합니다
'''
class EpsonConnectScanData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    imageUrl = models.FileField(upload_to='letters/')



class EpsonGlobalImageShare(models.Model):
    image_url = models.CharField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=9)
    created_at = models.DateTimeField(auto_now_add=True, null=True)


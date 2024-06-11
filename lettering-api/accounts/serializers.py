from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers
from .models import User


class NicknameCheckSerializer(serializers.Serializer):
    nickname = serializers.CharField(max_length=30, required=True)

    def validate_nickname(self, value):
        if User.objects.filter(nickname=value).exists():
            return False
        return True

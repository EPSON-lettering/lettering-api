from django.core.files import File
from rest_framework import serializers
from rest_framework.fields import empty

from .models import EpsonConnectScanData
from accounts.models import User
import base64


class EpsonConnectPrintSerializer(serializers.Serializer):
    imageFile = serializers.FileField()


class EpsonScanSerializer(serializers.ModelSerializer):
    class Meta:
        model = EpsonConnectScanData
        fields = '__all__'


class EpsonConnectEmailSerializer(serializers.Serializer):
    epsonEmail = serializers.CharField(source='epson_email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def create(self, validated_data):
        user = self.context['request'].user
        user.epson_email = validated_data["epsonEmail"]
        user.save()
        return user

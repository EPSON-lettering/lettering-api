from django.core.files import File
from rest_framework import serializers
from .models import EpsonConnectEmail, EpsonConnectScanData
from accounts.models import User
import base64


class EpsonConnectPrintSerializer(serializers.Serializer):
    imageFile = serializers.ImageField()
    deviceEmail = serializers.CharField()


class EpsonConnectAuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = EpsonConnectEmail
        fields = '__all__'

    def create(self, request):
        user = User.objects.get(id=request.user)
        device_email = request['deviceEmail']
        return EpsonConnectEmail.objects.create(user=user, deviceEmail=device_email)


class EpsonScanSerializer(serializers.ModelSerializer):
    class Meta:
        model = EpsonConnectScanData
        fields = '__all__'

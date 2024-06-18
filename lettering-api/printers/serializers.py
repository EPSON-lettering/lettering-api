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


class EpsonConnectEmailSerializer(serializers.ModelSerializer):
    epsonEmail = serializers.CharField(write_only=True)

    class Meta:
        model = EpsonConnectEmail
        fields = ['epsonEmail']

    def create(self, validated_data):
        user = self.context['user']
        user = User.objects.get(id=user)
        epson_email = validated_data['epsonEmail']

        try:
            epson_connect_email = EpsonConnectEmail.objects.get(user=user)
            epson_connect_email.epsonEmail = epson_email
            epson_connect_email.save()
        except EpsonConnectEmail.DoesNotExist:
            epson_connect_email = EpsonConnectEmail.objects.create(user=user, epsonEmail=epson_email)

        return epson_connect_email

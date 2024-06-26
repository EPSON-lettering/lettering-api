from rest_framework import serializers
from .models import Letter
from printers.models import EpsonGlobalImageShare
from matching.models import Match
import boto3
from botocore.config import Config
from accounts.models import User
from accounts.serializers import UserSerializer
import os
import uuid
from django.db import models

AWS_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
REGION = os.environ.get('AWS_S3_REGION_NAME')
config = Config(signature_version='v4')
CF_URL: str = os.environ.get('CF_URL')

class LetterSerializer(serializers.Serializer):
    scanData_id = serializers.IntegerField(read_only=True)

    def create(self, validated_data):
        ctx = self.context["request"]
        user = ctx.user
        match = Match.objects.get(requester=user)
        id = self.context["scan_id"]
        print(f'id: {id}')
        epson_image: EpsonGlobalImageShare = EpsonGlobalImageShare.objects.get(id=id)
        letter = Letter.objects.create(
            sender=user,
            receiver=match.acceptor,
            match=match,
            image_url=epson_image.image_url,
        )
        letter.save()
        return letter


class LetterModelSerializer(serializers.ModelSerializer):
    isRead = serializers.BooleanField(source="is_read")
    imageUrl = serializers.CharField(source="image_url")
    createdAt = serializers.DateTimeField(source="created_at")
    owner = serializers.SerializerMethodField()

    class Meta:
        model = Letter
        fields = ['id', 'imageUrl', 'sender', 'isRead', 'createdAt', 'owner']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def get_owner(self, obj):
        print(f'get_owner: {self.user}')
        if self.user is None:
            return None
        user = User.objects.get(id=self.user.id)
        return UserSerializer(user).data


class S3FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

    def create(self, validated_data):
        file = validated_data.get('file')
        filename = file.name
        s3 = boto3.client(
            's3',
            config=config,
            aws_access_key_id=AWS_ID,
            aws_secret_access_key=AWS_KEY,
            region_name=REGION
        )
        s3.upload_fileobj(
            file,
            BUCKET_NAME,
            filename
        )
        return {"file_url": f'{CF_URL}/{filename}'}

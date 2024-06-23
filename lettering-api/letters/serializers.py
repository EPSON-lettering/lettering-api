from rest_framework import serializers
from .models import Letter
from printers.models import EpsonConnectScanData
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


class LetterSerializer(serializers.Serializer):
    scanData_id = serializers.IntegerField(read_only=True)

    def create(self, validated_data):
        user = self.context['request'].user
        match = Match.objects.get(requester=user)
        ScanData = EpsonConnectScanData.objects.get(id=self.context['scanDataId'])
        letter = Letter.objects.create(
            sender=user,
            receiver=match.acceptor,
            match=match,
            image_url=ScanData['image_url'],
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
        print(f'file in S3FileUploadSerializer: {file}')
        s3 = boto3.client(
            's3',
            config=config,
            aws_access_key_id=AWS_ID,
            aws_secret_access_key=AWS_KEY,
            region_name=REGION
        )
        filename = f'{uuid.uuid4()}.png'
        s3.upload_fileobj(
            file,
            BUCKET_NAME,
            filename
        )
        url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': BUCKET_NAME, 'Key': filename},
        )

        return {"file_url": url}

from rest_framework import serializers
from .models import Letter
from printers.models import EpsonConnectScanData
from matching.models import Match
import boto3
import os
import uuid


AWS_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')


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

    class Meta:
        model = Letter
        fields = '__all__'


class ManualLetterSerializer(serializers.Serializer):
    pass


class S3FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

    def create(self, validated_data):
        file = validated_data.get('file')
        s3 = boto3.client(
            's3',
            aws_access_key_id=AWS_ID,
            aws_secret_access_key=AWS_KEY
        )
        filename = f'{uuid.uuid1()}.png'
        s3.upload_fileobj(
            file,
            BUCKET_NAME,
            filename
        )
        url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': BUCKET_NAME, 'Key': filename},
            ExpiresIn=3600
        )

        return {"file_url": url}

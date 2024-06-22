import boto3
import os
from matching.models import Match
from botocore.exceptions import ClientError
from rest_framework import serializers
from letters.models import Letter
from .models import EpsonConnectScanData


class EpsonConnectPrintSerializer(serializers.Serializer):
    imageFile = serializers.ImageField(required=True)


class EpsonScanSerializer(serializers.Serializer):
    imagefile = serializers.FileField()

    def create(self, validated_data):
        imagefile = validated_data['imagefile']
        user = self.context['request'].user

        # S3에 파일 업로드
        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        file_count = EpsonConnectScanData.objects.filter(user=user).count()
        file_name = f'{user.id}/{file_count + 1}.jpg'
        try:
            s3.upload_fileobj(
                imagefile,
                settings.AWS_STORAGE_BUCKET_NAME,
                file_name,
            )
        except ClientError as e:
            print(f"Error uploading file to S3: {e}")
            raise serializers.ValidationError("파일 업로드에 실패했습니다.")

        try:
            EpsonConnectScanData.objects.create(
                user=user,
                imageUrl=file_name,
            ).save()
        except ClientError as e:
            print(f"Error uploading file to S3: {e}")
            raise serializers.ValidationError("파일 업로드에 실패했습니다.")

        try:
            scan_data = EpsonConnectScanData.objects.create(
                user=user,
                imageUrl=file_name,
            )
            scan_data.save()
        except Exception as e:
            print(f"Error saving scan data: {e}")
            raise serializers.ValidationError("스캔 데이터 저장에 실패했습니다.")

        return validated_data


class EpsonConnectEmailSerializer(serializers.Serializer):
    epsonEmail = serializers.CharField(source='epson_email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def create(self, validated_data):
        user = self.context['request'].user
        user.epson_email = validated_data['epson_email']
        user.save()
        return user

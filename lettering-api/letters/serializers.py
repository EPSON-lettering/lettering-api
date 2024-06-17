from rest_framework import serializers
from .models import Letter


class LetterSerializer(serializers.ModelSerializer):
    imageUrl = serializers.ImageField(source='image_url')
    isRead = serializers.BooleanField()
    createdAt = serializers.DateTimeField(source='created_at')

    class Meta:
        model = Letter
        fields = ['id', 'receiver', 'sender', 'imageUrl', 'isRead', 'createdAt']

from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    isRead = serializers.BooleanField(source='is_read')
    createdAt = serializers.DateTimeField(source='created_at')

    class Meta:
        model = Notification
        fields = ['id', 'letter', 'message', 'isRead', 'createdAt', 'type']
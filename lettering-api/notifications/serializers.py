from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    createdAt = serializers.DateTimeField(source='created_at')
    isRead = serializers.BooleanField(source='is_read')

    class Meta:
        model = Notification
        fields = ['id', 'user', 'letter', 'comment', 'reply', 'message', 'isRead', 'createdAt', 'type']
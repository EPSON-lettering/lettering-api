from rest_framework import serializers
from .models import Comment, Reply
from accounts.models import User
from notifications.models import Notification

class CommentUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'nickname', 'profile_image_url']

class CommentSerializer(serializers.ModelSerializer):
    createdAt = serializers.DateTimeField(source='created_at')
    image = serializers.ImageField(required=False)
    sender = CommentUserSerializer()
    receiver = CommentUserSerializer()

    class Meta:
        model = Comment
        fields = ['id', 'letter', 'sender', 'receiver', 'message', 'image', 'createdAt', 'type']

    def create(self, validated_data):
        comment = super().create(validated_data)
        Notification.objects.create(
            user=comment.receiver,
            comment=comment,
            message=f'{comment.sender.nickname} 님이 새로운 {comment.type}을(를) 보냈습니다!',
            type='comment'
        )
        return comment

class ReplySerializer(serializers.ModelSerializer):
    createdAt = serializers.DateTimeField(source='created_at')
    image = serializers.ImageField(required=False)
    sender = CommentUserSerializer()
    receiver = CommentUserSerializer()

    class Meta:
        model = Reply
        fields = ['id', 'comment', 'sender', 'receiver', 'message', 'image', 'createdAt']

    def create(self, validated_data):
        reply = super().create(validated_data)
        Notification.objects.create(
            user=reply.receiver,
            reply=reply,
            message=f'내 피드백/채팅에 새로운 답글이 달렸습니다!',
            type='reply'
        )
        return reply

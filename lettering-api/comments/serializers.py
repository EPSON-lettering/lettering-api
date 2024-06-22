from rest_framework import serializers
from .models import Comment, Reply
from accounts.models import User
from accounts.serializers import UserSerializer
from notifications.models import Notification


class CommentUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'nickname', 'profile_image_url']


class CommentSerializer(serializers.ModelSerializer):
    createdAt = serializers.DateTimeField(source='created_at')
    image = serializers.ImageField(required=False)
    sender = UserSerializer()
    receiver = UserSerializer()

    class Meta:
        model = Comment
        fields = ['id', 'letter', 'sender', 'receiver', 'message', 'image', 'createdAt', 'type']

    def __init__(self, *args, **kwargs):
        self.sender_data = kwargs.pop('sender_data', None)
        super().__init__(*args, **kwargs)

    def get_sender(self, obj):
        print(f'sender_data: {self.sender_data}')
        if self.sender_data is None:
            return None
        return UserSerializer(self.sender_data).data


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
    sender = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    receiver = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

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
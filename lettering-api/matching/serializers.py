from rest_framework import serializers
from .models import MatchRequest, Match
from accounts.models import User

class MatchUserSerializer(serializers.ModelSerializer):
    profileImageUrl = serializers.CharField(source='profile_image_url')

    class Meta:
        model = User
        fields = ['id', 'nickname', 'profileImageUrl', 'language']

class MatchRequestSerializer(serializers.ModelSerializer):
    requester = MatchUserSerializer()
    receiver = MatchUserSerializer()
    createdAt = serializers.DateTimeField(source='created_at')

    class Meta:
        model = MatchRequest
        fields = ['id', 'requester', 'receiver', 'state', 'createdAt']

class MatchSerializer(serializers.ModelSerializer):
    requester = MatchUserSerializer()
    acceptor = MatchUserSerializer()
    nativeLang = serializers.CharField(source='native_lang')
    learningLang = serializers.CharField(source='learning_lang')
    createdAt = serializers.DateTimeField(source='created_at')
    withdrawReason = serializers.CharField(source='withdraw_reason', allow_null=True, allow_blank=True)

    class Meta:
        model = Match
        fields = ['requester', 'acceptor', 'state', 'nativeLang', 'learningLang', 'createdAt', 'withdrawReason']

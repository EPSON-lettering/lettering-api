from rest_framework import serializers
from .models import MatchRequest, Match
from accounts.models import User

class MatchUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'nickname', 'profile_image_url', 'language']

class MatchRequestSerializer(serializers.ModelSerializer):
    requester = MatchUserSerializer()
    receiver = MatchUserSerializer()

    class Meta:
        model = MatchRequest
        fields = ['id', 'requester', 'receiver', 'state', 'created_at']

class MatchSerializer(serializers.ModelSerializer):
    requester = MatchUserSerializer()
    acceptor = MatchUserSerializer()

    class Meta:
        model = Match
        fields = ['requester', 'acceptor', 'state', 'native_lang', 'learning_lang', 'created_at', 'withdraw_reason']

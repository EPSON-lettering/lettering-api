from rest_framework import serializers
from .models import MatchRequest, Match
from accounts.models import User
from interests.serializers import InterestSerializer


class MatchUserSerializer(serializers.ModelSerializer):
    profileImageUrl = serializers.CharField(source='profile_image_url')

    class Meta:
        model = User
        fields = ['id', 'nickname', 'profileImageUrl', 'language']


class MatchRequestSerializer(serializers.ModelSerializer):
    requester = MatchUserSerializer()
    receiver = MatchUserSerializer()
    createdAt = serializers.DateTimeField(source='created_at')
    duplicateInterests = serializers.SerializerMethodField()

    class Meta:
        model = MatchRequest
        fields = ['id', 'requester', 'receiver', 'state', 'createdAt', 'duplicateInterests']

    def __init__(self, *args, **kwargs):
        self.interests = kwargs.pop('interests', [])
        super().__init__(*args, **kwargs)

    def get_duplicateInterests(self, obj):
        return [InterestSerializer(interest).data for interest in self.interests]


class MatchSerializer(serializers.ModelSerializer):
    requester = MatchUserSerializer()
    acceptor = MatchUserSerializer()
    nativeLang = serializers.CharField(source='native_lang')
    learningLang = serializers.CharField(source='learning_lang')
    createdAt = serializers.DateTimeField(source='created_at')
    withdrawReason = serializers.CharField(source='withdraw_reason', allow_null=True, allow_blank=True)

    class Meta:
        model = Match
        fields = ['id', 'requester', 'acceptor', 'state', 'nativeLang', 'learningLang', 'createdAt', 'withdrawReason']


class SearchMatchDetailsSerializer(serializers.ModelSerializer):
    acceptor = MatchUserSerializer()
    createdAt = serializers.DateTimeField(source='created_at')

    class Meta:
        model = Match
        fields = ['id', 'acceptor', 'createdAt']


class IntegrateSearchMatchDetailsSerializer(serializers.ModelSerializer):
    interests = serializers.SerializerMethodField()
    requester = MatchUserSerializer()
    acceptor = MatchUserSerializer()
    createdAt = serializers.DateTimeField(source='created_at')

    class Meta:
        model = Match
        fields = ['id', 'requester', 'acceptor', 'createdAt', 'interests']

    def __init__(self, *args, **kwargs):
        self.interests = kwargs.pop('interests', [])
        self.match_details = kwargs.pop('match_details', None)
        super().__init__(*args, **kwargs)

    def get_interests(self, obj):
        return [InterestSerializer(interest).data for interest in self.interests]
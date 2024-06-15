from rest_framework import serializers
from .models import User, Language
from oauth.models import OauthUser
from interests.models import Interest, UserInterest
import re


class NicknameCheckSerializer(serializers.Serializer):
    nickname = serializers.CharField(max_length=13, required=True)

    def validate_nickname(self, value):
        if User.objects.filter(nickname=value).exists():
            raise serializers.ValidationError("이미 사용 중인 닉네임입니다!")

        if not re.match(r'^[가-힣A-Za-z0-9_]+$', value):
            raise serializers.ValidationError("문자 또는 숫자, 특수문자(_)만 가능합니다.")

        return value


class RegisterUserSerializer(serializers.Serializer):
    unique = serializers.CharField(max_length=255)
    provider = serializers.CharField(max_length=30)
    language = serializers.CharField(max_length=30)
    nickname = serializers.CharField(max_length=30)
    interests = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False
    )

    def create(self, validated_data):
        language_name = validated_data['language']
        language = Language.objects.get(lang_name=language_name)

        oauth_user, created = OauthUser.objects.get_or_create(
            provider=validated_data['provider'],
            provider_id=validated_data['unique']
        )

        user = User.objects.create(
            oauth=oauth_user,
            email=validated_data['unique'],
            nickname=validated_data['nickname'],
            language=language
        )

        interests_ids = validated_data['interests']
        for interest_id in interests_ids:
            interest = Interest.objects.get(id=interest_id)
            UserInterest.objects.create(user=user, interest=interest)

        return user

class UserSerializer(serializers.ModelSerializer):
    oauthId = serializers.PrimaryKeyRelatedField(source='oauth_id', read_only=True)
    profileImageUrl = serializers.FileField(source='profile_image_url', read_only=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    withdrawAt = serializers.DateTimeField(source='withdraw_at', read_only=True)
    printerStatus = serializers.BooleanField(source='printer_status', read_only=True)
    isLoggined = serializers.BooleanField(source='is_loggined', read_only=True)
    withdrawReason = serializers.CharField(source='withdraw_reason', read_only=True)
    class Meta:
        model = User
        fields = ['id', 'oauthId', 'nickname', 'profileImageUrl', 'createdAt', 'withdrawAt', 'language', 'printerStatus', 'isLoggined', 'withdrawReason', 'email']

    def get_interests(self, obj):
        user_interests = UserInterest.objects.filter(user=obj)
        return [user_interest.interest for user_interest in user_interests]

class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = '__all__'

class GoogleCallbackSerializer(serializers.Serializer):
    code = serializers.CharField(required=True)
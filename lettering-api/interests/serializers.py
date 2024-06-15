from rest_framework import serializers
from .models import Interest, UserInterest
from accounts.models import User


class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = '__all__'


class UserInterestChangeSerializer(serializers.Serializer):
    nickname = serializers.CharField(max_length=30, required=True)
    interests = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False
    )

    def validate_nickname(self, value):
        try:
            user = User.objects.get(nickname=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("닉네임과 일치하는 유저가 존재하지 않습니다.")
        self.user = user
        return value

    def validate_interests(self, value):
        if not value:
            raise serializers.ValidationError("관심사를 선택해주세요.")
        return value

    def create(self, validated_data):
        user = self.user
        UserInterest.objects.filter(user=user).delete()
        interests = validated_data['interests']
        for interest_id in interests:
            try:
                interest = Interest.objects.get(id=interest_id)
                UserInterest.objects.create(user=user, interest=interest)
            except Interest.DoesNotExist:
                continue
        return user

from rest_framework import serializers
from .models import UserBadge, Badge, BadgeStep


class BadgeStepSerializer(serializers.ModelSerializer):
    stepNumber = serializers.IntegerField(source='step_number')
    requiredCount = serializers.IntegerField(source='required_count')

    class Meta:
        model = BadgeStep
        fields = ['stepNumber', 'requiredCount']


class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = ['name', 'description', 'icon']


class UserBadgeSerializer(serializers.ModelSerializer):
    badge = BadgeSerializer()
    step = BadgeStepSerializer()

    class Meta:
        model = UserBadge
        fields = ['id', 'user', 'badge', 'step', 'progress', 'awarded_at']
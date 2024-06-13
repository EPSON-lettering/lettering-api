from rest_framework import serializers
from .models import Interest,UserInterest


class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = '__all__'


class UserInterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInterest
        fields = ['id', 'user']

    def create(self, validated_data):
        user = self.context['request'].user
        interest_id = self.validated_data['id']
        interest = Interest.objects.get(id=interest_id)
        return UserInterest.objects.create(user=user, interest=interest)

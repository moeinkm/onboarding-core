from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from accounts.models import UserProfile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["id", "username", "email", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = get_user_model().objects.create_user(**validated_data)
        UserProfile.objects.create(user=user, onboarding_complete=False)
        return user


class OnboardingSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["onboarding_complete"]

from rest_framework import generics
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.permissions import IsAuthenticated

from .serializers import UserSerializer, OnboardingSerializer


class UserCreateView(generics.CreateAPIView):
    serializer_class = UserSerializer


class OnboardingCompleteView(generics.UpdateAPIView):
    serializer_class = OnboardingSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.userprofile


class CreateTokenView(ObtainAuthToken):
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

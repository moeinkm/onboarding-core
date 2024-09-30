import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse


class TestAccountViews:
    @pytest.mark.django_db
    def test_createUser_validData_success(self, authenticated_client):
        url = reverse("accounts:create")
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword123",
        }
        response = authenticated_client.post(url, data)
        assert response.status_code == 201
        assert (
            get_user_model()
            .objects.filter(username="newuser", onboarding_complete=False)
            .exists()
        )

    @pytest.mark.django_db
    def test_completeOnboarding_authenticatedUser_success(
        self, authenticated_user, authenticated_client
    ):
        url = reverse("accounts:complete-onboarding")
        response = authenticated_client.patch(url, {"onboarding_complete": True})
        assert response.status_code == 200
        authenticated_user.refresh_from_db()
        assert authenticated_user.onboarding_complete is True

    @pytest.mark.django_db
    def test_createToken_validCredentials_success(self, authenticated_client):
        url = reverse("accounts:token")
        data = {"username": "testuser", "password": "testpass123"}
        response = authenticated_client.post(url, data)
        assert response.status_code == 200
        assert "token" in response.data


class TestAccountSerializers:
    @pytest.mark.django_db
    def test_userSerializer_validData_success(self):
        from accounts.api.serializers import UserSerializer

        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
        }
        serializer = UserSerializer(data=data)
        assert serializer.is_valid()
        user = serializer.save()
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.check_password("testpass123")
        assert (
            get_user_model()
            .objects.filter(username="testuser", onboarding_complete=False)
            .exists()
        )

    @pytest.mark.django_db
    def test_onboardingSerializer_validData_success(self):
        from accounts.api.serializers import OnboardingSerializer

        user = get_user_model().objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        data = {"onboarding_complete": True}
        serializer = OnboardingSerializer(instance=user, data=data)
        assert serializer.is_valid()
        updated_profile = serializer.save()
        assert updated_profile.onboarding_complete is True

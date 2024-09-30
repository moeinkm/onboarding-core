import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_user():
    def _create_user(
        username="testuser", email="test@example.com", password="testpass123"
    ):
        User = get_user_model()
        return User.objects.create_user(
            username=username, email=email, password=password
        )

    return _create_user


@pytest.fixture
def authenticated_user(api_client, create_user):
    user = create_user()
    api_client.force_authenticate(user=user)
    return user


@pytest.fixture
def authenticated_client(api_client, authenticated_user):
    return api_client

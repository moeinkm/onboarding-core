from django.urls import path

from .views import UserCreateView, OnboardingCompleteView, CreateTokenView


app_name = "accounts"

urlpatterns = [
    path("create/", UserCreateView.as_view(), name="create"),
    path(
        "complete-onboarding/",
        OnboardingCompleteView.as_view(),
        name="complete-onboarding",
    ),
    path("token/", CreateTokenView.as_view(), name="token"),
]

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import FileViewSet

router = DefaultRouter()
router.register(r"files", FileViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

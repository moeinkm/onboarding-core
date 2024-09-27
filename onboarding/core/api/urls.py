from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import FileViewSet

app_name = "core"

router = DefaultRouter()
router.register("", FileViewSet, "file")

urlpatterns = [
    path("", include(router.urls)),
]

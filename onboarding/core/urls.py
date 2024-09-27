from django.contrib import admin
from django.urls import path, include

api_url_patterns = [
    path("users/", include("accounts.api.urls", namespace="user")),
    path("files/", include("core.api.urls", namespace="core")),
]

urlpatterns = [
    path("api/", include(api_url_patterns)),
    path("admin/", admin.site.urls),
]

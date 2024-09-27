from rest_framework import viewsets
from rest_framework.decorators import action

from core.models import File
from .serializers import (
    FileSerializer,
    FileDataSerializer,
    SimpleFileSerializer,
    MultiUploadSerializer,
)


class FileViewSet(viewsets.ModelViewSet):
    queryset = File.objects.all().select_related()
    serializer_class = FileSerializer

    SERIALIZER_MAP = {
        "retrieve": FileDataSerializer,
        "list": SimpleFileSerializer,
        "multi_upload": MultiUploadSerializer,
    }

    def get_queryset(self):
        queryset = super().get_queryset().filter(user=self.request.user)
        if self.action == "retrieve":
            queryset = queryset.prefetch_related(
                "file_headers__header", "file_headers__values"
            )

        return queryset

    def get_serializer_class(self):
        default_serializer_class = super().get_serializer_class()

        return self.SERIALIZER_MAP.get(self.action, default_serializer_class)

    @action(detail=False, methods=["post"])
    def multi_upload(self, request):
        return self.create(request)

from rest_framework import viewsets
from core.models import File
from .serializers import FileSerializer, FileDataSerializer


class FileViewSet(viewsets.ModelViewSet):
    queryset = File.objects.all().select_related()
    serializer_class = FileSerializer

    def get_queryset(self):
        queryset = super().get_queryset().filter(user=self.request.user)
        if self.action == "retrieve":
            queryset = queryset.prefetch_related(
                "file_headers__header", "file_headers__values"
            )

        return queryset

    def get_serializer_class(self):
        if self.action == "retrieve":
            return FileDataSerializer
        return FileSerializer

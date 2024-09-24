from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from core.models import File
from .serializers import FileSerializer


class FileViewSet(viewsets.ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer

    @action(detail=True, methods=["get"])
    def csv_data(self, request, pk=None):
        file = self.get_object()
        headers = file.headers.all()

        data = []
        for header in headers:
            header_data = {
                "header": header.name,
                "values": list(header.values.values_list("value", flat=True)),
            }
            data.append(header_data)

        return Response(data)

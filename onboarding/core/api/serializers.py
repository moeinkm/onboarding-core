import csv
from io import StringIO

from django.core.files.base import ContentFile
from django.db import transaction
from rest_framework import serializers

from core.models import File, Header, Value, FileHeader


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ["id", "name", "file", "created_at"]
        read_only_fields = ["id", "created_at"]

    def create(self, validated_data):
        uploaded_file = validated_data.pop("file")
        name = validated_data.get("name", uploaded_file.name)

        with transaction.atomic():
            file_instance = File.objects.create(name=name)

            file_content = ContentFile(uploaded_file.read())
            file_instance.file.save(uploaded_file.name, file_content, save=True)

            self.process_csv(file_instance)

        return file_instance

    def process_csv(self, file_instance):
        csv_file = file_instance.file
        csv_content = csv_file.read().decode("utf-8")
        csv_reader = csv.reader(StringIO(csv_content))
        header_names = next(csv_reader)  # Get the header row

        file_headers = self.process_headers(file_instance, header_names)
        self.process_values(file_headers, csv_reader)

    def process_headers(self, file_instance, header_names):
        file_headers = {}
        for header_name in header_names:
            header, _ = Header.objects.get_or_create(
                name=header_name,
            )
            file_header, _ = FileHeader.objects.get_or_create(
                file=file_instance, header=header
            )
            file_headers[header_name] = file_header
        return file_headers

    def process_values(self, file_headers, csv_reader):
        for row in csv_reader:
            for header_name, value in zip(file_headers.keys(), row):
                Value.objects.create(file_header=file_headers[header_name], value=value)


class ValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Value
        fields = ["value"]


class HeaderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Header
        fields = ["name", "data_type"]


class FileHeaderSerializer(serializers.ModelSerializer):
    header = HeaderSerializer(read_only=True)
    values = ValueSerializer(many=True, read_only=True)

    class Meta:
        model = FileHeader
        fields = ["header", "values"]


class FileDataSerializer(serializers.ModelSerializer):
    file_headers = FileHeaderSerializer(many=True, read_only=True)

    class Meta:
        model = File
        fields = ["id", "name", "file", "file_headers"]

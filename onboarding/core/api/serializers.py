import csv
from io import StringIO

from django.core.files.base import ContentFile
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from core.models import File, Header, Value, FileHeader


class ValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Value
        fields = ["value"]


class HeaderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Header
        fields = ["name", "data_type"]


class SimpleFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ["id", "name", "created_at"]
        read_only_fields = ["id", "created_at"]


class FileSerializer(serializers.ModelSerializer):
    headers = HeaderSerializer(many=True, required=False)
    name = serializers.CharField(required=False)

    class Meta:
        model = File
        fields = ["id", "name", "file", "headers", "created_at"]
        read_only_fields = ["id", "created_at"]

    def create(self, validated_data):
        uploaded_file = validated_data.get("file")
        name = validated_data.get("name", uploaded_file.name)

        with transaction.atomic():
            file_instance = File.objects.create(
                name=name, user=self.context["request"].user
            )

            file_content = ContentFile(uploaded_file.read())
            file_instance.file.save(uploaded_file.name, file_content, save=True)

            self.process_csv(file_instance, validated_data)

        return file_instance

    def process_csv(self, file_instance, validated_data):
        csv_file = file_instance.file
        csv_content = csv_file.read().decode("utf-8")
        csv_reader = csv.reader(StringIO(csv_content))

        file_headers = self.process_headers(file_instance, csv_reader, validated_data)
        self.process_values(file_headers, csv_reader)

    def process_headers(self, file_instance, csv_reader, validated_data):
        header_names = next(csv_reader)
        file_headers = {}
        headers = []

        if validated_data.get("headers"):
            for item in validated_data.get("heaaders"):
                header, _ = Header.objects.get_or_create(
                    name=item["name"], defaults=item
                )
                headers.append(header)
        else:
            for header_name in header_names:
                header = Header.objects.get(
                    name=header_name,
                )
                if not header:
                    raise ValidationError(
                        "Headers settings not provided and does not exists"
                    )
                headers.append(header)

        for header in headers:
            file_header, _ = FileHeader.objects.create(
                file=file_instance, header=header
            )
            file_headers[header.name] = file_header

        return file_headers

    def process_values(self, file_headers, csv_reader):
        for row in csv_reader:
            for header_name, value in zip(file_headers.keys(), row):
                Value.objects.create(file_header=file_headers[header_name], value=value)


class MultiUploadSerializer(serializers.Serializer):
    files = serializers.ListField(
        child=serializers.FileField(
            max_length=100000, allow_empty_file=False, use_url=False
        )
    )

    def create(self, validated_data):
        with transaction.atomic():
            files = validated_data["files"]

            uploaded_files = []
            for file in files:
                file_serializer = FileSerializer(
                    data={"file": file}, context=self.context
                )

                if file_serializer.is_valid(raise_exception=True):
                    uploaded_file = file_serializer.save()
                    uploaded_files.append(uploaded_file)

        return uploaded_files


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
        read_only_fields = ["id"]

import csv
import json
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
    file_headers = serializers.CharField(required=False)
    name = serializers.CharField(required=False)

    class Meta:
        model = File
        fields = ["id", "name", "file", "file_headers", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate_file_headers(self, value):
        try:
            file_headers = json.loads(value)

            if not isinstance(file_headers, list):
                raise serializers.ValidationError("File headers must be a list.")

            for header in file_headers:
                if "name" not in header or "data_type" not in header:
                    raise serializers.ValidationError(
                        "Each header must contain a 'name' and a 'data_type' field."
                    )

            return file_headers
        except json.JSONDecodeError:
            raise serializers.ValidationError("Invalid JSON format for file headers.")

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
        if validated_data.get("file_headers"):
            for item in validated_data.get("file_headers"):
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
            file_header = FileHeader.objects.create(file=file_instance, header=header)
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

    def to_representation(self, instance):
        return {"files": [FileSerializer(file).data for file in instance]}


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

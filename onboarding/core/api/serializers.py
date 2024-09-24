from rest_framework import serializers

from core.models import File, Header, Value


class ValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Value
        fields = ["value"]


class HeaderSerializer(serializers.ModelSerializer):
    values = ValueSerializer(many=True, read_only=True)

    class Meta:
        model = Header
        fields = ["name", "data_type", "values"]


class FileSerializer(serializers.ModelSerializer):
    headers = HeaderSerializer(many=True, read_only=True)

    class Meta:
        model = File
        fields = ["id", "name", "headers"]

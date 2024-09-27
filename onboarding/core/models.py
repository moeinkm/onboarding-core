from django.contrib.auth import get_user_model
from django.db import models


class File(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to="uploads/")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Header(models.Model):
    name = models.CharField(max_length=255, unique=True)
    data_type = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class FileHeader(models.Model):
    file = models.ForeignKey(
        File, related_name="file_headers", on_delete=models.CASCADE
    )
    header = models.ForeignKey(
        Header, related_name="file_headers", on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ("file", "header")


class Value(models.Model):
    file_header = models.ForeignKey(
        FileHeader, related_name="values", on_delete=models.CASCADE
    )
    value = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.file_header.header.name}: {self.value}"

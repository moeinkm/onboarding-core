from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    onboarding_completed = models.BooleanField(default=False)


class Table(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to="uploads/")
    created_at = models.DateTimeField(auto_now_add=True)


class ColumnMapping(models.Model):
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    original_column = models.CharField(max_length=255)
    mapped_column = models.CharField(max_length=255)
    data_type = models.CharField(max_length=50)


class TableData(models.Model):
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    data = models.JSONField()

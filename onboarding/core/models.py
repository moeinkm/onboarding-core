from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    onboarding_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class File(models.Model):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to="uploads/")
    created_at = models.DateTimeField(auto_now_add=True)


class Header(models.Model):
    name = models.CharField(max_length=255)
    data_type = models.CharField(max_length=255)
    file = models.ManyToManyField(File, related_name="headers")


class Value(models.Model):
    header = models.ForeignKey(Header, related_name="values", on_delete=models.CASCADE)
    value = models.CharField(max_length=255)

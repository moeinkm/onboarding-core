from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    onboarding_complete = models.BooleanField(default=False)

    def __str__(self):
        return self.username

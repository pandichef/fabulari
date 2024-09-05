from django.db import models
from django.contrib.auth.models import AbstractUser


LANGUAGE_CHOICES = [
    ("en", "English"),
    ("es", "Spanish"),
    ("ru", "Russian"),
    # Add more languages as needed
]


class CustomUser(AbstractUser):
    native_language = models.CharField(
        max_length=10, choices=LANGUAGE_CHOICES, default="en", null=False, blank=False
    )
    working_on = models.CharField(
        max_length=10, choices=LANGUAGE_CHOICES, default="es", null=False, blank=False
    )

    class Meta:
        verbose_name = "Settings"
        verbose_name_plural = "Settings"

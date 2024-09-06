from datetime import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser


LANGUAGE_CHOICES = [
    ("en", "English"),
    ("es", "Spanish"),
    ("ru", "Russian"),
    ("he", "Hebrew"),
    ("ar", "Arabic"),
    ("zh", "Chinese"),
    ("de", "German"),
    ("la", "Latin"),
    ("fr", "French"),
    # Add more languages as needed
]

supported_languages = [code for code, _ in LANGUAGE_CHOICES]


class CustomUser(AbstractUser):
    native_language = models.CharField(
        max_length=10, choices=LANGUAGE_CHOICES, default="en", null=False, blank=False
    )
    working_on = models.CharField(
        max_length=10, choices=LANGUAGE_CHOICES, default="es", null=False, blank=False
    )
    readwise_api_key = models.CharField(
        max_length=75,
        blank=True,
        null=True,
        help_text='<a href="https://readwise.io/access_token" target="_blank">Generate API key here if you have an account.</a>',
    )
    last_readwise_update = models.DateTimeField(default=datetime(1900, 1, 1, 0, 0))

    class Meta:
        verbose_name = "Settings"
        verbose_name_plural = "Settings"

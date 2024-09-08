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
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    # email = models.EmailField(_("email address"), blank=True, )
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
        help_text='Generate API key <a href="https://readwise.io/access_token" target="_blank">here</a> if you have an account.',
    )
    last_readwise_update = models.DateTimeField(default=datetime(1900, 1, 1, 0, 0))
    # last_readwise_update_articles = models.DateTimeField(
    #     default=datetime(
    #         1900, 1, 1, 0, 0
    #     )  # STOPPED USING THIS; TOO COMPLICATED TO MAINTAIN
    # )
    use_readwise_for_study_materials = models.BooleanField(
        default=False,
        help_text='Send study materials to <a href="https://readwise.io/" target="_blank">Readwise</a> (instead of email) if <a href="https://readwise.io/access_token" target="_blank">API key</a> is available.',
    )
    retrieve_native_language_from_readwise = models.BooleanField(
        default=False,
        help_text="By default, only foreign vocabulary is retrieved from Readwise.  Turn this on to import from your native language as well.",
    )

    class Meta:
        verbose_name = "Settings"
        verbose_name_plural = "Settings"

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
    last_readwise_update_articles = models.DateTimeField(
        default=datetime(
            1900, 1, 1, 0, 0
        )  # STOPPED USING THIS; TOO COMPLICATED TO MAINTAIN
    )
    #     summarization_prompt_conditions = models.TextField(
    #         default="""
    # If the article is in Spanish, the response should be at a CEFR B1 level.
    #     """,
    #         help_text="Leave blank if there are no conditions.",
    #     )

    class Meta:
        verbose_name = "Settings"
        verbose_name_plural = "Settings"

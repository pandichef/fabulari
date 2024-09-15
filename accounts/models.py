from datetime import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils.translation import gettext_lazy as _

LANGUAGE_CHOICES = settings.LANGUAGE_CHOICES


class CustomUser(AbstractUser):
    openai_llm_model_complex_tasks = models.CharField(  # https://openai.com/api/pricing/
        max_length=100,
        default="gpt-4o-mini",
        null=False,
        blank=False,
        choices=[
            ("gpt-4o-mini", "gpt-4o-mini (cheapest model)"),
            ("gpt-4o", "gpt-4o (~30x more expensive than gpt-4o-mini)"),
            (
                "chatgpt-4o-latest",
                "chatgpt-4o-latest (~30x more expensive than gpt-4o-mini)",
            ),
        ],
        help_text=_(
            f"""Used for creating study materials and translation feedback.
        Cost estimates are as of September 2024. Note that gpt-4o-mini is used for simple translation and classification tasks.
        """
        ),
        # help_text=_(
        #     f"""Used for creating study materials and translation feedback.
        # Cost estimates are as of September 2024.
        # Note that {settings.OPENAI_LLM_MODEL_SIMPLE_TASKS} is used for simple translation and classification tasks.
        # """
        # ),
        verbose_name=_("OpenAI LLM Model"),
    )
    native_language = models.CharField(
        _("native language"),
        max_length=10,
        choices=LANGUAGE_CHOICES,
        default="en",
        null=False,
        blank=False,
    )
    working_on = models.CharField(
        _("working on"),
        max_length=10,
        choices=LANGUAGE_CHOICES,
        default="es",
        null=False,
        blank=False,
    )
    readwise_api_key = models.CharField(
        max_length=75,
        blank=True,
        null=True,
        help_text=_(
            'Generate API key <a href="https://readwise.io/access_token" target="_blank">here</a> if you have an account.'
        ),
    )
    last_readwise_update = models.DateTimeField(
        _("last readwise update"), default=datetime(1900, 1, 1, 0, 0)
    )
    # last_readwise_update_articles = models.DateTimeField(
    #     default=datetime(
    #         1900, 1, 1, 0, 0
    #     )  # STOPPED USING THIS; TOO COMPLICATED TO MAINTAIN
    # )
    use_readwise_for_study_materials = models.BooleanField(
        _("use readwise for study materials"),
        default=False,
        help_text=_(
            'Send study materials to <a href="https://readwise.io/" target="_blank">Readwise</a> (instead of email) if <a href="https://readwise.io/access_token" target="_blank">API key</a> is available.'
        ),
    )
    retrieve_native_language_from_readwise = models.BooleanField(
        _("retrieve native language from readwise"),
        default=False,
        help_text=_(
            "By default, only foreign vocabulary is retrieved from Readwise.  Turn this on to import from your native language as well."
        ),
    )

    class Meta:
        verbose_name = _("Settings")
        verbose_name_plural = _("Settings")

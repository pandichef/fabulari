from datetime import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils.translation import gettext_lazy as _

LANGUAGE_CHOICES = settings.LANGUAGE_CHOICES

# supported_languages = settings.supported_languages
# supported_languages = [code for code, _ in LANGUAGE_CHOICES]
# print(supported_languages)


class CustomUser(AbstractUser):
    # email = models.EmailField(_("email address"), blank=True, )
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
            # ("gpt-4-turbo", "gpt-4-turbo"),
            # ("gpt-4", "gpt-4"),
            # ("gpt-3.5-turbo", "gpt-3.5-turbo"),
            # ("chatgpt-4o-latest", "chatgpt-4o-latest"),
        ],
        help_text=f"""Used for creating study materials and translation feedback.  
Cost estimates are as of September 2024.
Note that {settings.OPENAI_LLM_MODEL_SIMPLE_TASKS} is used for simple translation and classification tasks.
""",
        verbose_name="OpenAI LLM Model",
    )
    # openai_embeddings_model = models.CharField(
    #     max_length=100,
    #     default="text-embedding-3-large",
    #     null=False,
    #     blank=False,
    #     choices=[("text-embedding-3-large", "text-embedding-3-large"),],
    # )
    native_language = models.CharField(
        max_length=10, choices=LANGUAGE_CHOICES, default="en", null=False, blank=False
    )
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

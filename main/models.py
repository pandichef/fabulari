import numpy as np
from django.db import models
from django.db.models import Avg, FloatField, F, ExpressionWrapper, Func, Value, StdDev
from decimal import Decimal
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

LANGUAGE_CHOICES = settings.LANGUAGE_CHOICES
User = get_user_model()


class Phrase(models.Model):
    created = models.DateTimeField(
        _("created"), auto_now_add=True
    )  # Set once when created
    modified = models.DateTimeField(
        _("modified"), auto_now=True
    )  # Update every time the object is saved
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=False, blank=False, verbose_name=_("user")
    )
    raw_text = models.CharField(max_length=255, verbose_name=_("Raw text"))
    cleaned_text = models.CharField(max_length=255, verbose_name=_("Phrase"))
    example_sentence = models.CharField(_("example sentence"), max_length=255)
    definition = models.CharField(_("definition"), max_length=255)
    language = models.CharField(
        _("language"),
        max_length=10,
        choices=LANGUAGE_CHOICES,
        null=False,
        blank=True,
        help_text=_("""Dectected from text if blank"""),
    )
    cosine_similarity = models.DecimalField(
        null=True, blank=False, max_digits=5, decimal_places=4
    )

    class Meta:
        unique_together = ("user", "cleaned_text")

    def __str__(self):
        return f"{self.cleaned_text}"

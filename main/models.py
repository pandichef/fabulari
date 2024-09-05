from django.db import models
from django.db.models import Avg, FloatField, F, ExpressionWrapper, Func, Value

# from accounts.models import CustomUser
from django.contrib.auth import get_user_model

from accounts.models import LANGUAGE_CHOICES

# LANGUAGE_CHOICES = [
#     ("en", "English"),
#     ("es", "Spanish"),
#     ("ru", "Russian"),
#     # Add more languages as needed
# ]

User = get_user_model()


class PhraseManager(models.Manager):
    # def get_mean_cosine_similarity(self):
    #     """Calculate and return the mean cosine similarity."""
    #     return self.aggregate(mean=Avg("cosine_similarity"))["mean"]

    def get_queryset(self):
        """Return a queryset annotated with distance from the mean value."""
        # mean_cosine_similarity = self.get_mean_cosine_similarity()
        qs = super().get_queryset()
        mean_cosine_similarity = qs.aggregate(Avg("cosine_similarity"))[
            "cosine_similarity__avg"
        ]  # todo: get the mean by user and language type

        # mean_cosine_similarity = 0.5

        mean_cosine_similarity = (
            0.5 if mean_cosine_similarity is None else mean_cosine_similarity
        )

        # if mean_cosine_similarity is None:
        #     return super().get_queryset().none()

        return qs.annotate(
            distance_from_mean=ExpressionWrapper(
                Func(F("cosine_similarity") - mean_cosine_similarity, function="ABS"),
                output_field=FloatField(),
            )
        ).order_by("distance_from_mean")


# class Setting(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     native_language = models.CharField(
#         max_length=10, choices=LANGUAGE_CHOICES, default="en", null=False, blank=False
#     )
#     working_on = models.CharField(
#         max_length=10, choices=LANGUAGE_CHOICES, default="es", null=False, blank=False
#     )


class Phrase(models.Model):
    # LANGUAGE_CHOICES = [
    #     ("es", "Spanish"),
    #     ("ru", "Russian"),
    #     # Add more languages as needed
    # ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    text = models.CharField(max_length=255)
    cleaned_text = models.CharField(max_length=255)
    example_sentence = models.CharField(max_length=255)
    definition = models.CharField(max_length=255)
    language = models.CharField(
        max_length=10,
        choices=LANGUAGE_CHOICES,
        null=False,
        blank=True,
        # help_text="""If you leave this blank, we'll assume it's the current "working on" language.""",
        help_text=""""working on" language if blank""",
    )
    cosine_similarity = models.FloatField(null=True, blank=False)

    objects = PhraseManager()

    class Meta:
        unique_together = ("user", "cleaned_text")

    def __str__(self):
        return f"{self.text}"

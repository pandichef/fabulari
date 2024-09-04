from django.db import models
from django.db.models import Avg, FloatField, F, ExpressionWrapper, Func, Value


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
        ]

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


class Phrase(models.Model):
    LANGUAGE_CHOICES = [
        ("es", "Spanish"),
        ("ru", "Russian"),
        # Add more languages as needed
    ]

    text = models.CharField(max_length=255, unique=True)
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default="es")
    cosine_similarity = models.FloatField(null=True, blank=True)

    objects = PhraseManager()

    def __str__(self):
        return f"{self.text}"

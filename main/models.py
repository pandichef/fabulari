import numpy as np
from django.db import models
from django.db.models import Avg, FloatField, F, ExpressionWrapper, Func, Value, StdDev
from decimal import Decimal

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

'''
class PhraseManager(models.Manager):
    # def get_mean_cosine_similarity(self):
    #     """Calculate and return the mean cosine similarity."""
    #     return self.aggregate(mean=Avg("cosine_similarity"))["mean"]

    def get_queryset(self):
        # todo: this doesn't work because relevance should be done within
        # user and language
        """Return a queryset annotated with distance from the mean value."""
        # mean_cosine_similarity = self.get_mean_cosine_similarity()
        qs = super().get_queryset()

        mean_value = qs.aggregate(Avg("cosine_similarity"))[
            "cosine_similarity__avg"
        ]  # todo: get the mean by user and language type
        stddev_value = qs.aggregate(StdDev("cosine_similarity"))[
            "cosine_similarity__stddev"
        ]  # todo: get the mean by user and language type

        # mean_cosine_similarity = (
        #     0.5 if mean_cosine_similarity is None else mean_cosine_similarity
        # )

        # qs_values = self.values_list("cosine_similarity")
        # # Step 2: Exclude None values
        # filtered_values = [value for value in qs_values if value is not None]

        # # Step 3: Convert to a NumPy array
        # numpy_array = np.array(filtered_values)

        # # Step 4: Calculate the mean value
        # if numpy_array.size > 0:
        #     mean_value = np.mean(numpy_array)
        #     stddev_value = np.std(numpy_array)
        # else:
        #     mean_value = 0.50
        #     stddev_value = 0.25

        #     print("No valid values to calculate the mean.")

        mean_cosine_similarity = np.random.normal(loc=mean_value, scale=stddev_value)

        # if mean_cosine_similarity is None:
        #     return super().get_queryset().none()

        return qs.annotate(
            distance_from_mean=ExpressionWrapper(
                Func(F("cosine_similarity") - mean_cosine_similarity, function="ABS"),
                output_field=FloatField(),
            )
        ).order_by("distance_from_mean")
'''

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
    text = models.CharField(max_length=255, verbose_name="Raw text")
    cleaned_text = models.CharField(max_length=255, verbose_name="Phrase")
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
    cosine_similarity = models.DecimalField(
        null=True, blank=False, max_digits=5, decimal_places=4
    )
    noise = models.DecimalField(
        null=False, blank=False, max_digits=5, decimal_places=4, default=Decimal(0.0000)
    )  # lowest value is queued up next
    que_score = models.DecimalField(
        null=False, blank=False, max_digits=5, decimal_places=4, default=Decimal(0.0000)
    )  # lowest value is queued up next

    # objects = PhraseManager()

    class Meta:
        unique_together = ("user", "cleaned_text")

    def __str__(self):
        return f"{self.cleaned_text}"

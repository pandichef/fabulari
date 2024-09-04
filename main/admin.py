from django.contrib import admin
from .models import Phrase


@admin.register(Phrase)
class PhraseAdmin(admin.ModelAdmin):
    list_display = ("text", "language", "cosine_similarity", "relevance_indicator")
    list_filter = ("language",)
    search_fields = ("text",)

    def get_readonly_fields(self, request, obj=None):
        return [
            "cosine_similarity",
        ]

    def relevance_indicator(self, obj):
        if obj.distance_from_mean:
            return obj.distance_from_mean
        else:
            return ""

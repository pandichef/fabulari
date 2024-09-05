from django.contrib import admin
from .models import Phrase


@admin.register(Phrase)
class PhraseAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "text",
        "language",
        "cosine_similarity",
        "relevance_indicator",
    )
    list_filter = ("language",)
    search_fields = ("text",)
    fields = (
        "text",
        "language",
        "cosine_similarity",
    )

    def get_readonly_fields(self, request, obj=None):
        return ["cosine_similarity", "user"]

    def relevance_indicator(self, obj):
        if obj.distance_from_mean:
            return obj.distance_from_mean
        else:
            return ""

    def save_model(self, request, obj, form, change):
        if not change:  # if the object is being created
            obj.user = request.user
        if not obj.language:
            obj.language = request.user.working_on
        obj.save()
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs  # Return all objects for superusers
        return qs.filter(user=request.user)  # Filter objects for regular users


# @admin.register(Setting)
# class SettingAdmin(admin.ModelAdmin):
#     pass

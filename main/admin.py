from django.contrib import admin

from django.db.utils import IntegrityError

# from django.core.exceptions  import Tra
from django.db.transaction import TransactionManagementError
from django.contrib import messages
from .models import Phrase
from purepython.cleantranslation import phrase_to_native_language


@admin.register(Phrase)
class PhraseAdmin(admin.ModelAdmin):
    # change_form_template = "phrase_change_form.html"
    def change_view(self, request, object_id, form_url="", extra_context=None):
        obj = self.get_object(request, object_id)
        extra_context = extra_context or {}
        # extra_context["save_on_top"] = True
        extra_context["show_save"] = False
        extra_context["show_save_and_add_another"] = False
        # extra_context["show_history"] = False
        return super().change_view(
            request, object_id, form_url, extra_context=extra_context
        )

    def add_view(self, request, form_url="", extra_context=None):
        # def add_view(self, request, object_id, form_url="", extra_context=None):
        # obj = self.get_object(request, object_id)
        extra_context = extra_context or {}
        # extra_context["save_on_top"] = True
        extra_context["show_save"] = False
        extra_context["show_save_and_add_another"] = False
        # extra_context["show_history"] = False
        # return super().change_view(
        #     request, object_id, form_url, extra_context=extra_context
        # )
        return self.changeform_view(request, None, form_url, extra_context)

    list_display = (
        "user",
        # "text",
        "cleaned_text",
        "definition",
        # "language",
        "cosine_similarity",
        "relevance",
    )
    list_filter = ("language",)
    search_fields = ("cleaned_text",)
    fields = (
        "text",
        "cleaned_text",
        "example_sentence",
        "definition",
        "language",
        "cosine_similarity",
    )

    def get_readonly_fields(self, request, obj=None):
        fields = [
            "cosine_similarity",
            "user",
            "cleaned_text",
            "example_sentence",
            "definition",
        ]

        if obj:
            return fields + ["language"]
        else:
            return fields

    def relevance(self, obj):
        if obj.distance_from_mean:
            return round(obj.distance_from_mean, 4)
        else:
            return ""

    # def cosine_similarity_(self, obj):
    #     if obj.cosine_similarity:
    #         return round(obj.cosine_similarity, 4)
    #     else:
    #         return ""

    def save_model(self, request, obj, form, change):
        # try:
        if not change:  # if the object is being created
            obj.user = request.user
        if not obj.language:
            obj.language = request.user.working_on
        (cleaned_text, example_sentence, definition) = phrase_to_native_language(
            phrase=obj.text,
            working_on=request.user.working_on,
            native_language=request.user.native_language,
        )

        # get_equivalent_object = Phrase.objects.get(cleaned_text=cleaned_text)
        # existing_object = Phrase.objects.get(cleaned_text=cleaned_text)
        existing_object = Phrase.objects.filter(cleaned_text=cleaned_text).first()

        if existing_object:
            # self.message_user(request, "This term already exists.")
            # Redirect to the change page of the existing object
            # self.message_user(
            #     request,
            #     "Redirected to the existing object due to a unique constraint.",
            #     # level="warning",
            # )
            # return redirect(change_url)
            obj.existing_obj_id = existing_object.id

        else:
            obj.cleaned_text = cleaned_text
            obj.example_sentence = example_sentence
            obj.definition = definition
            obj.save()
            super().save_model(request, obj, form, change)

    def response_add(self, request, obj):
        if obj.cleaned_text:
            return super().response_add(request, obj)
        else:
            from django.shortcuts import redirect
            from django.urls import reverse
            from django.shortcuts import redirect

            self.message_user(request, "This term already exists.  Redirecting.")

            change_url = reverse(
                "admin:main_phrase_change",  # Replace 'appname' with your app's name
                args=[obj.existing_obj_id],
            )
            return redirect(change_url)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs  # Return all objects for superusers
        return qs.filter(user=request.user)  # Filter objects for regular users

    def get_actions(self, request):
        actions = super().get_actions(request)
        # Remove all actions
        actions.clear()
        return actions


# @admin.register(Setting)
# class SettingAdmin(admin.ModelAdmin):
#     pass

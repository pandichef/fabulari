from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse
from django.shortcuts import redirect
from django.conf import settings
from purepython.create_phrase_object import get_phrase_metadata
from purepython.practice_translation import detect_language_code as detect
from purepython.practice_translation import from_native_language
from .models import Phrase

LANGUAGE_CHOICES = settings.LANGUAGE_CHOICES
SUPPORTED_LANGUAGES = [code for code, _ in LANGUAGE_CHOICES]


@admin.register(Phrase)
class PhraseAdmin(admin.ModelAdmin):
    # change_list_template = "change_list_with_readwise_import.html"
    # change_form_template = "change_form_without_history.html"
    change_form_template = "admin/change_form_with_bulk_add_button.html"

    def change_view(self, request, object_id, form_url="", extra_context=None):
        obj = self.get_object(request, object_id)
        extra_context = extra_context or {}
        extra_context["show_save"] = False
        # extra_context["being_edited"] = (
        #     obj is not None
        # )  # Assuming this condition for 'being_edited'
        extra_context["phrase_id"] = object_id  # The phrase_id you want to use
        return super().change_view(
            request, object_id, form_url, extra_context=extra_context
        )

    def add_view(self, request, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context["show_save"] = False
        extra_context["show_save_and_add_another"] = False
        return self.changeform_view(request, None, form_url, extra_context)

    list_display = (
        "cleaned_text",
        "definition",
        "cosine_similarity",
        "language",
        "user",
        "created",
    )
    # list_filter = ("language",)
    def get_list_filter(self, request):
        filters = ("language",)  # Default filters
        if request.user.is_superuser:
            filters += ("user",)  # Add 'user' filter if the user is a superuser
        return filters

    search_fields = ("cleaned_text",)
    fields = (
        "raw_text",
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
            # return fields + ["language"]
            return fields
        else:
            return fields

    def save_model(self, request, obj, form, change) -> bool:
        if change:  # if the object is being created
            last_obj = Phrase.objects.get(id=obj.id)
            raw_text_changed = (
                last_obj.raw_text != obj.raw_text
                or not last_obj.definition
                or not last_obj.example_sentence
            )
        else:
            raw_text_changed = False
            obj.user = request.user
            detected_language_code = detect(
                phrase=obj.raw_text, openai_model=settings.OPENAI_LLM_MODEL_SIMPLE_TASKS
            )
            if not obj.language:
                if detected_language_code == request.user.native_language:
                    obj.language = request.user.working_on

                    obj.raw_text = from_native_language(
                        obj.raw_text,
                        working_on=obj.language,
                        native_language=detected_language_code,
                        openai_model=settings.OPENAI_LLM_MODEL_SIMPLE_TASKS,
                    )
                else:
                    if not detected_language_code in SUPPORTED_LANGUAGES:
                        obj.language = request.user.working_on
                    else:
                        obj.language = detected_language_code
            else:
                if detected_language_code != obj.language:

                    if self:
                        self.message_user(
                            request,
                            f"The text you typed does not appear to be {dict(LANGUAGE_CHOICES)[obj.language]}.",
                        )
                    obj.language = detected_language_code
            # elif obj.language != request.user.native_language:
            #     from purepython.gptsrs import from_native_language

            #     obj.text = from_native_language(
            #         obj.text,
            #         working_on=obj.language,
            #         native_language=detected_language_code,
            #         openai_model=OPENAI_LLM_MODEL,
            #     )

        # get openai data if new object or raw_text changed
        if not change or raw_text_changed:
            native_language_metadata = list(
                get_phrase_metadata(
                    [{"raw_text": obj.raw_text, "language": obj.language}],
                    native_language=request.user.native_language,
                    openai_model=settings.OPENAI_LLM_MODEL_SIMPLE_TASKS,
                )
            )[0]
            if native_language_metadata:
                # (cleaned_text, example_sentence, definition) = native_language_metadata
                cleaned_text = native_language_metadata["cleaned_text"]
                example_sentence = native_language_metadata["example_sentence"]
                definition = native_language_metadata["definition"]
                if raw_text_changed:
                    obj.cleaned_text = cleaned_text
                    obj.example_sentence = example_sentence
                    obj.definition = definition
                    obj.save()
                    if self:
                        self.message_user(
                            request,
                            f"Retrieved values from {settings.OPENAI_LLM_MODEL_SIMPLE_TASKS}.",
                        )

                if not change:
                    existing_object = Phrase.objects.filter(
                        cleaned_text=cleaned_text, user=request.user
                    ).first()
                    if existing_object:
                        # just redirect if the object already exists
                        # this line of code is needed for the response_add method
                        obj.existing_obj_id = existing_object.id
                        # existing_object.text = obj.text
                        # existing_object.save()
                        return False
                    else:
                        obj.cleaned_text = cleaned_text
                        obj.example_sentence = example_sentence
                        obj.definition = definition
                        obj.save()
                        if self:
                            self.message_user(
                                request,
                                f"Retrieved values from {settings.OPENAI_LLM_MODEL_SIMPLE_TASKS}.",
                            )
            else:
                obj.cleaned_text = "(proper noun)"  # hack
                if self:
                    self.message_user(request, f"Not saved.  Contains proper noun.")
                return False

        # else:
        # Do nothing
        # existing_object = Phrase.objects.filter(
        #     cleaned_text=obj.text, user=request.user
        # ).first()

        # if existing_object:
        #     obj.existing_obj_id = existing_object.id
        # else:
        #     obj.cleaned_text = cleaned_text
        #     obj.example_sentence = example_sentence
        #     obj.definition = definition
        #     obj.save()
        if change:
            super().save_model(request, obj, form, change)
        return True

    def response_add(self, request, obj):
        if obj.cleaned_text == "(proper noun)":
            list_url = reverse(
                "admin:main_phrase_changelist",  # Replace 'appname' with your app's name
            )
            return redirect(list_url)
        elif obj.cleaned_text:
            return super().response_add(request, obj)
        else:
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
        # if not request.user.is_superuser:
        #     actions.clear()
        return actions


# @admin.register(Setting)
# class SettingAdmin(admin.ModelAdmin):
#     pass

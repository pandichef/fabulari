from django.utils.safestring import mark_safe
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse
from django.shortcuts import redirect
from django.conf import settings
from purepython.create_phrase_object import get_phrase_metadata
from purepython.practice_translation import detect_language_code as detect
from purepython.practice_translation import from_native_language
from .models import Phrase
from django import forms

LANGUAGE_CHOICES = settings.LANGUAGE_CHOICES
SUPPORTED_LANGUAGES = [code for code, _ in LANGUAGE_CHOICES]


class PhraseForm(forms.ModelForm):
    class Meta:
        model = Phrase
        fields = "__all__"  # or specify the fields you want

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set autofocus on a specific field
        self.fields["raw_text"].widget.attrs.update({"autofocus": "autofocus"})


@admin.register(Phrase)
class PhraseAdmin(admin.ModelAdmin):
    form = PhraseForm
    # change_list_template = "change_list_with_readwise_import.html"
    # change_form_template = "change_form_without_history.html"
    change_form_template = "admin/change_form_with_bulk_add_button.html"

    # def get_form(self, request, obj=None, **kwargs):
    #     # Call the base implementation to get the form
    #     form = super().get_form(request, obj, **kwargs)

    #     # If the object exists and has a 'language' field set to 'ar' or 'he'
    #     if obj and obj.language in ["ar", "he"]:
    #         # Add 'dir' attribute to the 'your_field' form field
    #         # form.base_fields["cleaned_text"].widget.attrs.update({"dir": "rtl"})
    #         # form.base_fields["raw_text"].widget.attrs.update({"dir": "rtl"})
    #         form.base_fields["raw_text"].widget.attrs.update({"dir": "rtl"})

    #     return form

    # def render

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
        "formatted_cleaned_text",  # for RTL Languages
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
        "_example_sentence",
        "definition",
        "language",
        "cosine_similarity",
    )

    # def st

    def get_readonly_fields(self, request, obj=None):
        fields = [
            "cosine_similarity",
            "user",
            "cleaned_text",
            "_example_sentence",
            "definition",
        ]
        return fields
        # if obj:
        #     return fields
        # else:
        #     return fields

    def formatted_cleaned_text(self, obj):
        # Check if the language is Arabic or Hebrew
        if obj.language in ["ar", "he"]:
            # Apply RTL formatting with left alignment
            return mark_safe(
                f'<div dir="rtl" style="text-align: left;">{obj.cleaned_text}</div>'
            )
        return obj.cleaned_text

    # Column name in list display
    formatted_cleaned_text.short_description = "Phrase"

    def _example_sentence(self, obj):
        from django.utils.safestring import mark_safe

        if obj.language in ["ar", "he"]:
            # return obj.example_sentence
            return mark_safe(
                f'<div dir="rtl" style="text-align: left;">{obj.example_sentence}</div>'
            )
        else:
            return obj.example_sentence

    _example_sentence.short_description = "Example sentence"

    # def get_object(self, request, object_id, from_field=None):
    #     from django.utils.safestring import mark_safe

    #     obj = super().get_object(request, object_id, from_field)

    #     if obj and obj.language in ["ar", "he"]:
    #         # Apply RTL formatting for the object's __str__ in the header
    #         obj.display_str = mark_safe(
    #             f'<div dir="rtl" style="text-align: left;">{obj.cleaned_text}</div>'
    #         )
    #     else:
    #         obj.display_str = "Add Phrase"

    #     return obj

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        # for RTL Languages

        obj = self.get_object(request, object_id)

        # Add extra context to display the formatted __str__ at the top and breadcrumbs
        if obj:
            extra_context = extra_context or {}
            extra_context["title"] = "Phrase"  # str(obj) if obj else "Change Object"
            if obj and obj.language in ["ar", "he"]:
                # Apply RTL formatting for the object's __str__ in the header
                extra_context["subtitle"] = self.formatted_cleaned_text(obj)
                # extra_context["subtitle"] =  mark_safe(
                #     f'<div dir="rtl" style="text-align: left;">{str(obj)}</div>'
                # )
            else:
                extra_context["subtitle"] = str(obj)
                # obj.display_str = "Add Phrase"
            # extra_context["subtitle"] = str(obj) if obj else "Change Object"

        return super().changeform_view(
            request, object_id, form_url, extra_context=extra_context
        )

    def save_model(self, request, obj, form, change):
        #
        if obj.id:
            last_obj = Phrase.objects.get(id=obj.id)
            do_nothing = (
                last_obj.raw_text == obj.raw_text
                and last_obj.language == obj.language
                and last_obj.definition  # e.g., if object created via add_multiple_phrases
                and last_obj.example_sentence  # e.g., if object created via add_multiple_phrases
            )
            if do_nothing:
                print("return True")
                return None

        # print("super().save_model(request, obj, form, change)")
        # super().save_model(request, obj, form, change)

        raw_text_language = detect(
            phrase=obj.raw_text,
            openai_llm_model=settings.OPENAI_LLM_MODEL_SIMPLE_TASKS,
        )
        if not obj.language:
            obj.language = request.user.working_on
        if obj.language != raw_text_language:
            translated_raw_text = from_native_language(
                sentence=obj.raw_text,
                working_on_verbose=dict(LANGUAGE_CHOICES)[obj.language],
                native_language_verbose=dict(LANGUAGE_CHOICES)[raw_text_language],
                # openai_llm_model=settings.OPENAI_LLM_MODEL_SIMPLE_TASKS,
                openai_llm_model=request.user.openai_llm_model_complex_tasks,
            )
        else:
            translated_raw_text = obj.raw_text

        native_language_metadata = list(
            get_phrase_metadata(
                [
                    {
                        "translated_raw_text": translated_raw_text,
                        "language": obj.language,
                    }
                ],
                native_language=request.user.native_language,
                # openai_model=settings.OPENAI_LLM_MODEL_SIMPLE_TASKS,
                openai_model=request.user.openai_llm_model_complex_tasks,
            )
        )[0]

        from pprint import pprint

        pprint(native_language_metadata)

        obj.cleaned_text = native_language_metadata["cleaned_text"]
        obj.example_sentence = native_language_metadata["example_sentence"]
        obj.definition = native_language_metadata["definition"]
        obj.user = request.user
        obj.save()

        #     # if change:  # if the object is being created
        #     last_obj = Phrase.objects.get(id=obj.id)
        #     raw_text_changed = (
        #         last_obj.raw_text != obj.raw_text
        #         or last_obj.language != obj.language
        #         or not last_obj.definition  # e.g., if object created via add_multiple_phrases
        #         or not last_obj.example_sentence  # e.g., if object created via add_multiple_phrases
        #     )

        # # get raw_text_in_working_on_language
        # detected_language_code = detect(
        #     phrase=obj.raw_text,
        #     openai_llm_model=settings.OPENAI_LLM_MODEL_SIMPLE_TASKS,
        # )
        # if detected_language_code != obj.language:
        #     raw_text_in_working_on_language = from_native_language(
        #         obj.raw_text,
        #         working_on_verbose=obj.language,
        #         native_language_verbose=detected_language_code,
        #         openai_llm_model=settings.OPENAI_LLM_MODEL_SIMPLE_TASKS,
        #     )
        # else:
        #     raw_text_in_working_on_language = obj.raw_text  # setup

        # ##########
        # if change:  # if the object is being created
        #     last_obj = Phrase.objects.get(id=obj.id)
        #     raw_text_changed = (
        #         last_obj.raw_text != obj.raw_text
        #         or last_obj.language != obj.language
        #         or not last_obj.definition  # e.g., if object created via add_multiple_phrases
        #         or not last_obj.example_sentence  # e.g., if object created via add_multiple_phrases
        #     )
        # else:
        #     raw_text_changed = False
        #     obj.user = request.user
        #     if not obj.language:
        #         if detected_language_code == request.user.native_language:
        #             obj.language = request.user.working_on

        #             raw_text_in_working_on_language = from_native_language(
        #                 obj.raw_text,
        #                 working_on_verbose=obj.language,
        #                 native_language_verbose=detected_language_code,
        #                 openai_llm_model=settings.OPENAI_LLM_MODEL_SIMPLE_TASKS,
        #             )
        #         else:
        #             if not detected_language_code in SUPPORTED_LANGUAGES:
        #                 obj.language = request.user.working_on
        #             else:
        #                 obj.language = detected_language_code
        #     else:
        #         if detected_language_code == request.user.native_language:
        #             # obj.language

        #             raw_text_in_working_on_language = from_native_language(
        #                 obj.raw_text,
        #                 working_on_verbose=obj.language,
        #                 native_language_verbose=detected_language_code,
        #                 openai_llm_model=settings.OPENAI_LLM_MODEL_SIMPLE_TASKS,
        #             )
        #         elif detected_language_code != obj.language:
        #             if self:
        #                 self.message_user(
        #                     request,
        #                     f"The text you typed does not appear to be {dict(LANGUAGE_CHOICES)[obj.language]}.",
        #                 )
        #             obj.language = detected_language_code
        #     # elif obj.language != request.user.native_language:
        #     #     from purepython.gptsrs import from_native_language

        #     #     obj.text = from_native_language(
        #     #         obj.text,
        #     #         working_on=obj.language,
        #     #         native_language=detected_language_code,
        #     #         openai_model=OPENAI_LLM_MODEL,
        #     #     )

        # # get openai data if new object or raw_text changed
        # if not change or raw_text_changed:
        #     native_language_metadata = list(
        #         get_phrase_metadata(
        #             # [{"raw_text": obj.raw_text, "language": obj.language}],
        #             [
        #                 {
        #                     "raw_text": raw_text_in_working_on_language,
        #                     "language": obj.language,
        #                 }
        #             ],
        #             native_language=request.user.native_language,
        #             openai_model=settings.OPENAI_LLM_MODEL_SIMPLE_TASKS,
        #         )
        #     )[0]
        #     if native_language_metadata:
        #         # (cleaned_text, example_sentence, definition) = native_language_metadata
        #         cleaned_text = native_language_metadata["cleaned_text"]
        #         example_sentence = native_language_metadata["example_sentence"]
        #         definition = native_language_metadata["definition"]
        #         if raw_text_changed:
        #             obj.cleaned_text = cleaned_text
        #             obj.example_sentence = example_sentence
        #             obj.definition = definition
        #             obj.save()
        #             if self:
        #                 self.message_user(
        #                     request,
        #                     f"Retrieved values from {settings.OPENAI_LLM_MODEL_SIMPLE_TASKS}.",
        #                 )

        #         if not change:
        #             existing_object = Phrase.objects.filter(
        #                 cleaned_text=cleaned_text, user=request.user
        #             ).first()
        #             if existing_object:
        #                 # just redirect if the object already exists
        #                 # this line of code is needed for the response_add method
        #                 obj.existing_obj_id = existing_object.id
        #                 # existing_object.text = obj.text
        #                 # existing_object.save()
        #                 return False
        #             else:
        #                 obj.cleaned_text = cleaned_text
        #                 obj.example_sentence = example_sentence
        #                 obj.definition = definition
        #                 obj.save()
        #                 if self:
        #                     self.message_user(
        #                         request,
        #                         f"Retrieved values from {settings.OPENAI_LLM_MODEL_SIMPLE_TASKS}.",
        #                     )
        #     else:
        #         obj.cleaned_text = "(proper noun)"  # hack
        #         if self:
        #             self.message_user(request, f"Not saved.  Contains proper noun.")
        #         return False

        # # else:
        # # Do nothing
        # # existing_object = Phrase.objects.filter(
        # #     cleaned_text=obj.text, user=request.user
        # # ).first()

        # # if existing_object:
        # #     obj.existing_obj_id = existing_object.id
        # # else:
        # #     obj.cleaned_text = cleaned_text
        # #     obj.example_sentence = example_sentence
        # #     obj.definition = definition
        # #     obj.save()
        # if change:
        #     super().save_model(request, obj, form, change)
        # return True

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

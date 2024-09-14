from django import forms
from django.conf import settings
from django.shortcuts import render, redirect
from django.db import IntegrityError
from django.contrib import messages
from main.models import Phrase
from django.contrib.admin.sites import site
from django.contrib.auth.decorators import login_required
from django.urls import reverse


LANGUAGE_CHOICES = settings.LANGUAGE_CHOICES


class LanguageChoiceForm(forms.Form):
    choice_field = forms.ChoiceField(choices=LANGUAGE_CHOICES, required=True)


@login_required(login_url="/admin/login/")
def add_multiple_phrases_view(request):
    admin_context = site.each_context(request)

    if request.method == "POST":
        # print("post")
        new_phrases = request.POST.get("words_input")
        new_phrases = new_phrases.split("\r\n")
        new_phrases = list(filter(None, new_phrases))
        language_code = request.POST.get("choice_field")
        language = dict(LANGUAGE_CHOICES)[language_code]
        # print(language)
        # list_of_phrase_objects = []
        total_count = len(new_phrases)
        added_count = 0
        for phrase_str in new_phrases:
            phrase_obj = Phrase(
                text=phrase_str,
                cleaned_text=phrase_str,
                language=language_code,
                user=request.user,
            )
            try:
                phrase_obj.save()
                added_count += 1
            except IntegrityError:
                pass

        # list_of_phrase_objects.append(phrase_obj)
        # Phrase.objects.bulk_create(list_of_phrase_objects)
        messages.success(
            request,
            f"""Added {added_count} new {language} words out of {total_count}.  ({total_count-added_count} already existed in the database.)  Note that metadata is not retrieved from {settings.OPENAI_LLM_MODEL_SIMPLE_TASKS} when adding data in bulk.""",
        )
        return redirect("/admin/main/phrase")
    else:
        admin_context.update(
            {
                "form": LanguageChoiceForm(
                    initial={"choice_field": request.user.working_on}
                )
            }
        )
        return render(request, "add_multiple_phrases.html", admin_context,)

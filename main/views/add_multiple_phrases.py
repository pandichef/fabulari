from main.models import LANGUAGE_CHOICES
from django import forms
from markdown2 import markdown
from datetime import datetime
import os
import numpy as np
from accounts.models import supported_languages as SUPPORTED_LANGUAGES
from requests.exceptions import ProxyError
from django.core.mail import send_mail
from purepython.assess_cefr_level import get_my_level, tuple_list_to_csv
from purepython.create_study_materials import create_article, create_article_title
from django import forms
from django.utils import timezone
from django.conf import settings
from django.db.models.functions import Abs
from django.shortcuts import render, HttpResponse, redirect
from purepython.practice_translation import (
    generate_full_sentence,
    to_native_language,
    from_native_language,
    compute_cosine_similarity,
    get_embeddings,
    get_feedback,
)
from django.db import IntegrityError
from django.db.models import Avg, FloatField, F, ExpressionWrapper, Func, Value, StdDev
from main.models import Phrase
from accounts.models import LANGUAGE_CHOICES
from purepython.practice_translation import OPENAI_EMBEDDINGS_MODEL
from purepython.create_phrase_object import phrase_to_native_language
from purepython.import_from_readwise import (
    fetch_from_export_api,
    make_digest,
    make_digest_multithreaded,
)
from django.contrib import messages
import pprint
from purepython.practice_translation import OPENAI_LLM_MODEL
from ..admin import PhraseAdmin
from django.utils.safestring import mark_safe
from purepython.create_study_materials import create_readwise_item


class LanguageChoiceForm(forms.Form):
    choice_field = forms.ChoiceField(choices=LANGUAGE_CHOICES, required=True)


def add_multiple_phrases_view(request):
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
            f"""Added {added_count} new {language} words out of {total_count}.  ({total_count-added_count} already existed in the database.)  Note that metadata is not retrieved from {OPENAI_LLM_MODEL} when adding data in bulk.""",
        )
        return redirect("/admin/main/phrase")
    else:
        return render(
            request,
            "add_multiple_phrases.html",
            {
                "form": LanguageChoiceForm(
                    initial={"choice_field": request.user.working_on}
                )
            },
        )

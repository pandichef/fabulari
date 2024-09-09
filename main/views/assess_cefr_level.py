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


def assess_cefr_level_view(request):
    qs = Phrase.objects.filter(
        user=request.user, language=request.user.working_on
    ).values_list("cleaned_text", "cosine_similarity")
    tuple_list = list(qs)
    # print(tuple_list_to_csv(tuple_list))
    llm_completion = get_my_level(
        word_list=tuple_list,
        working_on=dict(LANGUAGE_CHOICES)[request.user.working_on],
        openai_model=OPENAI_LLM_MODEL,
    )
    llm_completion = llm_completion if llm_completion else ""
    messages.success(
        request, llm_completion,
    )
    return redirect("/admin/main/phrase")
    # return redirect("https://www.nytimes.com")

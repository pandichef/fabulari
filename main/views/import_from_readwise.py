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


def import_from_readwise_view(request, populate_extra_fields_via_llm=False):
    if not request.user.readwise_api_key:
        messages.success(
            request,
            mark_safe(
                f"""To highlight phrases using Readwise, you must create a <a href="https://readwise.io/access_token">Readwise API key</a> and save it in your <a href="/admin/accounts/customuser/{request.user.id}/change">Settings</a>.
Note that Readwise is not a free service."""
            ),
        )
        return redirect("/admin/main/phrase")
    try:
        all_data = fetch_from_export_api(
            updated_after=request.user.last_readwise_update.isoformat(),
            token=request.user.readwise_api_key,
        )
        digest = make_digest_multithreaded(
            all_data, supported_languages=SUPPORTED_LANGUAGES
        )
        # messages.success(request, pprint.pformat(digest))
        counter = 0
        for item in digest:
            # print(request.user.native_language)
            if (
                item[1] != request.user.native_language
                or request.user.retrieve_native_language_from_readwise
            ):
                if populate_extra_fields_via_llm:  # slow! off by default
                    obj = Phrase(user=request.user, text=item[0], language=item[1])
                    was_retrieved = PhraseAdmin.save_model(
                        self=None, request=request, obj=obj, form=None, change=False
                    )
                    if was_retrieved:
                        counter += 1
                else:
                    obj = Phrase(
                        user=request.user,
                        text=item[0],
                        language=item[1],
                        cleaned_text=item[0],
                    )
                    try:
                        obj.save()
                        counter += 1
                    except IntegrityError:
                        pass
                # save_phrase_model(request, obj)
        datetime_1901 = timezone.make_aware(
            datetime(1901, 1, 1), timezone.get_current_timezone()
        )
        if request.user.last_readwise_update < datetime_1901:
            messages.success(
                request,
                f"""Successfully retrieved {counter} items from Readwise.  Going forward, only new items will be retrieved.""",
            )
        else:
            messages.success(
                request,
                f"""Successfully retrieved {counter} new items from Readwise.  Previously updated {request.user.last_readwise_update.strftime("%B %d, %Y at %I:%M %p")} (server time).""",
            )

        request.user.last_readwise_update = datetime.now()
        request.user.save()
    except ProxyError as e:
        # see https://www.pythonanywhere.com/forums/topic/33818/
        messages.success(
            request,
            f"""Encountered a proxy error.  The hosting service (PA) doesn't currently allow access to the Readwise API.""",
        )
        return redirect("/admin/main/phrase")
    except Exception as err:
        messages.error(
            request, f"{err}",
        )
    return redirect("/admin/main/phrase")

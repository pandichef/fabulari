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


class UseGPTRadioButtonForm(forms.Form):
    choice_field = forms.ChoiceField(
        choices=[(0, "Don't filter through GPT"), (1, "Filter through GPT First")],
        required=True,
        widget=forms.RadioSelect,
        initial=1,
    )


def create_study_materials_view(request):
    if request.method == "POST":
        gpt_first = int(request.POST.get("choice_field"))
        print(gpt_first)
        description_of_article = request.POST.get("words_input")
        # subject_split = description_of_article.split()[:10]
        # if len(subject_split):
        # subject = description_of_article
        # else:
        # subject = " ".join(subject_split) + "..."
        # sanitized_subject = subject.replace("\n", "").replace("\r", "")
        if gpt_first:
            # print("first")
            article = create_article(description_of_article)
        else:
            # print("not first")
            article = description_of_article
        subject = create_article_title(article)

        article_in_html = markdown(article)
        success = False
        if request.user.use_readwise_for_study_materials:
            # hack
            protocol_and_domain = f"{request.scheme}://{request.get_host()}"
            domain = request.get_host().split(":")[0]
            image_url = (
                protocol_and_domain + "/static/fabularilogo.webp"
                if not domain in ["127.0.0.1", "localhost"]
                else None
            )
            # print(request.get_host())
            res = create_readwise_item(
                token=request.user.readwise_api_key,
                title="[summary] " + subject,
                body_in_html=article_in_html,
                url=protocol_and_domain,
                image_url=image_url,
            )
            if res.status_code == 201:
                messages.success(
                    request,
                    mark_safe(
                        f"""An article regarding "{subject}" was sent to Reader using the API."""
                    ),
                )
            elif res.status_code == 200:
                messages.success(
                    request,
                    mark_safe(
                        f"""Readwise API determined that an article regarding "{subject}" already exists.  New item not created."""
                    ),
                )
            else:
                raise Exception(f"""[{res.status_code}] {res.content}""")
        else:
            while not success:
                try:
                    send_mail(
                        "[summary] " + subject,
                        article_in_html,
                        "from@example.com",
                        [request.user.email],
                        fail_silently=False,
                    )
                    success = True
                except:
                    pass
            messages.success(
                request,
                mark_safe(
                    f"""An article regarding "{subject}" was sent to {request.user.email}."""
                ),
            )
            # messages.success(
            #     request, f"""{res.content}""",
            # )
        return redirect("/admin/main/phrase")
        # return redirect("/create_article")
    else:
        if (
            request.user.use_readwise_for_study_materials
            and not request.user.readwise_api_key
        ):
            messages.success(
                request,
                mark_safe(
                    f""""Create Study Materials" lets you use ChatGPT to create new articles and send it to Readwise.  To do so, you must add a Readwise API Key in your <a href="/admin/accounts/customuser/{request.user.id}/change">Settings</a>.  Alternatively, you can opt to use email."""
                ),
            )
            return redirect("/admin/main/phrase")
        if not request.user.use_readwise_for_study_materials and not request.user.email:
            messages.success(
                request,
                mark_safe(
                    f""""Create Study Materials" lets you use ChatGPT to create new articles and send it to your email address.  To do so, you must provide an email address in your <a href="/admin/accounts/customuser/{request.user.id}/change">Settings</a>."""
                ),
            )
            return redirect("/admin/main/phrase")
            # return redirect_to_previous_page(request)

        return render(
            request, "create_study_materials.html", {"form": UseGPTRadioButtonForm()},
        )

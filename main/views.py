from datetime import datetime
import os
import numpy as np
from accounts.models import supported_languages as SUPPORTED_LANGUAGES
from django.utils import timezone
from django.conf import settings

# from django.db.models.expressions import RawSQL
# from django.db.models.functions import Abs, Coalesce
from django.db.models.functions import Abs
from django.shortcuts import render, HttpResponse, redirect
from purepython.gptsrs import (
    generate_full_sentence,
    to_native_language,
    from_native_language,
    compute_cosine_similarity,
    get_embeddings,
    get_feedback,
)
from django.db import IntegrityError

# from django.db.models import F
from django.db.models import Avg, FloatField, F, ExpressionWrapper, Func, Value, StdDev
from main.models import Phrase
from accounts.models import LANGUAGE_CHOICES
from purepython.gptsrs import OPENAI_EMBEDDINGS_MODEL
from purepython.cleantranslation import phrase_to_native_language
from purepython.fetch_readwise import fetch_from_export_api, make_digest
from django.contrib import messages
import pprint
from purepython.gptsrs import OPENAI_LLM_MODEL
from .admin import PhraseAdmin

# phrase_list = ["en cuanto a"]
from django.utils.safestring import mark_safe


"""
def save_phrase_model(request, obj, change=False, self=None):
    # todo: integrate this with the admin version
    if not change:  # if the object is being created
        obj.user = request.user

    if not obj.language:
        obj.language = request.user.working_on

    # Check if a similar object already exists based on "text"
    # fetch openai if the object doesn't exist or if the value of "text has changed"
    existing_object = Phrase.objects.filter(text=obj.text, user=request.user).first()
    if not existing_object or existing_object and existing_object.text != obj.text:

        if self:
            self.message_user(request, f"Retrieved values from {OPENAI_LLM_MODEL}.")

        (cleaned_text, example_sentence, definition) = phrase_to_native_language(
            phrase=obj.text,
            working_on=obj.language,
            native_language=request.user.native_language,
        )
        existing_object = Phrase.objects.filter(
            cleaned_text=cleaned_text, user=request.user
        ).first()
    else:
        existing_object = Phrase.objects.filter(
            cleaned_text=obj.text, user=request.user
        ).first()

    if existing_object:
        print("no obj created")
        obj.existing_obj_id = existing_object.id
    else:
        try:
            obj.cleaned_text = cleaned_text
            obj.example_sentence = example_sentence
            obj.definition = definition
            obj.save()
        except:
            pass
        # super().save_model(request, obj, form, change)
"""
from requests.exceptions import ProxyError

# from purepython.phrase_lists_utils import get_all_phrase_lists

from django.core.mail import send_mail
from purepython.get_my_level import get_my_level, tuple_list_to_csv
from purepython.create_article import create_article


def redirect_to_previous_page(request, fallback_url="/"):
    return redirect(request.META.get("HTTP_REFERER", fallback_url))


def create_article_view(request):
    if request.method == "POST":
        description_of_article = request.POST.get("words_input")
        subject_split = description_of_article.split()[:10]
        if len(subject_split):
            subject = description_of_article
        else:
            subject = " ".join(subject_split) + "..."
        sanitized_subject = subject.replace("\n", "").replace("\r", "")
        success = False
        while not success:
            try:
                send_mail(
                    "[summary] " + sanitized_subject,
                    create_article(description_of_article),
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
                f"""An article regarding "{sanitized_subject}" was sent to {request.user.email}."""
            ),
        )
        return redirect("/admin/main/phrase")
        # return redirect("/create_article")
    else:
        if not request.user.email:
            messages.success(
                request,
                mark_safe(
                    f"""The "Create Article" feature lets you use AI to create a new article and send it to your email address.  To do so, you must provide an email address in your <a href="/admin/accounts/customuser/{request.user.id}/change">Settings</a>."""
                ),
            )
            return redirect("/admin/main/phrase")
            # return redirect_to_previous_page(request)

        return render(request, "create_article.html", {},)


def collect_readwise_articles_view(request):
    from purepython.collect_readwise_articles import collect_readwise_articles

    print("------------------------------")
    print(request.user.email)
    print(request.user.email)
    print(request.user.email)
    print("------------------------------")

    if request.user.email and request.user.readwise_api_key:
        print("yes")
        try:
            limit = 50
            success_count, fail_count = collect_readwise_articles(
                updated_after=request.user.last_readwise_update_articles.isoformat(),
                # updated_after=None,
                recipient_list=[request.user.email],
                limit=limit,
            )
            fail_message = (
                f"""{fail_count} failed to send, likely due to an SMTP server issue.  """
                if fail_count
                else ""
            )
            up_to_date_message = (
                "There are no new summaries currently.  "
                if success_count + fail_count == 0
                else ""
            )
            limit_message = (
                f"Collecting summarizes is limited to {limit} articles due to server constraints.  "
                if success_count + fail_count == limit
                else ""
            )
            messages.success(
                request,
                f"""Successfully forwarded {success_count} emails.  """
                + fail_message
                + up_to_date_message
                + limit_message,
            )
        except ConnectionError:
            messages.success(
                request,
                f"The request do the Readwise API failed.  Try again in a few minutes.",
            )
        request.user.last_readwise_update_articles = datetime.now()
        request.user.save()
    else:
        messages.success(
            request,
            mark_safe(
                f"""The "Collect Readwise Summaries" feature collects article summarizies generated by Readwise and forwards them to your email address.
You must provide an email address and a <a href="https://readwise.io/access_token">Readwise API key</a> in your <a href="/admin/accounts/customuser/{request.user.id}/change">Settings</a>.
Note that Readwise is not a free service.
"""
            ),
        )
    return redirect_to_previous_page(request)

    # return redirect("/admin/main/phrase")


def get_my_level_view(request):
    qs = Phrase.objects.filter(
        user=request.user, language=request.user.working_on
    ).values_list("cleaned_text", "cosine_similarity")
    tuple_list = list(qs)
    # print(tuple_list_to_csv(tuple_list))
    llm_completion = get_my_level(
        word_list=tuple_list,
        working_on=request.user.working_on,
        openai_model=OPENAI_LLM_MODEL,
    )
    llm_completion = llm_completion if llm_completion else ""
    messages.success(
        request, llm_completion,
    )
    return redirect("/admin/main/phrase")
    # return redirect("https://www.nytimes.com")


# def view_phrase_lists(request):
#     phrase_lists = get_all_phrase_lists(os.path.join(settings.BASE_DIR, "purepython"))
#     return render(
#         request,
#         "phrase_lists.html",
#         {"list_title": "Phrase Lists", "items": phrase_lists},
#     )
from main.models import LANGUAGE_CHOICES
from django import forms


class LanguageChoiceForm(forms.Form):
    choice_field = forms.ChoiceField(choices=LANGUAGE_CHOICES, required=True)


def add_multiple_phrases(request):
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
            "phrase_lists.html",
            {
                "form": LanguageChoiceForm(
                    initial={"choice_field": request.user.working_on}
                )
            },
        )


def update_readwise(request, populate_extra_fields_via_llm=False):
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
    except ProxyError as e:
        # see https://www.pythonanywhere.com/forums/topic/33818/
        messages.success(
            request,
            f"""Encountered a proxy error.  The hosting service doesn't currently allow access to the Readwise API.""",
        )
        return redirect("/admin/main/phrase")
    digest = make_digest(all_data, supported_languages=SUPPORTED_LANGUAGES)
    # messages.success(request, pprint.pformat(digest))
    counter = 0
    for item in digest:
        # print(request.user.native_language)
        if item[1] != request.user.native_language:
            if populate_extra_fields_via_llm:  # slow!
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
    return redirect("/admin/main/phrase")


def prompt_view(request):
    if request.method == "POST":
        attempted_translation = request.POST.get("prompt", "")
        # print(attempted_translation)
        if attempted_translation == "":
            return redirect("prompt_view")
        # response_text = prompt + "yes we can"
        # print(attempted_translation)
        # print(attempted_translation)
        # print(request.session.get("full_working_on_sentence", ""))
        # print(
        #     [request.session.get("full_working_on_sentence", ""), attempted_translation]
        # )
        embeddings = get_embeddings(
            [request.session.get("full_working_on_sentence", ""), attempted_translation]
        )
        cosine_similarity = compute_cosine_similarity(embeddings[0], embeddings[1])
        # print(attempted_translation)
        feedback = get_feedback(
            request.session.get("equivalent_native_language_sentence", ""),
            attempted_translation,
            working_on=request.session.get("working_on", ""),
            native_language=request.session.get("native_language", ""),
        )

        phrase_object = Phrase.objects.get(id=request.session.get("phrase_id", ""))
        phrase_object.cosine_similarity = cosine_similarity
        if phrase_object.user == request.user:  # only if user is logged in
            phrase_object.save()

        return render(
            request,
            "prompt.html",
            {
                "english_sentence": request.session[
                    "equivalent_native_language_sentence"
                ],
                "attempted_translation": attempted_translation,
                "response": feedback,
                # + "\n"
                # + f"\n"
                # + f"\nPhrase: {phrase_object.cleaned_text}"
                # + f"\nCosine Similarity: {str(round(cosine_similarity,4))}"
                # + f"\nModel: {OPENAI_EMBEDDINGS_MODEL}",
                "phrase": phrase_object.cleaned_text,
                "cosine_similarity": str(round(cosine_similarity, 4)),
                "model": OPENAI_EMBEDDINGS_MODEL,
            },
        )

    ########################################################################
    # GET
    # Get most relevant phrase
    # print(request.user)

    if request.user.is_authenticated:
        native_language_code = request.user.native_language
        working_on_code = request.user.working_on
        qs = Phrase.objects.filter(user=request.user, language=working_on_code)
    else:
        native_language_code = "en"
        working_on_code = "es"
        qs = Phrase.objects.filter(language=working_on_code)
        qs = qs.filter(cosine_similarity__isnull=False)
    native_language = dict(LANGUAGE_CHOICES)[native_language_code]
    working_on = dict(LANGUAGE_CHOICES)[working_on_code]

    if len(qs) == 0:
        # Handle empty data
        return render(
            request,
            "prompt.html",
            {
                "english_sentence": "All least one phrase is required for app to work correctly.",
                "no_phrases": True,
            },
        )

    # Update que_score
    # print("""qs.update(cosine_similarity=F("cosine_similarity") + 1)""")
    qs_values = qs.values_list("cosine_similarity")
    # Step 2: Exclude None values
    first_elements = [t[0] for t in qs_values]
    filtered_values = [value for value in first_elements if value is not None]

    # Step 3: Convert to a NumPy array
    numpy_array = np.array(filtered_values)

    # Step 4: Calculate the mean value
    if numpy_array.size > 0:
        mean_value = float(np.mean(numpy_array)) + float(os.environ["FABULARI_PARAM0"])
        stddev_value = float(np.std(numpy_array)) * float(os.environ["FABULARI_PARAM1"])
    else:
        mean_value = 0.50 + float(os.environ["FABULARI_PARAM0"])
        stddev_value = 0.25 * float(os.environ["FABULARI_PARAM1"])

    # if request.user.is_authenticated:
    #     qs.update(
    #         noise=RawSQL(  # for MySQL
    #             f"{mean_value} + {stddev_value} * SQRT(-2 * LOG(RAND())) * COS(2 * PI() * RAND())",
    #             [],
    #         )
    #     )
    #     qs.update(que_score=Coalesce(Abs(F("cosine_similarity") - F("noise")), 0))
    # else:
    print(numpy_array)
    print(mean_value)
    print(stddev_value)
    random_value = np.random.normal(loc=mean_value, scale=stddev_value)
    print(random_value)
    qs = qs.annotate(
        que_score=ExpressionWrapper(
            Abs(F("cosine_similarity") - random_value), output_field=FloatField(),
        )
    ).order_by("que_score")

    # Generate template vars
    # lowest que_score goes first
    next_phrase = qs[0]

    full_working_on_sentence = generate_full_sentence(
        next_phrase.text, working_on=working_on
    )
    equivalent_native_language_sentence = to_native_language(
        full_working_on_sentence,
        working_on=working_on,
        native_language=native_language,
    )

    # store session variables
    request.session["phrase_id"] = next_phrase.id
    request.session["full_working_on_sentence"] = full_working_on_sentence
    request.session[
        "equivalent_native_language_sentence"
    ] = equivalent_native_language_sentence
    request.session["working_on"] = working_on
    request.session["native_language"] = native_language

    return render(
        request,
        "prompt.html",
        {
            "english_sentence": request.session["equivalent_native_language_sentence"],
            "working_on": working_on,
            "last_cosine_similarity": next_phrase.cosine_similarity
            if next_phrase.cosine_similarity
            else "N/A",
            "random_value": round(random_value, 4),
            "que_score": round(
                abs(float(next_phrase.cosine_similarity) - random_value), 4
            )
            if next_phrase.cosine_similarity
            else 0,
        },
    )

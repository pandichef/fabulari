from django.utils import timezone

from datetime import datetime
from requests.exceptions import ProxyError
from django.utils import timezone
from django.conf import settings
from django.shortcuts import redirect
from django.db import IntegrityError
from django.contrib import messages
from django.utils.safestring import mark_safe
from purepython.import_from_readwise import (
    fetch_from_export_api,
    make_digest_multithreaded,
)
from main.models import Phrase
from ..admin import PhraseAdmin
from django.contrib.auth.decorators import login_required
from django.urls import reverse

LANGUAGE_CHOICES = settings.LANGUAGE_CHOICES
# from accounts.models import supported_languages as SUPPORTED_LANGUAGES
SUPPORTED_LANGUAGES = [code for code, _ in LANGUAGE_CHOICES]


@login_required(login_url="/admin/login/")
def import_from_readwise_view(request, populate_extra_fields_via_llm=False):
    if not request.user.readwise_api_key:
        messages.success(
            request,
            mark_safe(
                f"""To highlight phrases using Readwise, you must create a <a href="https://readwise.io/access_token">Readwise API key</a> and save it in your <a href="/admin/accounts/customuser/{request.user.id}/change">Settings</a>.
Note that Readwise is not a free service."""
            ),
        )
        # return redirect("/admin/main/phrase")
        return redirect(reverse("admin:main_phrase_changelist"))
    try:
        from pprint import pprint

        # assert False, request.user.last_readwise_update.is_aware()
        print("request.user.last_readwise_update.isoformat()")
        from django.utils import timezone

        print(request.user.last_readwise_update.astimezone(timezone.utc).isoformat())
        all_data = fetch_from_export_api(
            updated_after=request.user.last_readwise_update.isoformat(),
            token=request.user.readwise_api_key,
        )
        # print("all_data")
        # pprint(all_data)
        digest = make_digest_multithreaded(
            all_data,
            supported_language_codes=SUPPORTED_LANGUAGES,
            openai_model=settings.OPENAI_LLM_MODEL_SIMPLE_TASKS,
        )
        # messages.success(request, pprint.pformat(digest))
        filtered_digest = [
            item
            for item in digest
            if item[1] != request.user.native_language
            or request.user.retrieve_native_language_from_readwise
        ]
        filtered_digest_dicts = [
            {"translated_raw_text": item[0], "language": item[1]}
            for item in filtered_digest
        ]
        from purepython.create_phrase_object import get_phrase_metadata

        from time import time

        t0 = time()
        obj_datas = list(
            get_phrase_metadata(
                filtered_digest_dicts,
                native_language=request.user.native_language,
                # openai_model=settings.OPENAI_LLM_MODEL_SIMPLE_TASKS,
                openai_model=request.user.openai_llm_model_complex_tasks,
            )
        )
        new_phrase_objects = [
            Phrase(
                raw_text=item["translated_raw_text"],
                language=item["language"],
                cleaned_text=item["cleaned_text"],
                example_sentence=item["example_sentence"],
                definition=item["definition"],
                sanity_check=item["sanity_check"],
                user=request.user,
            )
            for item in obj_datas
        ]
        before = Phrase.objects.count()
        Phrase.objects.bulk_create(new_phrase_objects, ignore_conflicts=True)
        after = Phrase.objects.count()
        readwise_phrase_count = len(new_phrase_objects)
        successful_saves_count = after - before
        # assert False, new_phrase_objects

        # counter = 0
        # for item in filtered_digest:
        #     if populate_extra_fields_via_llm:  # slow! off by default
        #         # todo: make this multithreaded
        #         obj = Phrase(user=request.user, text=item[0], language=item[1])
        #         was_retrieved = PhraseAdmin.save_model(  # this is a hack
        #             self=None, request=request, obj=obj, form=None, change=False
        #         )
        #         if was_retrieved:
        #             counter += 1
        #     else:
        #         obj = Phrase(
        #             user=request.user,
        #             text=item[0],
        #             language=item[1],
        #             cleaned_text=item[0],
        #         )
        #         try:
        #             obj.save()
        #             counter += 1
        #         except IntegrityError:
        #             pass
        #         # save_phrase_model(request, obj)
        datetime_1901 = timezone.make_aware(
            datetime(1901, 1, 1), timezone.get_current_timezone()
        )
        summary_text = f"""Saved {successful_saves_count} items from Readwise.  (Fetched {readwise_phrase_count} from Readwise and there were {readwise_phrase_count-successful_saves_count} duplicates.)"""
        if request.user.last_readwise_update < datetime_1901:
            messages.success(
                request,
                summary_text
                + f"""  Going forward, only new items will be retrieved.""",
            )
        else:
            messages.success(
                request,
                summary_text
                + f"""  Previously updated {request.user.last_readwise_update.strftime("%B %d, %Y at %I:%M %p")} (server time).""",
            )

        request.user.last_readwise_update = timezone.now()
        request.user.save()
    except ProxyError as e:
        # see https://www.pythonanywhere.com/forums/topic/33818/
        messages.success(
            request,
            f"""Encountered a proxy error.  The hosting service (PA) doesn't currently allow access to the Readwise API.""",
        )
        # return redirect("/admin/main/phrase")
        return redirect(reverse("admin:main_phrase_changelist"))
    except Exception as err:
        messages.error(
            request, f"{err}",
        )
    # return redirect("/admin/main/phrase")
    return redirect(reverse("admin:main_phrase_changelist"))

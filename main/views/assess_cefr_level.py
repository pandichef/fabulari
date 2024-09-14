from django.conf import settings
from django.shortcuts import redirect
from django.contrib import messages
from purepython.assess_cefr_level import assess_cefr_level
from main.models import Phrase
from django.contrib.auth.decorators import login_required
from django.urls import reverse


LANGUAGE_CHOICES = settings.LANGUAGE_CHOICES
SUPPORTED_LANGUAGES = [code for code, _ in LANGUAGE_CHOICES]


@login_required(login_url=reverse("admin:login"))
def assess_cefr_level_view(request):
    qs = Phrase.objects.filter(
        user=request.user, language=request.user.working_on
    ).values_list("cleaned_text", "cosine_similarity")
    tuple_list = list(qs)
    # print(tuple_list_to_csv(tuple_list))
    llm_completion = assess_cefr_level(
        word_list=tuple_list,
        working_on=dict(LANGUAGE_CHOICES)[request.user.working_on],
        openai_model=request.user.openai_llm_model_complex_tasks,
    )
    llm_completion = llm_completion if llm_completion else ""
    messages.success(
        request, llm_completion,
    )
    return redirect("/admin/main/phrase")
    # return redirect("https://www.nytimes.com")

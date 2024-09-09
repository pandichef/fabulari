from markdown2 import markdown
from django import forms
from django.core.mail import send_mail
from django import forms
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.utils.safestring import mark_safe
from purepython.create_study_materials import (
    create_article,
    create_article_title,
    create_readwise_item,
)


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
        description_of_article = request.POST.get("words_input")
        # subject_split = description_of_article.split()[:10]
        # if len(subject_split):
        # subject = description_of_article
        # else:
        # subject = " ".join(subject_split) + "..."
        # sanitized_subject = subject.replace("\n", "").replace("\r", "")
        if gpt_first:
            # print("first")
            article = create_article(
                description_of_article=description_of_article,
                openai_model=request.user.openai_llm_model_complex_tasks,
            )
        else:
            # print("not first")
            article = description_of_article
        subject = create_article_title(
            body_of_article=article, openai_model=settings.OPENAI_LLM_MODEL_SIMPLE_TASKS
        )

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
                author="fabulari",
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

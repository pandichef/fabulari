import re
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
from django.contrib.auth.decorators import login_required
from django.urls import reverse


def convert_to_markdown_if_plain_text(text: str) -> str:
    """
    Generated by ChatGPT

    Converts plain text into markdown format, or returns the input unchanged if it already contains markdown syntax.
    
    - Detects common markdown patterns such as headers, bold, italic, links, and lists.
    - If no markdown is detected, converts plain text by:
        - Treating single newlines as line breaks (two spaces + newline in markdown).
        - Treating double newlines as paragraph breaks.
    
    Args:
        text (str): The input text, either plain text or markdown.
    
    Returns:
        str: The text formatted as markdown.
    """
    # Define a basic check for markdown content
    markdown_patterns = [
        r"^#{1,6}\s",  # Headers
        r"\*\*.*\*\*",  # Bold
        r"\*.*\*",  # Italic
        r"\[.*\]\(.*\)",  # Links
        r">\s",  # Blockquotes
        r"`.*`",  # Inline code
        r"^\s*\d+\.\s",  # Ordered lists
        r"^\s*[-+*]\s",  # Unordered lists
    ]

    # Check if any markdown pattern is found in the input
    for pattern in markdown_patterns:
        if re.search(pattern, text, re.MULTILINE):
            return text  # Return as-is if markdown is detected

    # If no markdown is found, convert plain text to markdown
    # First, handle paragraphs (separated by two or more newlines)
    paragraphs = text.split("\n\n")

    # Convert each paragraph separately
    formatted_paragraphs = []
    for paragraph in paragraphs:
        # Convert single line breaks inside paragraphs to markdown line breaks (two spaces + \n)
        formatted_paragraph = paragraph.replace("\r\n", "  \n").replace("\n", "  \n")
        formatted_paragraphs.append(formatted_paragraph)

    # Join paragraphs with double newlines for markdown paragraph separation
    return "\n\n".join(formatted_paragraphs)


# # Example usage
# plain_text = """This is a plain text example.
# It has multiple lines in the same paragraph.
# Here's a new paragraph with more text.

# And here is another paragraph."""

# markdown_text = """# This is a markdown example
# - This line is in markdown
# - Here's another item"""

# print("Converted plain text to markdown:")
# print(convert_to_markdown(plain_text))

# print("\nMarkdown input (unchanged):")
# print(convert_to_markdown(markdown_text))


class UseGPTRadioButtonForm(forms.Form):
    choice_field = forms.ChoiceField(
        choices=[(0, "Don't filter through GPT"), (1, "Filter through GPT First")],
        required=True,
        widget=forms.RadioSelect,
        initial=1,
    )


def redirect_to_previous_page(request, fallback_url="/"):
    return redirect(request.META.get("HTTP_REFERER", fallback_url))


@login_required(login_url="/admin/login/")
def create_study_materials_view(request):
    if request.method == "POST":
        action = request.POST.get("action")
        print(action)
        if action == "try_again":
            return redirect_to_previous_page(request)
        # subject_split = description_of_article.split()[:10]
        # if len(subject_split):
        # subject = description_of_article
        # else:
        # subject = " ".join(subject_split) + "..."
        # sanitized_subject = subject.replace("\n", "").replace("\r", "")

        if request.session["article_in_html"]:
            article_in_html = request.session["article_in_html"]
            subject = request.session["article_title"]
        else:
            gpt_first = int(request.POST.get("choice_field"))
            description_of_article = request.POST.get("words_input")
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
                body_of_article=article,
                openai_model=settings.OPENAI_LLM_MODEL_SIMPLE_TASKS,
            )

            # def plaintext_to_markdown(text):
            #     # Replace single carriage returns or newlines with a markdown line break (two spaces + newline)
            #     formatted_text = text.replace("\r\n", "  \n").replace("\n", "  \n")
            #     return formatted_text

            article_in_html = markdown(convert_to_markdown_if_plain_text(article))

        if action == "preview_first":
            request.session["article_title"] = subject
            request.session["article_in_html"] = article_in_html
            return render(
                request,
                "create_study_materials.html",
                {
                    "form": UseGPTRadioButtonForm(),
                    "article": f"<h3>{subject}</h3>" + article_in_html,
                    "preview_page": True,
                },
            )
        else:
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
                success = False
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
            request.session["article_title"] = None
            request.session["article_in_html"] = None
            return redirect("/admin/main/phrase")
            # return redirect("/create_article")
    else:
        request.session["article_title"] = None
        request.session["article_in_html"] = None
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

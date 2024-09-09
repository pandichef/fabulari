import requests
from typing import Tuple
from purepython.practice_translation import (
    generate_full_sentence,
    # OPENAI_LLM_MODEL,
    client,
    to_native_language,
)


def create_article(
    description_of_article: str,  # e.g., "The history of Mongolia in 300 words",
    openai_model,  # e.g., ="gpt-4o-mini"
) -> str:
    completion = client.chat.completions.create(
        model=openai_model,
        messages=[
            {
                "role": "system",
                "content": f"""
You generate new content based on a user's prompt.  There are two possibilities.
One possibility is to create a new content from scrach.  For example, the user might type "the history of Mongolia" or "a haiku about Richard Nixon".
In either case, the content should be the length of a typical newspaper article, unless the user explicitly requests a different length.
The other possibility is to fetch existing content.  For example, the user might type "The lyrics to Stairway to Heaven" 
or "The first act of Hamlet". In such cases, return the content verbatim without regard to the length of the text.
""",
            },
            {"role": "user", "content": f"""{description_of_article}""",},
        ],
    )
    return completion.choices[0].message.content


def create_article_title(body_of_article, openai_model) -> str:  # ="gpt-4o-mini"
    completion = client.chat.completions.create(
        model=openai_model,
        messages=[
            {
                "role": "system",
                "content": f"""
You generate a title for articles given the body of the article.  The title must be less than or equal to 10 words.
The context will contain the body of the article and nothing else.
The text provide might also be a well known document, for example the lyrics to "Stairway to Heaven".
If so, the title should be "Lyrics to Stairway to Heaven by Led Zeppelin".
""",
            },
            {"role": "user", "content": f"""{body_of_article}""",},
        ],
    )
    return completion.choices[0].message.content


def create_readwise_item(
    token,
    title,
    body_in_html,
    author,  # ="fabulari",
    url,  # ="https://yourapp.com#document1",
    image_url=None,
):
    params = {
        "url": url,
        "html": body_in_html,
        "should_clean_html": False,
        "title": title,
        "author": author,
        "summary": "The document is itself a summary",
        "location": "feed",
        "category": "email",
        "tags": ["summary"],
    }
    if image_url:
        params["image_url"] = image_url

    res = requests.post(
        url="https://readwise.io/api/v3/save/",
        headers={"Authorization": f"Token {token}"},
        json=params,
    )
    return res

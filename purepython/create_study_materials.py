from typing import Tuple
from purepython.practice_translation import (
    generate_full_sentence,
    OPENAI_LLM_MODEL,
    client,
    to_native_language,
)


def create_article(
    description_of_article="The history of Mongolia in 300 words",
    openai_model=OPENAI_LLM_MODEL,
) -> str:
    completion = client.chat.completions.create(
        model=openai_model,
        messages=[
            {
                "role": "system",
                "content": f"""
You generate new articles based on a user's prompt.  For example, the user might ask "write me an article about the
history of Mongolia".  The article must be less than or equal to 10 paragraphs.""",
            },
            {"role": "user", "content": f"""{description_of_article}""",},
        ],
    )
    return completion.choices[0].message.content


def create_article_title(body_of_article, openai_model=OPENAI_LLM_MODEL,) -> str:
    completion = client.chat.completions.create(
        model=openai_model,
        messages=[
            {
                "role": "system",
                "content": f"""
You generate a title for articles given the body of the article.  The title must be less than or equal to 10 words.
The context will contain the body of the article and nothing else.
""",
            },
            {"role": "user", "content": f"""{body_of_article}""",},
        ],
    )
    return completion.choices[0].message.content


import requests


def create_readwise_item(
    token,
    title,
    body_in_html,
    author="fabulari",
    url="https://yourapp.com#document1",
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

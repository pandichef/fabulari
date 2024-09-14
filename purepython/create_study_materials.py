import requests
from typing import Tuple
from purepython.practice_translation import (
    generate_full_sentence,
    # OPENAI_LLM_MODEL,
    client,
    to_native_language,
)
from .assess_cefr_level import tuple_list_to_csv


def create_article_from_user_prompt(
    description_of_article: str,  # e.g., "The history of Mongolia in 300 words",
    openai_model,  # e.g., ="gpt-4o-mini"
) -> str | None:
    completion = client.chat.completions.create(
        model=openai_model,
        messages=[
            {
                "role": "system",
                "content": f"""
You generate new content based on a user's prompt.  There are two possibilities.
One possibility is to create a new content from scratch.  For example, the user might type "the history of Mongolia" or "a haiku about Richard Nixon".
In either case, the content should be the length of a typical newspaper article, unless the user explicitly requests a different length.
The other possibility is to fetch existing content.  For example, the user might type "The lyrics to Stairway to Heaven" 
or "The first act of Hamlet". In such cases, return the content verbatim without regard to the length of the text.
""",
            },
            {"role": "user", "content": f"""{description_of_article}""",},
        ],
    )
    return completion.choices[0].message.content


def create_article_from_phrase_list(
    word_list: list,  # e.g., [("casa", 0.80), ("perro", None), ("hijo", 0.5)],
    working_on: str,  # e.g., "Spanish"
    additional_context: str,  # e.g., "The history of Mongolia in 300 words",
    openai_model,  # e.g., ="gpt-4o-mini"
) -> str | None:
    word_list_as_str = tuple_list_to_csv(word_list)
    if additional_context:
        additional_context = f'If possible, in the context of the phrase list, choose a theme that is closely related to "{additional_context}".'

    completion = client.chat.completions.create(
        model=openai_model,
        messages=[
            {
                "role": "system",
                "content": f"""The CEFR organises {working_on} language proficiency into six levels from A1 to C2.
You assess the level of students' proficiency based on phrase lists that the student is currently working on.
Then you create an article using the phrase list at the CEFR level implied by the phrase list.
Do provide any commentary about the CEFR score of the user and do not provide a title to the article.
""",
            },
            {
                "role": "user",
                "content": f"""Below is a set of {working_on} phrases in CSV format.
The first items is the phrase that the student is working on.  The second is a score which indicates how well the student knows the phrase. 
A higher score indicates more proficiency.  The student hasn't been tested yet if the word is missing a score.
You can assume such words are quite new to the student and she would find them relatively challenging to use.
Estimate the student's {working_on} CEFR level based on these data.
Then you create an article using the phrase list at the CEFR level implied by the phrase list.
The article should emphasize new words (i.e., the ones that don't have a score) and the one that are neither too easy nor too hard 
(i.e., the ones that have scores generally near the middle of the range).  Do provide any commentary about the CEFR score of the user.
For example, don't say things like "the student appears to be operating at a CEFR level of A2 or possibly early B1" in either English or
{working_on}.  Only provide the text of the article.  Words and phrases from the word list should be in bold (using ** markdown syntax).
The content should be the length of a typical newspaper article, unless the user explicitly requests a different length. {additional_context}
\n\n{tuple_list_to_csv(word_list)}""",
            },
        ],
    )
    return completion.choices[0].message.content


def create_article_title(body_of_article, openai_model) -> str | None:  # ="gpt-4o-mini"
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
The CEFR organises language proficiency into six levels from A1 to C2.
Assess the article's CEFR level and indicate this level at the end of the title.  For example,
"La Historia de Gatos (A2)".
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

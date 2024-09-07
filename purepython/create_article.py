from typing import Tuple
from purepython.gptsrs import (
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

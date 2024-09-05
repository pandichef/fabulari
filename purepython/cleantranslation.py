from typing import Tuple
from purepython.gptsrs import (
    generate_full_sentence,
    OPENAI_LLM_MODEL,
    client,
    to_native_language,
)


def clean_phrase(
    phrase: str, working_on: str = "Spanish", openai_model: str = OPENAI_LLM_MODEL
) -> str:
    completion = client.chat.completions.create(
        model=openai_model,
        messages=[
            {
                "role": "system",
                # "content": f"You translate {'phrases' if phrase else 'sentences'} from {working_on} to {native_language}.",
                "content": f"""
You take potentially sloppily written words or phrases in {working_on} and return a cleaned up version of the same word or phrase.
If the input word is a conjugated verb, convert the word to its infinitive.
If the input word is a plural noun, convert the word to its singular version.
""",
            },
            {"role": "user", "content": phrase},
        ],
    )
    return completion.choices[0].message.content


def phrase_to_native_language(
    phrase,
    working_on="Spanish",
    native_language="English",
    openai_model=OPENAI_LLM_MODEL,
    # phrase=None,
) -> Tuple:
    cleaned_phrase = clean_phrase(phrase, working_on=working_on)
    example_sentence = generate_full_sentence(
        cleaned_phrase, working_on=working_on, openai_model=openai_model
    )
    definition_prompt = f"""I am a native {native_language} speaker trying to learn {working_on}.

Please translate the {working_on} word or phrase "{cleaned_phrase}" to {native_language} as it was used in the following sentence:
{example_sentence}

Do not include extra punctuation like leading and trailing quotes in the completion.
Do not provide a translation of the example sentence, only a translation of the word or phrase above.
"""

    # If the {working_on} word is a verb, also indicate the grammatical form.  For example, "preguntar" would "preguntar".

    # cleanup up phrase, definition, example sentence
    # return (1,)

    completion = client.chat.completions.create(
        model=openai_model,
        messages=[
            {
                "role": "system",
                # "content": f"You translate {'phrases' if phrase else 'sentences'} from {working_on} to {native_language}.",
                "content": f"You translate phrases from {working_on} to {native_language}.",
            },
            {"role": "user", "content": definition_prompt},
        ],
    )
    definition = completion.choices[0].message.content
    print(definition)
    print(definition)
    print(definition)
    print(definition)
    return (cleaned_phrase, example_sentence, definition)

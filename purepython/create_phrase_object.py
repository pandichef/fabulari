from typing import Tuple, Dict, Any
from purepython.practice_translation import (
    generate_full_sentence,
    # OPENAI_LLM_MODEL,
    client,
    to_native_language,
)
from .settings import LANGUAGE_CHOICE_DICT


def clean_text(
    phrase: str,  # e.g., "tener"
    working_on_verbose: str,  # e.g., Spanish
    openai_model: str,  # e.g., "gpt-4o-mini"
) -> str | None:
    # print(working_on_verbose)
    # print(working_on_verbose)
    # print(working_on_verbose)
    # print(working_on_verbose)

    """User is assumed to input imperfect phrase.  This function sanitizes the phrase."""
    if working_on_verbose == "Hebrew":
        # print("asfsafsdaf")
        semitic_language_extra = "Moreover, The response phrase should include the vowel characters for pedagogic purposes.  For example, the reponse should be בַּיִת instead of בית."
    elif working_on_verbose == "Arabic":
        semitic_language_extra = "Moreover, The response phrase should include the vowel characters for pedagogic purposes.  For example, the reponse should be مَنْزِل instead of منزل."
    else:
        semitic_language_extra = ""

    completion = client.chat.completions.create(
        model=openai_model,
        messages=[
            {
                "role": "system",
                # "content": f"You translate {'phrases' if phrase else 'sentences'} from {working_on} to {native_language}.",
                "content": f"""
You take potentially sloppily written words or phrases in {working_on_verbose} and return a cleaned up version of the same word or phrase.
The repsonse phrase should also be in {working_on_verbose}. {semitic_language_extra}
If the input phrase is a conjugated verb, convert the word to its infinitive.
However, if the input phrase merely contains a verb, use the original form so it will be grammatically correct.
If the input word is a plural noun, convert the word to its singular version.
Do not include extra commentary e.g., don't response with something like "vaca (singular form of vacas)".
If the phrase appears to contain a proper name but has additional content, the response should remove the proper noun from the cleaned phrase.
For example, the cleaned version of "José va caminando a casa" would be "ir caminando a casa".
If the phrase appears to be a proper name and nothing else, the response should be the exact string "(proper name)", which contains exactly 13 characters.
Ensure that the cleaned phrase is syntactically correct.  Examples:
The cleaned phrase can be "chica bonita", not "chica bonito".
The cleaned phrase can be "how are you today" but not "how be you today".
The cleaned phrase can be "como estas hoy" but not "como estar hoy".
Do not include any excess punctuation e.g., the clean phrase should not be "(jainism)", just "jainism".
""",
            },
            {"role": "user", "content": phrase},
        ],
    )
    return completion.choices[0].message.content


from purepython.parallel_map import mapify

# from purepython.create_phrase_object import get_phrase_metadata

# get_phrase_metadata_multithreaded = mapify(get_phrase_metadata)


@mapify
def get_phrase_metadata(
    input_dict: Dict[str, Any],
    # phrase: str,
    # working_on_code: str,  # = "es",
    native_language: str,  # = "en",
    openai_model: str  # = "gpt-4o-mini",
    # phrase=None,
) -> Dict[str, Any] | None:

    translated_raw_text = input_dict["translated_raw_text"]
    working_on_verbose = LANGUAGE_CHOICE_DICT[input_dict["language"]]
    native_language_verbose = LANGUAGE_CHOICE_DICT[native_language]

    """Gets extra data e.g., cleaned_phrase, definition, example sentence"""
    if len(translated_raw_text) < 2:  # at least 2 characters
        return None
    cleaned_text = clean_text(
        phrase=translated_raw_text,
        working_on_verbose=working_on_verbose,
        openai_model=openai_model,
    )
    if "(proper name)" in cleaned_text:
        return None
    example_sentence = generate_full_sentence(
        cleaned_text, working_on_verbose=working_on_verbose, openai_model=openai_model
    )
    # definition_prompt =

    # If the {working_on} word is a verb, also indicate the grammatical form.  For example, "preguntar" would "preguntar".

    # cleanup up phrase, definition, example sentence
    # return (1,)

    completion = client.chat.completions.create(
        model=openai_model,
        messages=[
            {
                "role": "system",
                # "content": f"You translate {'phrases' if phrase else 'sentences'} from {working_on} to {native_language}.",
                "content": f"You translate phrases from {working_on_verbose} to {native_language_verbose}.",
            },
            {
                "role": "user",
                "content": f"""I am a native {native_language_verbose} speaker trying to learn {working_on_verbose}.

Please translate the {working_on_verbose} word or phrase "{cleaned_text}" to {native_language_verbose} as it was used in the following sentence:
{example_sentence}

Do not include extra punctuation like leading and trailing quotes in the completion.
Do not provide a translation of the example sentence, only a translation of the word or phrase above.
""",
            },
        ],
    )
    definition = completion.choices[0].message.content
    print(definition)
    return_dict = {
        "cleaned_text": cleaned_text,
        "example_sentence": example_sentence,
        "definition": definition,
    }
    input_dict.update(return_dict)
    return input_dict

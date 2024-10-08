import numpy as np
from openai import OpenAI

# https://github.com/openai/openai-python/blob/release-v0.28.1/openai/embeddings_utils.py

client = OpenAI()

# OPENAI_LLM_MODEL = "gpt-4o-mini"
# OPENAI_EMBEDDINGS_MODEL = "text-embedding-3-large"


# LANGUAGE = "Spanish"
# OPENAI_LLM_MODEL = model="gpt-4o-mini"
# OPENAI_EMBEDDINGS_MODEL = "text-embedding-ada-002"
# OPENAI_EMBEDDINGS_MODEL = "text-similarity-davinci-001"


def generate_full_sentence(
    phrase: str,  # e.g., tener
    working_on_verbose: str,  # ="Spanish",
    openai_llm_model: str,  # ="gpt-4o-mini"
) -> str | None:
    hebrew_arabic_suffix = """
Even if the original {working_on} word or phrase doesn't have vowels, add the vowels in the output."""
    if working_on_verbose == "Hebrew":
        hebrew_arabic_suffix = (
            hebrew_arabic_suffix.format(working_on=working_on_verbose)
            + """\nFor example, if the user types בית, the clean phrase would be בַּיִת.  If the user types לישון, the clean phrase would be לִישׁוֹן."""
        )
    elif working_on_verbose == "Arabic":
        hebrew_arabic_suffix = (
            hebrew_arabic_suffix.format(working_on=working_on_verbose)
            + """\nFor example, if the user types منزل, the clean phrase would be مَنْزِل.  If the user types للنوم, the clean phrase would be لِلنَّوْمِ."""
        )
    else:
        hebrew_arabic_suffix = ""

    completion = client.chat.completions.create(
        model=openai_llm_model,
        messages=[
            {
                "role": "system",
                "content": f"""You take a phrase in {working_on_verbose} generate a random but terse sentence that contains the exact phrase.  
The sentence should have no more than 8 words.
Make sure the actual phrase is being used.  For example, in the example "en cuanto a", 
the sentence "El precio está en cuanto en mi opinión." contains a similar string "en cuanto", 
but this obviously doesn't convey the correct sense of the phrase "en cuanto a".
The result should only contain UTF characters in {working_on_verbose}.
Make sure the sentence is grammatically correct.
"""
                + hebrew_arabic_suffix,
            },
            {"role": "user", "content": phrase},
        ],
    )
    # if working_on_verbose == "Hebrew":
    #     return '<p dir="rtl">' + str(completion.choices[0].message.content) + "</p>"
    # elif working_on_verbose == "Arabic":
    #     return '<p dir="rtl">' + str(completion.choices[0].message.content) + "</p>"
    # else:
    return completion.choices[0].message.content


def to_native_language(
    sentence: str,
    working_on_verbose: str,  # ="Spanish",
    native_language_verbose: str,  # ="English",
    openai_llm_model: str,  # ="gpt-4o-mini",
    # phrase=None,
) -> str | None:
    # Sometimes Chinese appears in the output randomly in gpt-4o-mini;
    # this isn't a problem in gpt-4o
    if native_language_verbose != "Chinese":
        chinese_character_hack = f"  The output cannot contain Chinese characters.  Translate any Chinese characters to {native_language_verbose} first."
    else:
        chinese_character_hack = ""

    completion = client.chat.completions.create(
        model=openai_llm_model,
        messages=[
            {
                "role": "system",
                # "content": f"You translate {'phrases' if phrase else 'sentences'} from {working_on} to {native_language}.",
                "content": f"""You translate sentences from {working_on_verbose} to {native_language_verbose}.""",
            },
            {
                "role": "user",
                "content": sentence
                + f"""\n\nPlease translate this to {native_language_verbose} and use only {native_language_verbose} characters."""
                + chinese_character_hack,
            },
        ],
    )
    return completion.choices[0].message.content


def from_native_language(
    sentence: str,
    working_on_verbose: str,  # ="Spanish",
    native_language_verbose: str,  # ="English",
    openai_llm_model: str,  # ="gpt-4o-mini",
    is_phrases=False,  # I believe this for the i18n in Django
) -> str | None:
    if is_phrases:  # for deploy.py
        system_content = f"""You translate phrases from {native_language_verbose} to {working_on_verbose}.  
The number of words in the translation should be roughly similar to the number of words in the original text.
The formatting should also be similar.  For example, "native language" would be "lengua materna" in Spanish with 
2 words and all lower case letters.  The reponse should not contain any punctuation unless the punctuation is also
in the original text.  For example, "native language" should not be translated as "lengua materna." with a trailing period character.
The response should mimic the punctuation of the original text as much as possible.  For example, "Save as new" should be translated as 
"Guardar como nuevo" not "guardar como nuevo".
"""
    else:
        system_content = f""""You translate sentences from {native_language_verbose} to {working_on_verbose}.  
If the {native_language_verbose} sentence lacks certain punctuation, the {working_on_verbose} version should mirror the lack of punctuation."""

    completion = client.chat.completions.create(
        model=openai_llm_model,
        messages=[
            {"role": "system", "content": system_content,},
            {"role": "user", "content": sentence},
        ],
    )
    return completion.choices[0].message.content


# from .settings import SUPPORTED_LANGUAGES

# The response should be one of the follow language codes:
# {','.join(SUPPORTED_LANGUAGES)}


def detect_language_code(phrase: str, openai_llm_model: str):  # e.g., "gpt-4o-mini",
    completion = client.chat.completions.create(
        model=openai_llm_model,
        messages=[
            {
                "role": "system",
                "content": f"""
You identify the ISO language code for a given input phrase.
In the response, just provide the ISO.  For example, if you detect Spanish, just return the two characters "es".
If there is ambiguity, choose the language is that more commonly studied.
For example, while "caravana" is used in both Spanish (es) and Italian (it), respond with "es" since
Spanish is a much more commonly used and studied language. The reponse is almost always 2 or 3 characters and no more.
""",
            },
            {"role": "user", "content": phrase},
        ],
    )
    return completion.choices[0].message.content


# def get_embedding(text, model=OPENAI_EMBEDDINGS_MODEL):
#     text = text.replace("\n", " ")

#     return client.embeddings.create(input=[text], model=model).data[0].embedding
# from typing import List


def get_embeddings(
    sentences: list, openai_embeddings_model: str
):  # e.g., "text-embedding-3-large"
    objects = client.embeddings.create(
        model=openai_embeddings_model, input=sentences
    ).data
    # embeddings = [np.array(data["embedding"]) for data in response["data"]]
    embedding_vectors = [object.embedding for object in objects]
    return embedding_vectors


def compute_cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def get_feedback(
    sentence_in_native_language: str,
    attempted_translation: str,
    phrase_being_studied: str,
    working_on: str,  # ="Spanish",
    native_language: str,  # ="English",
    openai_model: str,  # ="gpt-4o-mini",
) -> str | None:
    completion = client.chat.completions.create(
        model=openai_model,
        messages=[
            {
                "role": "system",
                "content": f"""The user is a native {native_language} speaker.  
You provide feedback on a user's attempted translation from {native_language} to {working_on}.  
Ignore accent marks since the user might not have access the appropriate keyboard.
For example, if the user types llegare instead of llegaré, do not provide feedback on this.
Ignore punctuation errors.  For example, if the user types "por cierto has visto mi libro", don't point out the missing comma and question mark.
While the feedback should include corrected versions of individual words, the feedback should also highlight nuances of grammar and style.  
Simply provide the raw feedback in {native_language} without judging the response or providing encouragement.
For example, don't use phrases like "good job" or "keep practicing".
If the translation is 100% perfect, start with the word "Correct", but suggest alternative options, if appropriate.
""",
            },
            {
                "role": "user",
                "content": f"""The user translated the sentence "{sentence_in_native_language}" as "{attempted_translation}".  
Since the {working_on} phrase being studied here is {phrase_being_studied}, use this phrase in the corrected translation, where possible.""",
            },
        ],
    )
    return completion.choices[0].message.content


# if __name__ == "__main__":
#     phrase_list = ["en cuanto a"]
#     full_spanish_sentence = generate_full_sentence(phrase_list[0])
#     equivalent_english_sentence = to_native_language(full_spanish_sentence)
#     attempted_translation = input(f"{equivalent_english_sentence} >>> ")
#     embeddings = get_embeddings([full_spanish_sentence, attempted_translation])
#     cosine_similarity = compute_cosine_similarity(embeddings[0], embeddings[1])
#     print("-----------------------------------------------")
#     print(get_feedback(equivalent_english_sentence, attempted_translation))
#     print("-----------------------------------------------")
#     print("[Cosine Similarity: ", cosine_similarity, "]")

import numpy as np
from openai import OpenAI

# https://github.com/openai/openai-python/blob/release-v0.28.1/openai/embeddings_utils.py

client = OpenAI()

LANGUAGE = "Spanish"
OPENAI_LLM_MODEL = "gpt-4o-mini"
# OPENAI_LLM_MODEL = model="gpt-4o-mini"
# OPENAI_EMBEDDINGS_MODEL = "text-embedding-ada-002"
OPENAI_EMBEDDINGS_MODEL = "text-embedding-3-large"
# OPENAI_EMBEDDINGS_MODEL = "text-similarity-davinci-001"

phrase_list = ["en cuanto a"]


def generate_full_sentence(phrase, language=LANGUAGE, openai_model=OPENAI_LLM_MODEL):
    completion = client.chat.completions.create(
        model=openai_model,
        messages=[
            {
                "role": "system",
                "content": f"You take a phrase in {language} generate a random but terse sentence that contains the phrase.  The sentence should have no more than 8 words.",
            },
            {"role": "user", "content": phrase},
        ],
    )
    return completion.choices[0].message.content


def to_english(sentence, language=LANGUAGE, openai_model=OPENAI_LLM_MODEL):
    completion = client.chat.completions.create(
        model=openai_model,
        messages=[
            {
                "role": "system",
                "content": f"You translate sentences from {language} to English.",
            },
            {"role": "user", "content": sentence},
        ],
    )
    return completion.choices[0].message.content


def from_english(sentence, language=LANGUAGE, openai_model=OPENAI_LLM_MODEL):
    completion = client.chat.completions.create(
        model=openai_model,
        messages=[
            {
                "role": "system",
                "content": f"You translate sentences from English to {language}.",
            },
            {"role": "user", "content": sentence},
        ],
    )
    return completion.choices[0].message.content


# def get_embedding(text, model=OPENAI_EMBEDDINGS_MODEL):
#     text = text.replace("\n", " ")

#     return client.embeddings.create(input=[text], model=model).data[0].embedding


def get_embeddings(sentences, openai_model=OPENAI_EMBEDDINGS_MODEL):
    objects = client.embeddings.create(model=openai_model, input=sentences).data
    # embeddings = [np.array(data["embedding"]) for data in response["data"]]
    embedding_vectors = [object.embedding for object in objects]
    return embedding_vectors


def compute_cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def get_feedback(
    english_sentence,
    attempted_translation,
    language=LANGUAGE,
    openai_model=OPENAI_LLM_MODEL,
) -> str:
    completion = client.chat.completions.create(
        model=openai_model,
        messages=[
            {
                "role": "system",
                "content": f"""The user is a native English speaker.  
You provide feedback on user's attempted translation from English to {language}.  
Simply provide the raw feedback with judging the response or providing encouragement.  
Also, ignore accent marks since the user might not have access the appropriate keyboard.
For example, treat llegaré and llegare as synonyms.""",
            },
            {
                "role": "user",
                "content": f"""The user translated the sentence "{english_sentence}" as "{attempted_translation}".""",
            },
        ],
    )
    return completion.choices[0].message.content


if __name__ == "__main__":
    full_spanish_sentence = generate_full_sentence(phrase_list[0])
    equivalent_english_sentence = to_english(full_spanish_sentence)
    # print("--------------------")
    # print(full_spanish_sentence)
    # print(equivalent_english_sentence)
    # print("--------------------")
    attempted_translation = input(f"{equivalent_english_sentence} >>> ")

    # Get embeddings
    # full_spanish_sentence_embeddings = get_embedding(full_spanish_sentence)
    # attempted_translation_embeddings = get_embedding(attempted_translation)
    # cosine_similarity = compute_cosine_similarity(
    #     full_spanish_sentence_embeddings, attempted_translation_embeddings
    # )

    # print(cosine_similarity)
    embeddings = get_embeddings([full_spanish_sentence, attempted_translation])
    # embeddings = [np.array(embed) for embed in embeddings]
    cosine_similarity = compute_cosine_similarity(embeddings[0], embeddings[1])
    # print(embeddings)
    # print(type(embeddings[0]))
    # print(embeddings[0])
    # print(type(embeddings[0]))
    print("-----------------------------------------------")
    print(get_feedback(equivalent_english_sentence, attempted_translation))
    print("-----------------------------------------------")
    print("[Cosine Similarity: ", cosine_similarity, "]")

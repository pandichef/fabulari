import numpy as np
from openai import OpenAI

# https://github.com/openai/openai-python/blob/release-v0.28.1/openai/embeddings_utils.py

client = OpenAI()

# LANGUAGE = "Spanish"
OPENAI_LLM_MODEL = "gpt-4o-mini"
# OPENAI_LLM_MODEL = model="gpt-4o-mini"
# OPENAI_EMBEDDINGS_MODEL = "text-embedding-ada-002"
OPENAI_EMBEDDINGS_MODEL = "text-embedding-3-large"
# OPENAI_EMBEDDINGS_MODEL = "text-similarity-davinci-001"


def generate_full_sentence(phrase, working_on="Spanish", openai_model=OPENAI_LLM_MODEL):
    completion = client.chat.completions.create(
        model=openai_model,
        messages=[
            {
                "role": "system",
                "content": f"""You take a phrase in {working_on} generate a random but terse sentence that contains the exact phrase.  
The sentence should have no more than 8 words.
Make sure the actual phrase is being used.  For example, in the example "en cuanto a", 
the sentence "El precio está en cuanto en mi opinión." contains a similarl string "en cuanto", 
but this obviously doesn't convey the correct sense of the phrase "en cuanto a".
""",
            },
            {"role": "user", "content": phrase},
        ],
    )
    return completion.choices[0].message.content


def to_native_language(
    sentence,
    working_on="Spanish",
    native_language="English",
    openai_model=OPENAI_LLM_MODEL,
):
    completion = client.chat.completions.create(
        model=openai_model,
        messages=[
            {
                "role": "system",
                "content": f"You translate sentences from {working_on} to {native_language}.",
            },
            {"role": "user", "content": sentence},
        ],
    )
    return completion.choices[0].message.content


def from_native_language(
    sentence,
    working_on="Spanish",
    native_language="English",
    openai_model=OPENAI_LLM_MODEL,
):
    completion = client.chat.completions.create(
        model=openai_model,
        messages=[
            {
                "role": "system",
                "content": f"You translate sentences from {native_language} to {working_on}.",
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
    sentence_in_native_language,
    attempted_translation,
    working_on="Spanish",
    native_language="English",
    openai_model=OPENAI_LLM_MODEL,
) -> str:
    completion = client.chat.completions.create(
        model=openai_model,
        messages=[
            {
                "role": "system",
                "content": f"""The user is a native {native_language} speaker.  
You provide feedback on user's attempted translation from {native_language} to {working_on}.  
Simply provide the raw feedback in {native_language} without judging the response or providing encouragement.  
Also, ignore accent marks since the user might not have access the appropriate keyboard.
For example, treat llegaré and llegare as synonyms.""",
            },
            {
                "role": "user",
                "content": f"""The user translated the sentence "{sentence_in_native_language}" as "{attempted_translation}".""",
            },
        ],
    )
    return completion.choices[0].message.content


if __name__ == "__main__":
    phrase_list = ["en cuanto a"]
    full_spanish_sentence = generate_full_sentence(phrase_list[0])
    equivalent_english_sentence = to_native_language(full_spanish_sentence)
    attempted_translation = input(f"{equivalent_english_sentence} >>> ")
    embeddings = get_embeddings([full_spanish_sentence, attempted_translation])
    cosine_similarity = compute_cosine_similarity(embeddings[0], embeddings[1])
    print("-----------------------------------------------")
    print(get_feedback(equivalent_english_sentence, attempted_translation))
    print("-----------------------------------------------")
    print("[Cosine Similarity: ", cosine_similarity, "]")

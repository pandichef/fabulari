from typing import Tuple
from purepython.gptsrs import (
    generate_full_sentence,
    OPENAI_LLM_MODEL,
    client,
    to_native_language,
)


def tuple_list_to_csv(tuple_list):
    # Start with the headers
    csv_string = "phrase,score\n"

    # Loop through the data and construct each row
    for word, value in tuple_list:
        value_str = "" if value is None else str(value)
        csv_string += f"{word},{value_str}\n"
    return csv_string


def get_my_level(
    word_list=[("casa", 0.80), ("perro", None), ("hijo", 0.5)],
    working_on="Spanish",
    openai_model=OPENAI_LLM_MODEL,
) -> str:
    completion = client.chat.completions.create(
        model=openai_model,
        messages=[
            {
                "role": "system",
                "content": f"""The CEFR organises {working_on} language proficiency into six levels from A1 to C2.
You assess the level of students' proficiency based on phrase lists that the student is currently working on.""",
            },
            {
                "role": "user",
                "content": f"""Below is a set of {working_on} phrases in CSV format.
The first items is the phrase that the student is working on.  The second is a score which indicates how well the student knows the phrase. 
A higher score indicates more proficiency.  The student hasn't been tested yet if the word is missing a score.
Estimate the student's {working_on} CEFR level based on these data and limit the response to 2 sentences.
The first sentence provides the estimated level and should mention the language being evaluated.
The second sentence provides justification for this score.
The response should be expressed in the second person, as if you are speaking directly to the student.
\n\n{tuple_list_to_csv(word_list)}""",
            },
        ],
    )
    return completion.choices[0].message.content

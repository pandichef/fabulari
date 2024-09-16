from ..assess_cefr_level import assess_cefr_level

# from .patch_openai_api import set_openai_completion
from ..assess_cefr_level import assess_cefr_level
from .patch_openai_api import set_openai_completion


@set_openai_completion(
    {
        "assess_cefr_level": "Your estimated CEFR level is A2 for Spanish. You know some basic phrases but need more practice."
    }
)
def test_assess_cefr_level_a2():
    word_list = [("casa", 0.80), ("perro", None), ("hijo", 0.5)]
    language = "Spanish"
    model = "gpt-4o-mini"

    result = assess_cefr_level(word_list, language, model)

    assert (
        result
        == "Your estimated CEFR level is A2 for Spanish. You know some basic phrases but need more practice."
    )


# @set_openai_completion(
#     {
#         "assess_cefr_level": "Your estimated CEFR level is C1 for Spanish. You have a good command of complex phrases."
#     }
# )
# def test_assess_cefr_level_c1():
#     word_list = [("casa", 0.80), ("perro", None), ("hijo", 0.5)]
#     language = "Spanish"
#     model = "gpt-4o-mini"

#     result = assess_cefr_level(word_list, language, model)

#     assert (
#         result
#         == "Your estimated CEFR level is C1 for Spanish. You have a good command of complex phrases."
#     )

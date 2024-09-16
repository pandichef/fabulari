import pytest
from unittest.mock import patch
from ..assess_cefr_level import assess_cefr_level
import requests
from types import SimpleNamespace

# Assume the assess_cefr_level function is imported from the correct module

mock_response = SimpleNamespace(
    choices=[
        SimpleNamespace(
            message=SimpleNamespace(
                content="Your CEFR level is B1 for Spanish.\nYou know some phrases well but find new words challenging, placing you at an intermediate level."
            )
        )
    ]
)


def test_assess_cefr_level():
    word_list = [("casa", 0.80), ("perro", None), ("hijo", 0.5)]
    language = "Spanish"
    model = "gpt-4o-mini"

    with patch(
        "purepython.practice_translation.client.chat.completions.create",
        return_value=mock_response,
    ):
        # mocked_get.return_value = "mocked return value"

        # result = requests.get("https://www.nytimes.com")
        result = assess_cefr_level(word_list, language, model)
        assert result == mock_response.choices[0].message.content
        # assert result == "mocked return value"

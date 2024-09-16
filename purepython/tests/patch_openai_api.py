from unittest.mock import patch
from types import SimpleNamespace


# def set_openai_completion(
#     content,
#     the_thing_to_patch="purepython.practice_translation.client.chat.completions.create",
# ):
#     def decorator(func):
#         def wrapper(*args, **kwargs):
#             # Set up the mock response
#             mock_response = SimpleNamespace(
#                 choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
#             )

#             # Patch the OpenAI API call
#             with patch(the_thing_to_patch, return_value=mock_response,) as mock_create:
#                 # Call the actual test function with the mock in place
#                 return func(*args, **kwargs)

#         return wrapper

#     return decorator


# import pytest
# from unittest.mock import patch
# from types import SimpleNamespace


# @pytest.fixture
# def assess_cefr_level_fixture(request):
#     # Get the custom content passed to the fixture or use a default value
#     content = request.param
#     # (
#     #     request.param
#     #     if hasattr(request, "param")
#     #     else "Your estimated CEFR level is B1 for Spanish. This is because you know most basic phrases, but some words are still challenging."
#     # )

#     # Mock the response using SimpleNamespace
#     mock_response = SimpleNamespace(
#         choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
#     )

#     # Patch the OpenAI API call
#     with patch(
#         "purepython.practice_translation.client.chat.completions.create",
#         return_value=mock_response,
#     ) as mock_create:
#         yield mock_create

from unittest.mock import patch
from types import SimpleNamespace
import inspect


def set_openai_completion(
    mock_map,
    the_thing_to_patch="purepython.practice_translation.client.chat.completions.create",
):
    """
    Decorator to mock the OpenAI API calls for different functions with different responses.

    :param mock_map: A dictionary where the keys are function names and the values are the mock content to return.
    """

    def decorator(test_func):
        def wrapper(*args, **kwargs):
            # Define the side effect function
            def side_effect(*args, **kwargs):
                # Use inspect to get the calling function's name
                stack = inspect.stack()
                for frame_info in stack:
                    caller_name = frame_info.function
                    if caller_name in mock_map:
                        content = mock_map[caller_name]
                        return SimpleNamespace(
                            choices=[
                                SimpleNamespace(
                                    message=SimpleNamespace(content=content)
                                )
                            ]
                        )
                # If not found, return empty choices
                return SimpleNamespace(choices=[])

            # Patch the OpenAI API call
            with patch(
                the_thing_to_patch, side_effect=side_effect,
            ):
                return test_func(*args, **kwargs)

        return wrapper

    return decorator

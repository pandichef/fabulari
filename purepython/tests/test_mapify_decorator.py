from typing import List, Any, Dict
from ..parallel_map import threadpool_map, mapify


def mock_api(*args: Any, **kwargs: Any) -> Dict[str, Any]:
    return {"return_field_1": 1, "return_field_2": 2}


input_dict = {"input_field_1": "a", "input_field_2": "b"}


def get_data_from_api(
    input_dict: Dict[str, Any], *args: Any, **kwargs: Any
) -> Dict[str, Any]:
    return_data = mock_api(*args, **kwargs)
    input_dict.update(return_data)
    return input_dict


# from .parallel_map import mapify


# @mapify
# def get_data_from_api_decorated(
#     input_dict: Dict[str, Any], *args: Any, **kwargs: Any
# ) -> Dict[str, Any]:
#     return_data = mock_api(*args, **kwargs)
#     input_dict.update(return_data)
#     return input_dict


get_data_from_api_decorated = mapify(get_data_from_api)


def test_mapify_without_decorator():
    data_for_bulk_create = get_data_from_api(input_dict)
    assert data_for_bulk_create == {
        "return_field_1": 1,
        "return_field_2": 2,
        "input_field_1": "a",
        "input_field_2": "b",
    }


from collections.abc import Iterator


def test_mapify_with_decoratorּ_one_item():
    # Using list() to iterate through the result of map and take the first result
    data_for_bulk_create_iterator = get_data_from_api_decorated([input_dict], (), {})
    assert isinstance(data_for_bulk_create_iterator, Iterator)
    data_for_bulk_create = list(data_for_bulk_create_iterator)[0]
    # data_for_bulk_create = list(get_data_from_api_decorated([input_dict]))[0]  # type: ignore
    assert data_for_bulk_create == {
        "return_field_1": 1,
        "return_field_2": 2,
        "input_field_1": "a",
        "input_field_2": "b",
    }


def test_mapify_with_decorator_two_items():
    # Using list() to iterate through the result of map and take the first result
    data_for_bulk_create_iterator = get_data_from_api_decorated(
        [input_dict, input_dict], (), {}
    )
    assert isinstance(data_for_bulk_create_iterator, Iterator)
    data_for_bulk_create = list(data_for_bulk_create_iterator)
    # data_for_bulk_create = list(get_data_from_api_decorated([input_dict]))[0]  # type: ignore
    assert data_for_bulk_create[0] == {
        "return_field_1": 1,
        "return_field_2": 2,
        "input_field_1": "a",
        "input_field_2": "b",
    }
    assert data_for_bulk_create[1] == {
        "return_field_1": 1,
        "return_field_2": 2,
        "input_field_1": "a",
        "input_field_2": "b",
    }
    assert len(data_for_bulk_create) == 2

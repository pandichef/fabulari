# import asyncio

# from typing import Callable, Iterable, Iterator, Any
import functools
from typing import Callable, Iterable, Iterator, TypeVar, Any, List, Dict
from concurrent.futures import ThreadPoolExecutor

R = TypeVar("R")  # Return type from the function


def threadpool_map(function: Callable[..., R], *iterables: Iterable) -> Iterator[R]:
    with ThreadPoolExecutor() as executor:
        return executor.map(function, *iterables)


T = Callable[[Dict[str, Any], Any, Any], Dict[str, Any]]


def mapify(
    func: T,
) -> Callable[[List[Dict[str, Any]], Any, Any], Iterator[Dict[str, Any]]]:
    @functools.wraps(func)
    def wrapper(
        dicts_list: List[Dict[str, Any]], *args: Any, **kwargs: Any
    ) -> Iterator[Dict[str, Any]]:
        # If there's only one dictionary, run the function directly without creating threads
        if len(dicts_list) == 1:
            # print(1)
            # Directly yield the result as an iterator
            yield func(dicts_list[0], *args, **kwargs)
        else:
            # print(">1")
            # Use ThreadPoolExecutor to run the function concurrently
            with ThreadPoolExecutor() as executor:
                # Use map, passing dicts_list as first argument and *args, **kwargs to each function call
                result_iterator = executor.map(
                    lambda d: func(d, *args, **kwargs), dicts_list
                )
                # Yield results from the ThreadPoolExecutor
                yield from result_iterator

    return wrapper

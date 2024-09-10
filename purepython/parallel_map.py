import asyncio

# from typing import Callable, Iterable, Iterator, Any
from typing import Callable, Iterable, Iterator, TypeVar, Any
from concurrent.futures import ThreadPoolExecutor

R = TypeVar("R")  # Return type from the function


def threadpool_map(function: Callable[..., R], *iterables: Iterable) -> Iterator[R]:
    with ThreadPoolExecutor() as executor:
        return executor.map(function, *iterables)

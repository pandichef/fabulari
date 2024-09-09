from typing import Callable, Iterable, Iterator, TypeVar
from concurrent.futures import ThreadPoolExecutor

R = TypeVar("R")  # Return type from the function


def parallel_map(function: Callable[..., R], *iterables: Iterable) -> Iterator[R]:
    with ThreadPoolExecutor() as executor:
        return executor.map(function, *iterables)


# parallel_map = map

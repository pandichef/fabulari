from .parallel_map import threadpool_map

# Test cases for the parallel_map function
def test_parallel_map_addition():
    def add(x: int, y: int) -> int:
        return x + y

    numbers1 = [1, 2, 3]
    numbers2 = [4, 5, 6]
    results = threadpool_map(add, numbers1, numbers2)
    assert list(results) == [5, 7, 9]


def test_parallel_map_single_iterable():
    def square(x: int) -> int:
        return x * x

    numbers = [1, 2, 3, 4]
    results = threadpool_map(square, numbers)
    assert list(results) == [1, 4, 9, 16]


def test_parallel_map_different_lengths():
    def multiply(x: int, y: int) -> int:
        return x * y

    numbers1 = [1, 2, 3]
    numbers2 = [4, 5]
    results = threadpool_map(multiply, numbers1, numbers2)
    assert list(results) == [4, 10]  # Stops when the shortest iterable is exhausted


def test_parallel_map_no_iterables():
    def func():
        return "no-op"

    try:
        results = threadpool_map(func)  # No iterable provided
    except TypeError:
        print("test_parallel_map_no_iterables: PASSED")


def test_parallel_map_mixed_types():
    def stringify(x) -> str:
        return str(x)

    inputs = [1, 2.5, True, None, "text"]
    results = threadpool_map(stringify, inputs)
    assert list(results) == ["1", "2.5", "True", "None", "text"]


def test_parallel_map_different_lengths_builtin():
    def add(x: int, y: int) -> int:
        return x + y

    numbers1 = [1, 2, 3]
    numbers2 = [4, 5]  # Different length

    results = threadpool_map(add, numbers1, numbers2)  # Should not raise an error
    assert list(results) == [5, 7]  # Stops when the shortest iterable is exhausted


def test_parallel_map_mixed_return_types():
    def mixed_return(x):
        if x % 2 == 0:
            return x
        else:
            return str(x)

    inputs = [1, 2, 3, 4]
    results = threadpool_map(mixed_return, inputs)
    assert list(results) == ["1", 2, "3", 4]


def test_parallel_map_non_iterable():
    def square(x: int) -> int:
        return x * x

    try:
        threadpool_map(square, 123)  # Non-iterable input
        assert False, "Expected TypeError for non-iterable input"
    except TypeError:
        print("test_parallel_map_non_iterable: PASSED")


def test_parallel_map_three_iterables():
    def add_three(x, y, z):
        return x + y + z

    iter1 = [1, 2, 3]
    iter2 = [4, 5, 6]
    iter3 = [7, 8, 9]
    results = threadpool_map(add_three, iter1, iter2, iter3)
    assert list(results) == [12, 15, 18]


def test_parallel_map_side_effects():
    results = []

    def append_result(x):
        results.append(x * x)
        return x * x

    inputs = [1, 2, 3, 4]
    list(
        threadpool_map(append_result, inputs)
    )  # Convert the map object to a list to trigger evaluation

    assert results == [1, 4, 9, 16]


def test_parallel_map_string_concatenation():
    def concat(a: str, b: str) -> str:
        return a + b

    strings1 = ["a", "b", "c"]
    strings2 = ["1", "2", "3"]
    results = threadpool_map(concat, strings1, strings2)
    assert list(results) == ["a1", "b2", "c3"]


# def test_parallel_map_large_input():
#     # super slow!!!!
#     def increment(x: int) -> int:
#         return x + 1

#     large_list = list(range(10 ** 6))  # 1 million elements
#     results = threadpool_map(increment, large_list)
#     assert list(results) == list(range(1, 10 ** 6 + 1))

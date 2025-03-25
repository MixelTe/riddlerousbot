from typing import Callable, TypeVar

T = TypeVar("T")


def find(els: list[T], comparer: Callable[[T], bool]):
    for el in els:
        if comparer(el):
            return el
    return None

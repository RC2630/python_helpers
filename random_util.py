from random import randint
from collections.abc import MutableSequence

def random_element[T](seq: MutableSequence[T], remove: bool = False) -> T:
    if len(seq) == 0:
        raise ValueError("random_element() cannot be used on an empty sequence")
    random_index: int = randint(0, len(seq) - 1)
    element: T = seq[random_index]
    if remove:
        del seq[random_index]
    return element
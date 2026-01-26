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

def random_elements[T](seq: MutableSequence[T], count: int, remove: bool = False) -> list[T]:
    if len(seq) < count:
        raise ValueError("random_elements() cannot be used if length of sequence < count")
    random_indices: list[int] = []
    while len(random_indices) < count:
        random_index: int = randint(0, len(seq) - 1)
        if random_index not in random_indices:
            random_indices.append(random_index)
    elements: list[T] = [seq[random_index] for random_index in random_indices]
    if remove:
        random_indices.sort(reverse = True)
        for random_index in random_indices:
            del seq[random_index]
    return elements
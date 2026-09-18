from random import randint
from typing import Literal, Any
from collections.abc import Container, MutableSequence, Sequence, Collection
from helpers.misc_util import is_hashable

class EmptySequenceError(Exception): pass
class NotEnoughElementsError(Exception): pass
class RemoveNotPermittedError(Exception): pass

def verify[T](
    seq: Sequence[T],
    count: int = 1,
    remove: bool = False,
    exclude: Container[T] = (),
    mode: Literal["default", "distinct_indices", "unique_elements"] = "default"
) -> None:
    if count < 0:
        raise ValueError("count should not be negative")
    if mode not in ["default", "distinct_indices", "unique_elements"]:
        raise ValueError("unrecognized mode; check the type annotation")
    if remove and not isinstance(seq, MutableSequence):
        raise RemoveNotPermittedError("cannot remove elements from immutable sequence")
    seq_with_exclusion: list[T] = [e for e in seq if e not in exclude]
    if len(seq_with_exclusion) == 0 and count > 0:
        raise EmptySequenceError("cannot sample from an empty sequence (after exclusion)")
    if mode == "distinct_indices" and len(seq_with_exclusion) < count:
        raise NotEnoughElementsError("not enough distinct eligible indices (after exclusion)")
    if mode == "unique_elements":
        deduplicated: Collection[T] = (
            set(seq_with_exclusion)
            if is_hashable(tuple(seq_with_exclusion))
            else [e for i, e in enumerate(seq_with_exclusion) if e not in seq_with_exclusion[:i]]
        )
        if len(deduplicated) < count:
            raise NotEnoughElementsError("not enough unique eligible elements (after exclusion)")

def sample_from_sequence[T](
    seq: Sequence[T],
    count: int = 1,
    remove: bool = False,
    exclude: Container[T] = (),
    mode: Literal["default", "distinct_indices", "unique_elements"] = "default"
) -> list[T]:
    verify(seq, count, remove, exclude, mode)
    random_indices: set[int] = set()
    random_elements: set[T] | list[T] = set() if is_hashable(tuple(seq)) else []
    final_result: list[T] = []
    while len(final_result) < count:
        random_index: int = randint(0, len(seq) - 1)
        if (
            seq[random_index] not in exclude and ((
                mode == "default"
            ) or (
                mode == "distinct_indices" and random_index not in random_indices
            ) or (
                mode == "unique_elements" and seq[random_index] not in random_elements
            ))
        ):
            random_indices.add(random_index)
            final_result.append(seq[random_index])
            if mode == "unique_elements":
                append_func: Any = set.add if isinstance(random_elements, set) else list.append
                append_func(random_elements, seq[random_index])
    if remove:
        for random_index in sorted(random_indices, reverse = True):
            del seq[random_index]
    return final_result
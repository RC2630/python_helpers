from random import randint
from typing import Literal
from collections.abc import Container, MutableSequence, Sequence, Collection
from helpers.misc_util import is_hashable

class EmptySequenceError(Exception): pass
class NotEnoughElementsError(Exception): pass
class RemoveNotPermittedError(Exception): pass

# -----------------------------------------------------------

def validate_args[T](
    seq_with_exclusion: list[tuple[int, T]],
    count: int,
    remove: bool,
    mode: Literal["with_replacement", "distinct_indices", "unique_elements"],
    seq_is_mutable: bool
) -> None:
    
    if count < 0:
        raise ValueError("count should not be negative")
    if mode not in ["with_replacement", "distinct_indices", "unique_elements"]:
        raise ValueError("unrecognized mode; check the type annotation")
    if remove and not seq_is_mutable:
        raise RemoveNotPermittedError("cannot remove elements from immutable sequence")

    if len(seq_with_exclusion) == 0 and count > 0:
        raise EmptySequenceError("cannot sample from an empty sequence (after exclusion)")
    if mode == "distinct_indices" and len(seq_with_exclusion) < count:
        raise NotEnoughElementsError("not enough distinct eligible indices (after exclusion)")
    
    if mode == "unique_elements":
        seq_with_exclusion_values: list[T] = [e for i, e in seq_with_exclusion]
        deduplicated: Collection[T] = (
            set(seq_with_exclusion_values)
            if is_hashable(tuple(seq_with_exclusion_values))
            else [
                e for i, e in enumerate(seq_with_exclusion_values)
                if e not in seq_with_exclusion_values[:i]
            ]
        )
        if len(deduplicated) < count:
            raise NotEnoughElementsError("not enough unique eligible elements (after exclusion)")

# -----------------------------------------------------------

def sample_from_sequence[T](
    seq: Sequence[T],
    count: int = 1,
    remove: bool = False,
    exclude: Container[T] = (),
    mode: Literal["with_replacement", "distinct_indices", "unique_elements"] = "with_replacement",
    validate: bool = True
) -> list[T]:

    seq_with_exclusion: list[tuple[int, T]] = [
        (i, e) for i, e in enumerate(seq) if e not in exclude
    ]
    
    if validate:
        validate_args(seq_with_exclusion, count, remove, mode, isinstance(seq, MutableSequence))

    random_indices: set[int] = set()
    eligible_indices: list[int] = list(range(len(seq_with_exclusion)))
    final_result: list[T] = []

    while len(final_result) < count:
        random_pos: int = randint(0, len(eligible_indices) - 1)
        random_index: int = eligible_indices[random_pos]
        element: T = seq_with_exclusion[random_index][1]
        random_indices.add(random_index)
        final_result.append(element)
        if mode == "distinct_indices":
            eligible_indices[random_pos] = eligible_indices[-1]
            eligible_indices.pop()
        elif mode == "unique_elements":
            eligible_indices = [
                index for index in eligible_indices
                if seq_with_exclusion[index][1] != element
            ]

    if remove:
        assert isinstance(seq, MutableSequence)
        indices_to_delete: set[int] = {seq_with_exclusion[index][0] for index in random_indices}
        temp_seq: list[T] = []
        for i, element in enumerate(seq):
            if i not in indices_to_delete:
                temp_seq.append(element)
        seq.clear()
        seq.extend(temp_seq)
            
    return final_result
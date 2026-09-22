from typing import Any
from collections.abc import Sequence

def is_hashable(obj: Any) -> bool:
    try:
        hash(obj)
        return True
    except TypeError:
        return False

def is_hashable_seq[T](seq: Sequence[T], coarse: bool = False) -> bool:
    return is_hashable(
        seq[0]
        if coarse and len(seq) > 0
        else tuple(seq)
    )
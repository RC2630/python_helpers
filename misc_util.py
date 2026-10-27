from typing import Any, Callable
from collections.abc import Sequence
from itertools import groupby

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

def ordinal_number(n: int) -> str:
    s: str = str(n)
    if s.endswith(("11", "12", "13")):
        return s + "th"
    elif s.endswith("1"):
        return s + "st"
    elif s.endswith("2"):
        return s + "nd"
    elif s.endswith("3"):
        return s + "rd"
    else:
        return s + "th"
    
def multiplicative_number(n: int) -> str:
    if n == 1:
        return "once"
    elif n == 2:
        return "twice"
    elif n == 3:
        return "thrice"
    else:
        return f"{n} times"

def get_runs[T](l: list[T]) -> list[tuple[T, int]]:
    return [(value, len(list(group))) for value, group in groupby(l)]

def mark_requirements[**P, R](*requirements: str) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def decorator(f: Callable[P, R]) -> Callable[P, R]:
        requirements_docstring: str = f"REQUIRES: {', '.join(requirements)}"
        if f.__doc__ is None:
            f.__doc__ = requirements_docstring
        else:
            f.__doc__ += f"\n{requirements_docstring}"
        return f
    return decorator
from typing import Any, Callable, Never, TypeForm
from collections.abc import Sequence, Iterable
from itertools import groupby
from collections import defaultdict

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

def find_witness_if_any[T, W, S](
    iterable: Iterable[T],
    predicate: Callable[[T], bool],
    witness: Callable[[T], W] = lambda element: element,
    sentinel: S = None
) -> W | S:
    w: W | S = sentinel
    if any(
        predicate(element) and (w := witness(element)) is w
        for element in iterable
    ):
        return w
    else:
        return sentinel

type NestedDict[K, V] = dict[K, V | NestedDict[K, V]]
type StrictNestedDict[K] = NestedDict[K, Never]
type AnyNestedDict[K] = NestedDict[K, Any]

def make_nested_defaultdict[K, L](
    key_type: TypeForm[K] = Any,
    leaf_type: TypeForm[L] = Any
) -> NestedDict[K, L]:
    return defaultdict(make_nested_defaultdict)
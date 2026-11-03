from typing import cast, Any, Callable, Self
from collections.abc import Sequence
from collections import deque

type ConversionFunction = Callable[[Any], Representation]

CONVERSIONS: dict[
    type[Representation],
    Callable[[], dict[type[Representation], ConversionFunction]]
] = {}

# ----------------------------------------------

def register_conversions[T: Representation](
    conversions: Callable[[], dict[type[Representation], ConversionFunction]]
) -> Callable[[type[T]], type[T]]:
    def decorator(repr_type: type[T]) -> type[T]:
        CONVERSIONS[repr_type] = conversions
        return repr_type
    return decorator

# ----------------------------------------------

class Representation:

    @classmethod
    def generate(cls, max: int) -> Sequence[Self]:
        return []

    def find_path(self, destination: type[Representation]) -> list[type[Representation]]:
        frontier: deque[list[type[Representation]]] = deque([[type(self)]])
        visited: set[type[Representation]] = {type(self)}
        while len(frontier) > 0:
            curr_path: list[type[Representation]] = frontier.popleft()
            curr_type: type[Representation] = curr_path[-1]
            if curr_type is destination:
                return curr_path[1:]
            for neighbour_type in CONVERSIONS[curr_type]():
                if neighbour_type not in visited:
                    visited.add(neighbour_type)
                    frontier.append(curr_path + [neighbour_type])
        raise ValueError(f"no path connects {type(self).__name__} to {destination.__name__}")

    def to[T: Representation](self, repr_type: type[T]) -> T:
        curr: Representation = self
        for neighbour_type in self.find_path(repr_type):
            conversion_func: ConversionFunction = CONVERSIONS[type(curr)]()[neighbour_type]
            curr = conversion_func(curr)
        return cast(T, curr)

    def display(self) -> None:
        print()
        for repr_type in CONVERSIONS:
            print(f"{repr_type.__name__}: {self.to(repr_type)}")

    def test(self) -> None:
        for repr_type in CONVERSIONS:
            assert self.to(repr_type).to(type(self)) == self

    @staticmethod
    def generate_all(max: int) -> list[Representation]:
        representations: list[Representation] = []
        for repr_type in CONVERSIONS:
            representations.extend(repr_type.generate(max))
        return representations
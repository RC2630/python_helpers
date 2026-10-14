from collections.abc import Iterator

class Incrementer:

    def __init__(self, start: int = 0) -> None:
        self.curr: int = start

    def __call__(self) -> int:
        self.curr += 1
        return self.curr - 1

    def __iter__(self) -> Iterator[int]:
        while True:
            yield self()
from collections.abc import Iterator

class NullReferenceError(Exception): pass
NULL = sentinel("NULL")

class Reference[T]:

    def __init__(self, value: T | NULL = NULL) -> None:
        self.value: T | NULL = value

    def __call__(self) -> T:
        if self.value is NULL:
            raise NullReferenceError
        return self.value

    def is_null_reference(self) -> bool:
        return self.value is NULL

    def is_not_null_reference(self) -> bool:
        return self.value is not NULL

    def set_value(self, value: T) -> None:
        self.value = value

    def set_to_null_reference(self) -> None:
        self.value = NULL
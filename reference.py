class Reference[T]:

    def __init__(self, value: T) -> None:
        self.value: T = value

    def __call__(self) -> T:
        return self.value
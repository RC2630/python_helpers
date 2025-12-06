from typing import Any, Callable, overload, Final
from functools import wraps

class Pipable[T]:

    '''
    DOT PIPE STYLE
    --------------
    Pipable(1).func().value
        = func(1)
    Pipable(1).func(2).value
        = func(1, 2)
    Pipable(1).func(2, 3, 4).value
        = func(1, 2, 3, 4)
    Pipable(1).func(a = 5, b = 6).value
        = func(1, a = 5, b = 6)
    Pipable(1).func(2, a = 5, b = 6).value
        = func(1, 2, a = 5, b = 6)
    Pipable(1).func(2, 3, 4, a = 5, b = 6).value
        = func(1, 2, 3, 4, a = 5, b = 6)
    Pipable(1).func(2, ..., 3).value
        = func(2, 1, 3)
    Pipable(1).func(a = ..., b = 6).value
        = func(a = 1, b = 6)
    Pipable(1).func(2, a = ..., b = 6).value
        = func(2, a = 1, b = 6)
    Pipable(1).func(2, ..., 3, a = ..., b = 6).value
        = func(2, 1, 3, a = 1, b = 6)

    SHIFT PIPE STYLE
    ----------------
    Pipable(1) >> func >> Pipable.VALUE
        = func(1)
    Pipable(1) >> (func, 2) >> Pipable.VALUE
        = func(1, 2)
    Pipable(1) >> (func, (2, 3, 4)) >> Pipable.VALUE
        = func(1, 2, 3, 4)
    Pipable(1) >> (func, dict(a = 5, b = 6)) >> Pipable.VALUE
        = func(1, a = 5, b = 6)
    Pipable(1) >> (func, 2, dict(a = 5, b = 6)) >> Pipable.VALUE
        = func(1, 2, a = 5, b = 6)
    Pipable(1) >> (func, (2, 3, 4), dict(a = 5, b = 6)) >> Pipable.VALUE
        = func(1, 2, 3, 4, a = 5, b = 6)
    Pipable(1) >> (func, (2, ..., 3)) >> Pipable.VALUE
        = func(2, 1, 3)
    Pipable(1) >> (func, dict(a = ..., b = 6)) >> Pipable.VALUE
        = func(a = 1, b = 6)
    Pipable(1) >> (func, 2, dict(a = ..., b = 6)) >> Pipable.VALUE
        = func(2, a = 1, b = 6)
    Pipable(1) >> (func, (2, ..., 3), dict(a = ..., b = 6)) >> Pipable.VALUE
        = func(2, 1, 3, a = 1, b = 6)
    '''

    class ValueGetter:
        pass

    VALUE: Final[ValueGetter] = ValueGetter()
    BUILT_IN_CALLABLES: Final[dict[str, Callable]] = {
        name: getattr(__import__('builtins'), name)
        for name in dir(__import__('builtins'))
        if callable(getattr(__import__('builtins'), name))
    }
    ALL_AVAILABLE_CALLABLES: dict[str, Callable] = BUILT_IN_CALLABLES.copy()
    GET_AVAILABLE_CALLABLES: Final[str] = \
        "{key: value for key, value in (globals() | locals()).items() if callable(value)}"

    @classmethod
    def set_available_callables(cls, available_callables: dict[str, Callable]) -> None:
        cls.ALL_AVAILABLE_CALLABLES = cls.BUILT_IN_CALLABLES | available_callables

    def __init__(self, value: T, lookup_free_before_attr: bool = False) -> None:
        self.value: T = value
        self.lookup_free_before_attr: bool = lookup_free_before_attr
    
    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return repr(self.value)
    
    def replace_tuple(self, t: tuple[Any, ...]) -> tuple[tuple[Any, ...], bool]:
        l: list[Any] = list(t)
        replaced: bool = False
        for i in range(len(l)):
            if l[i] is ...:
                l[i] = self.value
                replaced = True
        return (tuple(l), replaced)
    
    def replace_dict(self, d: dict[str, Any]) -> tuple[dict[str, Any], bool]:
        replaced: bool = False
        d = d.copy()
        for key in d:
            if d[key] is ...:
                d[key] = self.value
                replaced = True
        return (d, replaced)
    
    def replace_tuple_dict(
        self, t: tuple[Any, ...], d: dict[str, Any]
    ) -> tuple[tuple[Any, ...], dict[str, Any], bool]:
        new_t, is_t_replaced = self.replace_tuple(t)
        new_d, is_d_replaced = self.replace_dict(d)
        return (new_t, new_d, is_t_replaced or is_d_replaced)
    
    def set_lookup_free_before_attr(self, lookup_free_before_attr: bool) -> Pipable[T]:
        self.lookup_free_before_attr = lookup_free_before_attr
        return self
    
    def __call__(self, *args: Any, **kwargs: Any) -> Pipable[Any]:
        assert callable(self.value)
        return Pipable(self.value(*args, **kwargs), self.lookup_free_before_attr)
    
    def __getattr__(self, attr: str) -> Pipable[Any]:

        if not self.lookup_free_before_attr and hasattr(self.value, attr):
            return Pipable(getattr(self.value, attr), self.lookup_free_before_attr)
        
        if attr in Pipable.ALL_AVAILABLE_CALLABLES:
            func: Callable[..., Any] = Pipable.ALL_AVAILABLE_CALLABLES[attr]
            @wraps(func)
            def fake_method(*args: Any, **kwargs: Any) -> Any:
                new_args, new_kwargs, is_replaced = self.replace_tuple_dict(args, kwargs)
                return func(*new_args, **new_kwargs) if is_replaced \
                       else func(self.value, *new_args, **new_kwargs)
            return Pipable(fake_method, self.lookup_free_before_attr)
        
        if self.lookup_free_before_attr and hasattr(self.value, attr):
            return Pipable(getattr(self.value, attr), self.lookup_free_before_attr)

        raise AttributeError

    # func() has >= 3 arguments & func() has **kwargs
    @overload
    def __rshift__[R](
        self, func_and_args: tuple[Callable[..., R], tuple[Any, ...], dict[str, Any]]
    ) -> Pipable[R]: ...

    # func() has 2 arguments & func() has **kwargs
    @overload
    def __rshift__[R](
        self, func_and_args: tuple[Callable[..., R], Any, dict[str, Any]]
    ) -> Pipable[R]: ...

    # func() has 1 argument & func() has **kwargs
    @overload
    def __rshift__[R](
        self, func_and_args: tuple[Callable[..., R], dict[str, Any]]
    ) -> Pipable[R]: ...

    # func() has >= 3 arguments
    @overload
    def __rshift__[R](
        self, func_and_args: tuple[Callable[..., R], tuple[Any, ...]]
    ) -> Pipable[R]: ...

    # func() has 2 arguments
    @overload
    def __rshift__[S, R](self, func_and_args: tuple[Callable[[T, S], R], S]) -> Pipable[R]: ...

    # func() has 1 argument
    @overload
    def __rshift__[R](self, func_and_args: Callable[[T], R]) -> Pipable[R]: ...

    # piping just to get the final value
    @overload
    def __rshift__(self, func_and_args: Pipable.ValueGetter) -> T: ...

    def __rshift__(
        self, func_and_args:
            tuple[Callable, tuple[Any, ...], dict[str, Any]] |
            tuple[Callable, Any, dict[str, Any]] |
            tuple[Callable, dict[str, Any]] |
            tuple[Callable, tuple[Any, ...]] |
            tuple[Callable, Any] |
            Callable |
            Pipable.ValueGetter
    ) -> Pipable[Any] | T:

        f: Any = func_and_args
        
        # piping just to get the final value
        if f is Pipable.VALUE:
            return self.value

        # func() has 1 argument
        elif callable(f):
            return Pipable(f(self.value))
        
        # func() has 2 arguments
        elif isinstance(f, tuple) and len(f) == 2 and not isinstance(f[1], tuple | dict):
            return Pipable(f[0](self.value, f[1]))
        
        # func() has >= 3 arguments
        elif isinstance(f, tuple) and len(f) == 2 and isinstance(f[1], tuple):
            new_tuple, is_replaced = self.replace_tuple(f[1])
            return Pipable(f[0](*new_tuple)) if is_replaced \
                   else Pipable(f[0](self.value, *new_tuple))
        
        # func() has 1 argument & func() has **kwargs
        elif isinstance(f, tuple) and len(f) == 2 and isinstance(f[1], dict):
            new_dict, is_replaced = self.replace_dict(f[1])
            return Pipable(f[0](**new_dict)) if is_replaced \
                   else Pipable(f[0](self.value, **new_dict))
        
        # func() has 2 arguments & func() has **kwargs
        elif isinstance(f, tuple) and len(f) == 3 and not isinstance(f[1], tuple):
            new_dict, is_replaced = self.replace_dict(f[2])
            return Pipable(f[0](f[1], **new_dict)) if is_replaced \
                   else Pipable(f[0](self.value, f[1], **new_dict))
        
        # func() has >= 3 arguments & func() has **kwargs
        elif isinstance(f, tuple) and len(f) == 3 and isinstance(f[1], tuple):
            new_tuple, new_dict, is_replaced = self.replace_tuple_dict(f[1], f[2])
            return Pipable(f[0](*new_tuple, **new_dict)) if is_replaced \
                   else Pipable(f[0](self.value, *new_tuple, **new_dict))
            
        raise RuntimeError("code should never reach here")
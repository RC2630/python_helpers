from functools import wraps
from typing import Callable, Concatenate, Any, NamedTuple, cast
from helpers.reference import Reference

type ResultRef[R] = Reference[FunctionCallRecord[R]]

class FunctionCallRecord[R](NamedTuple):
    args: tuple[Any, ...]
    kwargs: dict[str, Any]
    result: R

def init_ref[T](result_type: type[T] = cast(type[Any], Any)) -> ResultRef[T]:
    return Reference()

def change_to_output_param[**P, R](
    func: Callable[P, R]
) -> Callable[Concatenate[ResultRef[R], P], None]:
    @wraps(func)
    def inner(result: ResultRef[R], *args: P.args, **kwargs: P.kwargs) -> None:
        result.set_value(FunctionCallRecord(args, kwargs, func(*args, **kwargs)))
    return inner

def change_to_no_return[**P, R](
    result_ref: ResultRef[R]
) -> Callable[[Callable[P, R]], Callable[P, None]]:
    def actual_change_to_no_return(func: Callable[P, R]) -> Callable[P, None]:
        changed_func = change_to_output_param(func)
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> None:
            changed_func(result_ref, *args, **kwargs)
        return wrapper
    return actual_change_to_no_return
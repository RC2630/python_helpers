from typing import TypeForm, Any, get_origin, cast
from types import NoneType

def get_real_type[T](typeform: TypeForm[T]) -> type[T]:
    if typeform is None:
        return NoneType
    typ: Any = cast(Any, typeform)
    while True:
        value_changed: bool = False
        origin_changed: bool = False
        while True:
            try:
                typ = typ.__value__
                value_changed = True
            except AttributeError:
                break
        while True:
            origin: Any = get_origin(typ)
            if origin is not None:
                typ = origin
                origin_changed = True
            else:
                break
        if not value_changed and not origin_changed:
            return typ

def get_type_name(typeform: TypeForm[Any], final_component_only: bool = True) -> str:
    s: str = str(typeform)
    name: str = getattr(typeform, "__name__", s) if s.startswith("<class '") else s
    return name.split(".")[-1] if final_component_only else name
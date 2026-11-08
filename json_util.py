from json import loads, load, dumps, dump
from typing import cast, TypeForm
from types import NoneType
from helpers.typing_util import get_real_type, get_type_name

type JsonPrimitive = int | bool | float | str | None
type JsonArray = list[JsonItem]
type JsonObject = dict[str, JsonItem]
type JsonItem = JsonPrimitive | JsonArray | JsonObject

def strict_loads(json_string: str) -> JsonItem:
    return loads(json_string)

def strict_load(json_file_path: str) -> JsonItem:
    with open(json_file_path, "r") as f:
        return load(f)

def strict_dumps(json_item: JsonItem) -> str:
    return dumps(json_item)

def strict_dump(json_item: JsonItem, json_file_path: str) -> None:
    with open(json_file_path, "w") as f:
        dump(json_item, f)

def as_type[T](json_item: JsonItem, json_type: TypeForm[T]) -> T:
    json_real_type: type[T] = get_real_type(json_type)
    if json_real_type not in (int, float, bool, str, NoneType, dict, list):
        raise ValueError(f"{get_type_name(json_type)} is not a valid JSON type")
    if type(json_item) is not json_real_type:
        raise TypeError(
            f"wrong type: expected {json_real_type.__name__}, "
            f"actual {type(json_item).__name__}"
        )
    return cast(T, json_item)

def array_item(json_item: JsonItem, index: int) -> JsonItem:
    return as_type(json_item, list[JsonItem])[index]

def object_item(json_item: JsonItem, key: str) -> JsonItem:
    return as_type(json_item, dict[str, JsonItem])[key]
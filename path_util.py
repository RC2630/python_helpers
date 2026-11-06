from pathlib import Path
from collections.abc import Collection, Iterable
from datetime import datetime
import re

def get_all_files(
    path: str,
    included_extensions: Collection[str] | None = None,
    excluded_extensions: Collection[str] = (),
    recurse_into_subfolders: bool = True,
    only_modified_after_timestamp: datetime | None = None
) -> list[str]:
    return list(get_all_files_with_relative(
        path, included_extensions, excluded_extensions,
        recurse_into_subfolders, only_modified_after_timestamp
    ).values())

def validate(
    included_extensions: Collection[str] | None,
    excluded_extensions: Collection[str]
) -> None:
    if included_extensions is not None:
        assert len(excluded_extensions) == 0
        assert all(extension.startswith(".") for extension in included_extensions)
    if len(excluded_extensions) > 0:
        assert included_extensions is None
        assert all(extension.startswith(".") for extension in excluded_extensions)

def should_include_file(
    file: Path,
    included_extensions: Collection[str] | None,
    excluded_extensions: Collection[str],
    only_modified_after_timestamp: datetime | None
) -> bool:
    if included_extensions is not None and not any(
        file.name.endswith(extension) for extension in included_extensions
    ):
        return False
    if any(file.name.endswith(extension) for extension in excluded_extensions):
        return False
    if only_modified_after_timestamp is not None:
        return file.stat().st_mtime > only_modified_after_timestamp.timestamp()
    return True

def get_all_files_with_relative(
    path: str,
    included_extensions: Collection[str] | None = None,
    excluded_extensions: Collection[str] = (),
    recurse_into_subfolders: bool = True,
    only_modified_after_timestamp: datetime | None = None
) -> dict[str, str]:
    validate(included_extensions, excluded_extensions)
    if (m := re.match(r"/([a-z])/.*", path.lower())) is not None:
        path = f"{m.group(1).upper()}:/" + path[3:]
    root = Path(path)
    if root.is_file():
        if should_include_file(
            root, included_extensions, excluded_extensions, only_modified_after_timestamp
        ):
            return {root.as_posix().split("/")[-1]: root.as_posix()}
        else:
            return {}
    all_files: Iterable[Path] = root.rglob("*") if recurse_into_subfolders else root.glob("*")
    return {
        file.relative_to(root).as_posix(): file.as_posix()
        for file in all_files if file.is_file()
        if should_include_file(
            file, included_extensions, excluded_extensions, only_modified_after_timestamp
        )
    }
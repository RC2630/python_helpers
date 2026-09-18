from pathlib import Path

def get_all_files(path: str) -> list[str]:
    if path.lower().startswith("/c/"):
        path = "C:/" + path[3:]
    root = Path(path)
    if root.is_file():
        return [root.as_posix()]
    else:
        return [path.as_posix() for path in root.rglob("*") if path.is_file()]

def get_all_files_with_relative(path: str) -> dict[str, str]:
    if path.lower().startswith("/c/"):
        path = "C:/" + path[3:]
    root = Path(path)
    if root.is_file():
        return {root.as_posix().split("/")[-1]: root.as_posix()}
    else:
        return {
            path.relative_to(root).as_posix(): path.as_posix()
            for path in root.rglob("*") if path.is_file()
        }
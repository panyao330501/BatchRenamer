import glob
from pathlib import Path


def load_from_wildcard(pattern: str) -> list[Path]:
    """Expand a glob pattern and return matching file paths."""
    matched = glob.glob(pattern, recursive=True)
    return [Path(p) for p in matched if Path(p).is_file()]


def parse_drop_paths(raw: str, splitlist_fn) -> list[Path]:
    """Parse tkinterdnd2 drop event data into a flat list of file Paths.

    Folders are expanded one level (non-recursive) to include their direct files.
    """
    result: list[Path] = []
    for entry in splitlist_fn(raw):
        path = Path(entry)
        if path.is_file():
            result.append(path)
        elif path.is_dir():
            result.extend(p for p in path.iterdir() if p.is_file())
    return result

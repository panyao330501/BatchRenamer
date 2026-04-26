from pathlib import Path
from .rules import Rule


def compute_new_names(files: list[Path], rules: list[Rule]) -> list[dict]:
    """Apply the rule pipeline to every file and return result records.

    Each record has:
        path      – original Path object
        original  – original filename string
        new_name  – computed new filename (None on error)
        conflict  – True if two files would share the same new name
        error     – error message string, or None
        status    – None | 'ok' | 'locked' | 'error'  (set after execute)
    """
    results: list[dict] = []
    total = len(files)

    for idx, path in enumerate(files):
        stem = path.stem
        ext = path.suffix
        error: str | None = None

        try:
            for rule in rules:
                stem, ext = rule.apply(stem, ext, idx, total)
        except Exception as exc:
            error = str(exc)

        if error is None and not stem:
            error = "Empty filename after rules"

        new_name = (stem + ext) if error is None else None
        results.append({
            "path": path,
            "original": path.name,
            "new_name": new_name,
            "conflict": False,
            "error": error,
            "status": None,
        })

    # Detect conflicts (case-insensitive – Windows FS is case-insensitive)
    seen: dict[str, int] = {}
    for i, r in enumerate(results):
        if r["new_name"] is not None:
            key = r["new_name"].lower()
            if key in seen:
                results[i]["conflict"] = True
                results[seen[key]]["conflict"] = True
            else:
                seen[key] = i

    return results

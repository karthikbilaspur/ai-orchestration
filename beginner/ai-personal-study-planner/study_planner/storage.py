"""Small JSON persistence helpers with atomic writes."""
from __future__ import annotations

import json
import os
from pathlib import Path


class StorageError(RuntimeError):
    """Raised when a JSON file cannot be read or written."""


def save_json(path, data) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    try:
        tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        os.replace(tmp, path)
    except OSError as exc:
        raise StorageError(f"Could not write {path}: {exc}") from exc


def load_json(path, default=None):
    path = Path(path)
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise StorageError(f"Could not read {path}: {exc}") from exc

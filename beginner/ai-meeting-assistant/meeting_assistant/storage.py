"""Small persistence helpers with atomic writes."""
from __future__ import annotations

import json
import os
from pathlib import Path


class StorageError(RuntimeError):
    """Raised when a file cannot be read or written."""


def save_text(path, text: str) -> None:
    path = Path(path)
    tmp = path.with_name(path.name + ".tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp.write_text(text, encoding="utf-8")
        os.replace(tmp, path)
    except OSError as exc:
        raise StorageError(f"Could not write {path}: {exc}") from exc


def save_json(path, data) -> None:
    save_text(path, json.dumps(data, indent=2, ensure_ascii=False))


def read_text(path, max_chars: int | None = None) -> str:
    path = Path(path)
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise StorageError(f"{path} is not valid UTF-8 text.") from exc
    except OSError as exc:
        raise StorageError(f"Could not read {path}: {exc}") from exc
    if max_chars is not None and len(text) > max_chars:
        raise StorageError(f"{path} is too large (limit {max_chars} characters).")
    return text

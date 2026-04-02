"""Cache simples em disco para feeds (opcional)."""

from __future__ import annotations

import time
from pathlib import Path


def cache_get(path: Path, max_age_seconds: int) -> bytes | None:
    if not path.exists():
        return None
    age = time.time() - path.stat().st_mtime
    if age > max_age_seconds:
        return None
    return path.read_bytes()


def cache_put(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)

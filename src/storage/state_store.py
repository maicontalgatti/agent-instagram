"""Persistência de URLs/títulos já postados (JSON)."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from utils.text_utils import normalize_url, title_similarity

logger = logging.getLogger(__name__)


class StateStore:
    def __init__(self, path: Path):
        self.path = path
        self._data: dict[str, Any] = {"entries": []}

    def load(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._data = {"entries": []}
            return
        try:
            raw = self.path.read_text(encoding="utf-8")
            self._data = json.loads(raw) if raw.strip() else {"entries": []}
            if "entries" not in self._data:
                self._data["entries"] = []
        except (json.JSONDecodeError, OSError) as e:
            logger.warning("Estado corrompido, reiniciando: %s", e)
            self._data = {"entries": []}

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self._data, ensure_ascii=False, indent=2), encoding="utf-8")

    def is_posted(self, article: dict) -> bool:
        url = normalize_url(article.get("url") or "")
        title = (article.get("title") or "").strip()
        for e in self._data.get("entries", []):
            if normalize_url(e.get("url", "")) == url:
                return True
            if title and title_similarity(title, e.get("title") or "") >= 0.9:
                return True
        return False

    def record(
        self,
        *,
        url: str,
        title: str,
        score: float,
        source: str,
    ) -> None:
        entry = {
            "url": url,
            "title": title,
            "posted_at": datetime.now(timezone.utc).isoformat(),
            "score": score,
            "source": source,
        }
        self._data.setdefault("entries", []).append(entry)
        self.save()
        logger.info("Registrado no state_store: %s", title[:80])

"""JSON TTL cache for Bilibili API responses.

Bilibili rate-limits scrapers, so caching popular/trending/video lookups is
the polite default (data/ directory, JSON files, TTL from config).
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any

from .config import DATA_DIR, settings

logger = logging.getLogger(__name__)

_CACHE_DIR = DATA_DIR / "cache" / "bilibili"


def _path(key: str) -> Path:
    return _CACHE_DIR / f"{key}.json"


def get(key: str) -> dict | None:
    """Return cached dict if fresh, else None."""
    path = _path(key)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    ts = data.get("_ts", 0)
    if time.time() - ts > settings.cache_ttl:
        return None
    return data.get("data")


def set(key: str, value: Any) -> None:
    try:
        _CACHE_DIR.mkdir(parents=True, exist_ok=True)
        payload = {"_ts": time.time(), "data": value}
        _CACHE_DIR.joinpath(f"{key}.json").write_text(
            json.dumps(payload, ensure_ascii=False), encoding="utf-8"
        )
    except Exception:
        logger.debug("cache write failed for %s", key, exc_info=True)


def cached(key: str) -> dict | None:
    """Read-only probe used by health/diagnostics."""
    return get(key)


def clear() -> int:
    count = 0
    if _CACHE_DIR.exists():
        for f in _CACHE_DIR.glob("*.json"):
            try:
                f.unlink()
                count += 1
            except Exception:
                logger.debug("cache clear failed for %s", f.name, exc_info=True)
    return count

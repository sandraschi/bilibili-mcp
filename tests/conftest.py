"""Shared test fixtures."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

# Ensure a clean, deterministic settings state for tests.
os.environ.setdefault("BILIBILI_COOKIE", "")
os.environ.setdefault("BILIBILI_CACHE_TTL", "1")


@pytest.fixture(autouse=True)
def _clear_cache():
    """Point the cache at a throwaway dir and clear it before each test."""
    from bilibili_mcp import cache

    cache._CACHE_DIR = cache.DATA_DIR / "cache" / "bilibili"
    cache.clear()
    yield
    cache.clear()


SAMPLE_VIDEO = {
    "bvid": "BV1xx411c7mD",
    "aid": 170001,
    "title": "测试视频",
    "desc": "A sample description.",
    "duration": 120,
    "pic": "http://i0.hdslb.com/bfs/archive/x.jpg",
    "pubdate": 1700000000,
    "tname": "知识",
    "owner": {"mid": 1, "name": "测试UP"},
    "stat": {
        "view": 1000,
        "danmaku": 50,
        "reply": 10,
        "favorite": 5,
        "coin": 3,
        "share": 2,
        "like": 99,
    },
    "pages": [{"cid": 9001, "page": 1, "part": "P1"}],
}

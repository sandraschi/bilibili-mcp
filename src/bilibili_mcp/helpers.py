"""Shared helpers for bilibili tool surfaces - video slim dicts and id parsing."""

from __future__ import annotations

import re
from typing import Any

_BVID_RE = re.compile(r"(BV[0-9A-Za-z]{10})")


def parse_bvid(text: str) -> str:
    """Extract a bvid from free text or a bilibili.com/.../BVxxxx URL."""
    if not text:
        return ""
    match = _BVID_RE.search(text)
    return match.group(1) if match else text.strip()


def parse_aid(text: str) -> int:
    """Extract a numeric aid from free text or a bilibili.com/video/avN URL."""
    if not text:
        return 0
    match = re.search(r"(?:av|aid=)(\d+)", text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    digits = re.fullmatch(r"\d+", text.strip())
    return int(digits.group(0)) if digits else 0


def slim_video(v: dict[str, Any]) -> dict[str, Any]:
    """Project a raw Bilibili video dict to a stable, small shape."""
    return {
        "bvid": v.get("bvid", ""),
        "aid": v.get("aid", 0),
        "title": v.get("title", ""),
        "desc": (v.get("desc") or "")[:300],
        "duration": v.get("duration", 0),
        "pic": v.get("pic", ""),
        "play": v.get("play", v.get("stat", {}).get("view", 0)),
        "danmaku": v.get("danmaku", v.get("stat", {}).get("danmaku", 0)),
        "author": v.get("owner", {}).get("name", ""),
        "mid": v.get("owner", {}).get("mid", 0),
        "pubdate": v.get("pubdate", 0),
        "url": f"https://www.bilibili.com/video/{v.get('bvid', '')}",
    }


def format_video(v: dict[str, Any]) -> dict[str, Any]:
    """Rich single-video view (video_info) with stats block."""
    stat = v.get("stat", {}) or {}
    owner = v.get("owner", {}) or {}
    return {
        "bvid": v.get("bvid", ""),
        "aid": v.get("aid", 0),
        "title": v.get("title", ""),
        "desc": v.get("desc", ""),
        "duration": v.get("duration", 0),
        "pic": v.get("pic", ""),
        "pubdate": v.get("pubdate", 0),
        "tname": v.get("tname", ""),
        "url": f"https://www.bilibili.com/video/{v.get('bvid', '')}",
        "owner": {"mid": owner.get("mid", 0), "name": owner.get("name", "")},
        "stats": {
            "view": stat.get("view", 0),
            "danmaku": stat.get("danmaku", 0),
            "reply": stat.get("reply", 0),
            "favorite": stat.get("favorite", 0),
            "coin": stat.get("coin", 0),
            "share": stat.get("share", 0),
            "like": stat.get("like", 0),
        },
        "pages": len(v.get("pages", []) or []),
    }


def slim_comment(c: dict[str, Any]) -> dict[str, Any]:
    member = c.get("member", {}) or {}
    content = c.get("content", {}) or {}
    return {
        "rpid": c.get("rpid", 0),
        "author": member.get("uname", ""),
        "likes": c.get("like", 0),
        "time": c.get("ctime", 0),
        "text": (content.get("message") or "")[:500],
    }

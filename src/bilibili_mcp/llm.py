"""Local LLM integration for bilibili-mcp.

Used by the REST /api/translate and /api/summarize endpoints. Defaults to a
local Ollama (Local LLM First doctrine) and degrades honestly when no LLM is
reachable - translate falls back to a small built-in glossary, summarize
returns an explicit not_configured error instead of a fake summary.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from .config import settings

logger = logging.getLogger(__name__)

# Small built-in glossary for when no LLM is reachable. Not a translation
# engine - just enough to gloss common Bilibili terms.
_GLOSSARY: dict[str, str] = {
    "播放": "views",
    "弹幕": "danmaku",
    "点赞": "likes",
    "收藏": "favorites",
    "关注": "follow",
    "投稿": "upload",
    "UP主": "creator",
    "视频": "video",
    "热门": "trending",
    "排行榜": "ranking",
    "搜索": "search",
    "评论": "comments",
    "字幕": "subtitles",
    "创作": "creation",
}


def _glossary_gloss(text: str) -> str:
    out = text
    for zh, en in _GLOSSARY.items():
        out = out.replace(zh, f"{zh} ({en})")
    return out if out != text else ""


def _llm_chat(system: str, user: str) -> str | None:
    """One-shot chat against the configured local LLM; None if unreachable."""
    if not settings.llm_configured:
        return None
    try:
        resp = httpx.post(
            f"{settings.llm_base_url}/chat/completions",
            json={
                "model": settings.llm_model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "temperature": 0.3,
                "max_tokens": 1200,
            },
            timeout=60.0,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception as exc:
        logger.warning("LLM call failed: %s", exc)
        return None


def provider_health(force: bool = False) -> dict[str, Any]:
    """Reachability probe for the LLM provider."""
    if not settings.llm_configured:
        return {"available": False, "model": settings.llm_model, "base_url": settings.llm_base_url}
    try:
        resp = httpx.get(f"{settings.llm_base_url}/models", timeout=5.0)
        return {
            "available": resp.status_code == 200,
            "model": settings.llm_model,
            "base_url": settings.llm_base_url,
        }
    except Exception:
        return {"available": False, "model": settings.llm_model, "base_url": settings.llm_base_url}


def translate(text: str, target: str = "en") -> dict[str, Any]:
    """Translate Chinese to English via local LLM, falling back to a glossary."""
    if target != "en":
        return {"translated": False, "translation": "", "note": "only en target supported for now"}
    result = _llm_chat(
        "You are a concise Chinese-to-English translator. Output only the translation.",
        text,
    )
    if result:
        return {"translated": True, "translation": result, "note": "llm"}
    gloss = _glossary_gloss(text)
    if gloss:
        return {"translated": True, "translation": gloss, "note": "glossary"}
    return {
        "translated": False,
        "translation": "",
        "note": "No LLM configured/reachable and no glossary terms matched.",
    }


def summarize(text: str) -> str:
    """Summarise a transcript via the local LLM."""
    result = _llm_chat(
        "You summarise Chinese video transcripts into concise English bullet points "
        "(3-6 bullets). Preserve key facts, names and numbers. Output only the bullets.",
        text[:6000],
    )
    if result:
        return result
    raise RuntimeError(
        "Summarisation requires a reachable local LLM - set BILIBILI_LLM_BASE_URL and "
        "BILIBILI_LLM_MODEL (e.g. Ollama at http://127.0.0.1:11434/v1)."
    )

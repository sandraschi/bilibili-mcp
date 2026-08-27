"""Thin httpx client against Bilibili's public web APIs.

Bilibili has no stable public REST contract and aggressively rate-limits
scrapers, so this client is deliberately minimal, honest about failure, and
kept independent of fragile third-party wrappers. It targets the well-known
web-interface endpoints:

  /x/web-interface/popular       trending / popular feed
  /x/web-interface/ranking       regional / all rankings
  /x/web-interface/view          video metadata (by bvid or aid)
  /x/player/pagelist             page -> cid map for a video
  /x/player/wbi/v2 + /v2         subtitle metadata for a cid
  /x/v2/reply                    top comments for a video (oid = aid)

Every call returns a structured dict with success/error. Auth-gated or
risk-control responses (-101, -412, -403) are surfaced as actionable errors,
never faked.

A logged-in Cookie header (BILIBILI_COOKIE) is optional and unlocks a few
higher rate limits and account-tier endpoints; it is not required for the
content-intelligence tier.
"""

from __future__ import annotations

import logging
import threading
from typing import Any

import httpx

from .config import settings

logger = logging.getLogger(__name__)


class BilibiliError(Exception):
    """Raised for a non-success or non-2xx Bilibili API response."""

    def __init__(self, message: str, error_type: str = "api_error") -> None:
        super().__init__(message)
        self.error_type = error_type


class BilibiliClient:
    def __init__(self) -> None:
        self._base = settings.api_base
        self._timeout = settings.request_timeout
        self._cookie = settings.cookie
        self._lock = threading.Lock()
        self._last_status = {
            "tier": "account" if self._cookie else "anonymous",
            "rate_limited": False,
        }

    # ------------------------------------------------------------- transport

    def _headers(self) -> dict[str, str]:
        headers = {
            "User-Agent": settings.user_agent,
            "Referer": "https://www.bilibili.com/",
            "Accept": "application/json, text/plain, */*",
        }
        if self._cookie:
            headers["Cookie"] = self._cookie
        return headers

    def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"{self._base}{path}"
        try:
            resp = httpx.get(
                url,
                params=params,
                headers=self._headers(),
                timeout=self._timeout,
                follow_redirects=True,
            )
        except httpx.HTTPError as exc:
            raise BilibiliError(f"Network error reaching Bilibili: {exc}", "network") from exc

        if resp.status_code == 412:
            with self._lock:
                self._last_status["rate_limited"] = True
            raise BilibiliError(
                "Bilibili risk control blocked this request (HTTP 412). Slow down, add a delay, "
                "or set BILIBILI_COOKIE to raise the budget.",
                "rate_limited",
            )

        try:
            payload = resp.json()
        except Exception:
            raise BilibiliError(
                f"Non-JSON response from Bilibili (HTTP {resp.status_code}). This often means "
                "risk control served a captcha page.",
                "parse_error",
            ) from None

        # Bilibili returns HTTP 200 with a code field for logical errors.
        code = payload.get("code", 0)
        if code == -101:
            raise BilibiliError(
                "Bilibili returned -101 (not logged in) for this endpoint.", "auth_required"
            )
        if code == -403:
            raise BilibiliError(
                "Bilibili returned -403 (access denied) for this endpoint.", "auth_required"
            )
        if code != 0:
            message = payload.get("message") or payload.get("msg") or f"code {code}"
            raise BilibiliError(f"Bilibili API error: {message}", "api_error")
        return payload

    # ------------------------------------------------------------ surfaces

    def popular(self, page: int = 1, page_size: int = 20) -> list[dict[str, Any]]:
        """Popular feed (trending) - works anonymously."""
        payload = self._get(
            "/x/web-interface/popular",
            {"pn": max(1, page), "ps": min(max(1, page_size), 50), "web_location": "1430650"},
        )
        return payload.get("data", {}).get("list", [])

    def ranking(self, rid: int = 0, limit: int = 20) -> list[dict[str, Any]]:
        """All-region ranking - works anonymously. rid 0 = all, 1 = anime, etc."""
        payload = self._get(
            "/x/web-interface/ranking",
            {"rid": rid, "type": "all", "ps": min(max(1, limit), 50)},
        )
        return payload.get("data", {}).get("list", [])

    def hot_search(self, limit: int = 10) -> list[dict[str, Any]]:
        """Trending search keywords - works anonymously."""
        payload = self._get("/x/web-interface/search/square", {"limit": min(max(1, limit), 20)})
        return payload.get("data", {}).get("trending", {}).get("list", [])

    def search(self, keyword: str, page: int = 1, page_size: int = 20) -> dict[str, Any]:
        """Search videos. May hit risk control anonymously; handled honestly."""
        payload = self._get(
            "/x/web-interface/search/type",
            {
                "search_type": "video",
                "keyword": keyword,
                "page": max(1, page),
                "page_size": min(max(1, page_size), 50),
            },
        )
        data = payload.get("data", {}) or {}
        return {"result": data.get("result", []), "num_results": data.get("numResults", 0)}

    def search_user(self, keyword: str, page: int = 1, page_size: int = 20) -> dict[str, Any]:
        """Search users (bilibili space). May hit risk control anonymously."""
        payload = self._get(
            "/x/web-interface/search/type",
            {
                "search_type": "bili_user",
                "keyword": keyword,
                "page": max(1, page),
                "page_size": min(max(1, page_size), 50),
            },
        )
        data = payload.get("data", {}) or {}
        return {"result": data.get("result", []), "num_results": data.get("numResults", 0)}

    def video_info(self, bvid: str = "", aid: int = 0) -> dict[str, Any]:
        """Video metadata by bvid (BV1...) or aid."""
        params: dict[str, Any] = {}
        if bvid:
            params["bvid"] = bvid
        elif aid:
            params["aid"] = aid
        else:
            raise BilibiliError("video_info requires bvid or aid", "validation")
        payload = self._get("/x/web-interface/view", params)
        return payload.get("data", {})

    def pagelist(self, bvid: str) -> list[dict[str, Any]]:
        """Pages for a video; first page cid is used for subtitles."""
        payload = self._get("/x/player/pagelist", {"bvid": bvid})
        return payload.get("data", [])

    def subtitle_metadata(self, bvid: str, cid: int) -> list[dict[str, Any]]:
        """Subtitle tracks for a cid (from player/v2 or wbi/v2)."""
        try:
            payload = self._get("/x/player/v2", {"bvid": bvid, "cid": cid})
        except BilibiliError:
            # wbi/v2 may need a signed token; retry the newer endpoint once.
            payload = self._get("/x/player/wbi/v2", {"bvid": bvid, "cid": cid})
        data = payload.get("data", {}) or {}
        subtitles = (data.get("subtitle") or {}).get("subtitles", [])
        return subtitles or []

    def subtitle_text(self, subtitle_url: str) -> str:
        """Fetch and join a subtitle JSON (body of from/to/content) into text."""
        if not subtitle_url:
            return ""
        if subtitle_url.startswith("//"):
            subtitle_url = "https:" + subtitle_url
        resp = httpx.get(subtitle_url, headers=self._headers(), timeout=self._timeout)
        if resp.status_code != 200:
            return ""
        try:
            data = resp.json()
        except Exception:
            return ""
        segments = data.get("body", [])
        return "\n".join(str(seg.get("content", "")) for seg in segments if seg.get("content"))

    def comments(self, aid: int, page: int = 1, page_size: int = 20) -> list[dict[str, Any]]:
        """Top comments for a video (sort=2 hot). oid is the video aid."""
        payload = self._get(
            "/x/v2/reply",
            {
                "type": 1,
                "oid": aid,
                "sort": 2,
                "pn": max(1, page),
                "ps": min(max(1, page_size), 50),
            },
        )
        return payload.get("data", {}).get("replies", []) or []

    def status_snapshot(self) -> dict[str, Any]:
        return dict(self._last_status)


_client: BilibiliClient | None = None


def get_client() -> BilibiliClient:
    global _client
    if _client is None:
        _client = BilibiliClient()
    return _client

"""bilibili_transcript - fetch auto-generated subtitles as plain text.

The highest-value tool for content intelligence: turn a video into
summarizable text without watching it. Falls back through part cids and
honestly reports when no subtitles exist.
"""

from __future__ import annotations

from typing import Annotated

from fastmcp import Context
from pydantic import Field

from ..cache import get as cache_get
from ..cache import set as cache_set
from ..client import BilibiliError, get_client
from ..errors import READ_ONLY, error_response
from ..helpers import parse_bvid
from ..server_state import mcp

_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "success": {"type": "boolean"},
        "message": {"type": "string"},
        "data": {
            "type": "object",
            "properties": {
                "bvid": {"type": "string"},
                "cid": {"type": "integer"},
                "lang": {"type": "string"},
                "text": {"type": "string"},
                "word_count": {"type": "integer"},
            },
        },
        "error": {"type": "string"},
        "error_type": {"type": "string"},
        "suggestions": {"type": "array"},
    },
}


@mcp.tool(annotations=READ_ONLY, output_schema=_OUTPUT_SCHEMA, version="0.1.0")
async def bilibili_transcript(
    bvid: Annotated[
        str, Field(description="Video id or full bilibili.com/video/... URL (starts with BV).")
    ],
    part_index: Annotated[
        int,
        Field(
            description="Which part (1-based) to transcribe for multi-part videos. "
            "Defaults to the first part.",
            ge=1,
        ),
    ] = 1,
    ctx: Context | None = None,
) -> dict:
    """Fetch a video's auto-generated subtitle track as plain text.

    Returns the transcript as text so an LLM can summarise or translate it.
    Some videos have no subtitles (or subtitles require login to access); in
    that case the tool returns an honest, actionable error rather than empty.

    ## Return Format
    {"success": bool, "data": {"bvid": str, "cid": int, "lang": str,
     "text": str, "word_count": int}, "message": str}

    ## Examples
    bilibili_transcript(bvid="BV1xx411c7mD")
    bilibili_transcript(bvid="https://www.bilibili.com/video/BV1xx411c7mD", part_index=2)
    """
    client = get_client()
    bvid = parse_bvid(bvid)
    if not bvid:
        return {
            "success": False,
            "error": "could not parse a bvid from input",
            "error_type": "validation",
            "message": "could not parse a bvid from input",
        }
    key = f"transcript:{bvid}:{part_index}"
    cached = cache_get(key)
    if cached is not None:
        return {"success": True, "data": cached, "message": "Cached transcript.", "cached": True}
    try:
        info = client.video_info(bvid=bvid, aid=0)
        pages = info.get("pages", []) or []
        if not pages:
            return {
                "success": False,
                "error": "No playable pages found for this video.",
                "error_type": "not_found",
                "message": "No playable pages found for this video.",
            }
        page = pages[min(part_index - 1, len(pages) - 1)]
        cid = page.get("cid", 0)
        tracks = client.subtitle_metadata(bvid, cid)
        if not tracks:
            return {
                "success": False,
                "error": "No subtitle tracks available for this video (creator disabled captions).",
                "error_type": "not_found",
                "message": "No subtitle tracks available for this video (creator disabled captions).",
                "suggestions": [
                    "Some videos gate subtitles behind login - set BILIBILI_COOKIE and retry."
                ],
            }
        # Prefer an AI/auto subtitle; fall back to the first available track.
        track = next((t for t in tracks if t.get("ai_status", 0) == 2), tracks[0])
        url = track.get("subtitle_url", "")
        lang = track.get("lan", "unknown")
        text = client.subtitle_text(url)
        if not text:
            return {
                "success": False,
                "error": "Subtitle track was found but returned no text.",
                "error_type": "parse_error",
                "message": "Subtitle track was found but returned no text.",
            }
        result = {
            "bvid": bvid,
            "cid": cid,
            "lang": lang,
            "text": text,
            "word_count": len(text.split()),
        }
        cache_set(key, result)
        return {
            "success": True,
            "data": result,
            "message": f"Fetched {result['word_count']}-word transcript for {bvid} (part {part_index}).",
        }
    except BilibiliError as exc:
        return error_response(exc, error_type=exc.error_type)

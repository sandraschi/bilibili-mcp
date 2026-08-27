"""bilibili_video portmanteau - single-video intel: info, comments, pages."""

from __future__ import annotations

from typing import Annotated, Literal

from fastmcp import Context
from pydantic import Field

from ..client import BilibiliError, get_client
from ..errors import READ_ONLY, error_response
from ..helpers import format_video, parse_bvid, slim_comment
from ..server_state import mcp

_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "success": {"type": "boolean"},
        "operation": {"type": "string"},
        "message": {"type": "string"},
        "data": {"type": "object"},
        "error": {"type": "string"},
        "error_type": {"type": "string"},
        "suggestions": {"type": "array"},
    },
}


@mcp.tool(annotations=READ_ONLY, output_schema=_OUTPUT_SCHEMA, version="0.1.0")
async def bilibili_video(
    operation: Annotated[
        Literal["info", "comments", "pages"],
        Field(
            description=(
                "Operation: 'info' returns full metadata + stats for one video; "
                "'comments' returns the hot top comments (needs the video aid); "
                "'pages' returns the multi-part page list (first page cid is used "
                "for transcript)."
            )
        ),
    ],
    bvid: Annotated[
        str, Field(description="Video id or full bilibili.com/video/... URL (starts with BV).")
    ] = "",
    aid: Annotated[int, Field(description="Alternative numeric video aid (avN).")] = 0,
    limit: Annotated[int, Field(description="Max comments (1-50).", ge=1, le=50)] = 20,
    ctx: Context | None = None,
) -> dict:
    """Inspect a single Bilibili video: metadata, comments, or part list.

    ## Return Format
    {"success": bool, "operation": str, "data": {...}, "message": str}

    ## Examples
    bilibili_video(operation="info", bvid="BV1xx411c7mD")
    bilibili_video(operation="comments", bvid="BV1xx411c7mD", limit=10)
    bilibili_video(operation="pages", bvid="BV1xx411c7mD")
    """
    client = get_client()
    try:
        bvid = parse_bvid(bvid)
        if not bvid and not aid:
            return {
                "success": False,
                "operation": operation,
                "error": "bvid or aid required",
                "error_type": "validation",
                "message": "bvid or aid required",
            }
        if operation == "info":
            info = client.video_info(bvid=bvid, aid=aid)
            return {
                "success": True,
                "operation": operation,
                "data": format_video(info),
                "message": f"Fetched info for {info.get('bvid', bvid)}: {info.get('title', '')[:80]}",
            }
        if operation == "pages":
            if not bvid:
                return {
                    "success": False,
                    "operation": operation,
                    "error": "pages requires bvid",
                    "error_type": "validation",
                    "message": "pages requires bvid",
                }
            pages = client.pagelist(bvid)
            slim = [
                {"cid": p.get("cid", 0), "page": p.get("page", 0), "part": p.get("part", "")}
                for p in pages
            ]
            return {
                "success": True,
                "operation": operation,
                "data": {"bvid": bvid, "pages": slim, "count": len(slim)},
                "message": f"Found {len(slim)} part(s) for {bvid}.",
            }
        if operation == "comments":
            if not aid:
                info = client.video_info(bvid=bvid, aid=0)
                aid = info.get("aid", 0)
            if not aid:
                return {
                    "success": False,
                    "operation": operation,
                    "error": "could not resolve aid for comments",
                    "error_type": "validation",
                    "message": "could not resolve aid for comments",
                }
            replies = client.comments(aid, page=1, page_size=limit)
            slim = [slim_comment(c) for c in replies]
            return {
                "success": True,
                "operation": operation,
                "data": {"aid": aid, "comments": slim, "count": len(slim)},
                "message": f"Returned {len(slim)} hot comments for aid {aid}.",
            }
        return {
            "success": False,
            "operation": operation,
            "error": f"unknown operation {operation}",
            "error_type": "validation",
            "message": f"unknown operation {operation}",
        }
    except BilibiliError as exc:
        return error_response(exc, error_type=exc.error_type, operation=operation)

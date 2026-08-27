"""bilibili_search portmanteau - video and user search.

Anonymously these may hit Bilibili risk control; failures are surfaced
honestly with suggestions rather than an empty fake list.
"""

from __future__ import annotations

from typing import Annotated, Literal

from fastmcp import Context
from pydantic import Field

from ..client import BilibiliError, get_client
from ..errors import READ_ONLY, error_response
from ..helpers import slim_video
from ..server_state import mcp

_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "success": {"type": "boolean"},
        "operation": {"type": "string"},
        "message": {"type": "string"},
        "data": {"type": "array"},
        "count": {"type": "integer"},
        "error": {"type": "string"},
        "error_type": {"type": "string"},
        "suggestions": {"type": "array"},
    },
}


@mcp.tool(annotations=READ_ONLY, output_schema=_OUTPUT_SCHEMA, version="0.1.0")
async def bilibili_search(
    operation: Annotated[
        Literal["video", "user"],
        Field(
            description=(
                "Operation: 'video' searches video titles; 'user' searches creators "
                "(bilibili spaces). Both may be risk-controlled anonymously - if a "
                "-412 block is returned, retry after a delay or set BILIBILI_COOKIE."
            )
        ),
    ],
    keyword: Annotated[str, Field(description="Search term (Chinese or English).")],
    limit: Annotated[int, Field(description="Max results (1-50).", ge=1, le=50)] = 10,
    ctx: Context | None = None,
) -> dict:
    """Search Bilibili for videos or creators.

    ## Return Format
    {"success": bool, "operation": str, "data": [...], "count": int}

    ## Examples
    bilibili_search(operation="video", keyword="微积分")
    bilibili_search(operation="user", keyword="罗翔", limit=5)
    """
    client = get_client()
    try:
        if operation == "video":
            res = client.search(keyword, page=1, page_size=limit)
            items = [slim_video(v) for v in res["result"] if v.get("bvid")]
            message = f"Found {res['num_results']} videos for '{keyword}'; returned {len(items)}."
        elif operation == "user":
            res = client.search_user(keyword, page=1, page_size=limit)
            items = [
                {
                    "mid": u.get("mid", 0),
                    "name": u.get("uname", ""),
                    "fans": u.get("fans", 0),
                    "videos": u.get("videos", 0),
                    "sign": (u.get("usign") or "")[:200],
                    "url": f"https://space.bilibili.com/{u.get('mid', 0)}",
                }
                for u in res["result"]
                if u.get("mid")
            ]
            message = f"Found {res['num_results']} users for '{keyword}'; returned {len(items)}."
        else:
            return {
                "success": False,
                "operation": operation,
                "error": f"unknown operation {operation}",
                "error_type": "validation",
                "message": f"unknown operation {operation}",
            }
        return {
            "success": True,
            "operation": operation,
            "data": items,
            "count": len(items),
            "message": message,
        }
    except BilibiliError as exc:
        suggestions = (
            ["Search may need a login cookie (BILIBILI_COOKIE) to pass risk control."]
            if exc.error_type == "rate_limited"
            else []
        )
        return error_response(
            exc, error_type=exc.error_type, operation=operation, suggestions=suggestions
        )

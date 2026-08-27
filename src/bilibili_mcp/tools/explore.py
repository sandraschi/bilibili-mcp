"""bilibili_explore portmanteau - trending, ranking, and hot-search surfaces.

All operations work anonymously (content-intelligence tier).
"""

from __future__ import annotations

from typing import Annotated, Literal

from fastmcp import Context
from pydantic import Field

from ..cache import get as cache_get
from ..cache import set as cache_set
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
async def bilibili_explore(
    operation: Annotated[
        Literal["trending", "rank", "hot_search"],
        Field(
            description=(
                "Operation: 'trending' returns the popular feed (what is hot right now); "
                "'rank' returns the all-region daily ranking (rid 0 = all, 1 = anime, "
                "3 = music, 4 = game, 5 = entertainment, 36 = knowledge, 160 = fashion); "
                "'hot_search' returns the current trending search keywords."
            )
        ),
    ],
    limit: Annotated[int, Field(description="Max results (1-50).", ge=1, le=50)] = 20,
    rid: Annotated[
        int, Field(description="Ranking region id; only used for operation='rank'.")
    ] = 0,
    ctx: Context | None = None,
) -> dict:
    """Discover what is trending on Bilibili: popular feed, rankings, hot keywords.

    [RATIONALE]
    Discovery has three list surfaces (popular, rank, hot search) that share a
    single 'video-ish list' output; one tool with an operation discriminator
    keeps the surface compact and discoverable.

    ## Return Format
    {"success": bool, "operation": str, "data": [...], "count": int}

    ## Examples
    bilibili_explore(operation="trending", limit=10)
    bilibili_explore(operation="rank", rid=3, limit=15)
    bilibili_explore(operation="hot_search", limit=10)
    """
    client = get_client()
    key = f"{operation}:{rid}:{limit}"
    cached = cache_get(key)
    if cached is not None:
        return {
            "success": True,
            "operation": operation,
            "data": cached,
            "count": len(cached),
            "cached": True,
        }
    try:
        if operation == "trending":
            items = [slim_video(v) for v in client.popular(page=1, page_size=limit)]
            message = f"Returned {len(items)} trending videos."
        elif operation == "rank":
            items = [slim_video(v) for v in client.ranking(rid=rid, limit=limit)]
            message = f"Returned {len(items)} ranking entries (rid={rid})."
        elif operation == "hot_search":
            raw = client.hot_search(limit=limit)
            items = [
                {
                    "keyword": k.get("keyword", ""),
                    "heat": k.get("heat_score", k.get("show_name", "")),
                }
                for k in raw
            ]
            message = f"Returned {len(items)} trending search keywords."
        else:
            return {
                "success": False,
                "operation": operation,
                "error": f"unknown operation {operation}",
                "error_type": "validation",
                "message": f"unknown operation {operation}",
            }
        cache_set(key, items)
        return {
            "success": True,
            "operation": operation,
            "data": items,
            "count": len(items),
            "message": message,
        }
    except BilibiliError as exc:
        return error_response(exc, error_type=exc.error_type, operation=operation)

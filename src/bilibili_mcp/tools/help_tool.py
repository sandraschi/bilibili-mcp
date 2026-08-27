"""bilibili_help - self-description and tool discovery for agents."""

from __future__ import annotations

from typing import Annotated

from fastmcp import Context
from pydantic import Field

from ..errors import READ_ONLY
from ..server_state import mcp

_HELP_TEXT = """Bilibili MCP - content-intelligence bridge for the Chinese video platform.

Two tiers:
- Anonymous (default): bilibili_explore (trending/rank/hot_search),
  bilibili_search (video/user), bilibili_video (info/comments/pages),
  bilibili_transcript (subtitle text for summarisation).
- Account (BILIBILI_COOKIE set): bilibili_account unlocks following feed and
  favorites. Requires a +86 login (see docs/ONBOARDING.md).

No video playback - this server returns metadata, lists and transcripts so an
agent can search, rank and summarise Bilibili content without watching it.
"""


@mcp.tool(annotations=READ_ONLY, version="0.1.0")
async def bilibili_help(
    topic: Annotated[
        str, Field(description="Optional topic to focus on (e.g. 'transcript', 'account').")
    ] = "",
    ctx: Context | None = None,
) -> dict:
    """Explain how to use the bilibili-mcp server.

    ## Return Format
    {"success": bool, "data": {"help": str, "tools": [...]}, "message": str}

    ## Examples
    bilibili_help()
    bilibili_help(topic="transcript")
    """
    try:
        tools = await mcp.list_tools()
        names = sorted(t.name for t in tools)
    except Exception:
        names = []
    text = _HELP_TEXT
    if topic:
        text += f"\n\nFocus requested on: {topic}. The available tools are listed below."
    return {"success": True, "data": {"help": text, "tools": names}, "message": "Help returned."}

"""Prefab UI cards - required in-chat surfaces for list/status tools."""

from __future__ import annotations

from fastmcp import Context
from fastmcp.tools import ToolResult
from prefab_ui import PrefabApp
from prefab_ui.components import (
    Card,
    CardContent,
    CardHeader,
    CardTitle,
    Div,
    Heading,
    Row,
    Text,
)

from ..cache import clear as cache_clear
from ..client import BilibiliError, get_client
from ..config import settings
from ..errors import READ_ONLY, error_response
from ..helpers import slim_video
from ..server_state import mcp


def _kv(label: str, value: str) -> Row:
    """Key/value row - prefab Row is a layout container, so pair Texts."""
    return Row(
        justify="between",
        children=[
            Text(label, css_class="text-zinc-400"),
            Text(value, css_class="font-semibold"),
        ],
    )


@mcp.tool(app=True, annotations=READ_ONLY, version="0.1.0")
async def show_bilibili_trending_card(
    limit: int = 10,
    ctx: Context | None = None,
) -> ToolResult:
    """Show what is trending on Bilibili right now as a rich in-chat card.

    [RATIONALE]
    Status/list tools MUST ship a Prefab surface per fleet SOTA - this card
    renders the popular feed in chat without the agent reading raw JSON.

    ## Return Format
    ToolResult with content (plain text fallback) + structured PrefabApp card.

    ## Examples
    show_bilibili_trending_card(limit=5)
    """
    client = get_client()
    try:
        items = [slim_video(v) for v in client.popular(page=1, page_size=limit)]
    except BilibiliError as exc:
        err = error_response(exc, error_type=exc.error_type)
        return ToolResult(content=err["error"], structured_content=None)
    lines = []
    with PrefabApp(title="Bilibili Trending") as app:
        Heading("Trending on Bilibili")
        for v in items[:10]:
            title = v.get("title", "")
            author = v.get("author", "")
            play = v.get("play", 0)
            bvid = v.get("bvid", "")
            with Card(css_class="mb-2"):
                with CardHeader():
                    CardTitle(title[:80])
                with CardContent():
                    _kv("Author", author)
                    _kv("Views", f"{play:,}")
                    _kv("Video", bvid)
            lines.append(f"- **{title[:80]}** by {author} ({play:,} views) - {bvid}")
    plain = f"Trending on Bilibili ({len(items)}):\n" + "\n".join(lines)
    return ToolResult(content=plain, structured_content=app)


@mcp.tool(app=True, annotations=READ_ONLY, version="0.1.0")
async def show_bilibili_status_card(ctx: Context | None = None) -> ToolResult:
    """Show bilibili-mcp configuration status as a rich in-chat card.

    [RATIONALE]
    Status tools MUST ship a Prefab surface - one call shows tier, cookie
    state and cache headroom at a glance.

    ## Return Format
    ToolResult with content (plain text fallback) + structured PrefabApp card.

    ## Examples
    show_bilibili_status_card()
    """
    tier = "Account (logged in)" if settings.configured else "Anonymous"
    with PrefabApp(title="Bilibili MCP Status") as app:
        Heading("bilibili-mcp")
        _kv("Tier", tier)
        _kv("Cookie", "configured" if settings.configured else "not set")
        _kv("LLM provider", settings.llm_base_url or "(none)")
        _kv("LLM model", settings.llm_model)
        Div()
        Text(
            "Anonymous tier powers search, trending, video intel and transcripts. "
            "Set BILIBILI_COOKIE to unlock account-tier tools (following, favorites)."
        )
    plain = (
        f"Tier: {tier} | Cookie: {'configured' if settings.configured else 'not set'} | "
        f"LLM: {settings.llm_model} @ {settings.llm_base_url}"
    )
    return ToolResult(content=plain, structured_content=app)


@mcp.tool(app=True, annotations=READ_ONLY, version="0.1.0")
async def show_bilibili_cache_card(ctx: Context | None = None) -> ToolResult:
    """Show and clear the Bilibili response cache.

    [RATIONALE]
    A tiny status surface for the TTL cache - helps debug rate-limit staleness.

    ## Return Format
    ToolResult with content + structured PrefabApp card.

    ## Examples
    show_bilibili_cache_card()
    """
    cleared = cache_clear()
    with PrefabApp(title="Bilibili Cache") as app:
        Heading("Bilibili response cache")
        _kv("Action", "Cleared cache")
        _kv("Entries removed", str(cleared))
    return ToolResult(
        content=f"Cleared {cleared} cached Bilibili responses.", structured_content=app
    )

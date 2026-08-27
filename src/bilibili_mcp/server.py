"""bilibili-mcp server - FastMCP instance, FastAPI REST surface, dual transport.

Run modes:
  stdio : uv run python -m bilibili_mcp.server          (no env vars)
  http  : uv run python -m bilibili_mcp.server --mode http --host 127.0.0.1 --port 11185
  auto  : run_server.py switches on MCP_PORT / PORT env
"""

from __future__ import annotations

import argparse
import asyncio
import contextlib
import logging
import os
import time
from collections import deque
from pathlib import Path

import uvicorn
from fastapi import Body, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from . import __version__
from .client import get_client
from .config import settings
from .server_state import mcp

logger = logging.getLogger("bilibili_mcp")

# ------------------------------------------------------------------ log ring


class RingBufferHandler(logging.Handler):
    """In-memory ring buffer so the webapp Logs page works without files."""

    def __init__(self, capacity: int = 500) -> None:
        super().__init__()
        self.capacity = capacity
        self.records: deque[dict] = deque(maxlen=capacity)

    def emit(self, record: logging.LogRecord) -> None:
        # logging must never raise; the ring buffer is best-effort
        with contextlib.suppress(Exception):
            self.records.append(
                {
                    "ts": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(record.created)),
                    "level": record.levelname,
                    "source": record.name,
                    "message": record.getMessage(),
                }
            )


_ring = RingBufferHandler()
logging.basicConfig(
    level=logging.INFO, handlers=[_ring], format="%(levelname)s %(name)s: %(message)s"
)

# ------------------------------------------------------------------ MCP app

from . import tools as _tools  # noqa: E402, F401  (side-effect: registers all @mcp.tool)


async def _discover_tool_names() -> list[str]:
    try:
        tools = await mcp.list_tools()
        return sorted(t.name for t in tools)
    except Exception:
        return []


_TOOL_NAMES: list[str] = asyncio.run(_discover_tool_names())
_TOOL_COUNT = len(_TOOL_NAMES)


@mcp.resource("skill://bilibili-expert/SKILL.md")
def skill_bilibili_expert() -> str:
    """The bilibili-expert skill - how to use the server well."""
    skill_path = Path(__file__).parent / "skills" / "bilibili-expert" / "SKILL.md"
    if skill_path.exists():
        return skill_path.read_text(encoding="utf-8")
    return "Bilibili MCP server skill: use bilibili_explore for discovery, bilibili_transcript for summaries."


@mcp.prompt()
def bilibili_research() -> str:
    """Discover what is trending on Bilibili and summarise a video's transcript."""
    return (
        "You are exploring the Chinese video platform Bilibili.\n"
        "1. Call bilibili_explore(operation='trending', limit=10) to see what is hot right now.\n"
        "2. Pick a video and call bilibili_video(operation='info', bvid=...) for metadata, "
        "then bilibili_transcript(bvid=...) to get its subtitle text.\n"
        "3. Summarise the transcript in English (or the user's language) - Bilibili content is "
        "largely Chinese, so treat the transcript as source material to summarise, not to repeat verbatim.\n"
        "4. Respect Bilibili's rate limits - reuse cached results and do not re-fetch the same video twice in a session."
    )


@mcp.prompt()
def bilibili_briefing() -> str:
    """Produce a short 'what is trending on Bilibili' briefing."""
    return (
        "You are compiling a Bilibili trend briefing.\n"
        "1. Call bilibili_explore(operation='trending', limit=10) and "
        "bilibili_explore(operation='hot_search', limit=10).\n"
        "2. For the 2-3 most interesting videos, call bilibili_transcript(bvid=...) and summarise.\n"
        "3. Present a short briefing: what is trending, why it matters, and one insight. "
        "Never invent numbers - cite only what the tools returned."
    )


class TranslateRequest(BaseModel):
    text: str


class ChatRequest(BaseModel):
    messages: list[dict]
    model: str = ""


class SummarizeRequest(BaseModel):
    bvid: str


# ------------------------------------------------------------------ REST app


def build_app() -> FastAPI:
    _mcp_http = mcp.http_app(path="/")
    app = FastAPI(title="Bilibili MCP", version=__version__, lifespan=_mcp_http.lifespan)

    # Fleet CORS standard: explicit origins + unconditional LAN/Tailscale regex.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            f"http://localhost:{settings.frontend_port}",
            f"http://127.0.0.1:{settings.frontend_port}",
            "http://tauri.localhost",
            "https://tauri.localhost",
            "tauri://localhost",
        ],
        allow_origin_regex=(
            r"https?://(?:[a-zA-Z0-9-]+\.ts\.net|.*?\.tail-[a-f0-9]+\.ts\.net|tauri\.localhost"
            r"|localhost|127\.0\.0\.1|192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}"
            r"|100\.\d{1,3}\.\d{1,3}\.\d{1,3})(?::\d+)?$|^tauri://localhost$"
        ),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.mount("/mcp", _mcp_http)

    @app.get("/api/health")
    def health() -> dict:
        client = get_client()
        snapshot = client.status_snapshot()
        return {
            "status": "ok",
            "server": "bilibili-mcp",
            "version": __version__,
            "uptime_seconds": int(time.time() - _START_TS),
            "tool_count": _TOOL_COUNT,
            "configured": settings.configured,
            "tier": snapshot["tier"],
            "providers": {
                "bilibili": {"tier": snapshot["tier"], "configured": settings.configured}
            },
        }

    @app.get("/api/capabilities")
    def capabilities() -> dict:
        return {
            "server": "bilibili-mcp",
            "version": __version__,
            "features": {
                "explore": True,
                "search": True,
                "video": True,
                "transcript": True,
                "account": settings.configured or None,
                "anonymous": True,
            },
        }

    @app.get("/api/tools")
    def tools_list() -> dict:
        return {"tools": _TOOL_NAMES}

    @app.get("/api/skills")
    def skills_list() -> dict:
        return {
            "skills": [
                {
                    "name": "bilibili-expert",
                    "uri": "skill://bilibili-expert/SKILL.md",
                    "description": "How to use bilibili-mcp well - discovery, video intel, transcripts.",
                }
            ]
        }

    @app.get("/api/skills/{name}")
    def skill_content(name: str) -> str:
        skill_path = Path(__file__).parent / "skills" / f"{name}" / "SKILL.md"
        if skill_path.exists():
            return skill_path.read_text(encoding="utf-8")
        return "not found"

    @app.get("/api/dashboard")
    def dashboard() -> dict:
        client = get_client()
        snapshot = client.status_snapshot()
        return {
            "server": "bilibili-mcp",
            "version": __version__,
            "uptime_seconds": int(time.time() - _START_TS),
            "tool_count": _TOOL_COUNT,
            "configured": settings.configured,
            "tier": snapshot["tier"],
            "rate_limited": snapshot.get("rate_limited", False),
            "llm_configured": settings.llm_configured,
        }

    @app.get("/api/explore/trending")
    def explore_trending(limit: int = 20) -> dict:
        from .tools.explore import bilibili_explore

        return asyncio.run(bilibili_explore(operation="trending", limit=limit))

    @app.get("/api/explore/rank")
    def explore_rank(rid: int = 0, limit: int = 20) -> dict:
        from .tools.explore import bilibili_explore

        return asyncio.run(bilibili_explore(operation="rank", rid=rid, limit=limit))

    @app.get("/api/explore/hot_search")
    def explore_hot_search(limit: int = 10) -> dict:
        from .tools.explore import bilibili_explore

        return asyncio.run(bilibili_explore(operation="hot_search", limit=limit))

    @app.get("/api/search")
    def search_surface(keyword: str = "", operation: str = "video", limit: int = 10) -> dict:
        from .tools.search import bilibili_search

        if operation not in ("video", "user"):
            return {
                "success": False,
                "error": f"unknown search operation {operation}",
                "error_type": "validation",
            }
        return asyncio.run(bilibili_search(operation=operation, keyword=keyword, limit=limit))  # type: ignore[arg-type]

    @app.get("/api/video/info")
    def video_info(bvid: str = "", aid: int = 0) -> dict:
        from .tools.video import bilibili_video

        return asyncio.run(bilibili_video(operation="info", bvid=bvid, aid=aid))

    @app.get("/api/video/comments")
    def video_comments(bvid: str = "", limit: int = 20) -> dict:
        from .tools.video import bilibili_video

        return asyncio.run(bilibili_video(operation="comments", bvid=bvid, limit=limit))

    @app.get("/api/video/transcript")
    def video_transcript(bvid: str = "", part_index: int = 1) -> dict:
        from .tools.transcript import bilibili_transcript

        return asyncio.run(bilibili_transcript(bvid=bvid, part_index=part_index))

    @app.post("/api/translate", response_model=None)
    def translate_route(req: TranslateRequest = Body(...)) -> dict | JSONResponse:  # noqa: B008
        from .llm import translate

        result = translate(req.text)
        return {
            "success": True,
            "translated": result.get("translated", False),
            "translation": result.get("translation", ""),
            "note": result.get("note"),
        }

    @app.post("/api/summarize", response_model=None)
    def summarize_route(req: SummarizeRequest = Body(...)) -> dict | JSONResponse:  # noqa: B008
        from .tools.transcript import bilibili_transcript

        transcript = asyncio.run(bilibili_transcript(bvid=req.bvid, part_index=1))
        if not transcript.get("success"):
            return transcript
        text = transcript["data"]["text"]
        from .llm import summarize

        return {
            "success": True,
            "summary": summarize(text),
            "transcript_word_count": transcript["data"]["word_count"],
        }

    @app.get("/api/llm/discover")
    def llm_discover() -> dict:
        from .llm import discover_providers

        return discover_providers()

    @app.get("/api/llm/providers")
    def llm_providers() -> dict:
        from .llm import discover_providers

        return discover_providers()

    @app.post("/api/chat", response_model=None)
    def chat_route(req: ChatRequest = Body(...)) -> dict | JSONResponse:  # noqa: B008
        from .llm import chat_completion

        try:
            result = chat_completion(req.messages, req.model)
            return {"success": True, "reply": result["reply"], "model": result["model"]}
        except RuntimeError as exc:
            return JSONResponse(
                {
                    "success": False,
                    "error": str(exc),
                    "error_type": "not_configured",
                    "suggestions": [
                        "Start a local LLM (e.g. `ollama serve`) or set BILIBILI_LLM_BASE_URL / BILIBILI_LLM_MODEL.",
                    ],
                },
                status_code=503,
            )

    @app.get("/api/account/status")
    def account_status() -> dict:
        from .tools.account import bilibili_account

        return asyncio.run(bilibili_account(operation="status"))

    @app.get("/api/logs")
    def logs(limit: int = 100, level: str = "") -> dict:
        records = list(_ring.records)
        if level:
            records = [r for r in records if r["level"] == level.upper()]
        return {"logs": records[-max(limit, 1) :], "count": len(records)}

    @app.post("/api/shutdown", response_model=None)
    def shutdown() -> dict:
        """Graceful self-termination - stops the uvicorn server process."""
        import threading

        def _exit() -> None:
            time.sleep(0.5)
            os._exit(0)

        threading.Thread(target=_exit, daemon=True).start()
        return {"success": True, "message": "bilibili-mcp shutting down now."}

    return app


_START_TS = time.time()
app = build_app()


# ------------------------------------------------------------------- entry


def main() -> None:
    parser = argparse.ArgumentParser(prog="bilibili-mcp")
    parser.add_argument("--mode", choices=["stdio", "http"], default="stdio")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=settings.backend_port)
    args = parser.parse_args()

    if args.mode == "http":
        uvicorn.run(app, host=args.host, port=args.port, log_level="info")
    else:
        mcp.run()


if __name__ == "__main__":
    main()

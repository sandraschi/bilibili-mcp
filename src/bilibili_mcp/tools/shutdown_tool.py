"""bilibili_shutdown - graceful server self-termination (stdio/http)."""

from __future__ import annotations

import os
import threading
import time
from typing import Annotated

from fastmcp import Context
from pydantic import Field

from ..errors import MUTATING
from ..server_state import mcp


@mcp.tool(annotations=MUTATING, version="0.1.0")
async def bilibili_shutdown(
    confirm: Annotated[bool, Field(description="Must be True to shut down the server.")] = False,
    ctx: Context | None = None,
) -> dict:
    """Gracefully stop the bilibili-mcp server.

    ## Return Format
    {"success": bool, "message": str}

    ## Examples
    bilibili_shutdown(confirm=True)
    """
    if not confirm:
        return {
            "success": False,
            "message": "Confirmation required - pass confirm=True to shut down.",
        }
    threading.Thread(target=lambda: (time.sleep(0.5), os._exit(0)), daemon=True).start()
    return {"success": True, "message": "bilibili-mcp shutting down now."}

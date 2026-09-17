"""run_server.py - PyInstaller / MCPB entry point with MCP_PORT/PORT switching.

MCPB packs this alongside mcpb/src/ and runs it with PYTHONPATH=mcpb/src, so
this file must live at the repo root (copied into the bundle). The server is
imported from the bilibili_mcp package.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from bilibili_mcp.server import app, main  # noqa: E402

if __name__ == "__main__":
    port = os.environ.get("MCP_PORT") or os.environ.get("PORT")
    if port:
        sys.argv = [sys.argv[0], "--mode", "http", "--port", str(int(port))]
    main()

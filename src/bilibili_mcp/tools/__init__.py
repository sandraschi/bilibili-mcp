"""Tool registration for bilibili-mcp.

Portmanteau imports - each module decorates @mcp.tool at import time, so
importing here during server boot is what actually registers the tools.
"""

from . import (  # noqa: F401
    account,
    explore,
    help_tool,
    prefab,
    search,
    shutdown_tool,
    transcript,
    video,
)

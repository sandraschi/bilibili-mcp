"""Shared server state - the FastMCP instance lives here to avoid circular imports."""

from __future__ import annotations

from fastmcp import FastMCP

mcp = FastMCP("bilibili-mcp")

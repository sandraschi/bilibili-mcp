"""Shared tool helpers - error response factory and tool annotations.

Centralises the {success, message, error, error_type, suggestions} error
shape (TOOL_DESIGN_STANDARDS 4.2) with automatic logger.exception() capture,
and the FastMCP tool annotation constants (TOOL_DESIGN_STANDARDS 9).
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

# Tool annotations: signal behavior to the agent (READ_ONLY / MUTATING / DESTRUCTIVE).
READ_ONLY: dict[str, Any] = {"readonly": True}
MUTATING: dict[str, Any] = {"readonly": False}
DESTRUCTIVE: dict[str, Any] = {"readonly": False, "destructive": True}


def error_response(
    exc: Exception,
    error_type: str = "error",
    suggestions: list[str] | None = None,
    **extra: Any,
) -> dict[str, Any]:
    """Build a {success, message, error, error_type, suggestions} error dict.

    Must be called inside an except block so logger.exception() captures the
    active traceback. Never raises.
    """
    logger.exception("Tool failure (%s): %s", error_type, exc)
    return {
        "success": False,
        "message": str(exc),
        "error": str(exc),
        "error_type": error_type,
        "suggestions": suggestions or [],
        **extra,
    }


def requires_login() -> dict[str, Any]:
    """Honest account-tier response when no login cookie is configured.

    This is a declared, documented state - NOT a stub. The account-tier tools
    (following feed, favorites) genuinely cannot work without a logged-in
    +86 SESSDATA cookie, so they say so instead of faking success.
    """
    return {
        "success": False,
        "error_type": "auth_required",
        "error": "This operation requires a logged-in Bilibili account.",
        "message": "This operation requires a logged-in Bilibili account.",
        "suggestions": [
            "Most content-intelligence tools (search, trending, video info, transcript) work without an account.",
            "To unlock the account tier you need a +86 Bilibili account and a logged-in SESSDATA cookie.",
            'Set BILIBILI_COOKIE="SESSDATA=...;bili_jct=..." in .env - see docs/ONBOARDING.md.',
        ],
        "data": None,
    }

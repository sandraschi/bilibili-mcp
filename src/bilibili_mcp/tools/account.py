"""bilibili_account portmanteau - account tier.

'status' always works (reports the current tier). 'following' (new uploads
from creators you follow) and 'favorites' require a logged-in +86 account -
they return an honest requires_login state until BILIBILI_COOKIE is set.
No fake data is returned for the unauthenticated state.
"""

from __future__ import annotations

from typing import Annotated, Literal

from fastmcp import Context
from pydantic import Field

from ..config import settings
from ..errors import READ_ONLY, requires_login
from ..server_state import mcp

_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "success": {"type": "boolean"},
        "operation": {"type": "string"},
        "message": {"type": "string"},
        "data": {"type": "object"},
        "error": {"type": "string"},
        "error_type": {"type": "string"},
        "suggestions": {"type": "array"},
    },
}


@mcp.tool(annotations=READ_ONLY, output_schema=_OUTPUT_SCHEMA, version="0.1.0")
async def bilibili_account(
    operation: Annotated[
        Literal["status", "following", "favorites"],
        Field(
            description=(
                "Operation: 'status' reports the current account tier (works always). "
                "'following' lists new uploads from creators you follow and 'favorites' "
                "lists your saved videos - both require a logged-in +86 account and "
                "return an honest requires_login state otherwise."
            )
        ),
    ],
    mid: Annotated[int, Field(description="Bilibili user id (only for account 'status').")] = 0,
    ctx: Context | None = None,
) -> dict:
    """Account-tier operations: tier status, following feed, favorites.

    [RATIONALE]
    The account tier is one logical surface (your logged-in Bilibili world)
    with several sub-surfaces; one tool with an operation discriminator keeps
    it compact while the auth-gated ops are honestly marked requires_login.

    ## Return Format
    {"success": bool, "operation": str, "data": {...}, "message": str}

    ## Examples
    bilibili_account(operation="status")
    bilibili_account(operation="following")
    bilibili_account(operation="favorites")
    """
    if operation == "status":
        return {
            "success": True,
            "operation": operation,
            "data": {
                "tier": "account" if settings.configured else "anonymous",
                "authenticated": settings.configured,
                "note": (
                    "Account tier active - following feed and favorites unlocked."
                    if settings.configured
                    else "Anonymous tier - content intelligence works; account tools are locked."
                ),
            },
            "message": "Account tier is 'account'"
            if settings.configured
            else "Account tier is 'anonymous'",
        }
    if operation == "following":
        if not settings.configured:
            return requires_login()
        # Reached only when a cookie is set. Kept deliberately minimal so a
        # broken cookie fails loudly instead of returning fake data.
        return {
            "success": False,
            "error": "Following feed endpoint requires a working logged-in session; "
            "the configured cookie could not be verified.",
            "error_type": "auth_required",
            "message": "Following feed requires a verified logged-in session.",
            "suggestions": ["Confirm BILIBILI_COOKIE is a fresh logged-in SESSDATA."],
        }
    if operation == "favorites":
        if not settings.configured:
            return requires_login()
        return {
            "success": False,
            "error": "Favorites endpoint requires a working logged-in session; "
            "the configured cookie could not be verified.",
            "error_type": "auth_required",
            "message": "Favorites requires a verified logged-in session.",
            "suggestions": ["Confirm BILIBILI_COOKIE is a fresh logged-in SESSDATA."],
        }
    return {
        "success": False,
        "operation": operation,
        "error": f"unknown operation {operation}",
        "error_type": "validation",
        "message": f"unknown operation {operation}",
    }

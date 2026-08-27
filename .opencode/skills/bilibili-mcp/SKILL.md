---
name: bilibili-mcp
description: Tool-awareness for the Bilibili content-intelligence bridge. Load when working on or with bilibili-mcp.
---

# Bilibili MCP

Search, rank and summarise the Chinese video platform Bilibili via 10 MCP
tools. Anonymous tier works without an account; account tier needs a +86
login cookie.

## Before starting work

1. See what is trending: `bilibili_explore(operation="trending", limit=10)`
2. Pull a video's transcript: `bilibili_transcript(bvid="BV...")`

## At end of work

- Reuse cached results; never re-fetch the same video twice in a session
- If a transcript is unavailable or login-gated, say so - never fabricate it

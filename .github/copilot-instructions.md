# bilibili-mcp - GitHub Copilot instructions

Tool-awareness context for the Bilibili content-intelligence bridge.

You can search, rank and summarise the Chinese video platform Bilibili via
10 MCP tools. Anonymous tier works without an account; account tier needs a
+86 login cookie.

**Before starting work:**
1. See what is trending: `bilibili_explore(operation="trending", limit=10)`
2. Pull a video's transcript: `bilibili_transcript(bvid="BV...")`

**At end of work, keep it clean:**
- Reuse cached results; never re-fetch the same video twice in a session
- If a transcript is unavailable or login-gated, say so - never fabricate it

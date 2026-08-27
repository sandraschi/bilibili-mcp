# bilibili-expert

How to use bilibili-mcp well: discovery, video intel, and transcript summarisation.

## What this server does

Bilibili (B站) is China's largest video platform. This MCP bridges its public
web APIs so an agent can search, rank, inspect and - crucially - read a
video's auto-subtitle text to summarise or translate it. It does **not** play
video; it returns metadata, lists and transcripts.

## Two tiers

| Tier | Unlocked by | Tools |
|------|-------------|-------|
| Anonymous (default) | nothing | explore, search, video, transcript |
| Account | `BILIBILI_COOKIE` (+86 login) | account (following, favorites) |

The account tier needs a logged-in +86 Bilibili account. See docs/ONBOARDING.md.
Until then, account tools return an honest `requires_login` state - never fakes.

## Workflows

### 1. What is trending
```
bilibili_explore(operation="trending", limit=10)
bilibili_explore(operation="hot_search", limit=10)
```

### 2. Summarise a video without watching it
```
bilibili_video(operation="info", bvid="BV...")   # metadata + stats
bilibili_transcript(bvid="BV...")                # subtitle text
# then summarise the transcript (or call /api/summarize)
```

### 3. Search for content
```
bilibili_search(operation="video", keyword="微积分")
bilibili_search(operation="user", keyword="罗翔", limit=5)
```

## Rate-limit etiquette

Bilibili aggressively rate-limits scrapers. Default page sizes are small and
results are TTL-cached (default 10 min). If you get a `rate_limited` /
-412 error, slow down, reuse cached results, or set a cookie to raise the
budget. Never hammer the same endpoint repeatedly in a session.

## Honesty rules

- Never invent views/stats - report exactly what the API returned.
- If subtitles are unavailable or login-gated, say so - do not fabricate a
  transcript.
- Account-tier data (following feed, favorites) requires real auth; there is
  no mock data.

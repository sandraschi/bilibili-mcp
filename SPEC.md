# bilibili-mcp - Feature Spec

## What / why

Content-intelligence bridge for Bilibili (B站), China's largest video
platform. Search, trending, video intel, and transcript summarisation. The
core value is reading a video's auto-subtitle track as plain text so an LLM
can summarise or translate Bilibili content without watching it. No video
playback, no upload/comment automation.

## Tiers

| Tier | Auth | Tools | Status |
|------|------|-------|--------|
| Anonymous | none | explore, search, video, transcript, help, prefab | **shipped** |
| Account | `BILIBILI_COOKIE` (+86) | account (status, following, favorites) | status shipped; following/favorites honest requires_login until a real cookie exists |

## Tool surface

1. `bilibili_explore` - trending / rank / hot_search (anonymous)
2. `bilibili_search` - video / user (may need cookie past risk control)
3. `bilibili_video` - info / comments / pages (anonymous)
4. `bilibili_transcript` - subtitle text (anonymous; login-gated on some videos)
5. `bilibili_account` - status / following / favorites (following/favorites auth-gated)
6. `bilibili_help`, `bilibili_shutdown`
7. `show_bilibili_trending_card`, `show_bilibili_status_card`, `show_bilibili_cache_card` (Prefab)

## Why not a third-party bilibili library

Bilibili has no stable public REST contract and aggressively rate-limits
scrapers. A thin httpx client against the well-known web-interface endpoints
is more maintainable and honest than a fragile third-party wrapper, and keeps
dependencies minimal.

## Deferred / honest-limits

- **following / favorites**: blocked on a real +86 login. Until then they
  return `requires_login` - not stubs, declared states. Wiring them fully is
  the next stage once the user has a number.
- **Risk control (search, some transcripts)**: anonymous mode may be
  -412-blocked. Mitigation is a cookie + slow, cached access; documented, not
  hidden.
- **Full playback / danmaku streaming**: out of scope (content intelligence,
  not a player).

## Ports

Backend 11185, frontend 11186 (registered in WEBAPP_PORTS.md).

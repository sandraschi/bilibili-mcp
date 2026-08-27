# Tools - bilibili-mcp

## MCP tools

All tools return a structured dict: `{"success": bool, "message": str, ...}`.
On failure they include `error`, `error_type`, and `suggestions`.

### bilibili_explore

Discovery surfaces (all anonymous).

| Operation | Params | Returns |
|-----------|--------|---------|
| `trending` | `limit` (1-50) | popular feed: `data[]` of slim videos |
| `rank` | `rid`, `limit` | all-region ranking (rid: 0 all, 1 anime, 3 music, 4 game, 5 entertainment, 36 knowledge, 160 fashion) |
| `hot_search` | `limit` | trending search keywords: `data[]` of `{keyword, heat}` |

### bilibili_search

| Operation | Params | Notes |
|-----------|--------|-------|
| `video` | `keyword`, `limit` | searches video titles |
| `user` | `keyword`, `limit` | searches creators |

May hit risk control anonymously (-412). Returns an actionable error with a
suggestion to set a cookie.

### bilibili_video

| Operation | Params | Returns |
|-----------|--------|---------|
| `info` | `bvid` / `aid` | full metadata + stats block |
| `comments` | `bvid`, `limit` | hot top comments |
| `pages` | `bvid` | multi-part list (first part cid feeds transcript) |

### bilibili_transcript

`bvid`, `part_index` (1-based). Fetches a video's auto-subtitle track and
returns it as plain text for summarisation. Returns an honest error if no
subtitles exist or they are login-gated.

### bilibili_account

| Operation | Notes |
|-----------|-------|
| `status` | always works; reports tier anonymous/account |
| `following` | requires login; returns requires_login when logged out |
| `favorites` | requires login; returns requires_login when logged out |

### Support tools

- `bilibili_help(topic)` - self-description + tool list.
- `bilibili_shutdown(confirm)` - graceful shutdown (needs `confirm=True`).
- `show_bilibili_trending_card(limit)` - Prefab in-chat card (app=True).
- `show_bilibili_status_card()` - Prefab status card.
- `show_bilibili_cache_card()` - Prefab cache card (clears the cache).

## REST endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/health` | liveness + tier + version |
| GET | `/api/capabilities` | feature gating for the webapp |
| GET | `/api/tools` | registered tool names |
| GET | `/api/skills` | registered skills |
| GET | `/api/dashboard` | KPIs for the Dashboard page |
| GET | `/api/explore/trending` | trending feed |
| GET | `/api/explore/rank` | ranking |
| GET | `/api/explore/hot_search` | hot search keywords |
| GET | `/api/search?keyword=&operation=` | video/user search |
| GET | `/api/video/info?bvid=` | video metadata |
| GET | `/api/video/comments?bvid=` | video comments |
| GET | `/api/video/transcript?bvid=` | transcript text |
| POST | `/api/translate` | zh->en via local LLM (glossary fallback) |
| POST | `/api/summarize` | summarise a transcript via local LLM |
| GET | `/api/account/status` | account tier status |
| GET | `/api/logs` | ring-buffer log tail |
| POST | `/api/shutdown` | graceful self-termination |

## Prompts

- `bilibili_research` - discover trending + summarise a transcript.
- `bilibili_briefing` - produce a short trend briefing.

## Resources

- `skill://bilibili-expert/SKILL.md` - the bilibili-expert skill.

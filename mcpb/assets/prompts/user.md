# bilibili-mcp User Guide

Welcome to bilibili-mcp, a content-intelligence bridge for Bilibili, the
Chinese video platform. This server does not play videos. It retrieves
metadata, lists, rankings, and transcripts so that you, or an AI agent, can
search, rank, and summarise Bilibili content without watching it. This guide
teaches you everything you need: installation, configuration, ten step-by-step
tutorials, a complete API reference, a troubleshooting guide, and an FAQ.

If you are an end user, read from the top. If you are an AI agent consuming
this server, the tutorials and API reference are the operational core you need
to memorise. Everything here uses ASCII hyphens only; there are no em dashes in
this document by design.

## 1. What bilibili-mcp does

Bilibili (B站) is China's largest long-form video community. It hosts anime,
games, knowledge, science, food, vlog, and entertainment content, with a
signature culture of danmaku (live bullet comments). Because Bilibili is
primarily a Chinese platform, the richest searches use Chinese keywords, though
English terms work too.

bilibili-mcp bridges this content to you as structured data:

- Trending feeds, region rankings, and hot search keywords.
- Video metadata: title, author, upload time, view counts, danmaku, likes,
  coins, favourites, shares.
- Hot top comments for community sentiment.
- Multi-part page lists for videos split across episodes.
- Auto-subtitle transcripts, ideal for summarising the spoken content.
- Account-tier personal data (following, favorites) when you provide a valid
  +86 login cookie.

The server also exposes a webapp and a set of REST endpoints, and it can
summarise or translate content using a local LLM.

## 2. Access tiers

There are two tiers. Understanding them prevents most confusion.

### 2.1 Anonymous tier

No account, no cookie. This is the default and it powers the majority of the
tool surface:

- bilibili_explore (trending, rank, hot_search)
- bilibili_search (video, user)
- bilibili_video (info, comments, pages)
- bilibili_transcript
- bilibili_help, bilibili_shutdown
- The three show_* Prefab cards

Most workflows never need an account. Search, trending, ranking, and
summarisation all work anonymously.

### 2.2 Account tier

Set the environment variable BILIBILI_COOKIE to a valid session cookie from a
Bilibili account logged in with a Chinese +86 mobile number. This unlocks:

- bilibili_account operation following
- bilibili_account operation favorites

These two operations refuse to run without real auth. They return an honest
requires_login state when the cookie is missing, invalid, or expired. There is
no mock data and no fake lists. If you want these features, you must provide a
real cookie.

## 3. Installation

The server is a Python FastMCP server managed with uv. Installation is minimal.

### 3.1 Install with uv

Make sure you have uv installed, then from the repository root run:

    uv sync

This creates a virtual environment and installs all dependencies exactly as
pinned. If you are on a machine without uv, install it first (uv is a fast
Python package and project manager).

### 3.2 Run the server (stdio)

To run the MCP server in stdio mode (the default for MCP clients):

    uv run python server.py

Most MCP clients (Claude Desktop, and other MCP hosts) will launch this for
you. The command above is what a client, or a shell, uses to start it.

### 3.3 Run the server with the webapp

If you want the webapp and the REST API alongside the MCP server, use the
startup scripts:

    .\start.ps1

This will start the backend on port 11185 and the frontend on port 11186, and
open the dashboard in your browser. The backend serves the REST endpoints
documented later in this guide.

### 3.4 Verify it is running

Open your browser to http://127.0.0.1:11185/api/health. A healthy server
returns a JSON liveness response. The dashboard, when the webapp is running,
shows trending content and the server status.

## 4. Configuration

All configuration is via environment variables. There is no config file to edit
by hand unless you create an .env for convenience.

### 4.1 Environment variables

- BILIBILI_COOKIE (optional): A valid Bilibili session cookie from a +86 login
  account. Enables the account tier. Leave unset to stay anonymous.
- BILIBILI_API_BASE (default https://api.bilibili.com): The Bilibili API base
  URL. Override only when proxying or using a mirror.
- BILIBILI_LLM_BASE_URL (default http://127.0.0.1:11434/v1): OpenAI-compatible
  base URL for the local LLM used by /api/summarize and /api/translate.
  Defaults to a local Ollama instance.
- BILIBILI_LLM_MODEL (default qwen2.5:7b): The local LLM model for
  summarisation and translation.
- BILIBILI_CACHE_TTL (default 600): Seconds that API responses are cached.
- BILIBILI_BACKEND_PORT (default 11185): Backend port.
- BILIBILI_FRONTEND_PORT (default 11186): Frontend port.

### 4.2 Set the account cookie

On PowerShell:

    $env:BILIBILI_COOKIE = "SESSDATA=YOUR_VALUE; bili_jct=YOUR_VALUE"

On cmd:

    set BILIBILI_COOKIE=SESSDATA=YOUR_VALUE; bili_jct=YOUR_VALUE

The cookie must come from an account that logged in with a +86 phone number.
Cookies expire; when following or favorites stop working, refresh the cookie.

### 4.3 Configure the local LLM

Summarisation and translation need a local OpenAI-compatible LLM. The defaults
point at Ollama on localhost with qwen2.5:7b. If you run Ollama with that model
you need no configuration. Otherwise set BILIBILI_LLM_BASE_URL and
BILIBILI_LLM_MODEL to match your setup.

### 4.4 Tune the cache

Bilibili aggressively rate-limits scrapers. A higher BILIBILI_CACHE_TTL (for
example 900 or 1200) reduces API pressure and improves reliability, at the cost
of slightly older data. Trending and rankings change slowly; 600 is a sensible
default, and larger values are fine for most uses.

## 5. Tool reference

The server exposes ten MCP tools. This section is the definitive reference.

### 5.1 bilibili_explore

Discover what is popular, without an account.

- operation (required): trending | rank | hot_search.
- limit (optional): number of items (keep 5-20).
- rid (optional): region id for rank. 0 all, 1 anime, 3 music, 4 game,
  5 entertainment, 36 knowledge, 160 fashion.

Returns {"success": bool, "operation": str, "data": [], "count": int}.

### 5.2 bilibili_search

Search videos or users by keyword.

- operation (required): video | user.
- keyword (required): the search term. Chinese keywords work best.
- limit (optional): max results.

Returns {"success": bool, "operation": str, "data": [], "count": int}.

Note: search can trip risk control anonymously. See the troubleshooting
section for the -412 code.

### 5.3 bilibili_video

Get details on a single video.

- operation (required): info | comments | pages.
- bvid (optional): the BVxxxxxxx id.
- aid (optional): the numeric archive id.
- limit (optional): number of comments for the comments operation.

Provide either bvid or aid. bvid is preferred.

- info: metadata and statistics.
- comments: hot top comments.
- pages: the multi-part list.

Returns {"success": bool, "operation": str, "data": {...}|[], ...}.

### 5.4 bilibili_transcript

Fetch auto-subtitle text of a video.

- bvid (required): the video id.
- part_index (optional): which part for multi-part videos.

Returns {"success": bool, "data": {"bvid", "cid", "lang", "text",
"word_count"}}.

Honesty: many videos have no subtitles, or they are login-gated. If text is
empty, the server reports that honestly. Never assume a transcript exists.

### 5.5 bilibili_account

Account-gated personal data.

- operation (required): status | following | favorites.
- mid (optional): user id.

- status: always works, returns a tier report.
- following: requires the account tier.
- favorites: requires the account tier.

Without valid auth, following and favorites return an honest requires_login
state. No mock data.

### 5.6 bilibili_help

Self-description and tool list.

- topic (optional): a specific topic for help.

Useful at the start of a session to confirm capabilities.

### 5.7 bilibili_shutdown

Graceful shutdown.

- confirm (required): must be true to shut down.

Only call with explicit user intent. This stops the server.

### 5.8 show_bilibili_trending_card

Prefab UI card showing trending videos.

- limit (optional): how many items to show.

### 5.9 show_bilibili_status_card

Prefab status card: health, tier, configuration. No parameters.

### 5.10 show_bilibili_cache_card

Prefab cache card: cache statistics and a clear action. No parameters.

## 6. Tutorials

Ten step-by-step tutorials covering the most common workflows. Each is concrete
and reproducible.

### Tutorial 1: Find what is trending on Bilibili

Goal: See what is popular right now.

1. Call bilibili_explore with operation trending and limit 10.
2. Read the returned list of videos.
3. For any video that looks interesting, note its bvid and title.
4. Optionally call bilibili_video with operation info and that bvid to get full
   statistics.
5. If the user wants a visual overview, call show_bilibili_trending_card with a
   small limit.

This answers "what is hot on Bilibili right now?" in seconds.

### Tutorial 2: Find the top anime or knowledge videos

Goal: See the weekly ranking for a specific category.

1. Decide the category. Anime is rid 1, knowledge is rid 36, music is rid 3,
   games are rid 4, entertainment is rid 5, fashion is rid 160.
2. Call bilibili_explore with operation rank, rid 1 (for anime), and limit 10.
3. Compare several categories by repeating with different rid values.
4. Present the top items with titles and bvids.

This is ideal for "what are the top anime this week?" and similar questions.

### Tutorial 3: Summarise a video transcript

Goal: Understand the spoken content of a video without watching it.

1. Call bilibili_video with operation info and the bvid to get title and
   metadata.
2. Call bilibili_transcript with the same bvid.
3. Check the returned word_count and text.
4. If the text is present, summarise it into a concise set of key points.
5. If the text is empty (no subtitles, or login-gated), report that honestly.
   Offer the title and hot comments as an alternative basis.

This is the flagship workflow: "summarise this video".

### Tutorial 4: Search for content

Goal: Find videos about a topic.

1. Choose a keyword. For a Chinese topic use the Chinese term. Example:
   微积分 for calculus, 罗翔 for the law professor, 美食 for food, 知识 for
   knowledge, 科技 for technology.
2. Call bilibili_search with operation video and keyword 微积分, limit 10.
3. Review the results and pick relevant bvids.
4. For creators, call bilibili_search with operation user and the creator name.
5. Drill into any video with bilibili_video info or transcript.

This answers "find videos about X".

### Tutorial 5: Translate a Bilibili title or description

Goal: Turn a Chinese title into an English gloss.

1. Get a video title from an explore or search result.
2. Send the Chinese title to the /api/translate REST endpoint, or use your
   summarisation path with a translation instruction.
3. Present the original title plus the English gloss.

This makes Bilibili content accessible to non-Chinese speakers. Keep the
original Chinese alongside the translation.

### Tutorial 6: Compare two videos

Goal: Decide which of two videos is more popular or worth watching.

1. Call bilibili_video with operation info for each bvid.
2. Compare view counts, likes, danmaku, coins, favourites, and upload time.
3. Also compare transcript word_count if you fetched transcripts, as a proxy
   for depth.
4. Present a side-by-side comparison and a recommendation with reasons.

This answers "which of these is better?" with real numbers, not guesses.

### Tutorial 7: Work around risk control

Goal: Get results despite Bilibili rate limits.

1. Keep limits small (5-10) on every call.
2. Prefer cached data. If you already fetched something recently, reuse it
   instead of refetching.
3. Space out multiple fetches instead of bursting them.
4. If you hit a -412 error, stop retrying immediately. Wait, rely on the cache,
   and only then retry once with a smaller limit.
5. If the problem persists, tell the user that setting a valid BILIBILI_COOKIE
   (account tier) reduces these blocks.

This is the discipline that keeps the server usable.

### Tutorial 8: Set up the account tier

Goal: Unlock following and favorites.

1. Log into Bilibili in a browser with a Chinese +86 account.
2. Extract the session cookie (SESSDATA and related values).
3. Set the BILIBILI_COOKIE environment variable.
4. Restart the server.
5. Call bilibili_account with operation status to confirm the tier flipped to
   account.
6. Test with operation following or favorites.

Without a valid cookie, these return requires_login. With one, they return real
data.

### Tutorial 9: Use the Prefab cards

Goal: Give the user a rich visual overview.

1. For a trending overview, call show_bilibili_trending_card with a small limit.
2. For a health check, call show_bilibili_status_card.
3. For cache insight, call show_bilibili_cache_card.

Cards are presentation. The data behind them always comes from real tool
results, never invented numbers.

### Tutorial 10: Use the REST summarize endpoint

Goal: Summarise content via the HTTP API.

1. Ensure the local LLM is running (default Ollama at 127.0.0.1:11434).
2. Fetch a transcript via /api/video/transcript, or via bilibili_transcript.
3. POST the transcript text to /api/summarize.
4. Read the returned summary.
5. If the LLM is unreachable, the endpoint reports that honestly.

This is the programmatic path for batch summarisation outside the MCP client.

## 7. API reference

The REST API is served by the backend on port 11185. All endpoints return JSON.

### 7.1 Endpoint table

| Method | Path                     | Description                          |
|--------|--------------------------|--------------------------------------|
| GET    | /api/health              | Liveness probe                       |
| GET    | /api/capabilities        | Server capabilities                  |
| GET    | /api/tools               | Tool inventory                       |
| GET    | /api/skills              | Skill / guidance content             |
| GET    | /api/dashboard           | Webapp dashboard data                |
| GET    | /api/explore/trending    | Trending feed                        |
| GET    | /api/explore/rank        | Ranking board                        |
| GET    | /api/explore/hot_search  | Hot search keywords                  |
| GET    | /api/search              | Search results                       |
| GET    | /api/video/info          | Video metadata                       |
| GET    | /api/video/comments      | Video comments                       |
| GET    | /api/video/transcript    | Video transcript                     |
| GET    | /api/translate           | Translate text via local LLM         |
| GET    | /api/summarize           | Summarise text via local LLM         |
| GET    | /api/account/status      | Account tier report                  |
| GET    | /api/logs                | Recent server logs                   |
| GET    | /api/shutdown            | Graceful shutdown                    |

### 7.2 Example requests

Health:

    GET http://127.0.0.1:11185/api/health

Example response:

    {"success": true, "status": "ok"}

Trending:

    GET http://127.0.0.1:11185/api/explore/trending?limit=10

Rank:

    GET http://127.0.0.1:11185/api/explore/rank?rid=1&limit=10

Hot search:

    GET http://127.0.0.1:11185/api/explore/hot_search

Search:

    GET http://127.0.0.1:11185/api/search?keyword=微积分&limit=10

Video info:

    GET http://127.0.0.1:11185/api/video/info?bvid=BV1GJ411x7h7

Video comments:

    GET http://127.0.0.1:11185/api/video/comments?bvid=BV1GJ411x7h7&limit=10

Video transcript:

    GET http://127.0.0.1:11185/api/video/transcript?bvid=BV1GJ411x7h7

Translate:

    GET http://127.0.0.1:11185/api/translate?text=微积分入门

Summarize:

    GET http://127.0.0.1:11185/api/summarize?text=<transcript>

Account status:

    GET http://127.0.0.1:11185/api/account/status

Logs:

    GET http://127.0.0.1:11185/api/logs

## 8. Troubleshooting

### 8.1 -412 risk control error

Symptom: A call returns a -412 code, or results that are empty when data is
expected.

Cause: Bilibili flagged your traffic as automated.

Fix: Slow down, stop tight retries, rely on the cache, and use smaller limits.
If it persists, set a valid BILIBILI_COOKIE (account tier) to reduce blocks.

### 8.2 Empty transcript

Symptom: bilibili_transcript returns empty text.

Cause: The video has no auto-subtitles, or they are login-gated, or the
language is undetected.

Fix: Report honestly. Offer the title, description, and hot comments as
alternatives. Some videos simply have no subtitles.

### 8.3 requires_login on account operations

Symptom: following or favorites return requires_login.

Cause: No valid BILIBILI_COOKIE, or the cookie is expired or invalid.

Fix: Obtain a fresh cookie from a +86 login account, set BILIBILI_COOKIE, and
restart. Verify with bilibili_account operation status.

### 8.4 Summarize or translate reports the LLM is down

Symptom: /api/summarize or /api/translate returns an unreachable error.

Cause: The local LLM is not running, or BILIBILI_LLM_BASE_URL /
BILIBILI_LLM_MODEL point at the wrong place.

Fix: Start Ollama (or your LLM server), confirm the model name, and check the
two variables.

### 8.5 Server does not start

Symptom: uv run python server.py fails at import time.

Cause: Dependencies not installed, or a port conflict.

Fix: Run uv sync first. Confirm ports 11185 and 11186 are free (check
BILIBILI_BACKEND_PORT and BILIBILI_FRONTEND_PORT). Check the error message for
a missing module and re-sync.

### 8.6 Webapp does not open

Symptom: http://127.0.0.1:11186 does not load.

Cause: The frontend did not start, or a port conflict.

Fix: Confirm the frontend process is running. Free the port and restart via
start.ps1. The backend must be up on 11185 for the dashboard to show data.

### 8.7 Stale data in results

Symptom: Trending or rankings look old.

Cause: The TTL cache is serving cached data, which is expected.

Fix: If you need fresh data, raise confidence by clearing the cache (use
show_bilibili_cache_card, or restart the server). Prefer cache hits for routine
checks.

### 8.8 Rate limits while running many searches

Symptom: A burst of searches starts failing with -412.

Cause: Too many requests too quickly.

Fix: Reduce the number of calls, increase BILIBILI_CACHE_TTL, and space out
requests. Batch what you can into single calls.

## 9. FAQ

### Q1. Do I need an account to use bilibili-mcp?

No. The anonymous tier powers trending, search, video metadata, comments, pages,
and transcripts. Only following and favorites need the account tier.

### Q2. What is the account tier and why do I need a +86 login?

Bilibili personal-data endpoints require a logged-in session. A Chinese +86
mobile login produces the cookie that unlocks following and favorites. Without
it, those two operations return requires_login.

### Q3. Can I watch videos through bilibili-mcp?

No. The server returns metadata, lists, and transcripts. It never plays video.
That is by design: it is a content-intelligence bridge, not a player.

### Q4. Why are some video summaries not possible?

Because not every video has auto-subtitles. Without a transcript there is no
spoken content to summarise. In that case the server says so and offers the
title and comments instead. It never fakes a transcript.

### Q5. What do the rid values mean?

0 is all regions, 1 anime, 3 music, 4 game, 5 entertainment, 36 knowledge, and
160 fashion. They only apply to the rank operation.

### Q6. Can I search in English?

Yes. Chinese keywords give richer results because Bilibili is a Chinese
platform, but English and mixed-language search terms are supported.

### Q7. What is the -412 error?

It is Bilibili's risk-control response when traffic looks automated. The fix is
to slow down, use the cache, and optionally add a cookie.

### Q8. Why does trending not update every minute?

The TTL cache (default 600 seconds) serves cached data to protect you from rate
limits. Trending changes slowly, so cached results are usually fine. Clear the
cache if you need fresh data.

### Q9. What ports does the server use?

Backend on 11185 and frontend on 11186. Configure with BILIBILI_BACKEND_PORT
and BILIBILI_FRONTEND_PORT.

### Q10. What LLM does summarisation use?

By default a local Ollama instance at http://127.0.0.1:11434/v1 running model
qwen2.5:7b. Configure with BILIBILI_LLM_BASE_URL and BILIBILI_LLM_MODEL.

### Q11. Is the view count reliable?

Only if the API returned it. The server never invents statistics. If a number
is absent from the response, you will not see a fabricated one.

### Q12. What is the cache for?

It stores recent API responses for BILIBILI_CACHE_TTL seconds. Because Bilibili
rate-limits hard, the cache is what keeps the server usable. Show the cache card
to inspect it.

### Q13. How do I check the current tier?

Call bilibili_account with operation status. It returns a tier report showing
whether you are anonymous or account-tier and the cookie health.

### Q14. How do I fix a stale cache?

Clear the cache via show_bilibili_cache_card, or restart the server. Then the
next fetch will be fresh.

### Q15. What are the Prefab cards for?

show_bilibili_trending_card, show_bilibili_status_card, and
show_bilibili_cache_card render rich in-chat visual cards instead of raw JSON.
They are presentation only; the numbers always come from real tool results.

### Q16. Can I use the server without an MCP client?

Yes. The REST API on port 11185 gives you the same capabilities over HTTP,
including translate and summarize endpoints.

### Q17. What should I do if I get empty search results?

Treat it as a possible rate-limit signal if it happens right after a burst.
Slow down and retry once with a smaller limit. If it persists, consider the
account tier.

### Q18. Does the server store my cookie?

The cookie is read from the environment at runtime for outbound requests. Treat
BILIBILI_COOKIE as a secret: do not commit it, do not paste it into logs, and
use an .env that is gitignored.

### Q19. Can I run multiple servers on different ports?

Yes. Set distinct BILIBILI_BACKEND_PORT and BILIBILI_FRONTEND_PORT values for
each instance.

### Q20. Where do I get help about a specific tool?

Call bilibili_help, optionally with a topic. It returns the tool inventory and
self-description.

## 9.1 Query cookbook

A set of ready-to-use intent-to-action mappings. When a user asks one of these,
route to the listed tools in order.

- "What is trending on Bilibili right now?" -> bilibili_explore trending.
- "What are the top anime this week?" -> bilibili_explore rank rid 1.
- "What is hot in the knowledge area?" -> bilibili_explore rank rid 36.
- "What music is popular?" -> bilibili_explore rank rid 3.
- "What are people searching for?" -> bilibili_explore hot_search.
- "Find videos about calculus." -> bilibili_search video keyword 微积分.
- "Find videos about law or Luo Xiang." -> bilibili_search video keyword 罗翔.
- "Find food content." -> bilibili_search video keyword 美食.
- "Find a creator who posts tech." -> bilibili_search user.
- "Summarise this video." -> bilibili_video info, then bilibili_transcript.
- "What is this video about?" -> bilibili_transcript, then summarise.
- "Is this video worth watching?" -> bilibili_video info, compare view and
  engagement, plus comments for sentiment.
- "What are people saying about it?" -> bilibili_video comments.
- "Is this a series? Walk me through it." -> bilibili_video pages.
- "Compare these two videos." -> bilibili_video info for each.
- "Translate this title." -> translate endpoint or translation instruction.
- "Show me what is hot." -> show_bilibili_trending_card.
- "Is the server healthy?" -> show_bilibili_status_card.
- "What is in the cache?" -> show_bilibili_cache_card.
- "Who do I follow?" -> bilibili_account following (needs account tier).
- "What are my favourites?" -> bilibili_account favorites (needs account tier).

### 9.2 Tier-aware routing

Choose the right tier before acting:

- Anonymous tier handles discovery, ranking, search, metadata, comments, pages,
  transcripts, and all cards. Use it for almost everything.
- The account tier is required only for following and favorites. Do not reach
  for a cookie for a task that runs fine anonymously.
- Before calling following or favorites, confirm the tier with bilibili_account
  operation status. If it is anonymous, tell the user the call will return
  requires_login unless they set BILIBILI_COOKIE.

### 9.3 Request budgeting

Treat every call as a request against a rate-limited API. Budget accordingly:

- Prefer limits of 5 to 10 for exploration, and 10 to 20 only when the user
  explicitly wants a long list.
- Fetch a transcript only for videos the user genuinely cares about. Do not
  fetch transcripts for an entire trending feed.
- When a workflow needs several videos, gather all metadata first in one pass,
  then decide which transcripts to fetch. This avoids wasting calls.
- Reuse anything already in the cache. Re-fetching trending data you pulled
  minutes ago is wasteful.
- If a call fails, do not immediately retry. Re-read the plan, drop non-
  essential calls, and proceed with what is left.

## 9.4 Known limitations

Be transparent about what this server cannot do:

- No video playback. The server returns data, never streams or downloads video.
- No transcript for every video. Subtitle availability depends on the uploader
  and on login state. Some content has no subtitles at all.
- Personal data is gated. following and favorites need a real +86 login cookie;
  there is no mock or demo mode for them.
- Anonymous search can be rate-limited. Heavy or rapid searching returns -412
  risk-control errors.
- Translation and summarisation depend on the local LLM. If it is not running,
  those endpoints report an unreachable error rather than returning a result.

## 10. Best practices

- Keep request limits small (5-20). It is easier to fetch more later than to
  trip rate limits.
- Prefer cached data. Reuse recent responses before refetching.
- Space out multi-call workflows. Do not burst.
- Report honestly. Never invent statistics, transcripts, or account data.
- Keep original Chinese titles and add English glosses when useful.
- For following and favorites, confirm the account tier is active first via
  bilibili_account status.

## 10.1 A worked end-to-end example

Suppose the user asks: "What is the top knowledge video this week, and can you
summarise it?" Here is the exact sequence you should run.

1. Call bilibili_explore with operation rank, rid 36, and limit 10. This is the
   weekly knowledge ranking. From the result, note the number one video's bvid
   and title.
2. Call bilibili_video with operation info and that bvid. Record the view,
   like, coin, danmaku, and favourite counts so you can describe the video's
   footprint accurately.
3. Call bilibili_transcript with that bvid. If the transcript returns text,
   summarise it into a few key points.
4. Present the result: the video title, its bvid, its key statistics, and a
   summary of its spoken content.

If step 3 returns empty text, do not invent a summary. Instead report that the
video has no available subtitles, present the title and statistics, and offer
the hot comments as an alternative signal of what the video covers. This single
example ties together ranking, metadata, transcripts, and honest failure
handling, and it is the pattern behind most real requests.

## 10.2 Security notes

A few hygiene rules keep your use of the server safe.

- Treat BILIBILI_COOKIE as a secret. It grants access to your account data.
  Never commit it to version control, never paste it into logs, and store it in
  an .env file that is gitignored rather than in shell history.
- Do not use a shared or public cookie. Your following and favourites are
  personal.
- The local LLM defaults to localhost, so transcript text stays on your
  machine. If you change BILIBILI_LLM_BASE_URL to a remote endpoint, be aware
  that transcript text will be sent there.
- Do not hammer the Bilibili API. Rate limits exist for a reason, and heavy
  scraping can get an IP throttled. The cache exists specifically to keep
  request volume low.

## 11. Summary

bilibili-mcp turns Bilibili into searchable, rankable, summarisable data. Use
the anonymous tier for discovery, ranking, metadata, and transcripts. Use the
account tier only when you genuinely need personal data. Respect rate limits,
lean on the cache, and always be honest about what the API returned and what it
did not. With these habits you can search, compare, and summarise Bilibili
content quickly and reliably, without ever pressing play.

# Troubleshooting - bilibili-mcp

## Symptom -> fix

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `-412` / "risk control blocked" | Bilibili thinks you are a bot | Slow down, reuse cached results, or set `BILIBILI_COOKIE` to raise the budget. Never loop the API. |
| `-101` "not logged in" | endpoint needs auth | Set a logged-in `BILIBILI_COOKIE`. |
| Search returns nothing / blocked | anonymous risk control | Retry after a delay or configure a cookie. |
| "No subtitle tracks available" | creator disabled captions, or transcript login-gated | Nothing to fix - some videos have no subtitles. With a cookie, some gated ones unlock. |
| Transcript empty after found | subtitle fetch returned no text | Rare parse issue; retry once. |
| Backend not healthy after start | port in use or `.env` issue | `start.ps1` clears the port; check `data/backend.log`. |
| `summarize` returns not-configured | no reachable local LLM | Start Ollama (`ollama serve`) or set `BILIBILI_LLM_BASE_URL` / `BILIBILI_LLM_MODEL`. |
| Webapp shows MOCK content | no `BILIBILI_COOKIE` set | That is the expected mock-until-onboarded state. Set a cookie for account tier. |
| Account tools say requires_login | logged out | Complete onboarding (needs +86) and set `BILIBILI_COOKIE`. |

## Common errors

- **`error_type: rate_limited`** - you hit Bilibili's anti-bot. Back off.
- **`error_type: auth_required`** - endpoint needs a login cookie.
- **`error_type: not_found`** - video has no subtitles, or bad id.
- **`error_type: network`** - could not reach `api.bilibili.com`. Check
  connectivity / VPN to reach Chinese endpoints.

## Logs

- Ring-buffer logs are exposed at `GET /api/logs` (webapp Logs page).
- `data/backend.log` captures backend stdout/stderr via `start.ps1`.

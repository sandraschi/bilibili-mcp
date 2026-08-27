# Onboarding - bilibili-mcp

## What this is for

bilibili-mcp is a content-intelligence bridge for Bilibili (B站), China's
largest video platform. It lets an agent search, rank, inspect and summarise
Bilibili videos - the killer feature is reading a video's auto-subtitle track
as plain text so an LLM can summarise or translate it. It does **not** play
video, and it does **not** automate uploading or commenting.

The good news: the core tier (explore, search, video intel, transcripts)
works **with zero setup and no account**. This onboarding is mainly about the
optional **account tier** (following feed, favorites) - which requires a
Chinese +86 phone number.

## Cost and accounts (money / CC)

| Question | Answer |
|----------|--------|
| Do I need an account? | No - anonymous tier works for explore/search/video/transcript. Only the account tier needs one. |
| Free tier? | Yes - anonymous browsing and the content-intelligence API need no account and no payment. |
| Credit card required? | No for watching; only if you buy a +86 number (an eSIM) for the account tier. |
| Ongoing cost? | Free for anonymous tier. An eSIM for the account tier is a one-off ~EUR 10-20 plus a small top-up. |
| Who bills? | CUniq / CMLink (China Mobile/Unicom resellers) if you get an eSIM. |

## Prerequisites outside this repo

- **Anonymous tier: nothing.** No account, no number, no credit card.
- **Account tier (optional):** a Chinese **+86 phone number** is the real
  blocker. Bilibili's signup is effectively locked to mainland China numbers.
  Realistic options from Europe:
  - **CUniq (China Unicom) eSIM** - deliverable to EU countries with a +86
    mainland number. Best choice from Austria. ~EUR 10-20 + top-up.
  - **CMlink (China Mobile) eSIM** - similar.
  - Virtual SMS-receive services are cheapest but Bilibili's risk control
    frequently rejects those numbers (account gets locked). Avoid.
- A working network connection to `api.bilibili.com` (some networks need a
  VPN to reach Chinese endpoints reliably).

## First-timer setup steps

1. Clone and install:
   ```powershell
   git clone https://github.com/sandraschi/bilibili-mcp
   cd bilibili-mcp
   uv sync
   ```
2. Start the stack (backend 11185 + webapp 11186):
   ```powershell
   .\start.bat
   ```
3. **Try the anonymous tier right away** - open the webapp, search a keyword
   or open a trending video, and fetch its transcript. This should work with
   no further setup.
4. **(Optional) Account tier:** if you want following/favorites or need to
   pass search risk control:
   - Get a +86 number (CUniq/CMLink eSIM), register on bilibili.com.
   - After logging in in a browser, export your `SESSDATA` cookie.
   - Put it in `.env` as `BILIBILI_COOKIE="SESSDATA=...;bili_jct=..."`.
   - Restart the backend. `bilibili_account(operation="status")` should now
     report tier `account`.

## Pitfalls

- **Search can be risk-controlled anonymously.** If you see a -412 error,
  Bilibili thinks you are a bot. Slow down, reuse cached results, or set a
  login cookie to raise the budget. Never hammer the API in a loop.
- **Subtitles are not always available.** Some creators disable captions, and
  some transcripts are login-gated. The tool returns an honest error in that
  case - it does not fabricate a transcript.
- **+86 is the real gate.** A virtual SMS number will often get the account
  locked by Bilibili's risk control. Pay for a real CUniq/CMLink eSIM.
- **No video playback.** This server returns metadata and transcripts, not
  streams. For actually watching, use the Bilibili site/app.

## Sanity check

You know onboarding worked when:

- `GET /api/health` returns `"status": "ok"` with `tool_count >= 10`.
- The webapp Dashboard shows live (non-MOCK) trending content and the red
  onboarding button is gone.
- Anonymous tier: `bilibili_explore(operation="trending")` returns real items.
- Account tier: `bilibili_account(operation="status")` reports
  `"tier": "account"`.

## Declared doubles

- **Mock-until-onboarded:** until a `BILIBILI_COOKIE` is set, the webapp
  Dashboard shows clearly badged `MOCK` sample content (fake names like Joe
  Mocky / Sandra Mockinger) that clears once `configured` is true. This is
  declared in `webapp/src/pages/Dashboard.tsx` and is not live data.
- **Account tools when logged out:** `bilibili_account` operations
  `following`/`favorites` return an explicit `requires_login` state (not
  fake data) until a working cookie is configured.
- **No LLM:** `POST /api/summarize` requires a reachable local LLM
  (Ollama). Without one it returns an explicit not-configured error, not a
  fake summary.

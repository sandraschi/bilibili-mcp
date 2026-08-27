# Bilibili (B站)

Bilibili is China's largest video-sharing platform - often called the
"YouTube of China". It is known for its culture of **danmaku** (弹幕), a
real-time scrolling comment overlay that appears directly on the video, and
for a strong ecosystem of creators (UP主) spanning anime, gaming, science,
education, music, vlogs and knowledge content.

- Maintained by: Shanghai Bilibili Technology Co., Ltd.
- Founded: 2009 (as Mikufans), rebranded Bilibili in 2010.
- Platform: web (bilibili.com), iOS/Android apps.
- Not to be confused with: **Bilibili International / BiliBili app** variants
  (an unrelated third-party media app in some app stores), or the older
  "BiliBili" video services. This repo targets the mainland
  bilibili.com platform.

## Links

- Official site: https://www.bilibili.com
- Help / support: https://www.bilibili.com/blackboard/help.html
- Wikipedia: https://en.wikipedia.org/wiki/Bilibili

## Why this matters for the MCP

Bilibili has no stable public REST contract and aggressively rate-limits
scrapers. Signup effectively requires a Chinese **+86 phone number**, which is
the main onboarding hurdle for non-mainland users. The anonymous content
surface (popular feed, rankings, video metadata, subtitles) is reachable
without an account, which is what bilibili-mcp leans on for its core tier.

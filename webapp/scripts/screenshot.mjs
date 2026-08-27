// Capture a full-page screenshot of the bilibili-mcp dashboard.
// Usage: node scripts/screenshot.mjs <outfile.png>
import { chromium } from "playwright";

const out = process.argv[2] ?? "docs/screenshots/dashboard.png";
const url = process.env.SCREENSHOT_URL ?? "http://127.0.0.1:11186/";

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
await page.goto(url, { waitUntil: "networkidle" });
await page.waitForTimeout(2500);
await page.screenshot({ path: out, fullPage: true });
console.log(`screenshot written: ${out}`);
await browser.close();

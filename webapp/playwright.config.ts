import { defineConfig } from "@playwright/test";

const BACKEND_PORT = 11185;
const FRONTEND_PORT = 11186;

export default defineConfig({
  testDir: "./e2e",
  timeout: 60000,
  retries: 1,
  use: {
    baseURL: `http://127.0.0.1:${FRONTEND_PORT}`,
    headless: true,
    screenshot: "only-on-failure",
  },
  webServer: [
    {
      command: `uv run uvicorn bilibili_mcp.server:app --host 127.0.0.1 --port ${BACKEND_PORT} --log-level warning`,
      port: BACKEND_PORT,
      cwd: "../",
      timeout: 60000,
      reuseExistingServer: true,
    },
    {
      command: `bun run dev -- --port ${FRONTEND_PORT} --host 127.0.0.1 --strictPort`,
      port: FRONTEND_PORT,
      cwd: ".",
      timeout: 60000,
      reuseExistingServer: true,
    },
  ],
});

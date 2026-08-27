import { expect, test } from "@playwright/test";

test("Fleet Audit: Dashboard renders with onboarding cue", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByTestId("dashboard")).toBeVisible();
  await expect(page.getByTestId("onboarding-cue")).toBeVisible();
  await expect(page.getByTestId("sidebar")).toBeVisible();
});

test("Fleet Audit: Settings page renders", async ({ page }) => {
  await page.goto("/settings");
  await expect(page.getByTestId("settings-page")).toBeVisible();
  await expect(page.getByTestId("settings-server")).toBeVisible();
  await expect(page.getByTestId("token-state")).toBeVisible();
});

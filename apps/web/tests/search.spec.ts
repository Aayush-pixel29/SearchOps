import { test, expect } from "@playwright/test";

test("search playground renders", async ({ page }) => {
  test.skip(!process.env.SEARCHOPS_E2E, "Start API+web and set SEARCHOPS_E2E=1");
  await page.goto("http://localhost:3000/");
  await expect(page.getByText("Search playground")).toBeVisible();
  await page.getByRole("button", { name: "Search" }).click();
  await expect(page.locator("text=/#[0-9]/").first()).toBeVisible({ timeout: 30_000 });
});

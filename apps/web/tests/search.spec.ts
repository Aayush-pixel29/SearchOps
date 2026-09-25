import { test, expect } from "@playwright/test";

test("search playground renders and executes search", async ({ page }) => {
  await page.goto("http://localhost:3000", { waitUntil: "commit" });
  await expect(page.getByText("Search playground")).toBeVisible({ timeout: 20000 });
  const btn = page.getByRole("button", { name: "Search" });
  await expect(btn).toBeEnabled({ timeout: 15000 });
  await btn.click();
  await expect(page.locator("text=/#[0-9]/").first()).toBeVisible({ timeout: 15_000 });
});

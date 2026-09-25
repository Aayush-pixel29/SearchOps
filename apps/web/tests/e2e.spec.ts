import { test, expect } from "@playwright/test";

test.describe("SearchOps End-to-End User Journey", () => {
  test("complete flow: login -> search -> results -> inspect ranking reasons", async ({ page }) => {
    // 1. Navigate to the SearchOps Dashboard
    await page.goto("http://localhost:3000", { waitUntil: "commit" });
    await expect(page.getByText("Search playground")).toBeVisible({ timeout: 20000 });

    // 2. Verify Search Input is populated and button is enabled after auth token resolves
    const searchInput = page.locator("input");
    await expect(searchInput).toHaveValue(/laptops/i, { timeout: 10000 });

    const searchButton = page.getByRole("button", { name: /search/i });
    await expect(searchButton).toBeEnabled({ timeout: 15000 });

    // 3. Execute Search
    await searchButton.click();

    // 4. Verify results appear with rank badges
    const firstHit = page.locator("button:has-text('#1')").first();
    await expect(firstHit).toBeVisible({ timeout: 15000 });

    // 5. Click the #1 ranked result to open the Ranking Inspector
    await firstHit.click();

    // 6. Verify Inspector displays "Why this result ranked" and score breakdown
    await expect(page.getByText(/Why this result ranked/i)).toBeVisible({ timeout: 10000 });
    await expect(page.getByText("BM25 / Keyword Score")).toBeVisible();
    await expect(page.getByText("Dense Semantic Cosine")).toBeVisible();
    await expect(page.getByText("Composite Score", { exact: true })).toBeVisible();
  });
});

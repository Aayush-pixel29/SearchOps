import { chromium } from "@playwright/test";
import * as path from "path";
import * as fs from "fs";

async function main() {
  const screenshotDir = path.resolve(__dirname, "../../../docs/screenshots");
  if (!fs.existsSync(screenshotDir)) {
    fs.mkdirSync(screenshotDir, { recursive: true });
  }

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();

  console.log("Capturing screenshots...");

  // 1. Search Playground (with search executed and inspector open)
  await page.goto("http://localhost:3000/");
  await page.waitForTimeout(2000);
  const searchBtn = page.getByRole("button", { name: "Search" });
  if (await searchBtn.isEnabled()) {
    await searchBtn.click();
    await page.waitForTimeout(2000);
    const hit = page.locator("button:has-text('#1')").first();
    if (await hit.isVisible()) {
      await hit.click();
      await page.waitForTimeout(1000);
    }
  }
  await page.screenshot({ path: path.join(screenshotDir, "01_search_playground.png"), fullPage: true });
  console.log("Captured: 01_search_playground.png");

  // 2. Ranking Compare
  await page.goto("http://localhost:3000/compare");
  await page.waitForTimeout(2000);
  const compareBtn = page.getByRole("button", { name: "Compare" });
  if (await compareBtn.isEnabled()) {
    await compareBtn.click();
    await page.waitForTimeout(2500);
  }
  await page.screenshot({ path: path.join(screenshotDir, "02_ranking_compare.png"), fullPage: true });
  console.log("Captured: 02_ranking_compare.png");

  // 3. Evaluation Benchmark
  await page.goto("http://localhost:3000/evaluation");
  await page.waitForTimeout(2000);
  const benchmarkBtn = page.getByRole("button", { name: "Run benchmark" });
  if (await benchmarkBtn.isEnabled()) {
    await benchmarkBtn.click();
    await page.waitForTimeout(5000);
  }
  await page.screenshot({ path: path.join(screenshotDir, "03_evaluation_benchmark.png"), fullPage: true });
  console.log("Captured: 03_evaluation_benchmark.png");

  // 4. Performance & Traces
  await page.goto("http://localhost:3000/performance");
  await page.waitForTimeout(2000);
  await page.screenshot({ path: path.join(screenshotDir, "04_performance_traces.png"), fullPage: true });
  console.log("Captured: 04_performance_traces.png");

  // 5. Document Management
  await page.goto("http://localhost:3000/documents");
  await page.waitForTimeout(2000);
  await page.screenshot({ path: path.join(screenshotDir, "05_document_catalog.png"), fullPage: true });
  console.log("Captured: 05_document_catalog.png");

  // 6. Tenant Admin
  await page.goto("http://localhost:3000/admin");
  await page.waitForTimeout(2000);
  await page.screenshot({ path: path.join(screenshotDir, "06_tenant_admin.png"), fullPage: true });
  console.log("Captured: 06_tenant_admin.png");

  await browser.close();
  console.log("All screenshots captured successfully!");
}

main().catch(console.error);

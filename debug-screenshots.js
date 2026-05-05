import { chromium } from "playwright";
import { mkdirSync } from "fs";

mkdirSync("docs/debug", { recursive: true });

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();
  await page.setViewportSize({ width: 1280, height: 800 });

  console.log("Starting debug capture...");

  try {
    console.log("1. Navigating to login...");
    await page.goto("http://127.0.0.1:5173/login", { waitUntil: "networkidle" });
    
    console.log("2. Filling credentials...");
    await page.fill("#email", "user1@test.com");
    await page.fill("#password", "password123");
    
    console.log("3. Clicking login...");
    await page.click('button[type="submit"]');
    
    console.log("4. Waiting for navigation...");
    try {
      await page.waitForURL("**/browse", { timeout: 10000 });
      console.log("Login successful, reached /browse");
    } catch {
      console.log("Navigation to /browse failed or timed out. Checking current URL...");
      console.log("Current URL:", page.url());
      await page.screenshot({ path: "docs/debug/login-failure.png" });
    }

    // Check localStorage
    const authData = await page.evaluate(() => {
      return {
        token: localStorage.getItem("token"),
        user: localStorage.getItem("user")
      };
    });
    console.log("Auth data in localStorage:", authData.token ? "Token exists" : "No token");

    console.log("5. Taking /browse screenshot...");
    await page.goto("http://127.0.0.1:5173/browse", { waitUntil: "networkidle" });
    await page.waitForTimeout(2000); // Give it extra time
    await page.screenshot({ path: "docs/debug/browse-debug.png" });
    console.log("Debug screenshots saved to docs/debug/");

  } catch {
    console.error("Debug script error");
  } finally {
    await browser.close();
  }
})();

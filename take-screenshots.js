import { chromium } from "playwright";
import { mkdirSync } from "fs";

// Create screenshot directory
mkdirSync("docs/images", { recursive: true });

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();
  await page.setViewportSize({ width: 1280, height: 800 });

  console.log("Starting screenshots...");

  try {
    // 1. Registration form
    console.log("Taking screenshot: docs/images/registration-form.png...");
    await page.goto("http://127.0.0.1:5173/register", { waitUntil: "networkidle" });
    await page.screenshot({ path: "docs/images/registration-form.png", fullPage: true });

    // 2. Login form
    console.log("Taking screenshot: docs/images/login-form.png...");
    await page.goto("http://127.0.0.1:5173/login", { waitUntil: "networkidle" });
    await page.screenshot({ path: "docs/images/login-form.png", fullPage: true });

    // 3. About page
    console.log("Taking screenshot: docs/images/about-page.png...");
    await page.goto("http://127.0.0.1:5173/about", { waitUntil: "networkidle" });
    await page.screenshot({ path: "docs/images/about-page.png", fullPage: true });

    // 4. 404 page
    console.log("Taking screenshot: docs/images/notfound-page.png...");
    await page.goto("http://127.0.0.1:5173/nonexistent-page", { waitUntil: "networkidle" });
    await page.screenshot({ path: "docs/images/notfound-page.png", fullPage: true });

    // --- Login Step ---
    console.log("Logging in for authenticated screenshots...");
    await page.goto("http://127.0.0.1:5173/login", { waitUntil: "networkidle" });
    await page.fill("#email", "user1@test.com");
    await page.fill("#password", "password123");
    await page.click('button[type="submit"]');
    
    // Wait for the login to complete and navigate to home
    await page.waitForURL("http://127.0.0.1:5173/", { timeout: 10000 });
    await page.waitForTimeout(3000); 
    console.log("Login successful!");

    const takeAuthScreenshot = async (url, path, waitForSelector = "body", action = null) => {
      console.log("Taking screenshot: " + path + "...");
      await page.goto(url, { waitUntil: "networkidle", timeout: 20000 });
      try {
        await page.waitForSelector(waitForSelector, { timeout: 10000 });
      } catch (e) {
        console.warn("Warning: Selector " + waitForSelector + " not found for " + url + ". Still taking screenshot.");
      }
      if (action) {
        await action(page);
      }
      await page.waitForTimeout(1000); // Animation buffer
      await page.screenshot({ path: path, fullPage: true });
    };

    // 5. Browse page
    await takeAuthScreenshot(
      "http://127.0.0.1:5173/browse",
      "docs/images/browse-page.png",
      ".profile-card" 
    );

    // 6. Profile edit page
    await takeAuthScreenshot(
      "http://127.0.0.1:5173/profile/edit",
      "docs/images/profile-form.png",
      "form"
    );

    // 7. Matches page
    await takeAuthScreenshot(
      "http://127.0.0.1:5173/matches",
      "docs/images/mutual-matches.png"
    );

    // 8. Search page
    await takeAuthScreenshot(
      "http://127.0.0.1:5173/search",
      "docs/images/search-page.png"
    );

    // 9. Favorites page
    await takeAuthScreenshot(
      "http://127.0.0.1:5173/favorites",
      "docs/images/favorites-page.png"
    );

    // 10. Conversations list
    await takeAuthScreenshot(
      "http://127.0.0.1:5173/messages",
      "docs/images/conversations-list.png"
    );

    // 11. Notifications page
    await takeAuthScreenshot(
      "http://127.0.0.1:5173/notifications",
      "docs/images/notifications-panel.png"
    );

    // 12. Chat window
    await takeAuthScreenshot(
      "http://127.0.0.1:5173/messages/2",
      "docs/images/chat-window.png"
    );

    // --- New Screenshots ---

    // 13. Age preferences (Search page)
    await takeAuthScreenshot(
      "http://127.0.0.1:5173/search",
      "docs/images/age-preferences.png",
      ".age-inputs"
    );

    // 14. Upload picture (Profile page)
    await takeAuthScreenshot(
      "http://127.0.0.1:5173/profile",
      "docs/images/upload-picture.png",
      ".upload-btn"
    );

    // 15. Match score explanation (Browse page)
    await takeAuthScreenshot(
      "http://127.0.0.1:5173/browse",
      "docs/images/match-score-explanation.png",
      ".match-badge"
    );

    // 16. Bookmark button (Search page)
    await takeAuthScreenshot(
      "http://127.0.0.1:5173/search",
      "docs/images/bookmark-button.png",
      ".search-form",
      async (p) => {
        // Trigger a search to show results
        await p.click(".btn-search");
        await p.waitForSelector(".btn-bookmark", { timeout: 5000 });
      }
    );

    // 17. Notification dropdown (Any page, but home is fine)
    await takeAuthScreenshot(
      "http://127.0.0.1:5173/",
      "docs/images/notification-dropdown.png",
      "header",
      async (p) => {
        // Find the avatar dropdown button and click it
        // The button has an SVG chevron down
        await p.click("header button:has(svg path[d*='M19 9l-7 7-7-7'])");
        await p.waitForSelector(".dropdown-item", { timeout: 5000 });
      }
    );

    console.log("All screenshots taken successfully!");
  } catch (error) {
    console.error("Error taking screenshots:", error);
  } finally {
    await browser.close();
  }
})();

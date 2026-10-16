import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";


test("reviews all candidates with keyboard, theme, responsive, and accessibility parity", async ({ page }) => {
  const response = await page.goto("/");
  expect(response?.status()).toBe(200);
  expect(response?.headers()["content-security-policy"]).toContain("default-src 'self'");
  expect(response?.headers()["x-content-type-options"]).toBe("nosniff");

  await expect(page.getByRole("heading", { level: 1, name: "All product capabilities, one current view" })).toBeVisible();
  await expect(page.locator(".capability-card")).toHaveCount(26);
  await expect(page.getByText("Showing 26 of 26 product capabilities.")).toBeVisible();
  await expect(page.getByText("No evidence-backed parallel CAP lane is currently available.")).toBeVisible();

  const accessibility = await new AxeBuilder({ page }).analyze();
  expect(accessibility.violations).toEqual([]);

  await page.keyboard.press("Tab");
  await expect(page.getByRole("link", { name: "Skip to roadmap" })).toBeFocused();
  const theme = page.getByLabel("Theme");
  for (const value of ["dark", "light", "system"]) {
    await theme.selectOption(value);
    await expect(page.locator("html")).toHaveAttribute("data-theme", value);
    await expect(page.locator(".capability-card")).toHaveCount(26);
  }

  await page.setViewportSize({ width: 360, height: 800 });
  await expect(page.locator(".capability-card")).toHaveCount(26);
  const overflowing = await page.evaluate(() => Array.from(document.querySelectorAll<HTMLElement>("body *"))
    .filter((element) => element.getBoundingClientRect().right > document.documentElement.clientWidth + 1)
    .map((element) => `${element.tagName.toLowerCase()}.${element.className}`));
  expect(overflowing).toEqual([]);

  await page.emulateMedia({ colorScheme: "dark", forcedColors: "active", reducedMotion: "reduce" });
  await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
  await expect(page.locator(".capability-card")).toHaveCount(26);
});

test("navigates the live hierarchy and preserves honest missing states", async ({ page }) => {
  await page.goto("/cap/CAP-0008");
  await expect(page.getByRole("heading", { level: 2, name: "Declared slices" })).toBeVisible();
  await expect(page.getByRole("link", { name: /SLI-0036/ })).toBeVisible();
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);

  await page.goto("/slice/SLI-0036");
  await expect(page.getByRole("heading", { level: 2, name: "Associated work" })).toBeVisible();
  await expect(page.getByRole("link", { name: /WRK-0026/ })).toBeVisible();

  await page.goto("/work/WRK-0026");
  await expect(page.getByRole("heading", { level: 1, name: /WRK-0026/ })).toBeVisible();
  await expect(page.locator(".plan-document script")).toHaveCount(0);

  await page.goto("/capability/track-progress-and-competency-evidence");
  await expect(page.getByRole("heading", { level: 1, name: "Track Progress and Competency Evidence" })).toBeVisible();
  await expect(page.getByRole("link", { name: /SLI-0038: detailed plan not refined yet/ })).toBeVisible();
  await expect(page.getByRole("link", { name: /DEC-0009/ })).toBeVisible();
  await expect(page.getByLabel("Decision status: complete")).toBeVisible();

  await page.goto("/slice/SLI-0018");
  await expect(page.getByRole("heading", { level: 2, name: "Associated work" })).toBeVisible();
  await expect(page.getByRole("link", { name: /WRK-0043/ })).toBeVisible();

  await page.goto("/slice/SLI-0038");
  await expect(page.getByText(/has not been refined/)).toBeVisible();
  await expect(page.getByText(/does not block review of other work/)).toBeVisible();
  await expect(page.getByRole("link", { name: /DEC-0009/ })).toBeVisible();

  await page.goto("/decision/DEC-0009");
  await expect(page.getByRole("heading", { level: 1, name: /DEC-0009/ })).toBeVisible();
  await expect(page.getByText("Decision recorded")).toBeVisible();
  await expect(page.getByText("Yes", { exact: true })).toBeVisible();
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);

  await page.goto("/decision/DEC-0012");
  await expect(page.getByRole("heading", { level: 1, name: /DEC-0012/ })).toBeVisible();
  await expect(page.getByText("No decision outcome is recorded yet.")).toBeVisible();
  await expect(page.getByText("No separate canonical record linked")).toBeVisible();

  await page.goto("/work/NOT-REAL");
  await expect(page.getByRole("alert")).toContainText("Roadmap entry not found");
  await expect(page.getByRole("link", { name: "Return to all capabilities" })).toHaveAttribute("href", "/");
});

test("shows a bounded retry path when the live projection fails", async ({ page }) => {
  await page.route("**/api/roadmap", async (route) => {
    await route.fulfill({ status: 503, contentType: "application/json", body: '{"error":"unavailable"}' });
  });
  await page.goto("/");
  await expect(page.getByRole("alert")).toContainText("Roadmap unavailable");
  await expect(page.getByRole("button", { name: "Try again" })).toBeVisible();
});

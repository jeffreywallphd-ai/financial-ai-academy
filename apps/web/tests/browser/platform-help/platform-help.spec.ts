import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";
import type { Page, Route } from "@playwright/test";

import {
  platformHelpSearchFixture,
  platformHelpTopicFixture,
} from "../../component/platformHelpFixture";

const SESSION_PATTERN = "**/api/v1/session/single-profile";
const SEARCH_PATTERN = "**/api/v1/guidance/platform-help?*";
const TOPIC_PATTERN = "**/api/v1/guidance/platform-help/*/versions/*";

function json(route: Route, status: number, body: unknown) {
  return route.fulfill({
    status,
    contentType: "application/json",
    body: JSON.stringify(body),
  });
}

async function mockPlatformHelp(page: Page) {
  await page.route(SESSION_PATTERN, (route) =>
    json(route, 201, {
      status: "ready",
      authentication_method: "single_profile",
      expires_at: "2026-10-18T13:00:00Z",
    }),
  );
  await page.route(TOPIC_PATTERN, (route) => json(route, 200, platformHelpTopicFixture));
  await page.route(SEARCH_PATTERN, (route) => {
    const url = new URL(route.request().url());
    const query = url.searchParams.get("query") ?? "";
    const topicKind = url.searchParams.get("topic_kind");
    return json(route, 200, {
      ...platformHelpSearchFixture,
      query,
      ...(topicKind ? { topic_kind: topicKind } : { topic_kind: null }),
    });
  });
}

test("browses and reads reviewed platform help with equivalent themes", async ({ page }) => {
  await mockPlatformHelp(page);
  await page.goto("/help?query=calculations&topic_kind=method&page_size=20");

  await expect(
    page.getByRole("heading", { name: "Understand how the Academy works" }),
  ).toBeVisible();
  await expect(
    page.getByRole("link", { name: "Platform guide", exact: true }),
  ).toHaveAttribute("aria-current", "page");
  await page.getByRole("link", { name: "Read this topic" }).click();
  await expect(page).toHaveURL(/\/help\/topics\/platform-methods\/versions\/1\.0\.0/);
  await expect(
    page.getByRole("heading", { name: "How platform methods stay reproducible" }),
  ).toBeVisible();
  await expect(page.getByText("Known limit")).toBeVisible();
  await expect(page.getByText(/Last updated October 18, 2026/)).toBeVisible();

  const baseline = await page.locator("main").innerText();
  for (const theme of ["light", "dark", "system"] as const) {
    await page.getByLabel("Theme").selectOption(theme);
    await expect(page.locator("html")).toHaveAttribute("data-theme", theme);
    expect(await page.locator("main").innerText()).toBe(baseline);
    expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  }

  await page.getByRole("link", { name: "Return to platform guide" }).click();
  await expect(page).toHaveURL(/\/help\?query=calculations&topic_kind=method&page_size=20$/);
});

test("supports keyboard skip navigation and narrow reflow", async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 720 });
  await page.emulateMedia({ reducedMotion: "reduce", forcedColors: "active" });
  await mockPlatformHelp(page);
  await page.goto("/help");

  await page.keyboard.press("Tab");
  await expect(page.getByRole("link", { name: "Skip to platform guide" })).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(page.locator("main")).toBeFocused();
  const dimensions = await page.evaluate(() => ({
    viewport: document.documentElement.clientWidth,
    content: document.documentElement.scrollWidth,
  }));
  expect(dimensions.content).toBeLessThanOrEqual(dimensions.viewport);
});

test("rejects an unsafe response without rendering partial guide content", async ({ page }) => {
  await mockPlatformHelp(page);
  const invalid = structuredClone(platformHelpSearchFixture) as any;
  invalid.results[0].provider_payload = { private: true };
  await page.route(SEARCH_PATTERN, (route) => json(route, 200, invalid));

  await page.goto("/help?query=calculations&topic_kind=method&page_size=20");
  await expect(
    page.getByRole("heading", { name: "Platform guide response unavailable" }),
  ).toBeVisible();
  await expect(page.getByText("How platform methods stay reproducible")).toHaveCount(0);
  await expect(page.getByText("private")).toHaveCount(0);
});

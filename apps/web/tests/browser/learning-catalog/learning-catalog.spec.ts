import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";
import type { Page, Route } from "@playwright/test";

import { learningCatalogFixture } from "../../component/learningCatalogFixture";

const SESSION_PATTERN = "**/api/v1/session/single-profile";
const CATALOG_PATTERN = "**/api/v1/curriculum/opportunities";

function json(route: Route, status: number, body: unknown) {
  return route.fulfill({
    status,
    contentType: "application/json",
    body: JSON.stringify(body),
  });
}

async function mockReadyCatalog(
  page: Page,
  catalog: unknown = learningCatalogFixture,
) {
  await page.route(SESSION_PATTERN, (route) =>
    json(route, 201, {
      status: "ready",
      authentication_method: "single_profile",
      expires_at: "2026-10-15T13:00:00Z",
    }),
  );
  await page.route(CATALOG_PATTERN, (route) => json(route, 200, catalog));
}

test("renders the protected catalog with equivalent themes and no axe violations", async ({
  page,
}) => {
  await mockReadyCatalog(page);
  await page.goto("/");
  await expect(page).toHaveURL(/\/learn$/);

  const title = page.getByRole("heading", {
    level: 1,
    name: "Build financial understanding step by step",
  });
  await expect(title).toBeVisible();
  await expect(page.getByRole("article")).toHaveCount(2);
  await expect(
    page.getByRole("link", { name: "Open exact lesson" }),
  ).toHaveAttribute("href", "/learn/placements/cash-flow-basics-primary");
  await expect(
    page.getByText("The exact reviewed lesson is available."),
  ).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "Portfolio Project" }),
  ).toBeVisible();

  const baselineText = await page.locator("main").innerText();
  for (const theme of ["light", "dark", "system"] as const) {
    await page.getByLabel("Theme").selectOption(theme);
    await expect(page.locator("html")).toHaveAttribute("data-theme", theme);
    expect(await page.locator("main").innerText()).toBe(baselineText);
    const accessibility = await new AxeBuilder({ page }).analyze();
    expect(accessibility.violations).toEqual([]);
  }
});

test("supports keyboard focus, narrow reflow, reduced motion, and forced colors", async ({
  page,
}) => {
  await page.setViewportSize({ width: 375, height: 720 });
  await page.emulateMedia({
    reducedMotion: "reduce",
    forcedColors: "active",
  });
  await mockReadyCatalog(page);
  await page.goto("/learn");
  await expect(
    page.getByRole("heading", { name: "Cash Flow Basics" }),
  ).toBeVisible();

  await page.keyboard.press("Tab");
  await expect(page.getByRole("link", { name: "Skip to learning content" })).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(page.locator("main")).toBeFocused();

  const dimensions = await page.evaluate(() => ({
    viewport: document.documentElement.clientWidth,
    content: document.documentElement.scrollWidth,
    duration: getComputedStyle(document.documentElement)
      .getPropertyValue("--faa-duration-standard")
      .trim(),
  }));
  expect(dimensions.content).toBeLessThanOrEqual(dimensions.viewport);
  expect(dimensions.duration).toBe("0ms");

  const theme = page.getByLabel("Theme");
  await theme.focus();
  expect(
    await theme.evaluate((element) => getComputedStyle(element).outlineStyle),
  ).not.toBe("none");
});

test("shows a bounded denied state before requesting catalog records", async ({
  page,
}) => {
  let catalogRequested = false;
  await page.route(SESSION_PATTERN, async (route) => {
    await new Promise((resolve) => setTimeout(resolve, 250));
    await json(route, 403, {
      error_version: "1.0",
      code: "forbidden",
      message: "Request forbidden.",
      correlation_id: "00000000-0000-0000-0000-000000000000",
    });
  });
  await page.route(CATALOG_PATTERN, (route) => {
    catalogRequested = true;
    return json(route, 500, {});
  });

  await page.goto("/learn");
  await expect(
    page.getByRole("heading", { name: "Catalog access unavailable" }),
  ).toBeVisible();
  await expect(page.getByText("Cash Flow Basics")).toHaveCount(0);
  expect(catalogRequested).toBe(false);
});

test("rejects an invalid record without rendering a partial catalog", async ({
  page,
}) => {
  const invalid = structuredClone(learningCatalogFixture) as unknown as {
    records: Array<Record<string, unknown>>;
  };
  const firstRecord = invalid.records[0];
  if (!firstRecord) {
    throw new Error("Expected a catalog record.");
  }
  firstRecord.provider_payload = { bucket: "private" };
  await mockReadyCatalog(page, invalid);

  await page.goto("/learn");
  await expect(
    page.getByRole("heading", { name: "Catalog response unavailable" }),
  ).toBeVisible();
  await expect(page.getByRole("article")).toHaveCount(0);
  await expect(page.getByText("Cash Flow Basics")).toHaveCount(0);
  await expect(page.getByText("private")).toHaveCount(0);
});

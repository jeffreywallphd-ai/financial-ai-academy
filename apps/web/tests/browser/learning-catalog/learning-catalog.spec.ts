import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";
import type { Page, Route } from "@playwright/test";

import {
  learningCatalogFixture,
  learningQueryPageFixture,
} from "../../component/learningCatalogFixture";

const SESSION_PATTERN = "**/api/v1/session/single-profile";
const BROWSE_PATTERN = "**/api/v1/curriculum/opportunities";
const CATALOG_PATTERN = "**/api/v1/curriculum/opportunities/query*";

function json(route: Route, status: number, body: unknown) {
  return route.fulfill({
    status,
    contentType: "application/json",
    body: JSON.stringify(body),
  });
}

async function mockReadyCatalog(
  page: Page,
  catalog: unknown = learningQueryPageFixture,
  browse: unknown = learningCatalogFixture,
) {
  await page.route(SESSION_PATTERN, (route) =>
    json(route, 201, {
      status: "ready",
      authentication_method: "single_profile",
      expires_at: "2026-10-15T13:00:00Z",
    }),
  );
  await page.route(CATALOG_PATTERN, (route) => json(route, 200, catalog));
  await page.route(BROWSE_PATTERN, (route) => json(route, 200, browse));
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
    page.getByRole("searchbox", { name: "Search opportunities" }),
  ).toBeVisible();
  await expect(page.getByRole("button", { name: "Apply query" })).toBeVisible();
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
  await expect(
    page.getByRole("link", { name: "Skip to learning content" }),
  ).toBeFocused();
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

test("preserves every valid page-size value in the query controls", async ({
  page,
}) => {
  await mockReadyCatalog(page, {
    ...learningQueryPageFixture,
    applied_query: {
      ...learningQueryPageFixture.applied_query,
      page_size: 17,
    },
  });
  await page.goto("/learn?page_size=17");

  await expect(
    page.getByRole("spinbutton", { name: "Results per page" }),
  ).toHaveValue("17");
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
  const invalid = structuredClone(learningQueryPageFixture) as unknown as {
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

test("inspects exact current opportunity details with theme and return parity", async ({
  page,
}) => {
  await mockReadyCatalog(page, {
    ...learningQueryPageFixture,
    applied_query: {
      ...learningQueryPageFixture.applied_query,
      query: "cash",
    },
  });
  await page.goto("/learn?query=cash");
  await page.getByRole("link", { name: "View details" }).first().click();

  await expect(page).toHaveURL(
    /\/learn\/opportunities\/cash-flow-basics-primary\?return_to=%2Flearn%3Fquery%3Dcash$/,
  );
  await expect(
    page.getByRole("heading", { level: 1, name: "Cash Flow Basics" }),
  ).toBeVisible();
  await expect(page.getByText("cash-flow-basics@1.2.0")).toBeVisible();
  await expect(
    page.getByText(learningCatalogFixture.projection_generation),
  ).toBeVisible();
  await expect(
    page.getByRole("link", { name: "Open exact lesson" }),
  ).toHaveAttribute("href", "/learn/placements/cash-flow-basics-primary");
  await expect(
    page.getByRole("link", { name: "Return to catalog" }),
  ).toHaveAttribute("href", "/learn?query=cash");

  const baselineText = await page.locator("main").innerText();
  for (const theme of ["light", "dark", "system"] as const) {
    await page.getByLabel("Theme").selectOption(theme);
    await expect(page.locator("html")).toHaveAttribute("data-theme", theme);
    expect(await page.locator("main").innerText()).toBe(baselineText);
    const accessibility = await new AxeBuilder({ page }).analyze();
    expect(accessibility.violations).toEqual([]);
  }

  await page.getByRole("link", { name: "Return to catalog" }).click();
  await expect(page).toHaveURL(/\/learn\?query=cash$/);
});

test("keeps planned detail visible but non-executable", async ({ page }) => {
  await mockReadyCatalog(page);
  await page.goto("/learn/opportunities/portfolio-project-planned");

  await expect(
    page.getByRole("heading", { level: 1, name: "Portfolio Project" }),
  ).toBeVisible();
  await expect(
    page.getByText("This project is planned but cannot be opened yet."),
  ).toBeVisible();
  await expect(
    page.getByRole("link", { name: "Open exact lesson" }),
  ).toHaveCount(0);
  await expect(
    page.getByRole("link", { name: "Return to catalog" }),
  ).toHaveAttribute("href", "/learn");
});

test("supports detail keyboard focus, narrow reflow, reduced motion, and forced colors", async ({
  page,
}) => {
  await page.setViewportSize({ width: 375, height: 720 });
  await page.emulateMedia({ reducedMotion: "reduce", forcedColors: "active" });
  await mockReadyCatalog(page);
  await page.goto("/learn/opportunities/cash-flow-basics-primary");

  await page.keyboard.press("Tab");
  await expect(
    page.getByRole("link", { name: "Skip to learning content" }),
  ).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(page.locator("main")).toBeFocused();

  const returnLink = page.getByRole("link", { name: "Return to catalog" });
  await returnLink.focus();
  expect(
    await returnLink.evaluate(
      (element) => getComputedStyle(element).outlineStyle,
    ),
  ).not.toBe("none");
  await page.addStyleTag({ content: "html { font-size: 200% !important; }" });
  const dimensions = await page.evaluate(() => ({
    viewport: document.documentElement.clientWidth,
    content: document.documentElement.scrollWidth,
    duration: getComputedStyle(document.documentElement)
      .getPropertyValue("--faa-duration-standard")
      .trim(),
  }));
  expect(dimensions.content).toBeLessThanOrEqual(dimensions.viewport);
  expect(dimensions.duration).toBe("0ms");
});

test("fails closed for changed and invalid detail requests", async ({
  page,
}) => {
  await mockReadyCatalog(page);
  await page.goto("/learn/opportunities/removed-opportunity");
  await expect(
    page.getByRole("heading", { name: "Opportunity changed" }),
  ).toBeVisible();
  await expect(page.getByText("Cash Flow Basics")).toHaveCount(0);

  const invalid = structuredClone(learningCatalogFixture) as unknown as {
    records: Array<Record<string, unknown>>;
  };
  const firstRecord = invalid.records[0];
  if (!firstRecord) throw new Error("Expected a catalog record.");
  firstRecord.private_provider = "hidden";
  await page.unroute(BROWSE_PATTERN);
  await page.route(BROWSE_PATTERN, (route) => json(route, 200, invalid));
  await page.goto("/learn/opportunities/cash-flow-basics-primary");
  await expect(
    page.getByRole("heading", { name: "Opportunity response unavailable" }),
  ).toBeVisible();
  await expect(page.getByText("hidden")).toHaveCount(0);
});

test("denies detail before requesting catalog records", async ({ page }) => {
  let browseRequested = false;
  await page.route(SESSION_PATTERN, (route) =>
    json(route, 403, {
      error_version: "1.0",
      code: "forbidden",
      message: "Request forbidden.",
      correlation_id: "00000000-0000-0000-0000-000000000000",
    }),
  );
  await page.route(BROWSE_PATTERN, (route) => {
    browseRequested = true;
    return json(route, 500, {});
  });
  await page.goto("/learn/opportunities/cash-flow-basics-primary");
  await expect(
    page.getByRole("heading", { name: "Opportunity access unavailable" }),
  ).toBeVisible();
  await expect(page.getByText("Cash Flow Basics")).toHaveCount(0);
  expect(browseRequested).toBe(false);
});

test("selects and compares exact opportunities in learner order with theme parity", async ({
  page,
}) => {
  await mockReadyCatalog(page, {
    ...learningQueryPageFixture,
    applied_query: {
      ...learningQueryPageFixture.applied_query,
      query: "project",
    },
  });
  await page.goto("/learn?query=project");

  const compare = page.getByRole("button", { name: "Compare selected" });
  await expect(compare).toBeDisabled();
  await page
    .getByRole("checkbox", { name: "Compare Portfolio Project" })
    .check();
  await expect(compare).toBeDisabled();
  await page
    .getByRole("checkbox", { name: "Compare Cash Flow Basics" })
    .check();
  await expect(compare).toBeEnabled();
  await compare.click();

  const comparisonUrl = new URL(page.url());
  expect(comparisonUrl.pathname).toBe("/learn/opportunities/compare");
  expect(comparisonUrl.searchParams.get("return_to")).toBe(
    "/learn?query=project",
  );
  expect(comparisonUrl.searchParams.getAll("opportunity")).toEqual([
    "portfolio-project-planned",
    "cash-flow-basics-primary",
  ]);
  await expect(
    page.getByRole("heading", { level: 1, name: "Compare educational facts" }),
  ).toBeVisible();
  const cards = page.getByRole("article");
  await expect(cards).toHaveCount(2);
  await expect(cards.nth(0).getByRole("heading", { level: 2 })).toHaveText(
    "Portfolio Project",
  );
  await expect(cards.nth(1).getByRole("heading", { level: 2 })).toHaveText(
    "Cash Flow Basics",
  );
  await expect(
    cards.nth(0).getByRole("link", { name: "Open exact lesson" }),
  ).toHaveCount(0);
  await expect(
    cards.nth(1).getByRole("link", { name: "Open exact lesson" }),
  ).toHaveAttribute("href", "/learn/placements/cash-flow-basics-primary");
  await expect(
    page.getByRole("link", { name: "Return to catalog" }),
  ).toHaveAttribute("href", "/learn?query=project");

  const baselineText = await page.locator("main").innerText();
  for (const theme of ["light", "dark", "system"] as const) {
    await page.getByLabel("Theme").selectOption(theme);
    await expect(page.locator("html")).toHaveAttribute("data-theme", theme);
    expect(await page.locator("main").innerText()).toBe(baselineText);
    const accessibility = await new AxeBuilder({ page }).analyze();
    expect(accessibility.violations).toEqual([]);
  }
});

test("keeps comparison operable with keyboard, forced colors, narrow reflow, and 200-percent text", async ({
  page,
}) => {
  await page.setViewportSize({ width: 375, height: 720 });
  await page.emulateMedia({ reducedMotion: "reduce", forcedColors: "active" });
  await mockReadyCatalog(page);
  await page.goto(
    "/learn/opportunities/compare?opportunity=cash-flow-basics-primary&opportunity=portfolio-project-planned",
  );

  await page.keyboard.press("Tab");
  await expect(
    page.getByRole("link", { name: "Skip to learning content" }),
  ).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(page.locator("main")).toBeFocused();
  const detailLink = page.getByRole("link", { name: "View details" }).first();
  await detailLink.focus();
  expect(
    await detailLink.evaluate(
      (element) => getComputedStyle(element).outlineStyle,
    ),
  ).not.toBe("none");

  await page.addStyleTag({ content: "html { font-size: 200% !important; }" });
  const dimensions = await page.evaluate(() => ({
    viewport: document.documentElement.clientWidth,
    content: document.documentElement.scrollWidth,
    duration: getComputedStyle(document.documentElement)
      .getPropertyValue("--faa-duration-standard")
      .trim(),
  }));
  expect(dimensions.content).toBeLessThanOrEqual(dimensions.viewport);
  expect(dimensions.duration).toBe("0ms");
});

test("fails the whole comparison for changed, malformed, or invalid current data", async ({
  page,
}) => {
  await mockReadyCatalog(page);
  await page.goto(
    "/learn/opportunities/compare?opportunity=cash-flow-basics-primary&opportunity=removed-opportunity",
  );
  await expect(
    page.getByRole("heading", { name: "Comparison changed" }),
  ).toBeVisible();
  await expect(page.getByText("Cash Flow Basics")).toHaveCount(0);

  await page.goto(
    "/learn/opportunities/compare?opportunity=cash-flow-basics-primary",
  );
  await expect(
    page.getByRole("heading", { name: "Comparison link unavailable" }),
  ).toBeVisible();

  const invalid = structuredClone(learningCatalogFixture) as unknown as {
    records: Array<Record<string, unknown>>;
  };
  const firstRecord = invalid.records[0];
  if (!firstRecord) throw new Error("Expected a catalog record.");
  firstRecord.private_provider = "hidden";
  await page.unroute(BROWSE_PATTERN);
  await page.route(BROWSE_PATTERN, (route) => json(route, 200, invalid));
  await page.goto(
    "/learn/opportunities/compare?opportunity=cash-flow-basics-primary&opportunity=portfolio-project-planned",
  );
  await expect(
    page.getByRole("heading", { name: "Comparison response unavailable" }),
  ).toBeVisible();
  await expect(page.getByText("hidden")).toHaveCount(0);
  await expect(page.getByText("Portfolio Project")).toHaveCount(0);
});

test("denies comparison before requesting current catalog records", async ({
  page,
}) => {
  let browseRequested = false;
  await page.route(SESSION_PATTERN, (route) =>
    json(route, 403, {
      error_version: "1.0",
      code: "forbidden",
      message: "Request forbidden.",
      correlation_id: "00000000-0000-0000-0000-000000000000",
    }),
  );
  await page.route(BROWSE_PATTERN, (route) => {
    browseRequested = true;
    return json(route, 500, {});
  });
  await page.goto(
    "/learn/opportunities/compare?opportunity=cash-flow-basics-primary&opportunity=portfolio-project-planned",
  );
  await expect(
    page.getByRole("heading", { name: "Comparison access unavailable" }),
  ).toBeVisible();
  await expect(page.getByText("Cash Flow Basics")).toHaveCount(0);
  expect(browseRequested).toBe(false);
});

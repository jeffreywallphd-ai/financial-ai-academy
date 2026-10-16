import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";
import type { Page, Route } from "@playwright/test";

import {
  curriculumGraphFixture,
  navigationStateFixture,
} from "../../component/curriculumGraphFixture";

const SESSION_PATTERN = "**/api/v1/session/single-profile";
const GRAPH_PATTERN = "**/api/v1/curriculum/graphs/*/versions/*";
const NAVIGATION_PATTERN =
  "**/api/v1/adaptation/curricula/*/versions/*/navigation-state";
const GRAPH_URL =
  "/learn/curricula/investing-foundations/versions/1.0.0";

function json(route: Route, status: number, body: unknown) {
  return route.fulfill({
    status,
    contentType: "application/json",
    body: JSON.stringify(body),
  });
}

async function mockReadyGraph(
  page: Page,
  graph: unknown = curriculumGraphFixture,
  navigationState: unknown = navigationStateFixture,
) {
  await page.route(SESSION_PATTERN, (route) =>
    json(route, 201, {
      status: "ready",
      authentication_method: "single_profile",
      expires_at: "2026-10-15T13:00:00Z",
    }),
  );
  await page.route(GRAPH_PATTERN, (route) => json(route, 200, graph));
  await page.route(NAVIGATION_PATTERN, (route) =>
    json(route, 200, navigationState),
  );
}

test("renders an exact protected graph with list-map and theme parity", async ({
  page,
}) => {
  await mockReadyGraph(page);
  await page.goto(GRAPH_URL);

  await expect(
    page.getByRole("heading", { level: 1, name: "Investing Foundations" }),
  ).toBeVisible();
  await expect(
    page.getByText("investing-foundations@1.0.0", { exact: true }),
  ).toBeVisible();
  await expect(page.getByRole("article")).toHaveCount(6);
  await expect(page.getByText("Locked")).toHaveCount(3);
  await expect(
    page.getByText(
      "The approved curriculum assigns this activity only to optional branches.",
    ),
  ).toHaveCount(2);
  await expect(
    page.getByRole("article").getByText("branch-practice"),
  ).toHaveCount(2);
  await expect(
    page.getByRole("heading", { name: "Activities outside branch groupings" }),
  ).toBeVisible();
  await expect(page.getByRole("link", { name: /open|start|launch/i })).toHaveCount(
    0,
  );

  const listFacts = await page.getByTestId("curriculum-graph-list").innerText();
  await page.getByRole("button", { name: "Map view" }).click();
  await expect(page.getByRole("button", { name: "Map view" })).toHaveAttribute(
    "aria-pressed",
    "true",
  );
  expect(await page.getByTestId("curriculum-graph-map").innerText()).toBe(
    listFacts,
  );

  const baselineText = await page.locator("main").innerText();
  for (const theme of ["light", "dark", "system"] as const) {
    await page.getByLabel("Theme").selectOption(theme);
    await expect(page.locator("html")).toHaveAttribute("data-theme", theme);
    expect(await page.locator("main").innerText()).toBe(baselineText);
    const accessibility = await new AxeBuilder({ page }).analyze();
    expect(accessibility.violations).toEqual([]);
  }
});

test("keeps the graph operable with keyboard, narrow reflow, forced colors, reduced motion, and 200-percent text", async ({
  page,
}) => {
  await page.setViewportSize({ width: 375, height: 720 });
  await page.emulateMedia({ reducedMotion: "reduce", forcedColors: "active" });
  await mockReadyGraph(page);
  await page.goto(GRAPH_URL);

  await page.keyboard.press("Tab");
  await expect(
    page.getByRole("link", { name: "Skip to learning content" }),
  ).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(page.locator("main")).toBeFocused();

  const mapButton = page.getByRole("button", { name: "Map view" });
  await mapButton.focus();
  expect(
    await mapButton.evaluate(
      (element) => getComputedStyle(element).outlineStyle,
    ),
  ).not.toBe("none");
  await page.keyboard.press("Enter");
  await expect(mapButton).toHaveAttribute("aria-pressed", "true");

  await page.addStyleTag({ content: "html { font-size: 200% !important; }" });
  const dimensions = await page.evaluate(() => {
    const viewport = document.documentElement.clientWidth;
    return {
      viewport,
      content: document.documentElement.scrollWidth,
      overflowing: [...document.querySelectorAll<HTMLElement>("body *")]
        .filter(
          (element) =>
            Math.ceil(element.getBoundingClientRect().right) > viewport,
        )
        .map((element) => `${element.tagName}.${element.className}`)
        .slice(0, 10),
      duration: getComputedStyle(document.documentElement)
        .getPropertyValue("--faa-duration-standard")
        .trim(),
    };
  });
  expect(
    dimensions.content,
    `Overflowing elements: ${dimensions.overflowing.join(", ")}`,
  ).toBeLessThanOrEqual(dimensions.viewport);
  expect(dimensions.duration).toBe("0ms");
});

test("denies the route before requesting a graph", async ({ page }) => {
  let graphRequested = false;
  let navigationRequested = false;
  await page.route(SESSION_PATTERN, (route) =>
    json(route, 403, {
      error_version: "1.0",
      code: "forbidden",
      message: "Request forbidden.",
      correlation_id: "00000000-0000-0000-0000-000000000000",
    }),
  );
  await page.route(GRAPH_PATTERN, (route) => {
    graphRequested = true;
    return json(route, 500, {});
  });
  await page.route(NAVIGATION_PATTERN, (route) => {
    navigationRequested = true;
    return json(route, 500, {});
  });

  await page.goto(GRAPH_URL);
  await expect(
    page.getByRole("heading", { name: "Curriculum graph access unavailable" }),
  ).toBeVisible();
  await expect(page.getByText("Investing Foundations")).toHaveCount(0);
  expect(graphRequested).toBe(false);
  expect(navigationRequested).toBe(false);
});

test("fails closed for invalid, missing, and malformed exact graph requests", async ({
  page,
}) => {
  const invalid = structuredClone(curriculumGraphFixture) as unknown as Record<
    string,
    unknown
  >;
  invalid.private_provider_payload = { bucket: "hidden" };
  await mockReadyGraph(page, invalid);
  await page.goto(GRAPH_URL);
  await expect(
    page.getByRole("heading", { name: "Curriculum graph response unavailable" }),
  ).toBeVisible();
  await expect(page.getByText("Investing Foundations")).toHaveCount(0);
  await expect(page.getByText("hidden")).toHaveCount(0);

  await page.unroute(GRAPH_PATTERN);
  await page.route(GRAPH_PATTERN, (route) =>
    json(route, 404, {
      error_version: "1.0",
      code: "curriculum_graph_not_found",
      message: "Curriculum graph not found.",
      correlation_id: "00000000-0000-0000-0000-000000000000",
    }),
  );
  await page.goto(
    "/learn/curricula/investing-foundations/versions/9.9.9",
  );
  await expect(
    page.getByRole("heading", { name: "Curriculum graph version not found" }),
  ).toBeVisible();

  let malformedRequested = false;
  await page.unroute(GRAPH_PATTERN);
  await page.route(GRAPH_PATTERN, (route) => {
    malformedRequested = true;
    return json(route, 500, {});
  });
  await page.goto(`${GRAPH_URL}?latest=true`);
  await expect(
    page.getByRole("heading", { name: "Curriculum graph link unavailable" }),
  ).toBeVisible();
  expect(malformedRequested).toBe(false);
});

test("fails the whole page closed for an unavailable or mismatched navigation projection", async ({
  page,
}) => {
  await mockReadyGraph(page, curriculumGraphFixture, {
    ...navigationStateFixture,
    graph_digest: "9".repeat(64),
  });
  await page.goto(GRAPH_URL);
  await expect(
    page.getByRole("heading", { name: "Curriculum graph response unavailable" }),
  ).toBeVisible();
  await expect(page.getByText("Investing Foundations")).toHaveCount(0);

  await page.unroute(NAVIGATION_PATTERN);
  await page.route(NAVIGATION_PATTERN, (route) => json(route, 503, {}));
  await page.goto(GRAPH_URL);
  await expect(
    page.getByRole("heading", {
      name: "Curriculum graph temporarily unavailable",
    }),
  ).toBeVisible();
  await expect(page.getByText("Investing Foundations")).toHaveCount(0);
});

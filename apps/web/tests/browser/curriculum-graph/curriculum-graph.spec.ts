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

function displayLabel(value: string): string {
  return value
    .split(/[-_]/)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

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

test("renders an exact protected learning path with list-map and theme parity", async ({
  page,
}) => {
  await mockReadyGraph(page);
  await page.goto(GRAPH_URL);

  await expect(
    page.getByRole("heading", { level: 1, name: "Investing Foundations" }),
  ).toBeVisible();
  const cardOccurrences = (activityId: string) =>
    Math.max(
      1,
      curriculumGraphFixture.branches.filter((branch) =>
        branch.activity_ids.includes(activityId),
      ).length,
    );
  const expectedActivityCards = curriculumGraphFixture.activities.reduce(
    (count, activity) => count + cardOccurrences(activity.activity_id),
    0,
  );
  const expectedBlockedCards = navigationStateFixture.activity_states.reduce(
    (count, state) =>
      count +
      (state.eligibility === "locked" ? cardOccurrences(state.activity_id) : 0),
    0,
  );
  const expectedOptionalReasonCards =
    navigationStateFixture.activity_states.reduce(
      (count, state) =>
        count +
        (state.reasons.some((reason) => reason.code === "optional_activity")
          ? cardOccurrences(state.activity_id)
          : 0),
      0,
    );
  await expect(page.getByRole("article")).toHaveCount(expectedActivityCards);
  await expect(
    page.getByRole("article").getByText("Blocked", { exact: true }),
  ).toHaveCount(expectedBlockedCards);
  await expect(
    page.getByRole("article").getByText(
      "This activity is an optional part of the learning path.",
      { exact: true },
    ),
  ).toHaveCount(expectedOptionalReasonCards);
  await expect(
    page.getByRole("heading", { name: "Activities outside learning groups" }),
  ).toBeVisible();
  await expect(page.getByRole("link", { name: /open|start|launch/i })).toHaveCount(
    0,
  );
  await expect(
    page.getByRole("heading", { name: /curriculum graph/i }),
  ).toHaveCount(0);
  await expect(
    page.getByText("Eligibility state", { exact: true }).first(),
  ).toBeHidden();
  await expect(
    page.getByText("Navigation projection digest", { exact: true }),
  ).toBeHidden();

  const pageRecord = page.locator(".curriculum-graph__provenance");
  await pageRecord.locator("summary").click();
  for (const value of [
    `${curriculumGraphFixture.curriculum_id}@${curriculumGraphFixture.curriculum_version}`,
    curriculumGraphFixture.schema_version,
    navigationStateFixture.schema_version,
    curriculumGraphFixture.graph_digest,
    navigationStateFixture.evaluated_at,
    `${navigationStateFixture.policy_id}@${navigationStateFixture.policy_version}`,
    navigationStateFixture.source_set_digest,
    navigationStateFixture.projection_digest,
    ...curriculumGraphFixture.source_references,
  ]) {
    await expect(pageRecord.getByText(value, { exact: true }).first()).toBeVisible();
  }

  const [firstActivity] = curriculumGraphFixture.activities;
  expect(firstActivity).toBeDefined();
  if (!firstActivity) throw new Error("Expected at least one activity.");
  const firstState = navigationStateFixture.activity_states.find(
    (state) => state.activity_id === firstActivity.activity_id,
  );
  expect(firstState).toBeDefined();
  if (!firstState) throw new Error("Expected state for the first activity.");
  const firstCard = page
    .getByRole("article")
    .filter({
      has: page.getByRole("heading", { name: firstActivity.title }),
    })
    .first();
  await firstCard.getByText("Technical record").click();
  const activityIdRow = firstCard.getByText("Activity ID").locator("..");
  await expect(
    activityIdRow.getByText(firstActivity.activity_id, { exact: true }),
  ).toBeVisible();
  const firstDigest =
    firstActivity.reference.reference_kind === "lesson_placement"
      ? firstActivity.reference.package_digest
      : firstActivity.reference.definition_digest;
  await expect(
    firstCard.getByText(firstDigest, { exact: true }),
  ).toBeVisible();
  for (const reason of firstState.reasons) {
    await expect(firstCard.getByText(reason.code, { exact: true })).toBeVisible();
    await expect(
      firstCard.getByText(reason.explanation, { exact: true }),
    ).toBeVisible();
    const references = firstCard.getByRole("list", {
      name: `${displayLabel(reason.code)} references`,
    });
    for (const reference of reason.references) {
      await expect(references.getByText(reference, { exact: true })).toBeVisible();
    }
  }

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

test("keeps the learning path operable with keyboard, narrow reflow, forced colors, reduced motion, and 200-percent text", async ({
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

test("denies the route before requesting a learning path", async ({ page }) => {
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
    page.getByRole("heading", { name: "Learning path access unavailable" }),
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
    page.getByRole("heading", { name: "Learning path unavailable" }),
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
    page.getByRole("heading", { name: "Learning path version not found" }),
  ).toBeVisible();

  let malformedRequested = false;
  await page.unroute(GRAPH_PATTERN);
  await page.route(GRAPH_PATTERN, (route) => {
    malformedRequested = true;
    return json(route, 500, {});
  });
  await page.goto(`${GRAPH_URL}?latest=true`);
  await expect(
    page.getByRole("heading", { name: "Learning path link unavailable" }),
  ).toBeVisible();
  expect(malformedRequested).toBe(false);
});

test("fails the whole page closed for unavailable or mismatched path status", async ({
  page,
}) => {
  await mockReadyGraph(page, curriculumGraphFixture, {
    ...navigationStateFixture,
    graph_digest: "9".repeat(64),
  });
  await page.goto(GRAPH_URL);
  await expect(
    page.getByRole("heading", { name: "Learning path unavailable" }),
  ).toBeVisible();
  await expect(page.getByText("Investing Foundations")).toHaveCount(0);

  await page.unroute(NAVIGATION_PATTERN);
  await page.route(NAVIGATION_PATTERN, (route) => json(route, 503, {}));
  await page.goto(GRAPH_URL);
  await expect(
    page.getByRole("heading", {
      name: "Learning path temporarily unavailable",
    }),
  ).toBeVisible();
  await expect(page.getByText("Investing Foundations")).toHaveCount(0);
});

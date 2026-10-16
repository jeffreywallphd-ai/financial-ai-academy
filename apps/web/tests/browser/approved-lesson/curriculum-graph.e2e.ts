import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";
import type { Locator } from "@playwright/test";

import type {
  ActivityNavigationState,
  CurriculumGraph,
  NavigationState,
} from "../../../src/features/curriculum-graph/model";

const CURRICULUM_ID = "investing-foundations";
const CURRICULUM_VERSION = "1.0.0";
const GRAPH_PATH =
  `/learn/curricula/${CURRICULUM_ID}/versions/${CURRICULUM_VERSION}`;
const GRAPH_API =
  `/api/v1/curriculum/graphs/${CURRICULUM_ID}/versions/${CURRICULUM_VERSION}`;
const NAVIGATION_API =
  `/api/v1/adaptation/curricula/${CURRICULUM_ID}/versions/${CURRICULUM_VERSION}/navigation-state`;

function displayLabel(value: string): string {
  return value
    .split(/[-_]/)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

async function expectNavigationFacts(
  card: Locator,
  state: ActivityNavigationState,
) {
  for (const [dimension, value] of [
    ["Completion", state.completion],
    ["Eligibility", state.eligibility],
    ["Requirement", state.requirement],
    ["Availability", state.availability],
  ] as const) {
    const row = card.getByText(dimension, { exact: true }).locator("..");
    await expect(
      row.getByText(displayLabel(value), { exact: true }),
    ).toBeVisible();
  }
  const reasonItems = card.locator(
    ".curriculum-graph__state-reasons > ol > li",
  );
  await expect(reasonItems).toHaveCount(state.reasons.length);
  for (const [index, reason] of state.reasons.entries()) {
    const reasonItem = reasonItems.nth(index);
    await expect(
      reasonItem.getByText(reason.explanation, { exact: true }),
    ).toBeVisible();
    await expect(
      reasonItem.getByText(displayLabel(reason.code), { exact: true }),
    ).toBeVisible();
    const references = reasonItem.getByRole("list", {
      name: `${displayLabel(reason.code)} references`,
    });
    await expect(references.getByRole("listitem")).toHaveCount(
      reason.references.length,
    );
    for (const reference of reason.references) {
      await expect(
        references.getByText(reference, { exact: true }),
      ).toBeVisible();
    }
  }
}

test("opens the live exact graph with peer views, provenance, and flexible grouping", async ({
  context,
  page,
}) => {
  const navigationResponsePromise = page.waitForResponse(
    (candidate) =>
      new URL(candidate.url()).pathname === NAVIGATION_API &&
      candidate.request().method() === "GET",
  );
  const response = await page.goto(GRAPH_PATH);
  const navigationResponse = await navigationResponsePromise;
  expect(response?.status()).toBe(200);
  expect(response?.headers()["content-security-policy"]).toContain(
    "default-src 'self'",
  );
  expect(response?.headers()["x-content-type-options"]).toBe("nosniff");

  await expect(
    page.getByRole("heading", { level: 1, name: "Investing Foundations" }),
  ).toBeVisible();
  const apiResponse = await context.request.get(GRAPH_API);
  expect(apiResponse.status()).toBe(200);
  const graph = (await apiResponse.json()) as CurriculumGraph;
  expect(graph).toMatchObject({
    curriculum_id: CURRICULUM_ID,
    curriculum_version: CURRICULUM_VERSION,
    publication_state: "approved",
    schema_version: "1.0.0",
  });
  expect(graph.activities.length).toBeGreaterThan(0);
  expect(graph.branches.length).toBeGreaterThan(0);
  expect(navigationResponse.status()).toBe(200);
  const navigationState =
    (await navigationResponse.json()) as NavigationState;
  expect(navigationState).toMatchObject({
    curriculum_id: graph.curriculum_id,
    curriculum_version: graph.curriculum_version,
    graph_digest: graph.graph_digest,
    policy_id: "deterministic-prerequisite-baseline",
    policy_version: "1.0.0",
    schema_version: "1.0.0",
  });
  expect(navigationState.evaluated_at).toMatch(/Z$/);
  expect(navigationState.source_set_digest).toMatch(/^[a-f0-9]{64}$/);
  expect(navigationState.projection_digest).toMatch(/^[a-f0-9]{64}$/);
  expect(
    navigationState.activity_states.map((state) => state.activity_id),
  ).toEqual(graph.activities.map((activity) => activity.activity_id));
  expect(
    new Set(navigationState.activity_states.map((state) => state.activity_id))
      .size,
  ).toBe(graph.activities.length);

  const reasonCounts = navigationState.activity_states.map(
    (state) => state.reasons.length,
  );
  const referenceCounts = navigationState.activity_states.flatMap((state) =>
    state.reasons.map((reason) => reason.references.length),
  );
  expect(reasonCounts.every((count) => count >= 2 && count <= 2002)).toBe(
    true,
  );
  expect(referenceCounts.every((count) => count >= 1 && count <= 10)).toBe(
    true,
  );
  for (const activity of graph.activities.filter(
    (candidate) => candidate.kind === "assessment",
  )) {
    const state = navigationState.activity_states.find(
      (candidate) => candidate.activity_id === activity.activity_id,
    );
    expect(state).toMatchObject({
      availability: "available",
      completion: "unavailable",
      eligibility: "unavailable",
    });
    expect(state?.reasons.map((reason) => reason.code)).toContain(
      "completion_source_unavailable",
    );
  }

  await expect(
    page.getByText(`${graph.curriculum_id}@${graph.curriculum_version}`, {
      exact: true,
    }),
  ).toBeVisible();
  await expect(page.locator(`time[datetime="${graph.published_at}"]`)).toBeVisible();
  await expect(page.getByText(graph.summary, { exact: true })).toBeVisible();
  for (const source of graph.source_references) {
    await expect(page.getByText(source, { exact: true })).toBeVisible();
  }
  await page
    .locator("summary", { hasText: "Technical graph and navigation identity" })
    .click();
  await expect(page.getByText(graph.graph_digest, { exact: true })).toBeVisible();
  await expect(
    page.getByText(
      `${navigationState.policy_id}@${navigationState.policy_version}`,
      { exact: true },
    ),
  ).toBeVisible();
  await expect(
    page.getByText(navigationState.source_set_digest, { exact: true }),
  ).toBeVisible();
  await expect(
    page.getByText(navigationState.projection_digest, { exact: true }),
  ).toBeVisible();
  await expect(
    page.locator(`time[datetime="${navigationState.evaluated_at}"]`),
  ).toBeVisible();

  const list = page.getByTestId("curriculum-graph-list");
  await expect(list).toBeVisible();
  const expectedActivityCards = graph.activities.reduce((count, activity) => {
    const branchOccurrences = graph.branches.filter((branch) =>
      branch.activity_ids.includes(activity.activity_id),
    ).length;
    return count + Math.max(1, branchOccurrences);
  }, 0);
  await expect(page.getByRole("article")).toHaveCount(expectedActivityCards);
  await expect(
    page
      .locator(".curriculum-graph__unbranched")
      .getByRole("heading", { level: 4, name: "Review investing terms" }),
  ).toBeVisible();
  for (const activity of graph.activities) {
    const state = navigationState.activity_states.find(
      (candidate) => candidate.activity_id === activity.activity_id,
    );
    expect(state).toBeDefined();
    if (!state) throw new Error(`Missing state for ${activity.activity_id}.`);
    const branchOccurrences = graph.branches.filter((branch) =>
      branch.activity_ids.includes(activity.activity_id),
    ).length;
    const cards = page.getByRole("article").filter({
      has: page.getByText(activity.activity_id, { exact: true }),
    });
    await expect(cards).toHaveCount(Math.max(1, branchOccurrences));
    for (let index = 0; index < (await cards.count()); index += 1) {
      await expectNavigationFacts(cards.nth(index), state);
    }
  }
  await expect(page.getByRole("link", { name: /open|start|launch/i })).toHaveCount(
    0,
  );
  await expect(page.getByText(/you are eligible|you have completed|mastered/i)).toHaveCount(
    0,
  );

  const listFacts = await list.innerText();
  await page.getByRole("button", { name: "Map view" }).click();
  await expect(page.getByRole("button", { name: "Map view" })).toHaveAttribute(
    "aria-pressed",
    "true",
  );
  expect(await page.getByTestId("curriculum-graph-map").innerText()).toBe(
    listFacts,
  );

  const baseline = await page.locator("main").innerText();
  for (const theme of ["light", "dark", "system"] as const) {
    await page.getByLabel("Theme").selectOption(theme);
    await expect(page.locator("html")).toHaveAttribute("data-theme", theme);
    expect(await page.locator("main").innerText()).toBe(baseline);
    const accessibility = await new AxeBuilder({ page }).analyze();
    expect(accessibility.violations).toEqual([]);
  }
});

test("keeps the live graph operable under narrow, keyboard, and adaptive display conditions", async ({
  page,
}) => {
  await page.setViewportSize({ width: 375, height: 720 });
  await page.emulateMedia({ reducedMotion: "reduce", forcedColors: "active" });
  await page.goto(GRAPH_PATH);
  await expect(
    page.getByRole("heading", { level: 1, name: "Investing Foundations" }),
  ).toBeVisible();

  await page.keyboard.press("Tab");
  await expect(
    page.getByRole("link", { name: "Skip to learning content" }),
  ).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(page.locator("main")).toBeFocused();

  const mapButton = page.getByRole("button", { name: "Map view" });
  await mapButton.focus();
  expect(
    await mapButton.evaluate((element) => getComputedStyle(element).outlineStyle),
  ).not.toBe("none");
  await page.keyboard.press("Enter");
  await expect(mapButton).toHaveAttribute("aria-pressed", "true");

  await page.evaluate(() => {
    document.documentElement.style.fontSize = "200%";
  });
  const dimensions = await page.evaluate(() => ({
    viewport: document.documentElement.clientWidth,
    content: document.documentElement.scrollWidth,
    overflowing: [...document.querySelectorAll<HTMLElement>("body *")]
      .filter(
        (element) =>
          Math.ceil(element.getBoundingClientRect().right) >
          document.documentElement.clientWidth,
      )
      .map((element) => `${element.tagName}.${element.className}`)
      .slice(0, 10),
    duration: getComputedStyle(document.documentElement)
      .getPropertyValue("--faa-duration-standard")
      .trim(),
  }));
  expect(
    dimensions.content,
    `Overflowing elements: ${dimensions.overflowing.join(", ")}`,
  ).toBeLessThanOrEqual(dimensions.viewport);
  expect(Number.parseFloat(dimensions.duration)).toBe(0);
});

test("denies graph facts without context and never substitutes a missing version", async ({
  context,
  page,
  request,
}) => {
  const unauthorized = await request.get(GRAPH_API);
  expect(unauthorized.status()).toBe(401);
  const denial = await unauthorized.text();
  expect(denial).not.toContain("Investing Foundations");
  expect(denial).not.toMatch(/graph_digest|source_references|actor_id|learner_id/i);
  const unauthorizedNavigation = await request.get(NAVIGATION_API);
  expect(unauthorizedNavigation.status()).toBe(401);
  const navigationDenial = await unauthorizedNavigation.text();
  expect(navigationDenial).not.toMatch(
    /graph_digest|source_set_digest|projection_digest|activity_states|actor_id|learner_id/i,
  );

  await page.goto(GRAPH_PATH);
  await expect(
    page.getByRole("heading", { level: 1, name: "Investing Foundations" }),
  ).toBeVisible();
  const missingApi = await context.request.get(
    `/api/v1/curriculum/graphs/${CURRICULUM_ID}/versions/9.9.9`,
  );
  expect(missingApi.status()).toBe(404);
  const rejectedSelector = await context.request.get(
    `${NAVIGATION_API}?policy_version=9.9.9`,
  );
  expect(rejectedSelector.status()).toBe(400);
  const selectorDenial = await rejectedSelector.text();
  expect(selectorDenial).not.toMatch(
    /source_set_digest|projection_digest|activity_states|learner_id/i,
  );
  const missingNavigation = await context.request.get(
    `/api/v1/adaptation/curricula/${CURRICULUM_ID}/versions/9.9.9/navigation-state`,
  );
  expect(missingNavigation.status()).toBe(404);
  const missingNavigationBody = await missingNavigation.text();
  expect(missingNavigationBody).not.toContain("Investing Foundations");
  expect(missingNavigationBody).not.toMatch(
    /graph_digest|source_set_digest|projection_digest|activity_states|activity_id|completion|eligibility|requirement|learner_id/i,
  );

  await page.goto(`/learn/curricula/${CURRICULUM_ID}/versions/9.9.9`);
  await expect(
    page.getByRole("heading", { name: "Curriculum graph version not found" }),
  ).toBeVisible();
  await expect(page.getByText("Investing Foundations")).toHaveCount(0);
  await expect(page.getByText(/latest version was substituted/i)).toBeVisible();
});

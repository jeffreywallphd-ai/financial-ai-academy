import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

import type { CurriculumGraph } from "../../../src/features/curriculum-graph/model";

const CURRICULUM_ID = "investing-foundations";
const CURRICULUM_VERSION = "1.0.0";
const GRAPH_PATH =
  `/learn/curricula/${CURRICULUM_ID}/versions/${CURRICULUM_VERSION}`;
const GRAPH_API =
  `/api/v1/curriculum/graphs/${CURRICULUM_ID}/versions/${CURRICULUM_VERSION}`;

test("opens the live exact graph with peer views, provenance, and flexible grouping", async ({
  context,
  page,
}) => {
  const response = await page.goto(GRAPH_PATH);
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
  expect(graph.activities).toHaveLength(5);
  expect(graph.branches).toHaveLength(3);

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
  await page.locator("summary", { hasText: "Technical graph identity" }).click();
  await expect(page.getByText(graph.graph_digest, { exact: true })).toBeVisible();

  const list = page.getByTestId("curriculum-graph-list");
  await expect(list).toBeVisible();
  await expect(page.getByRole("article")).toHaveCount(6);
  await expect(
    page.getByRole("heading", {
      level: 4,
      name: "Explore diversification",
    }),
  ).toHaveCount(2);
  await expect(
    page
      .locator(".curriculum-graph__unbranched")
      .getByRole("heading", { level: 4, name: "Review investing terms" }),
  ).toBeVisible();
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

  await page.goto(GRAPH_PATH);
  await expect(
    page.getByRole("heading", { level: 1, name: "Investing Foundations" }),
  ).toBeVisible();
  const missingApi = await context.request.get(
    `/api/v1/curriculum/graphs/${CURRICULUM_ID}/versions/9.9.9`,
  );
  expect(missingApi.status()).toBe(404);

  await page.goto(`/learn/curricula/${CURRICULUM_ID}/versions/9.9.9`);
  await expect(
    page.getByRole("heading", { name: "Curriculum graph version not found" }),
  ).toBeVisible();
  await expect(page.getByText("Investing Foundations")).toHaveCount(0);
  await expect(page.getByText(/latest version was substituted/i)).toBeVisible();
});

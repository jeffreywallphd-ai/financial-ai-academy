import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";
import type { Page, Route } from "@playwright/test";

import { practiceFixture } from "../../component/practiceFixture";


const PRACTICE_PATH =
  "/learn/placements/intro-risk-return-primary/practice";
const SESSION_PATTERN = "**/api/v1/session/single-profile";
const PRACTICE_PATTERN =
  "**/api/v1/curriculum/placements/*/practice";

function json(route: Route, status: number, body: unknown) {
  return route.fulfill({
    status,
    contentType: "application/json",
    body: JSON.stringify(body),
  });
}

async function mockReadyPractice(
  page: Page,
  practice: unknown = practiceFixture,
) {
  await page.route(SESSION_PATTERN, (route) =>
    json(route, 201, {
      status: "ready",
      authentication_method: "single_profile",
      expires_at: "2026-10-16T18:00:00Z",
    }),
  );
  await page.route(PRACTICE_PATTERN, (route) =>
    json(route, 200, practice),
  );
}

test("opens every answer-safe response shape through the public API", async ({
  page,
}) => {
  let practiceRequest: { method: string; url: string; body: string | null } | null = null;
  await mockReadyPractice(page);
  await page.route(PRACTICE_PATTERN, (route) => {
    practiceRequest = {
      method: route.request().method(),
      url: route.request().url(),
      body: route.request().postData(),
    };
    return json(route, 200, practiceFixture);
  });

  await page.goto(PRACTICE_PATH);
  await expect(
    page.getByRole("heading", { level: 1, name: practiceFixture.title }),
  ).toBeVisible();
  await expect(page.getByRole("radio")).toHaveCount(2);
  await expect(page.getByRole("checkbox")).toHaveCount(3);
  await expect(page.getByLabel("Your answer (percent)")).toBeVisible();
  await expect(page.getByRole("button", { name: /check|submit|save/i })).toHaveCount(0);
  await expect(page.getByText(/does not check or save them yet/i)).toBeVisible();

  expect(practiceRequest).not.toBeNull();
  const captured = practiceRequest as unknown as {
    method: string;
    url: string;
    body: string | null;
  };
  expect(captured.method).toBe("GET");
  expect(new URL(captured.url).search).toBe("");
  expect(captured.body).toBeNull();

  await page.getByText("Technical record", { exact: true }).click();
  await expect(page.getByText(practiceFixture.definition_digest)).toBeVisible();
  await expect(page.getByText("risk-meaning", { exact: true })).toBeVisible();
  await expect(page.getByText("correct_option_id")).toHaveCount(0);

  const baselineText = await page.locator("main").innerText();
  await page.getByLabel("Theme").selectOption("light");
  const lightAccessibility = await new AxeBuilder({ page }).analyze();
  expect(lightAccessibility.violations).toEqual([]);

  await page.getByLabel("Theme").selectOption("dark");
  expect(await page.locator("main").innerText()).toBe(baselineText);
  const darkAccessibility = await new AxeBuilder({ page }).analyze();
  expect(darkAccessibility.violations).toEqual([]);

  await page.emulateMedia({ colorScheme: "dark" });
  await page.getByLabel("Theme").selectOption("system");
  expect(await page.locator("main").innerText()).toBe(baselineText);
});

test("preserves keyboard focus, narrow reflow, and forced-color meaning", async ({
  page,
}) => {
  await page.setViewportSize({ width: 375, height: 720 });
  await page.emulateMedia({ reducedMotion: "reduce", forcedColors: "active" });
  await mockReadyPractice(page);
  await page.goto(PRACTICE_PATH);

  await page.getByRole("radio", { name: /Outcomes can differ/i }).focus();
  await expect(page.getByRole("radio", { name: /Outcomes can differ/i })).toBeFocused();
  const outline = await page.getByRole("radio", { name: /Outcomes can differ/i }).evaluate(
    (element) => getComputedStyle(element).outlineStyle,
  );
  expect(outline).not.toBe("none");
  await page.keyboard.press("Space");
  await expect(page.getByRole("radio", { name: /Outcomes can differ/i })).toBeChecked();

  const dimensions = await page.evaluate(() => ({
    viewport: document.documentElement.clientWidth,
    content: document.documentElement.scrollWidth,
  }));
  expect(dimensions.content).toBeLessThanOrEqual(dimensions.viewport);
  const card = await page.locator("article").boundingBox();
  const rail = await page.getByRole("complementary", { name: "Practice activity details" }).boundingBox();
  expect(card).not.toBeNull();
  expect(rail).not.toBeNull();
  expect(rail?.y).toBeGreaterThan(card?.y ?? 0);
  expect(
    await page.evaluate(() =>
      getComputedStyle(document.documentElement)
        .getPropertyValue("--faa-duration-standard")
        .trim(),
    ),
  ).toBe("0ms");
});

test("shows a bounded denied state without requesting or revealing practice", async ({
  page,
}) => {
  let practiceRequested = false;
  await page.route(SESSION_PATTERN, (route) =>
    json(route, 403, {
      error_version: "1.0",
      code: "forbidden",
      message: "Request forbidden.",
      correlation_id: "00000000-0000-0000-0000-000000000000",
    }),
  );
  await page.route(PRACTICE_PATTERN, (route) => {
    practiceRequested = true;
    return json(route, 500, {});
  });

  await page.goto(PRACTICE_PATH);
  await expect(
    page.getByRole("heading", { name: "You don't have access to this activity" }),
  ).toBeVisible();
  await expect(page.getByText(practiceFixture.title)).toHaveCount(0);
  expect(practiceRequested).toBe(false);
});

test("fails the whole view closed when a private answer field appears", async ({
  page,
}) => {
  const invalid = structuredClone(practiceFixture) as unknown as {
    items: Array<Record<string, unknown>>;
  };
  invalid.items[0]!.correct_option_id = "uncertainty";
  await mockReadyPractice(page, invalid);

  await page.goto(PRACTICE_PATH);
  await expect(
    page.getByRole("heading", { name: "We couldn't show this activity safely" }),
  ).toBeVisible();
  await expect(page.getByText(practiceFixture.title)).toHaveCount(0);
  await expect(page.getByText("uncertainty", { exact: true })).toHaveCount(0);
});

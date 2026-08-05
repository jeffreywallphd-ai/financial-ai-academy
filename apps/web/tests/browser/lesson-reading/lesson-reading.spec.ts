import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";
import type { Page, Route } from "@playwright/test";

import { lessonFixture } from "../../component/lessonFixture";


const LESSON_PATH =
  "/learn/placements/intro-risk-return-primary";
const SESSION_PATTERN = "**/api/v1/session/single-profile";
const LESSON_PATTERN =
  "**/api/v1/curriculum/placements/*/lesson";

function json(route: Route, status: number, body: unknown) {
  return route.fulfill({
    status,
    contentType: "application/json",
    body: JSON.stringify(body),
  });
}

async function mockReadyLesson(
  page: Page,
  lesson: unknown = lessonFixture,
) {
  await page.route(SESSION_PATTERN, (route) =>
    json(route, 201, {
      status: "ready",
      authentication_method: "single_profile",
      expires_at: "2026-08-05T12:00:00Z",
    }),
  );
  await page.route(LESSON_PATTERN, (route) =>
    json(route, 200, lesson),
  );
  await page.route("**/api/v1/content/assets/risk-spectrum", (route) =>
    route.fulfill({
      status: 200,
      contentType: "image/png",
      body: Buffer.from(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJ" +
          "AAAADUlEQVR42mP8z8BQDwAFgwJ/lA2mWQAAAABJRU5ErkJggg==",
        "base64",
      ),
    }),
  );
}

test("renders equivalent light, dark, and system content accessibly", async ({
  page,
}) => {
  await mockReadyLesson(page);
  await page.goto(LESSON_PATH);
  const title = page.getByRole("heading", {
    level: 1,
    name: lessonFixture.title,
  });
  await expect(title).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "Learning objectives" }),
  ).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "Educational sources" }),
  ).toBeVisible();

  const baselineText = await page.locator("main").innerText();
  await page.getByLabel("Theme").selectOption("light");
  await expect(page.locator("html")).toHaveAttribute(
    "data-theme",
    "light",
  );
  await expect(page).toHaveScreenshot("lesson-light.png", {
    fullPage: true,
  });
  const lightAccessibility = await new AxeBuilder({ page }).analyze();
  expect(lightAccessibility.violations).toEqual([]);

  await page.getByLabel("Theme").selectOption("dark");
  await expect(page.locator("html")).toHaveAttribute(
    "data-theme",
    "dark",
  );
  await expect(page.locator("main")).toContainText(
    "Understanding Risk and Return",
  );
  expect(await page.locator("main").innerText()).toBe(baselineText);
  const darkAccessibility = await new AxeBuilder({ page }).analyze();
  expect(darkAccessibility.violations).toEqual([]);
  await expect(page).toHaveScreenshot("lesson-dark.png", {
    fullPage: true,
  });

  await page.emulateMedia({ colorScheme: "dark" });
  await page.getByLabel("Theme").selectOption("system");
  await expect(page.locator("html")).toHaveAttribute(
    "data-theme",
    "system",
  );
  expect(await page.locator("main").innerText()).toBe(baselineText);

  const accessibility = await new AxeBuilder({ page }).analyze();
  expect(accessibility.violations).toEqual([]);
});

test("preserves keyboard focus and safe external-source meaning", async ({
  page,
}) => {
  await mockReadyLesson(page);
  await page.goto(LESSON_PATH);
  await expect(
    page.getByRole("heading", { name: lessonFixture.title }),
  ).toBeVisible();

  await page.keyboard.press("Tab");
  await expect(page.getByRole("link", { name: "Skip to lesson" })).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(page.locator("#main-content")).toBeFocused();

  const source = page.getByRole("link", {
    name: /Introduction to investing.*opens in a new tab/i,
  });
  await source.focus();
  await expect(source).toBeFocused();
  await expect(source).toHaveAttribute("target", "_blank");
  await expect(source).toHaveAttribute("rel", "noopener noreferrer");
});

test("reflows at narrow and 200-percent-equivalent widths", async ({
  page,
}) => {
  await page.setViewportSize({ width: 375, height: 720 });
  await mockReadyLesson(page);
  await page.goto(LESSON_PATH);
  await expect(
    page.getByRole("heading", { name: lessonFixture.title }),
  ).toBeVisible();

  const dimensions = await page.evaluate(() => ({
    viewport: document.documentElement.clientWidth,
    content: document.documentElement.scrollWidth,
  }));
  expect(dimensions.content).toBeLessThanOrEqual(dimensions.viewport);
  const readingBox = await page.locator("article").boundingBox();
  const contextBox = await page.locator("aside").boundingBox();
  expect(readingBox).not.toBeNull();
  expect(contextBox).not.toBeNull();
  expect(contextBox?.y).toBeGreaterThan(readingBox?.y ?? 0);

  await page.setViewportSize({ width: 640, height: 900 });
  const zoomEquivalent = await page.evaluate(() => ({
    viewport: document.documentElement.clientWidth,
    content: document.documentElement.scrollWidth,
  }));
  expect(zoomEquivalent.content).toBeLessThanOrEqual(
    zoomEquivalent.viewport,
  );
});

test("honors reduced motion and forced colors with visible focus", async ({
  page,
}) => {
  await page.emulateMedia({
    reducedMotion: "reduce",
    forcedColors: "active",
  });
  await mockReadyLesson(page);
  await page.goto(LESSON_PATH);
  await expect(
    page.getByRole("heading", { name: lessonFixture.title }),
  ).toBeVisible();

  const duration = await page.evaluate(() =>
    getComputedStyle(document.documentElement)
      .getPropertyValue("--faa-duration-standard")
      .trim(),
  );
  expect(duration).toBe("0ms");
  const control = page.getByLabel("Theme");
  await control.focus();
  const outlineStyle = await control.evaluate(
    (element) => getComputedStyle(element).outlineStyle,
  );
  expect(outlineStyle).not.toBe("none");
});

test("shows loading then a bounded denied state without lesson details", async ({
  page,
}) => {
  let lessonRequested = false;
  await page.route(SESSION_PATTERN, async (route) => {
    await new Promise((resolve) => setTimeout(resolve, 400));
    await json(route, 403, {
      error_version: "1.0",
      code: "forbidden",
      message: "Request forbidden.",
      correlation_id: "00000000-0000-0000-0000-000000000000",
    });
  });
  await page.route(LESSON_PATTERN, (route) => {
    lessonRequested = true;
    return json(route, 500, {});
  });

  await page.goto(LESSON_PATH);
  await expect(
    page.getByRole("heading", { name: "Opening your lesson" }),
  ).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "Lesson access unavailable" }),
  ).toBeVisible();
  await expect(page.getByText(lessonFixture.title)).toHaveCount(0);
  expect(lessonRequested).toBe(false);
});

test("fails closed on an unknown content discriminator", async ({ page }) => {
  const invalid = structuredClone(lessonFixture) as unknown as {
    body: unknown[];
  };
  invalid.body.push({
    kind: "remote_embed",
    url: "https://attacker.invalid/embed",
  });
  await mockReadyLesson(page, invalid);

  await page.goto(LESSON_PATH);

  await expect(
    page.getByRole("heading", { name: "Lesson content unavailable" }),
  ).toBeVisible();
  await expect(page.getByText(lessonFixture.title)).toHaveCount(0);
  await expect(
    page.locator("main iframe, main video, main script"),
  ).toHaveCount(0);
});

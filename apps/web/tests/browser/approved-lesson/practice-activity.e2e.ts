import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";
import { writeFile } from "node:fs/promises";

import type { PracticePresentation } from "../../../src/features/practice-activity/model";


const PLACEMENT_ID = "intro-risk-return-practice";
const PRACTICE_PATH = `/learn/placements/${PLACEMENT_ID}/practice`;
const PRACTICE_API =
  `/api/v1/curriculum/placements/${PLACEMENT_ID}/practice`;
const SUBMISSION_API = `${PRACTICE_API}/submissions`;
const PROGRESS_API = `${PRACTICE_API}/progress`;
const DRAFT_API = `${PRACTICE_API}/draft`;

function nestedKeys(value: unknown): Set<string> {
  if (Array.isArray(value)) {
    return value.reduce((keys, item) => {
      for (const key of nestedKeys(item)) keys.add(key);
      return keys;
    }, new Set<string>());
  }
  if (typeof value === "object" && value !== null) {
    const keys = new Set<string>();
    for (const [key, item] of Object.entries(value)) {
      keys.add(key);
      for (const nested of nestedKeys(item)) keys.add(nested);
    }
    return keys;
  }
  return new Set<string>();
}

test("opens the same exact three-shape practice through the live public API", async ({
  context,
  page,
}) => {
  const practiceRequests: Array<{
    method: string;
    path: string;
    body: string | null;
  }> = [];
  page.on("request", (request) => {
    const path = new URL(request.url()).pathname;
    if (
      path === PRACTICE_API ||
      path === SUBMISSION_API ||
      path === PROGRESS_API ||
      path === DRAFT_API
    ) {
      practiceRequests.push({
        method: request.method(),
        path,
        body: request.postData(),
      });
    }
  });

  const response = await page.goto(PRACTICE_PATH);
  expect(response?.status()).toBe(200);
  expect(response?.headers()["content-security-policy"]).toContain(
    "default-src 'self'",
  );
  await expect(
    page.getByRole("heading", {
      level: 1,
      name: "Practice risk and return basics",
    }),
  ).toBeVisible();

  const apiResponse = await context.request.get(PRACTICE_API);
  expect(apiResponse.status()).toBe(200);
  const practice = (await apiResponse.json()) as PracticePresentation;
  expect(practice.placement_id).toBe(PLACEMENT_ID);
  expect(practice.package_version).toBe("2.0.0");
  expect(practice.items.map((item) => item.item_type)).toEqual([
    "single_select",
    "multiple_select",
    "numeric_entry",
  ]);
  expect(
    [...nestedKeys(practice)].filter((key) =>
      /^(answer|correct_option_ids?|feedback|scoring_policy)$/.test(key),
    ),
  ).toEqual([]);

  await expect(page.getByRole("radio")).toHaveCount(3);
  await expect(page.getByRole("checkbox")).toHaveCount(4);
  const numeric = page.getByLabel("Your answer (units)");
  await expect(numeric).toBeVisible();
  for (const invalid of ["01.00", "-0.00", "105", "1e2", "1,00"]) {
    await numeric.fill(invalid);
    expect(
      await numeric.evaluate((element: HTMLInputElement) =>
        element.checkValidity(),
      ),
    ).toBe(false);
  }
  await numeric.fill("105.00");
  expect(
    await numeric.evaluate((element: HTMLInputElement) =>
      element.checkValidity(),
    ),
  ).toBe(true);
  await expect(page.getByRole("button", { name: "Check answers" })).toBeVisible();

  await page.getByLabel("Outcomes can differ from what was expected.").check();
  const draftResponsePromise = page.waitForResponse(
    (draftResponse) =>
      new URL(draftResponse.url()).pathname === DRAFT_API &&
      draftResponse.request().method() === "PUT",
  );
  await page.getByRole("button", { name: "Save progress" }).click();
  const draftResponse = await draftResponsePromise;
  expect(draftResponse.status()).toBe(200);
  const draftRequestBody = draftResponse.request().postDataJSON();
  const draftResultBody = await draftResponse.json();
  await expect(page.getByRole("heading", { name: "Progress saved" })).toBeVisible();

  await page.reload();
  await expect(
    page.getByRole("heading", {
      level: 1,
      name: "Practice risk and return basics",
    }),
  ).toBeVisible();
  await expect(
    page.getByLabel("Outcomes can differ from what was expected."),
  ).toBeChecked();
  await expect(numeric).toHaveValue("105.00");

  await page.getByText("Technical record", { exact: true }).click();
  for (const exactFact of [
    practice.placement_id,
    practice.package_id,
    practice.package_version,
    practice.package_digest,
    practice.practice_id,
    practice.practice_version,
    practice.definition_digest,
    ...practice.items.map((item) => item.item_id),
  ]) {
    await expect(page.getByText(exactFact, { exact: true }).first()).toBeVisible();
  }

  const baselineText = await page.locator("main").innerText();
  await page.getByLabel("Theme").selectOption("light");
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  await page.getByLabel("Theme").selectOption("dark");
  expect(await page.locator("main").innerText()).toBe(baselineText);
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);

  await page.setViewportSize({ width: 375, height: 720 });
  await page.emulateMedia({ reducedMotion: "reduce", forcedColors: "active" });
  await page.getByRole("radio").first().focus();
  await expect(page.getByRole("radio").first()).toBeFocused();
  const dimensions = await page.evaluate(() => ({
    viewport: document.documentElement.clientWidth,
    content: document.documentElement.scrollWidth,
  }));
  expect(dimensions.content).toBeLessThanOrEqual(dimensions.viewport);

  await page.getByLabel("Hold assets from more than one issuer.").check();
  await page.getByLabel("Count the same position twice.").check();
  await numeric.fill("105.00");
  const submissionResponsePromise = page.waitForResponse(
    (submissionResponse) =>
      new URL(submissionResponse.url()).pathname === SUBMISSION_API &&
      submissionResponse.request().method() === "POST",
  );
  await page.getByRole("button", { name: "Check answers" }).click();
  const submissionResponse = await submissionResponsePromise;
  expect(submissionResponse.status()).toBe(200);
  const requestBody = submissionResponse.request().postDataJSON();
  const resultBody = await submissionResponse.json();

  const resultHeading = page.getByRole("heading", { name: "Your result" });
  await expect(resultHeading).toBeVisible();
  await expect(page.getByText("Some answers need review.")).toBeVisible();
  await expect(page.getByText("2 of 3", { exact: true })).toBeVisible();
  expect(
    await resultHeading.evaluate((element) =>
      document.activeElement?.contains(element),
    ),
  ).toBe(true);
  await expect(page.getByText("Question 1: Correct")).toBeVisible();
  await expect(page.getByText("Question 2: Review this question")).toBeVisible();
  await expect(page.getByText("Question 3: Correct")).toBeVisible();
  expect(
    [...nestedKeys(resultBody)].filter((key) =>
      /^(answer|correct_option_ids?|learner_id|request_fingerprint|scoring_policy)$/.test(
        key,
      ),
    ),
  ).toEqual([]);
  await page.emulateMedia({ reducedMotion: "reduce", forcedColors: "none" });
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);

  await expect(page.getByRole("heading", { name: "Attempt 1" })).toBeVisible();
  await expect(
    page.getByText(
      "Review risk and return is not available in this learning path.",
    ),
  ).toBeVisible();
  const progressResponse = await context.request.get(PROGRESS_API);
  expect(progressResponse.status()).toBe(200);
  const progressBody = await progressResponse.json();
  await page.getByRole("button", { name: "Try another attempt" }).click();
  await expect(
    page.getByLabel("Outcomes can differ from what was expected."),
  ).not.toBeChecked();
  await expect(numeric).toHaveValue("");
  await expect(page.getByRole("heading", { name: "Attempt 1" })).toBeVisible();

  const capturePath = process.env.FINANCIAL_AI_ACADEMY_PRACTICE_CAPTURE;
  if (capturePath) {
    await writeFile(
      capturePath,
      `${JSON.stringify(
        {
          draft_request: draftRequestBody,
          draft_result: draftResultBody,
          request: requestBody,
          result: resultBody,
          progress: progressBody,
        },
        null,
        2,
      )}\n`,
      { encoding: "utf-8", flag: "wx" },
    );
  }

  expect(practiceRequests.length).toBeGreaterThan(0);
  expect(
    practiceRequests.filter((request) => request.path === SUBMISSION_API),
  ).toEqual([
    {
      method: "POST",
      path: SUBMISSION_API,
      body: JSON.stringify(requestBody),
    },
  ]);
});

test("keeps live practice denials bounded and confidential", async ({
  context,
  page,
  request,
}) => {
  const unauthenticated = await request.get(PRACTICE_API);
  expect(unauthenticated.status()).toBe(401);
  expect(await unauthenticated.text()).not.toMatch(
    /answer|correct_option|feedback|learner_id|session_id|storage/i,
  );

  await page.goto(PRACTICE_PATH);
  await expect(
    page.getByRole("heading", {
      level: 1,
      name: "Practice risk and return basics",
    }),
  ).toBeVisible();
  const missing = await context.request.get(
    "/api/v1/curriculum/placements/not-a-practice/practice",
  );
  expect(missing.status()).toBe(404);
  expect(await missing.text()).not.toMatch(
    /answer|correct_option|feedback|learner_id|session_id|storage/i,
  );

  await page.goto("/learn/placements/not-a-practice/practice");
  await expect(
    page.getByRole("heading", { name: "Practice activity not found" }),
  ).toBeVisible();
  await expect(page.getByText("Practice risk and return basics")).toHaveCount(0);
});

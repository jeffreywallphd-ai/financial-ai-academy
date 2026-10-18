import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";
import type { Page, Route } from "@playwright/test";
import { readFile } from "node:fs/promises";

import {
  practiceFixture,
  practiceProgressFixture,
  practiceResultFixture,
} from "../../component/practiceFixture";
import type { PracticeProgress } from "../../../src/features/practice-activity/model";


const PRACTICE_PATH = "/learn/placements/intro-risk-return-primary/practice";
const SESSION_PATTERN = "**/api/v1/session/single-profile";
const PRACTICE_PATTERN = "**/api/v1/curriculum/placements/*/practice";
const SUBMISSION_PATTERN =
  "**/api/v1/curriculum/placements/*/practice/submissions";
const PROGRESS_PATTERN =
  "**/api/v1/curriculum/placements/*/practice/progress";
const DRAFT_PATTERN =
  "**/api/v1/curriculum/placements/*/practice/draft";

function json(route: Route, status: number, body: unknown) {
  return route.fulfill({
    status,
    contentType: "application/json",
    body: JSON.stringify(body),
  });
}

async function installFeatureGuidance(page: Page) {
  const root = new URL(
    "../../../../../backend/src/financial_ai_academy/modules/guidance/resources/feature-guidance/v1/",
    import.meta.url,
  );
  const [mapping, guidance] = await Promise.all([
    readFile(new URL("mappings/practice-activity-write-outcome-uncertain.json", root), "utf8").then(JSON.parse),
    readFile(new URL("records/practice-write-uncertain.json", root), "utf8").then(JSON.parse),
  ]);
  await page.route("**/api/v1/guidance/feature-guidance/**", (route) =>
    json(route, 200, { mapping, guidance }),
  );
}

async function mockReadyPractice(
  page: Page,
  practice: unknown = practiceFixture,
  progress: unknown = {
    ...structuredClone(practiceProgressFixture),
    draft: null,
    retry_state: {
      ...structuredClone(practiceProgressFixture.retry_state),
      attempts_used: 0,
      attempts_remaining: 3,
    },
    history: {
      ...structuredClone(practiceProgressFixture.history),
      attempts: [],
    },
    review_targets: [],
  },
) {
  await page.route(SESSION_PATTERN, (route) =>
    json(route, 201, {
      status: "ready",
      authentication_method: "single_profile",
      expires_at: "2026-10-16T18:00:00Z",
    }),
  );
  await page.route(PRACTICE_PATTERN, (route) => json(route, 200, practice));
  await page.route(PROGRESS_PATTERN, (route) => json(route, 200, progress));
  await page.route(DRAFT_PATTERN, (route) => {
    const body = route.request().postDataJSON() as Record<string, unknown>;
    return json(route, 200, {
      ...body,
      expected_revision: undefined,
      revision: Number(body.expected_revision) + 1,
      saved_at: "2026-10-16T17:00:00Z",
      response_fingerprint: "e".repeat(64),
    });
  });
}

async function answerEveryQuestion(page: Page) {
  await page.getByRole("radio", { name: /Outcomes can differ/i }).check();
  for (const checkbox of await page.getByRole("checkbox").all()) {
    await checkbox.check();
  }
  await page.getByLabel("Your answer (percent)").fill("5.00");
}

test("submits every response shape through the public API and shows the saved result", async ({
  page,
}) => {
  let openingRequest: { method: string; url: string; body: string | null } | null = null;
  let submittedBody: Record<string, unknown> | null = null;
  await mockReadyPractice(page);
  await page.route(PRACTICE_PATTERN, (route) => {
    openingRequest = {
      method: route.request().method(),
      url: route.request().url(),
      body: route.request().postData(),
    };
    return json(route, 200, practiceFixture);
  });
  await page.route(SUBMISSION_PATTERN, async (route) => {
    submittedBody = route.request().postDataJSON() as Record<string, unknown>;
    return json(route, 200, {
      ...practiceResultFixture,
      submission_id: submittedBody.submission_id,
    });
  });

  await page.goto(PRACTICE_PATH);
  await expect(page.getByRole("heading", { level: 1, name: practiceFixture.title })).toBeVisible();
  await expect(page.getByRole("radio")).toHaveCount(2);
  await expect(page.getByRole("checkbox")).toHaveCount(3);
  await expect(page.getByLabel("Your answer (percent)")).toBeVisible();
  await expect(page.getByRole("button", { name: "Check answers" })).toBeVisible();

  expect(openingRequest).not.toBeNull();
  const captured = openingRequest as unknown as {
    method: string;
    url: string;
    body: string | null;
  };
  expect(captured.method).toBe("GET");
  expect(new URL(captured.url).search).toBe("");
  expect(captured.body).toBeNull();

  await answerEveryQuestion(page);
  await page.getByRole("button", { name: "Check answers" }).click();
  await expect(page.getByRole("heading", { name: "Your result" })).toBeVisible();
  await expect(page.getByText("2 of 3")).toBeVisible();
  await expect(page.getByText(/does not show mastery, certification/i)).toBeVisible();
  expect(submittedBody).not.toBeNull();
  const requestBody = submittedBody as unknown as Record<string, unknown>;
  expect(requestBody).not.toHaveProperty("learner_id");
  expect(requestBody.responses).toEqual([
    expect.objectContaining({ item_type: "single_select", selected_option_id: "uncertainty" }),
    expect.objectContaining({ item_type: "multiple_select", selected_option_ids: ["time", "market", "fees"] }),
    expect.objectContaining({ item_type: "numeric_entry", entered_value: "5.00" }),
  ]);

  await page.getByLabel("Technical record for saved practice result").click();
  await expect(page.getByText(practiceResultFixture.evidence_id)).toBeVisible();
  await expect(page.getByText("correct_option_id")).toHaveCount(0);
  await expect(page.getByText("answer key", { exact: false })).toHaveCount(0);

  const baselineText = await page.locator("main").innerText();
  await page.getByLabel("Theme").selectOption("light");
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  await page.getByLabel("Theme").selectOption("dark");
  expect(await page.locator("main").innerText()).toBe(baselineText);
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  await page.emulateMedia({ colorScheme: "dark" });
  await page.getByLabel("Theme").selectOption("system");
  expect(await page.locator("main").innerText()).toBe(baselineText);
});

test("requires a complete response and focuses the first question", async ({ page }) => {
  let submitted = false;
  await mockReadyPractice(page);
  await page.route(SUBMISSION_PATTERN, (route) => {
    submitted = true;
    return json(route, 500, {});
  });
  await page.goto(PRACTICE_PATH);

  await page.getByRole("button", { name: "Check answers" }).click();

  await expect(page.getByRole("alert")).toContainText("Complete this question");
  await expect(page.getByRole("radio", { name: /Outcomes can differ/i })).toBeFocused();
  expect(submitted).toBe(false);
});

test("resumes, saves, reviews, and compares through the public progress API", async ({
  page,
}) => {
  let savedBody: Record<string, unknown> | null = null;
  await mockReadyPractice(page, practiceFixture, practiceProgressFixture);
  await page.unroute(DRAFT_PATTERN);
  await page.route(DRAFT_PATTERN, (route) => {
    savedBody = route.request().postDataJSON() as Record<string, unknown>;
    const { expected_revision: expectedRevision, ...scope } = savedBody;
    return json(route, 200, {
      ...scope,
      revision: Number(expectedRevision) + 1,
      saved_at: "2026-10-16T17:00:00Z",
      response_fingerprint: "e".repeat(64),
    });
  });

  await page.goto(PRACTICE_PATH);

  await expect(page.getByRole("radio", { name: /Outcomes can differ/i })).toBeChecked();
  await expect(page.getByLabel("Your answer (percent)")).toHaveValue("4.50");
  await expect(page.getByRole("heading", { name: "Attempt 1" })).toBeVisible();
  await expect(page.getByRole("link", { name: "Open Review risk and return" })).toHaveAttribute(
    "href",
    "/learn/placements/intro-risk-return-primary",
  );

  await page.getByRole("button", { name: "Save progress" }).click();
  await expect(page.getByRole("heading", { name: "Progress saved" })).toBeVisible();
  expect(savedBody).not.toBeNull();
  expect(savedBody).toMatchObject({
    expected_revision: 1,
    placement_id: practiceFixture.placement_id,
  });
  expect(savedBody).not.toHaveProperty("learner_id");
  const capturedSave = savedBody as unknown as { responses: unknown[] };
  expect(capturedSave.responses).toHaveLength(2);

  await page.getByText("Technical record for attempt 1").click();
  await expect(page.getByText(practiceProgressFixture.history.attempts[0]!.evidence_id)).toBeVisible();
  await expect(page.getByText("answer key", { exact: false })).toHaveCount(0);
});

test("shows retained history without mutation controls when attempts are exhausted", async ({
  page,
}) => {
  const firstAttempt = structuredClone(
    practiceProgressFixture.history.attempts[0]!,
  );
  const exhausted: PracticeProgress = {
    ...structuredClone(practiceProgressFixture),
    draft: null,
    retry_state: {
      ...structuredClone(practiceProgressFixture.retry_state),
      attempts_used: 3,
      attempts_remaining: 0,
      can_retry: false,
      state: "exhausted",
    },
    history: {
      ...structuredClone(practiceProgressFixture.history),
      attempts: [
        firstAttempt,
        {
          ...structuredClone(firstAttempt),
          attempt_order: 2,
          event_id: "44444444-4444-4444-8444-444444444445",
          attempt_id: "55555555-5555-4555-8555-555555555556",
          evidence_id: "66666666-6666-4666-8666-666666666667",
          submission_id: "77777777-7777-4777-8777-777777777778",
          completed_at: "2026-10-16T15:10:00Z",
        },
        {
          ...structuredClone(firstAttempt),
          attempt_order: 3,
          event_id: "44444444-4444-4444-8444-444444444446",
          attempt_id: "55555555-5555-4555-8555-555555555557",
          evidence_id: "66666666-6666-4666-8666-666666666668",
          submission_id: "77777777-7777-4777-8777-777777777779",
          completed_at: "2026-10-16T15:20:00Z",
        },
      ],
    },
  };
  await mockReadyPractice(page, practiceFixture, exhausted);

  await page.goto(PRACTICE_PATH);

  await expect(page.getByRole("heading", { name: "All attempts are complete" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Save progress" })).toHaveCount(0);
  await expect(page.getByRole("button", { name: "Check answers" })).toHaveCount(0);
  await expect(page.getByRole("heading", { name: "Attempt 1" })).toBeVisible();
});

test("fails the whole opening closed when progress includes private authority", async ({
  page,
}) => {
  await mockReadyPractice(page, practiceFixture, {
    ...structuredClone(practiceProgressFixture),
    learner_id: "private-learner",
  });

  await page.goto(PRACTICE_PATH);

  await expect(page.getByRole("heading", { name: "We couldn't show this activity safely" })).toBeVisible();
  await expect(page.getByText("private-learner")).toHaveCount(0);
  await expect(page.getByText(practiceFixture.title)).toHaveCount(0);
});

test("retries one exact prepared request after an uncertain failure", async ({ page }) => {
  const bodies: string[] = [];
  await mockReadyPractice(page);
  await installFeatureGuidance(page);
  await page.route(SUBMISSION_PATTERN, (route) => {
    const body = route.request().postData() ?? "";
    bodies.push(body);
    if (bodies.length === 1) {
      return json(route, 503, {
        error_version: "1.0",
        code: "unavailable",
        message: "Temporarily unavailable.",
        correlation_id: "00000000-0000-0000-0000-000000000000",
      });
    }
    const parsed = JSON.parse(body) as Record<string, unknown>;
    return json(route, 200, {
      ...practiceResultFixture,
      submission_id: parsed.submission_id,
    });
  });
  await page.goto(PRACTICE_PATH);
  await answerEveryQuestion(page);
  await page.getByRole("button", { name: "Check answers" }).click();

  await expect(page.getByRole("alert")).toContainText(/reuse the same answers/i);
  await expect(page.getByRole("heading", { name: "The practice result is not confirmed" })).toBeVisible();
  await expect(page.getByRole("radio", { name: /Outcomes can differ/i })).toBeDisabled();
  await page.getByRole("button", { name: "Try again" }).click();
  await expect(page.getByRole("heading", { name: "Your result" })).toBeVisible();
  expect(bodies).toHaveLength(2);
  expect(bodies[1]).toBe(bodies[0]);
});

test("renews an expired session once and keeps the exact submission", async ({ page }) => {
  let sessionCalls = 0;
  const bodies: string[] = [];
  await page.route(SESSION_PATTERN, (route) => {
    sessionCalls += 1;
    return json(route, 201, {
      status: "ready",
      authentication_method: "single_profile",
      expires_at: "2026-10-16T18:00:00Z",
    });
  });
  await page.route(PRACTICE_PATTERN, (route) => json(route, 200, practiceFixture));
  await page.route(PROGRESS_PATTERN, (route) =>
    json(route, 200, practiceProgressFixture),
  );
  await page.route(SUBMISSION_PATTERN, (route) => {
    const body = route.request().postData() ?? "";
    bodies.push(body);
    if (bodies.length === 1) {
      return json(route, 401, {
        error_version: "1.0",
        code: "unauthorized_context",
        message: "The learner session ended.",
        correlation_id: "00000000-0000-0000-0000-000000000000",
      });
    }
    const parsed = JSON.parse(body) as Record<string, unknown>;
    return json(route, 200, {
      ...practiceResultFixture,
      submission_id: parsed.submission_id,
    });
  });

  await page.goto(PRACTICE_PATH);
  await answerEveryQuestion(page);
  await page.getByRole("button", { name: "Check answers" }).click();

  await expect(page.getByRole("heading", { name: "Your result" })).toBeVisible();
  expect(sessionCalls).toBe(2);
  expect(bodies).toHaveLength(2);
  expect(bodies[1]).toBe(bodies[0]);
});

test("explains an existing completed attempt without claiming another result", async ({ page }) => {
  await mockReadyPractice(page);
  await page.route(SUBMISSION_PATTERN, (route) =>
    json(route, 409, {
      error_version: "1.0",
      code: "already_completed",
      message: "A completed practice attempt already exists.",
      correlation_id: "00000000-0000-0000-0000-000000000000",
    }),
  );
  await page.goto(PRACTICE_PATH);
  await answerEveryQuestion(page);
  await page.getByRole("button", { name: "Check answers" }).click();

  await expect(page.getByRole("alert")).toContainText(/already saved/i);
  await expect(page.getByText("2 of 3")).toHaveCount(0);
  await expect(page.getByRole("button", { name: "Try again" })).toHaveCount(0);
});

test("preserves keyboard focus, narrow reflow, and forced-color meaning", async ({ page }) => {
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
  const card = await page.locator("article").first().boundingBox();
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

test("shows a bounded denied state without requesting or revealing practice", async ({ page }) => {
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
  await expect(page.getByRole("heading", { name: "You don't have access to this activity" })).toBeVisible();
  await expect(page.getByText(practiceFixture.title)).toHaveCount(0);
  expect(practiceRequested).toBe(false);
});

test("fails the whole opening or result closed when a private field appears", async ({ page }) => {
  const invalidOpening = structuredClone(practiceFixture) as unknown as {
    items: Array<Record<string, unknown>>;
  };
  invalidOpening.items[0]!.correct_option_id = "uncertainty";
  await mockReadyPractice(page, invalidOpening);
  await page.goto(PRACTICE_PATH);
  await expect(page.getByRole("heading", { name: "We couldn't show this activity safely" })).toBeVisible();
  await expect(page.getByText(practiceFixture.title)).toHaveCount(0);

  await page.unroute(PRACTICE_PATTERN);
  await mockReadyPractice(page);
  await page.route(SUBMISSION_PATTERN, (route) => {
    const body = route.request().postDataJSON() as Record<string, unknown>;
    return json(route, 200, {
      ...practiceResultFixture,
      submission_id: body.submission_id,
      learner_id: "private-learner",
    });
  });
  await page.goto(PRACTICE_PATH);
  await answerEveryQuestion(page);
  await page.getByRole("button", { name: "Check answers" }).click();
  await expect(page.getByRole("alert")).toContainText(/couldn't safely show the result/i);
  await expect(page.getByText("private-learner")).toHaveCount(0);
  await expect(page.getByText("2 of 3")).toHaveCount(0);
});

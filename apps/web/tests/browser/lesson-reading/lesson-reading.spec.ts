import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";
import type { Page, Route } from "@playwright/test";
import { readFile } from "node:fs/promises";

import { lessonFixture } from "../../component/lessonFixture";
import {
  contextualHelpFixture,
  platformHelpTopicFixture,
} from "../../component/platformHelpFixture";

const LESSON_PATH = "/learn/placements/intro-risk-return-primary";
const SESSION_PATTERN = "**/api/v1/session/single-profile";
const LESSON_PATTERN = "**/api/v1/curriculum/placements/*/lesson";
const COMPLETION_PATTERN = "**/api/v1/curriculum/placements/*/completion";
const KNOWLEDGE_CHECK_PATTERN =
  "**/api/v1/curriculum/placements/*/knowledge-check**";
const CONTEXTUAL_HELP_PATTERN =
  "**/api/v1/guidance/contextual-help/*/versions/*";
const HELP_TOPIC_PATTERN = "**/api/v1/guidance/platform-help/*/versions/*";
const ACCOUNTABLE_HISTORY_PATTERN = "**/api/v1/audit/accountable-history";
const ACCOUNTABLE_HISTORY_EXPORT_PATTERN =
  "**/api/v1/audit/accountable-history/export";
const KNOWLEDGE_CHECK = {
  schema_version: "1.0.0",
  placement_id: "intro-risk-return-primary",
  package_id: "intro-risk-return",
  package_version: "1.1.0",
  package_digest: "a".repeat(64),
  assessment_id: "risk-return-check-1",
  assessment_version: "1.0.0",
  definition_digest: "b".repeat(64),
  item_type: "single_select",
  item_id: "risk-return-question-1",
  item_version: "1.0.0",
  scoring_policy_id: "single-select-exact-match",
  scoring_policy_version: "1.0.0",
  prompt: "Which statement best describes risk and return?",
  options: [
    {
      option_id: "higher-potential-higher-uncertainty",
      label: "Higher potential return generally comes with higher uncertainty.",
    },
    {
      option_id: "higher-risk-guarantees-return",
      label: "Taking more risk guarantees a higher return.",
    },
  ],
};
const INCOMPLETE_COMPLETION = {
  projection_version: "1.0.0",
  placement_id: "intro-risk-return-primary",
  completed: false,
  completion_meaning: "not_completed",
  source_digest: "c".repeat(64),
  rebuilt_at: "2026-10-15T12:00:00Z",
  history: [],
};
const COMPLETION_ENTRY = {
  event_id: "77777777-7777-4777-8777-777777777777",
  attempt_id: "55555555-5555-4555-8555-555555555555",
  evidence_id: "66666666-6666-4666-8666-666666666666",
  package_id: KNOWLEDGE_CHECK.package_id,
  package_version: KNOWLEDGE_CHECK.package_version,
  package_digest: KNOWLEDGE_CHECK.package_digest,
  assessment_id: KNOWLEDGE_CHECK.assessment_id,
  assessment_version: KNOWLEDGE_CHECK.assessment_version,
  definition_digest: KNOWLEDGE_CHECK.definition_digest,
  item_id: KNOWLEDGE_CHECK.item_id,
  item_version: KNOWLEDGE_CHECK.item_version,
  scoring_policy_id: KNOWLEDGE_CHECK.scoring_policy_id,
  scoring_policy_version: KNOWLEDGE_CHECK.scoring_policy_version,
  score: 1,
  max_score: 1,
  completed_at: "2026-10-15T12:00:00Z",
};
const COMPLETED_COMPLETION = {
  ...INCOMPLETE_COMPLETION,
  completed: true,
  completion_meaning: "bounded_knowledge_check_completed",
  history: [COMPLETION_ENTRY],
};

function accountableHistory(
  rootRequest: Record<string, unknown>,
  purpose: "learner_review" | "portable_evidence" = "learner_review",
) {
  const completion = rootRequest.root_kind === "knowledge_check_completion";
  return {
    schema_version: "1.0.0",
    purpose,
    root: completion
      ? {
          root_kind: "knowledge_check_completion",
          resource_id: rootRequest.evidence_id,
          occurrence: rootRequest.occurrence,
        }
      : {
          root_kind: "published_lesson",
          resource_id: rootRequest.package_id,
          resource_version: rootRequest.package_version,
        },
    state: "valid",
    title:
      purpose === "portable_evidence"
        ? "Portable evidence record"
        : "Source and history",
    summary: "This view shows the available source and history.",
    source_lineage_digest: "1".repeat(64),
    entries: [
      completion
        ? {
            sequence: 1,
            entry_id: "completion-evidence",
            role: "recorded",
            title: "Saved learning evidence",
            explanation: "The completed check was saved as learning evidence.",
            owner_module: "assessment",
            resource_kind: "completion_evidence",
            resource_id: rootRequest.evidence_id,
            occurrence: rootRequest.occurrence,
            integrity_digest: "2".repeat(64),
            recorded_at: "2026-10-15T12:00:00Z",
            validation_status: "validated",
          }
        : {
            sequence: 1,
            entry_id: "published-lesson",
            role: "published",
            title: "Published lesson",
            explanation:
              "This reviewed lesson version was published for learning.",
            owner_module: "content",
            resource_kind: "published_lesson",
            resource_id: rootRequest.package_id,
            resource_version: rootRequest.package_version,
            integrity_digest: "2".repeat(64),
            recorded_at: "2026-10-15T12:00:00Z",
            validation_status: "validated",
          },
    ],
    transformations: [],
    missing_links: [],
    diagnostics: [],
    redactions: [{ category: "owner_payload", count: 1 }],
    history_digest:
      purpose === "portable_evidence" ? "4".repeat(64) : "3".repeat(64),
  };
}

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
    readFile(
      new URL("mappings/lesson-reading-exact-version-unavailable.json", root),
      "utf8",
    ).then(JSON.parse),
    readFile(
      new URL("records/lesson-version-unavailable.json", root),
      "utf8",
    ).then(JSON.parse),
  ]);
  await page.route("**/api/v1/guidance/feature-guidance/**", (route) =>
    json(route, 200, { mapping, guidance }),
  );
}

async function mockReadyLesson(
  page: Page,
  lesson: unknown = lessonFixture,
  completion: unknown = INCOMPLETE_COMPLETION,
  contextualHelp: unknown | null = null,
) {
  await page.route(SESSION_PATTERN, (route) =>
    json(route, 201, {
      status: "ready",
      authentication_method: "single_profile",
      expires_at: "2026-08-05T12:00:00Z",
    }),
  );
  await page.route(LESSON_PATTERN, (route) => json(route, 200, lesson));
  await page.route(COMPLETION_PATTERN, (route) => json(route, 200, completion));
  await page.route(KNOWLEDGE_CHECK_PATTERN, (route) => {
    if (route.request().method() === "POST") {
      const request = route.request().postDataJSON() as {
        submission_id: string;
        selected_option_id: string;
      };
      return json(route, 200, {
        attempt_id: "55555555-5555-4555-8555-555555555555",
        evidence_id: "66666666-6666-4666-8666-666666666666",
        submission_id: request.submission_id,
        ...KNOWLEDGE_CHECK,
        selected_option_id: request.selected_option_id,
        score:
          request.selected_option_id === "higher-potential-higher-uncertainty"
            ? 1
            : 0,
        max_score: 1,
        correct:
          request.selected_option_id === "higher-potential-higher-uncertainty",
        feedback: {
          feedback_id: "risk-return-correct",
          text: "Correct. Risk and potential return should be considered together.",
        },
        submitted_at: "2026-10-15T12:00:00Z",
      });
    }
    return json(route, 200, KNOWLEDGE_CHECK);
  });
  await page.route(CONTEXTUAL_HELP_PATTERN, (route) =>
    contextualHelp === null
      ? json(route, 404, { code: "contextual_help_unavailable" })
      : json(route, 200, contextualHelp),
  );
  await page.route(HELP_TOPIC_PATTERN, (route) => {
    const match = /platform-help\/([^/]+)\/versions\/([^/?]+)/.exec(
      route.request().url(),
    );
    return json(route, 200, {
      ...platformHelpTopicFixture,
      topic_id: match?.[1] ?? "source-and-history",
      topic_version: match?.[2] ?? "1.0.0",
      title: "Source and history",
      related_topics: [],
    });
  });
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

test("opens exact contextual Help and returns to the unchanged lesson", async ({
  page,
}) => {
  await mockReadyLesson(
    page,
    lessonFixture,
    INCOMPLETE_COMPLETION,
    contextualHelpFixture,
  );
  await page.goto(LESSON_PATH);

  const contextualLink = page.getByRole("link", {
    name: "How to use source and history details",
  });
  await expect(contextualLink).toBeVisible();
  await contextualLink.click();
  await expect(
    page.getByRole("heading", { name: "Source and history" }),
  ).toBeVisible();
  await expect(
    page.getByRole("link", { name: "Return to lesson" }),
  ).toBeVisible();
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);

  await page.getByRole("link", { name: "Return to lesson" }).click();
  await expect(page).toHaveURL(LESSON_PATH);
  await expect(
    page.getByRole("heading", { name: lessonFixture.title }),
  ).toBeVisible();
});

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
  await expect(
    page.getByRole("heading", { name: "Knowledge check" }),
  ).toBeVisible();

  const baselineText = await page.locator("main").innerText();
  await page.getByLabel("Theme").selectOption("light");
  await expect(page.locator("html")).toHaveAttribute("data-theme", "light");
  await expect(page).toHaveScreenshot("lesson-light.png", {
    fullPage: true,
  });
  const lightAccessibility = await new AxeBuilder({ page }).analyze();
  expect(lightAccessibility.violations).toEqual([]);

  await page.getByLabel("Theme").selectOption("dark");
  await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
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
  await expect(page.locator("html")).toHaveAttribute("data-theme", "system");
  expect(await page.locator("main").innerText()).toBe(baselineText);

  const accessibility = await new AxeBuilder({ page }).analyze();
  expect(accessibility.violations).toEqual([]);

  await page
    .getByRole("complementary", { name: "Publication details" })
    .getByText("Technical record", { exact: true })
    .click();
  await expect(
    page.getByText(lessonFixture.package_version, { exact: true }),
  ).toBeVisible();
  await expect(
    page.getByText(lessonFixture.package_digest, { exact: true }),
  ).toBeVisible();
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
  await expect(
    page.getByRole("link", { name: "Skip to lesson" }),
  ).toBeFocused();
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

test("shows and downloads exact lesson history only after the learner asks", async ({
  page,
}) => {
  let readRequest: Record<string, unknown> | null = null;
  let exportRequest: Record<string, unknown> | null = null;
  await mockReadyLesson(page);
  await page.route(ACCOUNTABLE_HISTORY_PATTERN, (route) => {
    readRequest = route.request().postDataJSON() as Record<string, unknown>;
    return json(route, 200, accountableHistory(readRequest));
  });
  await page.route(ACCOUNTABLE_HISTORY_EXPORT_PATTERN, (route) => {
    exportRequest = route.request().postDataJSON() as Record<string, unknown>;
    const document = accountableHistory(exportRequest, "portable_evidence");
    return json(route, 200, {
      schema_version: "1.0.0",
      media_type:
        "application/vnd.financial-ai-academy.accountable-history+json",
      filename_stem: "lesson-1234abcd",
      exported_at: "2026-10-15T12:05:00Z",
      document_digest: document.history_digest,
      document,
    });
  });

  await page.goto(LESSON_PATH);
  expect(readRequest).toBeNull();
  const panel = page.getByRole("region", {
    name: "Source and history for lesson",
  });
  await panel.getByRole("button", { name: "Show source and history" }).click();

  await expect(panel.getByText("Available history")).toBeVisible();
  expect(readRequest).toEqual({
    schema_version: "1.0.0",
    root_kind: "published_lesson",
    package_id: lessonFixture.package_id,
    package_version: lessonFixture.package_version,
    package_digest: lessonFixture.package_digest,
  });
  expect(readRequest).not.toHaveProperty("learner_id");
  await panel.getByText("Technical record").click();
  await expect(
    panel.getByText(lessonFixture.package_digest, { exact: true }),
  ).toHaveCount(0);
  await expect(
    panel.getByText("published_lesson", { exact: true }).first(),
  ).toBeVisible();

  const download = page.waitForEvent("download");
  await panel.getByRole("button", { name: "Download evidence record" }).click();
  expect((await download).suggestedFilename()).toBe("lesson-1234abcd.json");
  expect(exportRequest).toEqual(readRequest);
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
});

test("submits the exact knowledge check without client learner authority", async ({
  page,
}) => {
  let requestBody: Record<string, unknown> | null = null;
  await mockReadyLesson(page);
  await page.route(KNOWLEDGE_CHECK_PATTERN, async (route) => {
    if (route.request().method() !== "POST") {
      return route.fallback();
    }
    requestBody = route.request().postDataJSON() as Record<string, unknown>;
    return json(route, 200, {
      attempt_id: "55555555-5555-4555-8555-555555555555",
      evidence_id: "66666666-6666-4666-8666-666666666666",
      submission_id: requestBody.submission_id,
      ...KNOWLEDGE_CHECK,
      selected_option_id: requestBody.selected_option_id,
      score: 1,
      max_score: 1,
      correct: true,
      feedback: {
        feedback_id: "risk-return-correct",
        text: "Correct. Risk and potential return should be considered together.",
      },
      submitted_at: "2026-10-15T12:00:00Z",
    });
  });

  await page.goto(LESSON_PATH);
  await page.getByRole("radio", { name: /Higher potential return/i }).check();
  await page.getByRole("button", { name: "Check answer" }).click();

  await expect(
    page.getByRole("heading", { name: "Knowledge check complete" }),
  ).toBeVisible();
  expect(requestBody).not.toBeNull();
  expect(requestBody).not.toHaveProperty("learner_id");
  const submittedId = String(
    (requestBody as unknown as Record<string, unknown>).submission_id,
  );
  await expect(
    page.getByText(/does not show mastery or certification/i),
  ).toBeVisible();

  const checkedAnswerRecord = page.getByLabel(
    "Technical record for checked answer",
  );
  await checkedAnswerRecord.click();
  const checkedAnswerDetails = checkedAnswerRecord.locator("..");
  for (const exactFact of [
    KNOWLEDGE_CHECK.schema_version,
    KNOWLEDGE_CHECK.placement_id,
    KNOWLEDGE_CHECK.package_digest,
    KNOWLEDGE_CHECK.definition_digest,
    "55555555-5555-4555-8555-555555555555",
    "66666666-6666-4666-8666-666666666666",
    submittedId,
    "2026-10-15T12:00:00Z",
    "risk-return-correct",
  ]) {
    await expect(
      checkedAnswerDetails.getByText(exactFact, { exact: true }),
    ).toBeVisible();
  }
  for (const versionedFact of [
    `${KNOWLEDGE_CHECK.package_id} version ${KNOWLEDGE_CHECK.package_version}`,
    `${KNOWLEDGE_CHECK.assessment_id} version ${KNOWLEDGE_CHECK.assessment_version}`,
    `${KNOWLEDGE_CHECK.item_id} version ${KNOWLEDGE_CHECK.item_version}`,
    `${KNOWLEDGE_CHECK.scoring_policy_id} version ${KNOWLEDGE_CHECK.scoring_policy_version}`,
  ]) {
    await expect(
      checkedAnswerDetails.getByText(versionedFact, { exact: true }),
    ).toBeVisible();
  }
  await expect(
    page.getByText(KNOWLEDGE_CHECK.options[0]!.option_id),
  ).toHaveCount(0);
});

test("reopens exact saved completion accessibly without another assessment request", async ({
  page,
}) => {
  let knowledgeCheckRequests = 0;
  let historyRequest: Record<string, unknown> | null = null;
  await mockReadyLesson(page, lessonFixture, COMPLETED_COMPLETION);
  await page.route(KNOWLEDGE_CHECK_PATTERN, (route) => {
    knowledgeCheckRequests += 1;
    return route.fallback();
  });
  await page.route(ACCOUNTABLE_HISTORY_PATTERN, (route) => {
    historyRequest = route.request().postDataJSON() as Record<string, unknown>;
    return json(route, 200, accountableHistory(historyRequest));
  });

  await page.goto(LESSON_PATH);
  await expect(
    page.getByRole("heading", { name: "Saved lesson completion" }),
  ).toBeVisible();
  await expect(page.getByText("1 of 1", { exact: true })).toBeVisible();
  await page.getByLabel("Technical record for saved completion").click();
  await page.getByLabel("Technical record for saved result 1").click();
  await expect(
    page.getByText(COMPLETION_ENTRY.package_digest, { exact: true }),
  ).toBeVisible();
  await expect(
    page.getByText(COMPLETION_ENTRY.definition_digest, { exact: true }),
  ).toBeVisible();
  await expect(
    page.getByText(COMPLETION_ENTRY.event_id, { exact: true }),
  ).toBeVisible();
  await expect(page.getByText(/not a mastery or certification/i)).toBeVisible();
  await expect(
    page.getByText(/does not provide investment advice/i),
  ).toBeVisible();
  await expect(page.getByRole("radio")).toHaveCount(0);
  expect(knowledgeCheckRequests).toBe(0);

  const historyPanel = page.getByRole("region", {
    name: "Source and history for saved result 1",
  });
  await historyPanel
    .getByRole("button", { name: "Show source and history" })
    .click();
  await expect(historyPanel.getByText("Available history")).toBeVisible();
  expect(historyRequest).toEqual({
    schema_version: "1.0.0",
    root_kind: "knowledge_check_completion",
    placement_id: COMPLETED_COMPLETION.placement_id,
    evidence_id: COMPLETION_ENTRY.evidence_id,
    occurrence: 1,
  });
  expect(historyRequest).not.toHaveProperty("learner_id");

  await page.getByLabel("Theme").selectOption("light");
  const lightText = await page.locator("main").innerText();
  const lightAccessibility = await new AxeBuilder({ page }).analyze();
  expect(lightAccessibility.violations).toEqual([]);

  await page.getByLabel("Theme").selectOption("dark");
  expect(await page.locator("main").innerText()).toBe(lightText);
  const darkAccessibility = await new AxeBuilder({ page }).analyze();
  expect(darkAccessibility.violations).toEqual([]);

  await page.setViewportSize({ width: 375, height: 720 });
  const dimensions = await page.evaluate(() => ({
    viewport: document.documentElement.clientWidth,
    content: document.documentElement.scrollWidth,
  }));
  expect(dimensions.content).toBeLessThanOrEqual(dimensions.viewport);
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
  expect(zoomEquivalent.content).toBeLessThanOrEqual(zoomEquivalent.viewport);
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
    page.getByRole("heading", { name: "You don't have access to this lesson" }),
  ).toBeVisible();
  await expect(page.getByText(lessonFixture.title)).toHaveCount(0);
  expect(lessonRequested).toBe(false);
});

test("explains an unavailable exact lesson without substituting content", async ({
  page,
}) => {
  await mockReadyLesson(page);
  await page.unroute(LESSON_PATTERN);
  await page.route(LESSON_PATTERN, (route) =>
    json(route, 404, { code: "not_found" }),
  );
  await installFeatureGuidance(page);
  const guidanceRequest = page.waitForRequest(
    "**/api/v1/guidance/feature-guidance/**",
  );

  await page.goto(LESSON_PATH);

  await expect(
    page.getByRole("heading", { name: "Lesson not found" }),
  ).toBeVisible();
  await expect(
    page.getByRole("heading", {
      level: 2,
      name: "This lesson version is not available",
    }),
  ).toBeVisible();
  await expect(page.getByText(lessonFixture.title)).toHaveCount(0);
  const url = new URL((await guidanceRequest).url());
  expect(url.pathname).toBe(
    "/api/v1/guidance/feature-guidance/lesson-reading/conditions/exact-version-unavailable/versions/1.0.0",
  );
  expect(url.search).toBe("");
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
    page.getByRole("heading", { name: "We couldn't show this lesson safely" }),
  ).toBeVisible();
  await expect(page.getByText(lessonFixture.title)).toHaveCount(0);
  await expect(
    page.locator("main iframe, main video, main script"),
  ).toHaveCount(0);
});

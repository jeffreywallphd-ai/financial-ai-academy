import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";
import type { Locator } from "@playwright/test";

import type {
  LearningCatalog,
  LearningOpportunity,
} from "../../../src/features/learning-catalog/model";
import type { NavigationState } from "../../../src/features/curriculum-graph/model";

const PLACEMENT_ID = "intro-risk-return-primary";
const GUIDED_PRACTICE_ID = "intro-risk-return-guided-practice";
const CATALOG_PATH = "/learn";
const CATALOG_API = "/api/v1/curriculum/opportunities";
const QUERY_API = "/api/v1/curriculum/opportunities/query";
const LESSON_PATH = `/learn/placements/${PLACEMENT_ID}`;
const LESSON_API =
  `/api/v1/curriculum/placements/${PLACEMENT_ID}/lesson`;
const CURRICULUM_ID = "investing-foundations";
const CURRICULUM_VERSION = "1.0.0";
const GRAPH_PATH =
  `/learn/curricula/${CURRICULUM_ID}/versions/${CURRICULUM_VERSION}`;
const NAVIGATION_API =
  `/api/v1/adaptation/curricula/${CURRICULUM_ID}/versions/${CURRICULUM_VERSION}/navigation-state`;
const LESSON_ACTIVITY_ID = "activity-risk-return-lesson";
const ASSESSMENT_ACTIVITY_ID = "activity-risk-return-check";
const DIGEST =
  "7cf84bc2f7483d9131db315260b3812f3ea29821bf296571c0c7e38f05b536bc";
const DEFINITION_DIGEST =
  "98e941f9b53ef429cb6d359246ddb9812e354db2a9381a2ee180ed5758343d2b";

function displayLabel(value: string): string {
  return value
    .split(/[-_]/)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

async function expectCurrentOpportunityFacts(
  container: Locator,
  opportunity: LearningOpportunity,
) {
  await expect(
    container.getByText(opportunity.summary, { exact: true }),
  ).toBeVisible();
  await expect(
    container.getByText(opportunity.opportunity_id, { exact: true }),
  ).toBeVisible();
  await expect(
    container
      .getByText(displayLabel(opportunity.kind), { exact: true })
      .first(),
  ).toBeVisible();
  await expect(
    container.getByText(displayLabel(opportunity.level), { exact: true }),
  ).toBeVisible();
  await expect(
    container.getByText(`${opportunity.estimated_minutes} minutes`, {
      exact: true,
    }),
  ).toBeVisible();
  await expect(
    container.getByText(opportunity.prerequisite_summary, { exact: true }),
  ).toBeVisible();
  await expect(
    container.getByText(
      `${opportunity.package_id}@${opportunity.package_version}`,
      { exact: true },
    ),
  ).toBeVisible();
  const topicList = container.getByRole("list", {
    name: `${opportunity.title} topics`,
  });
  for (const topic of opportunity.topics) {
    await expect(
      topicList.getByText(displayLabel(topic), { exact: true }),
    ).toBeVisible();
  }
  for (const objective of opportunity.objectives) {
    await expect(container.getByText(objective, { exact: true })).toBeVisible();
  }
  await expect(
    container.getByText(opportunity.provenance.published_by, { exact: false }),
  ).toBeVisible();
  await expect(
    container.locator(
      `time[datetime="${opportunity.provenance.published_at}"]`,
    ),
  ).toBeVisible();
  await expect(
    container.locator(
      `time[datetime="${opportunity.provenance.content_reviewed_on}"]`,
    ),
  ).toBeVisible();
  await expect(
    container.getByText(opportunity.provenance.educational_use_notice, {
      exact: true,
    }),
  ).toBeVisible();
  await expect(
    container.getByText(opportunity.package_digest, { exact: true }),
  ).toBeVisible();
  await expect(
    container.getByText(opportunity.source_fingerprint, { exact: true }),
  ).toBeVisible();
  await expect(
    container.getByText(opportunity.availability_reason, { exact: true }),
  ).toBeVisible();
}

test("browses the live catalog and opens the approved exact lesson", async ({
  context,
  page,
}) => {
  const response = await page.goto(CATALOG_PATH);
  expect(response?.status()).toBe(200);
  expect(response?.headers()["content-security-policy"]).toContain(
    "default-src 'self'",
  );
  expect(response?.headers()["x-content-type-options"]).toBe("nosniff");

  await expect(
    page.getByRole("heading", {
      level: 1,
      name: "Build financial understanding step by step",
    }),
  ).toBeVisible();
  const catalogCard = page.getByRole("article").filter({
    has: page.getByRole("heading", {
      level: 2,
      name: "Understanding Risk and Return",
    }),
    hasText: "The exact reviewed lesson is available in this local catalog.",
  });
  await expect(catalogCard).toBeVisible();
  await expect(page.getByRole("article")).toHaveCount(3);
  await expect(
    catalogCard.getByText(
      "Build a foundational understanding of how potential return and risk relate before comparing investments.",
    ),
  ).toBeVisible();
  await expect(
    catalogCard.getByText(
      "The exact reviewed lesson is available in this local catalog.",
    ),
  ).toBeVisible();
  await expect(
    catalogCard.getByText("intro-risk-return@1.1.0", { exact: true }),
  ).toBeVisible();
  await expect(catalogCard.getByText("Lesson", { exact: true })).toBeVisible();
  await expect(
    catalogCard.getByText("Available", { exact: true }),
  ).toBeVisible();
  const topicList = catalogCard.getByRole("list", {
    name: "Understanding Risk and Return topics",
  });
  await expect(
    topicList.getByText("Investment Basics", { exact: true }),
  ).toBeVisible();
  await expect(
    topicList.getByText("Risk And Return", { exact: true }),
  ).toBeVisible();
  await expect(
    catalogCard.getByText("Introductory", { exact: true }),
  ).toBeVisible();
  await expect(
    catalogCard.getByText("20 minutes", { exact: true }),
  ).toBeVisible();
  await expect(
    catalogCard.getByText("No prior lesson is required.", { exact: true }),
  ).toBeVisible();
  await expect(
    catalogCard.getByText(/Financial AI Academy fixture publisher/),
  ).toBeVisible();
  await expect(
    catalogCard.getByText(/does not provide personalized financial advice/i),
  ).toBeVisible();
  const catalogAccessibility = await new AxeBuilder({ page }).analyze();
  expect(catalogAccessibility.violations).toEqual([]);

  const beforeNavigationResponse = await context.request.get(NAVIGATION_API);
  expect(beforeNavigationResponse.status()).toBe(200);
  const beforeNavigation =
    (await beforeNavigationResponse.json()) as NavigationState;
  const beforeLessonState = beforeNavigation.activity_states.find(
    (state) => state.activity_id === LESSON_ACTIVITY_ID,
  );
  expect(
    new Set(beforeNavigation.activity_states.map((state) => state.activity_id))
      .size,
  ).toBe(beforeNavigation.activity_states.length);
  expect(beforeLessonState).toMatchObject({
    activity_id: LESSON_ACTIVITY_ID,
    availability: "available",
    completion: "incomplete",
    eligibility: "eligible",
    requirement: "required",
  });
  expect(beforeLessonState?.reasons.map((reason) => reason.code)).toEqual([
    "required_activity",
    "entry_activity",
  ]);

  const lessonAction = catalogCard.getByRole("link", {
    name: "Open exact lesson",
  });
  await expect(lessonAction).toHaveAttribute("href", LESSON_PATH);

  const catalogResponse = await context.request.get(CATALOG_API);
  expect(catalogResponse.status()).toBe(200);
  const catalog = await catalogResponse.json();
  expect(catalog.records).toHaveLength(3);
  const approvedOpportunity = catalog.records.find(
    (record: { opportunity_id: string }) =>
      record.opportunity_id === PLACEMENT_ID,
  );
  expect(approvedOpportunity).toMatchObject({
    opportunity_id: PLACEMENT_ID,
    placement_id: PLACEMENT_ID,
    destination: LESSON_PATH,
    kind: "lesson",
    topics: ["investment-basics", "risk-and-return"],
    level: "introductory",
    estimated_minutes: 20,
    prerequisite_summary: "No prior lesson is required.",
    availability: "available",
    availability_reason:
      "The exact reviewed lesson is available in this local catalog.",
    package_id: "intro-risk-return",
    package_version: "1.1.0",
    package_digest: DIGEST,
  });
  expect(approvedOpportunity.source_fingerprint).toMatch(/^[a-f0-9]{64}$/);
  expect(approvedOpportunity.projected_at).toBe(catalog.projected_at);
  await lessonAction.click();
  await expect(page).toHaveURL(new RegExp(`${LESSON_PATH}$`));

  await expect(
    page.getByRole("heading", {
      exact: true,
      level: 1,
      name: "Understanding Risk and Return",
    }),
  ).toBeVisible();
  await expect(
    page.getByText(
      "Explain why potential return and risk must be considered together.",
    ),
  ).toBeVisible();
  await expect(
    page
      .getByRole("region", { name: "Educational sources" })
      .getByRole("link", {
        name: /Introduction to Investing.*opens in a new tab/i,
      }),
  ).toHaveAttribute(
    "href",
    "https://www.investor.gov/introduction-investing",
  );
  await expect(page.getByText("1.1.0", { exact: true })).toBeVisible();
  await expect(page.getByText(DIGEST, { exact: true })).toBeVisible();
  await expect(
    page.getByText(
      /does not provide personalized financial advice or predict investment performance/i,
    ),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: /buy|sell|hold|trade/i }),
  ).toHaveCount(0);

  await page
    .getByRole("radio", {
      name: /Higher potential returns generally come with greater uncertainty/i,
    })
    .check();
  await page.getByRole("button", { name: "Check answer" }).click();
  await expect(
    page.getByRole("heading", { name: "Knowledge check complete" }),
  ).toBeVisible();
  await expect(
    page.getByText(/not mastery or certification/i),
  ).toBeVisible();

  await page.reload();
  await expect(
    page.getByRole("heading", { name: "Retained lesson completion" }),
  ).toBeVisible();
  const completionEvent = page.getByRole("article", {
    name: /Completion event/i,
  });
  await expect(page.getByText("1 of 1", { exact: true })).toBeVisible();
  await expect(
    completionEvent.getByText(DIGEST, { exact: true }),
  ).toBeVisible();
  await expect(
    completionEvent.getByText(DEFINITION_DIGEST, { exact: true }),
  ).toBeVisible();
  await expect(
    completionEvent.getByText("Attempt reference", { exact: true }),
  ).toBeVisible();
  await expect(
    completionEvent.getByText("Evidence reference", { exact: true }),
  ).toBeVisible();
  await expect(
    completionEvent.getByText("Source event", { exact: true }),
  ).toBeVisible();
  await expect(page.getByRole("radio")).toHaveCount(0);
  await expect(
    page.getByText(/not a mastery or certification decision/i),
  ).toBeVisible();
  await expect(
    page.getByText(/does not provide investment advice/i),
  ).toBeVisible();

  const sourceDigest = page
    .getByText("Source-set digest", { exact: true })
    .locator("..")
    .locator("code");
  await expect(sourceDigest).toHaveText(/^[a-f0-9]{64}$/);
  const retainedSourceDigest = await sourceDigest.textContent();

  await page.reload();
  await expect(
    page.getByRole("heading", { name: "Retained lesson completion" }),
  ).toBeVisible();
  await expect(
    page
      .getByText("Source-set digest", { exact: true })
      .locator("..")
      .locator("code"),
  ).toHaveText(retainedSourceDigest ?? "");
  await expect(page.getByRole("radio")).toHaveCount(0);

  const afterNavigationResponse = await context.request.get(NAVIGATION_API);
  expect(afterNavigationResponse.status()).toBe(200);
  const afterNavigation =
    (await afterNavigationResponse.json()) as NavigationState;
  expect(afterNavigation).toMatchObject({
    curriculum_id: beforeNavigation.curriculum_id,
    curriculum_version: beforeNavigation.curriculum_version,
    graph_digest: beforeNavigation.graph_digest,
    policy_id: beforeNavigation.policy_id,
    policy_version: beforeNavigation.policy_version,
    schema_version: beforeNavigation.schema_version,
  });
  expect(afterNavigation.source_set_digest).not.toBe(
    beforeNavigation.source_set_digest,
  );
  expect(afterNavigation.projection_digest).not.toBe(
    beforeNavigation.projection_digest,
  );
  const afterLessonState = afterNavigation.activity_states.find(
    (state) => state.activity_id === LESSON_ACTIVITY_ID,
  );
  expect(afterLessonState).toMatchObject({
    activity_id: LESSON_ACTIVITY_ID,
    availability: "available",
    completion: "completed",
    eligibility: "eligible",
    requirement: "required",
  });
  expect(afterLessonState?.reasons.map((reason) => reason.code)).toEqual([
    "activity_completed",
    "required_activity",
    "entry_activity",
  ]);
  expect(afterLessonState?.reasons[0]?.references).toContain(
    LESSON_ACTIVITY_ID,
  );
  const assessmentState = afterNavigation.activity_states.find(
    (state) => state.activity_id === ASSESSMENT_ACTIVITY_ID,
  );
  expect(assessmentState).toMatchObject({
    activity_id: ASSESSMENT_ACTIVITY_ID,
    availability: "available",
    completion: "unavailable",
    eligibility: "unavailable",
    requirement: "required",
  });
  expect(assessmentState?.reasons.map((reason) => reason.code)).toContain(
    "completion_source_unavailable",
  );

  await page.goto(GRAPH_PATH);
  await expect(
    page.getByRole("heading", { level: 1, name: "Investing Foundations" }),
  ).toBeVisible();
  const lessonStateCard = page.getByRole("article").filter({
    has: page.getByText(LESSON_ACTIVITY_ID, { exact: true }),
  });
  await expect(lessonStateCard).toHaveCount(1);
  await expect(
    lessonStateCard.getByText("Completed", { exact: true }),
  ).toBeVisible();
  await expect(
    lessonStateCard.getByText(
      "Accepted completion evidence exists for this exact activity.",
      { exact: true },
    ),
  ).toBeVisible();
  const listStateFacts = await lessonStateCard.innerText();
  await page.getByRole("button", { name: "Map view" }).click();
  expect(await lessonStateCard.innerText()).toBe(listStateFacts);
  await expect(
    page.getByRole("link", { name: /open|start|launch/i }),
  ).toHaveCount(0);

  const cookies = await context.cookies();
  const session = cookies.find(
    (cookie) => cookie.name === "financial_ai_academy_session",
  );
  expect(session).toBeDefined();
  expect(session?.httpOnly).toBe(true);
  expect(session?.sameSite).toBe("Strict");

  const accessibility = await new AxeBuilder({ page }).analyze();
  expect(accessibility.violations).toEqual([]);
});

test("inspects and compares live current opportunities before exact continuation", async ({
  context,
  page,
}) => {
  await page.goto(CATALOG_PATH);
  await expect(page.getByRole("article")).toHaveCount(3);
  const catalogResponse = await context.request.get(CATALOG_API);
  expect(catalogResponse.status()).toBe(200);
  const currentCatalog = (await catalogResponse.json()) as LearningCatalog;
  const currentAvailable = currentCatalog.records.find(
    (record) => record.opportunity_id === PLACEMENT_ID,
  );
  const currentPlanned = currentCatalog.records.find(
    (record) => record.opportunity_id === GUIDED_PRACTICE_ID,
  );
  expect(currentAvailable).toBeDefined();
  expect(currentPlanned).toBeDefined();
  if (!currentAvailable || !currentPlanned) {
    throw new Error("Expected current available and planned opportunities.");
  }
  const availableCard = page.getByRole("article").filter({
    hasText: "The exact reviewed lesson is available in this local catalog.",
  });
  await availableCard.getByRole("link", { name: "View details" }).click();

  await expect(page).toHaveURL(
    new RegExp(
      `/learn/opportunities/${PLACEMENT_ID}\\?return_to=%2Flearn$`,
    ),
  );
  await expect(
    page.getByRole("heading", {
      exact: true,
      level: 1,
      name: currentAvailable.title,
    }),
  ).toBeVisible();
  await expectCurrentOpportunityFacts(page.locator("main"), currentAvailable);
  await expect(
    page
      .getByText("Projection generation", { exact: true })
      .locator("..")
      .locator("code"),
  ).toHaveText(currentCatalog.projection_generation);
  await expect(
    page
      .getByText("Discovery schema", { exact: true })
      .locator("..")
      .locator("code"),
  ).toHaveText(currentCatalog.schema_version);
  await expect(
    page.locator(`time[datetime="${currentCatalog.projected_at}"]`),
  ).toBeVisible();
  await expect(
    page.getByRole("link", { name: "Open exact lesson" }),
  ).toHaveAttribute("href", LESSON_PATH);
  await expect(
    page.getByRole("link", { name: "Return to catalog" }),
  ).toHaveAttribute("href", CATALOG_PATH);
  const detailAccessibility = await new AxeBuilder({ page }).analyze();
  expect(detailAccessibility.violations).toEqual([]);

  await page.getByRole("link", { name: "Return to catalog" }).click();
  const plannedCard = page.getByRole("article").filter({
    hasText: "This synthetic guided practice remains planned in qualification.",
  });
  await plannedCard
    .getByRole("checkbox", { name: "Compare Understanding Risk and Return" })
    .check();
  await page
    .getByRole("article")
    .filter({
      hasText: "The exact reviewed lesson is available in this local catalog.",
    })
    .getByRole("checkbox", { name: "Compare Understanding Risk and Return" })
    .check();
  await page.getByRole("button", { name: "Compare selected" }).click();

  const comparisonUrl = new URL(page.url());
  expect(comparisonUrl.pathname).toBe("/learn/opportunities/compare");
  expect(comparisonUrl.searchParams.get("return_to")).toBe(CATALOG_PATH);
  expect(comparisonUrl.searchParams.getAll("opportunity")).toEqual([
    GUIDED_PRACTICE_ID,
    PLACEMENT_ID,
  ]);
  await expect(
    page.getByRole("heading", { level: 1, name: "Compare educational facts" }),
  ).toBeVisible();
  const comparisonCards = page.getByRole("article");
  await expect(comparisonCards).toHaveCount(2);
  await expect(
    comparisonCards.nth(0).getByText(GUIDED_PRACTICE_ID, { exact: true }),
  ).toBeVisible();
  await expect(
    comparisonCards.nth(1).getByText(PLACEMENT_ID, { exact: true }),
  ).toBeVisible();
  await expect(
    comparisonCards.nth(0).getByText("Selected 1", { exact: true }),
  ).toBeVisible();
  await expect(
    comparisonCards.nth(1).getByText("Selected 2", { exact: true }),
  ).toBeVisible();
  await expect(
    comparisonCards.nth(0).getByText("35 minutes", { exact: true }),
  ).toBeVisible();
  await expect(
    comparisonCards.nth(1).getByText("20 minutes", { exact: true }),
  ).toBeVisible();
  await expectCurrentOpportunityFacts(
    comparisonCards.nth(0),
    currentPlanned,
  );
  await expectCurrentOpportunityFacts(
    comparisonCards.nth(1),
    currentAvailable,
  );
  await expect(
    comparisonCards.nth(0).getByRole("link", { name: "Open exact lesson" }),
  ).toHaveCount(0);
  await expect(
    comparisonCards.nth(1).getByRole("link", { name: "Open exact lesson" }),
  ).toHaveAttribute("href", LESSON_PATH);
  await expect(
    comparisonCards.nth(0).getByRole("link", { name: "View details" }),
  ).toHaveAttribute(
    "href",
    `/learn/opportunities/${GUIDED_PRACTICE_ID}?return_to=%2Flearn`,
  );
  await expect(
    comparisonCards.nth(1).getByRole("link", { name: "View details" }),
  ).toHaveAttribute(
    "href",
    `/learn/opportunities/${PLACEMENT_ID}?return_to=%2Flearn`,
  );
  const comparisonContext = page.locator(".opportunity-comparison__context");
  await expect(comparisonContext.locator("code").nth(0)).toHaveText(
    currentCatalog.projection_generation,
  );
  await expect(comparisonContext.locator("code").nth(1)).toHaveText(
    currentCatalog.schema_version,
  );
  await expect(
    comparisonContext.locator(
      `time[datetime="${currentCatalog.projected_at}"]`,
    ),
  ).toBeVisible();
  await expect(page.getByText(/does not rank opportunities/i)).toBeVisible();
  await expect(page.getByText(/recommended for you|comparison score/i)).toHaveCount(
    0,
  );
  const comparisonAccessibility = await new AxeBuilder({ page }).analyze();
  expect(comparisonAccessibility.violations).toEqual([]);

  await comparisonCards
    .nth(1)
    .getByRole("link", { name: "Open exact lesson" })
    .click();
  await expect(page).toHaveURL(new RegExp(`${LESSON_PATH}$`));
  await expect(
    page.getByRole("heading", {
      exact: true,
      level: 1,
      name: "Understanding Risk and Return",
    }),
  ).toBeVisible();
});

test("fails closed for changed and malformed live opportunity selections", async ({
  page,
}) => {
  await page.goto("/learn/opportunities/not-a-current-opportunity");
  await expect(
    page.getByRole("heading", { name: "Opportunity changed" }),
  ).toBeVisible();
  await expect(page.getByText("Understanding Risk and Return")).toHaveCount(0);

  await page.goto(
    `/learn/opportunities/compare?opportunity=${PLACEMENT_ID}` +
      "&opportunity=not-a-current-opportunity",
  );
  await expect(
    page.getByRole("heading", { name: "Comparison changed" }),
  ).toBeVisible();
  await expect(page.getByText("Understanding Risk and Return")).toHaveCount(0);

  await page.goto(
    `/learn/opportunities/compare?opportunity=${PLACEMENT_ID}`,
  );
  await expect(
    page.getByRole("heading", { name: "Comparison link unavailable" }),
  ).toBeVisible();
  await expect(page.getByText("Understanding Risk and Return")).toHaveCount(0);
});

test("filters, pages, and rejects a mismatched live query cursor", async ({
  context,
  page,
}) => {
  await page.goto(`${CATALOG_PATH}?sort=duration_ascending&page_size=1`);
  await expect(page.getByRole("article")).toHaveCount(1);
  await expect(page.getByRole("article").getByText("10 minutes")).toBeVisible();
  await expect(page.getByText(/3 matches.*Showing 1 on this page/)).toBeVisible();

  const firstNext = page.getByRole("link", { name: "Next page" });
  await expect(firstNext).toBeVisible();
  await firstNext.click();
  await expect(page.getByRole("article").getByText("20 minutes")).toBeVisible();

  const secondNext = page.getByRole("link", { name: "Next page" });
  await expect(secondNext).toBeVisible();
  await secondNext.click();
  await expect(page.getByRole("article").getByText("35 minutes")).toBeVisible();
  await expect(page.getByRole("link", { name: "Next page" })).toHaveCount(0);

  await page.goto(
    `${CATALOG_PATH}?topic=guided-practice&level=intermediate` +
      "&availability=planned&minimum_minutes=30&maximum_minutes=40" +
      "&sort=duration_descending&page_size=17",
  );
  const filteredCard = page.getByRole("article");
  await expect(filteredCard).toHaveCount(1);
  await expect(filteredCard.getByText("35 minutes")).toBeVisible();
  await expect(filteredCard.getByText("Planned", { exact: true })).toBeVisible();
  await expect(
    page.getByRole("spinbutton", { name: "Results per page" }),
  ).toHaveValue("17");

  const observedIds: string[] = [];
  let cursor: string | null = null;
  let firstCursor = "";
  do {
    const parameters = new URLSearchParams({
      sort: "duration_ascending",
      page_size: "1",
    });
    if (cursor) parameters.set("cursor", cursor);
    const response = await context.request.get(`${QUERY_API}?${parameters}`);
    expect(response.status()).toBe(200);
    const result = await response.json();
    expect(result.total_matches).toBe(3);
    expect(result.applied_query).toMatchObject({
      sort: "duration_ascending",
      page_size: 1,
    });
    expect(result.records).toHaveLength(1);
    observedIds.push(result.records[0].opportunity_id);
    cursor = result.next_cursor;
    if (!firstCursor && cursor) firstCursor = cursor;
  } while (cursor);
  expect(observedIds).toEqual([
    "intro-risk-return-quick-review",
    PLACEMENT_ID,
    "intro-risk-return-guided-practice",
  ]);
  expect(firstCursor).not.toBe("");

  const mismatched = new URLSearchParams({
    sort: "title",
    page_size: "1",
    cursor: firstCursor,
  });
  const mismatchResponse = await context.request.get(
    `${QUERY_API}?${mismatched}`,
  );
  expect(mismatchResponse.status()).toBe(400);
  await expect(mismatchResponse.json()).resolves.toMatchObject({
    code: "invalid_query",
  });

  await page.goto(`${CATALOG_PATH}?${mismatched}`);
  await expect(
    page.getByRole("heading", { name: "Query could not be applied" }),
  ).toBeVisible();
  await expect(page.getByRole("article")).toHaveCount(0);
});

test("fails closed without context and never substitutes a missing version", async ({
  page,
  request,
}) => {
  const unauthorizedCatalog = await request.get(CATALOG_API);
  expect(unauthorizedCatalog.status()).toBe(401);
  const catalogDenial = await unauthorizedCatalog.text();
  expect(catalogDenial).not.toContain("Understanding Risk and Return");
  expect(catalogDenial).not.toContain(DIGEST);
  expect(catalogDenial).not.toMatch(/actor_id|learner_id|session_id/i);

  const unauthorizedQuery = await request.get(`${QUERY_API}?page_size=1`);
  expect(unauthorizedQuery.status()).toBe(401);
  const queryDenial = await unauthorizedQuery.text();
  expect(queryDenial).not.toContain("Understanding Risk and Return");
  expect(queryDenial).not.toMatch(
    /total_matches|next_cursor|actor_id|learner_id|session_id|provider/i,
  );

  const unauthorized = await request.get(LESSON_API);
  expect(unauthorized.status()).toBe(401);
  const denial = await unauthorized.text();
  expect(denial).not.toContain("Understanding Risk and Return");
  expect(denial).not.toContain(DIGEST);
  expect(denial).not.toMatch(/actor_id|learner_id|session_id/i);

  await page.goto("/learn/placements/not-a-real-placement");
  await expect(
    page.getByRole("heading", { name: "Lesson not found" }),
  ).toBeVisible();
  await expect(
    page.getByText(/A different or newer lesson was not substituted/i),
  ).toBeVisible();
  await expect(page.getByText("Understanding Risk and Return")).toHaveCount(0);
  await expect(page.getByText(DIGEST)).toHaveCount(0);
});

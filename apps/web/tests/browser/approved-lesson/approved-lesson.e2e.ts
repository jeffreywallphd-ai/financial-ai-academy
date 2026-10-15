import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";


const PLACEMENT_ID = "intro-risk-return-primary";
const CATALOG_PATH = "/learn";
const CATALOG_API = "/api/v1/curriculum/opportunities";
const QUERY_API = "/api/v1/curriculum/opportunities/query";
const LESSON_PATH = `/learn/placements/${PLACEMENT_ID}`;
const LESSON_API =
  `/api/v1/curriculum/placements/${PLACEMENT_ID}/lesson`;
const DIGEST =
  "7cf84bc2f7483d9131db315260b3812f3ea29821bf296571c0c7e38f05b536bc";
const DEFINITION_DIGEST =
  "98e941f9b53ef429cb6d359246ddb9812e354db2a9381a2ee180ed5758343d2b";

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

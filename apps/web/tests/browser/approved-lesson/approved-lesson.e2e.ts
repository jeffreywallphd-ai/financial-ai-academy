import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";


const PLACEMENT_ID = "intro-risk-return-primary";
const LESSON_PATH = `/learn/placements/${PLACEMENT_ID}`;
const LESSON_API =
  `/api/v1/curriculum/placements/${PLACEMENT_ID}/lesson`;
const DIGEST =
  "7cf84bc2f7483d9131db315260b3812f3ea29821bf296571c0c7e38f05b536bc";
const DEFINITION_DIGEST =
  "98e941f9b53ef429cb6d359246ddb9812e354db2a9381a2ee180ed5758343d2b";

test("opens the approved exact lesson through the live same-origin path", async ({
  context,
  page,
}) => {
  const response = await page.goto(LESSON_PATH);
  expect(response?.status()).toBe(200);
  expect(response?.headers()["content-security-policy"]).toContain(
    "default-src 'self'",
  );
  expect(response?.headers()["x-content-type-options"]).toBe("nosniff");

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

test("fails closed without context and never substitutes a missing version", async ({
  page,
  request,
}) => {
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

import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";


const PLACEMENT_ID = "intro-risk-return-primary";
const LESSON_PATH = `/learn/placements/${PLACEMENT_ID}`;
const LESSON_API =
  `/api/v1/curriculum/placements/${PLACEMENT_ID}/lesson`;
const DIGEST =
  "576d543b404a7f70f2e5bebee55c32a3f945d8e8da73654c43ef92e656aee008";

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
  await expect(page.getByText("1.0.0", { exact: true })).toBeVisible();
  await expect(page.getByText(DIGEST, { exact: true })).toBeVisible();
  await expect(
    page.getByText(
      /does not provide personalized financial advice or predict investment performance/i,
    ),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: /buy|sell|hold|trade/i }),
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

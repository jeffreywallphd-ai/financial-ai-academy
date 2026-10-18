import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page, type Response } from "@playwright/test";
import { writeFile } from "node:fs/promises";

import {
  contextualHelpIsSafe,
  platformHelpSearchPageIsSafe,
  platformHelpTopicIsSafe,
  type ContextualHelp,
  type PlatformHelpSearchPage,
  type PlatformHelpTopic,
} from "../../../src/features/platform-help/model";


const HELP_API = "/api/v1/guidance/platform-help";
const CONTEXT_API = "/api/v1/guidance/contextual-help";
const CONTEXT_VERSION = "1.0.0";
const CONTEXT_KEYS = [
  "ai-assistance",
  "lesson-publication",
  "practice-result",
  "project-result",
] as const;

function isLoopback(url: URL): boolean {
  return url.hostname === "127.0.0.1" || url.hostname === "localhost" || url.hostname === "[::1]";
}

function isSearchResponse(response: Response): boolean {
  return new URL(response.url()).pathname === HELP_API && response.request().method() === "GET";
}

function isTopicResponse(response: Response): boolean {
  const url = new URL(response.url());
  return url.pathname.startsWith(`${HELP_API}/`) && response.request().method() === "GET";
}

function isContextResponse(response: Response, contextKey: string): boolean {
  const url = new URL(response.url());
  return url.pathname ===
    `${CONTEXT_API}/${contextKey}/versions/${CONTEXT_VERSION}` &&
    response.request().method() === "GET";
}

async function openContextualFeature(
  page: Page,
  url: string,
  contextKey: string,
): Promise<ContextualHelp> {
  const responsePromise = page.waitForResponse((response) =>
    isContextResponse(response, contextKey),
  );
  await page.goto(url);
  const response = await responsePromise;
  expect(response.status()).toBe(200);
  const document = (await response.json()) as ContextualHelp;
  expect(contextualHelpIsSafe(document, contextKey, CONTEXT_VERSION)).toBe(true);
  return document;
}

async function openSearch(page: Page, url: string): Promise<PlatformHelpSearchPage> {
  const responsePromise = page.waitForResponse(isSearchResponse);
  await page.goto(url);
  const response = await responsePromise;
  expect(response.status()).toBe(200);
  return (await response.json()) as PlatformHelpSearchPage;
}

async function followSearch(page: Page, action: () => Promise<void>): Promise<PlatformHelpSearchPage> {
  const responsePromise = page.waitForResponse(isSearchResponse);
  await action();
  const response = await responsePromise;
  expect(response.status()).toBe(200);
  return (await response.json()) as PlatformHelpSearchPage;
}

async function followTopic(page: Page, action: () => Promise<void>): Promise<PlatformHelpTopic> {
  const responsePromise = page.waitForResponse(isTopicResponse);
  await action();
  const response = await responsePromise;
  expect(response.status()).toBe(200);
  return (await response.json()) as PlatformHelpTopic;
}

test("keeps reviewed platform help available through one local public API", async ({
  context,
  page,
}) => {
  test.setTimeout(90_000);
  const externalRequests: string[] = [];
  const guidanceRequests: Array<{ method: string; path: string }> = [];
  page.on("request", (request) => {
    const url = new URL(request.url());
    if (!isLoopback(url)) externalRequests.push(url.origin);
    if (url.pathname.startsWith(HELP_API) || url.pathname.startsWith(CONTEXT_API)) {
      guidanceRequests.push({ method: request.method(), path: url.pathname });
    }
  });

  const firstPage = await openSearch(page, "/help?page_size=1");
  expect(platformHelpSearchPageIsSafe(firstPage, { page_size: 1 })).toBe(true);
  expect(firstPage.results).toHaveLength(1);
  expect(firstPage.next_cursor).not.toBeNull();
  await expect(
    page.getByRole("heading", { level: 1, name: "Understand how the Academy works" }),
  ).toBeVisible();

  const continuedPage = await followSearch(page, async () => {
    await page.getByRole("link", { name: "Show more topics" }).click();
  });
  expect(
    platformHelpSearchPageIsSafe(continuedPage, {
      page_size: 1,
      cursor: firstPage.next_cursor,
    }),
  ).toBe(true);
  expect(continuedPage.corpus_digest).toBe(firstPage.corpus_digest);
  expect(continuedPage.results[0]?.topic_id).not.toBe(firstPage.results[0]?.topic_id);

  await page.getByLabel("Search the guide").fill("methods");
  await page.getByLabel("Type of help").selectOption("");
  await page.getByLabel("Results per page").fill("20");
  const searchedPage = await followSearch(page, async () => {
    await page.getByRole("button", { name: "Show topics" }).click();
  });
  expect(platformHelpSearchPageIsSafe(searchedPage, { query: "methods", page_size: 20 })).toBe(true);
  expect(searchedPage.results.map((result) => result.topic_id)).toContain("platform-methods");

  const methodTopic = await followTopic(page, async () => {
    await page.getByRole("link", { name: "Read this topic" }).click();
  });
  expect(platformHelpTopicIsSafe(methodTopic, "platform-methods", "1.0.0")).toBe(true);
  await expect(
    page.getByRole("heading", { level: 1, name: "How platform methods stay reproducible" }),
  ).toBeVisible();
  await page.getByText("Technical record", { exact: true }).click();
  await expect(page.getByText("platform-methods@1.0.0", { exact: true })).toBeVisible();
  const returnedPage = await followSearch(page, async () => {
    await page.getByRole("link", { name: "Return to platform guide" }).click();
  });
  expect(returnedPage).toEqual(searchedPage);

  const approvedSearch = await openSearch(page, "/help?query=approved%20help&page_size=20");
  expect(platformHelpSearchPageIsSafe(approvedSearch, { query: "approved help", page_size: 20 })).toBe(true);
  expect(approvedSearch.results.map((result) => result.topic_id)).toEqual(["approved-help"]);
  const approvedTopic = await followTopic(page, async () => {
    await page.getByRole("link", { name: "Read this topic" }).click();
  });
  expect(platformHelpTopicIsSafe(approvedTopic, "approved-help", "1.0.0")).toBe(true);
  const relatedTopic = await followTopic(page, async () => {
    await page.getByRole("link", { name: "education not advice" }).click();
  });
  expect(platformHelpTopicIsSafe(relatedTopic, "education-not-advice", "1.0.0")).toBe(true);

  const limitationPage = await openSearch(page, "/help?topic_kind=limitation&page_size=1");
  expect(
    platformHelpSearchPageIsSafe(limitationPage, {
      topic_kind: "limitation",
      page_size: 1,
    }),
  ).toBe(true);
  expect(limitationPage.results).toHaveLength(1);
  expect(limitationPage.next_cursor).not.toBeNull();
  const limitationContinuation = await followSearch(page, async () => {
    await page.getByRole("link", { name: "Show more topics" }).click();
  });
  expect(limitationContinuation.results).toHaveLength(1);
  expect(limitationContinuation.results[0]?.topic_id).not.toBe(
    limitationPage.results[0]?.topic_id,
  );

  const lessonContext = await openContextualFeature(
    page,
    "/learn/placements/intro-risk-return-primary",
    "lesson-publication",
  );
  await expect(
    page.getByRole("heading", {
      level: 3,
      name: `Questions about ${lessonContext.feature_label}`,
    }),
  ).toBeVisible();
  const lessonReference = lessonContext.help_references[0]!;
  const lessonTopic = await followTopic(page, async () => {
    await page.getByRole("link", { name: lessonReference.label }).click();
  });
  expect(
    platformHelpTopicIsSafe(
      lessonTopic,
      lessonReference.topic_id,
      lessonReference.topic_version,
    ),
  ).toBe(true);
  const returnedLessonContext = page.waitForResponse((response) =>
    isContextResponse(response, "lesson-publication"),
  );
  await page.getByRole("link", { name: "Return to lesson" }).click();
  expect((await returnedLessonContext).status()).toBe(200);
  await expect(
    page.getByRole("heading", {
      exact: true,
      level: 1,
      name: "Understanding Risk and Return",
    }),
  ).toBeVisible();

  const assistanceContext = await openContextualFeature(
    page,
    "/preferences/assistance",
    "ai-assistance",
  );
  await expect(
    page.getByRole("heading", {
      level: 3,
      name: `Questions about ${assistanceContext.feature_label}`,
    }),
  ).toBeVisible();

  const contexts: Record<string, ContextualHelp> = {
    "ai-assistance": assistanceContext,
    "lesson-publication": lessonContext,
  };
  for (const contextKey of CONTEXT_KEYS) {
    if (contexts[contextKey]) continue;
    const response = await context.request.get(
      `${CONTEXT_API}/${contextKey}/versions/${CONTEXT_VERSION}`,
    );
    expect(response.status()).toBe(200);
    const document = (await response.json()) as ContextualHelp;
    expect(contextualHelpIsSafe(document, contextKey, CONTEXT_VERSION)).toBe(true);
    contexts[contextKey] = document;
  }

  const contextTopics: Record<string, PlatformHelpTopic> = {};
  for (const document of Object.values(contexts)) {
    for (const reference of document.help_references) {
      const identity = `${reference.topic_id}@${reference.topic_version}`;
      if (contextTopics[identity]) continue;
      const response = await context.request.get(
        `${HELP_API}/${reference.topic_id}/versions/${reference.topic_version}`,
      );
      expect(response.status()).toBe(200);
      const topic = (await response.json()) as PlatformHelpTopic;
      expect(
        platformHelpTopicIsSafe(
          topic,
          reference.topic_id,
          reference.topic_version,
        ),
      ).toBe(true);
      contextTopics[identity] = topic;
    }
  }

  await openSearch(page, "/help?topic_kind=limitation&page_size=1");

  for (const theme of ["light", "dark", "system"] as const) {
    await page.getByLabel("Theme").selectOption(theme);
    await expect(page.locator("html")).toHaveAttribute("data-theme", theme);
  }
  await page.setViewportSize({ width: 320, height: 900 });
  await page.emulateMedia({ colorScheme: "dark", forcedColors: "active", reducedMotion: "reduce" });
  await page.getByLabel("Search the guide").focus();
  await page.keyboard.press("Tab");
  expect(
    await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth),
  ).toBe(true);

  await page.setViewportSize({ width: 1280, height: 900 });
  await page.evaluate(() => { document.documentElement.style.fontSize = "200%"; });
  await page.getByLabel("Search the guide").focus();
  await page.keyboard.press("Tab");
  await expect(page.getByLabel("Type of help")).toBeFocused();
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);

  expect(externalRequests).toEqual([]);
  expect(guidanceRequests.length).toBeGreaterThan(0);
  expect(guidanceRequests.every(({ method }) => method === "GET")).toBe(true);
  expect(
    guidanceRequests.every(({ path }) =>
      path === HELP_API ||
      /^\/api\/v1\/guidance\/platform-help\/[a-z0-9._-]+\/versions\/\d+\.\d+\.\d+$/.test(path) ||
      /^\/api\/v1\/guidance\/contextual-help\/[a-z0-9._-]+\/versions\/\d+\.\d+\.\d+$/.test(path),
    ),
  ).toBe(true);

  const capturePath = process.env.FINANCIAL_AI_ACADEMY_PLATFORM_HELP_CAPTURE;
  if (capturePath) {
    await writeFile(
      capturePath,
      `${JSON.stringify({
        schema_version: "1.0.0",
        first_page: firstPage,
        continued_page: continuedPage,
        searched_page: searchedPage,
        approved_search: approvedSearch,
        method_topic: methodTopic,
        approved_topic: approvedTopic,
        related_topic: relatedTopic,
        limitation_page: limitationPage,
        limitation_continuation: limitationContinuation,
        contexts,
        context_topics: contextTopics,
        expected: {
          external_request_count: externalRequests.length,
          guidance_methods: [...new Set(guidanceRequests.map(({ method }) => method))],
        },
      }, null, 2)}\n`,
      { encoding: "utf-8", flag: "wx" },
    );
  }
});

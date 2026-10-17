import AxeBuilder from "@axe-core/playwright";
import { expect, test, type APIResponse, type Locator, type Page } from "@playwright/test";
import { readFile, writeFile } from "node:fs/promises";

import type {
  LearnerPreferenceExport,
  LearnerPreferenceHistory,
  LearnerPreferenceProfile,
  PreparedPreferenceRequest,
} from "../../../src/features/learner-preferences/model";
import {
  learnerPreferenceHistoryIsSafe,
  learnerPreferenceProfileIsSafe,
} from "../../../src/features/learner-preferences/model";


const PREFERENCES_API = "/api/v1/learner-preferences";
const MUTATION_API = `${PREFERENCES_API}/mutations`;
const GOAL = "Compare risk and return Σ";
const GOAL_DETAIL = "Build a clear comparison without treating uncertainty as a promise.";
const UPDATED_GOAL = "Compare risk, return, and costs Café";
const EXPERIENCE = "Reading fund information";
const INTEREST = "Long-term investing İ";

type AcceptedMutation = {
  request: PreparedPreferenceRequest;
  response: LearnerPreferenceProfile;
};

async function submitMutation(page: Page, control: Locator): Promise<AcceptedMutation> {
  const responsePromise = page.waitForResponse(
    (response) =>
      new URL(response.url()).pathname === MUTATION_API &&
      response.request().method() === "POST",
  );
  const profileReload = page.waitForResponse(
    (response) =>
      new URL(response.url()).pathname === PREFERENCES_API &&
      response.request().method() === "GET",
  );
  const historyReload = page.waitForResponse(
    (response) =>
      new URL(response.url()).pathname === `${PREFERENCES_API}/history` &&
      response.request().method() === "GET",
  );
  await control.click();
  const response = await responsePromise;
  expect(response.status()).toBe(200);
  const [profileResponse, historyResponse] = await Promise.all([
    profileReload,
    historyReload,
  ]);
  expect(profileResponse.status()).toBe(200);
  expect(historyResponse.status()).toBe(200);
  const reloadedProfile = (await profileResponse.json()) as LearnerPreferenceProfile;
  const reloadedHistory = (await historyResponse.json()) as LearnerPreferenceHistory;
  expect(
    await learnerPreferenceProfileIsSafe(reloadedProfile),
    JSON.stringify(reloadedProfile),
  ).toBe(true);
  expect(
    learnerPreferenceHistoryIsSafe(reloadedHistory, reloadedProfile),
    JSON.stringify(reloadedHistory),
  ).toBe(true);
  const accepted = (await response.json()) as LearnerPreferenceProfile;
  await expect(page.locator('input[name="expected_revision"]').first()).toHaveValue(
    String(accepted.revision),
  );
  return {
    request: response.request().postDataJSON() as PreparedPreferenceRequest,
    response: accepted,
  };
}

async function responseJson<T>(response: APIResponse): Promise<T> {
  expect(response.status()).toBe(200);
  return (await response.json()) as T;
}

test("preserves learner-controlled preferences through the live public API", async ({
  context,
  page,
}) => {
  test.setTimeout(90_000);
  await page.goto("/preferences/learning");
  await expect(page.getByRole("heading", { level: 1, name: "Learning preferences" })).toBeVisible();
  await expect(page.getByText("You have not added a learning goal yet.")).toBeVisible();
  await expect(page.getByText("You have not described any experience yet.")).toBeVisible();
  await expect(page.getByText("You have not added an interest yet.")).toBeVisible();

  const initialProfile = await responseJson<LearnerPreferenceProfile>(
    await context.request.get(PREFERENCES_API),
  );
  expect(initialProfile).toMatchObject({
    revision: 1,
    goals: [],
    experience: [],
    interests: [],
  });

  // Keep a public-request count so destructive confirmation can be proven locally.
  const observedGoalRequests: PreparedPreferenceRequest[] = [];
  page.on("request", (request) => {
    if (new URL(request.url()).pathname === MUTATION_API && request.method() === "POST") {
      observedGoalRequests.push(request.postDataJSON() as PreparedPreferenceRequest);
    }
  });
  const goals = page.getByRole("region", { name: "Learning goals" });
  await goals.getByLabel("Goal").first().fill(GOAL);
  await goals.getByLabel(/Why this matters/).first().fill(GOAL_DETAIL);
  await submitMutation(page, goals.getByRole("button", { name: "Add goal" }));

  // Duplicate learner wording stays usable because controls include position.
  await goals.getByLabel("Goal").first().fill(GOAL);
  await goals.getByLabel(/Why this matters/).first().fill("A second personal reason.");
  await submitMutation(page, goals.getByRole("button", { name: "Add goal" }));
  await expect(page.getByRole("heading", { level: 3, name: GOAL })).toHaveCount(2);
  await submitMutation(
    page,
    page.getByRole("button", { name: `Move ${GOAL}, item 2 up` }),
  );
  const reorderedProfile = await responseJson<LearnerPreferenceProfile>(
    await context.request.get(PREFERENCES_API),
  );
  const reorderedHistory = await responseJson<LearnerPreferenceHistory>(
    await context.request.get(`${PREFERENCES_API}/history`),
  );
  expect(
    await learnerPreferenceProfileIsSafe(reorderedProfile),
    JSON.stringify(reorderedProfile),
  ).toBe(true);
  expect(
    learnerPreferenceHistoryIsSafe(reorderedHistory, reorderedProfile),
    JSON.stringify(reorderedHistory),
  ).toBe(true);

  const firstGoal = goals.locator(".preferences-list > li").first();
  await submitMutation(
    page,
    firstGoal.getByRole("button", { name: `Archive goal: ${GOAL}, item 1` }),
  );
  await expect(firstGoal.getByText("Archived", { exact: true })).toBeVisible();
  await submitMutation(
    page,
    firstGoal.getByRole("button", { name: `Restore goal: ${GOAL}, item 1` }),
  );

  const editFirstGoal = firstGoal.getByLabel(`Edit goal: ${GOAL}, item 1`);
  await editFirstGoal.focus();
  await expect(editFirstGoal).toBeFocused();
  await page.keyboard.press("Enter");
  await firstGoal.locator('input[name="title"]').fill(UPDATED_GOAL);
  await submitMutation(page, firstGoal.getByRole("button", { name: "Save goal" }));
  await expect(page.getByRole("heading", { level: 3, name: UPDATED_GOAL })).toBeVisible();

  const secondGoal = goals.locator(".preferences-list > li").nth(1);
  const removeGoal = secondGoal.getByRole("button", {
    name: `Remove goal: ${GOAL}, item 2`,
  });
  await expect(removeGoal).toBeDisabled();
  const postsBeforeConfirmation = observedGoalRequests.length;
  await removeGoal.click({ force: true });
  expect(observedGoalRequests).toHaveLength(postsBeforeConfirmation);
  await secondGoal.getByRole("checkbox", { name: /item 2.*permanently removes/ }).check();
  await submitMutation(page, removeGoal);
  await expect(page.getByRole("heading", { level: 3, name: GOAL })).toHaveCount(0);

  const experience = page.getByRole("region", { name: "Your experience" });
  await experience.getByLabel("Topic or skill").first().fill(EXPERIENCE);
  await experience.getByLabel("Your experience").first().selectOption("some_experience");
  await experience.getByLabel(/What you have done/).first().fill("Compared two public fund summaries.");
  await submitMutation(page, experience.getByRole("button", { name: "Add experience" }));
  const experienceCard = experience.locator(".preferences-list > li").first();
  await experienceCard.getByLabel(/Edit experience:/).click();
  await experienceCard.locator('select[name="level"]').selectOption("experienced");
  await submitMutation(page, experienceCard.getByRole("button", { name: "Save experience" }));

  const interests = page.getByRole("region", { name: "Interests" });
  await interests.getByLabel("Add an interest").fill(INTEREST);
  await submitMutation(page, interests.getByRole("button", { name: "Add interest" }));
  await interests.getByLabel("Add an interest").fill("Financial statements");
  await submitMutation(page, interests.getByRole("button", { name: "Add interest" }));
  await submitMutation(
    page,
    page.getByRole("button", { name: "Move Financial statements, item 2 up" }),
  );
  const interestCard = interests.locator(".preferences-list > li").first();
  await interestCard.getByLabel(/Edit interest:/).click();
  await interestCard.locator('input[name="label"]').fill("Reading financial statements");
  await submitMutation(page, interestCard.getByRole("button", { name: "Save interest" }));
  const removeInterest = interestCard.getByRole("button", {
    name: "Remove interest: Reading financial statements, item 1",
  });
  await interestCard.getByRole("checkbox", { name: /item 1.*permanently removes/ }).check();
  await submitMutation(page, removeInterest);

  // A concurrent public change makes the browser form stale and moves focus to its safe notice.
  const beforeStale = await responseJson<LearnerPreferenceProfile>(
    await context.request.get(PREFERENCES_API),
  );
  expect(
    (
      await context.request.post(MUTATION_API, {
        headers: { Origin: new URL(page.url()).origin },
        data: {
          schema_version: "1.0.0",
          idempotency_key: crypto.randomUUID(),
          expected_revision: beforeStale.revision,
          mutation: { operation: "create_interest", label: "Interruption marker" },
        },
      })
    ).status(),
  ).toBe(200);
  await goals.getByLabel("Goal").first().fill("A stale browser change");
  const staleResponse = page.waitForResponse(
    (response) => new URL(response.url()).pathname === MUTATION_API && response.status() === 409,
  );
  await goals.getByRole("button", { name: "Add goal" }).click();
  await staleResponse;
  await expect(page.getByRole("heading", { name: "Preferences changed" })).toBeFocused();
  await page.reload();

  // Export the populated record before exercising the bounded reset.
  const firstExportResponse = page.waitForResponse(
    (response) => new URL(response.url()).pathname === `${PREFERENCES_API}/export`,
  );
  const firstDownload = page.waitForEvent("download");
  await page.getByRole("button", { name: "Download preferences" }).click();
  const [populatedExportResponse, populatedDownload] = await Promise.all([
    firstExportResponse,
    firstDownload,
  ]);
  expect(populatedExportResponse.status()).toBe(200);
  expect(populatedDownload.suggestedFilename()).toBe("learning-preferences-export.json");
  const populatedDownloadPath = await populatedDownload.path();
  if (!populatedDownloadPath) throw new Error("The populated preference export is unavailable.");
  expect(JSON.parse(await readFile(populatedDownloadPath, "utf-8"))).toEqual(
    await populatedExportResponse.json(),
  );

  await page.getByRole("checkbox", { name: /removes all goals, experience, and interests/ }).check();
  await submitMutation(page, page.getByRole("button", { name: "Reset learning preferences" }));
  await expect(page.getByText("You have not added a learning goal yet.")).toBeVisible();
  await expect(page.getByText("You have not described any experience yet.")).toBeVisible();
  await expect(page.getByText("You have not added an interest yet.")).toBeVisible();

  // Leave a small, variable final profile for browser/headless/restart correlation.
  await goals.getByLabel("Goal").first().fill("Build a diversified example portfolio");
  await goals.getByLabel(/Why this matters/).first().fill("Use evidence and record assumptions.");
  await submitMutation(page, goals.getByRole("button", { name: "Add goal" }));
  await experience.getByLabel("Topic or skill").first().fill("Portfolio comparison");
  await experience.getByLabel("Your experience").first().selectOption("new");
  await submitMutation(page, experience.getByRole("button", { name: "Add experience" }));
  await interests.getByLabel("Add an interest").fill("Index funds Σ");
  const exactReplay = await submitMutation(
    page,
    interests.getByRole("button", { name: "Add interest" }),
  );

  await page.reload();
  await expect(page.getByRole("heading", { name: "Build a diversified example portfolio" })).toBeVisible();
  await page.getByLabel("Edit goal: Build a diversified example portfolio, item 1").click();
  await expect(page.locator('input[name="title"]').nth(1)).toHaveValue("Build a diversified example portfolio");
  await page.getByText("Technical record", { exact: true }).last().click();
  await expect(page.getByText(exactReplay.response.profile_id, { exact: true })).toBeVisible();

  for (const theme of ["dark", "light", "system"] as const) {
    await page.getByLabel("Theme").selectOption(theme);
    await expect(page.locator("html")).toHaveAttribute("data-theme", theme);
  }
  await page.emulateMedia({ colorScheme: "dark", forcedColors: "active", reducedMotion: "reduce" });
  await page.setViewportSize({ width: 320, height: 900 });
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  await page.setViewportSize({ width: 1280, height: 900 });
  await page.emulateMedia({ colorScheme: "light", forcedColors: "none", reducedMotion: "no-preference" });

  const exportResponsePromise = page.waitForResponse(
    (response) => new URL(response.url()).pathname === `${PREFERENCES_API}/export`,
  );
  const downloadPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: "Download preferences" }).click();
  const [exportResponse, download] = await Promise.all([
    exportResponsePromise,
    downloadPromise,
  ]);
  const exportDocument = (await exportResponse.json()) as LearnerPreferenceExport;
  const downloadedPath = await download.path();
  if (!downloadedPath) throw new Error("The final preference export is unavailable.");
  expect(JSON.parse(await readFile(downloadedPath, "utf-8"))).toEqual(exportDocument);
  await expect(page.getByText("Your learning-preferences download is ready.")).toBeVisible();

  const profile = await responseJson<LearnerPreferenceProfile>(
    await context.request.get(PREFERENCES_API),
  );
  const history = await responseJson<LearnerPreferenceHistory>(
    await context.request.get(`${PREFERENCES_API}/history`),
  );
  expect(profile).toEqual(exactReplay.response);
  expect(exportDocument.profile).toEqual(profile);
  expect(exportDocument.history).toEqual(history);

  const capturePath = process.env.FINANCIAL_AI_ACADEMY_LEARNER_PREFERENCES_CAPTURE;
  if (capturePath) {
    const sameKey = crypto.randomUUID();
    const changedKey = crypto.randomUUID();
    await writeFile(
      capturePath,
      `${JSON.stringify(
        {
          schema_version: "1.0.0",
          profile,
          history,
          export: exportDocument,
          exact_replay_request: exactReplay.request,
          exact_replay_response: exactReplay.response,
          races: {
            same_key_same_payload: {
              requests: [0, 1].map(() => ({
                schema_version: "1.0.0",
                idempotency_key: sameKey,
                expected_revision: profile.revision,
                mutation: { operation: "create_interest", label: "Race replay result" },
              })),
              expected: ["accepted", "accepted"],
            },
            same_key_changed_payload: {
              requests: ["Race conflict A", "Race conflict B"].map((label) => ({
                schema_version: "1.0.0",
                idempotency_key: changedKey,
                expected_revision: profile.revision + 1,
                mutation: { operation: "create_interest", label },
              })),
              expected: ["accepted", "conflict"],
            },
            different_key_same_revision: {
              requests: ["Race stale A", "Race stale B"].map((label) => ({
                schema_version: "1.0.0",
                idempotency_key: crypto.randomUUID(),
                expected_revision: profile.revision + 2,
                mutation: { operation: "create_interest", label },
              })),
              expected: ["accepted", "stale"],
            },
          },
          expected: {
            final_goal: "Build a diversified example portfolio",
            final_experience: "Portfolio comparison",
            final_interest: "Index funds Σ",
            reset_recorded: true,
            populated_export_profile_revision: (
              (await populatedExportResponse.json()) as LearnerPreferenceExport
            ).profile.revision,
          },
        },
        null,
        2,
      )}\n`,
      { encoding: "utf-8", flag: "wx" },
    );
  }
});

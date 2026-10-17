import AxeBuilder from "@axe-core/playwright";
import { expect, test, type APIResponse, type Locator, type Page } from "@playwright/test";
import { readFile, writeFile } from "node:fs/promises";

import type {
  PreparedPresentationPreferenceRequest,
  PresentationPreferenceExport,
  PresentationPreferenceHistory,
  PresentationPreferenceProfile,
  PresentationSettings,
} from "../../../src/features/presentation-preferences/model";
import {
  presentationPreferenceExportIsSafe,
  presentationPreferenceHistoryIsSafe,
  presentationPreferenceProfileIsSafe,
} from "../../../src/features/presentation-preferences/model";


const PREFERENCES_API = "/api/v1/learner-presentation-preferences";
const MUTATION_API = `${PREFERENCES_API}/mutations`;
const BASELINE: PresentationSettings = {
  motion: "system",
  reading_width: "standard",
  text_size: "default",
  text_spacing: "default",
};

type AcceptedMutation = {
  request: PreparedPresentationPreferenceRequest;
  response: PresentationPreferenceProfile;
};

async function responseJson<T>(response: APIResponse): Promise<T> {
  expect(response.status()).toBe(200);
  return (await response.json()) as T;
}

async function submitMutation(page: Page, control: Locator): Promise<AcceptedMutation> {
  const responsePromise = page.waitForResponse(
    (response) => new URL(response.url()).pathname === MUTATION_API &&
      response.request().method() === "POST",
  );
  await control.click();
  const response = await responsePromise;
  expect(response.status()).toBe(200);
  const accepted = (await response.json()) as PresentationPreferenceProfile;
  expect(await presentationPreferenceProfileIsSafe(accepted)).toBe(true);
  await expect(page.locator('input[name="expected_revision"]').first()).toHaveValue(
    String(accepted.revision),
  );
  return {
    request: response.request().postDataJSON() as PreparedPresentationPreferenceRequest,
    response: accepted,
  };
}

async function choose(page: Page, settings: PresentationSettings) {
  for (const [name, value] of Object.entries(settings)) {
    await page.locator(`input[name="${name}"][value="${value}"]`).check();
  }
  await expect(page.locator("html")).toHaveAttribute("data-text-size", settings.text_size);
  await expect(page.locator("html")).toHaveAttribute("data-text-spacing", settings.text_spacing);
  await expect(page.locator("html")).toHaveAttribute("data-reading-width", settings.reading_width);
  await expect(page.locator("html")).toHaveAttribute("data-motion", settings.motion);
}

function allSettings(): PresentationSettings[] {
  return ["default", "larger"].flatMap((text_size) =>
    ["default", "increased"].flatMap((text_spacing) =>
      ["standard", "focused"].flatMap((reading_width) =>
        ["system", "reduce"].map((motion) => ({
          motion,
          reading_width,
          text_size,
          text_spacing,
        }) as PresentationSettings),
      ),
    ),
  );
}

function profileSettings(profile: PresentationPreferenceProfile): PresentationSettings {
  return {
    motion: profile.motion,
    reading_width: profile.reading_width,
    text_size: profile.text_size,
    text_spacing: profile.text_spacing,
  };
}

test("preserves explicit display choices through the live public API", async ({
  context,
  page,
}) => {
  test.setTimeout(120_000);
  await page.goto("/preferences/display");
  await expect(page.getByRole("heading", { level: 1, name: "Display and accessibility" })).toBeVisible();
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);

  const initial = await responseJson<PresentationPreferenceProfile>(
    await context.request.get(PREFERENCES_API),
  );
  expect(initial).toMatchObject({ revision: 1, ...BASELINE });
  expect(await presentationPreferenceProfileIsSafe(initial)).toBe(true);
  await expect(page.locator("html")).toHaveAttribute("data-text-size", "default");
  await expect(page.locator("html")).toHaveAttribute("data-text-spacing", "default");
  await expect(page.locator("html")).toHaveAttribute("data-reading-width", "standard");
  await expect(page.locator("html")).toHaveAttribute("data-motion", "system");

  await page.getByLabel("Theme", { exact: true }).selectOption("dark");
  await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");

  const mutationRequests: PreparedPresentationPreferenceRequest[] = [];
  page.on("request", (request) => {
    if (new URL(request.url()).pathname === MUTATION_API && request.method() === "POST") {
      mutationRequests.push(request.postDataJSON() as PreparedPresentationPreferenceRequest);
    }
  });

  await choose(page, { ...BASELINE, text_size: "larger" });
  const beforeCancel = mutationRequests.length;
  await page.getByRole("button", { name: "Cancel preview" }).click();
  expect(mutationRequests).toHaveLength(beforeCancel);
  await choose(page, BASELINE);

  const combinations = allSettings();
  expect(combinations).toHaveLength(16);
  for (const settings of combinations) {
    await choose(page, settings);
    if (
      settings.text_size === BASELINE.text_size &&
      settings.text_spacing === BASELINE.text_spacing &&
      settings.reading_width === BASELINE.reading_width &&
      settings.motion === BASELINE.motion
    ) continue;
    const accepted = await submitMutation(
      page,
      page.getByRole("button", { name: "Save display choices" }),
    );
    expect(profileSettings(accepted.response)).toEqual(settings);
  }

  const populatedProfile = await responseJson<PresentationPreferenceProfile>(
    await context.request.get(PREFERENCES_API),
  );
  const populatedExport = await responseJson<PresentationPreferenceExport>(
    await context.request.get(`${PREFERENCES_API}/export`),
  );
  expect(await presentationPreferenceExportIsSafe(populatedExport)).toBe(true);
  expect(populatedExport.profile).toEqual(populatedProfile);

  await page.getByLabel(/I understand that this resets/).check();
  const exactReplay = await submitMutation(
    page,
    page.getByRole("button", { name: "Reset saved display choices" }),
  );
  expect(profileSettings(exactReplay.response)).toEqual(BASELINE);
  await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
  await choose(page, BASELINE);
  await expect(page.getByText("Reset display choices")).toBeVisible();

  await page.setViewportSize({ width: 320, height: 720 });
  await page.evaluate(() => {
    document.documentElement.style.fontSize = "200%";
  });
  const dimensions = await page.evaluate(() => ({
    content: document.documentElement.scrollWidth,
    viewport: document.documentElement.clientWidth,
  }));
  expect(dimensions.content).toBeLessThanOrEqual(dimensions.viewport);
  await page.emulateMedia({ forcedColors: "active", reducedMotion: "reduce" });
  const downloadControl = page.getByRole("button", { name: "Download display choices" });
  await downloadControl.focus();
  await page.keyboard.press("Tab");
  await page.keyboard.press("Shift+Tab");
  await expect(downloadControl).toBeFocused();
  expect(await downloadControl.evaluate(
    (element) => getComputedStyle(element).outlineStyle,
  )).not.toBe("none");
  await page.emulateMedia({ forcedColors: "none", reducedMotion: "no-preference" });
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);

  const exportResponsePromise = page.waitForResponse(
    (response) => new URL(response.url()).pathname === `${PREFERENCES_API}/export`,
  );
  const downloadPromise = page.waitForEvent("download");
  await downloadControl.press("Enter");
  const [exportResponse, download] = await Promise.all([exportResponsePromise, downloadPromise]);
  const exportDocument = (await exportResponse.json()) as PresentationPreferenceExport;
  expect(await presentationPreferenceExportIsSafe(exportDocument)).toBe(true);
  const downloadedPath = await download.path();
  if (!downloadedPath) throw new Error("The presentation-preference export is unavailable.");
  expect(JSON.parse(await readFile(downloadedPath, "utf-8"))).toEqual(exportDocument);

  const profile = await responseJson<PresentationPreferenceProfile>(
    await context.request.get(PREFERENCES_API),
  );
  const history = await responseJson<PresentationPreferenceHistory>(
    await context.request.get(`${PREFERENCES_API}/history`),
  );
  expect(profile).toEqual(exactReplay.response);
  expect(presentationPreferenceHistoryIsSafe(history, profile)).toBe(true);
  expect(exportDocument.profile).toEqual(profile);
  expect(exportDocument.history).toEqual(history);
  expect(exportDocument).not.toHaveProperty("theme");

  const capturePath = process.env.FINANCIAL_AI_ACADEMY_PRESENTATION_PREFERENCES_CAPTURE;
  if (capturePath) {
    const sameKey = crypto.randomUUID();
    const changedKey = crypto.randomUUID();
    const replacement = (expected_revision: number, idempotency_key: string, settings: PresentationSettings) => ({
      schema_version: "1.0.0" as const,
      idempotency_key,
      expected_revision,
      mutation: { operation: "replace_preferences" as const, ...settings },
    });
    await writeFile(
      capturePath,
      `${JSON.stringify({
        schema_version: "1.0.0",
        profile,
        history,
        export: exportDocument,
        exact_replay_request: exactReplay.request,
        exact_replay_response: exactReplay.response,
        races: {
          same_key_same_payload: {
            requests: [0, 1].map(() => replacement(profile.revision, sameKey, {
              motion: "reduce", reading_width: "focused", text_size: "larger", text_spacing: "increased",
            })),
            expected: ["accepted", "accepted"],
          },
          same_key_changed_payload: {
            requests: ["default", "larger"].map((text_size) => replacement(
              profile.revision + 1,
              changedKey,
              { motion: "system", reading_width: "focused", text_size: text_size as "default" | "larger", text_spacing: "increased" },
            )),
            expected: ["accepted", "conflict"],
          },
          different_key_same_revision: {
            requests: ["standard", "focused"].map((reading_width) => replacement(
              profile.revision + 2,
              crypto.randomUUID(),
              { motion: "reduce", reading_width: reading_width as "standard" | "focused", text_size: "larger", text_spacing: "default" },
            )),
            expected: ["accepted", "stale"],
          },
        },
        expected: {
          all_combinations: combinations,
          populated_export_profile_revision: populatedExport.profile.revision,
          reset_recorded: true,
          theme_after_reset: "dark",
        },
      }, null, 2)}\n`,
      { encoding: "utf-8", flag: "wx" },
    );
  }
});

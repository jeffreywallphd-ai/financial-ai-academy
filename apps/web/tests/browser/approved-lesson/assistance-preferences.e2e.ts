import AxeBuilder from "@axe-core/playwright";
import { expect, test, type APIResponse, type Locator, type Page } from "@playwright/test";
import { readFile, writeFile } from "node:fs/promises";

import type {
  AssistancePreferenceExport,
  AssistancePreferenceHistory,
  AssistancePreferenceProfile,
  PreparedAssistancePreferenceRequest,
} from "../../../src/features/assistance-preferences/model";
import {
  assistancePreferenceExportIsSafe,
  assistancePreferenceHistoryIsSafe,
  assistancePreferenceProfileIsSafe,
} from "../../../src/features/assistance-preferences/model";


const PREFERENCES_API = "/api/v1/learner-assistance-preferences";
const MUTATION_API = `${PREFERENCES_API}/mutations`;
const SESSION_API = "/api/v1/session/single-profile";
const LOCAL_KEY = "financial-ai-academy.local-learning-reminder-preference.v1";

type ObservedApiRequest = { method: string; path: string };

function assistanceRequestIsAllowed({ method, path }: ObservedApiRequest): boolean {
  return method === "GET" || (method === "POST" && (path === SESSION_API || path === MUTATION_API));
}

async function executionCalls(page: Page): Promise<Record<string, number>> {
  return page.evaluate(() => (
    window as unknown as Window & { __assistanceExecutionCalls: Record<string, number> }
  ).__assistanceExecutionCalls);
}

type AcceptedMutation = {
  request: PreparedAssistancePreferenceRequest;
  response: AssistancePreferenceProfile;
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
  const accepted = (await response.json()) as AssistancePreferenceProfile;
  expect(await assistancePreferenceProfileIsSafe(accepted)).toBe(true);
  await expect(page.locator('input[name="expected_revision"]').first()).toHaveValue(
    String(accepted.revision),
  );
  return {
    request: response.request().postDataJSON() as PreparedAssistancePreferenceRequest,
    response: accepted,
  };
}

test("preserves AI-help choice while keeping future reminders in this browser", async ({
  context,
  page,
}) => {
  test.setTimeout(120_000);
  await page.addInitScript(() => {
    const marker = { notificationPermissions: 0, serviceWorkers: 0 };
    Object.defineProperty(window, "__assistanceExecutionCalls", { value: marker });
    if ("Notification" in window && typeof Notification.requestPermission === "function") {
      Notification.requestPermission = async () => {
        marker.notificationPermissions += 1;
        return "denied";
      };
    }
    if (navigator.serviceWorker) {
      navigator.serviceWorker.register = (async () => {
        marker.serviceWorkers += 1;
        throw new Error("Service-worker registration is outside this feature.");
      }) as typeof navigator.serviceWorker.register;
    }
  });

  expect(assistanceRequestIsAllowed({ method: "GET", path: "/api/v1/learner-presentation-preferences" })).toBe(true);
  expect(assistanceRequestIsAllowed({ method: "POST", path: SESSION_API })).toBe(true);
  expect(assistanceRequestIsAllowed({ method: "POST", path: MUTATION_API })).toBe(true);
  expect(assistanceRequestIsAllowed({ method: "DELETE", path: SESSION_API })).toBe(false);
  expect(assistanceRequestIsAllowed({ method: "PUT", path: MUTATION_API })).toBe(false);
  expect(assistanceRequestIsAllowed({ method: "POST", path: "/api/v1/notifications" })).toBe(false);

  const observedRequests: ObservedApiRequest[] = [];
  page.on("request", (request) => {
    const url = new URL(request.url());
    if (url.pathname.startsWith("/api/")) {
      observedRequests.push({ method: request.method(), path: url.pathname });
    }
  });

  await page.goto("/preferences/assistance");
  await expect(page.getByRole("heading", { level: 1, name: "AI help and reminders" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Nothing runs in the background" })).toBeVisible();
  await expect(page.getByRole("radio", { name: "Keep AI help off" })).toBeChecked();
  await expect(page.getByRole("radio", { name: "Keep reminders off" })).toBeChecked();
  expect(await page.evaluate((key) => localStorage.getItem(key), LOCAL_KEY)).toBeNull();

  const initial = await responseJson<AssistancePreferenceProfile>(
    await context.request.get(PREFERENCES_API),
  );
  expect(initial).toMatchObject({ revision: 1, assistance_mode: "off" });
  expect(await assistancePreferenceProfileIsSafe(initial)).toBe(true);

  await page.getByRole("radio", { name: /Offer a help option when available/i }).check();
  const saved = await submitMutation(
    page,
    page.getByRole("button", { name: "Save AI-help choice" }),
  );
  expect(saved.response).toMatchObject({ revision: 2, assistance_mode: "on_request" });
  expect(saved.request).not.toHaveProperty("learner_id");
  expect(saved.request).not.toHaveProperty("provider");

  const requestsBeforeLocalSave = observedRequests.length;
  await page.getByRole("radio", { name: /Allow in-app reminders when available/i }).check();
  await page.getByRole("button", { name: "Save this-browser choice" }).click();
  await expect(page.getByText("This browser is using the saved choice.")).toBeVisible();
  const localSaveRequests = observedRequests.slice(requestsBeforeLocalSave);
  expect(localSaveRequests).toContainEqual({
    method: "GET",
    path: "/api/v1/learner-assistance-preferences/export",
  });
  expect(
    localSaveRequests.every(
      ({ method, path }) =>
        method === "GET" &&
        (path === "/api/v1/learner-assistance-preferences/export" ||
          path ===
            "/api/v1/guidance/contextual-help/ai-assistance/versions/1.0.0" ||
          path ===
            "/api/v1/guidance/feature-guidance/ai-assistance/conditions/provider-execution-not-enabled/versions/1.0.0"),
    ),
  ).toBe(true);
  const savedLocal = await page.evaluate((key) => JSON.parse(localStorage.getItem(key) ?? "null"), LOCAL_KEY);
  expect(savedLocal).toMatchObject({ revision: 2, reminder_mode: "in_app_when_available" });
  expect(savedLocal).not.toHaveProperty("learner_id");
  expect(await executionCalls(page)).toEqual({ notificationPermissions: 0, serviceWorkers: 0 });

  await page.reload();
  await expect(page.getByRole("radio", { name: /Offer a help option when available/i })).toBeChecked();
  await expect(page.getByRole("radio", { name: /Allow in-app reminders when available/i })).toBeChecked();

  const serverDownloadPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: "Download AI-help choice" }).click();
  const serverDownload = await serverDownloadPromise;
  const serverPath = await serverDownload.path();
  if (!serverPath) throw new Error("The AI-help preference download is unavailable.");
  const serverExport = JSON.parse(await readFile(serverPath, "utf8")) as AssistancePreferenceExport;
  expect(await assistancePreferenceExportIsSafe(serverExport)).toBe(true);
  expect(serverExport.profile).toEqual(saved.response);

  const localDownloadPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: "Download this-browser choice" }).click();
  const localDownload = await localDownloadPromise;
  const localPath = await localDownload.path();
  if (!localPath) throw new Error("The local reminder download is unavailable.");
  const localExport = JSON.parse(await readFile(localPath, "utf8"));
  expect(localExport.preference).toEqual(savedLocal);
  expect(JSON.stringify(localExport)).not.toContain("learner_id");
  expect(JSON.stringify(localExport)).not.toContain(saved.response.profile_id);

  await page.getByRole("checkbox", { name: /resets only the learner-owned AI-help choice/i }).check();
  const exactReplay = await submitMutation(
    page,
    page.getByRole("button", { name: "Reset AI-help choice" }),
  );
  expect(exactReplay.response).toMatchObject({ revision: 3, assistance_mode: "off" });
  await expect(page.getByRole("radio", { name: /Allow in-app reminders when available/i })).toBeChecked();

  await page.getByRole("checkbox", { name: /resets only the reminder choice/i }).check();
  await page.getByRole("button", { name: "Reset this-browser choice" }).click();
  await expect(page.getByRole("radio", { name: "Keep reminders off" })).toBeChecked();
  await expect(page.getByRole("radio", { name: "Keep AI help off" })).toBeChecked();

  const finalLocal = await page.evaluate((key) => JSON.parse(localStorage.getItem(key) ?? "null"), LOCAL_KEY);
  expect(finalLocal).toMatchObject({ revision: 3, reminder_mode: "off" });
  expect(finalLocal).not.toHaveProperty("learner_id");

  const profile = await responseJson<AssistancePreferenceProfile>(
    await context.request.get(PREFERENCES_API),
  );
  const history = await responseJson<AssistancePreferenceHistory>(
    await context.request.get(`${PREFERENCES_API}/history`),
  );
  const exportDocument = await responseJson<AssistancePreferenceExport>(
    await context.request.get(`${PREFERENCES_API}/export`),
  );
  expect(profile).toEqual(exactReplay.response);
  expect(assistancePreferenceHistoryIsSafe(history, profile)).toBe(true);
  expect(await assistancePreferenceExportIsSafe(exportDocument)).toBe(true);
  expect(exportDocument.profile).toEqual(profile);
  expect(exportDocument.history).toEqual(history);

  await page.setViewportSize({ width: 320, height: 900 });
  await page.evaluate(() => { document.documentElement.style.fontSize = "200%"; });
  const dimensions = await page.evaluate(() => ({
    content: document.documentElement.scrollWidth,
    viewport: document.documentElement.clientWidth,
  }));
  expect(dimensions.content).toBeLessThanOrEqual(dimensions.viewport);
  await page.emulateMedia({ colorScheme: "dark", forcedColors: "active", reducedMotion: "reduce" });
  const downloadControl = page.getByRole("button", { name: "Download AI-help choice" });
  await downloadControl.focus();
  await page.keyboard.press("Tab");
  await page.keyboard.press("Shift+Tab");
  await expect(downloadControl).toBeFocused();
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);

  expect(await executionCalls(page)).toEqual({ notificationPermissions: 0, serviceWorkers: 0 });
  expect(observedRequests.filter((request) => !assistanceRequestIsAllowed(request))).toEqual([]);

  const capturePath = process.env.FINANCIAL_AI_ACADEMY_ASSISTANCE_PREFERENCES_CAPTURE;
  if (capturePath) {
    const sameKey = crypto.randomUUID();
    const changedKey = crypto.randomUUID();
    const replacement = (
      expected_revision: number,
      idempotency_key: string,
      assistance_mode: "off" | "on_request",
    ): PreparedAssistancePreferenceRequest => ({
      schema_version: "1.0.0",
      idempotency_key,
      expected_revision,
      mutation: { operation: "replace_preferences", assistance_mode },
    });
    const reset = (
      expected_revision: number,
      idempotency_key: string,
    ): PreparedAssistancePreferenceRequest => ({
      schema_version: "1.0.0",
      idempotency_key,
      expected_revision,
      mutation: { operation: "reset_profile" },
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
        local: {
          saved: savedLocal,
          export: localExport,
          reset: finalLocal,
        },
        races: {
          same_key_same_payload: {
            requests: [0, 1].map(() => replacement(profile.revision, sameKey, "on_request")),
            expected: ["accepted", "accepted"],
          },
          same_key_changed_payload: {
            requests: [
              replacement(profile.revision + 1, changedKey, "off"),
              reset(profile.revision + 1, changedKey),
            ],
            expected: ["accepted", "conflict"],
          },
          different_key_same_revision: {
            requests: [0, 1].map(() => replacement(
              profile.revision + 2,
              crypto.randomUUID(),
              "on_request",
            )),
            expected: ["accepted", "stale"],
          },
        },
        expected: {
          first_open_server_revision: initial.revision,
          local_saved_revision: savedLocal.revision,
          local_reset_revision: finalLocal.revision,
          reset_recorded: true,
        },
      }, null, 2)}\n`,
      { encoding: "utf-8", flag: "wx" },
    );
  }
});

import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page, type Route } from "@playwright/test";
import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";

import type {
  AssistancePreferenceExport,
  AssistancePreferenceHistory,
  AssistancePreferenceProfile,
  PreparedAssistancePreferenceRequest,
} from "../../../src/features/assistance-preferences/model";


function canonical(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(canonical);
  if (typeof value === "object" && value !== null) {
    return Object.fromEntries(
      Object.entries(value as Record<string, unknown>)
        .sort(([first], [second]) => first.localeCompare(second))
        .map(([key, child]) => [key, canonical(child)]),
    );
  }
  return value;
}

function digest(value: unknown): string {
  return createHash("sha256").update(JSON.stringify(canonical(value)), "utf8").digest("hex");
}

function makeProfile(revision: number, mode: "off" | "on_request"): AssistancePreferenceProfile {
  const material = {
    schema_version: "1.0.0" as const,
    profile_id: "profile.assistance-1",
    learner_id: "11111111-1111-4111-8111-111111111111",
    revision,
    assistance_mode: mode,
    created_at: "2026-10-17T20:00:00Z",
    updated_at: `2026-10-17T20:${String(revision).padStart(2, "0")}:00Z`,
  };
  return { ...material, profile_digest: digest(material) };
}

function makeExport(
  profile: AssistancePreferenceProfile,
  history: AssistancePreferenceHistory,
): AssistancePreferenceExport {
  return {
    schema_version: "1.0.0",
    purpose: "A portable copy of the AI-help choice you selected.",
    limitations: ["This choice does not enable or call an AI service."],
    exported_at: "2026-10-17T21:00:00Z",
    profile,
    history,
  };
}

function json(route: Route, status: number, body: unknown) {
  return route.fulfill({ status, contentType: "application/json", body: JSON.stringify(body) });
}

async function installApi(page: Page) {
  let profile = makeProfile(1, "off");
  let history: AssistancePreferenceHistory = {
    schema_version: "1.0.0",
    profile_id: profile.profile_id,
    current_revision: 1,
    changes: [],
  };
  const requests: PreparedAssistancePreferenceRequest[] = [];
  const calls: Array<{ method: string; path: string }> = [];

  await page.route("**/api/v1/**", async (route) => {
    const request = route.request();
    const path = new URL(request.url()).pathname;
    calls.push({ method: request.method(), path });
    if (path === "/api/v1/session/single-profile") {
      return json(route, 201, {
        status: "ready",
        authentication_method: "single_profile",
        expires_at: "2026-10-18T20:00:00Z",
      });
    }
    if (path === "/api/v1/learner-assistance-preferences/export") {
      return json(route, 200, makeExport(profile, history));
    }
    if (path === "/api/v1/learner-assistance-preferences/mutations") {
      const body = request.postDataJSON() as PreparedAssistancePreferenceRequest;
      requests.push(body);
      const mode = body.mutation.operation === "reset_profile"
        ? "off"
        : body.mutation.assistance_mode;
      profile = makeProfile(profile.revision + 1, mode);
      history = {
        schema_version: "1.0.0",
        profile_id: profile.profile_id,
        current_revision: profile.revision,
        changes: [...history.changes, {
          schema_version: "1.0.0",
          revision: profile.revision,
          operation: body.mutation.operation,
          object_kind: "profile",
          object_id: null,
          occurred_at: profile.updated_at,
          resulting_profile_digest: profile.profile_digest,
        }],
      };
      return json(route, 200, profile);
    }
    return json(route, 404, { code: "not_found" });
  });
  return { calls, requests };
}

test("keeps learner-owned AI help and this-browser reminders separate and inert", async ({ page }) => {
  const api = await installApi(page);
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

  await page.goto("/preferences/assistance");
  await expect(page.getByRole("heading", { level: 1, name: "AI help and reminders" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Nothing runs in the background" })).toBeVisible();

  await page.getByRole("radio", { name: /Offer a help option when available/i }).check();
  await page.getByRole("button", { name: "Save AI-help choice" }).click();
  await expect(page.getByText("Offer a help option when available is saved.")).toBeVisible();
  expect(api.requests).toHaveLength(1);
  expect(api.requests[0]).toMatchObject({
    schema_version: "1.0.0",
    expected_revision: 1,
    mutation: { operation: "replace_preferences", assistance_mode: "on_request" },
  });
  expect(api.requests[0]).not.toHaveProperty("learner_id");
  expect(api.requests[0]).not.toHaveProperty("provider");

  const callsBeforeLocalSave = api.calls.length;
  await page.getByRole("radio", { name: /Allow in-app reminders when available/i }).check();
  await page.getByRole("button", { name: "Save this-browser choice" }).click();
  await expect(page.getByText("This browser is using the saved choice.")).toBeVisible();
  const localSaveCalls = api.calls.slice(callsBeforeLocalSave);
  expect(localSaveCalls.every(({ method }) => method === "GET")).toBe(true);
  expect(
    localSaveCalls.filter(
      ({ path }) =>
        path !==
        "/api/v1/guidance/contextual-help/ai-assistance/versions/1.0.0",
    ),
  ).toEqual([
    {
      method: "GET",
      path: "/api/v1/learner-assistance-preferences/export",
    },
  ]);
  const local = await page.evaluate(() => {
    const key = "financial-ai-academy.local-learning-reminder-preference.v1";
    return JSON.parse(window.localStorage.getItem(key) ?? "null");
  });
  expect(local).toMatchObject({ reminder_mode: "in_app_when_available", revision: 2 });
  expect(local).not.toHaveProperty("learner_id");

  await page.reload();
  await expect(page.getByRole("radio", { name: /Offer a help option when available/i })).toBeChecked();
  await expect(page.getByRole("radio", { name: /Allow in-app reminders when available/i })).toBeChecked();

  const serverDownload = page.waitForEvent("download");
  await page.getByRole("button", { name: "Download AI-help choice" }).click();
  const downloadedServer = await serverDownload;
  expect(downloadedServer.suggestedFilename()).toBe("ai-help-preference.json");
  const serverContent = JSON.parse(await readFile(await downloadedServer.path(), "utf8"));
  expect(serverContent.profile).toMatchObject({ assistance_mode: "on_request", revision: 2 });
  expect(serverContent).not.toHaveProperty("preference");

  const localDownload = page.waitForEvent("download");
  await page.getByRole("button", { name: "Download this-browser choice" }).click();
  const downloadedLocal = await localDownload;
  expect(downloadedLocal.suggestedFilename()).toBe("this-browser-reminder-choice.json");
  const localContent = JSON.parse(await readFile(await downloadedLocal.path(), "utf8"));
  expect(localContent.preference).toMatchObject({ reminder_mode: "in_app_when_available", revision: 2 });
  expect(JSON.stringify(localContent)).not.toContain("profile.assistance-1");
  expect(JSON.stringify(localContent)).not.toContain("learner_id");

  await page.getByRole("checkbox", { name: /resets only the learner-owned AI-help choice/i }).check();
  await page.getByRole("button", { name: "Reset AI-help choice" }).click();
  await expect(page.getByRole("radio", { name: "Keep AI help off" })).toBeChecked();
  await expect(page.getByRole("radio", { name: /Allow in-app reminders when available/i })).toBeChecked();

  await page.getByRole("checkbox", { name: /resets only the reminder choice/i }).check();
  await page.getByRole("button", { name: "Reset this-browser choice" }).click();
  await expect(page.getByRole("radio", { name: "Keep reminders off" })).toBeChecked();
  await expect(page.getByRole("radio", { name: "Keep AI help off" })).toBeChecked();

  const executionCalls = await page.evaluate(() => (
    window as unknown as Window & { __assistanceExecutionCalls: Record<string, number> }
  ).__assistanceExecutionCalls);
  expect(executionCalls).toEqual({ notificationPermissions: 0, serviceWorkers: 0 });

  await page.emulateMedia({ colorScheme: "dark", forcedColors: "active", reducedMotion: "reduce" });
  await page.setViewportSize({ width: 320, height: 900 });
  await page.evaluate(() => document.documentElement.style.fontSize = "200%");
  const layout = await page.evaluate(() => ({
    clientWidth: document.documentElement.clientWidth,
    innerWidth: window.innerWidth,
    scrollWidth: document.documentElement.scrollWidth,
    overflowing: [...document.querySelectorAll<HTMLElement>("body *")]
      .filter((element) => {
        const bounds = element.getBoundingClientRect();
        return bounds.right > window.innerWidth + 1 || bounds.left < -1;
      })
      .map((element) => element.tagName.toLowerCase()),
  }));
  expect(layout).toEqual({ clientWidth: 320, innerWidth: 320, scrollWidth: 320, overflowing: [] });
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
});

test("keeps local reminder preferences usable when the protected API is unavailable", async ({ page }) => {
  await page.route("**/api/v1/**", (route) => {
    const path = new URL(route.request().url()).pathname;
    if (path === "/api/v1/session/single-profile") {
      return json(route, 201, {
        status: "ready",
        authentication_method: "single_profile",
        expires_at: "2026-10-18T20:00:00Z",
      });
    }
    return json(route, 503, { code: "service_unavailable" });
  });

  await page.goto("/preferences/assistance");
  await expect(page.getByRole("heading", { name: "AI-help choice temporarily unavailable" })).toBeVisible();
  await page.getByRole("radio", { name: /Allow in-app reminders when available/i }).check();
  await page.getByRole("button", { name: "Save this-browser choice" }).click();
  await expect(page.getByRole("radio", { name: /Allow in-app reminders when available/i })).toBeChecked();
});

test("rejects a scope-expanding protected response without rendering it", async ({ page }) => {
  const profile = makeProfile(1, "off");
  const malformed = { ...profile, provider: "not-authorized" };
  await page.route("**/api/v1/**", (route) => {
    const path = new URL(route.request().url()).pathname;
    if (path === "/api/v1/session/single-profile") {
      return json(route, 201, {
        status: "ready",
        authentication_method: "single_profile",
        expires_at: "2026-10-18T20:00:00Z",
      });
    }
    return json(route, 200, makeExport(malformed as AssistancePreferenceProfile, {
      schema_version: "1.0.0",
      profile_id: profile.profile_id,
      current_revision: 1,
      changes: [],
    }));
  });

  await page.goto("/preferences/assistance");
  await expect(page.getByRole("heading", { name: "AI-help choice could not be shown" })).toBeVisible();
  await expect(page.getByText("not-authorized")).toHaveCount(0);
  await expect(page.getByRole("radio", { name: "Keep reminders off" })).toBeChecked();
});

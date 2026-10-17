import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page, type Route } from "@playwright/test";
import { createHash } from "node:crypto";

import type {
  PreparedPresentationPreferenceRequest,
  PresentationPreferenceExport,
  PresentationPreferenceHistory,
  PresentationPreferenceProfile,
} from "../../../src/features/presentation-preferences/model";


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

function makeProfile(
  revision: number,
  values: Pick<PresentationPreferenceProfile, "motion" | "reading_width" | "text_size" | "text_spacing">,
): PresentationPreferenceProfile {
  const updated = `2026-10-17T20:0${Math.min(revision + 3, 9)}:00Z`;
  const material = {
    schema_version: "1.0.0" as const,
    profile_id: "profile.display-1",
    learner_id: "11111111-1111-4111-8111-111111111111",
    revision,
    ...values,
    created_at: "2026-10-17T20:00:00Z",
    updated_at: updated,
  };
  return { ...material, profile_digest: digest(material) };
}

function makeExport(
  profile: PresentationPreferenceProfile,
  history: PresentationPreferenceHistory,
): PresentationPreferenceExport {
  return {
    schema_version: "1.0.0",
    purpose: "A portable copy of your display choices.",
    limitations: ["These choices are not medical or competency evidence."],
    exported_at: "2026-10-17T20:09:00Z",
    profile,
    history,
  };
}

function json(route: Route, status: number, body: unknown) {
  return route.fulfill({ status, contentType: "application/json", body: JSON.stringify(body) });
}

async function installApi(page: Page) {
  let profile = makeProfile(1, {
    motion: "system",
    reading_width: "standard",
    text_size: "default",
    text_spacing: "default",
  });
  let history: PresentationPreferenceHistory = {
    schema_version: "1.0.0",
    profile_id: profile.profile_id,
    current_revision: profile.revision,
    changes: [],
  };
  const requests: PreparedPresentationPreferenceRequest[] = [];

  await page.route("**/api/v1/**", async (route) => {
    const request = route.request();
    const path = new URL(request.url()).pathname;
    if (path === "/api/v1/session/single-profile") {
      return json(route, 201, {
        status: "ready",
        authentication_method: "single_profile",
        expires_at: "2026-10-18T20:00:00Z",
      });
    }
    if (path === "/api/v1/learner-presentation-preferences/export") {
      return json(route, 200, makeExport(profile, history));
    }
    if (path === "/api/v1/learner-presentation-preferences" && request.method() === "GET") {
      return json(route, 200, profile);
    }
    if (path === "/api/v1/learner-presentation-preferences/mutations") {
      const body = request.postDataJSON() as PreparedPresentationPreferenceRequest;
      requests.push(body);
      const values = body.mutation.operation === "reset_profile"
        ? {
            motion: "system" as const,
            reading_width: "standard" as const,
            text_size: "default" as const,
            text_spacing: "default" as const,
          }
        : body.mutation;
      profile = makeProfile(profile.revision + 1, {
        motion: values.motion,
        reading_width: values.reading_width,
        text_size: values.text_size,
        text_spacing: values.text_spacing,
      });
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
  return requests;
}

test("previews, saves, resets, and exports display choices without mixing local theme", async ({ page }) => {
  const requests = await installApi(page);
  await page.goto("/preferences/display");
  await expect(page.getByRole("heading", { level: 1, name: "Display and accessibility" })).toBeVisible();
  await expect(page.locator("html")).toHaveAttribute("data-text-size", "default");

  await page.getByRole("radio", { name: /Make text, spacing, and controls larger/i }).check();
  await expect(page.locator("html")).toHaveAttribute("data-text-size", "larger");
  await page.getByRole("button", { name: "Cancel preview" }).click();
  await expect(page.locator("html")).toHaveAttribute("data-text-size", "default");

  await page.getByRole("radio", { name: /Make text, spacing, and controls larger/i }).check();
  await page.getByRole("radio", { name: /Add more room around text/i }).check();
  await page.getByRole("radio", { name: /Keep long text in a narrower column/i }).check();
  await page.getByRole("radio", { name: /Remove optional application motion/i }).check();
  await page.getByRole("button", { name: "Save display choices" }).click();

  await expect(page.locator("html")).toHaveAttribute("data-text-size", "larger");
  await expect(page.locator("html")).toHaveAttribute("data-text-spacing", "increased");
  await expect(page.locator("html")).toHaveAttribute("data-reading-width", "focused");
  await expect(page.locator("html")).toHaveAttribute("data-motion", "reduce");
  expect(requests).toHaveLength(1);
  expect(requests[0]).toMatchObject({
    schema_version: "1.0.0",
    expected_revision: 1,
    mutation: {
      operation: "replace_preferences",
      text_size: "larger",
      text_spacing: "increased",
      reading_width: "focused",
      motion: "reduce",
    },
  });
  expect(requests[0]).not.toHaveProperty("learner_id");
  expect(requests[0]).not.toHaveProperty("theme");

  await page.getByLabel("Theme").last().selectOption("dark");
  await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
  await page.getByRole("checkbox", { name: /resets the four saved display choices/i }).check();
  await page.getByRole("button", { name: "Reset saved display choices" }).click();
  await expect(page.locator("html")).toHaveAttribute("data-text-size", "default");
  await expect(page.locator("html")).toHaveAttribute("data-motion", "system");
  await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
  expect(requests[1]?.mutation).toEqual({ operation: "reset_profile" });

  await page.getByText("Technical record").click();
  await expect(page.getByText("profile.display-1", { exact: true })).toBeVisible();
  const download = page.waitForEvent("download");
  await page.getByRole("button", { name: "Download display choices" }).click();
  expect((await download).suggestedFilename()).toBe("display-accessibility-settings.json");
  await expect(page.getByText("Your download is ready.")).toBeVisible();

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
      .map((element) => {
        const bounds = element.getBoundingClientRect();
        return `${element.tagName.toLowerCase()}.${element.className}:${Math.round(bounds.left)}-${Math.round(bounds.right)}`;
      }),
  }));
  expect(layout).toEqual({
    clientWidth: 320,
    innerWidth: 320,
    scrollWidth: 320,
    overflowing: [],
  });
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
});

test("keeps the safe display and local theme usable when saved choices are unavailable", async ({ page }) => {
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

  await page.goto("/preferences/display");
  await expect(page.getByRole("heading", { name: "Display settings temporarily unavailable" })).toBeVisible();
  await expect(page.locator("html")).toHaveAttribute("data-text-size", "default");
  await expect(page.locator("html")).toHaveAttribute("data-motion", "system");
  await page.getByLabel("Theme").selectOption("dark");
  await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
});

test("rejects malformed saved fields without rendering them", async ({ page }) => {
  const profile = makeProfile(1, {
    motion: "system",
    reading_width: "standard",
    text_size: "default",
    text_spacing: "default",
  });
  const malformed = { ...profile, inferred_disability: "low_vision" };
  await page.route("**/api/v1/**", (route) => {
    const path = new URL(route.request().url()).pathname;
    if (path === "/api/v1/session/single-profile") {
      return json(route, 201, {
        status: "ready",
        authentication_method: "single_profile",
        expires_at: "2026-10-18T20:00:00Z",
      });
    }
    if (path.endsWith("/export")) {
      return json(route, 200, {
        ...makeExport(profile, {
          schema_version: "1.0.0",
          profile_id: profile.profile_id,
          current_revision: 1,
          changes: [],
        }),
        profile: malformed,
      });
    }
    return json(route, 200, malformed);
  });

  await page.goto("/preferences/display");
  await expect(page.getByRole("heading", { name: "Display settings could not be shown" })).toBeVisible();
  await expect(page.getByText("low_vision")).toHaveCount(0);
  await expect(page.locator("html")).toHaveAttribute("data-text-size", "default");
});

import { describe, expect, it, vi } from "vitest";

import {
  createPresentationPreferencesAction,
  createPresentationPreferencesLoader,
  createPresentationProfileReader,
} from "../../src/features/presentation-preferences/api";
import {
  presentationPreferenceExportIsSafe,
  presentationPreferenceHistoryIsSafe,
  presentationPreferenceProfileIsSafe,
  presentationSettingsFromProfile,
  type PresentationPreferenceExport,
  type PresentationPreferenceHistory,
  type PresentationPreferenceProfile,
  type PresentationSettings,
} from "../../src/features/presentation-preferences/model";
import type { FinancialAcademyApiClient } from "../../src/generated/api-client";
import type { SingleProfileSession } from "../../src/platform/auth/singleProfileSession";
import { applyPresentationSettings } from "../../src/platform/presentation/presentation";


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

async function digest(value: unknown): Promise<string> {
  const bytes = new TextEncoder().encode(JSON.stringify(canonical(value)));
  const result = await crypto.subtle.digest("SHA-256", bytes);
  return [...new Uint8Array(result)]
    .map((byte) => byte.toString(16).padStart(2, "0"))
    .join("");
}

async function profileFixture(
  settings: PresentationSettings = {
    motion: "system",
    reading_width: "standard",
    text_size: "default",
    text_spacing: "default",
  },
  revision = 1,
): Promise<PresentationPreferenceProfile> {
  const material = {
    schema_version: "1.0.0" as const,
    profile_id: "profile.display-1",
    learner_id: "11111111-1111-4111-8111-111111111111",
    revision,
    ...settings,
    created_at: "2026-10-17T20:00:00Z",
    updated_at: "2026-10-17T20:05:00Z",
  };
  return { ...material, profile_digest: await digest(material) };
}

function historyFixture(
  profile: PresentationPreferenceProfile,
): PresentationPreferenceHistory {
  return {
    schema_version: "1.0.0",
    profile_id: profile.profile_id,
    current_revision: profile.revision,
    changes: profile.revision === 1 ? [] : [{
      schema_version: "1.0.0",
      revision: profile.revision,
      operation: "replace_preferences",
      object_kind: "profile",
      object_id: null,
      occurred_at: profile.updated_at,
      resulting_profile_digest: profile.profile_digest,
    }],
  };
}

function exportFixture(
  profile: PresentationPreferenceProfile,
): PresentationPreferenceExport {
  return {
    schema_version: "1.0.0",
    purpose: "A portable copy of your display choices.",
    limitations: ["These choices are not medical or competency evidence."],
    exported_at: "2026-10-17T20:06:00Z",
    profile,
    history: historyFixture(profile),
  };
}

function readySession() {
  return {
    ensure: vi.fn().mockResolvedValue({ status: "ready" }),
    invalidate: vi.fn(),
  } as unknown as SingleProfileSession;
}

describe("presentation preference contract adapter", () => {
  it("accepts and maps every closed display combination without preferring one", async () => {
    const combinations: PresentationSettings[] = [];
    for (const text_size of ["default", "larger"] as const) {
      for (const text_spacing of ["default", "increased"] as const) {
        for (const reading_width of ["standard", "focused"] as const) {
          for (const motion of ["system", "reduce"] as const) {
            combinations.push({ text_size, text_spacing, reading_width, motion });
          }
        }
      }
    }

    expect(combinations).toHaveLength(16);
    for (const [index, settings] of combinations.entries()) {
      const profile = await profileFixture(settings, index + 1);
      expect(await presentationPreferenceProfileIsSafe(profile)).toBe(true);
      expect(presentationSettingsFromProfile(profile)).toEqual(settings);
      expect(presentationPreferenceHistoryIsSafe(historyFixture(profile), profile)).toBe(true);
      expect(await presentationPreferenceExportIsSafe(exportFixture(profile))).toBe(true);
    }
  });

  it("fails closed for extra fields, invalid values, bad digests, and mismatched history", async () => {
    const profile = await profileFixture(undefined, 2);
    expect(await presentationPreferenceProfileIsSafe({ ...profile, inferred_need: "large_text" })).toBe(false);
    expect(await presentationPreferenceProfileIsSafe({ ...profile, text_size: "smaller" })).toBe(false);
    expect(await presentationPreferenceProfileIsSafe({ ...profile, profile_digest: "0".repeat(64) })).toBe(false);
    expect(presentationPreferenceHistoryIsSafe({
      ...historyFixture(profile),
      current_revision: 1,
    }, profile)).toBe(false);
    expect(await presentationPreferenceExportIsSafe({
      ...exportFixture(profile),
      history: { ...historyFixture(profile), profile_id: "profile.other-1" },
    })).toBe(false);
  });

  it("applies exactly four semantic root attributes and safely rejects an unknown runtime value", () => {
    const attributes = new Map<string, string>();
    const root = { setAttribute: (name: string, value: string) => attributes.set(name, value) };
    const applied = applyPresentationSettings({
      motion: "reduce",
      reading_width: "focused",
      text_size: "larger",
      text_spacing: "increased",
    }, root);
    expect(applied).toEqual({
      motion: "reduce",
      reading_width: "focused",
      text_size: "larger",
      text_spacing: "increased",
    });
    expect(Object.fromEntries(attributes)).toEqual({
      "data-motion": "reduce",
      "data-reading-width": "focused",
      "data-text-size": "larger",
      "data-text-spacing": "increased",
    });

    applyPresentationSettings({
      motion: "forced" as "reduce",
      reading_width: "focused",
      text_size: "larger",
      text_spacing: "increased",
    }, root);
    expect(Object.fromEntries(attributes)).toEqual({
      "data-motion": "system",
      "data-reading-width": "standard",
      "data-text-size": "default",
      "data-text-spacing": "default",
    });
  });
});

describe("presentation preference generated-client adapters", () => {
  it("loads one coherent validated export through the public client", async () => {
    const profile = await profileFixture();
    const exported = exportFixture(profile);
    const get = vi.fn().mockResolvedValue({
      data: exported,
      response: new Response(null, { status: 200 }),
    });
    const loader = createPresentationPreferencesLoader(
      { GET: get } as unknown as FinancialAcademyApiClient,
      readySession(),
    );

    await expect(loader({
      request: new Request("http://example.test/preferences/display"),
      params: {},
    } as Parameters<typeof loader>[0])).resolves.toEqual({
      status: "ready",
      export: exported,
      history: exported.history,
      profile,
    });
    expect(get).toHaveBeenCalledWith(
      "/api/v1/learner-presentation-preferences/export",
      expect.objectContaining({ signal: expect.any(AbortSignal) }),
    );
  });

  it("keeps the application baseline when the global profile is malformed", async () => {
    const profile = await profileFixture();
    const get = vi.fn().mockResolvedValue({
      data: { ...profile, arbitrary_css: "* { display: none }" },
      response: new Response(null, { status: 200 }),
    });
    const reader = createPresentationProfileReader(
      { GET: get } as unknown as FinancialAcademyApiClient,
      readySession(),
    );

    await expect(reader(new AbortController().signal)).resolves.toBeNull();
  });

  it("sends one complete replacement and maps stale writes without exposing server text", async () => {
    const post = vi.fn().mockResolvedValue({
      error: { code: "stale_revision", message: "private detail" },
      response: new Response(null, { status: 409 }),
    });
    const action = createPresentationPreferencesAction(
      { POST: post } as unknown as FinancialAcademyApiClient,
      readySession(),
    );
    const form = new FormData();
    form.set("form_intent", "save");
    form.set("operation", "replace_preferences");
    form.set("idempotency_key", "11111111-1111-4111-8111-111111111111");
    form.set("expected_revision", "7");
    form.set("text_size", "larger");
    form.set("text_spacing", "increased");
    form.set("reading_width", "focused");
    form.set("motion", "reduce");

    const result = await action({
      request: new Request("http://example.test/preferences/display", {
        method: "POST",
        body: form,
      }),
      params: {},
    } as Parameters<typeof action>[0]);

    expect(result).toMatchObject({ status: "error", kind: "stale", intent: "save" });
    expect(JSON.stringify(result)).not.toContain("private detail");
    expect(post).toHaveBeenCalledWith(
      "/api/v1/learner-presentation-preferences/mutations",
      expect.objectContaining({
        body: {
          schema_version: "1.0.0",
          idempotency_key: "11111111-1111-4111-8111-111111111111",
          expected_revision: 7,
          mutation: {
            operation: "replace_preferences",
            text_size: "larger",
            text_spacing: "increased",
            reading_width: "focused",
            motion: "reduce",
          },
        },
      }),
    );
  });

  it("rejects partial or extra browser fields before calling the API", async () => {
    const post = vi.fn();
    const action = createPresentationPreferencesAction(
      { POST: post } as unknown as FinancialAcademyApiClient,
      readySession(),
    );
    const form = new FormData();
    form.set("form_intent", "save");
    form.set("operation", "replace_preferences");
    form.set("idempotency_key", "11111111-1111-4111-8111-111111111111");
    form.set("expected_revision", "7");
    form.set("text_size", "larger");
    form.set("text_spacing", "increased");
    form.set("reading_width", "focused");
    form.set("motion", "reduce");
    form.set("learner_id", "someone-else");

    await expect(action({
      request: new Request("http://example.test/preferences/display", {
        method: "POST",
        body: form,
      }),
      params: {},
    } as Parameters<typeof action>[0])).resolves.toEqual({
      status: "error",
      kind: "invalid",
      intent: "save",
    });
    expect(post).not.toHaveBeenCalled();
  });
});

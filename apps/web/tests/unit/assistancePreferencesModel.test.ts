import { describe, expect, it, vi } from "vitest";

import {
  createAssistancePreferencesAction,
  createAssistancePreferencesExporter,
  createAssistancePreferencesLoader,
} from "../../src/features/assistance-preferences/api";

import {
  assistancePreferenceExportIsSafe,
  assistancePreferenceHistoryIsSafe,
  assistancePreferenceProfileIsSafe,
  type AssistancePreferenceExport,
  type AssistancePreferenceHistory,
  type AssistancePreferenceProfile,
} from "../../src/features/assistance-preferences/model";
import type { FinancialAcademyApiClient } from "../../src/generated/api-client";
import type { SingleProfileSession } from "../../src/platform/auth/singleProfileSession";
import { LOCAL_REMINDER_STORAGE_KEY } from "../../src/platform/reminders/localReminderPreference";


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

async function profile(
  revision = 1,
  times: { created_at?: string; updated_at?: string } = {},
): Promise<AssistancePreferenceProfile> {
  const material = {
    schema_version: "1.0.0" as const,
    profile_id: "profile.assistance-1",
    learner_id: "11111111-1111-4111-8111-111111111111",
    revision,
    assistance_mode: revision === 1 ? "off" as const : "on_request" as const,
    created_at: times.created_at ?? "2026-10-17T20:00:00Z",
    updated_at: times.updated_at ?? "2026-10-17T20:10:00Z",
  };
  return { ...material, profile_digest: await digest(material) };
}

function history(
  current: AssistancePreferenceProfile,
  revisions: number[],
  occurredAt: string | string[] = "2026-10-17T20:05:00Z",
): AssistancePreferenceHistory {
  return {
    schema_version: "1.0.0",
    profile_id: current.profile_id,
    current_revision: current.revision,
    changes: revisions.map((revision, index) => ({
      schema_version: "1.0.0",
      revision,
      operation: "replace_preferences",
      object_kind: "profile",
      object_id: null,
      occurred_at: Array.isArray(occurredAt)
        ? occurredAt[index] ?? "2026-10-17T20:05:00Z"
        : occurredAt,
      resulting_profile_digest: revision === current.revision
        ? current.profile_digest
        : "a".repeat(64),
    })),
  };
}

function exported(
  current: AssistancePreferenceProfile,
  retained: AssistancePreferenceHistory,
): AssistancePreferenceExport {
  return {
    schema_version: "1.0.0",
    purpose: "A portable copy of the AI-help choice you selected.",
    limitations: ["This choice does not enable or call an AI service."],
    exported_at: "2026-10-17T21:00:00Z",
    profile: current,
    history: retained,
  };
}

function readySession() {
  return {
    ensure: vi.fn().mockResolvedValue({ status: "ready" }),
    invalidate: vi.fn(),
  } as unknown as SingleProfileSession;
}

function memoryStorage() {
  const values = new Map<string, string>();
  return {
    getItem: vi.fn((key: string) => values.get(key) ?? null),
    setItem: vi.fn((key: string, value: string) => values.set(key, value)),
    values,
  };
}

describe("AI-help preference browser model", () => {
  it("accepts a complete canonical export and verifies the profile digest", async () => {
    const current = await profile(2);
    const retained = history(current, [2]);

    await expect(assistancePreferenceProfileIsSafe(current)).resolves.toBe(true);
    expect(assistancePreferenceHistoryIsSafe(retained, current)).toBe(true);
    await expect(assistancePreferenceExportIsSafe(exported(current, retained))).resolves.toBe(true);
  });

  it("rejects unknown authority fields and digest changes", async () => {
    const current = await profile(1);
    const retained = history(current, []);

    await expect(assistancePreferenceExportIsSafe({
      ...exported(current, retained),
      provider: "not-allowed",
    })).resolves.toBe(false);
    await expect(assistancePreferenceProfileIsSafe({
      ...current,
      assistance_mode: "on_request",
    })).resolves.toBe(false);
  });

  it("requires the exact retained revision window", async () => {
    const revisionTwo = await profile(2);
    expect(assistancePreferenceHistoryIsSafe(history(revisionTwo, []), revisionTwo)).toBe(false);

    const revisionFour = await profile(4);
    expect(assistancePreferenceHistoryIsSafe(history(revisionFour, [2, 4]), revisionFour)).toBe(false);

    const revisionOne = await profile(1);
    expect(assistancePreferenceHistoryIsSafe(history(revisionOne, []), revisionOne)).toBe(true);
  });

  it("accepts both newest-one-hundred boundaries", async () => {
    const revision101 = await profile(101);
    const revision102 = await profile(102);
    expect(assistancePreferenceHistoryIsSafe(
      history(revision101, Array.from({ length: 100 }, (_, index) => index + 2)),
      revision101,
    )).toBe(true);
    expect(assistancePreferenceHistoryIsSafe(
      history(revision102, Array.from({ length: 100 }, (_, index) => index + 3)),
      revision102,
    )).toBe(true);
  });

  it("rejects impossible and noncanonical times", async () => {
    await expect(assistancePreferenceProfileIsSafe(await profile(1, {
      updated_at: "2026-02-30T20:00:00Z",
    }))).resolves.toBe(false);
    await expect(assistancePreferenceProfileIsSafe(await profile(1, {
      updated_at: "2026-10-17 20:00:00Z",
    }))).resolves.toBe(false);
  });

  it.each([
    "2026-10-17T20:10:00Z",
    "2026-10-17T20:10:00.1Z",
    "2026-10-17T20:10:00.12Z",
    "2026-10-17T20:10:00.123Z",
    "2026-10-17T20:10:00.1234Z",
    "2026-10-17T20:10:00.12345Z",
    "2026-10-17T20:10:00.123456Z",
  ])("accepts canonical API timestamp precision: %s", async (updated_at) => {
    const current = await profile(2, { updated_at });
    await expect(assistancePreferenceProfileIsSafe(current)).resolves.toBe(true);
  });

  it.each([
    "2026-10-17T20:10:00.1234567Z",
    "2026-10-17T20:10:00+00:00",
    "2026-10-17T20:10:00.123456",
    "2026-04-31T20:10:00.123456Z",
    "2026-10-17T20:10:60Z",
  ])("rejects noncanonical API timestamp text: %s", async (updated_at) => {
    await expect(assistancePreferenceProfileIsSafe(
      await profile(2, { updated_at }),
    )).resolves.toBe(false);
  });

  it("preserves microsecond precision for profile, history, and export chronology", async () => {
    const reversedProfile = await profile(2, {
      created_at: "2026-10-17T20:10:00.123999Z",
      updated_at: "2026-10-17T20:10:00.123000Z",
    });
    await expect(assistancePreferenceProfileIsSafe(reversedProfile)).resolves.toBe(false);

    const current = await profile(2, {
      created_at: "2026-10-17T20:00:00Z",
      updated_at: "2026-10-17T20:10:00.123456Z",
    });
    expect(assistancePreferenceHistoryIsSafe(
      history(current, [2], "2026-10-17T20:10:00.123457Z"),
      current,
    )).toBe(false);

    const revisionThree = await profile(3, {
      created_at: "2026-10-17T20:00:00Z",
      updated_at: "2026-10-17T20:10:00.123999Z",
    });
    expect(assistancePreferenceHistoryIsSafe(
      history(revisionThree, [2, 3], [
        "2026-10-17T20:10:00.123456Z",
        "2026-10-17T20:10:00.123455Z",
      ]),
      revisionThree,
    )).toBe(false);

    const retained = history(current, [2], "2026-10-17T20:10:00.123455Z");
    await expect(assistancePreferenceExportIsSafe({
      ...exported(current, retained),
      exported_at: "2026-10-17T20:10:00.123455Z",
    })).resolves.toBe(false);
  });
});

describe("AI-help and reminder adapters", () => {
  it("loads the protected export and local reminder choice independently", async () => {
    const storage = memoryStorage();
    const get = vi.fn().mockResolvedValue({
      error: { code: "service_unavailable", detail: "private" },
      response: new Response(null, { status: 503 }),
    });
    const loader = createAssistancePreferencesLoader(
      { GET: get } as unknown as FinancialAcademyApiClient,
      readySession(),
      storage,
      () => "2026-10-17T20:00:00Z",
    );

    const result = await loader({
      request: new Request("http://example.test/preferences/assistance"),
      params: {},
    } as Parameters<typeof loader>[0]);

    expect(result.server).toEqual({ status: "unavailable" });
    expect(result.local).toMatchObject({
      status: "absent",
      envelope: { reminder_mode: "off", revision: 1 },
    });
    expect(JSON.stringify(result)).not.toContain("private");
  });

  it("sends only the closed learner-owned mutation through the generated client", async () => {
    const returned = await profile(8);
    const post = vi.fn().mockResolvedValue({
      data: returned,
      response: new Response(null, { status: 200 }),
    });
    const action = createAssistancePreferencesAction(
      { POST: post } as unknown as FinancialAcademyApiClient,
      readySession(),
      memoryStorage(),
      () => "2026-10-17T20:10:00Z",
    );
    const form = new FormData();
    form.set("form_intent", "server-save");
    form.set("operation", "replace_preferences");
    form.set("idempotency_key", "11111111-1111-4111-8111-111111111111");
    form.set("expected_revision", "7");
    form.set("assistance_mode", "on_request");

    const result = await action({
      request: new Request("http://example.test/preferences/assistance", {
        method: "POST",
        body: form,
      }),
      params: {},
    } as Parameters<typeof action>[0]);

    expect(result).toBeInstanceOf(Response);
    expect(post).toHaveBeenCalledWith(
      "/api/v1/learner-assistance-preferences/mutations",
      expect.objectContaining({
        body: {
          schema_version: "1.0.0",
          idempotency_key: "11111111-1111-4111-8111-111111111111",
          expected_revision: 7,
          mutation: { operation: "replace_preferences", assistance_mode: "on_request" },
        },
      }),
    );
  });

  it("keeps local reminder changes out of the session and public API", async () => {
    const storage = memoryStorage();
    const session = readySession();
    const post = vi.fn();
    const action = createAssistancePreferencesAction(
      { POST: post } as unknown as FinancialAcademyApiClient,
      session,
      storage,
      () => "2026-10-17T20:00:00Z",
    );
    const form = new FormData();
    form.set("form_intent", "local-save");
    form.set("reminder_mode", "in_app_when_available");

    const result = await action({
      request: new Request("http://example.test/preferences/assistance", {
        method: "POST",
        body: form,
      }),
      params: {},
    } as Parameters<typeof action>[0]);

    expect(result).toBeInstanceOf(Response);
    expect(post).not.toHaveBeenCalled();
    expect(session.ensure).not.toHaveBeenCalled();
    const stored = JSON.parse(storage.values.get(LOCAL_REMINDER_STORAGE_KEY) ?? "null");
    expect(stored).toMatchObject({
      reminder_mode: "in_app_when_available",
      revision: 2,
    });
    expect(stored).not.toHaveProperty("learner_id");
  });

  it("rejects scope-expanding browser fields before using either authority", async () => {
    const storage = memoryStorage();
    const session = readySession();
    const post = vi.fn();
    const action = createAssistancePreferencesAction(
      { POST: post } as unknown as FinancialAcademyApiClient,
      session,
      storage,
      () => "2026-10-17T20:00:00Z",
    );
    const form = new FormData();
    form.set("form_intent", "server-save");
    form.set("operation", "replace_preferences");
    form.set("idempotency_key", "11111111-1111-4111-8111-111111111111");
    form.set("expected_revision", "7");
    form.set("assistance_mode", "on_request");
    form.set("provider", "not-authorized");

    await expect(action({
      request: new Request("http://example.test/preferences/assistance", {
        method: "POST",
        body: form,
      }),
      params: {},
    } as Parameters<typeof action>[0])).resolves.toEqual({
      status: "error",
      authority: "server",
      kind: "invalid",
      intent: "save",
    });
    expect(post).not.toHaveBeenCalled();
    expect(session.ensure).not.toHaveBeenCalled();
    expect(storage.setItem).not.toHaveBeenCalled();
  });

  it("retains the complete request for malformed success and unexpected server outcomes", async () => {
    const prepared = {
      schema_version: "1.0.0" as const,
      idempotency_key: "request.commit-uncertain",
      expected_revision: 7,
      mutation: { operation: "replace_preferences" as const, assistance_mode: "on_request" as const },
    };
    const cases = [
      {
        kind: "invalid-response",
        response: {
          data: { ...(await profile(8)), provider: "not-authorized" },
          response: new Response(null, { status: 200 }),
        },
      },
      {
        kind: "unexpected",
        response: {
          error: { code: "server_error", detail: "private" },
          response: new Response(null, { status: 500 }),
        },
      },
    ] as const;

    for (const testCase of cases) {
      const post = vi.fn().mockResolvedValue(testCase.response);
      const action = createAssistancePreferencesAction(
        { POST: post } as unknown as FinancialAcademyApiClient,
        readySession(),
        memoryStorage(),
        () => "2026-10-17T20:10:00Z",
      );
      const form = new FormData();
      form.set("form_intent", "server-save");
      form.set("operation", prepared.mutation.operation);
      form.set("idempotency_key", prepared.idempotency_key);
      form.set("expected_revision", String(prepared.expected_revision));
      form.set("assistance_mode", prepared.mutation.assistance_mode);

      const result = await action({
        request: new Request("http://example.test/preferences/assistance", {
          method: "POST",
          body: form,
        }),
        params: {},
      } as Parameters<typeof action>[0]);

      expect(result).toEqual({
        status: "error",
        authority: "server",
        kind: testCase.kind,
        intent: "save",
        preparedRequest: prepared,
      });
      expect(JSON.stringify(result)).not.toContain("private");
    }
  });

  it("refuses an export when the visible revision changed after rendering", async () => {
    const current = await profile(2);
    const value = exported(current, history(current, [2]));
    const get = vi.fn().mockResolvedValue({
      data: value,
      response: new Response(null, { status: 200 }),
    });
    const exporter = createAssistancePreferencesExporter(
      { GET: get } as unknown as FinancialAcademyApiClient,
      readySession(),
    );

    await expect(exporter(1, "a".repeat(64))).resolves.toEqual({ status: "changed" });
    await expect(exporter(2, current.profile_digest)).resolves.toMatchObject({
      status: "ready",
      fileName: "ai-help-preference.json",
    });
  });
});

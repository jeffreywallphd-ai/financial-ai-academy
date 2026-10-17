import { describe, expect, it, vi } from "vitest";

import {
  createLearnerPreferencesAction,
  createLearnerPreferencesLoader,
} from "../../src/features/learner-preferences/api";
import type { FinancialAcademyApiClient } from "../../src/generated/api-client";
import type { SingleProfileSession } from "../../src/platform/auth/singleProfileSession";
import {
  experienceLevelLabel,
  learnerPreferenceExportIsSafe,
  learnerPreferenceHistoryIsSafe,
  learnerPreferenceProfileIsSafe,
  moveIdentifier,
  preferenceChangeLabel,
  type LearnerPreferenceExport,
  type LearnerPreferenceHistory,
  type LearnerPreferenceProfile,
} from "../../src/features/learner-preferences/model";


export const preferenceProfileFixture: LearnerPreferenceProfile = {
  schema_version: "1.0.0",
  profile_id: "profile.local-learner",
  learner_id: "11111111-1111-4111-8111-111111111111",
  revision: 4,
  goals: [
    {
      goal_id: "goal.research-literacy",
      title: "Understand how financial evidence is tested",
      detail: "Practice checking assumptions, sources, and limitations.",
      archived: false,
      created_at: "2026-10-17T18:01:00Z",
      updated_at: "2026-10-17T18:01:00Z",
    },
  ],
  experience: [
    {
      experience_id: "experience.python",
      subject: "Python for data analysis",
      level: "some_experience",
      detail: "I have used notebooks for class exercises.",
      created_at: "2026-10-17T18:02:00Z",
      updated_at: "2026-10-17T18:02:00Z",
    },
  ],
  interests: [
    {
      interest_id: "interest.market-structure",
      label: "How markets match buyers and sellers",
      created_at: "2026-10-17T18:03:00Z",
      updated_at: "2026-10-17T18:03:00Z",
    },
  ],
  created_at: "2026-10-17T18:00:00Z",
  updated_at: "2026-10-17T18:03:00Z",
  profile_digest: "3bafc94452c22184dfab79023d6659c571aca1cab02d00f55f0624daadc7088e",
};

export const preferenceHistoryFixture: LearnerPreferenceHistory = {
  schema_version: "1.0.0",
  profile_id: preferenceProfileFixture.profile_id,
  current_revision: preferenceProfileFixture.revision,
  changes: [
    {
      schema_version: "1.0.0",
      revision: 2,
      operation: "create_goal",
      object_kind: "goal",
      object_id: "goal.research-literacy",
      occurred_at: "2026-10-17T18:01:00Z",
      resulting_profile_digest: "b".repeat(64),
    },
    {
      schema_version: "1.0.0",
      revision: 3,
      operation: "create_experience",
      object_kind: "experience",
      object_id: "experience.python",
      occurred_at: "2026-10-17T18:02:00Z",
      resulting_profile_digest: "c".repeat(64),
    },
    {
      schema_version: "1.0.0",
      revision: 4,
      operation: "create_interest",
      object_kind: "interest",
      object_id: "interest.market-structure",
      occurred_at: "2026-10-17T18:03:00Z",
      resulting_profile_digest: preferenceProfileFixture.profile_digest,
    },
  ],
};

export const preferenceExportFixture: LearnerPreferenceExport = {
  schema_version: "1.0.0",
  purpose: "A portable copy of the learning preferences you entered.",
  limitations: [
    "These statements are not competency evidence.",
    "They are not financial advice or a suitability assessment.",
  ],
  exported_at: "2026-10-17T18:05:00Z",
  profile: preferenceProfileFixture,
  history: preferenceHistoryFixture,
};

describe("learner preference browser model", () => {
  it("accepts fixed contract-valid profile, history, export, and empty vectors", async () => {
    expect(await learnerPreferenceProfileIsSafe(preferenceProfileFixture)).toBe(true);
    expect(learnerPreferenceHistoryIsSafe(preferenceHistoryFixture, preferenceProfileFixture)).toBe(true);
    expect(await learnerPreferenceExportIsSafe(preferenceExportFixture)).toBe(true);
    const empty: LearnerPreferenceProfile = {
      schema_version: "1.0.0",
      profile_id: "profile.local-learner",
      learner_id: "11111111-1111-4111-8111-111111111111",
      revision: 1,
      goals: [],
      experience: [],
      interests: [],
      created_at: "2026-10-17T18:00:00Z",
      updated_at: "2026-10-17T18:00:00Z",
      profile_digest: "d30eecfd7e88c2f219056d824362e61dc6447dc572816f06a91247d3b5e24bce",
    };
    expect(await learnerPreferenceProfileIsSafe(empty)).toBe(true);
  });

  it("fails closed on extra fields, duplicate IDs, digest mismatch, and entry time escape", async () => {
    expect(await learnerPreferenceProfileIsSafe({ ...preferenceProfileFixture, hidden_score: 0.8 })).toBe(false);
    expect(await learnerPreferenceProfileIsSafe({
      ...preferenceProfileFixture,
      interests: [{ ...preferenceProfileFixture.interests[0]!, interest_id: preferenceProfileFixture.goals[0]!.goal_id }],
    })).toBe(false);
    expect(await learnerPreferenceProfileIsSafe({
      ...preferenceProfileFixture,
      profile_digest: "a".repeat(64),
    })).toBe(false);
    expect(await learnerPreferenceProfileIsSafe({
      ...preferenceProfileFixture,
      goals: [{ ...preferenceProfileFixture.goals[0]!, updated_at: "2026-10-17T18:04:00Z" }],
    })).toBe(false);
  });

  it("fails closed on history chronology, latest-result mismatch, and early export time", async () => {
    expect(learnerPreferenceHistoryIsSafe({
      ...preferenceHistoryFixture,
      changes: preferenceHistoryFixture.changes.map((change, index) => ({
        ...change,
        occurred_at: index === 1 ? "2026-10-17T18:00:30Z" : change.occurred_at,
      })),
    })).toBe(false);
    expect(learnerPreferenceHistoryIsSafe({
      ...preferenceHistoryFixture,
      changes: preferenceHistoryFixture.changes.map((change, index) => index === 2
        ? { ...change, resulting_profile_digest: "d".repeat(64) }
        : change),
    }, preferenceProfileFixture)).toBe(false);
    expect(await learnerPreferenceExportIsSafe({
      ...preferenceExportFixture,
      exported_at: "2026-10-17T18:02:59Z",
    })).toBe(false);
  });

  it("moves any valid item without hard-coding fixture counts", () => {
    expect(moveIdentifier(["goal.one", "goal.two", "goal.three"], "goal.two", "up")).toEqual([
      "goal.two",
      "goal.one",
      "goal.three",
    ]);
    expect(moveIdentifier(["goal.one", "goal.two", "goal.three"], "goal.two", "down")).toEqual([
      "goal.one",
      "goal.three",
      "goal.two",
    ]);
    expect(moveIdentifier(["goal.one"], "goal.one", "up")).toBeUndefined();
  });

  it("presents contract enums in plain learner-facing language", () => {
    expect(experienceLevelLabel("some_experience")).toBe("Some experience");
    expect(preferenceChangeLabel("reset_profile")).toBe("Reset learning preferences");
    expect(preferenceChangeLabel("reorder_goals")).not.toContain("_");
  });
});

function sessionReady() {
  return {
    ensure: vi.fn().mockResolvedValue({ status: "ready" }),
    invalidate: vi.fn(),
  } as unknown as SingleProfileSession;
}

describe("learner preference generated-client adapter", () => {
  it("loads a correlated profile and history through the public client", async () => {
    const get = vi.fn()
      .mockResolvedValueOnce({ data: preferenceProfileFixture, response: new Response(null, { status: 200 }) })
      .mockResolvedValueOnce({ data: preferenceHistoryFixture, response: new Response(null, { status: 200 }) });
    const client = { GET: get } as unknown as FinancialAcademyApiClient;
    const loader = createLearnerPreferencesLoader(client, sessionReady());

    const result = await loader({
      request: new Request("http://example.test/preferences/learning"),
      params: {},
    } as Parameters<typeof loader>[0]);

    expect(result).toEqual({
      status: "ready",
      profile: preferenceProfileFixture,
      history: preferenceHistoryFixture,
    });
    expect(get.mock.calls.map((call) => call[0])).toEqual([
      "/api/v1/learner-preferences",
      "/api/v1/learner-preferences/history",
    ]);
  });

  it("rejects a public profile/history pair whose latest integrity result does not match", async () => {
    const mismatchedHistory = {
      ...preferenceHistoryFixture,
      changes: preferenceHistoryFixture.changes.map((change, index) => index === 2
        ? { ...change, resulting_profile_digest: "d".repeat(64) }
        : change),
    };
    const get = vi.fn()
      .mockResolvedValueOnce({ data: preferenceProfileFixture, response: new Response(null, { status: 200 }) })
      .mockResolvedValueOnce({ data: mismatchedHistory, response: new Response(null, { status: 200 }) });
    const loader = createLearnerPreferencesLoader(
      { GET: get } as unknown as FinancialAcademyApiClient,
      sessionReady(),
    );

    await expect(loader({
      request: new Request("http://example.test/preferences/learning"),
      params: {},
    } as Parameters<typeof loader>[0])).resolves.toEqual({ status: "invalid-response" });
  });

  it("sends exact server-authoritative mutation fields and maps stale writes", async () => {
    const post = vi.fn().mockResolvedValue({
      error: { code: "stale_revision", message: "not exposed" },
      response: new Response(null, { status: 409 }),
    });
    const client = { POST: post } as unknown as FinancialAcademyApiClient;
    const action = createLearnerPreferencesAction(client, sessionReady());
    const form = new FormData();
    form.set("form_intent", "create-goal");
    form.set("idempotency_key", "request.create-1");
    form.set("expected_revision", "4");
    form.set("operation", "create_goal");
    form.set("title", "Compare market scenarios");
    form.set("detail", "Use more than one possible outcome.");

    const result = await action({
      request: new Request("http://example.test/preferences/learning", { method: "POST", body: form }),
      params: {},
    } as Parameters<typeof action>[0]);

    expect(result).toMatchObject({ status: "error", kind: "stale", intent: "create-goal" });
    expect(post).toHaveBeenCalledWith("/api/v1/learner-preferences/mutations", expect.objectContaining({
      body: {
        schema_version: "1.0.0",
        idempotency_key: "request.create-1",
        expected_revision: 4,
        mutation: {
          operation: "create_goal",
          title: "Compare market scenarios",
          detail: "Use more than one possible outcome.",
        },
      },
    }));
  });

  it("requires explicit removal confirmation before sending the bounded mutation", async () => {
    const post = vi.fn().mockResolvedValue({
      error: { code: "stale_revision" },
      response: new Response(null, { status: 409 }),
    });
    const client = { POST: post } as unknown as FinancialAcademyApiClient;
    const action = createLearnerPreferencesAction(client, sessionReady());
    const form = new FormData();
    form.set("form_intent", "remove-goal-goal.research-literacy");
    form.set("idempotency_key", "request.remove-1");
    form.set("expected_revision", "4");
    form.set("operation", "remove_goal");
    form.set("entry_id", "goal.research-literacy");

    const withoutConfirmation = await action({
      request: new Request("http://example.test/preferences/learning", { method: "POST", body: form }),
      params: {},
    } as Parameters<typeof action>[0]);
    expect(withoutConfirmation).toEqual({
      status: "error",
      kind: "invalid",
      intent: "remove-goal-goal.research-literacy",
    });
    expect(post).not.toHaveBeenCalled();

    form.set("confirm_remove", "remove");
    await action({
      request: new Request("http://example.test/preferences/learning", { method: "POST", body: form }),
      params: {},
    } as Parameters<typeof action>[0]);
    expect(post).toHaveBeenCalledWith("/api/v1/learner-preferences/mutations", expect.objectContaining({
      body: expect.objectContaining({
        mutation: { operation: "remove_goal", entry_id: "goal.research-literacy" },
      }),
    }));
  });
});

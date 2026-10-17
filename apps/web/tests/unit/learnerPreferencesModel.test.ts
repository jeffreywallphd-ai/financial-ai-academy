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
  profile_id: "profile.learning-1",
  learner_id: "11111111-1111-4111-8111-111111111111",
  revision: 4,
  goals: [
    {
      goal_id: "goal.risk-1",
      title: "Explain risk and return without promising an outcome",
      detail: "Compare several possible outcomes, including loss. 📊",
      archived: false,
      created_at: "2026-10-17T14:00:00Z",
      updated_at: "2026-10-17T14:02:00Z",
    },
    {
      goal_id: "goal.cash-2",
      title: "Understand cash-flow choices",
      detail: null,
      archived: true,
      created_at: "2026-10-17T14:01:00Z",
      updated_at: "2026-10-17T14:03:00Z",
    },
  ],
  experience: [
    {
      experience_id: "experience.finance-1",
      subject: "Personal finance",
      level: "some_experience",
      detail: "I have built a monthly budget.",
      created_at: "2026-10-17T14:04:00Z",
      updated_at: "2026-10-17T14:04:00Z",
    },
  ],
  interests: [
    {
      interest_id: "interest.etf-1",
      label: "ETF research",
      created_at: "2026-10-17T14:05:00Z",
      updated_at: "2026-10-17T14:05:00Z",
    },
    {
      interest_id: "interest.behavior-2",
      label: "Behavioral finance",
      created_at: "2026-10-17T14:06:00Z",
      updated_at: "2026-10-17T14:06:00Z",
    },
  ],
  created_at: "2026-10-17T14:00:00Z",
  updated_at: "2026-10-17T14:06:00Z",
  profile_digest: "a".repeat(64),
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
      object_id: "goal.risk-1",
      occurred_at: "2026-10-17T14:00:00Z",
      resulting_profile_digest: "b".repeat(64),
    },
    {
      schema_version: "1.0.0",
      revision: 3,
      operation: "create_experience",
      object_kind: "experience",
      object_id: "experience.finance-1",
      occurred_at: "2026-10-17T14:04:00Z",
      resulting_profile_digest: "c".repeat(64),
    },
    {
      schema_version: "1.0.0",
      revision: 4,
      operation: "reorder_interests",
      object_kind: "profile",
      object_id: null,
      occurred_at: "2026-10-17T14:06:00Z",
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
  exported_at: "2026-10-17T14:07:00Z",
  profile: preferenceProfileFixture,
  history: preferenceHistoryFixture,
};

describe("learner preference browser model", () => {
  it("accepts varied contract-valid profile, history, and export shapes", () => {
    expect(learnerPreferenceProfileIsSafe(preferenceProfileFixture)).toBe(true);
    expect(learnerPreferenceHistoryIsSafe(preferenceHistoryFixture)).toBe(true);
    expect(learnerPreferenceExportIsSafe(preferenceExportFixture)).toBe(true);
    const empty = {
      ...preferenceProfileFixture,
      revision: 1,
      goals: [],
      experience: [],
      interests: [],
    };
    expect(learnerPreferenceProfileIsSafe(empty)).toBe(true);
  });

  it("fails closed on extra fields, duplicate IDs, malformed chronology, and mismatched exports", () => {
    expect(learnerPreferenceProfileIsSafe({ ...preferenceProfileFixture, hidden_score: 0.8 })).toBe(false);
    expect(learnerPreferenceProfileIsSafe({
      ...preferenceProfileFixture,
      interests: [{ ...preferenceProfileFixture.interests[0]!, interest_id: preferenceProfileFixture.goals[0]!.goal_id }],
    })).toBe(false);
    expect(learnerPreferenceProfileIsSafe({
      ...preferenceProfileFixture,
      goals: [{ ...preferenceProfileFixture.goals[0]!, updated_at: "2026-10-16T14:00:00Z" }],
    })).toBe(false);
    expect(learnerPreferenceHistoryIsSafe({
      ...preferenceHistoryFixture,
      changes: [...preferenceHistoryFixture.changes].reverse(),
    })).toBe(false);
    expect(learnerPreferenceExportIsSafe({
      ...preferenceExportFixture,
      history: { ...preferenceHistoryFixture, current_revision: 3 },
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
});

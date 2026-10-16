import { describe, expect, it, vi } from "vitest";

import {
  createCurriculumActivityLauncher,
  createCurriculumGraphLoader,
} from "../../src/features/curriculum-graph/api";
import {
  activityLaunchIsSafe,
  curriculumGraphIsSafe,
  curriculumGraphPresentation,
  lessonDestinationWithReturnContext,
  navigationStateIsSafe,
  parseCurriculumGraphSelection,
} from "../../src/features/curriculum-graph/model";
import type { ActivityLaunch } from "../../src/features/curriculum-graph/model";
import type { FinancialAcademyApiClient } from "../../src/generated/api-client";
import type { SingleProfileSession } from "../../src/platform/auth/singleProfileSession";
import {
  curriculumGraphFixture,
  navigationStateFixture,
} from "../component/curriculumGraphFixture";

const expected = {
  curriculumId: "investing-foundations",
  curriculumVersion: "1.0.0",
};

const activityLaunchFixture = {
  schema_version: "1.0.0",
  curriculum_id: "investing-foundations",
  curriculum_version: "1.0.0",
  graph_digest: "f".repeat(64),
  activity_id: "activity-risk-return-lesson",
  navigation_projection_digest: "2".repeat(64),
  evaluated_at: "2026-10-15T12:30:00Z",
  placement_id: "intro-risk-return-primary",
  package_id: "intro-risk-return",
  package_version: "1.0.0",
  package_digest: "a".repeat(64),
  destination: "/learn/placements/intro-risk-return-primary",
} satisfies ActivityLaunch;

describe("curriculum graph route model", () => {
  it("accepts exact identifiers and only one bounded current-activity query", () => {
    expect(
      parseCurriculumGraphSelection(
        expected.curriculumId,
        expected.curriculumVersion,
        "https://academy.test/learn/curricula/investing-foundations/versions/1.0.0",
      ),
    ).toEqual(expected);
    expect(
      parseCurriculumGraphSelection(
        expected.curriculumId,
        expected.curriculumVersion,
        "https://academy.test/learn/curricula/investing-foundations/versions/1.0.0?activity=activity-risk-return-lesson",
      ),
    ).toEqual({
      ...expected,
      selectedActivityId: "activity-risk-return-lesson",
    });
    expect(
      parseCurriculumGraphSelection(
        "Investing Foundations",
        expected.curriculumVersion,
        "https://academy.test/learn",
      ),
    ).toBeNull();
    expect(
      parseCurriculumGraphSelection(
        expected.curriculumId,
        "latest",
        "https://academy.test/learn",
      ),
    ).toBeNull();
    expect(
      parseCurriculumGraphSelection(
        expected.curriculumId,
        expected.curriculumVersion,
        "https://academy.test/learn?latest=true",
      ),
    ).toBeNull();
    expect(
      parseCurriculumGraphSelection(
        expected.curriculumId,
        expected.curriculumVersion,
        "https://academy.test/learn?activity=activity-a&activity=activity-b",
      ),
    ).toBeNull();
  });

  it("accepts flexible valid shapes, partial hints, shared memberships, and unbranched activities", () => {
    expect(curriculumGraphIsSafe(curriculumGraphFixture, expected)).toBe(true);

    const withoutHints = structuredClone(curriculumGraphFixture) as Record<
      string,
      unknown
    >;
    delete withoutHints.presentation_order;
    expect(curriculumGraphIsSafe(withoutHints, expected)).toBe(true);

    const noBranchesOrRelationships = {
      ...structuredClone(curriculumGraphFixture),
      presentation_order: null,
      branches: [],
      relationships: [],
    };
    expect(curriculumGraphIsSafe(noBranchesOrRelationships, expected)).toBe(
      true,
    );

    const reorderedAndExpanded = {
      ...structuredClone(curriculumGraphFixture),
      objectives: [...curriculumGraphFixture.objectives].reverse(),
      activities: [
        ...curriculumGraphFixture.activities.slice(2),
        ...curriculumGraphFixture.activities.slice(0, 2),
      ],
    };
    expect(curriculumGraphIsSafe(reorderedAndExpanded, expected)).toBe(true);
  });

  it("uses presentation hints as partial ordering rather than a required fixed layout", () => {
    const presentation = curriculumGraphPresentation(curriculumGraphFixture);
    expect(presentation.objectives.map((item) => item.objective_id)).toEqual([
      "objective-diversification",
      "objective-risk-return",
    ]);
    expect(presentation.activities.map((item) => item.activity_id)).toEqual([
      "activity-risk-return-lesson",
      "activity-risk-return-check",
      "activity-diversification-reading",
      "activity-diversification-check",
      "activity-terms-glossary",
    ]);
    expect(presentation.branches).toEqual(curriculumGraphFixture.branches);
  });

  it("fails the whole graph for extra fields, wrong identity, or broken references", () => {
    const extra = structuredClone(curriculumGraphFixture) as unknown as Record<
      string,
      unknown
    >;
    extra.provider_payload = { private: true };
    expect(curriculumGraphIsSafe(extra, expected)).toBe(false);

    expect(
      curriculumGraphIsSafe(curriculumGraphFixture, {
        curriculumId: "different-curriculum",
        curriculumVersion: "1.0.0",
      }),
    ).toBe(false);

    const dangling = structuredClone(curriculumGraphFixture) as unknown as {
      relationships: Array<Record<string, unknown>>;
    };
    const firstRelationship = dangling.relationships[0];
    if (!firstRelationship) throw new Error("Expected relationship fixture.");
    firstRelationship.target_id = "missing-competency";
    expect(curriculumGraphIsSafe(dangling, expected)).toBe(false);

    const wrongReferenceKind = structuredClone(
      curriculumGraphFixture,
    ) as unknown as { activities: Array<Record<string, unknown>> };
    const firstActivity = wrongReferenceKind.activities[0];
    if (!firstActivity) throw new Error("Expected activity fixture.");
    firstActivity.kind = "assessment";
    expect(curriculumGraphIsSafe(wrongReferenceKind, expected)).toBe(false);
  });

  it("rejects duplicate identities and presentation hints for unknown records", () => {
    const duplicate = structuredClone(curriculumGraphFixture) as unknown as {
      branches: Array<Record<string, unknown>>;
    };
    const secondBranch = duplicate.branches[1];
    if (!secondBranch) throw new Error("Expected branch fixture.");
    secondBranch.branch_id = "branch-core";
    expect(curriculumGraphIsSafe(duplicate, expected)).toBe(false);

    const invalidHint = {
      ...structuredClone(curriculumGraphFixture),
      presentation_order: { activity_ids: ["activity-not-in-graph"] },
    };
    expect(curriculumGraphIsSafe(invalidHint, expected)).toBe(false);
  });

  it("enforces global identities, unambiguous branch kinds, and assessment relationships", () => {
    const crossTypeCollision = structuredClone(
      curriculumGraphFixture,
    ) as unknown as {
      objectives: Array<Record<string, unknown>>;
      competencies: Array<Record<string, unknown>>;
    };
    const objective = crossTypeCollision.objectives[0];
    const competency = crossTypeCollision.competencies[0];
    if (!objective || !competency) throw new Error("Expected graph nodes.");
    competency.competency_id = objective.objective_id;
    expect(curriculumGraphIsSafe(crossTypeCollision, expected)).toBe(false);

    const mixedBranchKinds = structuredClone(
      curriculumGraphFixture,
    ) as unknown as { branches: Array<Record<string, unknown>> };
    const practiceBranch = mixedBranchKinds.branches[2];
    if (!practiceBranch) throw new Error("Expected shared branch fixture.");
    practiceBranch.kind = "required";
    expect(curriculumGraphIsSafe(mixedBranchKinds, expected)).toBe(false);

    const lessonAssesses = structuredClone(curriculumGraphFixture) as unknown as {
      relationships: Array<Record<string, unknown>>;
    };
    const lessonRelationship = lessonAssesses.relationships[2];
    if (!lessonRelationship) throw new Error("Expected lesson relationship.");
    lessonRelationship.kind = "activity_assesses_competency";
    expect(curriculumGraphIsSafe(lessonAssesses, expected)).toBe(false);
  });

  it("matches canonical Unicode code-point and multiline text bounds", () => {
    const flexibleText = structuredClone(curriculumGraphFixture) as unknown as {
      title: string;
      summary: string;
      objectives: Array<Record<string, unknown>>;
    };
    flexibleText.title = "😀".repeat(240);
    flexibleText.summary =
      "  A reviewed summary may preserve leading space,\nline breaks, and trailing space.  ";
    const objective = flexibleText.objectives[0];
    if (!objective) throw new Error("Expected objective fixture.");
    objective.description = "First reviewed line.\nSecond reviewed line.";
    expect(curriculumGraphIsSafe(flexibleText, expected)).toBe(true);

    flexibleText.title += "😀";
    expect(curriculumGraphIsSafe(flexibleText, expected)).toBe(false);
  });

  it("counts source-reference locator bounds in Unicode code points", () => {
    const flexibleSource = structuredClone(curriculumGraphFixture) as unknown as {
      source_references: string[];
    };
    flexibleSource.source_references[0] = `zz:${"😀".repeat(255)}`;
    expect(curriculumGraphIsSafe(flexibleSource, expected)).toBe(true);

    flexibleSource.source_references[0] = `zz:${"😀".repeat(256)}`;
    expect(curriculumGraphIsSafe(flexibleSource, expected)).toBe(false);
  });
});

describe("curriculum activity launch model", () => {
  it("accepts only the exact graph, projection, lesson resource, and destination", () => {
    expect(
      activityLaunchIsSafe(
        activityLaunchFixture,
        curriculumGraphFixture,
        navigationStateFixture,
        activityLaunchFixture.activity_id,
      ),
    ).toBe(true);
    expect(
      activityLaunchIsSafe(
        {
          ...activityLaunchFixture,
          navigation_projection_digest: "7".repeat(64),
          evaluated_at: "2026-10-16T12:45:00Z",
        },
        curriculumGraphFixture,
        navigationStateFixture,
        activityLaunchFixture.activity_id,
      ),
    ).toBe(true);
    expect(
      lessonDestinationWithReturnContext(activityLaunchFixture),
    ).toBe(
      "/learn/placements/intro-risk-return-primary?curriculum_id=investing-foundations&curriculum_version=1.0.0&activity_id=activity-risk-return-lesson",
    );

    for (const changed of [
      { graph_digest: "9".repeat(64) },
      { placement_id: "different-placement" },
      { destination: "https://attacker.invalid/lesson" },
    ]) {
      expect(
        activityLaunchIsSafe(
          { ...activityLaunchFixture, ...changed },
          curriculumGraphFixture,
          navigationStateFixture,
          activityLaunchFixture.activity_id,
        ),
      ).toBe(false);
    }
  });

  it("uses the generated launch operation, renews once, and fails stale responses closed", async () => {
    const get = vi
      .fn()
      .mockResolvedValueOnce({ response: new Response(null, { status: 401 }) })
      .mockResolvedValueOnce({
        data: activityLaunchFixture,
        response: new Response(null, { status: 200 }),
      });
    const ensure = vi.fn().mockResolvedValue({ status: "ready" });
    const invalidate = vi.fn();
    const launcher = createCurriculumActivityLauncher(
      { GET: get } as unknown as FinancialAcademyApiClient,
      { ensure, invalidate } as unknown as SingleProfileSession,
    );

    await expect(
      launcher(
        curriculumGraphFixture,
        navigationStateFixture,
        activityLaunchFixture.activity_id,
        new AbortController().signal,
      ),
    ).resolves.toEqual({
      status: "ready",
      activityId: activityLaunchFixture.activity_id,
      destination:
        "/learn/placements/intro-risk-return-primary?curriculum_id=investing-foundations&curriculum_version=1.0.0&activity_id=activity-risk-return-lesson",
    });
    expect(ensure).toHaveBeenCalledTimes(2);
    expect(invalidate).toHaveBeenCalledOnce();
    expect(get).toHaveBeenNthCalledWith(
      2,
      "/api/v1/adaptation/curricula/{curriculum_id}/versions/{curriculum_version}/activities/{activity_id}/launch",
      expect.objectContaining({
        params: {
          path: {
            activity_id: "activity-risk-return-lesson",
            curriculum_id: "investing-foundations",
            curriculum_version: "1.0.0",
          },
        },
      }),
    );

    get.mockResolvedValueOnce({
      data: { ...activityLaunchFixture, graph_digest: "0".repeat(64) },
      response: new Response(null, { status: 200 }),
    });
    await expect(
      launcher(
        curriculumGraphFixture,
        navigationStateFixture,
        activityLaunchFixture.activity_id,
        new AbortController().signal,
      ),
    ).resolves.toEqual({
      status: "invalid",
      activityId: activityLaunchFixture.activity_id,
    });
  });
});

describe("curriculum navigation state model", () => {
  it("accepts a complete flexible projection with multiple reasons and four references", () => {
    expect(
      navigationStateIsSafe(navigationStateFixture, curriculumGraphFixture),
    ).toBe(true);
    expect(navigationStateFixture.activity_states[2]?.reasons[0]?.references).toHaveLength(
      4,
    );
  });

  it("accepts variable graph order only when the state closure follows that exact order", () => {
    const graph = {
      ...structuredClone(curriculumGraphFixture),
      presentation_order: null,
      activities: [...curriculumGraphFixture.activities].reverse(),
      branches: [],
      relationships: [],
    };
    const navigationState = {
      ...structuredClone(navigationStateFixture),
      activity_states: [...navigationStateFixture.activity_states].reverse(),
    };
    expect(navigationStateIsSafe(navigationState, graph)).toBe(true);

    navigationState.activity_states.reverse();
    expect(navigationStateIsSafe(navigationState, graph)).toBe(false);
  });

  it("rejects identity, digest, activity closure, duplicate, and extra-field mismatches", () => {
    const wrongDigest = {
      ...structuredClone(navigationStateFixture),
      graph_digest: "9".repeat(64),
    };
    expect(navigationStateIsSafe(wrongDigest, curriculumGraphFixture)).toBe(
      false,
    );

    const duplicate = structuredClone(navigationStateFixture);
    duplicate.activity_states[1] = structuredClone(duplicate.activity_states[0]!);
    expect(navigationStateIsSafe(duplicate, curriculumGraphFixture)).toBe(false);

    const missing = structuredClone(navigationStateFixture);
    missing.activity_states.pop();
    expect(navigationStateIsSafe(missing, curriculumGraphFixture)).toBe(false);

    const extra = structuredClone(navigationStateFixture) as unknown as Record<
      string,
      unknown
    >;
    extra.browser_selected_policy = true;
    expect(navigationStateIsSafe(extra, curriculumGraphFixture)).toBe(false);
  });

  it("rejects malformed reason bounds, references, timestamps, and strict versions", () => {
    const malformed = structuredClone(navigationStateFixture) as unknown as {
      policy_version: string;
      evaluated_at: string;
      activity_states: Array<{
        reasons: Array<{ references: string[]; explanation: string }>;
      }>;
    };
    malformed.activity_states[0]!.reasons[0]!.references = [];
    expect(navigationStateIsSafe(malformed, curriculumGraphFixture)).toBe(false);

    malformed.activity_states[0]!.reasons[0]!.references = [
      "activity-risk-return-lesson",
    ];
    malformed.activity_states[0]!.reasons[0]!.explanation = "";
    expect(navigationStateIsSafe(malformed, curriculumGraphFixture)).toBe(false);

    malformed.activity_states[0]!.reasons[0]!.explanation = "Valid reason.";
    malformed.evaluated_at = "2026-02-31T12:30:00Z";
    expect(navigationStateIsSafe(malformed, curriculumGraphFixture)).toBe(false);

    malformed.evaluated_at = navigationStateFixture.evaluated_at;
    malformed.policy_version = "1.0.0-beta";
    expect(navigationStateIsSafe(malformed, curriculumGraphFixture)).toBe(false);
  });
});

describe("curriculum graph loader", () => {
  it("renews once after navigation authorization expires and rereads the complete exact pair", async () => {
    const get = vi
      .fn()
      .mockResolvedValueOnce({
        data: curriculumGraphFixture,
        response: new Response(null, { status: 200 }),
      })
      .mockResolvedValueOnce({
        response: new Response(null, { status: 401 }),
      })
      .mockResolvedValueOnce({
        data: curriculumGraphFixture,
        response: new Response(null, { status: 200 }),
      })
      .mockResolvedValueOnce({
        data: navigationStateFixture,
        response: new Response(null, { status: 200 }),
      });
    const ensure = vi.fn().mockResolvedValue({ status: "ready" });
    const invalidate = vi.fn();
    const loader = createCurriculumGraphLoader(
      { GET: get } as unknown as FinancialAcademyApiClient,
      { ensure, invalidate } as unknown as SingleProfileSession,
    );

    await expect(
      loader({
        params: expected,
        request: new Request(
          "https://academy.test/learn/curricula/investing-foundations/versions/1.0.0",
        ),
      } as never),
    ).resolves.toEqual({
      status: "ready",
      graph: curriculumGraphFixture,
      navigationState: navigationStateFixture,
    });
    expect(ensure).toHaveBeenCalledTimes(2);
    expect(invalidate).toHaveBeenCalledOnce();
    expect(get).toHaveBeenCalledTimes(4);
    expect(get).toHaveBeenNthCalledWith(
      4,
      "/api/v1/adaptation/curricula/{curriculum_id}/versions/{curriculum_version}/navigation-state",
      expect.objectContaining({
        params: {
          path: {
            curriculum_id: "investing-foundations",
            curriculum_version: "1.0.0",
          },
        },
      }),
    );
  });

  it("fails the complete page closed when navigation state is unavailable or mismatched", async () => {
    const get = vi
      .fn()
      .mockResolvedValueOnce({
        data: curriculumGraphFixture,
        response: new Response(null, { status: 200 }),
      })
      .mockResolvedValueOnce({
        response: new Response(null, { status: 503 }),
      });
    const loader = createCurriculumGraphLoader(
      { GET: get } as unknown as FinancialAcademyApiClient,
      {
        ensure: vi.fn().mockResolvedValue({ status: "ready" }),
        invalidate: vi.fn(),
      } as unknown as SingleProfileSession,
    );
    const request = () =>
      loader({
        params: expected,
        request: new Request(
          "https://academy.test/learn/curricula/investing-foundations/versions/1.0.0",
        ),
      } as never);
    await expect(request()).resolves.toEqual({ status: "unavailable" });

    get
      .mockResolvedValueOnce({
        data: curriculumGraphFixture,
        response: new Response(null, { status: 200 }),
      })
      .mockResolvedValueOnce({
        data: {
          ...navigationStateFixture,
          curriculum_id: "different-curriculum",
        },
        response: new Response(null, { status: 200 }),
      });
    await expect(request()).resolves.toEqual({ status: "invalid-response" });
  });

  it("retains current position only when the fresh graph contains the selected activity", async () => {
    const get = vi
      .fn()
      .mockResolvedValueOnce({
        data: curriculumGraphFixture,
        response: new Response(null, { status: 200 }),
      })
      .mockResolvedValueOnce({
        data: navigationStateFixture,
        response: new Response(null, { status: 200 }),
      })
      .mockResolvedValueOnce({
        data: curriculumGraphFixture,
        response: new Response(null, { status: 200 }),
      })
      .mockResolvedValueOnce({
        data: navigationStateFixture,
        response: new Response(null, { status: 200 }),
      });
    const loader = createCurriculumGraphLoader(
      { GET: get } as unknown as FinancialAcademyApiClient,
      {
        ensure: vi.fn().mockResolvedValue({ status: "ready" }),
        invalidate: vi.fn(),
      } as unknown as SingleProfileSession,
    );
    const request = (activityId: string) =>
      loader({
        params: expected,
        request: new Request(
          `https://academy.test/learn/curricula/investing-foundations/versions/1.0.0?activity=${activityId}`,
        ),
      } as never);

    await expect(request("activity-risk-return-lesson")).resolves.toEqual({
      status: "ready",
      graph: curriculumGraphFixture,
      navigationState: navigationStateFixture,
      currentActivityId: "activity-risk-return-lesson",
    });
    await expect(request("activity-not-in-this-graph")).resolves.toEqual({
      status: "ready",
      graph: curriculumGraphFixture,
      navigationState: navigationStateFixture,
    });
  });

  it("rejects a malformed selection and session denial before graph transport", async () => {
    const get = vi.fn();
    const ensure = vi.fn().mockResolvedValue({
      status: "error",
      kind: "forbidden",
    });
    const loader = createCurriculumGraphLoader(
      { GET: get } as unknown as FinancialAcademyApiClient,
      { ensure, invalidate: vi.fn() } as unknown as SingleProfileSession,
    );
    await expect(
      loader({
        params: expected,
        request: new Request(
          "https://academy.test/learn/curricula/investing-foundations/versions/1.0.0?latest=true",
        ),
      } as never),
    ).resolves.toEqual({ status: "invalid-selection" });
    expect(ensure).not.toHaveBeenCalled();

    await expect(
      loader({
        params: expected,
        request: new Request(
          "https://academy.test/learn/curricula/investing-foundations/versions/1.0.0",
        ),
      } as never),
    ).resolves.toEqual({ status: "forbidden" });
    expect(get).not.toHaveBeenCalled();
  });
});

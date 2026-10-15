import { describe, expect, it, vi } from "vitest";

import { createCurriculumGraphLoader } from "../../src/features/curriculum-graph/api";
import {
  curriculumGraphIsSafe,
  curriculumGraphPresentation,
  parseCurriculumGraphSelection,
} from "../../src/features/curriculum-graph/model";
import type { FinancialAcademyApiClient } from "../../src/generated/api-client";
import type { SingleProfileSession } from "../../src/platform/auth/singleProfileSession";
import { curriculumGraphFixture } from "../component/curriculumGraphFixture";

const expected = {
  curriculumId: "investing-foundations",
  curriculumVersion: "1.0.0",
};

describe("curriculum graph route model", () => {
  it("accepts exact safe route identifiers without query or fragment state", () => {
    expect(
      parseCurriculumGraphSelection(
        expected.curriculumId,
        expected.curriculumVersion,
        "https://academy.test/learn/curricula/investing-foundations/versions/1.0.0",
      ),
    ).toEqual(expected);
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

describe("curriculum graph loader", () => {
  it("renews once after an unauthorized response and reads the exact version", async () => {
    const get = vi
      .fn()
      .mockResolvedValueOnce({
        response: new Response(null, { status: 401 }),
      })
      .mockResolvedValueOnce({
        data: curriculumGraphFixture,
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
    ).resolves.toEqual({ status: "ready", graph: curriculumGraphFixture });
    expect(ensure).toHaveBeenCalledTimes(2);
    expect(invalidate).toHaveBeenCalledOnce();
    expect(get).toHaveBeenCalledTimes(2);
    expect(get).toHaveBeenLastCalledWith(
      "/api/v1/curriculum/graphs/{curriculum_id}/versions/{curriculum_version}",
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

import { describe, expect, it } from "vitest";

import {
  canonicalDecimalPattern,
  practiceSubmissionResultIsSafe,
  preparePracticeSubmission,
  practicePresentationIsSafe,
} from "../../src/features/practice-activity/model";
import {
  practiceFixture,
  practiceResultFixture,
} from "../component/practiceFixture";


function fixture(): Record<string, unknown> {
  return structuredClone(practiceFixture) as unknown as Record<string, unknown>;
}

function matchesCanonicalDecimal(
  value: string,
  scale: number,
  allowNegative: boolean,
): boolean {
  return new RegExp(
    `^(?:${canonicalDecimalPattern(scale, allowNegative)})$`,
    "u",
  ).test(value);
}

function completeFormData() {
  const form = new FormData();
  form.append("risk-meaning", "uncertainty");
  form.append("risk-factors", "time");
  form.append("risk-factors", "market");
  form.append("risk-factors", "fees");
  form.append("simple-return", "5.00");
  return form;
}

describe("practice presentation validation", () => {
  it("accepts the closed public response and correlates the placement", () => {
    expect(
      practicePresentationIsSafe(
        practiceFixture,
        practiceFixture.placement_id,
      ),
    ).toBe(true);
    expect(practicePresentationIsSafe(practiceFixture, "other-placement")).toBe(
      false,
    );
  });

  it("accepts flexible valid counts and preserves non-fixture order", () => {
    const value = fixture();
    const items = value.items as unknown[];
    value.items = [items[2], items[0]];
    value.source_references = [
      ...(value.source_references as unknown[]),
      {
        resource_id: "second-reading",
        resource_version: "2.1.0",
        resource_digest: "e".repeat(64),
        title: "Another reviewed reading",
      },
    ];
    expect(practicePresentationIsSafe(value)).toBe(true);
  });

  it.each([
    ["private answer", (value: Record<string, unknown>) => {
      const item = (value.items as Record<string, unknown>[])[0]!;
      item.correct_option_id = "uncertainty";
    }],
    ["unknown item", (value: Record<string, unknown>) => {
      const item = (value.items as Record<string, unknown>[])[0]!;
      item.item_type = "free_text";
    }],
    ["duplicate item", (value: Record<string, unknown>) => {
      const items = value.items as Record<string, unknown>[];
      items.push(structuredClone(items[0]!));
    }],
    ["duplicate choice", (value: Record<string, unknown>) => {
      const item = (value.items as Record<string, unknown>[])[0]!;
      const options = item.options as Record<string, unknown>[];
      options.push(structuredClone(options[0]!));
    }],
    ["invalid decimal scale", (value: Record<string, unknown>) => {
      const item = (value.items as Record<string, unknown>[])[2]!;
      item.scale = 7;
    }],
    ["extra root field", (value: Record<string, unknown>) => {
      value.learner_id = "private-learner";
    }],
  ])("rejects %s without partial interpretation", (_name, mutate) => {
    const value = fixture();
    mutate(value);
    expect(practicePresentationIsSafe(value)).toBe(false);
  });

  it.each([
    ["0", true],
    ["7", true],
    ["-7", true],
    ["00", false],
    ["01", false],
    ["-0", false],
    ["-01", false],
  ])("applies canonical whole-number input validity to %s", (value, valid) => {
    expect(matchesCanonicalDecimal(value, 0, true)).toBe(valid);
  });

  it.each([
    ["0.00", true],
    ["1.00", true],
    ["-0.01", true],
    ["-1.00", true],
    ["00.00", false],
    ["01.00", false],
    ["-0.00", false],
    ["1.0", false],
    ["1", false],
    ["1e2", false],
    ["1,00", false],
  ])("applies canonical fixed-decimal input validity to %s", (value, valid) => {
    expect(matchesCanonicalDecimal(value, 2, true)).toBe(valid);
  });

  it("rejects negative values when the public item contract disallows them", () => {
    expect(matchesCanonicalDecimal("0.00", 2, false)).toBe(true);
    expect(matchesCanonicalDecimal("1.00", 2, false)).toBe(true);
    expect(matchesCanonicalDecimal("-0.01", 2, false)).toBe(false);
    expect(matchesCanonicalDecimal("-1.00", 2, false)).toBe(false);
  });

  it("builds the exact generated submission without learner or scoring authority", () => {
    const prepared = preparePracticeSubmission(
      practiceFixture,
      completeFormData(),
      practiceResultFixture.submission_id,
    );
    expect(prepared.status).toBe("ready");
    if (prepared.status !== "ready") {
      return;
    }
    expect(prepared.submission.body.responses).toHaveLength(3);
    expect(prepared.submission.body.responses[1]).toEqual(
      expect.objectContaining({
        item_type: "multiple_select",
        selected_option_ids: ["time", "market", "fees"],
      }),
    );
    expect("learner_id" in prepared.submission.body).toBe(false);
    expect("score" in prepared.submission.body).toBe(false);
  });

  it.each([
    ["missing response", (form: FormData) => form.delete("risk-factors")],
    ["unknown option", (form: FormData) => form.set("risk-meaning", "private-answer")],
    ["duplicate option", (form: FormData) => form.append("risk-factors", "time")],
    ["noncanonical decimal", (form: FormData) => form.set("simple-return", "05.0")],
  ])("rejects %s before submission", (_name, mutate) => {
    const form = completeFormData();
    mutate(form);
    expect(
      preparePracticeSubmission(
        practiceFixture,
        form,
        practiceResultFixture.submission_id,
      ).status,
    ).toBe("invalid");
  });

  it("accepts a complete correlated result and order-independent multiple selection", () => {
    const prepared = preparePracticeSubmission(
      practiceFixture,
      completeFormData(),
      practiceResultFixture.submission_id,
    );
    expect(prepared.status).toBe("ready");
    if (prepared.status !== "ready") {
      return;
    }
    const result = structuredClone(practiceResultFixture);
    const multiple = result.item_results[1];
    expect(multiple?.item_type).toBe("multiple_select");
    if (!multiple || multiple.item_type !== "multiple_select") {
      return;
    }
    multiple.selected_option_ids = ["fees", "time", "market"];
    expect(
      practiceSubmissionResultIsSafe(
        result,
        practiceFixture,
        prepared.submission,
      ),
    ).toBe(true);
  });

  it.each([
    "2026-02-31T12:00:00Z",
    "2026-10-16T12:00:00+01:00",
    "2026-10-16T12:00:00.1234567Z",
  ])("rejects noncanonical result time %s", (submittedAt) => {
    const prepared = preparePracticeSubmission(
      practiceFixture,
      completeFormData(),
      practiceResultFixture.submission_id,
    );
    expect(prepared.status).toBe("ready");
    if (prepared.status !== "ready") {
      return;
    }
    const result = structuredClone(practiceResultFixture);
    result.submitted_at = submittedAt;
    expect(
      practiceSubmissionResultIsSafe(
        result,
        practiceFixture,
        prepared.submission,
      ),
    ).toBe(false);
  });

  it.each([
    "2026-10-16T12:00:00Z",
    "2024-02-29T23:59:59.123456Z",
  ])("accepts canonical UTC result time %s", (submittedAt) => {
    const prepared = preparePracticeSubmission(
      practiceFixture,
      completeFormData(),
      practiceResultFixture.submission_id,
    );
    expect(prepared.status).toBe("ready");
    if (prepared.status !== "ready") {
      return;
    }
    const result = structuredClone(practiceResultFixture);
    result.submitted_at = submittedAt;
    expect(
      practiceSubmissionResultIsSafe(
        result,
        practiceFixture,
        prepared.submission,
      ),
    ).toBe(true);
  });

  it("accepts a valid one-question activity without fixture-count assumptions", () => {
    const practice = structuredClone(practiceFixture);
    practice.items = [practice.items[0]!];
    const form = new FormData();
    form.append("risk-meaning", "uncertainty");
    const prepared = preparePracticeSubmission(
      practice,
      form,
      practiceResultFixture.submission_id,
    );
    expect(prepared.status).toBe("ready");
    if (prepared.status !== "ready") {
      return;
    }
    const result = {
      ...structuredClone(practiceResultFixture),
      score: 1,
      max_score: 1,
      outcome: "all_correct" as const,
      item_results: [structuredClone(practiceResultFixture.item_results[0]!)],
    };
    expect(
      practiceSubmissionResultIsSafe(result, practice, prepared.submission),
    ).toBe(true);
  });

  it.each([
    ["private result field", (result: Record<string, unknown>) => {
      result.learner_id = "private-learner";
    }],
    ["mismatched definition", (result: Record<string, unknown>) => {
      result.definition_digest = "f".repeat(64);
    }],
    ["mismatched submitted response", (result: Record<string, unknown>) => {
      const items = result.item_results as Record<string, unknown>[];
      items[0]!.selected_option_id = "guarantee";
    }],
    ["duplicate result item", (result: Record<string, unknown>) => {
      const items = result.item_results as Record<string, unknown>[];
      items[1] = structuredClone(items[0]!);
    }],
    ["unavailable review reference", (result: Record<string, unknown>) => {
      result.review_reference_ids = ["private-review"];
    }],
    ["inconsistent total", (result: Record<string, unknown>) => {
      result.score = 3;
      result.outcome = "all_correct";
    }],
  ])("rejects %s without partial interpretation", (_name, mutate) => {
    const prepared = preparePracticeSubmission(
      practiceFixture,
      completeFormData(),
      practiceResultFixture.submission_id,
    );
    expect(prepared.status).toBe("ready");
    if (prepared.status !== "ready") {
      return;
    }
    const result = structuredClone(practiceResultFixture) as unknown as Record<string, unknown>;
    mutate(result);
    expect(
      practiceSubmissionResultIsSafe(
        result,
        practiceFixture,
        prepared.submission,
      ),
    ).toBe(false);
  });
});

import { describe, expect, it } from "vitest";

import { practicePresentationIsSafe } from "../../src/features/practice-activity/model";
import { practiceFixture } from "../component/practiceFixture";


function fixture(): Record<string, unknown> {
  return structuredClone(practiceFixture) as unknown as Record<string, unknown>;
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
});

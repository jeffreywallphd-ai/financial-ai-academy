import { describe, expect, it } from "vitest";

import type { Lesson } from "../../src/features/lesson-reading/model";
import { lessonContentIsSafe } from "../../src/features/lesson-reading/model";
import { lessonFixture } from "../component/lessonFixture";


function copyLesson(): Lesson {
  return structuredClone(lessonFixture);
}

describe("lessonContentIsSafe", () => {
  it("accepts the complete closed node and provenance fixture", () => {
    expect(lessonContentIsSafe(copyLesson())).toBe(true);
  });

  it("rejects an unknown node instead of partially rendering", () => {
    const lesson = copyLesson();
    (lesson.body as unknown[]).push({
      kind: "embedded_video",
      source: "https://attacker.invalid/video",
    });

    expect(lessonContentIsSafe(lesson)).toBe(false);
  });

  it("rejects non-HTTPS source and inline link locators", () => {
    const sourceLesson = copyLesson();
    (
      sourceLesson.sources[0] as { locator: string }
    ).locator = "http://example.test/source";
    expect(lessonContentIsSafe(sourceLesson)).toBe(false);

    const linkLesson = copyLesson();
    const paragraph = linkLesson.body[1] as {
      children: Array<{ kind?: string; href?: string }>;
    };
    const link = paragraph.children.find(
      (node) => node.kind === "source_link",
    );
    if (!link) {
      throw new Error("Test fixture source link is missing.");
    }
    link.href = "javascript:alert(1)";
    expect(lessonContentIsSafe(linkLesson)).toBe(false);
  });

  it("rejects undeclared assets and non-application locators", () => {
    const undeclared: Lesson = {
      ...copyLesson(),
      assets: [],
    };
    expect(lessonContentIsSafe(undeclared)).toBe(false);

    const locator = copyLesson();
    (
      locator.assets[0] as { locator: string }
    ).locator = "https://example.test/image.png";
    expect(lessonContentIsSafe(locator)).toBe(false);
  });
});

import { describe, expect, it, vi } from "vitest";

import { createLessonLoader } from "../../src/features/lesson-reading/api";
import type { Lesson } from "../../src/features/lesson-reading/model";
import {
  curriculumReturnDestination,
  lessonContentIsSafe,
  parseLessonReturnContext,
} from "../../src/features/lesson-reading/model";
import { lessonFixture } from "../component/lessonFixture";
import type { FinancialAcademyApiClient } from "../../src/generated/api-client";
import type { SingleProfileSession } from "../../src/platform/auth/singleProfileSession";


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

describe("lesson return context", () => {
  it("accepts only the complete exact identifier set and derives a local graph path", () => {
    const context = parseLessonReturnContext(
      "https://academy.test/learn/placements/intro-risk-return-primary?curriculum_id=investing-foundations&curriculum_version=1.0.0&activity_id=activity-risk-return-lesson",
    );
    expect(context).toEqual({
      curriculumId: "investing-foundations",
      curriculumVersion: "1.0.0",
      activityId: "activity-risk-return-lesson",
    });
    expect(context && curriculumReturnDestination(context)).toBe(
      "/learn/curricula/investing-foundations/versions/1.0.0?activity=activity-risk-return-lesson",
    );
  });

  it.each([
    "https://academy.test/learn/placements/example",
    "https://academy.test/learn/placements/example?curriculum_id=investing-foundations&curriculum_version=1.0.0",
    "https://academy.test/learn/placements/example?curriculum_id=investing-foundations&curriculum_version=latest&activity_id=activity-risk-return-lesson",
    "https://academy.test/learn/placements/example?curriculum_id=investing-foundations&curriculum_version=1.0.0&activity_id=activity-risk-return-lesson&return_to=https://attacker.invalid",
    "https://academy.test/learn/placements/example?curriculum_id=investing-foundations&curriculum_id=other&curriculum_version=1.0.0&activity_id=activity-risk-return-lesson",
  ])("ignores incomplete, extra, duplicate, or malformed context: %s", (url) => {
    expect(parseLessonReturnContext(url)).toBeNull();
  });

  it("carries valid context through the protected lesson loader without making it request authority", async () => {
    const get = vi.fn().mockResolvedValue({
      data: lessonFixture,
      response: new Response(null, { status: 200 }),
    });
    const loader = createLessonLoader(
      { GET: get } as unknown as FinancialAcademyApiClient,
      {
        ensure: vi.fn().mockResolvedValue({ status: "ready" }),
        invalidate: vi.fn(),
      } as unknown as SingleProfileSession,
    );

    await expect(
      loader({
        params: { placementId: "intro-risk-return-primary" },
        request: new Request(
          "https://academy.test/learn/placements/intro-risk-return-primary?curriculum_id=investing-foundations&curriculum_version=1.0.0&activity_id=activity-risk-return-lesson",
        ),
      } as never),
    ).resolves.toEqual({
      status: "ready",
      lesson: lessonFixture,
      returnContext: {
        curriculumId: "investing-foundations",
        curriculumVersion: "1.0.0",
        activityId: "activity-risk-return-lesson",
      },
    });
    expect(get).toHaveBeenCalledWith(
      "/api/v1/curriculum/placements/{placement_id}/lesson",
      expect.objectContaining({
        params: { path: { placement_id: "intro-risk-return-primary" } },
      }),
    );
  });
});

import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router";
import { describe, expect, it, vi } from "vitest";

import { LessonReadingPage } from "../../src/features/lesson-reading/LessonReadingPage";
import { LessonRouteView } from "../../src/features/lesson-reading/LessonRoute";
import type { FeatureGuidanceReader } from "../../src/features/platform-help/model";
import { lessonFixture } from "./lessonFixture";
import { contextualHelpFixture } from "./platformHelpFixture";


describe("LessonReadingPage", () => {
  it("renders the complete lesson with publication details and an accessible technical record", async () => {
    const user = userEvent.setup();
    render(<MemoryRouter><LessonReadingPage lesson={lessonFixture} /></MemoryRouter>);

    expect(
      screen.getByRole("heading", {
        level: 1,
        name: lessonFixture.title,
      }),
    ).toBeVisible();
    const objectives = screen.getByRole("region", {
      name: "Learning objectives",
    });
    expect(within(objectives).getAllByRole("listitem")).toHaveLength(2);
    expect(
      screen.getByRole("heading", { name: "Educational sources" }),
    ).toBeVisible();
    expect(
      screen.getByRole("heading", { name: "Publication details" }),
    ).toBeVisible();
    expect(screen.getByText(lessonFixture.provenance.published_by)).toBeVisible();
    const technicalRecord = screen.getByText("Technical record");
    const details = technicalRecord.closest("details");
    expect(details).not.toHaveAttribute("open");
    await user.click(technicalRecord);
    expect(details).toHaveAttribute("open");
    expect(screen.getByText(lessonFixture.package_id)).toBeVisible();
    expect(screen.getByText(lessonFixture.package_version)).toBeVisible();
    expect(screen.getByText(lessonFixture.package_digest)).toBeVisible();
    expect(
      screen.getByAltText("A labeled spectrum of investment risk."),
    ).toHaveAttribute(
      "src",
      "/api/v1/content/assets/risk-spectrum",
    );
    expect(screen.getByRole("link", { name: "Save to Saved learning" })).toHaveAttribute(
      "href",
      `/saved-learning/new?kind=lesson&placement=${lessonFixture.placement_id}&return=%2Flearn%2Fplacements%2F${lessonFixture.placement_id}`,
    );
  });

  it("marks external reviewed sources and prevents opener access", () => {
    render(<MemoryRouter><LessonReadingPage lesson={lessonFixture} /></MemoryRouter>);

    const source = screen.getByRole("link", {
      name: /Introduction to investing.*opens in a new tab/i,
    });
    expect(source).toHaveAttribute(
      "href",
      "https://www.investor.gov/introduction-investing",
    );
    expect(source).toHaveAttribute("target", "_blank");
    expect(source).toHaveAttribute("rel", "noopener noreferrer");
  });

  it("shows a bounded same-origin return action only when context is valid", () => {
    render(
      <MemoryRouter>
        <LessonReadingPage
          lesson={lessonFixture}
          returnTo="/learn/curricula/investing-foundations/versions/1.0.0?activity=activity-risk-return-lesson"
        />
      </MemoryRouter>,
    );

    expect(
      screen.getByRole("link", { name: "Return to learning path" }),
    ).toHaveAttribute(
      "href",
      "/learn/curricula/investing-foundations/versions/1.0.0?activity=activity-risk-return-lesson",
    );
  });

  it("shows server-owned contextual questions beside publication details", async () => {
    render(
      <MemoryRouter
        initialEntries={[`/learn/placements/${lessonFixture.placement_id}`]}
      >
        <LessonReadingPage
          lesson={lessonFixture}
          readContextualHelp={vi.fn().mockResolvedValue({
            status: "ready",
            context: contextualHelpFixture,
          })}
        />
      </MemoryRouter>,
    );

    expect(
      await screen.findByRole("heading", {
        name: "Questions about Lesson publication details",
      }),
    ).toBeVisible();
    expect(
      screen.getByRole("link", {
        name: "How to use source and history details",
      }),
    ).toHaveAttribute(
      "href",
      `/help/topics/source-and-history/versions/1.0.0?return_to=%2Flearn%2Fplacements%2F${lessonFixture.placement_id}`,
    );
  });
});

describe("LessonRouteView", () => {
  it.each([
    ["unauthorized", "We couldn't start your learner session"],
    ["forbidden", "You don't have access to this lesson"],
    ["not-found", "Lesson not found"],
    ["unavailable", "Lesson temporarily unavailable"],
    ["invalid-content", "We couldn't show this lesson safely"],
    ["unexpected", "We couldn't open this lesson"],
  ] as const)("renders bounded %s state", (status, heading) => {
    render(
      <LessonRouteView
        onRetry={() => undefined}
        state={{ status }}
      />,
    );

    expect(
      screen.getByRole("heading", { level: 1, name: heading }),
    ).toBeVisible();
    expect(screen.queryByText(lessonFixture.title)).not.toBeInTheDocument();
    expect(document.body.textContent).not.toContain(
      lessonFixture.package_digest,
    );
    expect(document.body.textContent).not.toMatch(
      /private learner session|exact lesson|safe reading checks|package digest|validator/i,
    );
  });

  it.each(["unauthorized", "unavailable", "unexpected"] as const)(
    "keeps the existing retry action for %s",
    async (status) => {
      const user = userEvent.setup();
      let retryCount = 0;
      render(
        <LessonRouteView
          onRetry={() => {
            retryCount += 1;
          }}
          state={{ status }}
        />,
      );

      await user.click(screen.getByRole("button", { name: "Try again" }));
      expect(retryCount).toBe(1);
    },
  );

  it("shows exact-version guidance without substituting the missing lesson", async () => {
    const readFeatureGuidance = vi.fn<FeatureGuidanceReader>(async () => ({
      status: "ready",
      resolution: {
        mapping: {},
        guidance: {
          heading: "This lesson version is unavailable",
          reason: "The requested version could not be opened.",
          outcome: "No different or newer lesson was substituted.",
          actions: [],
        },
      } as never,
    }));
    render(
      <MemoryRouter initialEntries={["/learn/placements/lesson-one"]}>
        <LessonRouteView
          onRetry={() => undefined}
          readFeatureGuidance={readFeatureGuidance}
          state={{ status: "not-found" }}
        />
      </MemoryRouter>,
    );

    expect(screen.getByRole("heading", { name: "Lesson not found" })).toBeVisible();
    expect(
      await screen.findByRole("heading", {
        name: "This lesson version is unavailable",
      }),
    ).toBeVisible();
    expect(readFeatureGuidance).toHaveBeenCalledWith(
      "lesson-reading",
      "exact-version-unavailable",
      "1.0.0",
      expect.any(AbortSignal),
    );
  });

  it("describes loading in learner terms", () => {
    render(
      <LessonRouteView
        onRetry={() => undefined}
        state={{ status: "loading" }}
      />,
    );

    expect(
      screen.getByRole("heading", { name: "Opening your lesson" }),
    ).toBeVisible();
    expect(screen.getByRole("status")).toHaveTextContent(
      /starting your learner session/i,
    );
    expect(screen.getByRole("status")).not.toHaveTextContent(
      /private|exact|package|validator/i,
    );
  });
});

import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { LessonReadingPage } from "../../src/features/lesson-reading/LessonReadingPage";
import { LessonRouteView } from "../../src/features/lesson-reading/LessonRoute";
import { lessonFixture } from "./lessonFixture";


describe("LessonReadingPage", () => {
  it("renders the complete approved hierarchy and provenance", () => {
    render(<LessonReadingPage lesson={lessonFixture} />);

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
      screen.getByText(lessonFixture.package_version),
    ).toBeVisible();
    expect(
      screen.getByText(lessonFixture.package_digest),
    ).toBeVisible();
    expect(
      screen.getByAltText("A labeled spectrum of investment risk."),
    ).toHaveAttribute(
      "src",
      "/api/v1/content/assets/risk-spectrum",
    );
  });

  it("marks external reviewed sources and prevents opener access", () => {
    render(<LessonReadingPage lesson={lessonFixture} />);

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
});

describe("LessonRouteView", () => {
  it.each([
    ["unauthorized", "Learner session required"],
    ["forbidden", "Lesson access unavailable"],
    ["not-found", "Lesson not found"],
    ["unavailable", "Lesson temporarily unavailable"],
    ["invalid-content", "Lesson content unavailable"],
    ["unexpected", "Something went wrong"],
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
  });
});

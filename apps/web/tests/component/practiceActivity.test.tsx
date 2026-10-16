import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { PracticeActivityPage } from "../../src/features/practice-activity/PracticeActivityPage";
import { PracticeActivityRouteView } from "../../src/features/practice-activity/PracticeActivityRoute";
import { practiceFixture } from "./practiceFixture";


describe("practice activity page", () => {
  it("renders every answer-safe response shape and no submission authority", async () => {
    const user = userEvent.setup();
    render(<PracticeActivityPage practice={practiceFixture} />);

    expect(
      screen.getByRole("heading", { level: 1, name: practiceFixture.title }),
    ).toBeVisible();
    expect(screen.getAllByRole("radio")).toHaveLength(2);
    expect(screen.getAllByRole("checkbox")).toHaveLength(3);
    expect(screen.getByLabelText("Your answer (percent)")).toHaveAttribute(
      "inputmode",
      "decimal",
    );
    expect(screen.queryByRole("button", { name: /check|submit|save/i })).toBeNull();
    expect(screen.getByText(/does not check or save them yet/i)).toBeVisible();

    await user.click(screen.getByText("Technical record", { exact: true }));
    const technicalRecord = screen.getByText("Technical record", { exact: true }).closest("details");
    expect(technicalRecord).not.toBeNull();
    expect(within(technicalRecord!).getByText(practiceFixture.definition_digest)).toBeVisible();
    expect(within(technicalRecord!).getByText("risk-meaning")).toBeVisible();
    expect(within(technicalRecord!).getByText("numeric-exact-or-inclusive-range version 1.0.0")).toBeVisible();
    expect(screen.queryByText("correct_option_id")).toBeNull();
  });

  it("renders variable item and reference counts without a fixed fixture assumption", () => {
    const practice = structuredClone(practiceFixture);
    practice.items = [practice.items[2]!, practice.items[0]!];
    practice.review_references.push({
      resource_id: "second-review",
      resource_version: "1.1.0",
      resource_digest: "e".repeat(64),
      title: "Another review resource",
    });
    render(<PracticeActivityPage practice={practice} />);

    const questions = screen.getAllByText(/Question [12]/);
    expect(questions).toHaveLength(2);
    expect(screen.getByLabelText("Your answer (percent)")).toBeVisible();
    expect(screen.getByRole("radio", { name: /Outcomes can differ/i })).toBeVisible();
    expect(screen.getByText("Another review resource")).toBeVisible();
  });

  it("keeps denied and malformed states bounded and retryable only when useful", async () => {
    const user = userEvent.setup();
    const onRetry = vi.fn();
    const { rerender } = render(
      <PracticeActivityRouteView onRetry={onRetry} state={{ status: "unavailable" }} />,
    );
    await user.click(screen.getByRole("button", { name: "Try again" }));
    expect(onRetry).toHaveBeenCalledOnce();
    expect(screen.queryByText(practiceFixture.title)).toBeNull();

    rerender(
      <PracticeActivityRouteView onRetry={onRetry} state={{ status: "invalid-content" }} />,
    );
    expect(screen.getByRole("heading", { name: "We couldn't show this activity safely" })).toBeVisible();
    expect(screen.queryByRole("button", { name: "Try again" })).toBeNull();
  });
});

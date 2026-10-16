import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { PracticeActivityPage } from "../../src/features/practice-activity/PracticeActivityPage";
import { PracticeActivityRouteView } from "../../src/features/practice-activity/PracticeActivityRoute";
import type {
  PracticeSubmissionResult,
  PracticeSubmitter,
} from "../../src/features/practice-activity/model";
import { practiceFixture, practiceResultFixture } from "./practiceFixture";


const idleSubmitter: PracticeSubmitter = async () => ({ status: "unexpected" });

async function answerEveryQuestion(user: ReturnType<typeof userEvent.setup>) {
  await user.click(screen.getByRole("radio", { name: /Outcomes can differ/i }));
  for (const checkbox of screen.getAllByRole("checkbox")) {
    await user.click(checkbox);
  }
  await user.type(screen.getByLabelText("Your answer (percent)"), "5.00");
}

function resultFor(submissionId: string): PracticeSubmissionResult {
  return { ...structuredClone(practiceResultFixture), submission_id: submissionId };
}

describe("practice activity page", () => {
  it("renders every answer-safe response shape and one API-backed action", async () => {
    const user = userEvent.setup();
    render(
      <PracticeActivityPage
        practice={practiceFixture}
        submitPractice={idleSubmitter}
      />,
    );

    expect(
      screen.getByRole("heading", { level: 1, name: practiceFixture.title }),
    ).toBeVisible();
    expect(screen.getAllByRole("radio")).toHaveLength(2);
    expect(screen.getAllByRole("checkbox")).toHaveLength(3);
    expect(screen.getByLabelText("Your answer (percent)")).toHaveAttribute(
      "inputmode",
      "decimal",
    );
    expect(screen.getByRole("button", { name: "Check answers" })).toBeVisible();
    expect(screen.getByText(/saves your first completed attempt/i)).toBeVisible();

    await user.click(screen.getByText("Technical record", { exact: true }));
    const technicalRecord = screen.getByText("Technical record", { exact: true }).closest("details");
    expect(technicalRecord).not.toBeNull();
    expect(within(technicalRecord!).getByText(practiceFixture.definition_digest)).toBeVisible();
    expect(within(technicalRecord!).getByText("risk-meaning")).toBeVisible();
    expect(within(technicalRecord!).getByText("numeric-exact-or-inclusive-range version 1.0.0")).toBeVisible();
    expect(screen.queryByText("correct_option_id")).toBeNull();
  });

  it("submits the generated three-shape request and renders only server results", async () => {
    const user = userEvent.setup();
    const submitPractice = vi.fn<PracticeSubmitter>(
      async (_practice, submission) => ({
        status: "result",
        result: resultFor(submission.body.submission_id),
      }),
    );
    render(
      <PracticeActivityPage
        practice={practiceFixture}
        submitPractice={submitPractice}
      />,
    );

    await answerEveryQuestion(user);
    await user.click(screen.getByRole("button", { name: "Check answers" }));

    expect(await screen.findByRole("heading", { name: "Your result" })).toBeVisible();
    expect(screen.getByText("2 of 3")).toBeVisible();
    expect(screen.getByRole("heading", { name: /Question 3: Review this question/i })).toBeVisible();
    expect(screen.getByText(practiceResultFixture.item_results[2]!.feedback.text)).toBeVisible();
    expect(screen.getByText(/does not show mastery, certification/i)).toBeVisible();
    expect(screen.queryByText(/correct_option_id|answer key/i)).toBeNull();
    expect(submitPractice).toHaveBeenCalledOnce();

    const prepared = submitPractice.mock.calls[0]![1];
    expect(prepared.placementId).toBe(practiceFixture.placement_id);
    expect("learner_id" in prepared.body).toBe(false);
    expect(prepared.body.responses).toEqual([
      expect.objectContaining({
        item_type: "single_select",
        selected_option_id: "uncertainty",
      }),
      expect.objectContaining({
        item_type: "multiple_select",
        selected_option_ids: ["time", "market", "fees"],
      }),
      expect.objectContaining({
        item_type: "numeric_entry",
        entered_value: "5.00",
      }),
    ]);
    expect(screen.getByRole("radio", { name: /Outcomes can differ/i })).toBeDisabled();
  });

  it("focuses the first incomplete question without calling the API", async () => {
    const user = userEvent.setup();
    const submitPractice = vi.fn<PracticeSubmitter>();
    render(
      <PracticeActivityPage
        practice={practiceFixture}
        submitPractice={submitPractice}
      />,
    );

    await user.click(screen.getByRole("button", { name: "Check answers" }));

    expect(screen.getByRole("alert")).toHaveTextContent(/Complete this question/i);
    expect(screen.getByRole("radio", { name: /Outcomes can differ/i })).toHaveFocus();
    expect(submitPractice).not.toHaveBeenCalled();
  });

  it("reuses the identical prepared request after an uncertain failure", async () => {
    const user = userEvent.setup();
    const submitPractice = vi
      .fn<PracticeSubmitter>()
      .mockResolvedValueOnce({ status: "unavailable" })
      .mockImplementationOnce(async (_practice, submission) => ({
        status: "result",
        result: resultFor(submission.body.submission_id),
      }));
    render(
      <PracticeActivityPage
        practice={practiceFixture}
        submitPractice={submitPractice}
      />,
    );

    await answerEveryQuestion(user);
    await user.click(screen.getByRole("button", { name: "Check answers" }));
    expect(await screen.findByRole("alert")).toHaveTextContent(/reuse the same answers/i);
    expect(screen.getByRole("radio", { name: /Outcomes can differ/i })).toBeDisabled();
    await user.click(screen.getByRole("button", { name: "Try again" }));
    expect(await screen.findByRole("heading", { name: "Your result" })).toBeVisible();

    expect(submitPractice).toHaveBeenCalledTimes(2);
    expect(submitPractice.mock.calls[1]![1]).toBe(submitPractice.mock.calls[0]![1]);
    expect(submitPractice.mock.calls[1]![1].body.submission_id).toBe(
      submitPractice.mock.calls[0]![1].body.submission_id,
    );
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
    render(
      <PracticeActivityPage practice={practice} submitPractice={idleSubmitter} />,
    );

    const questions = screen.getAllByText(/Question [12]/);
    expect(questions).toHaveLength(2);
    expect(screen.getByLabelText("Your answer (percent)")).toBeVisible();
    expect(screen.getByRole("radio", { name: /Outcomes can differ/i })).toBeVisible();
    expect(screen.getByText("Another review resource")).toBeVisible();
  });

  it("keeps denied and malformed opening states bounded and retryable only when useful", async () => {
    const user = userEvent.setup();
    const onRetry = vi.fn();
    const { rerender } = render(
      <PracticeActivityRouteView
        onRetry={onRetry}
        state={{ status: "unavailable" }}
        submitPractice={idleSubmitter}
      />,
    );
    await user.click(screen.getByRole("button", { name: "Try again" }));
    expect(onRetry).toHaveBeenCalledOnce();
    expect(screen.queryByText(practiceFixture.title)).toBeNull();

    rerender(
      <PracticeActivityRouteView
        onRetry={onRetry}
        state={{ status: "invalid-content" }}
        submitPractice={idleSubmitter}
      />,
    );
    expect(screen.getByRole("heading", { name: "We couldn't show this activity safely" })).toBeVisible();
    expect(screen.queryByRole("button", { name: "Try again" })).toBeNull();
  });
});

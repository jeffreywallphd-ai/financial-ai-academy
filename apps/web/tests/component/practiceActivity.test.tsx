import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { PracticeActivityPage } from "../../src/features/practice-activity/PracticeActivityPage";
import { PracticeActivityRouteView } from "../../src/features/practice-activity/PracticeActivityRoute";
import {
  practiceDraftSaveResultIsSafe,
  practiceProgressIsSafe,
} from "../../src/features/practice-activity/model";
import type {
  PracticeDraftSaver,
  PracticeProgress,
  PracticeProgressReader,
  PracticeSubmissionResult,
  PracticeSubmitter,
} from "../../src/features/practice-activity/model";
import {
  practiceFixture,
  practiceProgressFixture,
  practiceResultFixture,
} from "./practiceFixture";


const idleSubmitter: PracticeSubmitter = async () => ({ status: "unexpected" });
const idleProgressReader: PracticeProgressReader = async () => ({
  status: "progress",
  progress: structuredClone(practiceProgressFixture),
});
const idleDraftSaver: PracticeDraftSaver = async (_practice, save) => ({
  status: "saved",
  draft: {
    ...structuredClone(practiceProgressFixture.draft!),
    responses: save.body.responses,
    revision: save.body.expected_revision + 1,
    saved_at: "2026-10-16T17:00:00Z",
  },
});

async function answerEveryQuestion(user: ReturnType<typeof userEvent.setup>) {
  await user.click(screen.getByRole("radio", { name: /Outcomes can differ/i }));
  for (const checkbox of screen.getAllByRole("checkbox")) {
    await user.click(checkbox);
  }
  const number = screen.getByLabelText("Your answer (percent)");
  await user.clear(number);
  await user.type(number, "5.00");
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
        progress={structuredClone(practiceProgressFixture)}
        readProgress={idleProgressReader}
        saveDraft={idleDraftSaver}
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
    expect(screen.getByText(/save partial answers to continue later/i)).toBeVisible();
    expect(screen.getByRole("radio", { name: /Outcomes can differ/i })).toBeChecked();
    expect(screen.getByLabelText("Your answer (percent)")).toHaveValue("4.50");
    expect(screen.getByRole("heading", { name: "Your saved attempts" })).toBeVisible();

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
        progress={structuredClone(practiceProgressFixture)}
        readProgress={idleProgressReader}
        saveDraft={idleDraftSaver}
        submitPractice={submitPractice}
      />,
    );

    await answerEveryQuestion(user);
    await user.click(screen.getByRole("button", { name: "Check answers" }));

    expect(await screen.findByRole("heading", { name: "Your result" })).toBeVisible();
    expect(screen.getAllByText("2 of 3")).toHaveLength(2);
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
        progress={structuredClone(practiceProgressFixture)}
        readProgress={idleProgressReader}
        saveDraft={idleDraftSaver}
        submitPractice={submitPractice}
      />,
    );

    await user.click(screen.getByRole("button", { name: "Check answers" }));

    expect(screen.getByRole("alert")).toHaveTextContent(/Complete this question/i);
    expect(screen.getByRole("checkbox", { name: "Time horizon" })).toHaveFocus();
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
        progress={structuredClone(practiceProgressFixture)}
        readProgress={idleProgressReader}
        saveDraft={idleDraftSaver}
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

  it("saves a valid partial snapshot with the current server revision", async () => {
    const user = userEvent.setup();
    const progress: PracticeProgress = {
      ...structuredClone(practiceProgressFixture),
      draft: null,
    };
    const saveDraft = vi.fn<PracticeDraftSaver>(idleDraftSaver);
    render(
      <PracticeActivityPage
        practice={practiceFixture}
        progress={progress}
        readProgress={idleProgressReader}
        saveDraft={saveDraft}
        submitPractice={idleSubmitter}
      />,
    );

    await user.click(screen.getByRole("radio", { name: /Outcomes can differ/i }));
    await user.click(screen.getByRole("button", { name: "Save progress" }));

    expect(await screen.findByRole("heading", { name: "Progress saved" })).toBeVisible();
    expect(saveDraft).toHaveBeenCalledOnce();
    const preparedSave = saveDraft.mock.calls[0]![1];
    expect(preparedSave.body.expected_revision).toBe(0);
    expect(preparedSave.body.responses).toEqual([
      expect.objectContaining({
        item_id: "risk-meaning",
        selected_option_id: "uncertainty",
      }),
    ]);
    expect("learner_id" in preparedSave.body).toBe(false);
  });

  it("does not overwrite a stale draft and offers the latest saved progress", async () => {
    const user = userEvent.setup();
    const saveDraft = vi.fn<PracticeDraftSaver>(async () => ({ status: "conflict" }));
    render(
      <PracticeActivityPage
        practice={practiceFixture}
        progress={structuredClone(practiceProgressFixture)}
        readProgress={idleProgressReader}
        saveDraft={saveDraft}
        submitPractice={idleSubmitter}
      />,
    );

    await user.click(screen.getByRole("button", { name: "Save progress" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(/newer progress is already saved/i);
    expect(screen.getByRole("button", { name: "Load saved progress" })).toBeVisible();
    expect(saveDraft.mock.calls[0]![1].body.expected_revision).toBe(1);
  });

  it("keeps completed history visible while starting a distinct retry", async () => {
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
        progress={structuredClone(practiceProgressFixture)}
        readProgress={idleProgressReader}
        saveDraft={idleDraftSaver}
        submitPractice={submitPractice}
      />,
    );

    await answerEveryQuestion(user);
    await user.click(screen.getByRole("button", { name: "Check answers" }));
    await user.click(await screen.findByRole("button", { name: "Try another attempt" }));

    expect(screen.getByRole("heading", { name: "Your saved attempts" })).toBeVisible();
    expect(screen.getByRole("heading", { name: "Attempt 1" })).toBeVisible();
    expect(screen.getByRole("radio", { name: /Outcomes can differ/i })).not.toBeChecked();
    expect(screen.getByLabelText("Your answer (percent)")).toHaveValue("");
    expect(screen.getByRole("button", { name: "Check answers" })).toBeEnabled();
  });

  it("removes mutation controls when the server says attempts are exhausted", () => {
    const firstAttempt = structuredClone(
      practiceProgressFixture.history.attempts[0]!,
    );
    const progress: PracticeProgress = {
      ...structuredClone(practiceProgressFixture),
      draft: null,
      retry_state: {
        ...structuredClone(practiceProgressFixture.retry_state),
        attempts_used: 3,
        attempts_remaining: 0,
        can_retry: false,
        state: "exhausted",
      },
      history: {
        ...structuredClone(practiceProgressFixture.history),
        attempts: [
          firstAttempt,
          {
            ...structuredClone(firstAttempt),
            attempt_order: 2,
            event_id: "44444444-4444-4444-8444-444444444445",
            attempt_id: "55555555-5555-4555-8555-555555555556",
            evidence_id: "66666666-6666-4666-8666-666666666667",
            submission_id: "77777777-7777-4777-8777-777777777778",
            completed_at: "2026-10-16T15:10:00Z",
          },
          {
            ...structuredClone(firstAttempt),
            attempt_order: 3,
            event_id: "44444444-4444-4444-8444-444444444446",
            attempt_id: "55555555-5555-4555-8555-555555555557",
            evidence_id: "66666666-6666-4666-8666-666666666668",
            submission_id: "77777777-7777-4777-8777-777777777779",
            completed_at: "2026-10-16T15:20:00Z",
          },
        ],
      },
    };
    render(
      <PracticeActivityPage
        practice={practiceFixture}
        progress={progress}
        readProgress={idleProgressReader}
        saveDraft={idleDraftSaver}
        submitPractice={idleSubmitter}
      />,
    );

    expect(screen.getByRole("heading", { name: "All attempts are complete" })).toBeVisible();
    expect(screen.queryByRole("button", { name: "Save progress" })).toBeNull();
    expect(screen.queryByRole("button", { name: "Check answers" })).toBeNull();
    expect(screen.getByRole("heading", { name: "Attempt 1" })).toBeVisible();
  });

  it("fails progress closed for extra authority or mismatched exact chains", () => {
    const extra = {
      ...structuredClone(practiceProgressFixture),
      learner_id: "private-learner",
    };
    const mismatched = structuredClone(practiceProgressFixture);
    mismatched.history.package_version = "9.9.9";

    expect(practiceProgressIsSafe(extra, practiceFixture)).toBe(false);
    expect(practiceProgressIsSafe(mismatched, practiceFixture)).toBe(false);
    expect(practiceProgressIsSafe(practiceProgressFixture, practiceFixture)).toBe(true);
  });

  it("correlates a saved draft with the exact conditional write", () => {
    const prepared = {
      placementId: practiceFixture.placement_id,
      body: {
        schema_version: "1.0.0" as const,
        placement_id: practiceFixture.placement_id,
        package_id: practiceFixture.package_id,
        package_version: practiceFixture.package_version,
        package_digest: practiceFixture.package_digest,
        definition_digest: practiceFixture.definition_digest,
        practice_id: practiceFixture.practice_id,
        practice_version: practiceFixture.practice_version,
        attempt_policy_id: practiceFixture.attempt_policy.policy_id,
        attempt_policy_version: practiceFixture.attempt_policy.policy_version,
        expected_revision: 1,
        responses: structuredClone(practiceProgressFixture.draft!.responses),
      },
    };
    const saved = {
      ...structuredClone(practiceProgressFixture.draft!),
      revision: 2,
    };
    const wrongResponse = structuredClone(saved);
    wrongResponse.responses[0]!.selected_option_id = "certainty";
    const wrongRevision = { ...structuredClone(saved), revision: 5 };

    expect(practiceDraftSaveResultIsSafe(saved, practiceFixture, prepared)).toBe(true);
    expect(
      practiceDraftSaveResultIsSafe(wrongResponse, practiceFixture, prepared),
    ).toBe(false);
    expect(
      practiceDraftSaveResultIsSafe(wrongRevision, practiceFixture, prepared),
    ).toBe(false);
  });

  it("rejects progress whose summary, retry, or review evidence conflicts", () => {
    const wrongScore = structuredClone(practiceProgressFixture);
    wrongScore.history.attempts[0]!.score = 1;
    const wrongAttemptCount = structuredClone(practiceProgressFixture);
    wrongAttemptCount.retry_state.attempts_used = 2;
    wrongAttemptCount.retry_state.attempts_remaining = 1;
    const wrongTargets = structuredClone(practiceProgressFixture);
    wrongTargets.review_targets = [];

    expect(practiceProgressIsSafe(wrongScore, practiceFixture)).toBe(false);
    expect(practiceProgressIsSafe(wrongAttemptCount, practiceFixture)).toBe(false);
    expect(practiceProgressIsSafe(wrongTargets, practiceFixture)).toBe(false);
  });

  it("accepts optional generated fields without opening the payload", () => {
    const optional = structuredClone(practiceProgressFixture) as Record<
      string,
      unknown
    >;
    delete optional.schema_version;
    const destination = (
      structuredClone(practiceProgressFixture).review_targets[0] as {
        destination: { section_id?: string | null };
      }
    ).destination;
    destination.section_id = null;
    const nullableSection = {
      ...structuredClone(practiceProgressFixture),
      review_targets: [
        {
          ...structuredClone(practiceProgressFixture.review_targets[0]),
          destination,
        },
      ],
    };

    expect(practiceProgressIsSafe(optional, practiceFixture)).toBe(true);
    expect(practiceProgressIsSafe(nullableSection, practiceFixture)).toBe(true);
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
      <PracticeActivityPage
        practice={practice}
        progress={{
          ...structuredClone(practiceProgressFixture),
          draft: null,
          history: {
            ...structuredClone(practiceProgressFixture.history),
            attempts: [],
          },
          review_targets: [],
          retry_state: {
            ...structuredClone(practiceProgressFixture.retry_state),
            attempts_used: 0,
            attempts_remaining: 3,
          },
        }}
        readProgress={idleProgressReader}
        saveDraft={idleDraftSaver}
        submitPractice={idleSubmitter}
      />,
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
        readProgress={idleProgressReader}
        saveDraft={idleDraftSaver}
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
        readProgress={idleProgressReader}
        saveDraft={idleDraftSaver}
        state={{ status: "invalid-content" }}
        submitPractice={idleSubmitter}
      />,
    );
    expect(screen.getByRole("heading", { name: "We couldn't show this activity safely" })).toBeVisible();
    expect(screen.queryByRole("button", { name: "Try again" })).toBeNull();
  });
});

import { useEffect, useRef, useState } from "react";

import { Icon } from "../../components/Icon";
import {
  ContextualHelpLinks,
  unavailableContextualHelpReader,
} from "../platform-help/ContextualHelpLinks";
import type { ContextualHelpReader } from "../platform-help/model";
import type {
  PracticeItem,
  PracticePresentation,
  PracticeProgress,
  PracticeProgressReader,
  PracticeDraft,
  PracticeDraftSaver,
  PracticeResponse,
  PracticeSubmissionOutcome,
  PracticeSubmissionResult,
  PracticeSubmitter,
  PreparedPracticeSubmission,
  PreparedPracticeDraftSave,
} from "./model";
import {
  canonicalDecimalPattern,
  preparePracticeDraftSave,
  preparePracticeSubmission,
  savedResponseForItem,
} from "./model";


type SubmissionViewState =
  | { status: "idle" }
  | { status: "invalid-input"; itemId: string }
  | { status: "submitting" }
  | PracticeSubmissionOutcome;

type DraftViewState =
  | { status: "idle" }
  | { status: "invalid-input"; itemId: string }
  | { status: "saving" }
  | { status: "saved"; draft: PracticeDraft }
  | { status: "invalid-request" }
  | { status: "unauthorized" }
  | { status: "forbidden" }
  | { status: "not-found" }
  | { status: "conflict" }
  | { status: "unavailable"; prepared: PreparedPracticeDraftSave }
  | { status: "invalid-result" }
  | { status: "unexpected" };

type ProgressRefreshState = "idle" | "loading" | "unavailable";

const DATE_TIME_FORMAT = new Intl.DateTimeFormat("en", {
  dateStyle: "long",
  timeStyle: "short",
  timeZone: "UTC",
});

function itemKind(item: PracticeItem): string {
  switch (item.item_type) {
    case "single_select":
      return "Choose one answer";
    case "multiple_select":
      return "Choose all answers that apply";
    case "numeric_entry":
      return "Enter a number";
  }
}

function PracticeResponseControl({
  disabled,
  index,
  invalid,
  item,
  savedResponse,
}: {
  disabled: boolean;
  index: number;
  invalid: boolean;
  item: PracticeItem;
  savedResponse: PracticeResponse | undefined;
}) {
  const descriptionId = `practice-item-${item.item_id}-description`;
  const errorId = `practice-item-${item.item_id}-error`;
  const describedBy = invalid ? `${descriptionId} ${errorId}` : descriptionId;
  if (item.item_type === "numeric_entry") {
    return (
      <fieldset className="practice-item">
        <legend>
          <span>Question {index + 1}</span>
          {item.prompt}
        </legend>
        <p className="practice-response-kind" id={descriptionId}>
          {item.scale === 0
            ? "Enter a whole number."
            : `Enter a number with exactly ${item.scale} decimal ${item.scale === 1 ? "place" : "places"}.`} Use 0 or a number without a leading zero. {item.allow_negative ? "Negative values are allowed, but negative zero is not." : "Use zero or a positive value."} Unit: {item.unit_label}.
        </p>
        <label htmlFor={`practice-item-${item.item_id}`}>
          Your answer ({item.unit_label})
        </label>
        <input
          aria-describedby={describedBy}
          aria-invalid={invalid || undefined}
          autoComplete="off"
          defaultValue={
            savedResponse?.item_type === "numeric_entry"
              ? savedResponse.entered_value
              : ""
          }
          disabled={disabled}
          id={`practice-item-${item.item_id}`}
          inputMode="decimal"
          name={item.item_id}
          pattern={canonicalDecimalPattern(item.scale, item.allow_negative)}
          type="text"
        />
        {invalid ? (
          <p className="practice-field-error" id={errorId}>
            Enter a number in the format described above.
          </p>
        ) : null}
      </fieldset>
    );
  }
  return (
    <fieldset className="practice-item">
      <legend>
        <span>Question {index + 1}</span>
        {item.prompt}
      </legend>
      <p className="practice-response-kind" id={descriptionId}>
        {itemKind(item)}.
      </p>
      <div aria-describedby={describedBy} className="practice-options">
        {item.options.map((option) => (
          <label key={option.option_id}>
            <input
              aria-invalid={invalid || undefined}
              defaultChecked={
                savedResponse?.item_type === "single_select"
                  ? savedResponse.selected_option_id === option.option_id
                  : savedResponse?.item_type === "multiple_select"
                    ? savedResponse.selected_option_ids.includes(option.option_id)
                    : false
              }
              disabled={disabled}
              name={item.item_id}
              type={item.item_type === "single_select" ? "radio" : "checkbox"}
              value={option.option_id}
            />
            <span>{option.label}</span>
          </label>
        ))}
      </div>
      {invalid ? (
        <p className="practice-field-error" id={errorId}>
          {item.item_type === "single_select"
            ? "Choose one answer."
            : "Choose at least one answer."}
        </p>
      ) : null}
    </fieldset>
  );
}

function TechnicalRecord({ practice }: { practice: PracticePresentation }) {
  return (
    <details>
      <summary>Technical record</summary>
      <dl>
        <div><dt>Data format version</dt><dd>{practice.schema_version}</dd></div>
        <div><dt>Placement</dt><dd>{practice.placement_id}</dd></div>
        <div><dt>Lesson package</dt><dd>{practice.package_id}</dd></div>
        <div><dt>Lesson version</dt><dd>{practice.package_version}</dd></div>
        <div><dt>Lesson integrity code</dt><dd><code>{practice.package_digest}</code></dd></div>
        <div><dt>Practice activity</dt><dd>{practice.practice_id}</dd></div>
        <div><dt>Practice version</dt><dd>{practice.practice_version}</dd></div>
        <div><dt>Practice integrity code</dt><dd><code>{practice.definition_digest}</code></dd></div>
        <div><dt>Attempt policy</dt><dd>{practice.attempt_policy.policy_id} version {practice.attempt_policy.policy_version}</dd></div>
      </dl>
      <h3>Question records</h3>
      {practice.items.map((item, index) => (
        <dl key={item.item_id}>
          <div><dt>Question</dt><dd>{index + 1}</dd></div>
          <div><dt>Question ID</dt><dd>{item.item_id}</dd></div>
          <div><dt>Question version</dt><dd>{item.item_version}</dd></div>
          <div><dt>Response type</dt><dd>{item.item_type}</dd></div>
          <div><dt>Scoring policy</dt><dd>{item.scoring_policy_id} version {item.scoring_policy_version}</dd></div>
          <div><dt>Maximum score</dt><dd>{item.max_score}</dd></div>
          {"options" in item
            ? item.options.map((option) => (
                <div key={option.option_id}>
                  <dt>Choice ID</dt><dd>{option.option_id}</dd>
                </div>
              ))
            : null}
        </dl>
      ))}
      <h3>Resource records</h3>
      {[...practice.source_references, ...practice.review_references].map(
        (reference, index) => (
          <dl key={`${reference.resource_id}-${reference.resource_digest}-${index}`}>
            <div><dt>Resource</dt><dd>{reference.resource_id}</dd></div>
            <div><dt>Resource version</dt><dd>{reference.resource_version}</dd></div>
            <div><dt>Resource integrity code</dt><dd><code>{reference.resource_digest}</code></dd></div>
          </dl>
        ),
      )}
    </details>
  );
}

function submittedAnswer(
  item: PracticeItem,
  result: PracticeSubmissionResult["item_results"][number],
): string {
  if (item.item_type === "numeric_entry" && result.item_type === "numeric_entry") {
    return `${result.entered_value} ${item.unit_label}`;
  }
  if (item.item_type === "single_select" && result.item_type === "single_select") {
    return item.options.find(
      (option) => option.option_id === result.selected_option_id,
    )?.label ?? "Submitted answer";
  }
  if (item.item_type === "multiple_select" && result.item_type === "multiple_select") {
    return result.selected_option_ids
      .map(
        (selected) =>
          item.options.find((option) => option.option_id === selected)?.label ??
          "Submitted answer",
      )
      .join(", ");
  }
  return "Submitted answer";
}

function ResultPanel({
  practice,
  readContextualHelp = unavailableContextualHelpReader,
  result,
}: {
  practice: PracticePresentation;
  readContextualHelp?: ContextualHelpReader;
  result: PracticeSubmissionResult;
}) {
  const references = new Map(
    practice.review_references.map((reference) => [
      reference.resource_id,
      reference.title,
    ]),
  );
  return (
    <section aria-labelledby="practice-result-title" className="practice-result">
      <h2 id="practice-result-title">Your result</h2>
      <p className="practice-result-summary">
        {result.outcome === "all_correct"
          ? "All answers are correct."
          : "Some answers need review."}
      </p>
      <dl className="practice-result-score">
        <div><dt>Score</dt><dd>{result.score} of {result.max_score}</dd></div>
        <div>
          <dt>Saved</dt>
          <dd><time dateTime={result.submitted_at}>{DATE_TIME_FORMAT.format(new Date(result.submitted_at))} UTC</time></dd>
        </div>
      </dl>
      <ol className="practice-result-list">
        {result.item_results.map((itemResult, index) => {
          const item = practice.items[index]!;
          return (
            <li key={itemResult.item_id}>
              <article>
                <h3>Question {index + 1}: {itemResult.correct ? "Correct" : "Review this question"}</h3>
                <p><strong>Your answer:</strong> {submittedAnswer(item, itemResult)}</p>
                <p>{itemResult.feedback.text}</p>
                <p>
                  <strong>Review material:</strong>{" "}
                  {itemResult.feedback.review_reference_ids
                    .map((referenceId) => references.get(referenceId))
                    .join(", ")}
                </p>
              </article>
            </li>
          );
        })}
      </ol>
      <p>
        This result checks this practice activity only. It does not show
        mastery, certification, investment suitability, or investment advice.
      </p>
      {readContextualHelp === unavailableContextualHelpReader ? null : (
        <ContextualHelpLinks
          contextKey="practice-result"
          readContextualHelp={readContextualHelp}
        />
      )}
      <details>
        <summary aria-label="Technical record for saved practice result">
          Technical record
        </summary>
        <dl>
          <div><dt>Result data format</dt><dd>{result.schema_version}</dd></div>
          <div><dt>Attempt reference</dt><dd><code>{result.attempt_id}</code></dd></div>
          <div><dt>Evidence reference</dt><dd><code>{result.evidence_id}</code></dd></div>
          <div><dt>Submission reference</dt><dd><code>{result.submission_id}</code></dd></div>
          <div><dt>Placement</dt><dd>{result.placement_id}</dd></div>
          <div><dt>Lesson package</dt><dd>{result.package_id} version {result.package_version}</dd></div>
          <div><dt>Lesson integrity code</dt><dd><code>{result.package_digest}</code></dd></div>
          <div><dt>Practice activity</dt><dd>{result.practice_id} version {result.practice_version}</dd></div>
          <div><dt>Practice integrity code</dt><dd><code>{result.definition_digest}</code></dd></div>
          <div><dt>Attempt policy</dt><dd>{result.attempt_policy_id} version {result.attempt_policy_version}</dd></div>
          <div><dt>Saved at</dt><dd><code>{result.submitted_at}</code></dd></div>
        </dl>
      </details>
    </section>
  );
}

function ReviewTargets({ progress }: { progress: PracticeProgress }) {
  if (progress.review_targets.length === 0) {
    return null;
  }
  return (
    <section aria-labelledby="practice-review-title" className="practice-review">
      <h2 id="practice-review-title">Review before another attempt</h2>
      <p>
        These lessons match the review material named by your latest saved
        result. They are not personalized recommendations.
      </p>
      <ul>
        {progress.review_targets.map((target) => (
          <li key={target.resource_id}>
            {target.state === "available" ? (
              <a
                href={`/learn/placements/${encodeURIComponent(target.destination.placement_id)}`}
              >
                Open {target.resource_title}
              </a>
            ) : (
              <span>
                {target.resource_title} is not available in this learning path.
              </span>
            )}
          </li>
        ))}
      </ul>
    </section>
  );
}

function AttemptHistory({
  practice,
  progress,
}: {
  practice: PracticePresentation;
  progress: PracticeProgress;
}) {
  const attempts = progress.history.attempts;
  return (
    <section aria-labelledby="practice-history-title" className="practice-history">
      <h2 id="practice-history-title">Your saved attempts</h2>
      {attempts.length === 0 ? (
        <p>No completed attempts are saved yet.</p>
      ) : (
        <ol>
          {attempts.map((attempt) => (
            <li key={attempt.attempt_id}>
              <article>
                <h3>Attempt {attempt.attempt_order}</h3>
                <dl className="practice-history-summary">
                  <div>
                    <dt>Score</dt>
                    <dd>{attempt.score} of {attempt.max_score}</dd>
                  </div>
                  <div>
                    <dt>Result</dt>
                    <dd>
                      {attempt.outcome === "all_correct"
                        ? "All answers correct"
                        : "Review needed"}
                    </dd>
                  </div>
                  <div>
                    <dt>Saved</dt>
                    <dd>
                      <time dateTime={attempt.completed_at}>
                        {DATE_TIME_FORMAT.format(new Date(attempt.completed_at))} UTC
                      </time>
                    </dd>
                  </div>
                </dl>
                <ul className="practice-history-items">
                  {attempt.item_summaries.map((summary, index) => (
                    <li key={summary.item_id}>
                      Question {index + 1}: {summary.correct ? "Correct" : "Review needed"}
                    </li>
                  ))}
                </ul>
                <details>
                  <summary>Technical record for attempt {attempt.attempt_order}</summary>
                  <dl>
                    <div><dt>Attempt reference</dt><dd><code>{attempt.attempt_id}</code></dd></div>
                    <div><dt>Evidence reference</dt><dd><code>{attempt.evidence_id}</code></dd></div>
                    <div><dt>Event reference</dt><dd><code>{attempt.event_id}</code></dd></div>
                    <div><dt>Submission reference</dt><dd><code>{attempt.submission_id}</code></dd></div>
                    <div><dt>Evidence-source integrity code</dt><dd><code>{progress.history.source_digest}</code></dd></div>
                    <div><dt>Practice activity</dt><dd>{practice.practice_id} version {practice.practice_version}</dd></div>
                  </dl>
                </details>
              </article>
            </li>
          ))}
        </ol>
      )}
      <p>
        These records show results for this practice activity. They do not show
        mastery, certification, investment suitability, or investment advice.
      </p>
    </section>
  );
}

function statusMessage(status: SubmissionViewState["status"]): {
  title: string;
  body: string;
} | null {
  switch (status) {
    case "invalid-input":
      return { title: "Complete this question", body: "Choose or enter an answer before checking your work." };
    case "invalid-request":
      return { title: "We couldn't check these answers", body: "No new result was recorded. Reload the activity before trying again." };
    case "unauthorized":
      return { title: "Your learner session ended", body: "We couldn't check these answers. No new result was recorded. Reload the activity to start a new session." };
    case "forbidden":
      return { title: "You don't have access to check these answers", body: "No new result was recorded." };
    case "not-found":
    case "stale":
      return { title: "This activity changed", body: "We did not save a new result from this page. Reload the activity to open the current version." };
    case "conflict":
      return { title: "These answers don't match the first request", body: "No duplicate result was recorded. Reload the activity before continuing." };
    case "already-completed":
      return { title: "A completed attempt is already saved", body: "No duplicate result was recorded. Reload this activity to see your saved attempts and current retry status." };
    case "attempt-limit":
      return { title: "No attempts remain", body: "No new result was recorded. Your earlier attempts are still available below." };
    case "unavailable":
      return { title: "We couldn't confirm the saved result", body: "Try again. We will reuse the same answers and submission reference to avoid a duplicate result." };
    case "invalid-result":
      return { title: "We couldn't safely show the result", body: "Your answers may have been saved, but no partial result was shown. Reload the activity before continuing." };
    case "unexpected":
      return { title: "We couldn't finish checking these answers", body: "Your answers may have been saved. Reload the activity before continuing." };
    default:
      return null;
  }
}

function draftStatusMessage(status: DraftViewState["status"]): {
  title: string;
  body: string;
} | null {
  switch (status) {
    case "invalid-input":
      return { title: "Check this answer", body: "Correct the answer format before saving your progress." };
    case "saved":
      return { title: "Progress saved", body: "You can leave this activity and continue these answers later." };
    case "invalid-request":
      return { title: "We couldn't save this progress", body: "Reload the activity before trying again. Your saved progress was not replaced." };
    case "unauthorized":
      return { title: "Your learner session ended", body: "We couldn't save this progress. Reload the activity to start a new session." };
    case "forbidden":
      return { title: "You don't have access to save this progress", body: "Your saved progress was not changed." };
    case "not-found":
      return { title: "This activity is no longer available", body: "Your saved progress was not changed. Return to your learning path." };
    case "conflict":
      return { title: "Newer progress is already saved", body: "We did not replace it. Reload the activity to continue from the latest saved answers." };
    case "unavailable":
      return { title: "We couldn't confirm the save", body: "Your progress may have been saved. Try the same save again, or reload before changing these answers." };
    case "invalid-result":
      return { title: "We couldn't safely confirm the save", body: "We did not show partial save details. Reload the activity before continuing." };
    case "unexpected":
      return { title: "We couldn't finish saving", body: "Your progress may have been saved. Reload the activity before continuing." };
    default:
      return null;
  }
}

export function PracticeActivityPage({
  practice,
  progress: initialProgress,
  readContextualHelp = unavailableContextualHelpReader,
  readProgress,
  saveDraft,
  submitPractice,
}: {
  practice: PracticePresentation;
  progress: PracticeProgress;
  readContextualHelp?: ContextualHelpReader;
  readProgress: PracticeProgressReader;
  saveDraft: PracticeDraftSaver;
  submitPractice: PracticeSubmitter;
}) {
  const [progress, setProgress] = useState(initialProgress);
  const [resumeDraft, setResumeDraft] = useState(initialProgress.draft);
  const [formKey, setFormKey] = useState(0);
  const [prepared, setPrepared] = useState<PreparedPracticeSubmission | null>(null);
  const [submission, setSubmission] = useState<SubmissionViewState>({ status: "idle" });
  const [draft, setDraft] = useState<DraftViewState>({ status: "idle" });
  const [progressRefresh, setProgressRefresh] =
    useState<ProgressRefreshState>("idle");
  const formRef = useRef<HTMLFormElement | null>(null);
  const statusRef = useRef<HTMLElement | null>(null);
  const draftStatusRef = useRef<HTMLElement | null>(null);
  const submissionInFlight = useRef(false);
  const draftInFlight = useRef(false);
  const submitAbortController = useRef<AbortController | null>(null);
  const draftAbortController = useRef<AbortController | null>(null);
  const progressAbortController = useRef<AbortController | null>(null);

  useEffect(
    () => () => {
      submitAbortController.current?.abort();
      draftAbortController.current?.abort();
      progressAbortController.current?.abort();
    },
    [],
  );
  useEffect(() => {
    if (
      submission.status !== "idle" &&
      submission.status !== "submitting" &&
      submission.status !== "invalid-input"
    ) {
      statusRef.current?.focus();
    }
  }, [submission.status]);
  useEffect(() => {
    if (
      draft.status !== "idle" &&
      draft.status !== "saving" &&
      draft.status !== "invalid-input"
    ) {
      draftStatusRef.current?.focus();
    }
  }, [draft.status]);

  async function refreshProgress(options?: { restoreDraft?: boolean }) {
    progressAbortController.current?.abort();
    const controller = new AbortController();
    progressAbortController.current = controller;
    setProgressRefresh("loading");
    try {
      const outcome = await readProgress(practice, controller.signal);
      if (controller.signal.aborted) {
        return false;
      }
      if (outcome.status !== "progress") {
        setProgressRefresh("unavailable");
        return false;
      }
      setProgress(outcome.progress);
      if (options?.restoreDraft) {
        setResumeDraft(outcome.progress.draft);
        setPrepared(null);
        setSubmission({ status: "idle" });
        setDraft({ status: "idle" });
        setFormKey((value) => value + 1);
      }
      setProgressRefresh("idle");
      return true;
    } catch {
      if (!controller.signal.aborted) {
        setProgressRefresh("unavailable");
      }
      return false;
    }
  }

  async function send(value: PreparedPracticeSubmission) {
    if (submissionInFlight.current) {
      return;
    }
    submissionInFlight.current = true;
    submitAbortController.current?.abort();
    const controller = new AbortController();
    submitAbortController.current = controller;
    setSubmission({ status: "submitting" });
    try {
      const outcome = await submitPractice(practice, value, controller.signal);
      if (!controller.signal.aborted) {
        setSubmission(outcome);
        if (outcome.status === "result") {
          setResumeDraft(null);
          await refreshProgress();
        }
      }
    } catch {
      if (!controller.signal.aborted) {
        setSubmission({ status: "unexpected" });
      }
    } finally {
      submissionInFlight.current = false;
    }
  }

  async function savePreparedDraft(value: PreparedPracticeDraftSave) {
    if (draftInFlight.current) {
      return;
    }
    draftInFlight.current = true;
    draftAbortController.current?.abort();
    const controller = new AbortController();
    draftAbortController.current = controller;
    setDraft({ status: "saving" });
    try {
      const outcome = await saveDraft(practice, value, controller.signal);
      if (controller.signal.aborted) {
        return;
      }
      if (outcome.status === "saved") {
        setProgress((current) => ({ ...current, draft: outcome.draft }));
        setResumeDraft(outcome.draft);
        setDraft({ status: "saved", draft: outcome.draft });
      } else if (outcome.status === "unavailable") {
        setDraft({ status: "unavailable", prepared: value });
      } else {
        setDraft(outcome);
      }
    } catch {
      if (!controller.signal.aborted) {
        setDraft({ status: "unexpected" });
      }
    } finally {
      draftInFlight.current = false;
    }
  }

  function focusItem(itemId: string, form: HTMLFormElement) {
    const control = form.elements.namedItem(itemId);
    if (control instanceof HTMLElement) {
      control.focus();
      return;
    }
    if (control instanceof RadioNodeList) {
      const first = control.item(0);
      if (first instanceof HTMLElement) {
        first.focus();
      }
    }
  }

  function saveCurrentProgress() {
    const form = formRef.current;
    if (form === null || prepared !== null || !progress.retry_state.can_retry) {
      return;
    }
    const preparation = preparePracticeDraftSave(
      practice,
      new FormData(form),
      progress.draft?.revision ?? 0,
    );
    if (preparation.status === "invalid") {
      setDraft({ status: "invalid-input", itemId: preparation.itemId });
      focusItem(preparation.itemId, form);
      return;
    }
    void savePreparedDraft(preparation.save);
  }

  function beginAnotherAttempt() {
    if (!progress.retry_state.can_retry) {
      return;
    }
    setPrepared(null);
    setSubmission({ status: "idle" });
    setDraft({ status: "idle" });
    setResumeDraft(null);
    setFormKey((value) => value + 1);
    requestAnimationFrame(() => {
      const first = formRef.current?.elements.namedItem(
        practice.items[0]?.item_id ?? "",
      );
      if (first instanceof HTMLElement) {
        first.focus();
      } else if (first instanceof RadioNodeList) {
        const control = first.item(0);
        if (control instanceof HTMLElement) {
          control.focus();
        }
      }
    });
  }

  const locked = prepared !== null || !progress.retry_state.can_retry;
  const message = statusMessage(submission.status);
  const draftMessage = draftStatusMessage(draft.status);

  return (
    <div className="practice-layout">
      <article aria-labelledby="practice-title" className="practice-card">
        <header className="practice-header">
          <p className="eyebrow">
            <Icon className="faa-icon--active" name="learn" />
            Practice activity
          </p>
          <h1 id="practice-title">{practice.title}</h1>
          <p className="practice-purpose">{practice.purpose}</p>
          <p>{practice.instructions}</p>
        </header>

        <section aria-labelledby="practice-response-status" className="practice-notice">
          <h2 id="practice-response-status">
            {progress.retry_state.can_retry
              ? resumeDraft
                ? "Continue your saved answers"
                : "Answer every question"
              : "All attempts are complete"}
          </h2>
          <p>
            {progress.retry_state.can_retry
              ? "Save partial answers to continue later, or check every answer when you are ready."
              : "Review your saved attempts and learning material below."}
          </p>
        </section>

        <form
          key={formKey}
          noValidate
          ref={formRef}
          onChange={() => {
            if (submission.status === "invalid-input") {
              setSubmission({ status: "idle" });
            }
            if (draft.status === "invalid-input" || draft.status === "saved") {
              setDraft({ status: "idle" });
            }
          }}
          onSubmit={(event) => {
            event.preventDefault();
            if (locked || submissionInFlight.current) {
              return;
            }
            const preparation = preparePracticeSubmission(
              practice,
              new FormData(event.currentTarget),
              crypto.randomUUID(),
            );
            if (preparation.status === "invalid") {
              setSubmission({ status: "invalid-input", itemId: preparation.itemId });
              focusItem(preparation.itemId, event.currentTarget);
              return;
            }
            setPrepared(preparation.submission);
            void send(preparation.submission);
          }}
        >
          <section aria-labelledby="practice-questions">
            <h2 id="practice-questions">Questions</h2>
            <div className="practice-question-list">
              {practice.items.map((item, index) => (
                <PracticeResponseControl
                  disabled={locked}
                  index={index}
                  invalid={submission.status === "invalid-input" && submission.itemId === item.item_id}
                  item={item}
                  key={item.item_id}
                  savedResponse={savedResponseForItem(resumeDraft, item.item_id)}
                />
              ))}
            </div>
          </section>
          {!locked ? (
            <div className="practice-actions">
              <button
                className="button button--secondary"
                disabled={draft.status === "saving"}
                onClick={saveCurrentProgress}
                type="button"
              >
                Save progress
              </button>
              <button className="button practice-submit" type="submit">Check answers</button>
            </div>
          ) : null}
        </form>

        <div aria-atomic="true" aria-live="polite" className="practice-draft-status">
          {draft.status === "saving" ? <p role="status">Saving your progress…</p> : null}
          {draftMessage ? (
            <section
              className={draft.status === "saved" ? "practice-save-confirmation" : "practice-submission-error"}
              ref={(element) => { draftStatusRef.current = element; }}
              role={draft.status === "saved" ? "status" : "alert"}
              tabIndex={-1}
            >
              <h2>{draftMessage.title}</h2>
              <p>{draftMessage.body}</p>
              {draft.status === "saved" ? (
                <p>
                  Saved <time dateTime={draft.draft.saved_at}>{DATE_TIME_FORMAT.format(new Date(draft.draft.saved_at))} UTC</time>
                </p>
              ) : null}
              {draft.status === "unavailable" ? (
                <button className="button button--secondary" onClick={() => void savePreparedDraft(draft.prepared)} type="button">
                  Try same save again
                </button>
              ) : null}
              {draft.status === "conflict" ? (
                <button className="button button--secondary" onClick={() => void refreshProgress({ restoreDraft: true })} type="button">
                  Load saved progress
                </button>
              ) : null}
            </section>
          ) : null}
        </div>

        <div aria-atomic="true" aria-live="polite" className="practice-submission-status">
          {submission.status === "submitting" ? <p role="status">Checking your answers…</p> : null}
          {submission.status === "result" ? (
            <div ref={(element) => { statusRef.current = element; }} tabIndex={-1}>
              <ResultPanel
                practice={practice}
                readContextualHelp={readContextualHelp}
                result={submission.result}
              />
              {progressRefresh === "loading" ? <p role="status">Updating your saved attempts…</p> : null}
              {progressRefresh === "unavailable" ? (
                <p>Reload this activity to see the latest saved attempt and retry status.</p>
              ) : null}
              {progressRefresh === "idle" && progress.retry_state.can_retry ? (
                <button className="button" onClick={beginAnotherAttempt} type="button">
                  Try another attempt
                </button>
              ) : null}
            </div>
          ) : null}
          {message ? (
            <section
              className="practice-submission-error"
              ref={(element) => { statusRef.current = element; }}
              role="alert"
              tabIndex={-1}
            >
              <h2>{message.title}</h2>
              <p>{message.body}</p>
              {submission.status === "unavailable" && prepared ? (
                <button className="button button--secondary" onClick={() => void send(prepared)} type="button">
                  Try again
                </button>
              ) : null}
            </section>
          ) : null}
        </div>

        <ReviewTargets progress={progress} />
        <AttemptHistory practice={practice} progress={progress} />

        <section aria-labelledby="practice-resources" className="practice-resources">
          <h2 id="practice-resources">Learning and review material</h2>
          <div className="practice-resource-groups">
            <div>
              <h3>Learning material</h3>
              <ul>{practice.source_references.map((reference) => <li key={reference.resource_id}>{reference.title}</li>)}</ul>
            </div>
            <div>
              <h3>Review material</h3>
              <ul>{practice.review_references.map((reference) => <li key={reference.resource_id}>{reference.title}</li>)}</ul>
            </div>
          </div>
        </section>
      </article>

      <aside aria-label="Practice activity details" className="practice-context-rail">
        <section aria-labelledby="attempt-policy" className="context-card">
          <h2 id="attempt-policy">
            <Icon className="faa-icon--success" name="shield-check" />
            How attempts work now
          </h2>
          <p>
            {progress.retry_state.attempts_used} of {progress.retry_state.max_attempts} attempts completed.
          </p>
          <p>
            {progress.retry_state.attempts_remaining === 1
              ? "1 attempt remains."
              : `${progress.retry_state.attempts_remaining} attempts remain.`}
          </p>
          {progress.draft ? (
            <p>
              Saved progress is available from <time dateTime={progress.draft.saved_at}>{DATE_TIME_FORMAT.format(new Date(progress.draft.saved_at))} UTC</time>.
            </p>
          ) : (
            <p>No partial answers are currently saved.</p>
          )}
        </section>
        <section aria-labelledby="practice-evidence" className="context-card">
          <h2 id="practice-evidence">Activity details</h2>
          <p>
            This activity checks general learning. It does not assess investment suitability, provide investment advice, or show mastery or certification.
          </p>
          <TechnicalRecord practice={practice} />
        </section>
      </aside>
    </div>
  );
}

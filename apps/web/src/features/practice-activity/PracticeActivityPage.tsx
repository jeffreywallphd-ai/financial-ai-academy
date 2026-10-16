import { useEffect, useRef, useState } from "react";

import { Icon } from "../../components/Icon";
import type {
  PracticeItem,
  PracticePresentation,
  PracticeSubmissionOutcome,
  PracticeSubmissionResult,
  PracticeSubmitter,
  PreparedPracticeSubmission,
} from "./model";
import {
  canonicalDecimalPattern,
  preparePracticeSubmission,
} from "./model";


type SubmissionViewState =
  | { status: "idle" }
  | { status: "invalid-input"; itemId: string }
  | { status: "submitting" }
  | PracticeSubmissionOutcome;

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
}: {
  disabled: boolean;
  index: number;
  invalid: boolean;
  item: PracticeItem;
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
  result,
}: {
  practice: PracticePresentation;
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
      return { title: "A completed attempt is already saved", body: "No second result was recorded. Additional attempts and earlier-attempt review will be added in a later step." };
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

export function PracticeActivityPage({
  practice,
  submitPractice,
}: {
  practice: PracticePresentation;
  submitPractice: PracticeSubmitter;
}) {
  const [prepared, setPrepared] = useState<PreparedPracticeSubmission | null>(null);
  const [submission, setSubmission] = useState<SubmissionViewState>({ status: "idle" });
  const statusRef = useRef<HTMLElement | null>(null);
  const inFlight = useRef(false);
  const abortController = useRef<AbortController | null>(null);

  useEffect(() => () => abortController.current?.abort(), []);
  useEffect(() => {
    if (
      submission.status !== "idle" &&
      submission.status !== "submitting" &&
      submission.status !== "invalid-input"
    ) {
      statusRef.current?.focus();
    }
  }, [submission.status]);

  async function send(value: PreparedPracticeSubmission) {
    if (inFlight.current) {
      return;
    }
    inFlight.current = true;
    abortController.current?.abort();
    const controller = new AbortController();
    abortController.current = controller;
    setSubmission({ status: "submitting" });
    try {
      const outcome = await submitPractice(practice, value, controller.signal);
      if (!controller.signal.aborted) {
        setSubmission(outcome);
      }
    } catch {
      if (!controller.signal.aborted) {
        setSubmission({ status: "unexpected" });
      }
    } finally {
      inFlight.current = false;
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

  const locked = prepared !== null;
  const message = statusMessage(submission.status);

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
          <h2 id="practice-response-status">Answer every question</h2>
          <p>Check your answers when you are ready. This step saves your first completed attempt.</p>
        </section>

        <form
          noValidate
          onChange={() => {
            if (submission.status === "invalid-input") {
              setSubmission({ status: "idle" });
            }
          }}
          onSubmit={(event) => {
            event.preventDefault();
            if (locked || inFlight.current) {
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
                />
              ))}
            </div>
          </section>
          {!locked ? (
            <button className="button practice-submit" type="submit">Check answers</button>
          ) : null}
        </form>

        <div aria-atomic="true" aria-live="polite" className="practice-submission-status">
          {submission.status === "submitting" ? <p role="status">Checking your answers…</p> : null}
          {submission.status === "result" ? (
            <div ref={(element) => { statusRef.current = element; }} tabIndex={-1}>
              <ResultPanel practice={practice} result={submission.result} />
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
          <p>This page can save your first completed attempt.</p>
          <p>The lesson version allows up to {practice.attempt_policy.max_attempts} attempts.</p>
          <p>Additional attempts, pause-and-return, and earlier-attempt review will be added in a later step.</p>
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

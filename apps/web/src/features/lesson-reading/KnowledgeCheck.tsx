import { useEffect, useMemo, useRef, useState } from "react";

import {
  createFinancialAcademyApiClient,
  type components,
  type FinancialAcademyApiClient,
} from "../../generated/api-client";


type Completion =
  components["schemas"]["LessonCompletionResponseModel"];
type CompletionHistoryEntry =
  components["schemas"]["LessonCompletionHistoryEntryModel"];
type Presentation =
  components["schemas"]["KnowledgeCheckPresentationResponseModel"];
type Result =
  components["schemas"]["KnowledgeCheckResultResponseModel"];

type FailureStage = "completion" | "knowledge-check";
type LoadState =
  | { status: "loading" }
  | { status: "completed"; completion: Completion }
  | { status: "ready"; presentation: Presentation }
  | { status: "denied"; stage: FailureStage }
  | { status: "invalid"; stage: FailureStage }
  | { status: "unavailable"; stage: FailureStage };

type SubmitState =
  | { status: "idle" }
  | { status: "submitting" }
  | { status: "result"; result: Result }
  | { status: "conflict" }
  | { status: "denied" }
  | { status: "unavailable" };

const DIGEST = /^[a-f0-9]{64}$/;
const REFERENCE = /^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$/;
const TIMESTAMP =
  /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$/;
const DATE_TIME_FORMAT = new Intl.DateTimeFormat("en", {
  dateStyle: "long",
  timeStyle: "short",
  timeZone: "UTC",
});

function safeReference(value: string): boolean {
  return REFERENCE.test(value);
}

function safeTimestamp(value: string): boolean {
  return TIMESTAMP.test(value) && !Number.isNaN(Date.parse(value));
}

function formatTimestamp(value: string): string {
  return DATE_TIME_FORMAT.format(new Date(value));
}

function safeHistoryEntry(value: CompletionHistoryEntry): boolean {
  return (
    safeReference(value.event_id) &&
    safeReference(value.attempt_id) &&
    safeReference(value.evidence_id) &&
    safeReference(value.package_id) &&
    value.package_version === "1.1.0" &&
    DIGEST.test(value.package_digest) &&
    safeReference(value.assessment_id) &&
    value.assessment_version === "1.0.0" &&
    DIGEST.test(value.definition_digest) &&
    safeReference(value.item_id) &&
    value.item_version === "1.0.0" &&
    value.scoring_policy_id === "single-select-exact-match" &&
    value.scoring_policy_version === "1.0.0" &&
    Number.isInteger(value.score) &&
    value.score >= 0 &&
    value.max_score === 1 &&
    value.score <= value.max_score &&
    safeTimestamp(value.completed_at)
  );
}

function sameEvidenceChain(
  first: CompletionHistoryEntry,
  value: CompletionHistoryEntry,
): boolean {
  return (
    value.package_id === first.package_id &&
    value.package_version === first.package_version &&
    value.package_digest === first.package_digest &&
    value.assessment_id === first.assessment_id &&
    value.assessment_version === first.assessment_version &&
    value.definition_digest === first.definition_digest &&
    value.item_id === first.item_id &&
    value.item_version === first.item_version &&
    value.scoring_policy_id === first.scoring_policy_id &&
    value.scoring_policy_version === first.scoring_policy_version
  );
}

function safeCompletion(value: Completion, placementId: string): boolean {
  if (
    value.projection_version !== "1.0.0" ||
    value.placement_id !== placementId ||
    !DIGEST.test(value.source_digest) ||
    !safeTimestamp(value.rebuilt_at) ||
    !Array.isArray(value.history)
  ) {
    return false;
  }
  if (!value.completed) {
    return (
      value.completion_meaning === "not_completed" &&
      value.history.length === 0
    );
  }
  if (
    value.completion_meaning !== "bounded_knowledge_check_completed" ||
    value.history.length === 0 ||
    !value.history.every(safeHistoryEntry)
  ) {
    return false;
  }
  const first = value.history[0];
  if (!first || !value.history.every((entry) => sameEvidenceChain(first, entry))) {
    return false;
  }
  const eventIds = new Set<string>();
  const evidenceIds = new Set<string>();
  const attemptIds = new Set<string>();
  let previousKey = "";
  for (const entry of value.history) {
    const orderKey = `${entry.completed_at}\u0000${entry.event_id}`;
    if (
      orderKey < previousKey ||
      eventIds.has(entry.event_id) ||
      evidenceIds.has(entry.evidence_id) ||
      attemptIds.has(entry.attempt_id)
    ) {
      return false;
    }
    previousKey = orderKey;
    eventIds.add(entry.event_id);
    evidenceIds.add(entry.evidence_id);
    attemptIds.add(entry.attempt_id);
  }
  return true;
}

function safePresentation(value: Presentation): boolean {
  return (
    value.schema_version === "1.0.0" &&
    value.item_type === "single_select" &&
    DIGEST.test(value.package_digest) &&
    DIGEST.test(value.definition_digest) &&
    value.prompt.trim().length > 0 &&
    value.options.length >= 2 &&
    value.options.length <= 6 &&
    new Set(value.options.map((option) => option.option_id)).size ===
      value.options.length &&
    value.options.every(
      (option) =>
        option.option_id.trim().length > 0 &&
        option.label.trim().length > 0,
    )
  );
}

function browserClient() {
  return createFinancialAcademyApiClient(window.location.origin);
}

function RetainedCompletion({ completion }: { completion: Completion }) {
  return (
    <section
      aria-labelledby="retained-completion-title"
      className="knowledge-check-card completion-card"
    >
      <p className="eyebrow">Retained learning evidence</p>
      <h2 id="retained-completion-title">Retained lesson completion</h2>
      <p>
        Your completion was reproduced from retained Assessment evidence for
        this exact lesson placement.
      </p>

      <dl className="completion-summary">
        <div>
          <dt>Completion meaning</dt>
          <dd>Bounded knowledge check completed</dd>
        </div>
        <div>
          <dt>Projection rebuilt</dt>
          <dd>
            <time dateTime={completion.rebuilt_at}>
              {formatTimestamp(completion.rebuilt_at)} UTC
            </time>
          </dd>
        </div>
        <div>
          <dt>Source-set digest</dt>
          <dd>
            <code>{completion.source_digest}</code>
          </dd>
        </div>
      </dl>

      <h3>Completion evidence</h3>
      <ol className="completion-history">
        {completion.history.map((entry) => (
          <li key={entry.event_id}>
            <article aria-label={`Completion event ${entry.event_id}`}>
              <dl>
                <div>
                  <dt>Score</dt>
                  <dd>
                    {entry.score} of {entry.max_score}
                  </dd>
                </div>
                <div>
                  <dt>Completed</dt>
                  <dd>
                    <time dateTime={entry.completed_at}>
                      {formatTimestamp(entry.completed_at)} UTC
                    </time>
                  </dd>
                </div>
                <div>
                  <dt>Lesson package</dt>
                  <dd>
                    {entry.package_id} version {entry.package_version}
                  </dd>
                </div>
                <div>
                  <dt>Package digest</dt>
                  <dd>
                    <code>{entry.package_digest}</code>
                  </dd>
                </div>
                <div>
                  <dt>Assessment</dt>
                  <dd>
                    {entry.assessment_id} version {entry.assessment_version}
                  </dd>
                </div>
                <div>
                  <dt>Definition digest</dt>
                  <dd>
                    <code>{entry.definition_digest}</code>
                  </dd>
                </div>
                <div>
                  <dt>Item</dt>
                  <dd>
                    {entry.item_id} version {entry.item_version}
                  </dd>
                </div>
                <div>
                  <dt>Scoring policy</dt>
                  <dd>
                    {entry.scoring_policy_id} version{" "}
                    {entry.scoring_policy_version}
                  </dd>
                </div>
                <div>
                  <dt>Attempt reference</dt>
                  <dd>
                    <code>{entry.attempt_id}</code>
                  </dd>
                </div>
                <div>
                  <dt>Evidence reference</dt>
                  <dd>
                    <code>{entry.evidence_id}</code>
                  </dd>
                </div>
                <div>
                  <dt>Source event</dt>
                  <dd>
                    <code>{entry.event_id}</code>
                  </dd>
                </div>
              </dl>
            </article>
          </li>
        ))}
      </ol>
      <p className="completion-limitation">
        This is evidence of one bounded knowledge check. It is not a mastery or
        certification decision and does not provide investment advice,
        suitability, or performance evidence.
      </p>
    </section>
  );
}

export function KnowledgeCheck({
  client,
  placementId,
}: {
  client?: FinancialAcademyApiClient;
  placementId: string;
}) {
  const api = useMemo(() => client ?? browserClient(), [client]);
  const [load, setLoad] = useState<LoadState>({ status: "loading" });
  const [selected, setSelected] = useState("");
  const [submission, setSubmission] = useState<SubmitState>({
    status: "idle",
  });
  const submissionId = useRef<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    setLoad({ status: "loading" });
    setSelected("");
    setSubmission({ status: "idle" });
    submissionId.current = null;

    async function loadKnowledgeCheck() {
      try {
        const completionResponse = await api.GET(
          "/api/v1/curriculum/placements/{placement_id}/completion",
          {
            params: { path: { placement_id: placementId } },
            signal: controller.signal,
          },
        );
        if (controller.signal.aborted) {
          return;
        }
        if (
          completionResponse.response.status === 401 ||
          completionResponse.response.status === 403
        ) {
          setLoad({ status: "denied", stage: "completion" });
          return;
        }
        if (
          completionResponse.response.status !== 200 ||
          !completionResponse.data
        ) {
          setLoad({ status: "unavailable", stage: "completion" });
          return;
        }
        const completion =
          completionResponse.data as unknown as Completion;
        if (!safeCompletion(completion, placementId)) {
          setLoad({ status: "invalid", stage: "completion" });
          return;
        }
        if (completion.completed) {
          setLoad({ status: "completed", completion });
          return;
        }

        const presentationResponse = await api.GET(
          "/api/v1/curriculum/placements/{placement_id}/knowledge-check",
          {
            params: { path: { placement_id: placementId } },
            signal: controller.signal,
          },
        );
        if (controller.signal.aborted) {
          return;
        }
        if (
          presentationResponse.response.status === 401 ||
          presentationResponse.response.status === 403
        ) {
          setLoad({ status: "denied", stage: "knowledge-check" });
        } else if (
          presentationResponse.response.status === 200 &&
          presentationResponse.data
        ) {
          const presentation =
            presentationResponse.data as unknown as Presentation;
          setLoad(
            safePresentation(presentation)
              ? { status: "ready", presentation }
              : { status: "invalid", stage: "knowledge-check" },
          );
        } else if (presentationResponse.response.status === 400) {
          setLoad({ status: "invalid", stage: "knowledge-check" });
        } else {
          setLoad({ status: "unavailable", stage: "knowledge-check" });
        }
      } catch {
        if (!controller.signal.aborted) {
          setLoad({ status: "unavailable", stage: "completion" });
        }
      }
    }

    void loadKnowledgeCheck();
    return () => controller.abort();
  }, [api, placementId]);

  if (load.status === "loading") {
    return (
      <section aria-live="polite" className="knowledge-check-card">
        <p role="status">Checking retained completion evidence…</p>
      </section>
    );
  }
  if (load.status === "completed") {
    return <RetainedCompletion completion={load.completion} />;
  }
  if (load.status !== "ready") {
    const subject =
      load.stage === "completion" ? "completion record" : "knowledge check";
    const copy = {
      denied: `Your learner session cannot open this ${subject}.`,
      invalid: `This ${subject} did not pass the safe presentation checks.`,
      unavailable: `The exact ${subject} is temporarily unavailable.`,
    }[load.status];
    return (
      <section
        aria-labelledby="knowledge-check-status"
        className="knowledge-check-card knowledge-check-card--warning"
      >
        <h2 id="knowledge-check-status">
          {load.stage === "completion"
            ? "Completion record unavailable"
            : "Knowledge check unavailable"}
        </h2>
        <p>{copy} Your learning record was not changed.</p>
      </section>
    );
  }

  const presentation = load.presentation;

  async function submit() {
    if (!selected || submission.status === "submitting") {
      return;
    }
    const stableId = submissionId.current ?? crypto.randomUUID();
    submissionId.current = stableId;
    setSubmission({ status: "submitting" });
    try {
      const response = await api.POST(
        "/api/v1/curriculum/placements/{placement_id}/knowledge-check/submissions",
        {
          params: { path: { placement_id: placementId } },
          body: {
            schema_version: "1.0.0",
            submission_id: stableId,
            placement_id: presentation.placement_id,
            package_id: presentation.package_id,
            package_version: presentation.package_version,
            package_digest: presentation.package_digest,
            assessment_id: presentation.assessment_id,
            assessment_version: presentation.assessment_version,
            definition_digest: presentation.definition_digest,
            item_id: presentation.item_id,
            item_version: presentation.item_version,
            scoring_policy_id: presentation.scoring_policy_id,
            scoring_policy_version: presentation.scoring_policy_version,
            selected_option_id: selected,
          },
        },
      );
      if (response.response.status === 200 && response.data) {
        setSubmission({ status: "result", result: response.data });
      } else if (
        response.response.status === 401 ||
        response.response.status === 403
      ) {
        setSubmission({ status: "denied" });
      } else if (response.response.status === 409) {
        setSubmission({ status: "conflict" });
      } else {
        setSubmission({ status: "unavailable" });
      }
    } catch {
      setSubmission({ status: "unavailable" });
    }
  }

  const completed = submission.status === "result";

  return (
    <section
      aria-labelledby="knowledge-check-title"
      className="knowledge-check-card"
    >
      <p className="eyebrow">Check your understanding</p>
      <h2 id="knowledge-check-title">Knowledge check</h2>
      <form
        onSubmit={(event) => {
          event.preventDefault();
          void submit();
        }}
      >
        <fieldset disabled={completed || submission.status === "submitting"}>
          <legend>{presentation.prompt}</legend>
          <div className="knowledge-check-options">
            {presentation.options.map((option) => (
              <label key={option.option_id}>
                <input
                  checked={selected === option.option_id}
                  name="knowledge-check-answer"
                  onChange={() => {
                    setSelected(option.option_id);
                    setSubmission({ status: "idle" });
                    submissionId.current = null;
                  }}
                  type="radio"
                  value={option.option_id}
                />
                <span>{option.label}</span>
              </label>
            ))}
          </div>
        </fieldset>
        <button
          disabled={!selected || completed || submission.status === "submitting"}
          type="submit"
        >
          {submission.status === "submitting"
            ? "Checking answer…"
            : "Check answer"}
        </button>
      </form>

      <div aria-atomic="true" aria-live="polite">
        {submission.status === "result" ? (
          <section
            className={
              submission.result.correct
                ? "knowledge-check-feedback knowledge-check-feedback--success"
                : "knowledge-check-feedback knowledge-check-feedback--review"
            }
          >
            <h3>
              {submission.result.correct
                ? "Knowledge check complete"
                : "Review the concept"}
            </h3>
            <p>{submission.result.feedback.text}</p>
            <p>
              Score: {submission.result.score} of {submission.result.max_score}.
              This records this bounded check, not mastery or certification.
            </p>
          </section>
        ) : null}
        {submission.status === "conflict" ? (
          <p className="knowledge-check-message" role="alert">
            This submission no longer matches the exact knowledge check. Reload
            the lesson before trying again.
          </p>
        ) : null}
        {submission.status === "denied" ? (
          <p className="knowledge-check-message" role="alert">
            Your learner session cannot submit this knowledge check. No result
            was recorded.
          </p>
        ) : null}
        {submission.status === "unavailable" ? (
          <p className="knowledge-check-message" role="alert">
            The answer could not be recorded. Try again to safely reuse this
            submission without creating duplicate evidence.
          </p>
        ) : null}
      </div>
    </section>
  );
}

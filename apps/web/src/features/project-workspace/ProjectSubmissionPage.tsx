import { useEffect, useRef, useState } from "react";
import { Form, Link } from "react-router";

import type {
  ProjectActivityCompletion,
  ProjectCompletionEvidence,
  ProjectCompletionHistory,
  ProjectLearningActionState,
  ProjectLearningSelection,
  ProjectShell,
  ProjectSubmissionCandidate,
} from "./model";
import { readableProjectDate } from "./model";

function resourceLabel(resource: ProjectSubmissionCandidate["resources"][number], index: number) {
  const kind = resource.resource_kind === "artifact"
    ? "file"
    : resource.resource_kind === "source"
      ? "source"
      : resource.resource_kind === "note"
        ? "note"
        : "connected record";
  return `${kind} ${index + 1}`;
}

function SubmissionError({ state }: { state: ProjectLearningActionState }) {
  const heading = useRef<HTMLHeadingElement>(null);
  useEffect(() => { heading.current?.focus(); }, [state]);
  const message = state.kind === "refused"
    ? "Your checkpoint was not added to your learning record. Review the points below and try again."
    : state.kind === "invalid-input"
      ? "Choose at least one saved item for every milestone, then try again."
      : state.kind === "conflict"
        ? "The checkpoint changed while this request was being checked. Return to the Project and save a new checkpoint."
        : state.kind === "not-found"
          ? "This checkpoint is no longer available."
          : state.kind === "forbidden"
            ? "This learner profile cannot add Project learning evidence."
            : state.kind === "unauthorized"
              ? "Your private learner view could not be renewed."
              : state.kind === "invalid-response"
                ? "The response did not pass its safety checks, so nothing was shown as accepted."
                : "The request could not be confirmed. Your unchanged retry uses the same request number.";
  return <section aria-labelledby="project-submission-error" className="project-form-error" role="alert">
    <h2 id="project-submission-error" ref={heading} tabIndex={-1}>Checkpoint not submitted</h2>
    <p>{message}</p>
    {state.issues?.length ? <ul>{state.issues.map((issue) => <li key={`${issue.code}:${issue.reference}`}>{issue.message}</li>)}</ul> : null}
  </section>;
}

function CompletionSummary({ completion }: { completion: ProjectActivityCompletion }) {
  return <section aria-labelledby="project-completion-heading" className="project-section">
    <div><p className="eyebrow">Learning record</p><h2 id="project-completion-heading">Project learning status</h2></div>
    <p className="project-empty">{completion.completed
      ? "At least one checkpoint has been accepted as evidence that you completed this Project activity. This does not grade the quality of the work or show mastery."
      : "No checkpoint has been accepted for this Project activity yet."}</p>
    <details><summary>Technical record</summary><dl className="project-technical">
      <div><dt>Meaning</dt><dd><code>{completion.completion_meaning}</code></dd></div>
      <div><dt>Projection fingerprint</dt><dd><code>{completion.source_digest}</code></dd></div>
      <div><dt>Rebuilt</dt><dd><time dateTime={completion.rebuilt_at}>{completion.rebuilt_at}</time></dd></div>
    </dl></details>
  </section>;
}

function History({ history, projectId }: { history: ProjectCompletionHistory; projectId: string }) {
  return <section aria-labelledby="project-submission-history" className="project-section">
    <div><p className="eyebrow">Earlier submissions</p><h2 id="project-submission-history">Accepted checkpoints</h2></div>
    {history.items.length === 0 ? <p className="project-empty">No checkpoints have been accepted for learning yet.</p> : <ol className="project-work-list">
      {history.items.map((item) => <li className="project-panel" key={item.submission_id}>
        <h3>Accepted {readableProjectDate(item.submitted_at)}</h3>
        <p>{item.supersedes_submission_id ? "This submission replaces an earlier accepted checkpoint." : "This is an accepted Project checkpoint."}</p>
        <Link className="button button--secondary" to={`/projects/${encodeURIComponent(projectId)}/learning?submission=${encodeURIComponent(item.submission_id)}`}>Open submitted evidence</Link>
      </li>)}
    </ol>}
  </section>;
}

function CandidateForm({
  actionState,
  busy,
  candidate,
  submissionId,
}: {
  actionState: ProjectLearningActionState | undefined;
  busy: boolean;
  candidate: ProjectSubmissionCandidate;
  submissionId: string;
}) {
  const [requestId, setRequestId] = useState(actionState?.submissionId ?? submissionId);
  const [selected, setSelected] = useState(() => new Set(actionState?.selections ?? []));
  useEffect(() => {
    setRequestId(actionState?.submissionId ?? submissionId);
    setSelected(new Set(actionState?.selections ?? []));
  }, [actionState, submissionId]);
  function changeSelection(value: string, checked: boolean) {
    const next = new Set(selected);
    if (checked) next.add(value); else next.delete(value);
    setSelected(next);
    if (actionState) {
      const original = new Set(actionState.selections);
      const unchanged = original.size === next.size && [...original].every((item) => next.has(item));
      setRequestId(unchanged ? actionState.submissionId : crypto.randomUUID().toLowerCase());
    }
  }
  return <section aria-labelledby="project-submit-heading" className="project-section">
    <div><p className="eyebrow">Submit for learning</p><h2 id="project-submit-heading">Choose evidence for each milestone</h2><p>Choose only the saved items that support each milestone. The Academy checks the exact checkpoint again before accepting it.</p></div>
    {actionState ? <SubmissionError state={actionState} /> : null}
    <Form className="project-form" method="post">
      <input name="submission_id" type="hidden" value={requestId} />
      <fieldset disabled={busy}>
        <legend>Evidence choices</legend>
        {candidate.milestones.map((milestone) => <fieldset className="project-submission-milestone" key={milestone.milestone_id}>
          <legend>{milestone.sequence}. {milestone.title}</legend>
          <p className="project-form__help">Choose one or more saved items.</p>
          <div className="project-submission-options">
            {candidate.resources.map((resource, index) => {
              const value = `${milestone.milestone_id}:${index}`;
              return <label key={value}><input checked={selected.has(value)} name="selection" onChange={(event) => changeSelection(value, event.currentTarget.checked)} type="checkbox" value={value} /> <span>{resourceLabel(resource, index)}</span></label>;
            })}
          </div>
        </fieldset>)}
        <div className="project-form__actions"><button className="button project-button--primary" type="submit">Submit checkpoint</button></div>
      </fieldset>
    </Form>
    <details><summary>Technical record</summary><dl className="project-technical">
      <div><dt>Checkpoint ID</dt><dd><code>{candidate.project.snapshot_id}</code></dd></div>
      <div><dt>Checkpoint fingerprint</dt><dd><code>{candidate.project.snapshot_digest}</code></dd></div>
      <div><dt>Review policy</dt><dd><code>{candidate.policy_id}@{candidate.policy_version}</code></dd></div>
      <div><dt>Learning placement</dt><dd><code>{candidate.origin.placement_id}@{candidate.origin.placement_version}</code></dd></div>
    </dl></details>
  </section>;
}

function Evidence({ evidence }: { evidence: ProjectCompletionEvidence }) {
  return <section aria-labelledby="project-evidence-heading" className="project-section">
    <div><p className="eyebrow">Accepted evidence</p><h2 id="project-evidence-heading">Submitted checkpoint</h2></div>
    <p className="project-empty">This checkpoint was accepted as Project activity evidence. Acceptance does not grade its quality, show mastery, or provide financial advice.</p>
    <ol className="project-work-list">{evidence.milestone_evidence.map((milestone) => <li className="project-panel" key={milestone.milestone_id}>
      <h3>Milestone evidence</h3><p>{milestone.resources.length} saved {milestone.resources.length === 1 ? "item" : "items"} submitted.</p>
      <details><summary>Technical record</summary><dl className="project-technical">
        <div><dt>Milestone ID</dt><dd><code>{milestone.milestone_id}</code></dd></div>
        <div><dt>Resources</dt><dd><ul>{milestone.resources.map((resource, index) => <li key={`${resource.resource_kind}:${resource.resource_id}:${index}`}><code>{resource.resource_kind}:{resource.resource_id}</code></li>)}</ul></dd></div>
      </dl></details>
    </li>)}</ol>
    <details><summary>Submission technical record</summary><dl className="project-technical">
      <div><dt>Submission ID</dt><dd><code>{evidence.submission_id}</code></dd></div>
      <div><dt>Evidence ID</dt><dd><code>{evidence.evidence_id}</code></dd></div>
      <div><dt>Request fingerprint</dt><dd><code>{evidence.request_fingerprint}</code></dd></div>
      <div><dt>Submitted</dt><dd><time dateTime={evidence.submitted_at}>{evidence.submitted_at}</time></dd></div>
    </dl></details>
  </section>;
}

export function ProjectSubmissionPage({
  actionState,
  busy,
  candidate,
  completion,
  evidence,
  history,
  project,
  selection,
  submissionId,
}: {
  actionState: ProjectLearningActionState | undefined;
  busy: boolean;
  candidate: ProjectSubmissionCandidate | undefined;
  completion: ProjectActivityCompletion;
  evidence: ProjectCompletionEvidence | undefined;
  history: ProjectCompletionHistory;
  project: ProjectShell;
  selection: ProjectLearningSelection;
  submissionId: string;
}) {
  return <article className="project-page project-detail">
    <header className="project-page__header"><p className="eyebrow">Project learning evidence</p><h1>{project.title}</h1><p>Use a fixed checkpoint to show the work you completed for this learning Project.</p><Link to={`/projects/${encodeURIComponent(project.project_id)}`}>Return to Project</Link></header>
    <CompletionSummary completion={completion} />
    {selection.mode === "snapshot" && candidate ? <CandidateForm actionState={actionState} busy={busy} candidate={candidate} submissionId={submissionId} /> : null}
    {selection.mode === "submission" && evidence ? <Evidence evidence={evidence} /> : null}
    {selection.mode === "overview" ? <p className="project-empty">Open a saved checkpoint from the Project page when you are ready to submit it for learning.</p> : null}
    <History history={history} projectId={project.project_id} />
  </article>;
}

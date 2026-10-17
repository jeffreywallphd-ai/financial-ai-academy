import { useEffect, useRef, useState } from "react";
import { Form } from "react-router";

import {
  experienceLevelLabel,
  moveIdentifier,
  preferenceChangeLabel,
  type LearnerPreferenceHistory,
  type LearnerPreferenceMutation,
  type LearnerPreferenceProfile,
  type LearnerPreferencesActionState,
  type LearnerPreferencesExporter,
  type LearnerPreferencesExportOutcome,
} from "./model";


function requestKey() {
  return crypto.randomUUID();
}

function MutationFields({
  actionState,
  intent,
  mutation,
  revision,
}: {
  actionState: LearnerPreferencesActionState | undefined;
  intent: string;
  mutation: LearnerPreferenceMutation;
  revision: number;
}) {
  const [freshKey, setFreshKey] = useState(requestKey);
  const [retryAbandoned, setRetryAbandoned] = useState(false);
  const keyInput = useRef<HTMLInputElement>(null);
  const prepared = actionState?.intent === intent ? actionState.preparedRequest : undefined;
  const signature = JSON.stringify(mutation);
  const preparedSignature = prepared ? JSON.stringify(prepared.mutation) : undefined;
  const retryable = Boolean(
    prepared &&
    (actionState?.kind === "unavailable" ||
      actionState?.kind === "invalid-response" ||
      actionState?.kind === "unexpected"),
  );
  const usePrepared = Boolean(retryable && !retryAbandoned && signature === preparedSignature);
  useEffect(() => setRetryAbandoned(false), [prepared?.idempotency_key]);
  useEffect(() => {
    if (prepared && signature !== preparedSignature) setRetryAbandoned(true);
  }, [prepared, preparedSignature, signature]);
  useEffect(() => setFreshKey(requestKey()), [revision, actionState?.kind, prepared?.idempotency_key]);
  useEffect(() => {
    const form = keyInput.current?.form;
    if (!form) return undefined;
    const renew = () => queueMicrotask(() => setFreshKey(requestKey()));
    form.addEventListener("submit", renew);
    return () => form.removeEventListener("submit", renew);
  }, []);
  return (
    <>
      <input name="form_intent" type="hidden" value={intent} />
      <input name="idempotency_key" ref={keyInput} type="hidden" value={usePrepared && prepared ? prepared.idempotency_key : freshKey} />
      <input name="expected_revision" type="hidden" value={usePrepared && prepared ? prepared.expected_revision : revision} />
    </>
  );
}

function actionMessage(kind: LearnerPreferencesActionState["kind"]): { title: string; detail: string } {
  if (kind === "stale") return { title: "Preferences changed", detail: "Your learning preferences changed before this update finished. Refresh the page, review the current choices, and try again." };
  if (kind === "conflict") return { title: "Use a fresh request", detail: "That earlier request no longer matches this change. Review the fields and try again with the fresh request now prepared." };
  if (kind === "limit") return { title: "Preference limit reached", detail: "This profile already contains the maximum number of entries in that section. Remove one you no longer need, then try again." };
  if (kind === "unauthorized") return { title: "Learner session needed", detail: "We couldn't confirm your learner session. No private preferences were changed. Try again." };
  if (kind === "forbidden") return { title: "Learning preferences unavailable", detail: "This learner profile cannot make that preference change." };
  if (kind === "not-found") return { title: "Preference not found", detail: "That preference is no longer available. No other preferences were changed. Refresh the page to review the current profile." };
  if (kind === "invalid") return { title: "Check this change", detail: "One or more entries are missing or too long. Review the fields and try again." };
  if (kind === "invalid-response") return { title: "Saved result unavailable", detail: "We couldn't safely confirm the saved result, so no partial private details were shown. Reload this page before making another change." };
  if (kind === "unavailable") return { title: "Change not confirmed", detail: "We couldn't confirm whether this change finished. Keep the form unchanged and try the same request again, or reload the page to check." };
  return { title: "Change not completed", detail: "We couldn't complete this change safely. No technical or private details were shown. Reload this page, review the current preferences, and try again." };
}

function ActionNotice({ actionState }: { actionState: LearnerPreferencesActionState | undefined }) {
  const heading = useRef<HTMLHeadingElement>(null);
  useEffect(() => {
    if (actionState) heading.current?.focus();
  }, [actionState]);
  if (!actionState) return null;
  const message = actionMessage(actionState.kind);
  return (
    <section aria-live="assertive" className="preferences-alert" role="alert">
      <h2 ref={heading} tabIndex={-1}>{message.title}</h2>
      <p>{message.detail}</p>
    </section>
  );
}

function OrderControls({
  actionState,
  busy,
  ids,
  index,
  itemId,
  itemLabel,
  operation,
  revision,
}: {
  actionState: LearnerPreferencesActionState | undefined;
  busy: boolean;
  ids: readonly string[];
  index: number;
  itemId: string;
  itemLabel: string;
  operation: "reorder_goals" | "reorder_experience" | "reorder_interests";
  revision: number;
}) {
  return (
    <div aria-label="Change order" className="preferences-order" role="group">
      {(["up", "down"] as const).map((direction) => {
        const orderedIds = moveIdentifier(ids, itemId, direction);
        if (!orderedIds) return null;
        const intent = `${operation}-${direction}-${itemId}`;
        const mutation = { operation, ordered_ids: orderedIds } as LearnerPreferenceMutation;
        return (
          <Form key={direction} method="post">
            <MutationFields actionState={actionState} intent={intent} mutation={mutation} revision={revision} />
            <input name="operation" type="hidden" value={operation} />
            {orderedIds.map((id) => <input key={id} name="ordered_ids" type="hidden" value={id} />)}
            <button aria-label={`Move ${itemLabel} ${direction}`} className="button button--quiet" disabled={busy} type="submit">
              Move {direction}
              <span className="visually-hidden"> item {index + 1}</span>
            </button>
          </Form>
        );
      })}
    </div>
  );
}

function GoalForm({
  actionState,
  busy,
  goal,
  revision,
}: {
  actionState: LearnerPreferencesActionState | undefined;
  busy: boolean;
  goal?: LearnerPreferenceProfile["goals"][number];
  revision: number;
}) {
  const [title, setTitle] = useState(goal?.title ?? "");
  const [detail, setDetail] = useState(goal?.detail ?? "");
  const intent = goal ? `update-goal-${goal.goal_id}` : "create-goal";
  const mutation: LearnerPreferenceMutation = goal
    ? { operation: "update_goal", entry_id: goal.goal_id, title, detail: detail || null }
    : { operation: "create_goal", title, detail: detail || null };
  const operation = mutation.operation;
  return (
    <Form className="preferences-form" method="post">
      <MutationFields actionState={actionState} intent={intent} mutation={mutation} revision={revision} />
      <input name="operation" type="hidden" value={operation} />
      {goal ? <input name="entry_id" type="hidden" value={goal.goal_id} /> : null}
      <label>
        <span>Goal</span>
        <input maxLength={160} name="title" onChange={(event) => setTitle(event.target.value)} required value={title} />
      </label>
      <label>
        <span>Why this matters to you <small>(optional)</small></span>
        <textarea maxLength={2000} name="detail" onChange={(event) => setDetail(event.target.value)} rows={goal ? 3 : 4} value={detail} />
      </label>
      <button className="button preferences-button--primary" disabled={busy} type="submit">{goal ? "Save goal" : "Add goal"}</button>
    </Form>
  );
}

function ExperienceForm({
  actionState,
  busy,
  entry,
  revision,
}: {
  actionState: LearnerPreferencesActionState | undefined;
  busy: boolean;
  entry?: LearnerPreferenceProfile["experience"][number];
  revision: number;
}) {
  const [subject, setSubject] = useState(entry?.subject ?? "");
  const [level, setLevel] = useState<LearnerPreferenceProfile["experience"][number]["level"]>(entry?.level ?? "new");
  const [detail, setDetail] = useState(entry?.detail ?? "");
  const intent = entry ? `update-experience-${entry.experience_id}` : "create-experience";
  const mutation: LearnerPreferenceMutation = entry
    ? { operation: "update_experience", entry_id: entry.experience_id, subject, level, detail: detail || null }
    : { operation: "create_experience", subject, level, detail: detail || null };
  const operation = mutation.operation;
  return (
    <Form className="preferences-form" method="post">
      <MutationFields actionState={actionState} intent={intent} mutation={mutation} revision={revision} />
      <input name="operation" type="hidden" value={operation} />
      {entry ? <input name="entry_id" type="hidden" value={entry.experience_id} /> : null}
      <label>
        <span>Topic or skill</span>
        <input maxLength={120} name="subject" onChange={(event) => setSubject(event.target.value)} required value={subject} />
      </label>
      <label>
        <span>Your experience</span>
        <select name="level" onChange={(event) => setLevel(event.target.value as typeof level)} value={level}>
          <option value="new">New to this topic</option>
          <option value="some_experience">Some experience</option>
          <option value="experienced">Experienced</option>
        </select>
      </label>
      <label>
        <span>What you have done <small>(optional)</small></span>
        <textarea maxLength={1000} name="detail" onChange={(event) => setDetail(event.target.value)} rows={3} value={detail} />
      </label>
      <button className="button preferences-button--primary" disabled={busy} type="submit">{entry ? "Save experience" : "Add experience"}</button>
    </Form>
  );
}

function InterestForm({
  actionState,
  busy,
  entry,
  revision,
}: {
  actionState: LearnerPreferencesActionState | undefined;
  busy: boolean;
  entry?: LearnerPreferenceProfile["interests"][number];
  revision: number;
}) {
  const [label, setLabel] = useState(entry?.label ?? "");
  const intent = entry ? `rename-interest-${entry.interest_id}` : "create-interest";
  const mutation: LearnerPreferenceMutation = entry
    ? { operation: "rename_interest", entry_id: entry.interest_id, label }
    : { operation: "create_interest", label };
  const operation = mutation.operation;
  return (
    <Form className="preferences-form preferences-form--inline" method="post">
      <MutationFields actionState={actionState} intent={intent} mutation={mutation} revision={revision} />
      <input name="operation" type="hidden" value={operation} />
      {entry ? <input name="entry_id" type="hidden" value={entry.interest_id} /> : null}
      <label>
        <span>{entry ? "Interest" : "Add an interest"}</span>
        <input maxLength={120} name="label" onChange={(event) => setLabel(event.target.value)} required value={label} />
      </label>
      <button className="button preferences-button--primary" disabled={busy} type="submit">{entry ? "Save interest" : "Add interest"}</button>
    </Form>
  );
}

function ItemMutationForm({
  actionState,
  busy,
  entryId,
  intent,
  label,
  operation,
  revision,
  targetLabel,
}: {
  actionState: LearnerPreferencesActionState | undefined;
  busy: boolean;
  entryId: string;
  intent: string;
  label: string;
  operation: "archive_goal" | "restore_goal" | "remove_goal" | "remove_experience" | "remove_interest";
  revision: number;
  targetLabel: string;
}) {
  const [removeConfirmed, setRemoveConfirmed] = useState(false);
  const mutation = { operation, entry_id: entryId } as LearnerPreferenceMutation;
  const removesEntry = operation.startsWith("remove");
  return (
    <Form method="post">
      <MutationFields actionState={actionState} intent={intent} mutation={mutation} revision={revision} />
      <input name="operation" type="hidden" value={operation} />
      <input name="entry_id" type="hidden" value={entryId} />
      {removesEntry ? (
        <label>
          <input
            checked={removeConfirmed}
            name="confirm_remove"
            onChange={(event) => setRemoveConfirmed(event.target.checked)}
            required
            type="checkbox"
            value="remove"
          />
          {` I understand that removing “${targetLabel}” permanently removes this wording from my learning preferences.`}
        </label>
      ) : null}
      <button
        aria-label={`${label}: ${targetLabel}`}
        className={removesEntry ? "button preferences-button--danger" : "button button--quiet"}
        disabled={busy || (removesEntry && !removeConfirmed)}
        type="submit"
      >{label}</button>
    </Form>
  );
}

function startDownload(content: string, fileName: string) {
  const url = URL.createObjectURL(new Blob([content], { type: "application/json" }));
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = fileName;
  anchor.click();
  URL.revokeObjectURL(url);
}

function ExportNotice({ outcome }: { outcome: LearnerPreferencesExportOutcome | null }) {
  if (!outcome) return null;
  const message = outcome.status === "ready"
    ? "Your learning-preferences download is ready."
    : outcome.status === "changed"
      ? "Your preferences changed while the download was prepared. Refresh this page and try again."
      : outcome.status === "invalid-response"
        ? "The download did not pass its integrity check, so it was not saved."
        : outcome.status === "unauthorized" || outcome.status === "forbidden"
          ? "Your private learner access could not be confirmed. The download was not saved."
          : "The download is temporarily unavailable. Try again.";
  return <p aria-live="polite" className={outcome.status === "ready" ? "preferences-result" : "preferences-alert"} role="status">{message}</p>;
}

function History({ history }: { history: LearnerPreferenceHistory }) {
  return (
    <section className="preferences-section" aria-labelledby="preference-history-heading">
      <h2 id="preference-history-heading">Recent changes</h2>
      <p>This list records what kind of change you made. It does not keep old copies of your private wording.</p>
      {history.changes.length === 0 ? <p className="preferences-empty">You have not changed these preferences yet.</p> : (
        <ol className="preferences-history">
          {[...history.changes].reverse().map((change) => (
            <li key={change.revision}>
              <strong>{preferenceChangeLabel(change.operation)}</strong>
              <span><time dateTime={change.occurred_at}>{new Date(change.occurred_at).toLocaleString()}</time></span>
              <details>
                <summary>Technical record</summary>
                <dl className="preferences-technical">
                  <div><dt>Result revision</dt><dd>{change.revision}</dd></div>
                  <div><dt>Change type</dt><dd><code>{change.operation}</code></dd></div>
                  {change.object_id ? <div><dt>Item identifier</dt><dd><code>{change.object_id}</code></dd></div> : null}
                  <div><dt>Result integrity code</dt><dd><code>{change.resulting_profile_digest}</code></dd></div>
                </dl>
              </details>
            </li>
          ))}
        </ol>
      )}
    </section>
  );
}

export function LearnerPreferencesPage({
  actionState,
  busy,
  exportPreferences,
  history,
  profile,
}: {
  actionState: LearnerPreferencesActionState | undefined;
  busy: boolean;
  exportPreferences: LearnerPreferencesExporter;
  history: LearnerPreferenceHistory;
  profile: LearnerPreferenceProfile;
}) {
  const [exporting, setExporting] = useState(false);
  const [exportOutcome, setExportOutcome] = useState<LearnerPreferencesExportOutcome | null>(null);
  const goalIds = profile.goals.map((goal) => goal.goal_id);
  const experienceIds = profile.experience.map((entry) => entry.experience_id);
  const interestIds = profile.interests.map((entry) => entry.interest_id);
  const download = async () => {
    setExporting(true);
    const outcome = await exportPreferences(profile.revision, profile.profile_digest);
    if (outcome.status === "ready") startDownload(outcome.content, outcome.fileName);
    setExportOutcome(outcome);
    setExporting(false);
  };
  return (
    <article className="preferences-page">
      <header className="preferences-page__header">
        <p className="eyebrow">Your learning</p>
        <h1>Learning preferences</h1>
        <p>Record what you want to learn, how you describe your experience, and what interests you.</p>
      </header>

      <aside className="preferences-purpose" aria-label="How these preferences are used">
        <h2>You stay in control</h2>
        <p>These are your own statements. They are not proof of competency or financial suitability, and they do not change your access to learning activities.</p>
      </aside>
      <ActionNotice actionState={actionState} />

      <section className="preferences-section" aria-labelledby="goals-heading">
        <div className="preferences-section__heading"><div><h2 id="goals-heading">Learning goals</h2><p>Add up to 20 goals and keep them in the order that matters to you.</p></div><span>{profile.goals.length} of 20</span></div>
        <GoalForm actionState={actionState} busy={busy} revision={profile.revision} />
        {profile.goals.length === 0 ? <p className="preferences-empty">You have not added a learning goal yet.</p> : (
          <ol className="preferences-list">
            {profile.goals.map((goal, index) => (
              <li className={goal.archived ? "preferences-card preferences-card--muted" : "preferences-card"} key={goal.goal_id}>
                <div className="preferences-card__heading"><div><h3>{goal.title}</h3>{goal.archived ? <strong className="preferences-status">Archived</strong> : null}</div><OrderControls actionState={actionState} busy={busy} ids={goalIds} index={index} itemId={goal.goal_id} itemLabel={goal.title} operation="reorder_goals" revision={profile.revision} /></div>
                {goal.detail ? <p>{goal.detail}</p> : <p className="preferences-muted">No additional detail.</p>}
                <details><summary aria-label={`Edit goal: ${goal.title}`}>Edit goal</summary><GoalForm actionState={actionState} busy={busy} goal={goal} revision={profile.revision} /></details>
                <div className="preferences-actions">
                  <ItemMutationForm actionState={actionState} busy={busy} entryId={goal.goal_id} intent={`${goal.archived ? "restore" : "archive"}-goal-${goal.goal_id}`} label={goal.archived ? "Restore goal" : "Archive goal"} operation={goal.archived ? "restore_goal" : "archive_goal"} revision={profile.revision} targetLabel={goal.title} />
                  <ItemMutationForm actionState={actionState} busy={busy} entryId={goal.goal_id} intent={`remove-goal-${goal.goal_id}`} label="Remove goal" operation="remove_goal" revision={profile.revision} targetLabel={goal.title} />
                </div>
                <details><summary>Technical record</summary><dl className="preferences-technical"><div><dt>Goal identifier</dt><dd><code>{goal.goal_id}</code></dd></div><div><dt>Last updated</dt><dd><time dateTime={goal.updated_at}>{goal.updated_at}</time></dd></div></dl></details>
              </li>
            ))}
          </ol>
        )}
      </section>

      <section className="preferences-section" aria-labelledby="experience-heading">
        <div className="preferences-section__heading"><div><h2 id="experience-heading">Your experience</h2><p>Describe your experience in your own words. This is not a competency assessment.</p></div><span>{profile.experience.length} of 20</span></div>
        <ExperienceForm actionState={actionState} busy={busy} revision={profile.revision} />
        {profile.experience.length === 0 ? <p className="preferences-empty">You have not described any experience yet.</p> : (
          <ol className="preferences-list">
            {profile.experience.map((entry, index) => (
              <li className="preferences-card" key={entry.experience_id}>
                <div className="preferences-card__heading"><div><h3>{entry.subject}</h3><strong className="preferences-status">{experienceLevelLabel(entry.level)}</strong></div><OrderControls actionState={actionState} busy={busy} ids={experienceIds} index={index} itemId={entry.experience_id} itemLabel={entry.subject} operation="reorder_experience" revision={profile.revision} /></div>
                {entry.detail ? <p>{entry.detail}</p> : <p className="preferences-muted">No additional detail.</p>}
                <details><summary aria-label={`Edit experience: ${entry.subject}`}>Edit experience</summary><ExperienceForm actionState={actionState} busy={busy} entry={entry} revision={profile.revision} /></details>
                <div className="preferences-actions"><ItemMutationForm actionState={actionState} busy={busy} entryId={entry.experience_id} intent={`remove-experience-${entry.experience_id}`} label="Remove experience" operation="remove_experience" revision={profile.revision} targetLabel={entry.subject} /></div>
                <details><summary>Technical record</summary><dl className="preferences-technical"><div><dt>Experience identifier</dt><dd><code>{entry.experience_id}</code></dd></div><div><dt>Last updated</dt><dd><time dateTime={entry.updated_at}>{entry.updated_at}</time></dd></div></dl></details>
              </li>
            ))}
          </ol>
        )}
      </section>

      <section className="preferences-section" aria-labelledby="interests-heading">
        <div className="preferences-section__heading"><div><h2 id="interests-heading">Interests</h2><p>Add topics you would like to explore. They do not create a recommendation by themselves.</p></div><span>{profile.interests.length} of 50</span></div>
        <InterestForm actionState={actionState} busy={busy} revision={profile.revision} />
        {profile.interests.length === 0 ? <p className="preferences-empty">You have not added an interest yet.</p> : (
          <ol className="preferences-list preferences-list--compact">
            {profile.interests.map((entry, index) => (
              <li className="preferences-card" key={entry.interest_id}>
                <div className="preferences-card__heading"><h3>{entry.label}</h3><OrderControls actionState={actionState} busy={busy} ids={interestIds} index={index} itemId={entry.interest_id} itemLabel={entry.label} operation="reorder_interests" revision={profile.revision} /></div>
                <details><summary aria-label={`Edit interest: ${entry.label}`}>Edit interest</summary><InterestForm actionState={actionState} busy={busy} entry={entry} revision={profile.revision} /></details>
                <div className="preferences-actions"><ItemMutationForm actionState={actionState} busy={busy} entryId={entry.interest_id} intent={`remove-interest-${entry.interest_id}`} label="Remove interest" operation="remove_interest" revision={profile.revision} targetLabel={entry.label} /></div>
                <details><summary>Technical record</summary><dl className="preferences-technical"><div><dt>Interest identifier</dt><dd><code>{entry.interest_id}</code></dd></div><div><dt>Last updated</dt><dd><time dateTime={entry.updated_at}>{entry.updated_at}</time></dd></div></dl></details>
              </li>
            ))}
          </ol>
        )}
      </section>

      <History history={history} />

      <section className="preferences-section preferences-section--management" aria-labelledby="preference-record-heading">
        <h2 id="preference-record-heading">Your preference record</h2>
        <p>Download the current profile and recent change history, or reset only these preferences. Resetting does not remove completed learning, saved work, or project evidence.</p>
        <div className="preferences-actions">
          <button className="button preferences-button--primary" disabled={exporting} onClick={() => void download()} type="button">{exporting ? "Preparing download…" : "Download preferences"}</button>
          <Form className="preferences-reset" method="post">
            <MutationFields actionState={actionState} intent="reset-profile" mutation={{ operation: "reset_profile" }} revision={profile.revision} />
            <input name="operation" type="hidden" value="reset_profile" />
            <label><input name="confirm_reset" required type="checkbox" value="reset" /> I understand that this removes all goals, experience, and interests from this profile.</label>
            <button className="button preferences-button--danger" disabled={busy} type="submit">Reset learning preferences</button>
          </Form>
        </div>
        <ExportNotice outcome={exportOutcome} />
        <details>
          <summary>Technical record</summary>
          <dl className="preferences-technical">
            <div><dt>Data format version</dt><dd><code>{profile.schema_version}</code></dd></div>
            <div><dt>Profile identifier</dt><dd><code>{profile.profile_id}</code></dd></div>
            <div><dt>Profile revision</dt><dd>{profile.revision}</dd></div>
            <div><dt>Profile integrity code</dt><dd><code>{profile.profile_digest}</code></dd></div>
            <div><dt>Created</dt><dd><time dateTime={profile.created_at}>{profile.created_at}</time></dd></div>
            <div><dt>Last updated</dt><dd><time dateTime={profile.updated_at}>{profile.updated_at}</time></dd></div>
          </dl>
        </details>
      </section>
    </article>
  );
}

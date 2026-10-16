import { useState } from "react";
import { Form, Link, useNavigation } from "react-router";

import type { LearningProjectStartOption, ProjectCreateActionState } from "./model";

function errorMessage(kind: ProjectCreateActionState["kind"]): string {
  if (kind === "invalid-input") return "Check the Project title and purpose, then try again.";
  if (kind === "unauthorized") return "A private learner session is required. Try again.";
  if (kind === "forbidden") return "This learner profile cannot create a Project.";
  if (kind === "invalid-response") return "The Project response did not pass its safety checks.";
  if (kind === "unavailable") return "The Project could not be created right now. Your unchanged retry will not create a duplicate.";
  return "The Project could not be completed safely. Try again.";
}

export function ProjectCreatePage({ actionState, idempotencyKey: initialKey, option }: {
  actionState: ProjectCreateActionState | undefined;
  idempotencyKey: string;
  option: LearningProjectStartOption | null;
}) {
  const [idempotencyKey, setIdempotencyKey] = useState(actionState?.idempotencyKey ?? initialKey);
  const navigation = useNavigation();
  const submitting = navigation.state === "submitting";
  return (
    <section className="project-page project-create">
      <header className="project-page__header">
        <p className="eyebrow">New Project</p>
        <h1>{option ? `Start ${option.title}` : "Create an independent Project"}</h1>
        <p>{option ? option.purpose : "Give your Project a clear title and purpose. You can connect more resources in later development stages."}</p>
      </header>
      {actionState ? <div aria-live="assertive" className="project-form-error" role="alert"><strong>Project not created</strong><p>{errorMessage(actionState.kind)}</p></div> : null}
      <Form
        className="project-form"
        method="post"
        onChange={() => {
          if (actionState?.idempotencyKey === idempotencyKey) setIdempotencyKey(crypto.randomUUID().toLowerCase());
        }}
      >
        <input name="placement_id" type="hidden" value={option?.origin.placement_id ?? ""} />
        <input name="idempotency_key" type="hidden" value={idempotencyKey} />
        <label htmlFor="project-title">Project title</label>
        <input autoComplete="off" defaultValue={actionState?.draft?.title ?? option?.title ?? ""} id="project-title" maxLength={120} minLength={1} name="title" required />
        <label htmlFor="project-charter">What do you want this Project to accomplish?</label>
        <textarea defaultValue={actionState?.draft?.charter ?? ""} id="project-charter" maxLength={4000} minLength={1} name="charter" required rows={7} />
        <p className="project-form__help">Describe the result you want to produce. Do not include passwords, account numbers, or other private financial information.</p>
        {option ? <details><summary>Technical record</summary><dl className="project-technical"><div><dt>Learning placement</dt><dd><code>{option.origin.placement_id}@{option.origin.placement_version}</code></dd></div><div><dt>Brief digest</dt><dd><code>{option.origin.brief_digest}</code></dd></div></dl></details> : null}
        <div className="project-form__actions">
          <button className="button project-button--primary" disabled={submitting} type="submit">{submitting ? "Creating Project…" : "Create Project"}</button>
          <Link className="button button--secondary" to="/projects">Cancel</Link>
        </div>
      </Form>
    </section>
  );
}

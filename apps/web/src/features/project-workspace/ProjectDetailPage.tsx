import { useMemo, useState, type ReactNode } from "react";
import { Form, Link } from "react-router";

import type {
  ProjectArtifact,
  ProjectDownloadOutcome,
  ProjectExportOutcome,
  ProjectShell,
  ProjectSnapshot,
  ProjectWorkspace,
  ProjectWorkspaceActionState,
} from "./model";
import { readableProjectDate } from "./model";

type ArtifactDownloader = (projectId: string, artifact: ProjectArtifact) => Promise<ProjectDownloadOutcome>;
type SnapshotExporter = (projectId: string, snapshotId: string) => Promise<ProjectExportOutcome>;

function requestKey() {
  return crypto.randomUUID().toLowerCase();
}

function IntentForm({
  busy,
  children,
  className = "project-form",
  intent,
  projectRevision,
  workspaceRevision,
}: {
  busy: boolean;
  children: ReactNode;
  className?: string;
  intent: "add-note" | "replace-note" | "add-reference" | "replace-reference" | "add-artifact" | "close-snapshot";
  projectRevision?: number;
  workspaceRevision: number;
}) {
  const [editVersion, setEditVersion] = useState(0);
  const key = useMemo(requestKey, [editVersion, intent, projectRevision, workspaceRevision]);
  return (
    <Form className={className} encType="multipart/form-data" method="post" onChange={() => setEditVersion((current) => current + 1)}>
      <input name="intent" type="hidden" value={intent} />
      <input name="idempotency_key" type="hidden" value={key} />
      <input name="expected_workspace_revision" type="hidden" value={workspaceRevision} />
      {projectRevision === undefined ? null : <input name="expected_project_revision" type="hidden" value={projectRevision} />}
      <fieldset disabled={busy}>{children}</fieldset>
    </Form>
  );
}

function ActionProblem({ state }: { state: ProjectWorkspaceActionState | undefined }) {
  if (!state) return null;
  const message = state.kind === "stale"
    ? "This Project changed before your work was saved. Your earlier work is still protected. Reload the current Project, review it, and try again."
    : state.kind === "conflict"
      ? "This request no longer matches the saved retry. Your current Project was not overwritten. Change the form to start a fresh request."
      : state.kind === "invalid-input"
        ? "Some information could not be accepted. Nothing was saved. Check the form and try again."
        : state.kind === "unauthorized" || state.kind === "forbidden"
          ? "Your private learner access could not be confirmed. No Project information was changed."
          : state.kind === "not-found"
            ? "This Project item is no longer available. Nothing was changed."
            : state.kind === "invalid-response"
              ? "The saved response did not pass its safety checks, so it was not displayed. Reload the Project before trying again."
              : "The request could not be completed right now. Nothing was changed. An unchanged retry will not create a duplicate.";
  return <div aria-live="polite" className="project-form-error" role="alert"><h2>Work not saved</h2><p>{message}</p></div>;
}

function NoteForm({ busy, note, workspaceRevision }: {
  busy: boolean;
  note?: ProjectWorkspace["notes"][number];
  workspaceRevision: number;
}) {
  return (
    <IntentForm busy={busy} intent={note ? "replace-note" : "add-note"} workspaceRevision={workspaceRevision}>
      <legend>{note ? "Edit note" : "Add a note"}</legend>
      {note ? <><input name="note_id" type="hidden" value={note.note_id} /><input name="note_version" type="hidden" value={note.note_version} /></> : null}
      <label htmlFor={`note-title-${note?.note_id ?? "new"}`}>Note title</label>
      <input defaultValue={note?.title} id={`note-title-${note?.note_id ?? "new"}`} maxLength={120} name="title" required />
      <label htmlFor={`note-body-${note?.note_id ?? "new"}`}>Note</label>
      <textarea defaultValue={note?.body} id={`note-body-${note?.note_id ?? "new"}`} maxLength={20000} name="body" required rows={5} />
      <div className="project-form__actions"><button className="button project-button--primary" type="submit">{note ? "Save note changes" : "Save note"}</button></div>
    </IntentForm>
  );
}

function OptionalSourceFields({ reference }: { reference: ProjectWorkspace["references"][number] | undefined }) {
  const suffix = reference?.reference_id ?? "new";
  return <details className="project-form__details"><summary>Add version, license, or usage details</summary><div className="project-form__detail-fields">
    <label htmlFor={`source-version-${suffix}`}>Source version <span className="project-optional">(optional)</span></label>
    <input defaultValue={reference?.source_version ?? ""} id={`source-version-${suffix}`} maxLength={128} name="source_version" />
    <label htmlFor={`source-digest-${suffix}`}>Exact source fingerprint <span className="project-optional">(optional)</span></label>
    <input defaultValue={reference?.source_digest ?? ""} id={`source-digest-${suffix}`} inputMode="text" maxLength={64} name="source_digest" pattern="[a-f0-9]{64}" />
    <label htmlFor={`license-${suffix}`}>License <span className="project-optional">(optional)</span></label>
    <input defaultValue={reference?.license ?? ""} id={`license-${suffix}`} maxLength={160} name="license" />
    <label htmlFor={`use-${suffix}`}>Limits on use <span className="project-optional">(optional)</span></label>
    <textarea defaultValue={reference?.use_constraints ?? ""} id={`use-${suffix}`} maxLength={1000} name="use_constraints" rows={3} />
  </div></details>;
}

function ReferenceForm({ busy, reference, workspaceRevision }: {
  busy: boolean;
  reference?: ProjectWorkspace["references"][number];
  workspaceRevision: number;
}) {
  const suffix = reference?.reference_id ?? "new";
  return (
    <IntentForm busy={busy} intent={reference ? "replace-reference" : "add-reference"} workspaceRevision={workspaceRevision}>
      <legend>{reference ? "Edit source" : "Add a source"}</legend>
      {reference ? <><input name="reference_id" type="hidden" value={reference.reference_id} /><input name="reference_version" type="hidden" value={reference.reference_version} /></> : null}
      <label htmlFor={`reference-title-${suffix}`}>Source title</label>
      <input defaultValue={reference?.title} id={`reference-title-${suffix}`} maxLength={160} name="title" required />
      <label htmlFor={`reference-url-${suffix}`}>Secure web address</label>
      <input defaultValue={reference?.url} id={`reference-url-${suffix}`} maxLength={2048} name="url" pattern="https://.*" required type="url" />
      <label htmlFor={`source-name-${suffix}`}>Publisher or source</label>
      <input defaultValue={reference?.source_name} id={`source-name-${suffix}`} maxLength={160} name="source_name" required />
      <OptionalSourceFields reference={reference} />
      <div className="project-form__actions"><button className="button project-button--primary" type="submit">{reference ? "Save source changes" : "Save source"}</button></div>
    </IntentForm>
  );
}

const artifactKindLabels = {
  dataset: "Dataset",
  notebook: "Notebook file",
  code: "Code file",
  environment: "Environment description",
  result: "Result",
  reflection: "Reflection",
  supporting_file: "Supporting file",
} as const;

const mediaTypeLabels = {
  "text/plain": "Plain text",
  "text/csv": "CSV data",
  "text/markdown": "Markdown text",
  "text/x-python": "Python source",
  "application/json": "JSON data",
  "application/x-ipynb+json": "Notebook file",
  "application/pdf": "PDF document",
  "application/octet-stream": "Other supported file",
} as const;

function TechnicalFact({ children, label }: { children: ReactNode; label: string }) {
  return <div><dt>{label}</dt><dd>{children}</dd></div>;
}

function ExactTime({ value }: { value: string }) {
  return <time dateTime={value}><code>{value}</code></time>;
}

function supplied(value: string | null | undefined) {
  return value ?? "Not provided";
}

function ArtifactForm({ busy, workspaceRevision }: { busy: boolean; workspaceRevision: number }) {
  const [artifactKind, setArtifactKind] = useState("supporting_file");
  const [sourceType, setSourceType] = useState("learner_created");
  return (
    <IntentForm busy={busy} intent="add-artifact" workspaceRevision={workspaceRevision}>
      <legend>Add a file</legend>
      <p className="project-form__help">Choose a supported file up to 10 MB. The Academy stores it for safe download; it does not run, expand, or actively preview it.</p>
      <label htmlFor="project-file">File</label>
      <input id="project-file" name="file" required type="file" />
      <label htmlFor="artifact-kind">What does this file contain?</label>
      <select id="artifact-kind" name="artifact_kind" onChange={(event) => setArtifactKind(event.target.value)} value={artifactKind}>
        {Object.entries(artifactKindLabels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
      </select>
      <label htmlFor="media-type">File format</label>
      <select defaultValue="application/octet-stream" id="media-type" name="media_type">
        {Object.entries(mediaTypeLabels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
      </select>
      <label htmlFor="result-classification">How was the content produced? {artifactKind === "result" ? null : <span className="project-optional">(optional)</span>}</label>
      <select defaultValue="" id="result-classification" name="result_classification" required={artifactKind === "result"}>
        <option value="">Not a result</option><option value="observed">Observed</option><option value="calculated">Calculated</option><option value="simulated">Simulated</option><option value="predicted">Predicted</option><option value="generated">Generated</option><option value="narrative">Written interpretation</option>
      </select>
      <label htmlFor="source-type">Where did it come from?</label>
      <select id="source-type" name="source_type" onChange={(event) => setSourceType(event.target.value)} value={sourceType}>
        <option value="learner_created">I created it</option><option value="supplied">It came with learning material</option><option value="external">It came from another source</option>
      </select>
      <label htmlFor="artifact-source-title">Source title</label>
      <input id="artifact-source-title" maxLength={160} name="source_title" required />
      <details className="project-form__details"><summary>Add source and assumption details</summary><div className="project-form__detail-fields">
        <label htmlFor="artifact-source-url">Secure source address <span className="project-optional">(optional)</span></label>
        <input id="artifact-source-url" maxLength={2048} name="source_url" pattern="https://.*" type="url" />
        <label htmlFor="artifact-source-version">Source version <span className="project-optional">(optional)</span></label>
        <input id="artifact-source-version" maxLength={128} name="source_version" />
        <label htmlFor="artifact-source-digest">Exact source fingerprint <span className="project-optional">(optional)</span></label>
        <input id="artifact-source-digest" maxLength={64} name="source_digest" pattern="[a-f0-9]{64}" />
        {sourceType === "learner_created" ? null : <p className="project-form__help">Provide a source version, an exact source fingerprint, or both.</p>}
        <label htmlFor="artifact-license">License <span className="project-optional">(optional)</span></label>
        <input id="artifact-license" maxLength={160} name="license" />
        <label htmlFor="artifact-use">Limits on use <span className="project-optional">(optional)</span></label>
        <textarea id="artifact-use" maxLength={1000} name="use_constraints" rows={3} />
        <label htmlFor="artifact-assumptions">Assumptions <span className="project-optional">(one per line)</span></label>
        <textarea id="artifact-assumptions" maxLength={4000} name="assumptions" rows={3} />
      </div></details>
      <div className="project-form__actions"><button className="button project-button--primary" type="submit">Add file</button></div>
    </IntentForm>
  );
}

function startDownload(content: BlobPart, mediaType: string, fileName: string) {
  const url = URL.createObjectURL(new Blob([content], { type: mediaType }));
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = fileName;
  anchor.click();
  URL.revokeObjectURL(url);
}

function DownloadNotice({ status }: { status: string | null }) {
  if (!status) return null;
  return <p aria-live="polite" className={status === "ready" ? "project-download-status" : "project-form-error"} role="status">
    {status === "ready" ? "Your download is ready."
      : status === "invalid-response" ? "The download did not pass its integrity check, so it was not saved."
        : status === "not-found" ? "That saved item is no longer available."
          : status === "unauthorized" || status === "forbidden" ? "Your private learner access could not be confirmed."
            : "The download is temporarily unavailable. Try again."}
  </p>;
}

export function ProjectDetailPage({
  actionState,
  busy,
  downloadArtifact,
  exportSnapshot,
  project,
  snapshots,
  workspace,
}: {
  actionState: ProjectWorkspaceActionState | undefined;
  busy: boolean;
  downloadArtifact: ArtifactDownloader;
  exportSnapshot: SnapshotExporter;
  project: ProjectShell;
  snapshots: readonly ProjectSnapshot[];
  workspace: ProjectWorkspace;
}) {
  const [downloadStatus, setDownloadStatus] = useState<string | null>(null);
  const learning = project.origin.origin_type === "learning" ? project.origin : null;

  async function handleArtifactDownload(artifact: ProjectArtifact) {
    setDownloadStatus(null);
    const outcome = await downloadArtifact(project.project_id, artifact);
    if (outcome.status === "ready") startDownload(outcome.bytes, "application/octet-stream", outcome.fileName);
    setDownloadStatus(outcome.status);
  }

  async function handleSnapshotExport(snapshotId: string) {
    setDownloadStatus(null);
    const outcome = await exportSnapshot(project.project_id, snapshotId);
    if (outcome.status === "ready") startDownload(outcome.content, "application/json", outcome.fileName);
    setDownloadStatus(outcome.status);
  }

  return (
    <article className="project-page project-detail">
      <header className="project-page__header">
        <p className="eyebrow">Active Project</p>
        <h1>{project.title}</h1>
        <p>{project.charter}</p>
        <Link className="button button--secondary" to="/projects">Return to Projects</Link>
      </header>
      <ActionProblem state={actionState} />
      <DownloadNotice status={downloadStatus} />
      <section className="project-panel">
        <h2>Project source</h2>
        {learning ? <><p>This Project began with the learning brief <strong>{learning.brief_title}</strong>.</p><p>{learning.brief_purpose}</p></> : <p>You started this Project from your own idea.</p>}
        <dl className="project-facts">
          <div><dt>Status</dt><dd>Active</dd></div>
          <div><dt>Started</dt><dd><time dateTime={project.created_at}>{readableProjectDate(project.created_at)}</time></dd></div>
          <div><dt>Last updated</dt><dd><time dateTime={workspace.updated_at}>{readableProjectDate(workspace.updated_at)}</time></dd></div>
        </dl>
        <details>
          <summary>Technical record</summary>
          <dl className="project-technical">
            <div><dt>Project ID</dt><dd><code>{project.project_id}</code></dd></div>
            <div><dt>Project revision</dt><dd><code>{project.revision}</code></dd></div>
            <div><dt>Workspace revision</dt><dd><code>{workspace.workspace_revision}</code></dd></div>
            {learning ? <>
              <div><dt>Learning placement</dt><dd><code>{learning.placement_id}@{learning.placement_version}</code></dd></div>
              <div><dt>Placement digest</dt><dd><code>{learning.placement_digest}</code></dd></div>
              <div><dt>Learning package</dt><dd><code>{learning.package_id}@{learning.package_version}</code></dd></div>
              <div><dt>Package digest</dt><dd><code>{learning.package_digest}</code></dd></div>
              <div><dt>Curriculum</dt><dd><code>{learning.curriculum_id}@{learning.curriculum_version}</code></dd></div>
              <div><dt>Curriculum digest</dt><dd><code>{learning.curriculum_digest}</code></dd></div>
              <div><dt>Brief</dt><dd><code>{learning.brief_id}@{learning.brief_version}</code></dd></div>
              <div><dt>Brief digest</dt><dd><code>{learning.brief_digest}</code></dd></div>
              <div><dt>Brief format</dt><dd><code>{learning.project_brief_schema_version}</code></dd></div>
            </> : null}
          </dl>
        </details>
      </section>

      <section className="project-section" aria-labelledby="project-notes-heading">
        <div><p className="eyebrow">Working record</p><h2 id="project-notes-heading">Notes</h2></div>
        {workspace.notes.length === 0 ? <p className="project-empty">No notes yet.</p> : <ul className="project-work-list">{workspace.notes.map((note) => <li className="project-panel" key={note.note_id}>
          <h3>{note.title}</h3><p className="project-preserved-text">{note.body}</p>
          <details><summary>Note record and editing</summary>
            <dl className="project-technical">
              <TechnicalFact label="Note"><code>{note.note_id}@{note.note_version}</code></TechnicalFact>
              <TechnicalFact label="Created"><ExactTime value={note.created_at} /></TechnicalFact>
              <TechnicalFact label="Last updated"><ExactTime value={note.updated_at} /></TechnicalFact>
            </dl>
            <NoteForm busy={busy} note={note} workspaceRevision={workspace.workspace_revision} />
          </details>
        </li>)}</ul>}
        <NoteForm busy={busy} workspaceRevision={workspace.workspace_revision} />
      </section>

      <section className="project-section" aria-labelledby="project-sources-heading">
        <div><p className="eyebrow">Evidence trail</p><h2 id="project-sources-heading">Sources</h2></div>
        {workspace.references.length === 0 ? <p className="project-empty">No sources yet.</p> : <ul className="project-work-list">{workspace.references.map((reference) => <li className="project-panel" key={reference.reference_id}>
          <h3>{reference.title}</h3><p>{reference.source_name}</p><a href={reference.url} rel="noreferrer" target="_blank">Open source in a new tab</a>
          <details><summary>Source record and editing</summary>
            <dl className="project-technical">
              <TechnicalFact label="Source"><code>{reference.reference_id}@{reference.reference_version}</code></TechnicalFact>
              <TechnicalFact label="Secure web address"><code>{reference.url}</code></TechnicalFact>
              <TechnicalFact label="Source version">{supplied(reference.source_version)}</TechnicalFact>
              <TechnicalFact label="Source fingerprint"><code>{supplied(reference.source_digest)}</code></TechnicalFact>
              <TechnicalFact label="License">{supplied(reference.license)}</TechnicalFact>
              <TechnicalFact label="Limits on use">{supplied(reference.use_constraints)}</TechnicalFact>
              <TechnicalFact label="Created"><ExactTime value={reference.created_at} /></TechnicalFact>
              <TechnicalFact label="Last updated"><ExactTime value={reference.updated_at} /></TechnicalFact>
            </dl>
            <ReferenceForm busy={busy} reference={reference} workspaceRevision={workspace.workspace_revision} />
          </details>
        </li>)}</ul>}
        <ReferenceForm busy={busy} workspaceRevision={workspace.workspace_revision} />
      </section>

      <section className="project-section" aria-labelledby="project-files-heading">
        <div><p className="eyebrow">Saved evidence</p><h2 id="project-files-heading">Files</h2><p>The Academy stores files for safe download but does not run, expand, or actively preview them.</p></div>
        {workspace.artifacts.length === 0 ? <p className="project-empty">No files yet.</p> : <ul className="project-work-list">{workspace.artifacts.map((artifact) => <li className="project-panel" key={`${artifact.artifact_id}-${artifact.artifact_version}`}>
          <h3>{artifact.logical_path}</h3><dl className="project-facts"><TechnicalFact label="Kind">{artifactKindLabels[artifact.artifact_kind]}</TechnicalFact><TechnicalFact label="Source">{artifact.provenance.source_title}</TechnicalFact><TechnicalFact label="Size">{artifact.byte_count.toLocaleString()} bytes</TechnicalFact>{artifact.result_classification ? <TechnicalFact label="Result type">{artifact.result_classification}</TechnicalFact> : null}</dl>
          <button className="button button--secondary" disabled={busy} onClick={() => void handleArtifactDownload(artifact)} type="button">Download original file</button>
          <details><summary>Technical record</summary><dl className="project-technical">
            <TechnicalFact label="Artifact"><code>{artifact.artifact_id}@{artifact.artifact_version}</code></TechnicalFact>
            <TechnicalFact label="Logical path"><code>{artifact.logical_path}</code></TechnicalFact>
            <TechnicalFact label="Artifact kind"><code>{artifact.artifact_kind}</code></TechnicalFact>
            <TechnicalFact label="Content fingerprint"><code>{artifact.content_digest}</code></TechnicalFact>
            <TechnicalFact label="Media type"><code>{artifact.media_type}</code></TechnicalFact>
            <TechnicalFact label="Inspection limit"><code>{artifact.inspection_mode}</code></TechnicalFact>
            <TechnicalFact label="Exact size">{artifact.byte_count} bytes</TechnicalFact>
            <TechnicalFact label="Result classification"><code>{supplied(artifact.result_classification)}</code></TechnicalFact>
            <TechnicalFact label="Source type"><code>{artifact.provenance.source_type}</code></TechnicalFact>
            <TechnicalFact label="Source title">{artifact.provenance.source_title}</TechnicalFact>
            <TechnicalFact label="Source address"><code>{supplied(artifact.provenance.source_url)}</code></TechnicalFact>
            <TechnicalFact label="Source version">{supplied(artifact.provenance.source_version)}</TechnicalFact>
            <TechnicalFact label="Source fingerprint"><code>{supplied(artifact.provenance.source_digest)}</code></TechnicalFact>
            <TechnicalFact label="License">{supplied(artifact.provenance.license)}</TechnicalFact>
            <TechnicalFact label="Limits on use">{supplied(artifact.provenance.use_constraints)}</TechnicalFact>
            <TechnicalFact label="Assumptions">{artifact.assumptions.length === 0 ? "None recorded" : <ul>{artifact.assumptions.map((assumption) => <li key={assumption}>{assumption}</li>)}</ul>}</TechnicalFact>
            <TechnicalFact label="Environment">{artifact.environment ? <><code>{artifact.environment.name}@{artifact.environment.version}</code>{artifact.environment.dependency_digest ? <> — <code>{artifact.environment.dependency_digest}</code></> : null}</> : "Not provided"}</TechnicalFact>
            <TechnicalFact label="Created"><ExactTime value={artifact.created_at} /></TechnicalFact>
          </dl></details>
        </li>)}</ul>}
        <ArtifactForm busy={busy} workspaceRevision={workspace.workspace_revision} />
      </section>

      {workspace.domain_links.length === 0 ? null : <section className="project-section" aria-labelledby="project-links-heading"><div><p className="eyebrow">Connected records</p><h2 id="project-links-heading">Related Project records</h2></div><ul className="project-work-list">{workspace.domain_links.map((link) => <li className="project-panel" key={link.link_id}>
        <h3>{link.resource_type}</h3><p>{link.provenance}</p><details><summary>Technical record</summary><dl className="project-technical">
          <TechnicalFact label="Link ID"><code>{link.link_id}</code></TechnicalFact>
          <TechnicalFact label="Link type"><code>{link.link_type}</code></TechnicalFact>
          <TechnicalFact label="Owner"><code>{link.owner_module}</code></TechnicalFact>
          <TechnicalFact label="Resource"><code>{link.resource_type}:{link.resource_id}</code></TechnicalFact>
          <TechnicalFact label="Resource version"><code>{supplied(link.resource_version)}</code></TechnicalFact>
          <TechnicalFact label="Resource date">{link.resource_as_of ? <ExactTime value={link.resource_as_of} /> : "Not provided"}</TechnicalFact>
          <TechnicalFact label="Reference fingerprint"><code>{link.owner_reference_digest}</code></TechnicalFact>
          <TechnicalFact label="Availability"><code>{link.target_status}</code></TechnicalFact>
          <TechnicalFact label="Validated"><ExactTime value={link.validated_at} /></TechnicalFact>
          <TechnicalFact label="Created"><ExactTime value={link.created_at} /></TechnicalFact>
        </dl></details>
      </li>)}</ul></section>}

      <section className="project-section" id="snapshots" aria-labelledby="project-snapshots-heading">
        <div><p className="eyebrow">Fixed evidence</p><h2 id="project-snapshots-heading">Saved checkpoints</h2><p>A checkpoint keeps one exact version of your Project evidence. You can keep working afterward without changing it.</p></div>
        {snapshots.length === 0 ? <p className="project-empty">No saved checkpoints yet.</p> : <ol className="project-work-list">{snapshots.map((snapshot) => <li className="project-panel" key={snapshot.snapshot_id}>
          <h3>Checkpoint from <time dateTime={snapshot.closed_at}>{readableProjectDate(snapshot.closed_at)}</time></h3><p>It contains {snapshot.snapshot.notes.length} notes, {snapshot.snapshot.references.length} sources, and {snapshot.snapshot.artifacts.length} files.</p>
          <button className="button button--secondary" disabled={busy} onClick={() => void handleSnapshotExport(snapshot.snapshot_id)} type="button">Download evidence record</button>
          <details><summary>Technical record</summary><dl className="project-technical">
            <TechnicalFact label="Snapshot ID"><code>{snapshot.snapshot_id}</code></TechnicalFact>
            <TechnicalFact label="Snapshot fingerprint"><code>{snapshot.snapshot_digest}</code></TechnicalFact>
            <TechnicalFact label="Closed"><ExactTime value={snapshot.closed_at} /></TechnicalFact>
            <TechnicalFact label="Project"><code>{snapshot.snapshot.project_id}</code></TechnicalFact>
            <TechnicalFact label="Learner"><code>{snapshot.snapshot.learner_id}</code></TechnicalFact>
            <TechnicalFact label="Project revision"><code>{snapshot.snapshot.project_revision}</code></TechnicalFact>
            <TechnicalFact label="Project fingerprint"><code>{snapshot.snapshot.project_shell_digest}</code></TechnicalFact>
            <TechnicalFact label="Workspace revision"><code>{snapshot.snapshot.workspace_revision}</code></TechnicalFact>
            <TechnicalFact label="Workspace opened"><ExactTime value={snapshot.snapshot.workspace_created_at} /></TechnicalFact>
            <TechnicalFact label="Workspace updated"><ExactTime value={snapshot.snapshot.workspace_updated_at} /></TechnicalFact>
            <TechnicalFact label="Note records">{snapshot.snapshot.notes.length === 0 ? "None" : <ul>{snapshot.snapshot.notes.map((item) => <li key={item.record_id}><code>{item.record_id}@{item.record_version} — {item.record_digest}</code></li>)}</ul>}</TechnicalFact>
            <TechnicalFact label="Source records">{snapshot.snapshot.references.length === 0 ? "None" : <ul>{snapshot.snapshot.references.map((item) => <li key={item.record_id}><code>{item.record_id}@{item.record_version} — {item.record_digest}</code></li>)}</ul>}</TechnicalFact>
            <TechnicalFact label="File records">{snapshot.snapshot.artifacts.length === 0 ? "None" : <ul>{snapshot.snapshot.artifacts.map((item) => <li key={item.artifact_id}><code>{item.artifact_id}@{item.artifact_version} — {item.manifest_digest} — {item.content_digest} — {item.byte_count} bytes</code></li>)}</ul>}</TechnicalFact>
            <TechnicalFact label="Related records">{snapshot.snapshot.domain_links.length === 0 ? "None" : <ul>{snapshot.snapshot.domain_links.map((item) => <li key={item.link_id}><code>{item.link_id} — {item.record_digest} — {item.owner_reference_digest}</code></li>)}</ul>}</TechnicalFact>
          </dl></details>
        </li>)}</ol>}
        <IntentForm busy={busy} intent="close-snapshot" projectRevision={project.revision} workspaceRevision={workspace.workspace_revision}>
          <legend>Save a fixed checkpoint</legend>
          <p className="project-form__help">This creates a fixed record of the current Project and files. Your live Project stays open for more work.</p>
          <div className="project-form__actions"><button className="button project-button--primary" type="submit">Save checkpoint</button></div>
        </IntentForm>
      </section>
    </article>
  );
}

import { useEffect, useRef, useState } from "react";
import { Form, Link } from "react-router";

import { Icon } from "../../components/Icon";
import {
  readableWorkspaceDate,
  type PersonalWorkspace,
  type PersonalWorkspaceCollection,
  type PersonalWorkspaceRecord,
  type SaveSelection,
  type WorkspaceActionState,
} from "./model";


function requestKey() {
  return crypto.randomUUID();
}

function MutationFields({
  actionState,
  intent,
  revision,
}: {
  actionState?: WorkspaceActionState | undefined;
  intent: string;
  revision: number;
}) {
  const [idempotencyKey, setIdempotencyKey] = useState(() =>
    actionState?.intent === intent && actionState.kind !== "conflict"
      ? actionState.idempotencyKey
      : requestKey(),
  );
  useEffect(() => {
    if (actionState?.intent === intent && actionState.kind === "conflict") {
      setIdempotencyKey(requestKey());
    }
  }, [actionState, intent]);
  return (
    <>
      <input name="form_intent" type="hidden" value={intent} />
      <input name="idempotency_key" type="hidden" value={idempotencyKey} />
      <input name="expected_revision" type="hidden" value={revision} />
    </>
  );
}

function actionMessage(kind: WorkspaceActionState["kind"]): {
  detail: string;
  title: string;
} {
  if (kind === "stale") {
    return {
      title: "Saved learning changed",
      detail: "Your saved learning changed before this update finished. Refresh the page, review the current work, and try again.",
    };
  }
  if (kind === "source-unavailable" || kind === "not-found") {
    return {
      title: "Item not saved",
      detail: "This learning item or saved record is no longer available. No other saved work was changed.",
    };
  }
  if (kind === "unauthorized") {
    return {
      title: "Learner session needed",
      detail: "We couldn't confirm your learner session. No private saved-learning details were changed. Try again.",
    };
  }
  if (kind === "forbidden") {
    return {
      title: "Saved learning unavailable",
      detail: "This learner profile cannot make that saved-learning change.",
    };
  }
  if (kind === "invalid") {
    return {
      title: "Check this change",
      detail: "One or more entries are missing or too long. Review the fields and try again.",
    };
  }
  if (kind === "conflict") {
    return {
      title: "Use a fresh request",
      detail: "That saved request no longer matches this change. Review the fields and try again with the fresh request now prepared.",
    };
  }
  if (kind === "invalid-response") {
    return {
      title: "Saved result unavailable",
      detail: "We couldn't safely confirm the saved result, so no partial details were shown. Reload Saved learning before making another change.",
    };
  }
  if (kind === "unavailable") {
    return {
      title: "Change not confirmed",
      detail: "We couldn't confirm whether this change finished. Keep the form unchanged and try the same request again, or reload Saved learning to check.",
    };
  }
  return {
    title: "Change not completed",
    detail: "We couldn't complete this change safely. No technical or private details were shown.",
  };
}

export function WorkspaceActionNotice({
  actionState,
}: {
  actionState?: WorkspaceActionState | undefined;
}) {
  const heading = useRef<HTMLHeadingElement>(null);
  useEffect(() => {
    if (actionState) heading.current?.focus();
  }, [actionState]);
  if (!actionState) return null;
  const message = actionMessage(actionState.kind);
  return (
    <section aria-live="assertive" className="saved-learning-alert" role="alert">
      <h2 ref={heading} tabIndex={-1}>{message.title}</h2>
      <p>{message.detail}</p>
    </section>
  );
}

function recordName(record: PersonalWorkspaceRecord): string {
  if (record.record_kind === "note") return record.title;
  return record.label ?? record.target.title;
}

function TechnicalRecord({ record }: { record: PersonalWorkspaceRecord }) {
  return (
    <details>
      <summary>Technical record</summary>
      <dl className="saved-learning-technical">
        <div><dt>Saved record</dt><dd><code>{record.record_id}</code></dd></div>
        <div><dt>Learning resource type</dt><dd><code>{record.target.reference_kind}</code></dd></div>
        {record.target.reference_kind === "learning_opportunity" ? (
          <>
            <div><dt>Learning opportunity</dt><dd><code>{record.target.opportunity_id}</code></dd></div>
            <div><dt>Source integrity code</dt><dd><code>{record.target.source_fingerprint}</code></dd></div>
          </>
        ) : null}
        <div><dt>Learning placement</dt><dd><code>{record.target.placement_id}</code></dd></div>
        <div><dt>Lesson package</dt><dd><code>{record.target.package_id}@{record.target.package_version}</code></dd></div>
        <div><dt>Lesson integrity code</dt><dd><code>{record.target.package_digest}</code></dd></div>
        <div><dt>Source checked</dt><dd><time dateTime={record.target.validated_at}>{record.target.validated_at}</time></dd></div>
        <div><dt>Published by</dt><dd>{record.target.provenance.published_by}</dd></div>
        <div><dt>Published</dt><dd><time dateTime={record.target.provenance.published_at}>{record.target.provenance.published_at}</time></dd></div>
        <div><dt>Content reviewed</dt><dd><time dateTime={record.target.provenance.content_reviewed_on}>{record.target.provenance.content_reviewed_on}</time></dd></div>
      </dl>
    </details>
  );
}

function reordered(records: readonly PersonalWorkspaceRecord[], index: number, offset: -1 | 1) {
  const ids = records.map((record) => record.record_id);
  const destination = index + offset;
  if (destination < 0 || destination >= ids.length) return ids;
  const [moved] = ids.splice(index, 1);
  if (moved) ids.splice(destination, 0, moved);
  return ids;
}

function RecordCard({
  actionState,
  busy,
  index,
  record,
  records,
  revision,
}: {
  actionState?: WorkspaceActionState | undefined;
  busy: boolean;
  index: number;
  record: PersonalWorkspaceRecord;
  records: readonly PersonalWorkspaceRecord[];
  revision: number;
}) {
  const updateIntent = `update:${record.record_id}`;
  const retryMutation = actionState?.intent === updateIntent
    ? actionState.retryMutation
    : undefined;
  const retryNote = retryMutation?.operation === "update_note" && retryMutation.record_id === record.record_id
    ? retryMutation
    : undefined;
  const retryBookmark = retryMutation?.operation === "update_bookmark" && retryMutation.record_id === record.record_id
    ? retryMutation
    : undefined;
  const [noteTitle, setNoteTitle] = useState(retryNote?.title ?? (record.record_kind === "note" ? record.title : ""));
  const [noteBody, setNoteBody] = useState(retryNote?.body ?? (record.record_kind === "note" ? record.body : ""));
  const [bookmarkLabel, setBookmarkLabel] = useState(retryBookmark?.label ?? (record.record_kind === "bookmark" ? record.label ?? "" : ""));
  return (
    <li className="saved-learning-card">
      <article aria-labelledby={`saved-record-${record.record_id}`}>
        <header className="saved-learning-card__header">
          <p className="saved-learning-meta">{record.record_kind === "note" ? "Note" : "Bookmark"}{record.archived ? " · Archived" : ""}</p>
          <h3 id={`saved-record-${record.record_id}`}>{recordName(record)}</h3>
          <p>Saved for <Link to={record.target.destination}>{record.target.title}</Link>.</p>
        </header>

        {record.record_kind === "note" ? (
          <Form className="saved-learning-form" method="post">
            <MutationFields actionState={actionState} intent={updateIntent} revision={revision} />
            <input name="operation" type="hidden" value="update_note" />
            <input name="record_id" type="hidden" value={record.record_id} />
            <label>Note title<input disabled={busy} maxLength={200} name="title" onChange={(event) => setNoteTitle(event.currentTarget.value)} required value={noteTitle} /></label>
            <label>Note<textarea disabled={busy} maxLength={10_000} name="body" onChange={(event) => setNoteBody(event.currentTarget.value)} required rows={5} value={noteBody} /></label>
            <button className="button" disabled={busy} type="submit">Save note changes</button>
          </Form>
        ) : (
          <Form className="saved-learning-form" method="post">
            <MutationFields actionState={actionState} intent={updateIntent} revision={revision} />
            <input name="operation" type="hidden" value="update_bookmark" />
            <input name="record_id" type="hidden" value={record.record_id} />
            <label>Personal label<input disabled={busy} maxLength={200} name="label" onChange={(event) => setBookmarkLabel(event.currentTarget.value)} value={bookmarkLabel} /></label>
            <button className="button" disabled={busy} type="submit">Save bookmark changes</button>
          </Form>
        )}

        <div aria-label={`Order and status for ${recordName(record)}`} className="saved-learning-actions" role="group">
          {([-1, 1] as const).map((offset) => {
            const label = offset === -1 ? "Move earlier" : "Move later";
            const disabled = busy || (offset === -1 ? index === 0 : index === records.length - 1);
            const intent = `reorder:${record.record_id}:${offset}`;
            return (
              <Form key={offset} method="post">
                <MutationFields actionState={actionState} intent={intent} revision={revision} />
                <input name="operation" type="hidden" value="reorder_records" />
                {reordered(records, index, offset).map((recordId) => <input key={recordId} name="record_ids" type="hidden" value={recordId} />)}
                <button className="button button--secondary" disabled={disabled} type="submit">{label}</button>
              </Form>
            );
          })}
          <Form method="post">
            <MutationFields actionState={actionState} intent={`${record.archived ? "restore" : "archive"}:${record.record_id}`} revision={revision} />
            <input name="operation" type="hidden" value={record.archived ? "restore_record" : "archive_record"} />
            <input name="record_id" type="hidden" value={record.record_id} />
            <button className="button button--secondary" disabled={busy} type="submit">{record.archived ? "Restore record" : "Archive record"}</button>
          </Form>
        </div>

        <TechnicalRecord record={record} />
        <details className="saved-learning-remove">
          <summary>Remove saved record</summary>
          <p>This removes your saved note or bookmark and its collection membership. It does not remove the learning resource.</p>
          <Form method="post">
            <MutationFields actionState={actionState} intent={`remove:${record.record_id}`} revision={revision} />
            <input name="operation" type="hidden" value="remove_record" />
            <input name="record_id" type="hidden" value={record.record_id} />
            <button className="button saved-learning-button--danger" disabled={busy} type="submit">Remove saved record</button>
          </Form>
        </details>
      </article>
    </li>
  );
}

function CollectionPanel({
  actionState,
  busy,
  collection,
  records,
  revision,
}: {
  actionState?: WorkspaceActionState | undefined;
  busy: boolean;
  collection: PersonalWorkspaceCollection;
  records: readonly PersonalWorkspaceRecord[];
  revision: number;
}) {
  const retryMutation = actionState?.retryMutation;
  const retryTitle = actionState?.intent === `rename:${collection.collection_id}` &&
    retryMutation?.operation === "rename_collection" &&
    retryMutation.collection_id === collection.collection_id
    ? retryMutation.title
    : collection.title;
  const retryMemberIds = actionState?.intent === `members:${collection.collection_id}` &&
    retryMutation?.operation === "set_collection_members" &&
    retryMutation.collection_id === collection.collection_id
    ? retryMutation.member_record_ids
    : collection.member_record_ids;
  const [title, setTitle] = useState(retryTitle);
  const [memberIds, setMemberIds] = useState(() => new Set(retryMemberIds));
  return (
    <section className="saved-learning-panel">
      <h3>{collection.title}</h3>
      <Form className="saved-learning-form" method="post">
        <MutationFields actionState={actionState} intent={`rename:${collection.collection_id}`} revision={revision} />
        <input name="operation" type="hidden" value="rename_collection" />
        <input name="collection_id" type="hidden" value={collection.collection_id} />
        <label>Collection name<input disabled={busy} maxLength={200} name="title" onChange={(event) => setTitle(event.currentTarget.value)} required value={title} /></label>
        <button className="button button--secondary" disabled={busy} type="submit">Rename collection</button>
      </Form>
      <Form className="saved-learning-form" method="post">
        <MutationFields actionState={actionState} intent={`members:${collection.collection_id}`} revision={revision} />
        <input name="operation" type="hidden" value="set_collection_members" />
        <input name="collection_id" type="hidden" value={collection.collection_id} />
        <fieldset disabled={busy}>
          <legend>Saved items in this collection</legend>
          {records.length === 0 ? <p>No saved items are available.</p> : records.map((record) => (
            <label className="saved-learning-choice" key={record.record_id}>
              <input
                checked={memberIds.has(record.record_id)}
                name="member_record_ids"
                onChange={(event) => {
                  const checked = event.currentTarget.checked;
                  setMemberIds((current) => {
                    const next = new Set(current);
                    if (checked) next.add(record.record_id);
                    else next.delete(record.record_id);
                    return next;
                  });
                }}
                type="checkbox"
                value={record.record_id}
              />
              <span>{recordName(record)}</span>
            </label>
          ))}
        </fieldset>
        <button className="button button--secondary" disabled={busy} type="submit">Save collection items</button>
      </Form>
      <details className="saved-learning-remove">
        <summary>Remove collection</summary>
        <p>This removes the collection only. Your notes and bookmarks stay saved.</p>
        <Form method="post">
          <MutationFields actionState={actionState} intent={`remove-collection:${collection.collection_id}`} revision={revision} />
          <input name="operation" type="hidden" value="remove_collection" />
          <input name="collection_id" type="hidden" value={collection.collection_id} />
          <button className="button saved-learning-button--danger" disabled={busy} type="submit">Remove collection</button>
        </Form>
      </details>
      <details>
        <summary>Technical record</summary>
        <dl className="saved-learning-technical">
          <div><dt>Collection</dt><dd><code>{collection.collection_id}</code></dd></div>
          <div><dt>Created</dt><dd><time dateTime={collection.created_at}>{collection.created_at}</time></dd></div>
          <div><dt>Updated</dt><dd><time dateTime={collection.updated_at}>{collection.updated_at}</time></dd></div>
        </dl>
      </details>
    </section>
  );
}

export function PersonalWorkspacePage({
  actionState,
  busy,
  workspace,
}: {
  actionState?: WorkspaceActionState | undefined;
  busy: boolean;
  workspace: PersonalWorkspace;
}) {
  const retryCollection = actionState?.intent === "create-collection" && actionState.retryMutation?.operation === "create_collection"
    ? actionState.retryMutation
    : undefined;
  const [newCollectionTitle, setNewCollectionTitle] = useState(retryCollection?.title ?? "");
  return (
    <section className="saved-learning-page">
      <header className="saved-learning-page__header">
        <p className="eyebrow"><Icon name="learn" />Your learning</p>
        <h1>Saved learning</h1>
        <p>Keep personal notes and bookmarks with the learning resource they came from. Open a lesson or learning opportunity to save something new.</p>
        <Link className="button saved-learning-button--primary" to="/learn">Choose learning to save</Link>
      </header>
      <WorkspaceActionNotice actionState={actionState} />

      <div className="saved-learning-layout">
        <section aria-labelledby="saved-records-heading" className="saved-learning-section">
          <h2 id="saved-records-heading">Notes and bookmarks</h2>
          {workspace.records.length === 0 ? (
            <p className="saved-learning-empty">You have not saved any learning yet. Open a lesson or opportunity and choose “Save to Saved learning.”</p>
          ) : (
            <ol className="saved-learning-list">
              {workspace.records.map((record, index) => (
                <RecordCard actionState={actionState} busy={busy} index={index} key={`${record.record_id}:${record.updated_at}`} record={record} records={workspace.records} revision={workspace.revision} />
              ))}
            </ol>
          )}
        </section>

        <aside aria-labelledby="collections-heading" className="saved-learning-rail">
          <section className="saved-learning-panel">
            <h2 id="collections-heading">Collections</h2>
            <Form className="saved-learning-form" method="post">
              <MutationFields actionState={actionState} intent="create-collection" revision={workspace.revision} />
              <input name="operation" type="hidden" value="create_collection" />
              <label>Collection name<input disabled={busy} maxLength={200} name="title" onChange={(event) => setNewCollectionTitle(event.currentTarget.value)} required value={newCollectionTitle} /></label>
              <button className="button" disabled={busy} type="submit">Create collection</button>
            </Form>
          </section>

          {workspace.collections.length === 0 ? <p className="saved-learning-empty">No collections yet. Create one when you want to group saved notes and bookmarks.</p> : null}
          {workspace.collections.map((collection) => (
            <CollectionPanel
              actionState={actionState}
              busy={busy}
              collection={collection}
              key={`${collection.collection_id}:${collection.updated_at}`}
              records={workspace.records}
              revision={workspace.revision}
            />
          ))}

          <details className="saved-learning-panel">
            <summary>Technical record</summary>
            <dl className="saved-learning-technical">
              <div><dt>Workspace</dt><dd><code>{workspace.workspace_id}</code></dd></div>
              <div><dt>Workspace revision</dt><dd>{workspace.revision}</dd></div>
              <div><dt>Data format version</dt><dd><code>{workspace.schema_version}</code></dd></div>
              <div><dt>Workspace integrity code</dt><dd><code>{workspace.workspace_digest}</code></dd></div>
              <div><dt>Created</dt><dd>{readableWorkspaceDate(workspace.created_at)}</dd></div>
              <div><dt>Updated</dt><dd>{readableWorkspaceDate(workspace.updated_at)}</dd></div>
            </dl>
          </details>
        </aside>
      </div>
    </section>
  );
}

function SelectionFields({ selection }: { selection: SaveSelection }) {
  return (
    <>
      <input name="reference_kind" type="hidden" value={selection.kind} />
      <input name="placement_id" type="hidden" value={selection.placementId} />
      {selection.kind === "learning_opportunity" ? <input name="opportunity_id" type="hidden" value={selection.opportunityId} /> : null}
    </>
  );
}

export function SaveLearningPage({
  actionState,
  busy,
  selection,
  workspace,
}: {
  actionState?: WorkspaceActionState | undefined;
  busy: boolean;
  selection: SaveSelection;
  workspace: PersonalWorkspace;
}) {
  const objectName = selection.kind === "placed_lesson" ? "lesson" : "learning opportunity";
  const retryNote = actionState?.intent === "create-note" && actionState.retryMutation?.operation === "create_note"
    ? actionState.retryMutation
    : undefined;
  const retryBookmark = actionState?.intent === "create-bookmark" && actionState.retryMutation?.operation === "create_bookmark"
    ? actionState.retryMutation
    : undefined;
  const [noteTitle, setNoteTitle] = useState(retryNote?.title ?? "");
  const [noteBody, setNoteBody] = useState(retryNote?.body ?? "");
  const [bookmarkLabel, setBookmarkLabel] = useState(retryBookmark?.label ?? "");
  return (
    <section className="saved-learning-page saved-learning-save">
      <header className="saved-learning-page__header">
        <p className="eyebrow"><Icon name="learn" />Saved learning</p>
        <h1>Save this {objectName}</h1>
        <p>Add a personal note or bookmark. The saved item keeps a link to this exact published learning resource.</p>
        <div className="saved-learning-actions">
          <Link className="button button--secondary" to={selection.returnTo}>Return to {objectName}</Link>
          <Link className="button button--secondary" to="/saved-learning">Open Saved learning</Link>
        </div>
      </header>
      <WorkspaceActionNotice actionState={actionState} />
      <div className="saved-learning-save__forms">
        <Form className="saved-learning-panel saved-learning-form" method="post">
          <h2>Save a note</h2>
          <p>Write what you want to remember about this {objectName}.</p>
          <MutationFields actionState={actionState} intent="create-note" revision={workspace.revision} />
          <SelectionFields selection={selection} />
          <input name="operation" type="hidden" value="create_note" />
          <label>Note title<input disabled={busy} maxLength={200} name="title" onChange={(event) => setNoteTitle(event.currentTarget.value)} required value={noteTitle} /></label>
          <label>Note<textarea disabled={busy} maxLength={10_000} name="body" onChange={(event) => setNoteBody(event.currentTarget.value)} required rows={8} value={noteBody} /></label>
          <button className="button saved-learning-button--primary" disabled={busy} type="submit">Save note</button>
        </Form>
        <Form className="saved-learning-panel saved-learning-form" method="post">
          <h2>Save a bookmark</h2>
          <p>Keep a direct link for later. A personal label is optional.</p>
          <MutationFields actionState={actionState} intent="create-bookmark" revision={workspace.revision} />
          <SelectionFields selection={selection} />
          <input name="operation" type="hidden" value="create_bookmark" />
          <label>Personal label <span>(optional)</span><input disabled={busy} maxLength={200} name="label" onChange={(event) => setBookmarkLabel(event.currentTarget.value)} value={bookmarkLabel} /></label>
          <button className="button saved-learning-button--primary" disabled={busy} type="submit">Save bookmark</button>
        </Form>
      </div>
    </section>
  );
}

import { useEffect, useRef, useState } from "react";
import { Form, Link } from "react-router";

import { Icon } from "../../components/Icon";
import {
  type PersonalWorkspace,
  type PersonalWorkspaceCollection,
  type PersonalWorkspaceMutation,
  type PersonalWorkspaceQueryResult,
  type PersonalWorkspaceRecord,
  type SaveSelection,
  type WorkspaceSearchValues,
  type WorkspaceActionState,
  workspaceSearchHref,
} from "./model";


function requestKey() {
  return crypto.randomUUID();
}

function limited(value: string, maximum: number): string {
  return Array.from(value).slice(0, maximum).join("");
}

function preparedMutation(
  actionState: WorkspaceActionState | undefined,
  intent: string,
): PersonalWorkspaceMutation | undefined {
  return actionState?.intent === intent
    ? actionState.preparedRequest?.mutation
    : undefined;
}

function MutationFields({
  actionState,
  intent,
  mutation,
  revision,
}: {
  actionState?: WorkspaceActionState | undefined;
  intent: string;
  mutation: PersonalWorkspaceMutation;
  revision: number;
}) {
  const [freshKey, setFreshKey] = useState(requestKey);
  const [retryAbandoned, setRetryAbandoned] = useState(false);
  const keyInput = useRef<HTMLInputElement>(null);
  const prepared = actionState?.intent === intent
    ? actionState.preparedRequest
    : undefined;
  const mutationSignature = JSON.stringify(mutation);
  const preparedSignature = prepared
    ? JSON.stringify(prepared.mutation)
    : undefined;
  const retryable = Boolean(
    prepared &&
      (actionState?.kind === "unavailable" ||
        actionState?.kind === "invalid-response" ||
        actionState?.kind === "unexpected"),
  );
  const usePrepared = Boolean(
    retryable && !retryAbandoned && mutationSignature === preparedSignature,
  );
  useEffect(() => {
    setRetryAbandoned(false);
  }, [prepared?.idempotency_key]);
  useEffect(() => {
    if (prepared && mutationSignature !== preparedSignature) {
      setRetryAbandoned(true);
    }
  }, [mutationSignature, prepared, preparedSignature]);
  useEffect(() => {
    setFreshKey(requestKey());
  }, [revision, actionState?.kind, prepared?.idempotency_key]);
  useEffect(() => {
    const form = keyInput.current?.form;
    if (!form) return undefined;
    const renew = () => queueMicrotask(() => setFreshKey(requestKey()));
    form.addEventListener("submit", renew);
    return () => form.removeEventListener("submit", renew);
  }, []);
  const idempotencyKey = usePrepared && prepared
    ? prepared.idempotency_key
    : freshKey;
  const expectedRevision = usePrepared && prepared
    ? prepared.expected_revision
    : revision;
  return (
    <>
      <input name="form_intent" type="hidden" value={intent} />
      <input name="idempotency_key" ref={keyInput} type="hidden" value={idempotencyKey} />
      <input name="expected_revision" type="hidden" value={expectedRevision} />
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

function sourceStatus(status: PersonalWorkspaceRecord["target"]["target_status"]): {
  detail: string;
  label: string;
} {
  if (status === "stale") {
    return {
      label: "Saved details changed",
      detail: "The saved source has changed. Check it again before you open it.",
    };
  }
  if (status === "unavailable") {
    return {
      label: "Source unavailable",
      detail: "This source cannot be opened right now. Your note or bookmark is still saved.",
    };
  }
  return {
    label: "Ready to open",
    detail: "This saved source was available when it was last checked.",
  };
}

function TechnicalRecord({ record }: { record: PersonalWorkspaceRecord }) {
  const target = record.target;
  return (
    <details>
      <summary>Technical record</summary>
      <dl className="saved-learning-technical">
        <div><dt>Saved record</dt><dd><code>{record.record_id}</code></dd></div>
        <div><dt>Learning resource type</dt><dd><code>{target.reference_kind}</code></dd></div>
        <div><dt>Saved record created</dt><dd><time dateTime={record.created_at}>{record.created_at}</time></dd></div>
        <div><dt>Saved record updated</dt><dd><time dateTime={record.updated_at}>{record.updated_at}</time></dd></div>
        <div><dt>Source owner</dt><dd><code>{target.owner_module}</code></dd></div>
        <div><dt>Source status</dt><dd>{target.target_status}</dd></div>
        {target.owner_module === "curriculum" ? (
          <>
            {target.reference_kind === "learning_opportunity" ? (
              <>
                <div><dt>Learning opportunity</dt><dd><code>{target.opportunity_id}</code></dd></div>
                <div><dt>Source integrity code</dt><dd><code>{target.source_fingerprint}</code></dd></div>
              </>
            ) : null}
            <div><dt>Learning placement</dt><dd><code>{target.placement_id}</code></dd></div>
            <div><dt>Lesson package</dt><dd><code>{target.package_id}@{target.package_version}</code></dd></div>
            <div><dt>Lesson integrity code</dt><dd><code>{target.package_digest}</code></dd></div>
            <div><dt>Published by</dt><dd>{target.provenance.published_by}</dd></div>
            <div><dt>Published</dt><dd><time dateTime={target.provenance.published_at}>{target.provenance.published_at}</time></dd></div>
            <div><dt>Content reviewed</dt><dd><time dateTime={target.provenance.content_reviewed_on}>{target.provenance.content_reviewed_on}</time></dd></div>
            <div><dt>Educational-use notice</dt><dd>{target.provenance.educational_use_notice}</dd></div>
          </>
        ) : (
          <>
            <div><dt>Project</dt><dd><code>{target.project_id}</code></dd></div>
            <div><dt>Project revision</dt><dd>{target.project_revision}</dd></div>
            <div><dt>Project workspace revision</dt><dd>{target.workspace_revision}</dd></div>
            <div><dt>Project status</dt><dd>{target.lifecycle}</dd></div>
            {target.reference_kind === "project_snapshot" ? (
              <>
                <div><dt>Saved checkpoint</dt><dd><code>{target.snapshot_id}</code></dd></div>
                <div><dt>Checkpoint integrity code</dt><dd><code>{target.snapshot_digest}</code></dd></div>
                <div><dt>Checkpoint saved</dt><dd><time dateTime={target.closed_at}>{target.closed_at}</time></dd></div>
              </>
            ) : null}
            {target.reference_kind === "project_artifact" ? (
              <>
                <div><dt>Project file</dt><dd><code>{target.artifact_id}</code></dd></div>
                <div><dt>File version</dt><dd>{target.artifact_version}</dd></div>
                <div><dt>File kind</dt><dd>{target.artifact_kind}</dd></div>
                <div><dt>File path</dt><dd><code>{target.logical_path}</code></dd></div>
                <div><dt>File type</dt><dd><code>{target.media_type}</code></dd></div>
                <div><dt>Inspection mode</dt><dd><code>{target.inspection_mode}</code></dd></div>
                <div><dt>File size in bytes</dt><dd>{target.byte_count}</dd></div>
                <div><dt>File integrity code</dt><dd><code>{target.content_digest}</code></dd></div>
                <div><dt>File added</dt><dd><time dateTime={target.created_at}>{target.created_at}</time></dd></div>
              </>
            ) : null}
          </>
        )}
        <div><dt>Source checked</dt><dd><time dateTime={target.validated_at}>{target.validated_at}</time></dd></div>
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
  allowReorder,
  busy,
  index,
  record,
  records,
  revision,
}: {
  actionState?: WorkspaceActionState | undefined;
  allowReorder: boolean;
  busy: boolean;
  index: number;
  record: PersonalWorkspaceRecord;
  records: readonly PersonalWorkspaceRecord[];
  revision: number;
}) {
  const updateIntent = `update:${record.record_id}`;
  const retryMutation = preparedMutation(actionState, updateIntent);
  const retryNote = retryMutation?.operation === "update_note" && retryMutation.record_id === record.record_id
    ? retryMutation
    : undefined;
  const retryBookmark = retryMutation?.operation === "update_bookmark" && retryMutation.record_id === record.record_id
    ? retryMutation
    : undefined;
  const [noteTitle, setNoteTitle] = useState(retryNote?.title ?? (record.record_kind === "note" ? record.title : ""));
  const [noteBody, setNoteBody] = useState(retryNote?.body ?? (record.record_kind === "note" ? record.body : ""));
  const [bookmarkLabel, setBookmarkLabel] = useState(retryBookmark?.label ?? (record.record_kind === "bookmark" ? record.label ?? "" : ""));
  const noteMutation = record.record_kind === "note"
    ? { operation: "update_note", record_id: record.record_id, title: noteTitle, body: noteBody } as const
    : undefined;
  const bookmarkMutation = record.record_kind === "bookmark"
    ? { operation: "update_bookmark", record_id: record.record_id, label: bookmarkLabel } as const
    : undefined;
  const status = sourceStatus(record.target.target_status);
  return (
    <li className="saved-learning-card">
      <article aria-labelledby={`saved-record-${record.record_id}`}>
        <header className="saved-learning-card__header">
          <p className="saved-learning-meta">{record.record_kind === "note" ? "Note" : "Bookmark"}{record.archived ? " · Archived" : ""}</p>
          <h3 id={`saved-record-${record.record_id}`}>{recordName(record)}</h3>
          <p>
            Saved for {record.target.target_status === "available" ? (
              <Link to={record.target.destination}>{record.target.title}</Link>
            ) : (
              <strong>{record.target.title}</strong>
            )}.
          </p>
          <div className={`saved-learning-status saved-learning-status--${record.target.target_status}`}>
            <p><strong>{status.label}.</strong> {status.detail}</p>
            {record.target.target_status === "available" ? (
              <Link className="button button--secondary" to={record.target.destination}>Open saved source</Link>
            ) : null}
          </div>
        </header>

        {record.record_kind === "note" ? (
          <Form className="saved-learning-form" method="post">
            <MutationFields actionState={actionState} intent={updateIntent} mutation={noteMutation!} revision={revision} />
            <input name="operation" type="hidden" value="update_note" />
            <input name="record_id" type="hidden" value={record.record_id} />
            <label>Note title<input disabled={busy} maxLength={240} name="title" onChange={(event) => setNoteTitle(limited(event.currentTarget.value, 120))} required value={noteTitle} /></label>
            <label>Note<textarea disabled={busy} maxLength={16_000} name="body" onChange={(event) => setNoteBody(limited(event.currentTarget.value, 8_000))} required rows={5} value={noteBody} /></label>
            <button className="button" disabled={busy} type="submit">Save note changes</button>
          </Form>
        ) : (
          <Form className="saved-learning-form" method="post">
            <MutationFields actionState={actionState} intent={updateIntent} mutation={bookmarkMutation!} revision={revision} />
            <input name="operation" type="hidden" value="update_bookmark" />
            <input name="record_id" type="hidden" value={record.record_id} />
            <label>Personal label<input disabled={busy} maxLength={240} name="label" onChange={(event) => setBookmarkLabel(limited(event.currentTarget.value, 120))} value={bookmarkLabel} /></label>
            <button className="button" disabled={busy} type="submit">Save bookmark changes</button>
          </Form>
        )}

        <div aria-label={`Order and status for ${recordName(record)}`} className="saved-learning-actions" role="group">
          {allowReorder ? ([-1, 1] as const).map((offset) => {
            const label = offset === -1 ? "Move earlier" : "Move later";
            const disabled = busy || (offset === -1 ? index === 0 : index === records.length - 1);
            const intent = `reorder:${record.record_id}:${offset}`;
            const recordIds = reordered(records, index, offset);
            return (
              <Form key={offset} method="post">
                <MutationFields actionState={actionState} intent={intent} mutation={{ operation: "reorder_records", record_ids: recordIds }} revision={revision} />
                <input name="operation" type="hidden" value="reorder_records" />
                {recordIds.map((recordId) => <input key={recordId} name="record_ids" type="hidden" value={recordId} />)}
                <button className="button button--secondary" disabled={disabled} type="submit">{label}</button>
              </Form>
            );
          }) : null}
          <Form method="post">
            <MutationFields actionState={actionState} intent={`refresh:${record.record_id}`} mutation={{ operation: "refresh_reference", record_id: record.record_id }} revision={revision} />
            <input name="operation" type="hidden" value="refresh_reference" />
            <input name="record_id" type="hidden" value={record.record_id} />
            <button className="button button--secondary" disabled={busy} type="submit"><Icon name="refresh" />Check source</button>
          </Form>
          <Form method="post">
            <MutationFields actionState={actionState} intent={`${record.archived ? "restore" : "archive"}:${record.record_id}`} mutation={{ operation: record.archived ? "restore_record" : "archive_record", record_id: record.record_id }} revision={revision} />
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
            <MutationFields actionState={actionState} intent={`remove:${record.record_id}`} mutation={{ operation: "remove_record", record_id: record.record_id }} revision={revision} />
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
  const retryMutation = actionState?.preparedRequest?.mutation;
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
  const [memberIds, setMemberIds] = useState(() => [...retryMemberIds]);
  const recordsById = new Map(records.map((record) => [record.record_id, record]));
  const renameMutation = {
    operation: "rename_collection",
    collection_id: collection.collection_id,
    title,
  } as const;
  const membersMutation = {
    operation: "set_collection_members",
    collection_id: collection.collection_id,
    member_record_ids: memberIds,
  } as const;
  function moveMember(index: number, offset: -1 | 1) {
    setMemberIds((current) => {
      const destination = index + offset;
      if (destination < 0 || destination >= current.length) return current;
      const next = [...current];
      const [moved] = next.splice(index, 1);
      if (moved) next.splice(destination, 0, moved);
      return next;
    });
  }
  return (
    <section className="saved-learning-panel">
      <h3>{collection.title}</h3>
      <Form className="saved-learning-form" method="post">
        <MutationFields actionState={actionState} intent={`rename:${collection.collection_id}`} mutation={renameMutation} revision={revision} />
        <input name="operation" type="hidden" value="rename_collection" />
        <input name="collection_id" type="hidden" value={collection.collection_id} />
        <label>Collection name<input disabled={busy} maxLength={240} name="title" onChange={(event) => setTitle(limited(event.currentTarget.value, 120))} required value={title} /></label>
        <button className="button button--secondary" disabled={busy} type="submit">Rename collection</button>
      </Form>
      <Form className="saved-learning-form" method="post">
        <MutationFields actionState={actionState} intent={`members:${collection.collection_id}`} mutation={membersMutation} revision={revision} />
        <input name="operation" type="hidden" value="set_collection_members" />
        <input name="collection_id" type="hidden" value={collection.collection_id} />
        {memberIds.map((recordId) => <input key={recordId} name="member_record_ids" type="hidden" value={recordId} />)}
        <fieldset disabled={busy}>
          <legend>Saved items in this collection</legend>
          {records.length === 0 ? <p>No saved items are available.</p> : records.map((record) => (
            <label className="saved-learning-choice" key={record.record_id}>
              <input
                checked={memberIds.includes(record.record_id)}
                disabled={busy || (!memberIds.includes(record.record_id) && memberIds.length >= 100)}
                onChange={(event) => {
                  const checked = event.currentTarget.checked;
                  setMemberIds((current) => {
                    if (checked) {
                      return current.includes(record.record_id) || current.length >= 100
                        ? current
                        : [...current, record.record_id];
                    }
                    return current.filter((recordId) => recordId !== record.record_id);
                  });
                }}
                type="checkbox"
                value={record.record_id}
              />
              <span>{recordName(record)}</span>
            </label>
          ))}
        </fieldset>
        {memberIds.length > 0 ? (
          <ol aria-label={`Order of saved items in ${collection.title}`} className="saved-learning-member-order">
            {memberIds.map((recordId, index) => {
              const member = recordsById.get(recordId);
              if (!member) return null;
              const name = recordName(member);
              return (
                <li key={recordId}>
                  <span>{name}</span>
                  <span className="saved-learning-actions">
                    <button aria-label={`Move ${name} earlier in collection`} className="button button--secondary" disabled={busy || index === 0} onClick={() => moveMember(index, -1)} type="button">Move earlier</button>
                    <button aria-label={`Move ${name} later in collection`} className="button button--secondary" disabled={busy || index === memberIds.length - 1} onClick={() => moveMember(index, 1)} type="button">Move later</button>
                  </span>
                </li>
              );
            })}
          </ol>
        ) : null}
        <button className="button button--secondary" disabled={busy} type="submit">Save collection items</button>
      </Form>
      <details className="saved-learning-remove">
        <summary>Remove collection</summary>
        <p>This removes the collection only. Your notes and bookmarks stay saved.</p>
        <Form method="post">
          <MutationFields actionState={actionState} intent={`remove-collection:${collection.collection_id}`} mutation={{ operation: "remove_collection", collection_id: collection.collection_id }} revision={revision} />
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
  result,
  search = {},
  workspace,
}: {
  actionState?: WorkspaceActionState | undefined;
  busy: boolean;
  result?: PersonalWorkspaceQueryResult | undefined;
  search?: WorkspaceSearchValues | undefined;
  workspace: PersonalWorkspace;
}) {
  const retryCollectionMutation = preparedMutation(actionState, "create-collection");
  const retryCollection = retryCollectionMutation?.operation === "create_collection"
    ? retryCollectionMutation
    : undefined;
  const [newCollectionTitle, setNewCollectionTitle] = useState(retryCollection?.title ?? "");
  const visibleRecords = result?.records ?? workspace.records;
  const hasSearch = Boolean(
    search.text ||
      search.recordKind ||
      search.ownerModule ||
      search.referenceKind ||
      search.targetStatus ||
      search.archived ||
      search.collectionId ||
      search.cursor ||
      (search.sort && search.sort !== "workspace_order"),
  );
  const allowReorder = !hasSearch &&
    !result?.next_cursor &&
    visibleRecords.length === workspace.records.length &&
    visibleRecords.every(
      (record, index) => record.record_id === workspace.records[index]?.record_id,
    );
  return (
    <section className="saved-learning-page">
      <header className="saved-learning-page__header">
        <p className="eyebrow"><Icon name="learn" />Your learning</p>
        <h1>Saved learning</h1>
        <p>Keep personal notes and bookmarks with the learning resource they came from. Open a lesson or learning opportunity to save something new.</p>
        <Link className="button saved-learning-button--primary" to="/learn">Choose learning to save</Link>
      </header>
      <WorkspaceActionNotice actionState={actionState} />

      <section aria-labelledby="saved-search-heading" className="saved-learning-panel saved-learning-search">
        <div className="saved-learning-search__heading">
          <div>
            <h2 id="saved-search-heading">Find saved learning</h2>
            <p>Search your notes and bookmarks, then narrow the results when you need to.</p>
          </div>
        </div>
        <Form className="saved-learning-form saved-learning-search__form" method="get">
          <label className="saved-learning-search__text">Search words<input defaultValue={search.text ?? ""} maxLength={240} name="q" /></label>
          <label>Saved item<select defaultValue={search.recordKind ?? ""} name="record"><option value="">All items</option><option value="note">Notes</option><option value="bookmark">Bookmarks</option></select></label>
          <label>Source area<select defaultValue={search.ownerModule ?? ""} name="source"><option value="">All source areas</option><option value="curriculum">Learning</option><option value="project">Projects</option></select></label>
          <label>Source type<select defaultValue={search.referenceKind ?? ""} name="kind"><option value="">All source types</option><option value="learning_opportunity">Learning opportunity</option><option value="placed_lesson">Lesson</option><option value="project_workspace">Project</option><option value="project_snapshot">Project checkpoint</option><option value="project_artifact">Project file</option></select></label>
          <label>Source status<select defaultValue={search.targetStatus ?? ""} name="status"><option value="">All statuses</option><option value="available">Ready to open</option><option value="stale">Saved details changed</option><option value="unavailable">Source unavailable</option></select></label>
          <label>Saved status<select defaultValue={search.archived ?? ""} name="archive"><option value="">Current and archived</option><option value="active">Current only</option><option value="archived">Archived only</option></select></label>
          <label>Collection<select defaultValue={search.collectionId ?? ""} name="collection"><option value="">All collections</option>{workspace.collections.map((collection) => <option key={collection.collection_id} value={collection.collection_id}>{collection.title}</option>)}</select></label>
          <label>Order<select defaultValue={search.sort ?? "workspace_order"} name="sort"><option value="workspace_order">Saved order</option><option value="updated_desc">Recently updated</option><option value="updated_asc">Oldest update first</option><option value="title_asc">Title</option><option value="source_asc">Source</option></select></label>
          <div className="saved-learning-actions saved-learning-search__actions">
            <button className="button saved-learning-button--primary" disabled={busy} type="submit">Show results</button>
            <Link className="button button--secondary" to="/saved-learning">Clear filters</Link>
          </div>
        </Form>
      </section>

      <div className="saved-learning-layout">
        <section aria-labelledby="saved-records-heading" className="saved-learning-section">
          <h2 id="saved-records-heading">Notes and bookmarks</h2>
          {workspace.records.length === 0 ? (
            <p className="saved-learning-empty">You have not saved any learning yet. Open a lesson or opportunity and choose “Save to Saved learning.”</p>
          ) : visibleRecords.length === 0 ? (
            <p className="saved-learning-empty">No saved items match these filters. Clear a filter or change the search words to see more results.</p>
          ) : (
            <>
              <p className="saved-learning-results" role="status">Showing {visibleRecords.length} saved {visibleRecords.length === 1 ? "item" : "items"}.</p>
              <ol className="saved-learning-list">
                {visibleRecords.map((record, index) => (
                  <RecordCard actionState={actionState} allowReorder={allowReorder} busy={busy} index={index} key={`${record.record_id}:${record.updated_at}:${record.target.validated_at}`} record={record} records={visibleRecords} revision={workspace.revision} />
                ))}
              </ol>
              {result?.next_cursor ? (
                <Link className="button button--secondary saved-learning-more" to={workspaceSearchHref(search, result.next_cursor)}>Show more results</Link>
              ) : null}
            </>
          )}
        </section>

        <aside aria-labelledby="collections-heading" className="saved-learning-rail">
          <section className="saved-learning-panel">
            <h2 id="collections-heading">Collections</h2>
            <Form className="saved-learning-form" method="post">
              <MutationFields actionState={actionState} intent="create-collection" mutation={{ operation: "create_collection", title: newCollectionTitle }} revision={workspace.revision} />
              <input name="operation" type="hidden" value="create_collection" />
              <label>Collection name<input disabled={busy} maxLength={240} name="title" onChange={(event) => setNewCollectionTitle(limited(event.currentTarget.value, 120))} required value={newCollectionTitle} /></label>
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
              <div><dt>Created</dt><dd><time dateTime={workspace.created_at}>{workspace.created_at}</time></dd></div>
              <div><dt>Updated</dt><dd><time dateTime={workspace.updated_at}>{workspace.updated_at}</time></dd></div>
            </dl>
          </details>
        </aside>
      </div>
    </section>
  );
}

function SelectionFields({ selection }: { selection: SaveSelection }) {
  if (selection.kind === "project_workspace") {
    return <><input name="reference_kind" type="hidden" value={selection.kind} /><input name="project_id" type="hidden" value={selection.projectId} /></>;
  }
  if (selection.kind === "project_snapshot") {
    return <><input name="reference_kind" type="hidden" value={selection.kind} /><input name="project_id" type="hidden" value={selection.projectId} /><input name="snapshot_id" type="hidden" value={selection.snapshotId} /></>;
  }
  if (selection.kind === "project_artifact") {
    return <><input name="reference_kind" type="hidden" value={selection.kind} /><input name="project_id" type="hidden" value={selection.projectId} /><input name="artifact_id" type="hidden" value={selection.artifactId} /><input name="artifact_version" type="hidden" value={selection.artifactVersion} /></>;
  }
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
  const objectName = selection.kind === "placed_lesson"
    ? "lesson"
    : selection.kind === "learning_opportunity"
      ? "learning opportunity"
      : selection.kind === "project_workspace"
        ? "Project"
        : selection.kind === "project_snapshot"
          ? "checkpoint"
          : "file record";
  const retryNoteMutation = preparedMutation(actionState, "create-note");
  const retryNote = retryNoteMutation?.operation === "create_note"
    ? retryNoteMutation
    : undefined;
  const retryBookmarkMutation = preparedMutation(actionState, "create-bookmark");
  const retryBookmark = retryBookmarkMutation?.operation === "create_bookmark"
    ? retryBookmarkMutation
    : undefined;
  const [noteTitle, setNoteTitle] = useState(retryNote?.title ?? "");
  const [noteBody, setNoteBody] = useState(retryNote?.body ?? "");
  const [bookmarkLabel, setBookmarkLabel] = useState(retryBookmark?.label ?? "");
  const selector = selection.kind === "learning_opportunity" ? {
        reference_kind: selection.kind,
        opportunity_id: selection.opportunityId,
        placement_id: selection.placementId,
      } as const
    : selection.kind === "placed_lesson" ? {
        reference_kind: selection.kind,
        placement_id: selection.placementId,
      } as const
      : selection.kind === "project_workspace" ? {
          reference_kind: selection.kind,
          project_id: selection.projectId,
        } as const
        : selection.kind === "project_snapshot" ? {
            reference_kind: selection.kind,
            project_id: selection.projectId,
            snapshot_id: selection.snapshotId,
          } as const
          : {
              reference_kind: selection.kind,
              project_id: selection.projectId,
              artifact_id: selection.artifactId,
              artifact_version: selection.artifactVersion,
            } as const;
  const projectSelection = selection.kind.startsWith("project_");
  return (
    <section className="saved-learning-page saved-learning-save">
      <header className="saved-learning-page__header">
        <p className="eyebrow"><Icon name="learn" />Saved learning</p>
        <h1>Save this {objectName}</h1>
        <p>{projectSelection
          ? "Add a personal note or bookmark. Saved learning keeps a reference to this exact Project item and checks your access again when you save."
          : "Add a personal note or bookmark. The saved item keeps a link to this exact published learning resource."}</p>
        <div className="saved-learning-actions">
          <Link className="button button--secondary" to={selection.returnTo}>Return to {projectSelection ? "Project" : objectName}</Link>
          <Link className="button button--secondary" to="/saved-learning">Open Saved learning</Link>
        </div>
      </header>
      <WorkspaceActionNotice actionState={actionState} />
      <div className="saved-learning-save__forms">
        <Form className="saved-learning-panel saved-learning-form" method="post">
          <h2>Save a note</h2>
          <p>Write what you want to remember about this {objectName}.</p>
          <MutationFields actionState={actionState} intent="create-note" mutation={{ operation: "create_note", selector, title: noteTitle, body: noteBody }} revision={workspace.revision} />
          <SelectionFields selection={selection} />
          <input name="operation" type="hidden" value="create_note" />
          <label>Note title<input disabled={busy} maxLength={240} name="title" onChange={(event) => setNoteTitle(limited(event.currentTarget.value, 120))} required value={noteTitle} /></label>
          <label>Note<textarea disabled={busy} maxLength={16_000} name="body" onChange={(event) => setNoteBody(limited(event.currentTarget.value, 8_000))} required rows={8} value={noteBody} /></label>
          <button className="button saved-learning-button--primary" disabled={busy} type="submit">Save note</button>
        </Form>
        <Form className="saved-learning-panel saved-learning-form" method="post">
          <h2>Save a bookmark</h2>
          <p>Keep a direct link for later. A personal label is optional.</p>
          <MutationFields actionState={actionState} intent="create-bookmark" mutation={{ operation: "create_bookmark", selector, label: bookmarkLabel }} revision={workspace.revision} />
          <SelectionFields selection={selection} />
          <input name="operation" type="hidden" value="create_bookmark" />
          <label>Personal label <span>(optional)</span><input disabled={busy} maxLength={240} name="label" onChange={(event) => setBookmarkLabel(limited(event.currentTarget.value, 120))} value={bookmarkLabel} /></label>
          <button className="button saved-learning-button--primary" disabled={busy} type="submit">Save bookmark</button>
        </Form>
      </div>
    </section>
  );
}

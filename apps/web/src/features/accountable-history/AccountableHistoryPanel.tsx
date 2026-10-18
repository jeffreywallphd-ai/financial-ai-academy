import { useEffect, useId, useRef, useState } from "react";

import { Icon } from "../../components/Icon";
import type {
  AccountableHistoryExporter,
  AccountableHistoryReader,
} from "./api";
import type {
  AccountableHistoryDocument,
  AccountableHistoryFailure,
  AccountableHistoryRequest,
  PortableEvidenceExport,
} from "./model";

type PanelState =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "ready"; document: AccountableHistoryDocument }
  | { status: AccountableHistoryFailure };

type DownloadState = "idle" | "preparing" | "ready" | AccountableHistoryFailure;

const STATE_COPY = {
  valid: {
    label: "Available history",
    explanation:
      "The available source and processing records passed their checks.",
    icon: "shield-check" as const,
  },
  incomplete: {
    label: "Some history is unavailable",
    explanation:
      "You can review the available steps and the connections that could not be shown.",
    icon: "warning-triangle" as const,
  },
  invalid: {
    label: "History could not be validated",
    explanation:
      "The technical record keeps the safe validation notes. Do not treat this history as complete.",
    icon: "error-circle" as const,
  },
};

const REDACTION_COPY: Record<
  AccountableHistoryDocument["redactions"][number]["category"],
  string
> = {
  protected_content: "Protected learning content",
  learner_private_identity: "Private learner details",
  owner_payload: "Details held by the source record",
  provider_or_secret_material: "Provider or secret material",
  internal_diagnostics: "Internal diagnostic detail",
  storage_details: "Storage detail",
};

function failureCopy(status: AccountableHistoryFailure): string {
  if (status === "unauthorized") {
    return "We couldn't confirm your learner session. No source or history details were shown. Try again.";
  }
  if (status === "forbidden") {
    return "Source and history is not available with this learner access. No private details were shown.";
  }
  if (status === "invalid-response") {
    return "We couldn't safely show this source and history. No partial record was shown. Try again later.";
  }
  return "Source and history is temporarily unavailable. Your learning record was not changed. Try again.";
}

function downloadCopy(status: DownloadState): string | null {
  if (status === "idle") return null;
  if (status === "preparing") return "Preparing your evidence record.";
  if (status === "ready") return "Your evidence record download is ready.";
  if (status === "invalid-response") {
    return "The evidence record did not pass its checks, so no download was saved.";
  }
  if (status === "unauthorized") {
    return "We couldn't confirm your learner session. No download was saved.";
  }
  if (status === "forbidden") {
    return "Evidence download is not available with this learner access. No download was saved.";
  }
  return "The evidence record is temporarily unavailable. No download was saved. Try again.";
}

function startDownload(record: PortableEvidenceExport): void {
  const content = `${JSON.stringify(record, null, 2)}\n`;
  const url = URL.createObjectURL(
    new Blob([content], { type: record.media_type }),
  );
  const anchor = document.createElement("a");
  anchor.download = `${record.filename_stem}.json`;
  anchor.href = url;
  document.body.append(anchor);
  try {
    anchor.click();
  } finally {
    anchor.remove();
    URL.revokeObjectURL(url);
  }
}

function TechnicalRecord({
  document,
}: {
  document: AccountableHistoryDocument;
}) {
  return (
    <details className="accountable-history__technical">
      <summary>Technical record</summary>
      <dl>
        <div>
          <dt>Data format version</dt>
          <dd>{document.schema_version}</dd>
        </div>
        <div>
          <dt>Review purpose</dt>
          <dd>
            <code>{document.purpose}</code>
          </dd>
        </div>
        <div>
          <dt>Root kind</dt>
          <dd>
            <code>{document.root.root_kind}</code>
          </dd>
        </div>
        <div>
          <dt>Root reference</dt>
          <dd>
            <code>{document.root.resource_id}</code>
          </dd>
        </div>
        {"resource_version" in document.root ? (
          <div>
            <dt>Root version</dt>
            <dd>
              <code>{document.root.resource_version}</code>
            </dd>
          </div>
        ) : (
          <div>
            <dt>Root occurrence</dt>
            <dd>{document.root.occurrence}</dd>
          </div>
        )}
        <div>
          <dt>Validation state</dt>
          <dd>
            <code>{document.state}</code>
          </dd>
        </div>
        <div>
          <dt>Source-lineage integrity code</dt>
          <dd>
            <code>{document.source_lineage_digest}</code>
          </dd>
        </div>
        <div>
          <dt>History integrity code</dt>
          <dd>
            <code>{document.history_digest}</code>
          </dd>
        </div>
      </dl>

      <h4>History entries</h4>
      <ol>
        {document.entries.map((entry) => (
          <li key={entry.entry_id}>
            <dl>
              <div>
                <dt>Sequence</dt>
                <dd>{entry.sequence}</dd>
              </div>
              <div>
                <dt>Entry reference</dt>
                <dd>
                  <code>{entry.entry_id}</code>
                </dd>
              </div>
              <div>
                <dt>Role</dt>
                <dd>
                  <code>{entry.role}</code>
                </dd>
              </div>
              <div>
                <dt>Owning area</dt>
                <dd>
                  <code>{entry.owner_module}</code>
                </dd>
              </div>
              <div>
                <dt>Resource kind</dt>
                <dd>
                  <code>{entry.resource_kind}</code>
                </dd>
              </div>
              <div>
                <dt>Resource reference</dt>
                <dd>
                  <code>{entry.resource_id}</code>
                </dd>
              </div>
              {"resource_version" in entry ? (
                <div>
                  <dt>Resource version</dt>
                  <dd>
                    <code>{entry.resource_version}</code>
                  </dd>
                </div>
              ) : (
                <div>
                  <dt>Resource occurrence</dt>
                  <dd>{entry.occurrence}</dd>
                </div>
              )}
              <div>
                <dt>Recorded at</dt>
                <dd>
                  <code>{entry.recorded_at}</code>
                </dd>
              </div>
              <div>
                <dt>Validation status</dt>
                <dd>
                  <code>{entry.validation_status}</code>
                </dd>
              </div>
              <div>
                <dt>Integrity code</dt>
                <dd>
                  <code>{entry.integrity_digest}</code>
                </dd>
              </div>
            </dl>
          </li>
        ))}
      </ol>

      {document.transformations.length > 0 ? (
        <>
          <h4>Connections</h4>
          <ul>
            {document.transformations.map((item, index) => (
              <li
                key={`${item.source_entry_id}-${item.relation}-${item.target_entry_id}-${index}`}
              >
                <code>{item.source_entry_id}</code> <code>{item.relation}</code>{" "}
                <code>{item.target_entry_id}</code>
              </li>
            ))}
          </ul>
        </>
      ) : null}

      {document.missing_links.length > 0 ? (
        <>
          <h4>Unavailable connection records</h4>
          <ul>
            {document.missing_links.map((item, index) => (
              <li
                key={`${item.source_entry_id}-${item.target_reference}-${index}`}
              >
                <code>{item.source_entry_id}</code> <code>{item.relation}</code>{" "}
                <code>{item.target_reference}</code> (<code>{item.reason}</code>
                )
              </li>
            ))}
          </ul>
        </>
      ) : null}

      {document.diagnostics.length > 0 ? (
        <>
          <h4>Validation records</h4>
          <ul>
            {document.diagnostics.map((item, index) => (
              <li key={`${item.code}-${item.reference}-${index}`}>
                <code>{item.code}</code>: <code>{item.reference}</code>
              </li>
            ))}
          </ul>
        </>
      ) : null}

      {document.redactions.length > 0 ? (
        <>
          <h4>Details left out</h4>
          <ul>
            {document.redactions.map((item) => (
              <li key={item.category}>
                <code>{item.category}</code>: {item.count}
              </li>
            ))}
          </ul>
        </>
      ) : null}
    </details>
  );
}

export function AccountableHistoryPanel({
  contextLabel,
  exportHistory,
  readHistory,
  request,
}: {
  contextLabel: string;
  exportHistory: AccountableHistoryExporter;
  readHistory: AccountableHistoryReader;
  request: AccountableHistoryRequest;
}) {
  const headingId = useId();
  const readController = useRef<AbortController | null>(null);
  const exportController = useRef<AbortController | null>(null);
  const requestKey = JSON.stringify(request);
  const [state, setState] = useState<PanelState>({ status: "idle" });
  const [download, setDownload] = useState<DownloadState>("idle");

  useEffect(() => {
    readController.current?.abort();
    exportController.current?.abort();
    setState({ status: "idle" });
    setDownload("idle");
    return () => {
      readController.current?.abort();
      exportController.current?.abort();
    };
  }, [requestKey]);

  async function showHistory() {
    readController.current?.abort();
    const controller = new AbortController();
    readController.current = controller;
    setDownload("idle");
    setState({ status: "loading" });
    try {
      const outcome = await readHistory(request, controller.signal);
      if (!controller.signal.aborted) setState(outcome);
    } catch {
      if (!controller.signal.aborted) setState({ status: "unavailable" });
    }
  }

  async function downloadHistory() {
    exportController.current?.abort();
    const controller = new AbortController();
    exportController.current = controller;
    setDownload("preparing");
    try {
      const outcome = await exportHistory(request, controller.signal);
      if (controller.signal.aborted) return;
      if (outcome.status !== "ready") {
        setDownload(outcome.status);
        return;
      }
      startDownload(outcome.record);
      setDownload("ready");
    } catch {
      if (!controller.signal.aborted) setDownload("unavailable");
    }
  }

  if (state.status === "idle") {
    return (
      <section
        aria-label={`Source and history for ${contextLabel}`}
        className="accountable-history accountable-history--idle"
      >
        <h3 id={headingId}>Source and history</h3>
        <p>
          See where this {contextLabel} came from and which checks were
          available.
        </p>
        <button
          className="button button--secondary"
          onClick={() => void showHistory()}
          type="button"
        >
          <Icon name="citation" />
          Show source and history
        </button>
      </section>
    );
  }

  if (state.status === "loading") {
    return (
      <section
        aria-label={`Source and history for ${contextLabel}`}
        className="accountable-history"
      >
        <h3 id={headingId}>Source and history</h3>
        <p aria-live="polite" role="status">
          Loading the available source and history…
        </p>
      </section>
    );
  }

  if (state.status !== "ready") {
    return (
      <section
        aria-label={`Source and history for ${contextLabel}`}
        className="accountable-history accountable-history--warning"
      >
        <h3 id={headingId}>Source and history unavailable</h3>
        <p role="alert">{failureCopy(state.status)}</p>
        {state.status === "forbidden" ? null : (
          <button
            className="button button--secondary"
            onClick={() => void showHistory()}
            type="button"
          >
            Try again
          </button>
        )}
      </section>
    );
  }

  const document = state.document;
  const stateCopy = STATE_COPY[document.state];
  const downloadMessage = downloadCopy(download);
  return (
    <section
      aria-label={`Source and history for ${contextLabel}`}
      className="accountable-history"
    >
      <header>
        <p className="eyebrow">{contextLabel}</p>
        <h3 id={headingId}>{document.title}</h3>
        <p>{document.summary}</p>
      </header>

      <div
        className={`accountable-history__state accountable-history__state--${document.state}`}
      >
        <Icon name={stateCopy.icon} />
        <div>
          <strong>{stateCopy.label}</strong>
          <p>{stateCopy.explanation}</p>
        </div>
      </div>

      <ol className="accountable-history__steps">
        {document.entries.map((entry) => (
          <li key={entry.entry_id}>
            <article>
              <span
                aria-hidden="true"
                className="accountable-history__sequence"
              >
                {entry.sequence}
              </span>
              <div>
                <h4>{entry.title}</h4>
                <p>{entry.explanation}</p>
                {entry.validation_status === "incomplete" ? (
                  <p className="accountable-history__entry-note">
                    Some supporting history is unavailable for this step.
                  </p>
                ) : null}
              </div>
            </article>
          </li>
        ))}
      </ol>

      {document.missing_links.length > 0 ? (
        <section
          aria-labelledby={`${headingId}-gaps`}
          className="accountable-history__notice"
        >
          <h4 id={`${headingId}-gaps`}>Unavailable connections</h4>
          <ul>
            {document.missing_links.map((item, index) => (
              <li
                key={`${item.source_entry_id}-${item.target_reference}-${index}`}
              >
                {item.explanation}
              </li>
            ))}
          </ul>
        </section>
      ) : null}

      {document.diagnostics.length > 0 ? (
        <section
          aria-labelledby={`${headingId}-notes`}
          className="accountable-history__notice"
        >
          <h4 id={`${headingId}-notes`}>Validation notes</h4>
          <ul>
            {document.diagnostics.map((item, index) => (
              <li key={`${item.code}-${item.reference}-${index}`}>
                {item.explanation}
              </li>
            ))}
          </ul>
        </section>
      ) : null}

      {document.redactions.length > 0 ? (
        <section
          aria-labelledby={`${headingId}-privacy`}
          className="accountable-history__privacy"
        >
          <h4 id={`${headingId}-privacy`}>Details left out</h4>
          <p>
            Private, protected, and internal details stay with their source
            records.
          </p>
          <ul>
            {document.redactions.map((item) => (
              <li key={item.category}>{REDACTION_COPY[item.category]}</li>
            ))}
          </ul>
        </section>
      ) : null}

      <TechnicalRecord document={document} />

      <div className="accountable-history__actions">
        <button
          disabled={download === "preparing"}
          onClick={() => void downloadHistory()}
          type="button"
        >
          {download === "preparing"
            ? "Preparing download…"
            : "Download evidence record"}
        </button>
        <button
          className="button button--secondary"
          onClick={() => void showHistory()}
          type="button"
        >
          Refresh source and history
        </button>
      </div>
      {downloadMessage ? (
        <p
          aria-live="polite"
          className="accountable-history__download-status"
          role="status"
        >
          {downloadMessage}
        </p>
      ) : null}
      <p className="accountable-history__limitation">
        This record explains available source and processing history. It is not
        proof of mastery, certification, suitability, compliance, or investment
        performance.
      </p>
    </section>
  );
}

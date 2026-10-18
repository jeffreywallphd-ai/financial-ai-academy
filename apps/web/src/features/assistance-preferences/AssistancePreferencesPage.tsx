import { useEffect, useMemo, useRef, useState } from "react";
import { Form } from "react-router";

import { StatusPanel } from "../../components/StatusPanel";
import type { LocalReminderMode } from "../../platform/reminders/localReminderPreference";
import {
  assistanceChangeLabel,
  assistanceModeLabel,
  type AssistancePreferenceProfile,
  type AssistancePreferencesActionState,
  type AssistancePreferencesExporter,
  type AssistancePreferencesExportOutcome,
  type AssistancePreferencesRouteState,
  type LocalReminderExporter,
} from "./model";


function newRequestKey(): string {
  try {
    return globalThis.crypto.randomUUID();
  } catch {
    return `request.${Date.now().toString(36)}.${Math.random().toString(36).slice(2, 12)}`;
  }
}

function actionMessage(state: AssistancePreferencesActionState) {
  const subject = state.authority === "local" ? "Reminder choice" : "AI-help choice";
  if (state.kind === "stale") {
    return { title: `${subject} changed`, detail: "Reload the page, review the current choice, and save again." };
  }
  if (state.kind === "conflict") {
    return { title: `${subject} could not be repeated`, detail: "Reload the page before trying this change again." };
  }
  if (state.kind === "unavailable") {
    return state.authority === "server"
      ? { title: "AI-help change not confirmed", detail: "If you did not change the choice, try Save again to safely repeat the same request." }
      : { title: "Reminder choice not saved", detail: "This browser could not store the choice. No reminder was scheduled or sent." };
  }
  if (state.kind === "no-change") {
    return { title: `${subject} is already saved`, detail: "Choose a different option before saving." };
  }
  if (state.kind === "forbidden" || state.kind === "unauthorized") {
    return { title: `${subject} not allowed`, detail: "Nothing changed. Reload the page to renew the learner session." };
  }
  if (state.kind === "invalid") {
    return { title: `Review the ${subject.toLowerCase()}`, detail: "Choose one available option and try again." };
  }
  if (state.kind === "invalid-response") {
    return { title: `${subject} could not be verified`, detail: "The last verified choice remains in use. Reload before trying again." };
  }
  return { title: "Change not completed", detail: "Reload this page, review the current choices, and try again." };
}

function Choice({
  checked,
  description,
  label,
  name,
  onChange,
  value,
}: {
  checked: boolean;
  description: string;
  label: string;
  name: string;
  onChange: (value: string) => void;
  value: string;
}) {
  return (
    <label className="assistance-choice">
      <input
        checked={checked}
        name={name}
        onChange={(event) => onChange(event.currentTarget.value)}
        type="radio"
        value={value}
      />
      <span>
        <strong>{label}</strong>
        <small>{description}</small>
      </span>
    </label>
  );
}

function ServerUnavailable({
  onRetry,
  status,
}: {
  onRetry: () => void;
  status: Exclude<AssistancePreferencesRouteState["server"], { status: "ready" }>["status"];
}) {
  if (status === "forbidden" || status === "unauthorized") {
    return <StatusPanel actionLabel="Try again" description="We could not open the learner-owned AI-help choice. The reminder choice in this browser remains separate and usable." icon="lock" onAction={onRetry} title="Learner session needed" tone="warning" />;
  }
  if (status === "invalid-response") {
    return <StatusPanel actionLabel="Try again" description="We could not safely verify the saved AI-help choice. AI help remains off here, and no private details were shown." icon="error-circle" onAction={onRetry} title="AI-help choice could not be shown" tone="danger" />;
  }
  if (status === "not-found") {
    return <StatusPanel actionLabel="Try again" description="The saved AI-help choice is no longer available. No partial details were shown." icon="info-circle" onAction={onRetry} title="AI-help choice not found" tone="info" />;
  }
  return <StatusPanel actionLabel="Try again" description="The learner-owned AI-help choice could not be loaded. AI help remains off here, while the reminder choice in this browser remains usable." icon="warning-triangle" onAction={onRetry} title="AI-help choice temporarily unavailable" tone="warning" />;
}

function downloadFile(outcome: Extract<AssistancePreferencesExportOutcome, { status: "ready" }>) {
  const url = URL.createObjectURL(new Blob([outcome.content], { type: "application/json" }));
  const link = document.createElement("a");
  link.href = url;
  link.download = outcome.fileName;
  link.click();
  URL.revokeObjectURL(url);
}

export function AssistancePreferencesPage({
  actionState,
  busy,
  exportLocalReminder,
  exportPreferences,
  onRetry,
  state,
}: {
  actionState: AssistancePreferencesActionState | undefined;
  busy: boolean;
  exportLocalReminder: LocalReminderExporter;
  exportPreferences: AssistancePreferencesExporter;
  onRetry: () => void;
  state: AssistancePreferencesRouteState;
}) {
  const serverProfile = state.server.status === "ready" ? state.server.profile : undefined;
  const pendingServer = actionState?.authority === "server" ? actionState.preparedRequest : undefined;
  const pendingSave = pendingServer?.mutation.operation === "replace_preferences"
    ? pendingServer
    : undefined;
  const pendingReset = pendingServer?.mutation.operation === "reset_profile"
    ? pendingServer
    : undefined;
  const pendingMode = pendingServer?.mutation.operation === "replace_preferences"
    ? pendingServer.mutation.assistance_mode
    : undefined;
  const [serverMode, setServerMode] = useState<AssistancePreferenceProfile["assistance_mode"]>(
    pendingMode ?? serverProfile?.assistance_mode ?? "off",
  );
  const [serverRequestKey, setServerRequestKey] = useState(
    pendingServer?.mutation.operation === "replace_preferences"
      ? pendingServer.idempotency_key
      : newRequestKey(),
  );
  const [serverResetKey] = useState(
    pendingServer?.mutation.operation === "reset_profile"
      ? pendingServer.idempotency_key
      : newRequestKey(),
  );
  const [serverResetConfirmed, setServerResetConfirmed] = useState(false);
  const localEnvelope = state.local.envelope;
  const [localMode, setLocalMode] = useState<LocalReminderMode>(
    localEnvelope?.reminder_mode ?? "off",
  );
  const [localResetConfirmed, setLocalResetConfirmed] = useState(false);
  const [serverDownload, setServerDownload] = useState<string | null>(null);
  const [localDownload, setLocalDownload] = useState<string | null>(null);
  const errorHeading = useRef<HTMLHeadingElement>(null);

  useEffect(() => {
    if (actionState) errorHeading.current?.focus();
  }, [actionState]);

  useEffect(() => {
    if (!pendingServer && serverProfile) setServerMode(serverProfile.assistance_mode);
  }, [pendingServer, serverProfile?.profile_digest, serverProfile?.assistance_mode]);

  useEffect(() => {
    if (localEnvelope) setLocalMode(localEnvelope.reminder_mode);
  }, [localEnvelope?.integrity_code, localEnvelope?.reminder_mode]);

  const message = actionState ? actionMessage(actionState) : null;
  const serverUnchanged = serverMode === serverProfile?.assistance_mode;
  const localUnchanged = localMode === localEnvelope?.reminder_mode;
  const localStatus = useMemo(() => {
    if (state.local.status === "invalid") return "A saved reminder choice could not be verified. This page is using off without overwriting the saved record.";
    if (state.local.status === "absent") return "No reminder choice has been saved in this browser yet.";
    if (state.local.status === "unavailable") return "This browser cannot read or save a reminder choice right now.";
    return "This choice is saved only in this browser.";
  }, [state.local.status]);

  async function downloadServer() {
    if (!serverProfile) return;
    setServerDownload("Preparing the learner-owned download.");
    const outcome = await exportPreferences(serverProfile.revision, serverProfile.profile_digest);
    if (outcome.status !== "ready") {
      setServerDownload(outcome.status === "changed"
        ? "The saved AI-help choice changed. Reload before downloading."
        : "The learner-owned download is not available right now.");
      return;
    }
    downloadFile(outcome);
    setServerDownload("The learner-owned download is ready.");
  }

  async function downloadLocal() {
    setLocalDownload("Preparing the this-browser-only download.");
    const outcome = await exportLocalReminder();
    if (outcome.status !== "ready") {
      setLocalDownload("The this-browser-only download is not available right now.");
      return;
    }
    downloadFile(outcome);
    setLocalDownload("The this-browser-only download is ready.");
  }

  return (
    <article className="assistance-preferences-page">
      <header className="assistance-preferences-page__header">
        <p className="eyebrow">Your choices</p>
        <h1>AI help and reminders</h1>
        <p>Record what you may want in the future. These choices do not turn on AI help or send a reminder today.</p>
      </header>

      <section className="assistance-preferences-purpose">
        <h2>Nothing runs in the background</h2>
        <p>AI help is not available on this screen. Reminders are not available yet. Saving a choice does not share learning data, call a model, schedule work, or contact you.</p>
      </section>

      {message ? (
        <section aria-live="assertive" className="assistance-preferences-alert" role="alert">
          <h2 ref={errorHeading} tabIndex={-1}>{message.title}</h2>
          <p>{message.detail}</p>
        </section>
      ) : null}

      <section className="assistance-preferences-section" aria-labelledby="ai-help-heading">
        <header>
          <p className="eyebrow">Saved with your learner profile</p>
          <h2 id="ai-help-heading">AI-help choice</h2>
          <p>This portable choice is available through the same protected API used by browser and headless clients. It is not permission to share data or use an AI provider.</p>
        </header>
        {state.server.status === "ready" ? (
          <>
            <Form className="assistance-preferences-form" method="post">
              <input name="form_intent" type="hidden" value="server-save" />
              <input name="operation" type="hidden" value="replace_preferences" />
              <input name="expected_revision" type="hidden" value={pendingSave?.expected_revision ?? state.server.profile.revision} />
              <input name="idempotency_key" type="hidden" value={serverRequestKey} />
              <fieldset>
                <legend>When should AI help be considered?</legend>
                <p>This records a preference only. A future feature would still need an approved provider and a separate action from you each time.</p>
                <div className="assistance-choice-grid">
                  <Choice checked={serverMode === "off"} description="Do not offer an AI-help action." label="Keep AI help off" name="assistance_mode" onChange={(value) => { setServerMode(value as AssistancePreferenceProfile["assistance_mode"]); setServerRequestKey(newRequestKey()); }} value="off" />
                  <Choice checked={serverMode === "on_request"} description="A future feature may offer an action that you must start yourself." label="Offer a help option when available" name="assistance_mode" onChange={(value) => { setServerMode(value as AssistancePreferenceProfile["assistance_mode"]); setServerRequestKey(newRequestKey()); }} value="on_request" />
                </div>
              </fieldset>
              <div className="assistance-preferences-actions">
                <button className="button assistance-button--primary" disabled={busy || serverUnchanged} type="submit">{busy ? "Saving…" : "Save AI-help choice"}</button>
                <span aria-live="polite">{serverUnchanged ? `${assistanceModeLabel(state.server.profile.assistance_mode)} is saved.` : "This choice has not been saved."}</span>
              </div>
            </Form>

            <div className="assistance-reset">
              <h3>Reset AI-help choice</h3>
              <p>Reset saves a new learner-profile revision with AI help off. It does not change the reminder choice in this browser.</p>
              <Form method="post">
                <input name="form_intent" type="hidden" value="server-reset" />
                <input name="operation" type="hidden" value="reset_profile" />
                <input name="expected_revision" type="hidden" value={pendingReset?.expected_revision ?? state.server.profile.revision} />
                <input name="idempotency_key" type="hidden" value={serverResetKey} />
                <label><input checked={serverResetConfirmed} name="confirm_reset" onChange={(event) => setServerResetConfirmed(event.currentTarget.checked)} type="checkbox" value="reset" /><span>I understand this resets only the learner-owned AI-help choice.</span></label>
                <button className="button assistance-button--danger" disabled={busy || !serverResetConfirmed || state.server.profile.assistance_mode === "off"} type="submit">Reset AI-help choice</button>
              </Form>
            </div>

            <div className="assistance-download">
              <h3>Download learner-owned choice</h3>
              <p>This portable file includes the current AI-help choice and bounded non-content change history. It contains no reminder choice.</p>
              <button className="button" onClick={() => void downloadServer()} type="button">Download AI-help choice</button>
              <span aria-live="polite">{serverDownload}</span>
            </div>

            <div>
              <h3>Recent AI-help changes</h3>
              <ol className="assistance-history">
                {state.server.history.changes.length ? state.server.history.changes.map((change) => (
                  <li key={change.revision}><strong>{assistanceChangeLabel(change.operation)}</strong><span>{new Date(change.occurred_at).toLocaleString()}</span></li>
                )) : <li>No saved AI-help changes yet.</li>}
              </ol>
            </div>

            <details className="assistance-technical-record">
              <summary>Technical record for AI-help choice</summary>
              <dl>
                <div><dt>Contract version</dt><dd>{state.server.profile.schema_version}</dd></div>
                <div><dt>Profile</dt><dd>{state.server.profile.profile_id}</dd></div>
                <div><dt>Revision</dt><dd>{state.server.profile.revision}</dd></div>
                <div><dt>Created</dt><dd>{state.server.profile.created_at}</dd></div>
                <div><dt>Updated</dt><dd>{state.server.profile.updated_at}</dd></div>
                <div><dt>Integrity code</dt><dd>{state.server.profile.profile_digest}</dd></div>
              </dl>
            </details>
          </>
        ) : <ServerUnavailable onRetry={onRetry} status={state.server.status} />}
      </section>

      <section className="assistance-preferences-section" aria-labelledby="reminder-heading">
        <header>
          <p className="eyebrow">Saved only in this browser</p>
          <h2 id="reminder-heading">Future in-app reminder choice</h2>
          <p>Reminders are not available yet. This local choice has no learner identity, no headless meaning, and never leaves this browser.</p>
          <p className="assistance-local-status">{localStatus}</p>
        </header>
        {localEnvelope ? (
          <>
            <Form className="assistance-preferences-form" method="post">
              <input name="form_intent" type="hidden" value="local-save" />
              <fieldset>
                <legend>What should this browser remember?</legend>
                <div className="assistance-choice-grid">
                  <Choice checked={localMode === "off"} description="Store no future reminder request." label="Keep reminders off" name="reminder_mode" onChange={(value) => setLocalMode(value as LocalReminderMode)} value="off" />
                  <Choice checked={localMode === "in_app_when_available"} description="Remember that you may want reminders inside the application if they are added later." label="Allow in-app reminders when available" name="reminder_mode" onChange={(value) => setLocalMode(value as LocalReminderMode)} value="in_app_when_available" />
                </div>
              </fieldset>
              <div className="assistance-preferences-actions">
                <button className="button assistance-button--primary" disabled={busy || localUnchanged || state.local.status === "unavailable"} type="submit">{busy ? "Saving…" : "Save this-browser choice"}</button>
                <span aria-live="polite">{localUnchanged ? "This browser is using the saved choice." : "This-browser choice has not been saved."}</span>
              </div>
            </Form>

            <div className="assistance-reset">
              <h3>Reset this-browser choice</h3>
              <p>Reset changes only this browser to reminders off. It does not change the learner-owned AI-help choice.</p>
              <Form method="post">
                <input name="form_intent" type="hidden" value="local-reset" />
                <label><input checked={localResetConfirmed} name="confirm_reset" onChange={(event) => setLocalResetConfirmed(event.currentTarget.checked)} type="checkbox" value="reset" /><span>I understand this resets only the reminder choice in this browser.</span></label>
                <button className="button assistance-button--danger" disabled={busy || !localResetConfirmed || localEnvelope.reminder_mode === "off"} type="submit">Reset this-browser choice</button>
              </Form>
            </div>

            <div className="assistance-download">
              <h3>Download this-browser choice</h3>
              <p>This separate file contains no learner identity and is not an AI-help or reminder-delivery record.</p>
              <button className="button" onClick={() => void downloadLocal()} type="button">Download this-browser choice</button>
              <span aria-live="polite">{localDownload}</span>
            </div>

            <details className="assistance-technical-record">
              <summary>Technical record for this browser</summary>
              <dl>
                <div><dt>Contract version</dt><dd>{localEnvelope.schema_version}</dd></div>
                <div><dt>Revision</dt><dd>{localEnvelope.revision}</dd></div>
                <div><dt>Updated</dt><dd>{localEnvelope.updated_at}</dd></div>
                <div><dt>Integrity code</dt><dd>{localEnvelope.integrity_code}</dd></div>
              </dl>
            </details>
          </>
        ) : <StatusPanel description="This browser cannot verify or store the local reminder choice. AI help remains a separate learner-owned choice." icon="warning-triangle" title="This-browser choice unavailable" tone="warning" />}
      </section>
    </article>
  );
}

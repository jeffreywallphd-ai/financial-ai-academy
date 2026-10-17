import {
  useEffect,
  useMemo,
  useRef,
  useState,
  type ChangeEvent,
} from "react";
import { Form } from "react-router";

import { usePresentation } from "../../platform/presentation/presentation";
import { useTheme, type ThemePreference } from "../../platform/theme/theme";
import {
  presentationChangeLabel,
  presentationSettingsEqual,
  presentationSettingsFromProfile,
  type PresentationPreferenceHistory,
  type PresentationPreferenceProfile,
  type PresentationPreferencesActionState,
  type PresentationPreferencesExporter,
  type PresentationSettings,
  BASELINE_PRESENTATION,
} from "./model";


function newRequestKey(): string {
  try {
    return globalThis.crypto.randomUUID();
  } catch {
    return `request.${Date.now().toString(36)}.${Math.random().toString(36).slice(2, 12)}`;
  }
}

function actionMessage(state: PresentationPreferencesActionState) {
  if (state.kind === "stale") {
    return {
      title: "Display choices changed",
      detail: "Reload the page, review the current choices, and then save again.",
    };
  }
  if (state.kind === "conflict") {
    return {
      title: "Change could not be repeated",
      detail: "Reload the page before trying this change again.",
    };
  }
  if (state.kind === "unavailable") {
    return {
      title: "Change not confirmed",
      detail: "Your preview is still visible. If you did not change it, try Save again to safely repeat the same request.",
    };
  }
  if (state.kind === "forbidden" || state.kind === "unauthorized") {
    return {
      title: "Change not allowed",
      detail: "The saved choices were not changed. Reload the page to renew the learner session.",
    };
  }
  if (state.kind === "invalid") {
    return {
      title: "Review the display choices",
      detail: "Choose one option in every group before saving.",
    };
  }
  if (state.kind === "invalid-response") {
    return {
      title: "Saved response could not be used",
      detail: "The application kept the last complete safe display. Reload before trying again.",
    };
  }
  return {
    title: "Change not completed",
    detail: "Reload this page, review the current choices, and try again.",
  };
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
  name: keyof PresentationSettings;
  onChange: (event: ChangeEvent<HTMLInputElement>) => void;
  value: string;
}) {
  return (
    <label className="display-choice">
      <input
        checked={checked}
        name={name}
        onChange={onChange}
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

export function PresentationPreferencesPage({
  actionState,
  busy,
  exportPreferences,
  history,
  profile,
}: {
  actionState: PresentationPreferencesActionState | undefined;
  busy: boolean;
  exportPreferences: PresentationPreferencesExporter;
  history: PresentationPreferenceHistory;
  profile: PresentationPreferenceProfile;
}) {
  const { acceptProfile, preview, restore } = usePresentation();
  const theme = useTheme();
  const accepted = useMemo(() => presentationSettingsFromProfile(profile), [profile]);
  const [draft, setDraft] = useState<PresentationSettings>(accepted);
  const [requestKey, setRequestKey] = useState(newRequestKey);
  const [resetKey, setResetKey] = useState(newRequestKey);
  const [resetConfirmed, setResetConfirmed] = useState(false);
  const [downloadStatus, setDownloadStatus] = useState<string | null>(null);
  const errorHeading = useRef<HTMLHeadingElement>(null);

  useEffect(() => {
    acceptProfile(profile);
    setDraft(accepted);
    setRequestKey(newRequestKey());
    setResetKey(newRequestKey());
    setResetConfirmed(false);
    return () => restore();
  }, [acceptProfile, accepted, profile, restore]);

  useEffect(() => {
    if (actionState) errorHeading.current?.focus();
  }, [actionState]);

  function changeChoice(event: ChangeEvent<HTMLInputElement>) {
    const name = event.currentTarget.name as keyof PresentationSettings;
    const next = { ...draft, [name]: event.currentTarget.value } as PresentationSettings;
    setDraft(next);
    setRequestKey(newRequestKey());
    preview(next);
  }

  function cancelPreview() {
    setDraft(accepted);
    setRequestKey(newRequestKey());
    restore();
  }

  async function download() {
    setDownloadStatus("Preparing your download.");
    const outcome = await exportPreferences(profile.revision, profile.profile_digest);
    if (outcome.status !== "ready") {
      setDownloadStatus(outcome.status === "changed"
        ? "Your saved choices changed. Reload the page before downloading."
        : "The download is not available right now. Your settings were not changed.");
      return;
    }
    const url = URL.createObjectURL(new Blob([outcome.content], { type: "application/json" }));
    const link = document.createElement("a");
    link.href = url;
    link.download = outcome.fileName;
    link.click();
    URL.revokeObjectURL(url);
    setDownloadStatus("Your download is ready.");
  }

  const message = actionState ? actionMessage(actionState) : null;
  const unchanged = presentationSettingsEqual(draft, accepted);
  const baselineAlreadySaved = presentationSettingsEqual(accepted, BASELINE_PRESENTATION);

  return (
    <article className="display-preferences-page">
      <header className="display-preferences-page__header">
        <p className="eyebrow">Your display</p>
        <h1>Display and accessibility</h1>
        <p>Choose how reading pages and controls appear. Changes preview right away and stay reversible.</p>
      </header>

      <section className="display-preferences-purpose">
        <h2>These choices change presentation only</h2>
        <p>They do not describe a medical condition, measure competency, change course access, or affect financial results.</p>
      </section>

      {message ? (
        <section aria-live="assertive" className="display-preferences-alert" role="alert">
          <h2 ref={errorHeading} tabIndex={-1}>{message.title}</h2>
          <p>{message.detail}</p>
        </section>
      ) : null}

      <Form className="display-preferences-form" method="post">
        <input name="form_intent" type="hidden" value="save" />
        <input name="operation" type="hidden" value="replace_preferences" />
        <input name="expected_revision" type="hidden" value={profile.revision} />
        <input name="idempotency_key" type="hidden" value={requestKey} />

        <fieldset>
          <legend>Text size</legend>
          <p>Increase the whole interface without hiding content or controls.</p>
          <div className="display-choice-grid">
            <Choice checked={draft.text_size === "default"} description="Use the standard readable size." label="Standard" name="text_size" onChange={changeChoice} value="default" />
            <Choice checked={draft.text_size === "larger"} description="Make text, spacing, and controls larger." label="Larger" name="text_size" onChange={changeChoice} value="larger" />
          </div>
        </fieldset>

        <fieldset>
          <legend>Text spacing</legend>
          <p>Add room between letters, words, and lines.</p>
          <div className="display-choice-grid">
            <Choice checked={draft.text_spacing === "default"} description="Use the standard reading rhythm." label="Standard" name="text_spacing" onChange={changeChoice} value="default" />
            <Choice checked={draft.text_spacing === "increased"} description="Add more room around text." label="More space" name="text_spacing" onChange={changeChoice} value="increased" />
          </div>
        </fieldset>

        <fieldset>
          <legend>Reading width</legend>
          <p>Choose how wide long reading sections can become.</p>
          <div className="display-choice-grid">
            <Choice checked={draft.reading_width === "standard"} description="Use the standard reading width." label="Standard" name="reading_width" onChange={changeChoice} value="standard" />
            <Choice checked={draft.reading_width === "focused"} description="Keep long text in a narrower column." label="Focused" name="reading_width" onChange={changeChoice} value="focused" />
          </div>
        </fieldset>

        <fieldset>
          <legend>Motion</legend>
          <p>Your device's reduced-motion setting always takes priority when it is more protective.</p>
          <div className="display-choice-grid">
            <Choice checked={draft.motion === "system"} description="Follow your device setting." label="Follow device" name="motion" onChange={changeChoice} value="system" />
            <Choice checked={draft.motion === "reduce"} description="Remove optional application motion." label="Reduce motion" name="motion" onChange={changeChoice} value="reduce" />
          </div>
        </fieldset>

        <div className="display-preferences-actions">
          <button className="button display-button--primary" disabled={busy || unchanged} type="submit">
            {busy ? "Saving…" : "Save display choices"}
          </button>
          <button className="button" disabled={busy || unchanged} onClick={cancelPreview} type="button">
            Cancel preview
          </button>
          <span aria-live="polite">{unchanged ? "Saved choices are in use." : "Previewing unsaved choices."}</span>
        </div>
      </Form>

      <section className="display-preferences-section">
        <h2>Theme on this device</h2>
        <p>Theme is stored only in this browser. It is separate from the learner profile and its download.</p>
        <div className="display-theme-controls">
          <label>
            Theme
            <select
              onChange={(event) => theme.setPreference(event.currentTarget.value as ThemePreference)}
              value={theme.preference}
            >
              <option value="system">Use device setting</option>
              <option value="light">Light</option>
              <option value="dark">Dark</option>
            </select>
          </label>
          <button className="button" disabled={theme.preference === "system"} onClick={() => theme.setPreference("system")} type="button">
            Use device theme
          </button>
        </div>
      </section>

      <section className="display-preferences-section">
        <h2>Reset saved display choices</h2>
        <p>Reset returns text size, spacing, reading width, and motion to their safe defaults. It does not reset the browser theme.</p>
        <Form className="display-reset" method="post">
          <input name="form_intent" type="hidden" value="reset" />
          <input name="operation" type="hidden" value="reset_profile" />
          <input name="expected_revision" type="hidden" value={profile.revision} />
          <input name="idempotency_key" type="hidden" value={resetKey} />
          <label>
            <input
              checked={resetConfirmed}
              name="confirm_reset"
              onChange={(event) => {
                setResetConfirmed(event.currentTarget.checked);
                setResetKey(newRequestKey());
              }}
              type="checkbox"
              value="reset"
            />
            <span>I understand that this resets the four saved display choices.</span>
          </label>
          <button className="button display-button--danger" disabled={busy || !resetConfirmed || baselineAlreadySaved} type="submit">
            Reset saved display choices
          </button>
          {baselineAlreadySaved ? <span>Your saved display choices are already at the safe defaults.</span> : null}
        </Form>
      </section>

      <section className="display-preferences-section">
        <h2>History and download</h2>
        <p>The download contains these choices and a short change history. It does not contain the local theme.</p>
        <button className="button" onClick={() => void download()} type="button">Download display choices</button>
        {downloadStatus ? <p aria-live="polite">{downloadStatus}</p> : null}
        <ol className="display-history">
          {history.changes.length ? history.changes.map((change) => (
            <li key={`${change.revision}-${change.resulting_profile_digest}`}>
              <strong>{presentationChangeLabel(change.operation)}</strong>
              <span>{new Date(change.occurred_at).toLocaleString()}</span>
            </li>
          )) : <li>No saved changes yet.</li>}
        </ol>
      </section>

      <details className="display-technical-record">
        <summary>Technical record</summary>
        <dl>
          <div><dt>Contract version</dt><dd>{profile.schema_version}</dd></div>
          <div><dt>Profile</dt><dd>{profile.profile_id}</dd></div>
          <div><dt>Revision</dt><dd>{profile.revision}</dd></div>
          <div><dt>Created</dt><dd>{profile.created_at}</dd></div>
          <div><dt>Updated</dt><dd>{profile.updated_at}</dd></div>
          <div><dt>Integrity code</dt><dd>{profile.profile_digest}</dd></div>
        </dl>
      </details>
    </article>
  );
}

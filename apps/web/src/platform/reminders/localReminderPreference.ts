export const LOCAL_REMINDER_STORAGE_KEY =
  "financial-ai-academy.local-learning-reminder-preference.v1";

const VERSION = "1.0.0" as const;
const MAX_HISTORY = 100;
const DIGEST = /^[a-f0-9]{64}$/;

export type LocalReminderMode = "in_app_when_available" | "off";
export type LocalReminderOperation = "replace_preference" | "reset_preference";

export interface LocalReminderChange {
  schema_version: typeof VERSION;
  revision: number;
  operation: LocalReminderOperation;
  occurred_at: string;
}

export interface LocalReminderPreferenceEnvelope {
  schema_version: typeof VERSION;
  revision: number;
  reminder_mode: LocalReminderMode;
  updated_at: string;
  changes: LocalReminderChange[];
  integrity_code: string;
}

export interface LocalReminderPreferenceRead {
  status: "absent" | "invalid" | "ready" | "unavailable";
  envelope: LocalReminderPreferenceEnvelope;
}

export interface LocalReminderPreferenceStorage {
  getItem(key: string): string | null;
  setItem(key: string, value: string): void;
}

export class LocalReminderPreferenceError extends Error {
  constructor(
    public readonly code:
      | "invalid_current"
      | "invalid_choice"
      | "invalid_time"
      | "no_change"
      | "storage_unavailable",
  ) {
    super("The local learning-reminder preference could not be changed.");
  }
}

function record(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function exact(value: Record<string, unknown>, keys: string[]): boolean {
  const actual = Object.keys(value).sort();
  return actual.length === keys.length &&
    actual.every((key, index) => key === [...keys].sort()[index]);
}

function timestamp(value: unknown): value is string {
  return typeof value === "string" &&
    value.endsWith("Z") &&
    Number.isFinite(Date.parse(value));
}

function mode(value: unknown): value is LocalReminderMode {
  return value === "off" || value === "in_app_when_available";
}

function operation(value: unknown): value is LocalReminderOperation {
  return value === "replace_preference" || value === "reset_preference";
}

function canonical(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(canonical);
  if (record(value)) {
    return Object.fromEntries(
      Object.keys(value)
        .sort()
        .map((key) => [key, canonical(value[key])]),
    );
  }
  return value;
}

export async function canonicalIntegrity(value: unknown): Promise<string> {
  if (!globalThis.crypto?.subtle) {
    throw new LocalReminderPreferenceError("storage_unavailable");
  }
  const bytes = new TextEncoder().encode(JSON.stringify(canonical(value)));
  const digest = await globalThis.crypto.subtle.digest("SHA-256", bytes);
  return [...new Uint8Array(digest)]
    .map((byte) => byte.toString(16).padStart(2, "0"))
    .join("");
}

function changeIsSafe(value: unknown): value is LocalReminderChange {
  return record(value) &&
    exact(value, ["occurred_at", "operation", "revision", "schema_version"]) &&
    value.schema_version === VERSION &&
    Number.isSafeInteger(value.revision) &&
    Number(value.revision) >= 2 &&
    operation(value.operation) &&
    timestamp(value.occurred_at);
}

async function envelopeIsSafe(
  value: unknown,
): Promise<boolean> {
  if (!record(value) || !exact(value, [
    "changes",
    "integrity_code",
    "reminder_mode",
    "revision",
    "schema_version",
    "updated_at",
  ])) return false;
  if (
    value.schema_version !== VERSION ||
    !Number.isSafeInteger(value.revision) ||
    Number(value.revision) < 1 ||
    !mode(value.reminder_mode) ||
    !timestamp(value.updated_at) ||
    typeof value.integrity_code !== "string" ||
    !DIGEST.test(value.integrity_code) ||
    !Array.isArray(value.changes) ||
    value.changes.length > MAX_HISTORY ||
    !value.changes.every(changeIsSafe)
  ) return false;

  const changes = value.changes as LocalReminderChange[];
  if (!changes.every((change, index) =>
    change.revision <= Number(value.revision) &&
    Date.parse(change.occurred_at) <= Date.parse(value.updated_at as string) &&
    (index === 0 || (
      changes[index - 1]!.revision < change.revision &&
      Date.parse(changes[index - 1]!.occurred_at) <= Date.parse(change.occurred_at)
    )),
  )) return false;
  const latest = changes.at(-1);
  if (latest && latest.revision !== value.revision) return false;
  if (!latest && value.revision !== 1) return false;

  const { integrity_code: integrityCode, ...material } = value;
  return (await canonicalIntegrity(material)) === integrityCode;
}

async function seal(
  material: Omit<LocalReminderPreferenceEnvelope, "integrity_code">,
): Promise<LocalReminderPreferenceEnvelope> {
  return {
    ...material,
    integrity_code: await canonicalIntegrity(material),
  };
}

export async function defaultLocalReminderPreference(
  updatedAt: string,
): Promise<LocalReminderPreferenceEnvelope> {
  if (!timestamp(updatedAt)) {
    throw new LocalReminderPreferenceError("invalid_time");
  }
  return seal({
    schema_version: VERSION,
    revision: 1,
    reminder_mode: "off",
    updated_at: updatedAt,
    changes: [],
  });
}

export async function readLocalReminderPreference(
  storage: Pick<LocalReminderPreferenceStorage, "getItem">,
  virtualDefaultTime: string,
): Promise<LocalReminderPreferenceRead> {
  const fallback = await defaultLocalReminderPreference(virtualDefaultTime);
  let stored: string | null;
  try {
    stored = storage.getItem(LOCAL_REMINDER_STORAGE_KEY);
  } catch {
    return { status: "unavailable", envelope: fallback };
  }
  if (stored === null) return { status: "absent", envelope: fallback };
  try {
    const value: unknown = JSON.parse(stored);
    if (await envelopeIsSafe(value)) {
      return {
        status: "ready",
        envelope: value as LocalReminderPreferenceEnvelope,
      };
    }
    return { status: "invalid", envelope: fallback };
  } catch {
    return { status: "invalid", envelope: fallback };
  }
}

async function changeLocalReminderPreference(
  storage: Pick<LocalReminderPreferenceStorage, "setItem">,
  current: LocalReminderPreferenceEnvelope,
  reminderMode: LocalReminderMode,
  occurredAt: string,
  changeOperation: LocalReminderOperation,
): Promise<LocalReminderPreferenceEnvelope> {
  if (!(await envelopeIsSafe(current))) {
    throw new LocalReminderPreferenceError("invalid_current");
  }
  if (!mode(reminderMode)) {
    throw new LocalReminderPreferenceError("invalid_choice");
  }
  if (!timestamp(occurredAt) || Date.parse(occurredAt) < Date.parse(current.updated_at)) {
    throw new LocalReminderPreferenceError("invalid_time");
  }
  if (reminderMode === current.reminder_mode) {
    throw new LocalReminderPreferenceError("no_change");
  }
  const revision = current.revision + 1;
  const next = await seal({
    schema_version: VERSION,
    revision,
    reminder_mode: reminderMode,
    updated_at: occurredAt,
    changes: [
      ...current.changes,
      {
        schema_version: VERSION,
        revision,
        operation: changeOperation,
        occurred_at: occurredAt,
      },
    ].slice(-MAX_HISTORY),
  });
  try {
    storage.setItem(LOCAL_REMINDER_STORAGE_KEY, JSON.stringify(next));
  } catch {
    throw new LocalReminderPreferenceError("storage_unavailable");
  }
  return next;
}

export async function replaceLocalReminderPreference(
  storage: Pick<LocalReminderPreferenceStorage, "setItem">,
  current: LocalReminderPreferenceEnvelope,
  reminderMode: LocalReminderMode,
  occurredAt: string,
): Promise<LocalReminderPreferenceEnvelope> {
  return changeLocalReminderPreference(
    storage,
    current,
    reminderMode,
    occurredAt,
    "replace_preference",
  );
}

export async function resetLocalReminderPreference(
  storage: Pick<LocalReminderPreferenceStorage, "setItem">,
  current: LocalReminderPreferenceEnvelope,
  occurredAt: string,
): Promise<LocalReminderPreferenceEnvelope> {
  return changeLocalReminderPreference(
    storage,
    current,
    "off",
    occurredAt,
    "reset_preference",
  );
}

export async function exportLocalReminderPreference(
  current: LocalReminderPreferenceEnvelope,
): Promise<string> {
  if (!(await envelopeIsSafe(current))) {
    throw new LocalReminderPreferenceError("invalid_current");
  }
  return JSON.stringify({
    schema_version: VERSION,
    purpose: "Review a learning-reminder choice stored in this browser.",
    limitations: [
      "This download has no learner identity or headless meaning.",
      "The choice does not schedule or send a reminder.",
    ],
    preference: current,
  }, null, 2);
}

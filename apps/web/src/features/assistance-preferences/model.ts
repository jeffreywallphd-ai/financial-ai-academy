import type { components } from "../../generated/api-client";
import type {
  LocalReminderPreferenceEnvelope,
  LocalReminderPreferenceRead,
} from "../../platform/reminders/localReminderPreference";


export type AssistancePreferenceProfile =
  components["schemas"]["AssistancePreferenceProfileResponseModel"];
export type AssistancePreferenceHistory =
  components["schemas"]["AssistancePreferenceHistoryResponseModel"];
export type AssistancePreferenceExport =
  components["schemas"]["AssistancePreferenceExportResponseModel"];
export type PreparedAssistancePreferenceRequest =
  components["schemas"]["AssistancePreferenceMutationRequestModel"];

export type AssistanceServerState =
  | {
      status: "ready";
      export: AssistancePreferenceExport;
      history: AssistancePreferenceHistory;
      profile: AssistancePreferenceProfile;
    }
  | {
      status:
        | "forbidden"
        | "invalid-response"
        | "not-found"
        | "unauthorized"
        | "unavailable"
        | "unexpected";
    };

export type LocalReminderState =
  | {
      status: Exclude<LocalReminderPreferenceRead["status"], "unavailable">;
      envelope: LocalReminderPreferenceEnvelope;
    }
  | { status: "unavailable"; envelope?: LocalReminderPreferenceEnvelope };

export interface AssistancePreferencesRouteState {
  local: LocalReminderState;
  server: AssistanceServerState;
}

export type AssistancePreferencesActionFailure =
  | "conflict"
  | "forbidden"
  | "invalid"
  | "invalid-response"
  | "not-found"
  | "no-change"
  | "stale"
  | "unauthorized"
  | "unavailable"
  | "unexpected";

export type AssistancePreferencesActionState = {
  status: "error";
  authority: "local" | "server";
  kind: AssistancePreferencesActionFailure;
  intent: "reset" | "save";
  preparedRequest?: PreparedAssistancePreferenceRequest;
};

export type AssistancePreferencesExportOutcome =
  | {
      status: "ready";
      content: string;
      fileName: string;
    }
  | {
      status:
        | "changed"
        | "forbidden"
        | "invalid-response"
        | "not-found"
        | "unauthorized"
        | "unavailable"
        | "unexpected";
    };

export type AssistancePreferencesExporter = (
  expectedRevision: number,
  expectedDigest: string,
) => Promise<AssistancePreferencesExportOutcome>;

export type LocalReminderExporter = () => Promise<AssistancePreferencesExportOutcome>;

const DIGEST = /^[a-f0-9]{64}$/;
const IDENTIFIER = /^[a-z0-9][a-z0-9._-]{2,63}$/;
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const CANONICAL_UTC = /^[1-9]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])T([01]\d|2[0-3]):[0-5]\d:[0-5]\d(?:\.\d{1,6})?Z$/;

function record(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function exact(value: Record<string, unknown>, keys: readonly string[]): boolean {
  const actual = Object.keys(value).sort();
  const expected = [...keys].sort();
  return actual.length === expected.length &&
    actual.every((key, index) => key === expected[index]);
}

function boundedText(value: unknown, minimum: number, maximum: number): value is string {
  return typeof value === "string" &&
    Array.from(value).length >= minimum &&
    Array.from(value).length <= maximum;
}

function timestamp(value: unknown): value is string {
  if (typeof value !== "string" || !CANONICAL_UTC.test(value)) return false;
  const parsed = new Date(value);
  if (!Number.isFinite(parsed.getTime())) return false;
  return parsed.toISOString().slice(0, 19) === value.slice(0, 19);
}

function canonical(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(canonical);
  if (record(value)) {
    return Object.fromEntries(
      Object.keys(value).sort().map((key) => [key, canonical(value[key])]),
    );
  }
  return value;
}

async function sha256(value: unknown): Promise<string | undefined> {
  if (!globalThis.crypto?.subtle) return undefined;
  try {
    const bytes = new TextEncoder().encode(JSON.stringify(canonical(value)));
    const digest = await globalThis.crypto.subtle.digest("SHA-256", bytes);
    return [...new Uint8Array(digest)]
      .map((byte) => byte.toString(16).padStart(2, "0"))
      .join("");
  } catch {
    return undefined;
  }
}

function profileHasSafeShape(value: unknown): value is AssistancePreferenceProfile {
  return record(value) && exact(value, [
    "assistance_mode",
    "created_at",
    "learner_id",
    "profile_digest",
    "profile_id",
    "revision",
    "schema_version",
    "updated_at",
  ]) &&
    value.schema_version === "1.0.0" &&
    typeof value.profile_id === "string" && IDENTIFIER.test(value.profile_id) &&
    typeof value.learner_id === "string" && UUID.test(value.learner_id) &&
    Number.isSafeInteger(value.revision) && Number(value.revision) >= 1 &&
    (value.assistance_mode === "off" || value.assistance_mode === "on_request") &&
    timestamp(value.created_at) &&
    timestamp(value.updated_at) &&
    Date.parse(value.created_at) <= Date.parse(value.updated_at) &&
    typeof value.profile_digest === "string" && DIGEST.test(value.profile_digest);
}

export async function assistancePreferenceProfileIsSafe(
  value: unknown,
): Promise<boolean> {
  if (!profileHasSafeShape(value)) return false;
  const { profile_digest: profileDigest, ...material } = value;
  return (await sha256(material)) === profileDigest;
}

function changeIsSafe(
  value: unknown,
): value is AssistancePreferenceHistory["changes"][number] {
  return record(value) && exact(value, [
    "object_id",
    "object_kind",
    "occurred_at",
    "operation",
    "resulting_profile_digest",
    "revision",
    "schema_version",
  ]) &&
    value.schema_version === "1.0.0" &&
    Number.isSafeInteger(value.revision) && Number(value.revision) >= 2 &&
    (value.operation === "replace_preferences" || value.operation === "reset_profile") &&
    value.object_kind === "profile" &&
    value.object_id === null &&
    timestamp(value.occurred_at) &&
    typeof value.resulting_profile_digest === "string" &&
    DIGEST.test(value.resulting_profile_digest);
}

export function assistancePreferenceHistoryIsSafe(
  value: unknown,
  profile: AssistancePreferenceProfile,
): value is AssistancePreferenceHistory {
  if (!record(value) || !exact(value, [
    "changes",
    "current_revision",
    "profile_id",
    "schema_version",
  ])) return false;
  if (
    value.schema_version !== "1.0.0" ||
    value.profile_id !== profile.profile_id ||
    value.current_revision !== profile.revision ||
    !Array.isArray(value.changes) ||
    value.changes.length > 100 ||
    !value.changes.every(changeIsSafe)
  ) return false;
  const changes = value.changes as AssistancePreferenceHistory["changes"];
  const expectedFirst = Math.max(2, profile.revision - 99);
  const expectedLength = profile.revision === 1
    ? 0
    : profile.revision - expectedFirst + 1;
  if (changes.length !== expectedLength) return false;
  if (!changes.every((change, index) =>
    change.revision === expectedFirst + index &&
    Date.parse(change.occurred_at) <= Date.parse(profile.updated_at) &&
    (index === 0 || Date.parse(changes[index - 1]!.occurred_at) <= Date.parse(change.occurred_at))
  )) return false;
  const latest = changes.at(-1);
  return !latest || (
    latest.revision === profile.revision &&
    latest.resulting_profile_digest === profile.profile_digest
  );
}

export async function assistancePreferenceExportIsSafe(
  value: unknown,
): Promise<boolean> {
  if (!record(value) || !exact(value, [
    "exported_at",
    "history",
    "limitations",
    "profile",
    "purpose",
    "schema_version",
  ])) return false;
  if (
    value.schema_version !== "1.0.0" ||
    !boundedText(value.purpose, 1, 240) ||
    !Array.isArray(value.limitations) ||
    value.limitations.length < 1 ||
    value.limitations.length > 8 ||
    !value.limitations.every((item) => boundedText(item, 1, 320)) ||
    !timestamp(value.exported_at) ||
    !profileHasSafeShape(value.profile) ||
    !assistancePreferenceHistoryIsSafe(value.history, value.profile) ||
    Date.parse(value.exported_at) < Date.parse(value.profile.updated_at)
  ) return false;
  return assistancePreferenceProfileIsSafe(value.profile);
}

export function publicErrorCode(value: unknown): string | undefined {
  return record(value) && typeof value.code === "string" ? value.code : undefined;
}

export function assistanceModeLabel(mode: AssistancePreferenceProfile["assistance_mode"]): string {
  return mode === "on_request" ? "Offer a help option when available" : "Keep AI help off";
}

export function assistanceChangeLabel(
  operation: AssistancePreferenceHistory["changes"][number]["operation"],
): string {
  return operation === "reset_profile" ? "Reset AI-help choice" : "Changed AI-help choice";
}

import type { components } from "../../generated/api-client";
import {
  BASELINE_PRESENTATION,
  presentationSettingsFromProfile,
  type PresentationSettings,
} from "../../platform/presentation/presentation";

export {
  BASELINE_PRESENTATION,
  presentationSettingsFromProfile,
  type PresentationSettings,
};


export type PresentationPreferenceProfile =
  components["schemas"]["PresentationPreferenceProfileResponseModel"];
export type PresentationPreferenceHistory =
  components["schemas"]["PresentationPreferenceHistoryResponseModel"];
export type PresentationPreferenceExport =
  components["schemas"]["PresentationPreferenceExportResponseModel"];
export type PreparedPresentationPreferenceRequest =
  components["schemas"]["PresentationPreferenceMutationRequestModel"];

export type PresentationPreferencesRouteState =
  | {
      status: "ready";
      export: PresentationPreferenceExport;
      history: PresentationPreferenceHistory;
      profile: PresentationPreferenceProfile;
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

export type PresentationPreferencesActionFailure =
  | "conflict"
  | "forbidden"
  | "invalid"
  | "invalid-response"
  | "not-found"
  | "stale"
  | "unauthorized"
  | "unavailable"
  | "unexpected";

export type PresentationPreferencesActionState = {
  status: "error";
  kind: PresentationPreferencesActionFailure;
  intent: "reset" | "save";
  preparedRequest?: PreparedPresentationPreferenceRequest;
};

export type PresentationPreferencesExportOutcome =
  | {
      status: "ready";
      content: string;
      export: PresentationPreferenceExport;
      fileName: string;
    }
  | {
      status:
        | "changed"
        | "forbidden"
        | "invalid-response"
        | "unauthorized"
        | "unavailable"
        | "unexpected";
    };

export type PresentationPreferencesExporter = (
  expectedRevision: number,
  expectedDigest: string,
) => Promise<PresentationPreferencesExportOutcome>;

const DIGEST = /^[a-f0-9]{64}$/;
const IDENTIFIER = /^[a-z0-9][a-z0-9._-]{2,63}$/;
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

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
  return typeof value === "string" &&
    value.endsWith("Z") &&
    Number.isFinite(Date.parse(value));
}

function canonicalJson(value: unknown): string {
  function canonical(valueAtKey: unknown): unknown {
    if (Array.isArray(valueAtKey)) return valueAtKey.map(canonical);
    if (record(valueAtKey)) {
      return Object.fromEntries(
        Object.keys(valueAtKey)
          .sort()
          .map((key) => [key, canonical(valueAtKey[key])]),
      );
    }
    return valueAtKey;
  }
  return JSON.stringify(canonical(value));
}

async function sha256(value: unknown): Promise<string | undefined> {
  if (!globalThis.crypto?.subtle) return undefined;
  try {
    const bytes = new TextEncoder().encode(canonicalJson(value));
    const digest = await globalThis.crypto.subtle.digest("SHA-256", bytes);
    return [...new Uint8Array(digest)]
      .map((byte) => byte.toString(16).padStart(2, "0"))
      .join("");
  } catch {
    return undefined;
  }
}

export function presentationSettingsAreSafe(
  value: unknown,
): value is PresentationSettings {
  return record(value) &&
    exact(value, ["motion", "reading_width", "text_size", "text_spacing"]) &&
    (value.motion === "system" || value.motion === "reduce") &&
    (value.reading_width === "standard" || value.reading_width === "focused") &&
    (value.text_size === "default" || value.text_size === "larger") &&
    (value.text_spacing === "default" || value.text_spacing === "increased");
}

export function presentationSettingsEqual(
  first: PresentationSettings,
  second: PresentationSettings,
): boolean {
  return first.motion === second.motion &&
    first.reading_width === second.reading_width &&
    first.text_size === second.text_size &&
    first.text_spacing === second.text_spacing;
}

function profileHasSafeShape(
  value: unknown,
): value is PresentationPreferenceProfile {
  if (!record(value) || !exact(value, [
    "schema_version",
    "profile_id",
    "learner_id",
    "revision",
    "text_size",
    "text_spacing",
    "reading_width",
    "motion",
    "created_at",
    "updated_at",
    "profile_digest",
  ])) return false;
  return value.schema_version === "1.0.0" &&
    typeof value.profile_id === "string" && IDENTIFIER.test(value.profile_id) &&
    typeof value.learner_id === "string" && UUID.test(value.learner_id) &&
    Number.isSafeInteger(value.revision) && Number(value.revision) >= 1 &&
    presentationSettingsAreSafe({
      motion: value.motion,
      reading_width: value.reading_width,
      text_size: value.text_size,
      text_spacing: value.text_spacing,
    }) &&
    timestamp(value.created_at) &&
    timestamp(value.updated_at) &&
    Date.parse(value.created_at) <= Date.parse(value.updated_at) &&
    typeof value.profile_digest === "string" && DIGEST.test(value.profile_digest);
}

export async function presentationPreferenceProfileIsSafe(
  value: unknown,
): Promise<boolean> {
  if (!profileHasSafeShape(value)) return false;
  const { profile_digest: profileDigest, ...material } = value;
  return (await sha256(material)) === profileDigest;
}

function changeIsSafe(
  value: unknown,
): value is PresentationPreferenceHistory["changes"][number] {
  if (!record(value) || !exact(value, [
    "schema_version",
    "revision",
    "operation",
    "object_kind",
    "object_id",
    "occurred_at",
    "resulting_profile_digest",
  ])) return false;
  return value.schema_version === "1.0.0" &&
    Number.isSafeInteger(value.revision) && Number(value.revision) >= 1 &&
    (value.operation === "replace_preferences" || value.operation === "reset_profile") &&
    value.object_kind === "profile" &&
    value.object_id === null &&
    timestamp(value.occurred_at) &&
    typeof value.resulting_profile_digest === "string" &&
    DIGEST.test(value.resulting_profile_digest);
}

export function presentationPreferenceHistoryIsSafe(
  value: unknown,
  profile?: PresentationPreferenceProfile,
): value is PresentationPreferenceHistory {
  if (!record(value) || !exact(value, [
    "schema_version",
    "profile_id",
    "current_revision",
    "changes",
  ])) return false;
  if (
    value.schema_version !== "1.0.0" ||
    typeof value.profile_id !== "string" ||
    !IDENTIFIER.test(value.profile_id) ||
    !Number.isSafeInteger(value.current_revision) ||
    Number(value.current_revision) < 1 ||
    !Array.isArray(value.changes) ||
    value.changes.length > 100 ||
    !value.changes.every(changeIsSafe)
  ) return false;
  const changes = value.changes as PresentationPreferenceHistory["changes"];
  if (!changes.every((change, index) =>
    change.revision <= Number(value.current_revision) &&
    (index === 0 || (
      changes[index - 1]!.revision < change.revision &&
      Date.parse(changes[index - 1]!.occurred_at) <= Date.parse(change.occurred_at)
    )),
  )) return false;
  if (!profile) return true;
  if (
    value.profile_id !== profile.profile_id ||
    value.current_revision !== profile.revision ||
    changes.some((change) => Date.parse(change.occurred_at) > Date.parse(profile.updated_at))
  ) return false;
  const latest = changes.at(-1);
  return !latest || (
    latest.revision === profile.revision &&
    latest.resulting_profile_digest === profile.profile_digest
  );
}

export async function presentationPreferenceExportIsSafe(
  value: unknown,
): Promise<boolean> {
  if (!record(value) || !exact(value, [
    "schema_version",
    "purpose",
    "limitations",
    "exported_at",
    "profile",
    "history",
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
    !presentationPreferenceHistoryIsSafe(value.history, value.profile) ||
    Date.parse(value.exported_at) < Date.parse(value.profile.updated_at)
  ) return false;
  return presentationPreferenceProfileIsSafe(value.profile);
}

export function publicErrorCode(value: unknown): string | undefined {
  return record(value) && typeof value.code === "string" ? value.code : undefined;
}

export function presentationChangeLabel(
  operation: PresentationPreferenceHistory["changes"][number]["operation"],
): string {
  return operation === "reset_profile" ? "Reset display choices" : "Changed display choices";
}

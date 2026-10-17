import type { components } from "../../generated/api-client";


export type LearnerPreferenceProfile =
  components["schemas"]["LearnerPreferenceProfileResponseModel"];
export type LearnerPreferenceHistory =
  components["schemas"]["LearnerPreferenceHistoryResponseModel"];
export type LearnerPreferenceExport =
  components["schemas"]["LearnerPreferenceExportResponseModel"];
export type LearnerPreferenceMutation =
  components["schemas"]["LearnerPreferenceMutationRequestModel"]["mutation"];
export type PreparedPreferenceRequest =
  components["schemas"]["LearnerPreferenceMutationRequestModel"];

export type LearnerPreferencesRouteState =
  | {
      status: "ready";
      profile: LearnerPreferenceProfile;
      history: LearnerPreferenceHistory;
    }
  | {
      status:
        | "unauthorized"
        | "forbidden"
        | "not-found"
        | "invalid-response"
        | "unavailable"
        | "unexpected";
    };

export type LearnerPreferencesActionFailure =
  | "unauthorized"
  | "forbidden"
  | "invalid"
  | "not-found"
  | "stale"
  | "conflict"
  | "limit"
  | "invalid-response"
  | "unavailable"
  | "unexpected";

export type LearnerPreferencesActionState = {
  status: "error";
  kind: LearnerPreferencesActionFailure;
  intent: string;
  preparedRequest?: PreparedPreferenceRequest;
};

export type LearnerPreferencesExportOutcome =
  | {
      status: "ready";
      content: string;
      fileName: string;
      export: LearnerPreferenceExport;
    }
  | {
      status:
        | "changed"
        | "unauthorized"
        | "forbidden"
        | "invalid-response"
        | "unavailable"
        | "unexpected";
    };

export type LearnerPreferencesExporter = (
  expectedRevision: number,
  expectedDigest: string,
) => Promise<LearnerPreferencesExportOutcome>;

const IDENTIFIER = /^[a-z0-9][a-z0-9._-]{2,63}$/;
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const DIGEST = /^[a-f0-9]{64}$/;
const OPERATIONS = new Set([
  "create_goal",
  "update_goal",
  "archive_goal",
  "restore_goal",
  "remove_goal",
  "reorder_goals",
  "create_experience",
  "update_experience",
  "remove_experience",
  "reorder_experience",
  "create_interest",
  "rename_interest",
  "remove_interest",
  "reorder_interests",
  "reset_profile",
]);

function record(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function exact(value: Record<string, unknown>, keys: readonly string[]): boolean {
  const actual = Object.keys(value).sort();
  const expected = [...keys].sort();
  return actual.length === expected.length && actual.every((key, index) => key === expected[index]);
}

function text(value: unknown, minimum: number, maximum: number): value is string {
  if (typeof value !== "string") return false;
  const characters = Array.from(value);
  return characters.length >= minimum &&
    characters.length <= maximum &&
    value === value.trim() &&
    characters.every((character) => {
      const codePoint = character.codePointAt(0) ?? 0;
      return !(
        codePoint <= 8 ||
        (codePoint >= 11 && codePoint <= 12) ||
        (codePoint >= 14 && codePoint <= 31) ||
        codePoint === 127 ||
        (codePoint >= 0xd800 && codePoint <= 0xdfff)
      );
    });
}

function nullableText(value: unknown, maximum: number): value is string | null {
  return value === null || text(value, 1, maximum);
}

function identifier(value: unknown): value is string {
  return typeof value === "string" && IDENTIFIER.test(value);
}

function timestamp(value: unknown): value is string {
  return typeof value === "string" && value.endsWith("Z") && Number.isFinite(Date.parse(value));
}

function chronological(created: string, updated: string): boolean {
  return Date.parse(created) <= Date.parse(updated);
}

function contained(created: string, updated: string, profileCreated: string, profileUpdated: string): boolean {
  return Date.parse(created) >= Date.parse(profileCreated) &&
    Date.parse(updated) <= Date.parse(profileUpdated);
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
    const result = await globalThis.crypto.subtle.digest("SHA-256", bytes);
    return [...new Uint8Array(result)]
      .map((byte) => byte.toString(16).padStart(2, "0"))
      .join("");
  } catch {
    return undefined;
  }
}

function goalIsSafe(
  value: unknown,
): value is components["schemas"]["LearnerPreferenceGoalModel"] {
  if (!record(value) || !exact(value, ["goal_id", "title", "detail", "archived", "created_at", "updated_at"])) return false;
  return identifier(value.goal_id) &&
    text(value.title, 1, 160) &&
    nullableText(value.detail, 2_000) &&
    typeof value.archived === "boolean" &&
    timestamp(value.created_at) &&
    timestamp(value.updated_at) &&
    chronological(value.created_at, value.updated_at);
}

function experienceIsSafe(
  value: unknown,
): value is components["schemas"]["LearnerPreferenceExperienceModel"] {
  if (!record(value) || !exact(value, ["experience_id", "subject", "level", "detail", "created_at", "updated_at"])) return false;
  return identifier(value.experience_id) &&
    text(value.subject, 1, 120) &&
    (value.level === "new" || value.level === "some_experience" || value.level === "experienced") &&
    nullableText(value.detail, 1_000) &&
    timestamp(value.created_at) &&
    timestamp(value.updated_at) &&
    chronological(value.created_at, value.updated_at);
}

function interestIsSafe(
  value: unknown,
): value is components["schemas"]["LearnerPreferenceInterestModel"] {
  if (!record(value) || !exact(value, ["interest_id", "label", "created_at", "updated_at"])) return false;
  return identifier(value.interest_id) &&
    text(value.label, 1, 120) &&
    timestamp(value.created_at) &&
    timestamp(value.updated_at) &&
    chronological(value.created_at, value.updated_at);
}

function learnerPreferenceProfileHasSafeShape(
  value: unknown,
): value is LearnerPreferenceProfile {
  if (!record(value) || !exact(value, [
    "schema_version",
    "profile_id",
    "learner_id",
    "revision",
    "goals",
    "experience",
    "interests",
    "created_at",
    "updated_at",
    "profile_digest",
  ])) return false;
  if (
    value.schema_version !== "1.0.0" ||
    !identifier(value.profile_id) ||
    typeof value.learner_id !== "string" ||
    !UUID.test(value.learner_id) ||
    !Number.isSafeInteger(value.revision) ||
    Number(value.revision) < 1 ||
    !Array.isArray(value.goals) || value.goals.length > 20 || !value.goals.every(goalIsSafe) ||
    !Array.isArray(value.experience) || value.experience.length > 20 || !value.experience.every(experienceIsSafe) ||
    !Array.isArray(value.interests) || value.interests.length > 50 || !value.interests.every(interestIsSafe) ||
    !timestamp(value.created_at) ||
    !timestamp(value.updated_at) ||
    !chronological(value.created_at, value.updated_at) ||
    typeof value.profile_digest !== "string" ||
    !DIGEST.test(value.profile_digest)
  ) return false;
  const profile = value as LearnerPreferenceProfile;
  const ids = [
    ...profile.goals.map((item) => item.goal_id),
    ...profile.experience.map((item) => item.experience_id),
    ...profile.interests.map((item) => item.interest_id),
  ];
  if (new Set(ids).size !== ids.length) return false;
  return [...profile.goals, ...profile.experience, ...profile.interests].every((item) =>
    contained(item.created_at, item.updated_at, profile.created_at, profile.updated_at));
}

export async function learnerPreferenceProfileIsSafe(value: unknown): Promise<boolean> {
  if (!learnerPreferenceProfileHasSafeShape(value)) return false;
  const { profile_digest: profileDigest, ...material } = value;
  return (await sha256(material)) === profileDigest;
}

function changeIsSafe(
  value: unknown,
): value is components["schemas"]["LearnerPreferenceChangeModel"] {
  if (!record(value) || !exact(value, [
    "schema_version",
    "revision",
    "operation",
    "object_kind",
    "object_id",
    "occurred_at",
    "resulting_profile_digest",
  ])) return false;
  if (
    value.schema_version !== "1.0.0" ||
    !Number.isSafeInteger(value.revision) ||
    Number(value.revision) < 1 ||
    typeof value.operation !== "string" ||
    !OPERATIONS.has(value.operation) ||
    !timestamp(value.occurred_at) ||
    typeof value.resulting_profile_digest !== "string" ||
    !DIGEST.test(value.resulting_profile_digest)
  ) return false;
  if (["reorder_goals", "reorder_experience", "reorder_interests", "reset_profile"].includes(value.operation)) {
    return value.object_kind === "profile" && value.object_id === null;
  }
  const expectedKind = value.operation.includes("goal")
    ? "goal"
    : value.operation.includes("experience")
      ? "experience"
      : "interest";
  return value.object_kind === expectedKind && identifier(value.object_id);
}

export function learnerPreferenceHistoryIsSafe(
  value: unknown,
  profile?: LearnerPreferenceProfile,
): value is LearnerPreferenceHistory {
  if (!record(value) || !exact(value, ["schema_version", "profile_id", "current_revision", "changes"])) return false;
  if (
    value.schema_version !== "1.0.0" ||
    !identifier(value.profile_id) ||
    !Number.isSafeInteger(value.current_revision) ||
    Number(value.current_revision) < 1 ||
    !Array.isArray(value.changes) ||
    value.changes.length > 100 ||
    !value.changes.every(changeIsSafe)
  ) return false;
  const changes = value.changes as LearnerPreferenceHistory["changes"];
  if (!changes.every((change, index) =>
    change.revision <= Number(value.current_revision) &&
    (index === 0 || (
      changes[index - 1]!.revision < change.revision &&
      Date.parse(changes[index - 1]!.occurred_at) <= Date.parse(change.occurred_at)
    ))
  )) return false;
  if (!profile) return true;
  if (value.profile_id !== profile.profile_id || value.current_revision !== profile.revision) return false;
  const latest = changes.at(-1);
  return !latest || (
    latest.revision === profile.revision &&
    latest.resulting_profile_digest === profile.profile_digest
  );
}

export async function learnerPreferenceExportIsSafe(
  value: unknown,
): Promise<boolean> {
  if (!record(value) || !exact(value, ["schema_version", "purpose", "limitations", "exported_at", "profile", "history"])) return false;
  if (!(value.schema_version === "1.0.0" &&
    text(value.purpose, 1, 240) &&
    Array.isArray(value.limitations) &&
    value.limitations.length >= 1 &&
    value.limitations.length <= 8 &&
    value.limitations.every((item) => text(item, 1, 320)) &&
    timestamp(value.exported_at) &&
    learnerPreferenceProfileHasSafeShape(value.profile) &&
    learnerPreferenceHistoryIsSafe(value.history, value.profile) &&
    Date.parse(value.exported_at) >= Date.parse(value.profile.updated_at)
  )) return false;
  return learnerPreferenceProfileIsSafe(value.profile);
}

export function preferenceMutationErrorCode(value: unknown): string | undefined {
  return record(value) && typeof value.code === "string" ? value.code : undefined;
}

export function moveIdentifier(
  identifiers: readonly string[],
  identifierToMove: string,
  direction: "up" | "down",
): string[] | undefined {
  const index = identifiers.indexOf(identifierToMove);
  if (index < 0) return undefined;
  const target = direction === "up" ? index - 1 : index + 1;
  if (target < 0 || target >= identifiers.length) return undefined;
  const moved = [...identifiers];
  [moved[index], moved[target]] = [moved[target]!, moved[index]!];
  return moved;
}

export function experienceLevelLabel(level: LearnerPreferenceProfile["experience"][number]["level"]): string {
  if (level === "new") return "New to this topic";
  if (level === "some_experience") return "Some experience";
  return "Experienced";
}

export function preferenceChangeLabel(
  operation: LearnerPreferenceHistory["changes"][number]["operation"],
): string {
  const labels: Record<typeof operation, string> = {
    create_goal: "Added a goal",
    update_goal: "Updated a goal",
    archive_goal: "Archived a goal",
    restore_goal: "Restored a goal",
    remove_goal: "Removed a goal",
    reorder_goals: "Reordered goals",
    create_experience: "Added experience",
    update_experience: "Updated experience",
    remove_experience: "Removed experience",
    reorder_experience: "Reordered experience",
    create_interest: "Added an interest",
    rename_interest: "Renamed an interest",
    remove_interest: "Removed an interest",
    reorder_interests: "Reordered interests",
    reset_profile: "Reset learning preferences",
  };
  return labels[operation];
}

import type { components } from "../../generated/api-client";

export type ProjectShell = components["schemas"]["ProjectShellResponseModel"];
export type LearningProjectStartOption =
  components["schemas"]["LearningProjectStartOptionResponseModel"];

export type ProjectListRouteState =
  | { status: "ready"; projects: readonly ProjectShell[]; options: readonly LearningProjectStartOption[] }
  | { status: "unauthorized" | "forbidden" | "unavailable" | "invalid-response" | "unexpected" };

export type ProjectDetailRouteState =
  | { status: "ready"; project: ProjectShell }
  | { status: "invalid-selection" | "not-found" | "unauthorized" | "forbidden" | "unavailable" | "invalid-response" | "unexpected" };

export type ProjectCreateRouteState =
  | { status: "ready"; option: LearningProjectStartOption | null; idempotencyKey: string }
  | { status: "invalid-selection" | "unauthorized" | "forbidden" | "unavailable" | "invalid-response" | "unexpected" };

export type ProjectCreateActionState = {
  status: "error";
  kind: "invalid-input" | "invalid-selection" | "conflict" | "unauthorized" | "forbidden" | "unavailable" | "invalid-response" | "unexpected";
  idempotencyKey: string;
  draft?: { title: string; charter: string };
};

const IDENTIFIER = /^[a-z0-9][a-z0-9._-]{0,127}$/;
const SEMVER = /^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$/;
const DIGEST = /^[a-f0-9]{64}$/;
const DATE_TIME = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.(\d{1,6}))?(Z|[+-](\d{2}):(\d{2}))$/;

function record(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function exactKeys(value: Record<string, unknown>, keys: readonly string[]) {
  const actual = Object.keys(value).sort();
  return actual.length === keys.length && keys.slice().sort().every((key, index) => key === actual[index]);
}

function text(value: unknown, minimum: number, maximum: number): value is string {
  return typeof value === "string" && value === value.trim() && value.length >= minimum && value.length <= maximum && !/[\0\r\n]/.test(value);
}

function timestamp(value: unknown): value is string {
  if (typeof value !== "string") return false;
  const match = DATE_TIME.exec(value);
  if (!match) return false;
  const [year, month, day, hour, minute, second, offsetHour, offsetMinute] = [
    match[1], match[2], match[3], match[4], match[5], match[6], match[9] ?? "00", match[10] ?? "00",
  ].map(Number);
  if (!year || !month || !day) return false;
  return month <= 12 && day <= new Date(Date.UTC(year, month, 0)).getUTCDate()
    && hour! <= 23 && minute! <= 59 && second! <= 59 && offsetHour! <= 23 && offsetMinute! <= 59
    && !Number.isNaN(Date.parse(value));
}

export function projectIdentifierIsSafe(value: unknown): value is string {
  return typeof value === "string" && IDENTIFIER.test(value);
}

function learningOriginIsSafe(value: unknown): value is components["schemas"]["LearningProjectOriginModel"] {
  if (!record(value) || !exactKeys(value, [
    "origin_type", "project_brief_schema_version", "package_id", "package_version", "package_digest",
    "brief_id", "brief_version", "brief_digest", "curriculum_id", "curriculum_version",
    "curriculum_digest", "placement_id", "placement_version", "placement_digest", "brief_title", "brief_purpose",
  ])) return false;
  return value.origin_type === "learning" && value.project_brief_schema_version === "1.0.0"
    && [value.package_id, value.brief_id, value.curriculum_id, value.placement_id].every(projectIdentifierIsSafe)
    && [value.package_version, value.brief_version, value.curriculum_version, value.placement_version].every(
      (item) => typeof item === "string" && SEMVER.test(item),
    )
    && [value.package_digest, value.brief_digest, value.curriculum_digest, value.placement_digest].every(
      (item) => typeof item === "string" && DIGEST.test(item),
    )
    && text(value.brief_title, 1, 120) && text(value.brief_purpose, 1, 2000);
}

function originIsSafe(value: unknown): boolean {
  return record(value) && value.origin_type === "independent"
    ? exactKeys(value, ["origin_type"])
    : learningOriginIsSafe(value);
}

export function projectShellIsSafe(value: unknown): value is ProjectShell {
  if (!record(value) || !exactKeys(value, [
    "schema_version", "project_id", "learner_id", "title", "charter", "origin",
    "lifecycle", "revision", "created_at", "updated_at",
  ])) return false;
  return value.schema_version === "1.0.0"
    && projectIdentifierIsSafe(value.project_id)
    && projectIdentifierIsSafe(value.learner_id)
    && text(value.title, 1, 120)
    && text(value.charter, 1, 4000)
    && originIsSafe(value.origin)
    && value.lifecycle === "active"
    && Number.isInteger(value.revision) && Number(value.revision) >= 1
    && timestamp(value.created_at) && timestamp(value.updated_at);
}

export function learningProjectStartOptionIsSafe(value: unknown): value is LearningProjectStartOption {
  return record(value)
    && exactKeys(value, ["title", "purpose", "origin"])
    && text(value.title, 1, 120)
    && text(value.purpose, 1, 2000)
    && learningOriginIsSafe(value.origin)
    && value.title === value.origin.brief_title
    && value.purpose === value.origin.brief_purpose;
}

export function projectListIsSafe(value: unknown): value is { records: readonly ProjectShell[] } {
  if (!record(value) || !exactKeys(value, ["records"]) || !Array.isArray(value.records) || value.records.length > 500) return false;
  return value.records.every(projectShellIsSafe)
    && new Set(value.records.map((item) => item.project_id)).size === value.records.length;
}

export function learningStartOptionListIsSafe(value: unknown): value is { records: readonly LearningProjectStartOption[] } {
  if (!record(value) || !exactKeys(value, ["records"]) || !Array.isArray(value.records) || value.records.length > 500) return false;
  return value.records.every(learningProjectStartOptionIsSafe)
    && new Set(value.records.map((item) => item.origin.placement_id)).size === value.records.length;
}

export function readableProjectDate(value: string): string {
  return new Intl.DateTimeFormat("en", { day: "numeric", month: "short", timeZone: "UTC", year: "numeric" }).format(new Date(value));
}

import type { components } from "../../generated/api-client";


export type PersonalWorkspace =
  components["schemas"]["PersonalWorkspaceResponseModel"];
export type PersonalWorkspaceRecord = PersonalWorkspace["records"][number];
export type PersonalWorkspaceCollection =
  PersonalWorkspace["collections"][number];
export type PersonalWorkspaceMutation =
  components["schemas"]["PersonalWorkspaceMutationRequestModel"]["mutation"];
export type PreparedWorkspaceRequest = {
  schema_version: "1.0.0";
  idempotency_key: string;
  expected_revision: number;
  mutation: PersonalWorkspaceMutation;
};

export type WorkspaceFailureKind =
  | "forbidden"
  | "invalid-response"
  | "invalid-selection"
  | "not-found"
  | "unauthorized"
  | "unavailable"
  | "unexpected";

export type WorkspaceRouteState =
  | { status: "ready"; workspace: PersonalWorkspace }
  | { status: WorkspaceFailureKind };

export type SaveSelection =
  | {
      kind: "learning_opportunity";
      opportunityId: string;
      placementId: string;
      returnTo: string;
    }
  | {
      kind: "placed_lesson";
      placementId: string;
      returnTo: string;
    };

export type SaveLearningRouteState =
  | { status: "ready"; selection: SaveSelection; workspace: PersonalWorkspace }
  | { status: WorkspaceFailureKind };

export type WorkspaceActionFailure =
  | "conflict"
  | "forbidden"
  | "invalid"
  | "invalid-response"
  | "not-found"
  | "source-unavailable"
  | "stale"
  | "unauthorized"
  | "unavailable"
  | "unexpected";

export type WorkspaceActionState = {
  status: "error";
  kind: WorkspaceActionFailure;
  intent: string;
  preparedRequest?: PreparedWorkspaceRequest;
};

const DIGEST = /^[a-f0-9]{64}$/;
const CURRICULUM_ID = /^[a-z0-9][a-z0-9._-]{2,63}$/;
const PLATFORM_ID = /^[a-z0-9][a-z0-9._-]{0,127}$/;
const SEMANTIC_VERSION = /^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?$/;
const DATE = /^\d{4}-\d{2}-\d{2}$/;
const UTC_DATE_TIME = /^(\d{4}-\d{2}-\d{2})[Tt](\d{2}):(\d{2}):(\d{2})(?:\.\d+)?Z$/;
const PROJECT_ARTIFACT_KINDS = new Set([
  "code",
  "dataset",
  "environment",
  "notebook",
  "reflection",
  "result",
  "supporting_file",
]);
const PROJECT_MEDIA_TYPES = new Set([
  "application/json",
  "application/octet-stream",
  "application/pdf",
  "application/x-ipynb+json",
  "text/csv",
  "text/markdown",
  "text/plain",
  "text/x-python",
]);
const PROJECT_INSPECTION_MODES = new Set(["metadata_only", "plain_text"]);

function hasNullCharacter(value: string): boolean {
  return value.includes("\u0000");
}

function record(value: unknown): Record<string, unknown> | undefined {
  return typeof value === "object" && value !== null && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : undefined;
}

function boundedString(
  value: unknown,
  minimum: number,
  maximum: number,
): value is string {
  return (
    typeof value === "string" &&
    Array.from(value).length >= minimum &&
    Array.from(value).length <= maximum &&
    !hasNullCharacter(value)
  );
}

function hasOnlyKeys(value: Record<string, unknown>, keys: readonly string[]): boolean {
  const accepted = new Set(keys);
  return Object.keys(value).every((key) => accepted.has(key));
}

export function workspaceIdentifierIsSafe(value: unknown): value is string {
  return typeof value === "string" && PLATFORM_ID.test(value);
}

export function curriculumIdentifierIsSafe(value: unknown): value is string {
  return typeof value === "string" && CURRICULUM_ID.test(value);
}

function utcDateTimeIsSafe(value: unknown): value is string {
  if (typeof value !== "string") return false;
  const matched = UTC_DATE_TIME.exec(value);
  if (!matched) return false;
  const [, date, hour, minute, second] = matched;
  return Boolean(
    dateIsSafe(date) &&
      Number(hour) <= 23 &&
      Number(minute) <= 59 &&
      Number(second) <= 59 &&
      Number.isFinite(Date.parse(value)),
  );
}

function dateIsSafe(value: unknown): value is string {
  if (typeof value !== "string" || !DATE.test(value)) return false;
  const parsed = new Date(`${value}T00:00:00Z`);
  return Number.isFinite(parsed.valueOf()) && parsed.toISOString().slice(0, 10) === value;
}

function referenceDestinationIsSafe(value: unknown): value is string {
  if (typeof value !== "string") return false;
  const matched = /^\/learn\/placements\/([^/?#]+)$/.exec(value);
  return Boolean(matched?.[1] && CURRICULUM_ID.test(matched[1]));
}

function positiveInteger(value: unknown): value is number {
  return Number.isSafeInteger(value) && Number(value) >= 1;
}

function projectLogicalPathIsSafe(value: unknown): value is string {
  if (
    typeof value !== "string" ||
    Array.from(value).length < 1 ||
    Array.from(value).length > 240 ||
    value.normalize("NFC") !== value
  ) {
    return false;
  }
  const reserved = /^(?:con|prn|aux|nul|com[1-9¹²³]|lpt[1-9¹²³])(?:\..*)?$/i;
  return (
    !value.includes("\\") &&
    !value.startsWith("/") &&
    value.split("/").every(
      (segment) =>
        segment !== "" &&
        segment !== "." &&
        segment !== ".." &&
        segment === segment.trim() &&
        !segment.endsWith(".") &&
        ![...segment].some(
          (character) =>
            character.charCodeAt(0) < 32 || '<>:"|?*'.includes(character),
        ) &&
        !reserved.test(segment),
    )
  );
}

function projectReferenceBaseIsSafe(
  candidate: Record<string, unknown>,
): boolean {
  return (
    candidate.owner_module === "project" &&
    candidate.lifecycle === "active" &&
    candidate.target_status === "available" &&
    workspaceIdentifierIsSafe(candidate.project_id) &&
    boundedString(candidate.title, 1, 240) &&
    positiveInteger(candidate.project_revision) &&
    positiveInteger(candidate.workspace_revision) &&
    utcDateTimeIsSafe(candidate.validated_at)
  );
}

function projectReferenceIsSafe(candidate: Record<string, unknown>): boolean {
  if (!projectReferenceBaseIsSafe(candidate)) return false;
  const projectId = String(candidate.project_id);
  if (candidate.reference_kind === "project_workspace") {
    return (
      hasOnlyKeys(candidate, [
        "reference_kind",
        "owner_module",
        "project_id",
        "title",
        "lifecycle",
        "project_revision",
        "workspace_revision",
        "destination",
        "target_status",
        "validated_at",
      ]) && candidate.destination === `/projects/${projectId}#workspace`
    );
  }
  if (candidate.reference_kind === "project_snapshot") {
    return (
      hasOnlyKeys(candidate, [
        "reference_kind",
        "owner_module",
        "project_id",
        "snapshot_id",
        "title",
        "lifecycle",
        "project_revision",
        "workspace_revision",
        "snapshot_digest",
        "closed_at",
        "destination",
        "target_status",
        "validated_at",
      ]) &&
      workspaceIdentifierIsSafe(candidate.snapshot_id) &&
      typeof candidate.snapshot_digest === "string" &&
      DIGEST.test(candidate.snapshot_digest) &&
      utcDateTimeIsSafe(candidate.closed_at) &&
      Date.parse(String(candidate.closed_at)) <=
        Date.parse(String(candidate.validated_at)) &&
      candidate.destination ===
        `/projects/${projectId}#snapshot-${String(candidate.snapshot_id)}`
    );
  }
  if (candidate.reference_kind === "project_artifact") {
    return (
      hasOnlyKeys(candidate, [
        "reference_kind",
        "owner_module",
        "project_id",
        "artifact_id",
        "artifact_version",
        "title",
        "lifecycle",
        "project_revision",
        "workspace_revision",
        "artifact_kind",
        "logical_path",
        "media_type",
        "inspection_mode",
        "byte_count",
        "content_digest",
        "created_at",
        "destination",
        "target_status",
        "validated_at",
      ]) &&
      workspaceIdentifierIsSafe(candidate.artifact_id) &&
      positiveInteger(candidate.artifact_version) &&
      typeof candidate.artifact_kind === "string" &&
      PROJECT_ARTIFACT_KINDS.has(candidate.artifact_kind) &&
      projectLogicalPathIsSafe(candidate.logical_path) &&
      typeof candidate.media_type === "string" &&
      PROJECT_MEDIA_TYPES.has(candidate.media_type) &&
      typeof candidate.inspection_mode === "string" &&
      PROJECT_INSPECTION_MODES.has(candidate.inspection_mode) &&
      Number.isSafeInteger(candidate.byte_count) &&
      Number(candidate.byte_count) >= 0 &&
      Number(candidate.byte_count) <= 10_485_760 &&
      typeof candidate.content_digest === "string" &&
      DIGEST.test(candidate.content_digest) &&
      utcDateTimeIsSafe(candidate.created_at) &&
      Date.parse(String(candidate.created_at)) <=
        Date.parse(String(candidate.validated_at)) &&
      candidate.destination ===
        `/projects/${projectId}#artifact-${String(candidate.artifact_id)}-v${String(candidate.artifact_version)}`
    );
  }
  return false;
}

function provenanceIsSafe(value: unknown): boolean {
  const candidate = record(value);
  return Boolean(
    candidate &&
      hasOnlyKeys(candidate, ["published_by", "published_at", "content_reviewed_on", "educational_use_notice"]) &&
      boundedString(candidate.published_by, 1, 160) &&
      utcDateTimeIsSafe(candidate.published_at) &&
      dateIsSafe(candidate.content_reviewed_on) &&
      boundedString(candidate.educational_use_notice, 1, 500),
  );
}

function referenceIsSafe(value: unknown): boolean {
  const candidate = record(value);
  if (
    candidate?.reference_kind === "project_workspace" ||
    candidate?.reference_kind === "project_snapshot" ||
    candidate?.reference_kind === "project_artifact"
  ) {
    return projectReferenceIsSafe(candidate);
  }
  if (
    !candidate ||
    !hasOnlyKeys(candidate, candidate.reference_kind === "learning_opportunity"
      ? ["reference_kind", "owner_module", "opportunity_id", "placement_id", "package_id", "package_version", "package_digest", "source_fingerprint", "title", "destination", "target_status", "provenance", "validated_at"]
      : ["reference_kind", "owner_module", "placement_id", "package_id", "package_version", "package_digest", "title", "destination", "target_status", "provenance", "validated_at"]) ||
    candidate.owner_module !== "curriculum" ||
    candidate.target_status !== "available" ||
    !curriculumIdentifierIsSafe(candidate.placement_id) ||
    !curriculumIdentifierIsSafe(candidate.package_id) ||
    typeof candidate.package_version !== "string" ||
    !SEMANTIC_VERSION.test(candidate.package_version) ||
    typeof candidate.package_digest !== "string" ||
    !DIGEST.test(candidate.package_digest) ||
    !boundedString(candidate.title, 1, 240) ||
    !referenceDestinationIsSafe(candidate.destination) ||
    candidate.destination !== `/learn/placements/${String(candidate.placement_id)}` ||
    !utcDateTimeIsSafe(candidate.validated_at) ||
    !provenanceIsSafe(candidate.provenance)
  ) {
    return false;
  }
  if (candidate.reference_kind === "placed_lesson") return true;
  return (
    candidate.reference_kind === "learning_opportunity" &&
    curriculumIdentifierIsSafe(candidate.opportunity_id) &&
    typeof candidate.source_fingerprint === "string" &&
    DIGEST.test(candidate.source_fingerprint)
  );
}

function workspaceRecordIsSafe(value: unknown): value is PersonalWorkspaceRecord {
  const candidate = record(value);
  if (
    !candidate ||
    !hasOnlyKeys(candidate, ["record_kind", "record_id", ...(candidate.record_kind === "note" ? ["title", "body"] : ["label"]), "target", "archived", "created_at", "updated_at"]) ||
    !workspaceIdentifierIsSafe(candidate.record_id) ||
    typeof candidate.archived !== "boolean" ||
    !utcDateTimeIsSafe(candidate.created_at) ||
    !utcDateTimeIsSafe(candidate.updated_at) ||
    Date.parse(candidate.created_at) > Date.parse(candidate.updated_at) ||
    !referenceIsSafe(candidate.target)
  ) {
    return false;
  }
  if (candidate.record_kind === "note") {
    return (
      boundedString(candidate.title, 1, 120) &&
      boundedString(candidate.body, 1, 8_000)
    );
  }
  return (
    candidate.record_kind === "bookmark" &&
    (candidate.label === null || boundedString(candidate.label, 0, 120))
  );
}

function collectionIsSafe(value: unknown): value is PersonalWorkspaceCollection {
  const candidate = record(value);
  return Boolean(
    candidate &&
      hasOnlyKeys(candidate, ["collection_id", "title", "member_record_ids", "created_at", "updated_at"]) &&
      workspaceIdentifierIsSafe(candidate.collection_id) &&
      boundedString(candidate.title, 1, 120) &&
      utcDateTimeIsSafe(candidate.created_at) &&
      utcDateTimeIsSafe(candidate.updated_at) &&
      Date.parse(candidate.created_at as string) <=
        Date.parse(candidate.updated_at as string) &&
      Array.isArray(candidate.member_record_ids) &&
      candidate.member_record_ids.length <= 100 &&
      candidate.member_record_ids.every(workspaceIdentifierIsSafe) &&
      new Set(candidate.member_record_ids).size ===
        candidate.member_record_ids.length,
  );
}

export function personalWorkspaceIsSafe(
  value: unknown,
): value is PersonalWorkspace {
  const candidate = record(value);
  if (
    !candidate ||
    !hasOnlyKeys(candidate, ["schema_version", "workspace_id", "learner_id", "revision", "records", "collections", "created_at", "updated_at", "workspace_digest"]) ||
    candidate.schema_version !== "1.0.0" ||
    !workspaceIdentifierIsSafe(candidate.workspace_id) ||
    !workspaceIdentifierIsSafe(candidate.learner_id) ||
    !Number.isInteger(candidate.revision) ||
    Number(candidate.revision) < 1 ||
    !utcDateTimeIsSafe(candidate.created_at) ||
    !utcDateTimeIsSafe(candidate.updated_at) ||
    Date.parse(candidate.created_at) > Date.parse(candidate.updated_at) ||
    typeof candidate.workspace_digest !== "string" ||
    !DIGEST.test(candidate.workspace_digest) ||
    !Array.isArray(candidate.records) ||
    candidate.records.length > 200 ||
    !candidate.records.every(workspaceRecordIsSafe) ||
    !Array.isArray(candidate.collections) ||
    candidate.collections.length > 50 ||
    !candidate.collections.every(collectionIsSafe)
  ) {
    return false;
  }
  const recordIds = candidate.records.map((item) => item.record_id);
  const collectionIds = candidate.collections.map((item) => item.collection_id);
  if (
    new Set(recordIds).size !== recordIds.length ||
    new Set(collectionIds).size !== collectionIds.length
  ) {
    return false;
  }
  const acceptedRecords = new Set(recordIds);
  return candidate.collections.every((collection) =>
    collection.member_record_ids.every((memberId) =>
      acceptedRecords.has(memberId),
    ),
  );
}

function one(search: URLSearchParams, name: string): string | undefined {
  const values = search.getAll(name);
  return values.length === 1 && values[0] ? values[0] : undefined;
}

function returnPathIsSafe(value: string | undefined): value is string {
  const matched = value
    ? /^\/learn\/(?:opportunities|placements)\/([^/?#]+)$/.exec(value)
    : null;
  return Boolean(
    value &&
      (value === "/learn" || (matched?.[1] && CURRICULUM_ID.test(matched[1]))) &&
      !hasNullCharacter(value) &&
      Array.from(value).length <= 512,
  );
}

export function parseSaveSelection(url: URL): SaveSelection | undefined {
  const kind = one(url.searchParams, "kind");
  const placementId = one(url.searchParams, "placement");
  const returnToValue = one(url.searchParams, "return");
  const returnTo = returnPathIsSafe(returnToValue) ? returnToValue : "/learn";
  if (!placementId || !CURRICULUM_ID.test(placementId)) return undefined;
  if (kind === "lesson") {
    return { kind: "placed_lesson", placementId, returnTo };
  }
  const opportunityId = one(url.searchParams, "opportunity");
  if (
    kind === "opportunity" &&
    opportunityId &&
    CURRICULUM_ID.test(opportunityId)
  ) {
    return {
      kind: "learning_opportunity",
      opportunityId,
      placementId,
      returnTo,
    };
  }
  return undefined;
}

export function readableWorkspaceDate(value: string): string {
  return new Intl.DateTimeFormat("en", {
    day: "numeric",
    month: "short",
    timeZone: "UTC",
    year: "numeric",
  }).format(new Date(value));
}

export function mutationErrorCode(value: unknown): string | undefined {
  const candidate = record(value);
  return typeof candidate?.code === "string" ? candidate.code : undefined;
}

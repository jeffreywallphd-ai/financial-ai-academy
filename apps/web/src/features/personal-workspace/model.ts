import type { components } from "../../generated/api-client";


export type PersonalWorkspace =
  components["schemas"]["PersonalWorkspaceResponseModel"];
export type PersonalWorkspaceRecord = PersonalWorkspace["records"][number];
export type PersonalWorkspaceCollection =
  PersonalWorkspace["collections"][number];
export type PersonalWorkspaceMutation =
  components["schemas"]["PersonalWorkspaceMutationRequestModel"]["mutation"];
export type PersonalWorkspaceQuery =
  components["schemas"]["PersonalWorkspaceQueryRequestModel"];
export type PersonalWorkspaceQueryResult =
  components["schemas"]["PersonalWorkspaceQueryResponseModel"];
export type PreparedWorkspaceRequest = {
  schema_version: "1.0.0";
  idempotency_key: string;
  expected_revision: number;
  mutation: PersonalWorkspaceMutation;
};

export type WorkspaceFailureKind =
  | "forbidden"
  | "invalid-response"
  | "invalid-query"
  | "invalid-selection"
  | "not-found"
  | "unauthorized"
  | "unavailable"
  | "unexpected";

export type WorkspaceRouteState =
  | {
      status: "ready";
      workspace: PersonalWorkspace;
      query: PersonalWorkspaceQuery;
      result: PersonalWorkspaceQueryResult;
      search: WorkspaceSearchValues;
    }
  | { status: WorkspaceFailureKind };

export type WorkspaceSearchValues = {
  archived?: "active" | "archived";
  collectionId?: string;
  cursor?: string;
  limit?: number;
  ownerModule?: "curriculum" | "project";
  recordKind?: "note" | "bookmark";
  referenceKind?:
    | "learning_opportunity"
    | "placed_lesson"
    | "project_workspace"
    | "project_snapshot"
    | "project_artifact";
  sort?:
    | "workspace_order"
    | "updated_desc"
    | "updated_asc"
    | "title_asc"
    | "source_asc";
  targetStatus?: "available" | "stale" | "unavailable";
  text?: string;
};

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
    }
  | {
      kind: "project_workspace";
      projectId: string;
      returnTo: string;
    }
  | {
      kind: "project_snapshot";
      projectId: string;
      snapshotId: string;
      returnTo: string;
    }
  | {
      kind: "project_artifact";
      projectId: string;
      artifactId: string;
      artifactVersion: number;
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
const TARGET_STATUSES = new Set(["available", "stale", "unavailable"]);

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

function targetStatusIsSafe(value: unknown): value is "available" | "stale" | "unavailable" {
  return typeof value === "string" && TARGET_STATUSES.has(value);
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
    targetStatusIsSafe(candidate.target_status) &&
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
    !targetStatusIsSafe(candidate.target_status) ||
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

const RECORD_KINDS = new Set(["note", "bookmark"]);
const OWNER_MODULES = new Set(["curriculum", "project"]);
const REFERENCE_KINDS = new Set([
  "learning_opportunity",
  "placed_lesson",
  "project_workspace",
  "project_snapshot",
  "project_artifact",
]);
const QUERY_SORTS = new Set([
  "workspace_order",
  "updated_desc",
  "updated_asc",
  "title_asc",
  "source_asc",
]);
const CURSOR = /^[A-Za-z0-9_-]{1,512}$/;

function closedArray(
  value: unknown,
  accepted: ReadonlySet<string>,
  maximum: number,
): value is readonly string[] {
  return (
    Array.isArray(value) &&
    value.length >= 1 &&
    value.length <= maximum &&
    value.every((item) => typeof item === "string" && accepted.has(item)) &&
    new Set(value).size === value.length
  );
}

export function personalWorkspaceQueryIsSafe(
  value: unknown,
): value is PersonalWorkspaceQuery {
  const candidate = record(value);
  if (
    !candidate ||
    !hasOnlyKeys(candidate, [
      "schema_version",
      "text",
      "record_kinds",
      "owner_modules",
      "reference_kinds",
      "target_statuses",
      "archived",
      "collection_id",
      "sort",
      "limit",
      "cursor",
    ]) ||
    candidate.schema_version !== "1.0.0"
  ) {
    return false;
  }
  return (
    (candidate.text === undefined || boundedString(candidate.text, 1, 240)) &&
    (candidate.record_kinds === undefined || closedArray(candidate.record_kinds, RECORD_KINDS, 2)) &&
    (candidate.owner_modules === undefined || closedArray(candidate.owner_modules, OWNER_MODULES, 2)) &&
    (candidate.reference_kinds === undefined || closedArray(candidate.reference_kinds, REFERENCE_KINDS, 5)) &&
    (candidate.target_statuses === undefined || closedArray(candidate.target_statuses, TARGET_STATUSES, 3)) &&
    (candidate.archived === undefined || typeof candidate.archived === "boolean") &&
    (candidate.collection_id === undefined || workspaceIdentifierIsSafe(candidate.collection_id)) &&
    (candidate.sort === undefined || (typeof candidate.sort === "string" && QUERY_SORTS.has(candidate.sort))) &&
    (candidate.limit === undefined || (positiveInteger(candidate.limit) && Number(candidate.limit) <= 100)) &&
    (candidate.cursor === undefined || (typeof candidate.cursor === "string" && CURSOR.test(candidate.cursor)))
  );
}

export function personalWorkspaceQueryResultIsSafe(
  value: unknown,
): value is PersonalWorkspaceQueryResult {
  const candidate = record(value);
  if (
    !candidate ||
    !hasOnlyKeys(candidate, [
      "schema_version",
      "workspace_revision",
      "query_digest",
      "applied_query",
      "records",
      "next_cursor",
    ]) ||
    candidate.schema_version !== "1.0.0" ||
    !positiveInteger(candidate.workspace_revision) ||
    typeof candidate.query_digest !== "string" ||
    !DIGEST.test(candidate.query_digest) ||
    !personalWorkspaceQueryIsSafe(candidate.applied_query) ||
    !Array.isArray(candidate.records) ||
    candidate.records.length > 100 ||
    !candidate.records.every(workspaceRecordIsSafe) ||
    candidate.records.length > Number(candidate.applied_query.limit ?? 50) ||
    !(
      candidate.next_cursor === null ||
      (typeof candidate.next_cursor === "string" && CURSOR.test(candidate.next_cursor))
    )
  ) {
    return false;
  }
  const recordIds = candidate.records.map((item) => item.record_id);
  return new Set(recordIds).size === recordIds.length;
}

function pythonSplitWhitespace(character: string): boolean {
  const codePoint = character.codePointAt(0)!;
  return (
    (codePoint >= 0x0009 && codePoint <= 0x000d) ||
    (codePoint >= 0x001c && codePoint <= 0x0020) ||
    codePoint === 0x0085 ||
    codePoint === 0x00a0 ||
    codePoint === 0x1680 ||
    (codePoint >= 0x2000 && codePoint <= 0x200a) ||
    codePoint === 0x2028 ||
    codePoint === 0x2029 ||
    codePoint === 0x202f ||
    codePoint === 0x205f ||
    codePoint === 0x3000
  );
}

function collapsePythonWhitespace(value: string): string {
  const parts: string[] = [];
  let part = "";
  for (const character of value) {
    if (pythonSplitWhitespace(character)) {
      if (part) parts.push(part);
      part = "";
    } else {
      part += character;
    }
  }
  if (part) parts.push(part);
  return parts.join(" ");
}

function normalizedQueryText(value: string): string {
  const casefolded = Array.from(value.normalize("NFKC"), (character) => {
    const codePoint = character.codePointAt(0)!;
    if (
      (codePoint >= 0x13a0 && codePoint <= 0x13f5) ||
      (codePoint >= 0x13f8 && codePoint <= 0x13fd) ||
      (codePoint >= 0xab70 && codePoint <= 0xabbf)
    ) {
      return character.toUpperCase();
    }
    if (character === "ı") return character;
    return character.toUpperCase().toLowerCase().replaceAll("ß", "ss");
  }).join("");
  return collapsePythonWhitespace(casefolded);
}

function normalizedWorkspaceQuery(
  query: PersonalWorkspaceQuery,
): PersonalWorkspaceQuery {
  return {
    schema_version: "1.0.0",
    ...(query.text === undefined ? {} : { text: normalizedQueryText(query.text) }),
    ...(query.record_kinds === undefined ? {} : { record_kinds: [...query.record_kinds].sort() }),
    ...(query.owner_modules === undefined ? {} : { owner_modules: [...query.owner_modules].sort() }),
    ...(query.reference_kinds === undefined ? {} : { reference_kinds: [...query.reference_kinds].sort() }),
    ...(query.target_statuses === undefined ? {} : { target_statuses: [...query.target_statuses].sort() }),
    ...(query.archived === undefined ? {} : { archived: query.archived }),
    ...(query.collection_id === undefined ? {} : { collection_id: query.collection_id }),
    sort: query.sort ?? "workspace_order",
    limit: query.limit ?? 50,
    ...(query.cursor === undefined ? {} : { cursor: query.cursor }),
  };
}

function canonicalJson(value: unknown): string {
  if (Array.isArray(value)) {
    return `[${value.map(canonicalJson).join(",")}]`;
  }
  if (value !== null && typeof value === "object") {
    const candidate = value as Record<string, unknown>;
    return `{${Object.keys(candidate)
      .sort()
      .map((key) => `${JSON.stringify(key)}:${canonicalJson(candidate[key])}`)
      .join(",")}}`;
  }
  return JSON.stringify(value);
}

export function personalWorkspaceQueriesMatch(
  requested: PersonalWorkspaceQuery,
  applied: PersonalWorkspaceQuery,
): boolean {
  return canonicalJson(normalizedWorkspaceQuery(requested)) ===
    canonicalJson(normalizedWorkspaceQuery(applied));
}

export async function personalWorkspaceQueryDigest(
  query: PersonalWorkspaceQuery,
): Promise<string> {
  const normalized = normalizedWorkspaceQuery(query);
  const material: Record<string, unknown> = {
    schema_version: normalized.schema_version,
    ...(normalized.text === undefined ? {} : { text: normalized.text }),
    ...(normalized.record_kinds === undefined ? {} : { record_kinds: normalized.record_kinds }),
    ...(normalized.owner_modules === undefined ? {} : { owner_modules: normalized.owner_modules }),
    ...(normalized.reference_kinds === undefined ? {} : { reference_kinds: normalized.reference_kinds }),
    ...(normalized.target_statuses === undefined ? {} : { target_statuses: normalized.target_statuses }),
    ...(normalized.archived === undefined ? {} : { archived: normalized.archived }),
    ...(normalized.collection_id === undefined ? {} : { collection_id: normalized.collection_id }),
    ...(normalized.sort === "workspace_order" ? {} : { sort: normalized.sort }),
    ...(normalized.limit === 50 ? {} : { limit: normalized.limit }),
  };
  const digest = await globalThis.crypto.subtle.digest(
    "SHA-256",
    new TextEncoder().encode(canonicalJson(material)),
  );
  return Array.from(new Uint8Array(digest), (byte) => byte.toString(16).padStart(2, "0")).join("");
}

const BROWSER_QUERY_FIELDS = new Set([
  "q",
  "record",
  "source",
  "kind",
  "status",
  "archive",
  "collection",
  "sort",
  "limit",
  "cursor",
]);

function optionalBrowserValue(search: URLSearchParams, name: string): string | undefined {
  const values = search.getAll(name);
  if (values.length > 1) return undefined;
  return values[0] || undefined;
}

export function parseWorkspaceSearch(
  url: URL,
): { query: PersonalWorkspaceQuery; search: WorkspaceSearchValues } | undefined {
  for (const key of url.searchParams.keys()) {
    if (!BROWSER_QUERY_FIELDS.has(key) || url.searchParams.getAll(key).length > 1) {
      return undefined;
    }
  }
  const text = optionalBrowserValue(url.searchParams, "q");
  const recordKind = optionalBrowserValue(url.searchParams, "record");
  const ownerModule = optionalBrowserValue(url.searchParams, "source");
  const referenceKind = optionalBrowserValue(url.searchParams, "kind");
  const targetStatus = optionalBrowserValue(url.searchParams, "status");
  const archived = optionalBrowserValue(url.searchParams, "archive");
  const collectionId = optionalBrowserValue(url.searchParams, "collection");
  const sort = optionalBrowserValue(url.searchParams, "sort");
  const limitValue = optionalBrowserValue(url.searchParams, "limit");
  const cursor = optionalBrowserValue(url.searchParams, "cursor");
  const limit = limitValue === undefined ? 50 : positiveQueryInteger(limitValue);
  const normalizedText = text === undefined ? undefined : normalizedQueryText(text);
  if (
    (text !== undefined && (
      !boundedString(text, 1, 240) ||
      normalizedText === undefined ||
      !boundedString(normalizedText, 1, 240)
    )) ||
    (recordKind !== undefined && !RECORD_KINDS.has(recordKind)) ||
    (ownerModule !== undefined && !OWNER_MODULES.has(ownerModule)) ||
    (referenceKind !== undefined && !REFERENCE_KINDS.has(referenceKind)) ||
    (targetStatus !== undefined && !TARGET_STATUSES.has(targetStatus)) ||
    (archived !== undefined && archived !== "active" && archived !== "archived") ||
    (collectionId !== undefined && !workspaceIdentifierIsSafe(collectionId)) ||
    (sort !== undefined && !QUERY_SORTS.has(sort)) ||
    limit === undefined ||
    limit > 100 ||
    (cursor !== undefined && !CURSOR.test(cursor))
  ) {
    return undefined;
  }
  const search: WorkspaceSearchValues = {
    ...(text === undefined ? {} : { text }),
    ...(recordKind === undefined ? {} : { recordKind: recordKind as NonNullable<WorkspaceSearchValues["recordKind"]> }),
    ...(ownerModule === undefined ? {} : { ownerModule: ownerModule as NonNullable<WorkspaceSearchValues["ownerModule"]> }),
    ...(referenceKind === undefined ? {} : { referenceKind: referenceKind as NonNullable<WorkspaceSearchValues["referenceKind"]> }),
    ...(targetStatus === undefined ? {} : { targetStatus: targetStatus as NonNullable<WorkspaceSearchValues["targetStatus"]> }),
    ...(archived === undefined ? {} : { archived: archived as NonNullable<WorkspaceSearchValues["archived"]> }),
    ...(collectionId === undefined ? {} : { collectionId }),
    ...(sort === undefined ? {} : { sort: sort as NonNullable<WorkspaceSearchValues["sort"]> }),
    ...(limitValue === undefined ? {} : { limit }),
    ...(cursor === undefined ? {} : { cursor }),
  };
  const query: PersonalWorkspaceQuery = {
    schema_version: "1.0.0",
    limit,
    sort: search.sort ?? "workspace_order",
    ...(normalizedText === undefined ? {} : { text: normalizedText }),
    ...(search.recordKind === undefined ? {} : { record_kinds: [search.recordKind] }),
    ...(search.ownerModule === undefined ? {} : { owner_modules: [search.ownerModule] }),
    ...(search.referenceKind === undefined ? {} : { reference_kinds: [search.referenceKind] }),
    ...(search.targetStatus === undefined ? {} : { target_statuses: [search.targetStatus] }),
    ...(search.archived === undefined ? {} : { archived: search.archived === "archived" }),
    ...(search.collectionId === undefined ? {} : { collection_id: search.collectionId }),
    ...(search.cursor === undefined ? {} : { cursor: search.cursor }),
  };
  return { query, search };
}

export function workspaceSearchHref(
  search: WorkspaceSearchValues,
  cursor?: string,
): string {
  const values = new URLSearchParams();
  if (search.text) values.set("q", search.text);
  if (search.recordKind) values.set("record", search.recordKind);
  if (search.ownerModule) values.set("source", search.ownerModule);
  if (search.referenceKind) values.set("kind", search.referenceKind);
  if (search.targetStatus) values.set("status", search.targetStatus);
  if (search.archived) values.set("archive", search.archived);
  if (search.collectionId) values.set("collection", search.collectionId);
  if (search.sort) values.set("sort", search.sort);
  if (search.limit) values.set("limit", String(search.limit));
  if (cursor) values.set("cursor", cursor);
  const query = values.toString();
  return query ? `/saved-learning?${query}` : "/saved-learning";
}

function one(search: URLSearchParams, name: string): string | undefined {
  const values = search.getAll(name);
  return values.length === 1 && values[0] ? values[0] : undefined;
}

function queryFieldsAreExact(
  search: URLSearchParams,
  required: readonly string[],
  optional: readonly string[] = [],
): boolean {
  const allowed = new Set([...required, ...optional]);
  for (const key of search.keys()) {
    if (!allowed.has(key)) return false;
  }
  return required.every((key) => search.getAll(key).length === 1) &&
    optional.every((key) => search.getAll(key).length <= 1);
}

function positiveQueryInteger(value: string | undefined): number | undefined {
  if (!value || !/^[1-9][0-9]*$/.test(value)) return undefined;
  const parsed = Number(value);
  return Number.isSafeInteger(parsed) ? parsed : undefined;
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
  const projectId = one(url.searchParams, "project");
  if (
    kind === "project_workspace" &&
    workspaceIdentifierIsSafe(projectId) &&
    queryFieldsAreExact(url.searchParams, ["kind", "project"])
  ) {
    return {
      kind,
      projectId,
      returnTo: `/projects/${projectId}#workspace`,
    };
  }
  const snapshotId = one(url.searchParams, "snapshot");
  if (
    kind === "project_snapshot" &&
    workspaceIdentifierIsSafe(projectId) &&
    workspaceIdentifierIsSafe(snapshotId) &&
    queryFieldsAreExact(url.searchParams, ["kind", "project", "snapshot"])
  ) {
    return {
      kind,
      projectId,
      snapshotId,
      returnTo: `/projects/${projectId}#snapshot-${snapshotId}`,
    };
  }
  const artifactId = one(url.searchParams, "artifact");
  const artifactVersion = positiveQueryInteger(one(url.searchParams, "version"));
  if (
    kind === "project_artifact" &&
    workspaceIdentifierIsSafe(projectId) &&
    workspaceIdentifierIsSafe(artifactId) &&
    artifactVersion !== undefined &&
    queryFieldsAreExact(url.searchParams, ["kind", "project", "artifact", "version"])
  ) {
    return {
      kind,
      projectId,
      artifactId,
      artifactVersion,
      returnTo: `/projects/${projectId}#artifact-${artifactId}-v${artifactVersion}`,
    };
  }
  const placementId = one(url.searchParams, "placement");
  const returnToValue = one(url.searchParams, "return");
  const returnTo = returnPathIsSafe(returnToValue) ? returnToValue : "/learn";
  if (
    !placementId ||
    !CURRICULUM_ID.test(placementId) ||
    !queryFieldsAreExact(
      url.searchParams,
      kind === "opportunity" ? ["kind", "opportunity", "placement"] : ["kind", "placement"],
      ["return"],
    )
  ) return undefined;
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

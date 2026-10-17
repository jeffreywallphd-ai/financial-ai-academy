import type { components } from "../../generated/api-client";


export type PersonalWorkspace =
  components["schemas"]["PersonalWorkspaceResponseModel"];
export type PersonalWorkspaceRecord = PersonalWorkspace["records"][number];
export type PersonalWorkspaceCollection =
  PersonalWorkspace["collections"][number];
export type PersonalWorkspaceMutation =
  components["schemas"]["PersonalWorkspaceMutationRequestModel"]["mutation"];

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
  idempotencyKey: string;
  retryMutation?: PersonalWorkspaceMutation;
};

const DIGEST = /^[a-f0-9]{64}$/;
const OPPORTUNITY_ID = /^[a-z0-9][a-z0-9._-]{2,63}$/;
const PRODUCER_ID = /^[a-z0-9][a-z0-9._-]{2,63}$/;
const DATE = /^\d{4}-\d{2}-\d{2}$/;

function hasControlCharacter(value: string): boolean {
  return Array.from(value).some((character) => {
    const code = character.codePointAt(0) ?? 0;
    return code <= 0x1f || code === 0x7f;
  });
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
    value.length >= minimum &&
    value.length <= maximum &&
    !hasControlCharacter(value)
  );
}

export function workspaceIdentifierIsSafe(value: unknown): value is string {
  return (
    boundedString(value, 1, 128) &&
    value.trim() === value &&
    !/\s/.test(value)
  );
}

function utcDateTimeIsSafe(value: unknown): value is string {
  if (typeof value !== "string" || !value.endsWith("Z")) return false;
  const parsed = Date.parse(value);
  return Number.isFinite(parsed);
}

function dateIsSafe(value: unknown): value is string {
  if (typeof value !== "string" || !DATE.test(value)) return false;
  const parsed = new Date(`${value}T00:00:00Z`);
  return Number.isFinite(parsed.valueOf()) && parsed.toISOString().slice(0, 10) === value;
}

function safeDestination(value: unknown): value is string {
  if (typeof value !== "string") return false;
  const matched = /^\/learn\/(?:opportunities|placements)\/([^/?#]+)$/.exec(value);
  return Boolean(matched?.[1] && PRODUCER_ID.test(matched[1]));
}

function provenanceIsSafe(value: unknown): boolean {
  const candidate = record(value);
  return Boolean(
    candidate &&
      boundedString(candidate.published_by, 1, 200) &&
      utcDateTimeIsSafe(candidate.published_at) &&
      dateIsSafe(candidate.content_reviewed_on) &&
      boundedString(candidate.educational_use_notice, 1, 1_000),
  );
}

function referenceIsSafe(value: unknown): boolean {
  const candidate = record(value);
  if (
    !candidate ||
    candidate.owner_module !== "curriculum" ||
    candidate.target_status !== "available" ||
    !PRODUCER_ID.test(String(candidate.placement_id ?? "")) ||
    !PRODUCER_ID.test(String(candidate.package_id ?? "")) ||
    !boundedString(candidate.package_version, 1, 64) ||
    typeof candidate.package_digest !== "string" ||
    !DIGEST.test(candidate.package_digest) ||
    !boundedString(candidate.title, 1, 300) ||
    !safeDestination(candidate.destination) ||
    candidate.destination !== `/learn/placements/${String(candidate.placement_id)}` ||
    !utcDateTimeIsSafe(candidate.validated_at) ||
    !provenanceIsSafe(candidate.provenance)
  ) {
    return false;
  }
  if (candidate.reference_kind === "placed_lesson") return true;
  return (
    candidate.reference_kind === "learning_opportunity" &&
    typeof candidate.opportunity_id === "string" &&
    OPPORTUNITY_ID.test(candidate.opportunity_id) &&
    typeof candidate.source_fingerprint === "string" &&
    DIGEST.test(candidate.source_fingerprint)
  );
}

function workspaceRecordIsSafe(value: unknown): value is PersonalWorkspaceRecord {
  const candidate = record(value);
  if (
    !candidate ||
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
      boundedString(candidate.title, 1, 200) &&
      boundedString(candidate.body, 1, 10_000)
    );
  }
  return (
    candidate.record_kind === "bookmark" &&
    (candidate.label === null || boundedString(candidate.label, 1, 200))
  );
}

function collectionIsSafe(value: unknown): value is PersonalWorkspaceCollection {
  const candidate = record(value);
  return Boolean(
    candidate &&
      workspaceIdentifierIsSafe(candidate.collection_id) &&
      boundedString(candidate.title, 1, 200) &&
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
  return Boolean(
    value &&
      (value === "/learn" || safeDestination(value)) &&
      !hasControlCharacter(value) &&
      value.length <= 512,
  );
}

export function parseSaveSelection(url: URL): SaveSelection | undefined {
  const kind = one(url.searchParams, "kind");
  const placementId = one(url.searchParams, "placement");
  const returnToValue = one(url.searchParams, "return");
  const returnTo = returnPathIsSafe(returnToValue) ? returnToValue : "/learn";
  if (!placementId || !PRODUCER_ID.test(placementId)) return undefined;
  if (kind === "lesson") {
    return { kind: "placed_lesson", placementId, returnTo };
  }
  const opportunityId = one(url.searchParams, "opportunity");
  if (
    kind === "opportunity" &&
    opportunityId &&
    OPPORTUNITY_ID.test(opportunityId)
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

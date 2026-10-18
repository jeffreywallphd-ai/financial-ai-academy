import type { components } from "../../generated/api-client";

export type AccountableHistoryDocument =
  components["schemas"]["AccountableHistoryResponseModel"];
export type PortableEvidenceExport =
  components["schemas"]["PortableEvidenceExportResponseModel"];
export type PublishedLessonHistoryRequest =
  components["schemas"]["PublishedLessonLineageRequestModel"];
export type CompletionHistoryRequest =
  components["schemas"]["KnowledgeCheckCompletionLineageRequestModel"];
export type AccountableHistoryRequest =
  PublishedLessonHistoryRequest | CompletionHistoryRequest;

export type AccountableHistoryFailure =
  "forbidden" | "invalid-response" | "unauthorized" | "unavailable";

export type AccountableHistoryReadOutcome =
  | { status: "ready"; document: AccountableHistoryDocument }
  | { status: AccountableHistoryFailure };

export type AccountableHistoryExportOutcome =
  | { status: "ready"; record: PortableEvidenceExport }
  | { status: AccountableHistoryFailure };

const DIGEST = /^[a-f0-9]{64}$/;
const IDENTIFIER =
  // oxlint-disable-next-line no-control-regex -- Control and formatting characters are explicitly rejected at the browser trust boundary.
  /^[^\s._:/\\?#\u0000-\u001f\u007f-\u009f\u200b-\u200f\u202a-\u202e\u2060-\u206f\ufeff][^\s/\\?#\u0000-\u001f\u007f-\u009f\u200b-\u200f\u202a-\u202e\u2060-\u206f\ufeff]{0,127}$/u;
const VERSION = /^[A-Za-z0-9][A-Za-z0-9._+-]{0,79}$/;
const TIMESTAMP =
  /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-]\d{2}:\d{2})$/;
const EXPORT_TIMESTAMP = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?Z$/;
const TIMESTAMP_PARTS =
  /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.(\d{1,6}))?(?:Z|([+-])(\d{2}):(\d{2}))$/;
const SAFE_TEXT =
  // oxlint-disable-next-line no-control-regex -- Control and formatting characters are explicitly rejected at the browser trust boundary.
  /^[^<>\u0000-\u001f\u007f-\u009f\u061c\u200b-\u200f\u202a-\u202e\u2060-\u206f\ufeff]+$/u;
const FILE_STEM = /^[a-z0-9][a-z0-9-]{0,79}$/;

const ROLES = [
  "source",
  "published",
  "defined",
  "completed",
  "recorded",
] as const;
const RELATIONS = [
  "published_from",
  "defined_by",
  "produced",
  "recorded_as",
] as const;
const DIAGNOSTICS = [
  "missing_reference",
  "owner_unavailable",
  "unsupported_contract_version",
  "integrity_mismatch",
  "invalid_relation",
  "identity_conflict",
  "redacted_detail",
] as const;
const REDACTIONS = [
  "protected_content",
  "learner_private_identity",
  "owner_payload",
  "provider_or_secret_material",
  "internal_diagnostics",
  "storage_details",
] as const;

const ENTRY_OWNER = {
  educational_source: "content",
  published_lesson: "content",
  assessment_definition: "assessment",
  knowledge_check_event: "assessment",
  completion_evidence: "assessment",
  audit_reference: "audit",
} as const;

const VERSIONED_KINDS = new Set([
  "educational_source",
  "published_lesson",
  "assessment_definition",
]);

type UnknownRecord = Record<string, unknown>;

function record(value: unknown): UnknownRecord | null {
  return typeof value === "object" && value !== null && !Array.isArray(value)
    ? (value as UnknownRecord)
    : null;
}

function exactKeys(value: UnknownRecord, keys: readonly string[]): boolean {
  const actual = Object.keys(value).sort();
  const expected = [...keys].sort();
  return (
    actual.length === expected.length &&
    actual.every((key, index) => key === expected[index])
  );
}

function oneOf<T extends string>(
  value: unknown,
  choices: readonly T[],
): value is T {
  return typeof value === "string" && choices.includes(value as T);
}

function integerBetween(
  value: unknown,
  minimum: number,
  maximum: number,
): boolean {
  return (
    Number.isInteger(value) &&
    Number(value) >= minimum &&
    Number(value) <= maximum
  );
}

function text(value: unknown, maximum: number): value is string {
  return (
    typeof value === "string" &&
    Array.from(value).length >= 1 &&
    Array.from(value).length <= maximum &&
    SAFE_TEXT.test(value)
  );
}

function timestamp(value: unknown, canonicalUtc = false): value is string {
  const pattern = canonicalUtc ? EXPORT_TIMESTAMP : TIMESTAMP;
  if (typeof value !== "string" || !pattern.test(value)) return false;
  const parts = TIMESTAMP_PARTS.exec(value);
  if (!parts) return false;

  const year = Number(parts[1]);
  const month = Number(parts[2]);
  const day = Number(parts[3]);
  const hour = Number(parts[4]);
  const minute = Number(parts[5]);
  const second = Number(parts[6]);
  const offsetHour = parts[9] === undefined ? 0 : Number(parts[9]);
  const offsetMinute = parts[10] === undefined ? 0 : Number(parts[10]);
  const leapYear = year % 4 === 0 && (year % 100 !== 0 || year % 400 === 0);
  const daysInMonth = [
    31,
    leapYear ? 29 : 28,
    31,
    30,
    31,
    30,
    31,
    31,
    30,
    31,
    30,
    31,
  ];
  const maximumDay = daysInMonth[month - 1] ?? 0;

  return (
    year >= 1 &&
    month >= 1 &&
    month <= 12 &&
    day >= 1 &&
    day <= maximumDay &&
    hour <= 23 &&
    minute <= 59 &&
    second <= 59 &&
    offsetHour <= 23 &&
    offsetMinute <= 59
  );
}

function historyRequestIsSafe(
  value: unknown,
): value is AccountableHistoryRequest {
  const request = record(value);
  if (!request || request.schema_version !== "1.0.0") return false;
  if (request.root_kind === "published_lesson") {
    return (
      exactKeys(request, [
        "schema_version",
        "root_kind",
        "package_id",
        "package_version",
        "package_digest",
      ]) &&
      typeof request.package_id === "string" &&
      IDENTIFIER.test(request.package_id) &&
      typeof request.package_version === "string" &&
      VERSION.test(request.package_version) &&
      typeof request.package_digest === "string" &&
      DIGEST.test(request.package_digest)
    );
  }
  if (request.root_kind === "knowledge_check_completion") {
    return (
      exactKeys(request, [
        "schema_version",
        "root_kind",
        "placement_id",
        "evidence_id",
        "occurrence",
      ]) &&
      typeof request.placement_id === "string" &&
      IDENTIFIER.test(request.placement_id) &&
      typeof request.evidence_id === "string" &&
      IDENTIFIER.test(request.evidence_id) &&
      integerBetween(request.occurrence, 1, Number.MAX_SAFE_INTEGER)
    );
  }
  return false;
}

function rootMatches(
  value: unknown,
  request: AccountableHistoryRequest,
): boolean {
  const root = record(value);
  if (!root) return false;
  if (request.root_kind === "published_lesson") {
    return (
      exactKeys(root, ["root_kind", "resource_id", "resource_version"]) &&
      root.root_kind === request.root_kind &&
      root.resource_id === request.package_id &&
      root.resource_version === request.package_version
    );
  }
  return (
    exactKeys(root, ["root_kind", "resource_id", "occurrence"]) &&
    root.root_kind === request.root_kind &&
    root.resource_id === request.evidence_id &&
    root.occurrence === request.occurrence
  );
}

function entryMatchesRoot(
  value: unknown,
  request: AccountableHistoryRequest,
): boolean {
  const entry = record(value);
  if (!entry) return false;
  if (request.root_kind === "published_lesson") {
    return (
      entry.resource_kind === "published_lesson" &&
      entry.resource_id === request.package_id &&
      entry.resource_version === request.package_version
    );
  }
  return (
    entry.resource_kind === "completion_evidence" &&
    entry.resource_id === request.evidence_id &&
    entry.occurrence === request.occurrence
  );
}

function entryIsSafe(
  value: unknown,
  expectedSequence: number,
): value is AccountableHistoryDocument["entries"][number] {
  const entry = record(value);
  if (!entry || typeof entry.resource_kind !== "string") return false;
  const expectedOwner =
    ENTRY_OWNER[entry.resource_kind as keyof typeof ENTRY_OWNER];
  if (!expectedOwner) return false;
  const versioned = VERSIONED_KINDS.has(entry.resource_kind);
  const keys = [
    "sequence",
    "entry_id",
    "role",
    "title",
    "explanation",
    "owner_module",
    "resource_kind",
    "resource_id",
    versioned ? "resource_version" : "occurrence",
    "integrity_digest",
    "recorded_at",
    "validation_status",
  ];
  return (
    exactKeys(entry, keys) &&
    entry.sequence === expectedSequence &&
    typeof entry.entry_id === "string" &&
    IDENTIFIER.test(entry.entry_id) &&
    oneOf(entry.role, ROLES) &&
    text(entry.title, 160) &&
    text(entry.explanation, 500) &&
    entry.owner_module === expectedOwner &&
    typeof entry.resource_id === "string" &&
    IDENTIFIER.test(entry.resource_id) &&
    (versioned
      ? typeof entry.resource_version === "string" &&
        VERSION.test(entry.resource_version)
      : integerBetween(entry.occurrence, 1, Number.MAX_SAFE_INTEGER)) &&
    typeof entry.integrity_digest === "string" &&
    DIGEST.test(entry.integrity_digest) &&
    timestamp(entry.recorded_at) &&
    oneOf(entry.validation_status, ["validated", "incomplete"] as const)
  );
}

function documentIsSafe(
  value: unknown,
  request: AccountableHistoryRequest,
  purpose: AccountableHistoryDocument["purpose"],
): value is AccountableHistoryDocument {
  const document = record(value);
  if (
    !document ||
    !exactKeys(document, [
      "schema_version",
      "purpose",
      "root",
      "state",
      "title",
      "summary",
      "source_lineage_digest",
      "entries",
      "transformations",
      "missing_links",
      "diagnostics",
      "redactions",
      "history_digest",
    ])
  )
    return false;
  if (
    document.schema_version !== "1.0.0" ||
    document.purpose !== purpose ||
    !rootMatches(document.root, request) ||
    !oneOf(document.state, ["valid", "incomplete", "invalid"] as const) ||
    !text(document.title, 160) ||
    !text(document.summary, 500) ||
    typeof document.source_lineage_digest !== "string" ||
    !DIGEST.test(document.source_lineage_digest) ||
    typeof document.history_digest !== "string" ||
    !DIGEST.test(document.history_digest)
  )
    return false;

  if (
    !Array.isArray(document.entries) ||
    document.entries.length < 1 ||
    document.entries.length > 64 ||
    !document.entries.every((entry, index) => entryIsSafe(entry, index + 1))
  )
    return false;
  const entryIds = new Set(
    document.entries.map((entry) => record(entry)?.entry_id),
  );
  if (entryIds.size !== document.entries.length || entryIds.has(undefined))
    return false;
  if (
    document.entries.filter((entry) => entryMatchesRoot(entry, request))
      .length !== 1
  )
    return false;

  if (
    !Array.isArray(document.transformations) ||
    document.transformations.length > 128
  )
    return false;
  for (const value of document.transformations) {
    const transformation = record(value);
    if (
      !transformation ||
      !exactKeys(transformation, [
        "source_entry_id",
        "target_entry_id",
        "relation",
      ]) ||
      !entryIds.has(transformation.source_entry_id) ||
      !entryIds.has(transformation.target_entry_id) ||
      !oneOf(transformation.relation, RELATIONS)
    )
      return false;
  }

  if (
    !Array.isArray(document.missing_links) ||
    document.missing_links.length > 32
  )
    return false;
  for (const value of document.missing_links) {
    const link = record(value);
    if (
      !link ||
      !exactKeys(link, [
        "source_entry_id",
        "relation",
        "target_reference",
        "reason",
        "explanation",
      ]) ||
      !entryIds.has(link.source_entry_id) ||
      !oneOf(link.relation, RELATIONS) ||
      typeof link.target_reference !== "string" ||
      !IDENTIFIER.test(link.target_reference) ||
      !oneOf(link.reason, ["not_found", "unavailable", "redacted"] as const) ||
      !text(link.explanation, 500)
    )
      return false;
  }

  if (!Array.isArray(document.diagnostics) || document.diagnostics.length > 32)
    return false;
  for (const value of document.diagnostics) {
    const diagnostic = record(value);
    if (
      !diagnostic ||
      !exactKeys(diagnostic, ["code", "reference", "explanation"]) ||
      !oneOf(diagnostic.code, DIAGNOSTICS) ||
      typeof diagnostic.reference !== "string" ||
      !IDENTIFIER.test(diagnostic.reference) ||
      !text(diagnostic.explanation, 500)
    )
      return false;
  }

  if (!Array.isArray(document.redactions) || document.redactions.length > 6)
    return false;
  const redactionCategories = new Set<string>();
  for (const value of document.redactions) {
    const redaction = record(value);
    if (
      !redaction ||
      !exactKeys(redaction, ["category", "count"]) ||
      !oneOf(redaction.category, REDACTIONS) ||
      redactionCategories.has(redaction.category) ||
      !integerBetween(redaction.count, 1, 1_000_000)
    )
      return false;
    redactionCategories.add(redaction.category);
  }
  return true;
}

export function accountableHistoryDocumentIsSafe(
  value: unknown,
  request: AccountableHistoryRequest,
): value is AccountableHistoryDocument {
  return (
    historyRequestIsSafe(request) &&
    documentIsSafe(value, request, "learner_review")
  );
}

export function portableEvidenceExportIsSafe(
  value: unknown,
  request: AccountableHistoryRequest,
): value is PortableEvidenceExport {
  const wrapper = record(value);
  if (
    !historyRequestIsSafe(request) ||
    !wrapper ||
    !exactKeys(wrapper, [
      "schema_version",
      "media_type",
      "filename_stem",
      "exported_at",
      "document_digest",
      "document",
    ])
  )
    return false;
  if (
    wrapper.schema_version !== "1.0.0" ||
    wrapper.media_type !==
      "application/vnd.financial-ai-academy.accountable-history+json" ||
    typeof wrapper.filename_stem !== "string" ||
    !FILE_STEM.test(wrapper.filename_stem) ||
    !timestamp(wrapper.exported_at, true) ||
    typeof wrapper.document_digest !== "string" ||
    !DIGEST.test(wrapper.document_digest) ||
    !documentIsSafe(wrapper.document, request, "portable_evidence")
  )
    return false;
  return wrapper.document_digest === record(wrapper.document)?.history_digest;
}

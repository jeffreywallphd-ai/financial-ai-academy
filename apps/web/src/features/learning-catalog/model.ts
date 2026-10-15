import type { components } from "../../generated/api-client";

export type LearningCatalog =
  components["schemas"]["LearningOpportunityBrowseResponseModel"];
export type LearningOpportunity =
  components["schemas"]["LearningOpportunityResponseModel"];

export type LearningCatalogRouteState =
  | { status: "loading" }
  | { status: "ready"; catalog: LearningCatalog }
  | { status: "unauthorized" }
  | { status: "forbidden" }
  | { status: "unavailable" }
  | { status: "invalid-response" }
  | { status: "unexpected" };

const IDENTIFIER = /^[a-z0-9][a-z0-9._-]{2,63}$/;
const TOPIC = /^[a-z0-9][a-z0-9-]{1,49}$/;
const DIGEST = /^[a-f0-9]{64}$/;
const SEMANTIC_VERSION =
  /^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?$/;
const DESTINATION =
  /^\/learn\/placements\/[a-z0-9][a-z0-9._-]{2,63}$/;
const DATE = /^\d{4}-\d{2}-\d{2}$/;
const DATE_TIME =
  /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.\d{1,6})?(Z|[+-](\d{2}):(\d{2}))$/;

const BROWSE_KEYS = [
  "projected_at",
  "projection_generation",
  "records",
  "schema_version",
] as const;
const OPPORTUNITY_KEYS = [
  "availability",
  "availability_reason",
  "destination",
  "estimated_minutes",
  "kind",
  "level",
  "objectives",
  "opportunity_id",
  "package_digest",
  "package_id",
  "package_version",
  "placement_id",
  "prerequisite_summary",
  "projected_at",
  "provenance",
  "schema_version",
  "source_fingerprint",
  "summary",
  "title",
  "topics",
] as const;
const PROVENANCE_KEYS = [
  "content_reviewed_on",
  "educational_use_notice",
  "published_at",
  "published_by",
] as const;

function record(value: unknown): Record<string, unknown> | null {
  return typeof value === "object" && value !== null && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : null;
}

function hasExactKeys(
  value: Record<string, unknown>,
  expected: readonly string[],
): boolean {
  const actual = Object.keys(value).sort();
  const sortedExpected = [...expected].sort();
  return (
    actual.length === sortedExpected.length &&
    actual.every((key, index) => key === sortedExpected[index])
  );
}

function boundedText(
  value: unknown,
  minimum: number,
  maximum: number,
): value is string {
  return (
    typeof value === "string" &&
    value === value.trim() &&
    value.length >= minimum &&
    value.length <= maximum &&
    !/[\0\r\n]/.test(value)
  );
}

function validDate(value: unknown): value is string {
  if (typeof value !== "string" || !DATE.test(value)) {
    return false;
  }
  const parsed = new Date(value + "T00:00:00Z");
  return (
    !Number.isNaN(parsed.valueOf()) &&
    parsed.toISOString().slice(0, 10) === value
  );
}

function validDateTime(value: unknown): value is string {
  if (typeof value !== "string") {
    return false;
  }
  const match = DATE_TIME.exec(value);
  if (!match) {
    return false;
  }
  const [year, month, day, hour, minute, second, offsetHour, offsetMinute] = [
    match[1],
    match[2],
    match[3],
    match[4],
    match[5],
    match[6],
    match[8] ?? "00",
    match[9] ?? "00",
  ].map(Number);
  if (
    !year ||
    !month ||
    !day ||
    hour === undefined ||
    minute === undefined ||
    second === undefined ||
    offsetHour === undefined ||
    offsetMinute === undefined
  ) {
    return false;
  }
  const daysInMonth = new Date(Date.UTC(year, month, 0)).getUTCDate();
  return (
    month <= 12 &&
    day <= daysInMonth &&
    hour <= 23 &&
    minute <= 59 &&
    second <= 59 &&
    offsetHour <= 23 &&
    offsetMinute <= 59 &&
    !Number.isNaN(Date.parse(value))
  );
}

function uniqueStrings(
  value: unknown,
  minimumItems: number,
  maximumItems: number,
  itemIsValid: (item: unknown) => item is string,
): value is string[] {
  return (
    Array.isArray(value) &&
    value.length >= minimumItems &&
    value.length <= maximumItems &&
    value.every(itemIsValid) &&
    new Set(value).size === value.length
  );
}

function stringsAreStrictlySorted(values: readonly string[]): boolean {
  for (let index = 1; index < values.length; index += 1) {
    const previous = values[index - 1];
    const current = values[index];
    if (previous === undefined || current === undefined || previous >= current) {
      return false;
    }
  }
  return true;
}

function provenanceIsSafe(value: unknown): boolean {
  const candidate = record(value);
  return (
    candidate !== null &&
    hasExactKeys(candidate, PROVENANCE_KEYS) &&
    boundedText(candidate.published_by, 1, 160) &&
    validDateTime(candidate.published_at) &&
    validDate(candidate.content_reviewed_on) &&
    boundedText(candidate.educational_use_notice, 1, 500)
  );
}

function opportunityIsSafe(
  value: unknown,
  projectedAt: string,
): value is LearningOpportunity {
  const candidate = record(value);
  const objectivesAreSafe = uniqueStrings(
    candidate?.objectives,
    1,
    20,
    (item): item is string => boundedText(item, 1, 500),
  );
  const topicsAreSafe = uniqueStrings(
    candidate?.topics,
    1,
    8,
    (item): item is string => typeof item === "string" && TOPIC.test(item),
  );
  return (
    candidate !== null &&
    hasExactKeys(candidate, OPPORTUNITY_KEYS) &&
    candidate.schema_version === "1.0.0" &&
    typeof candidate.opportunity_id === "string" &&
    IDENTIFIER.test(candidate.opportunity_id) &&
    typeof candidate.placement_id === "string" &&
    IDENTIFIER.test(candidate.placement_id) &&
    typeof candidate.destination === "string" &&
    DESTINATION.test(candidate.destination) &&
    candidate.destination === "/learn/placements/" + candidate.placement_id &&
    ["course", "lesson", "lab", "project"].includes(String(candidate.kind)) &&
    boundedText(candidate.title, 1, 240) &&
    boundedText(candidate.summary, 20, 500) &&
    objectivesAreSafe &&
    topicsAreSafe &&
    stringsAreStrictlySorted(candidate.topics as string[]) &&
    ["introductory", "intermediate", "advanced"].includes(
      String(candidate.level),
    ) &&
    Number.isInteger(candidate.estimated_minutes) &&
    Number(candidate.estimated_minutes) >= 1 &&
    Number(candidate.estimated_minutes) <= 1440 &&
    boundedText(candidate.prerequisite_summary, 2, 500) &&
    ["available", "unavailable", "planned"].includes(
      String(candidate.availability),
    ) &&
    boundedText(candidate.availability_reason, 10, 500) &&
    typeof candidate.package_id === "string" &&
    IDENTIFIER.test(candidate.package_id) &&
    typeof candidate.package_version === "string" &&
    SEMANTIC_VERSION.test(candidate.package_version) &&
    typeof candidate.package_digest === "string" &&
    DIGEST.test(candidate.package_digest) &&
    provenanceIsSafe(candidate.provenance) &&
    typeof candidate.source_fingerprint === "string" &&
    DIGEST.test(candidate.source_fingerprint) &&
    candidate.projected_at === projectedAt
  );
}

function canonicalJson(value: unknown): string {
  function canonical(valueAtKey: unknown): unknown {
    if (Array.isArray(valueAtKey)) {
      return valueAtKey.map(canonical);
    }
    const objectValue = record(valueAtKey);
    if (objectValue) {
      return Object.fromEntries(
        Object.keys(objectValue)
          .sort()
          .map((key) => [key, canonical(objectValue[key])]),
      );
    }
    return valueAtKey;
  }
  return JSON.stringify(canonical(value));
}

async function sha256(value: unknown): Promise<string | null> {
  if (!globalThis.crypto?.subtle) {
    return null;
  }
  const bytes = new TextEncoder().encode(canonicalJson(value));
  try {
    const result = await globalThis.crypto.subtle.digest("SHA-256", bytes);
    return [...new Uint8Array(result)]
      .map((byte) => byte.toString(16).padStart(2, "0"))
      .join("");
  } catch {
    return null;
  }
}

function sourceMeaning(opportunity: LearningOpportunity) {
  return {
    schema_version: opportunity.schema_version,
    opportunity_id: opportunity.opportunity_id,
    placement_id: opportunity.placement_id,
    destination: opportunity.destination,
    kind: opportunity.kind,
    title: opportunity.title,
    summary: opportunity.summary,
    objectives: opportunity.objectives,
    topics: opportunity.topics,
    level: opportunity.level,
    estimated_minutes: opportunity.estimated_minutes,
    prerequisite_summary: opportunity.prerequisite_summary,
    availability: opportunity.availability,
    availability_reason: opportunity.availability_reason,
    package_id: opportunity.package_id,
    package_version: opportunity.package_version,
    package_digest: opportunity.package_digest,
    provenance: opportunity.provenance,
  };
}

async function integrityIsCoherent(
  records: readonly LearningOpportunity[],
  generation: string,
): Promise<boolean> {
  for (const opportunity of records) {
    if (
      (await sha256(sourceMeaning(opportunity))) !==
      opportunity.source_fingerprint
    ) {
      return false;
    }
  }
  const stableRecords = records.map((opportunity) => ({
    ...sourceMeaning(opportunity),
    source_fingerprint: opportunity.source_fingerprint,
  }));
  return (await sha256(stableRecords)) === generation;
}

export async function learningCatalogIsSafe(
  value: unknown,
): Promise<boolean> {
  const candidate = record(value);
  if (
    candidate === null ||
    !hasExactKeys(candidate, BROWSE_KEYS) ||
    candidate.schema_version !== "1.0.0" ||
    typeof candidate.projection_generation !== "string" ||
    !DIGEST.test(candidate.projection_generation) ||
    !validDateTime(candidate.projected_at) ||
    !Array.isArray(candidate.records) ||
    candidate.records.length > 500 ||
    !candidate.records.every((item) =>
      opportunityIsSafe(item, candidate.projected_at as string),
    )
  ) {
    return false;
  }
  const records = candidate.records as LearningOpportunity[];
  const opportunityIds = records.map((item) => item.opportunity_id);
  return (
    new Set(opportunityIds).size === opportunityIds.length &&
    (await integrityIsCoherent(
      records,
      candidate.projection_generation as string,
    ))
  );
}

export function opportunityCanOpen(
  opportunity: LearningOpportunity,
): boolean {
  return (
    opportunity.kind === "lesson" &&
    opportunity.availability === "available"
  );
}

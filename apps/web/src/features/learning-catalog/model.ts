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
  /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-]\d{2}:\d{2})$/;
const ASCII = /^[\x20-\x7e]+$/;

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
  return (
    typeof value === "string" &&
    DATE_TIME.test(value) &&
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

function recordsRespectObservableOrder(
  records: readonly LearningOpportunity[],
): boolean {
  for (let index = 1; index < records.length; index += 1) {
    const previous = records[index - 1];
    const current = records[index];
    if (!previous || !current) {
      return false;
    }
    if (ASCII.test(previous.title) && ASCII.test(current.title)) {
      const previousTitle = previous.title.toLowerCase();
      const currentTitle = current.title.toLowerCase();
      if (
        previousTitle > currentTitle ||
        (previousTitle === currentTitle &&
          previous.opportunity_id > current.opportunity_id)
      ) {
        return false;
      }
    } else if (
      previous.title === current.title &&
      previous.opportunity_id > current.opportunity_id
    ) {
      return false;
    }
  }
  return true;
}

export function learningCatalogIsSafe(
  value: unknown,
): value is LearningCatalog {
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
  const placementIds = records.map((item) => item.placement_id);
  return (
    new Set(opportunityIds).size === opportunityIds.length &&
    new Set(placementIds).size === placementIds.length &&
    recordsRespectObservableOrder(records)
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

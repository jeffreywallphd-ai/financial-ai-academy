import type { components, operations } from "../../generated/api-client";

export type LearningCatalog =
  components["schemas"]["LearningOpportunityBrowseResponseModel"];
export type LearningOpportunity =
  components["schemas"]["LearningOpportunityResponseModel"];
export type LearningCatalogQueryPage =
  components["schemas"]["LearningOpportunityQueryPageResponseModel"];
export type AppliedLearningCatalogQuery =
  components["schemas"]["AppliedLearningOpportunityQueryResponseModel"];
export type LearningCatalogQueryParameters = NonNullable<
  operations["queryLearningOpportunities"]["parameters"]["query"]
>;

export type LearningCatalogRouteState =
  | { status: "loading" }
  | { status: "ready"; page: LearningCatalogQueryPage }
  | { status: "unauthorized" }
  | { status: "forbidden" }
  | { status: "unavailable" }
  | { status: "invalid-query" }
  | { status: "stale-cursor" }
  | { status: "invalid-response" }
  | { status: "unexpected" };

const IDENTIFIER = /^[a-z0-9][a-z0-9._-]{2,63}$/;
const TOPIC = /^[a-z0-9][a-z0-9-]{1,49}$/;
const DIGEST = /^[a-f0-9]{64}$/;
const SEMANTIC_VERSION =
  /^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?$/;
const DESTINATION = /^\/learn\/placements\/[a-z0-9][a-z0-9._-]{2,63}$/;
const DATE = /^(\d{4})-(\d{2})-(\d{2})$/;
const DATE_TIME =
  /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.(\d{1,6}))?(Z|[+-](\d{2}):(\d{2}))$/;

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
const QUERY_PAGE_KEYS = [
  "applied_query",
  "next_cursor",
  "projected_at",
  "projection_generation",
  "records",
  "schema_version",
  "total_matches",
] as const;
const APPLIED_QUERY_KEYS = [
  "availabilities",
  "kinds",
  "levels",
  "maximum_minutes",
  "minimum_minutes",
  "page_size",
  "prerequisite_query",
  "query",
  "sort",
  "topics",
] as const;
const CURSOR = /^[A-Za-z0-9_-]+\.[a-f0-9]{64}$/;

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
  if (typeof value !== "string") {
    return false;
  }
  const match = DATE.exec(value);
  if (!match) {
    return false;
  }
  const year = Number(match[1]);
  const month = Number(match[2]);
  const day = Number(match[3]);
  if (!year || !month || !day || month > 12) {
    return false;
  }
  const daysInMonth = new Date(Date.UTC(year, month, 0)).getUTCDate();
  return day <= daysInMonth && !Number.isNaN(Date.parse(value + "T00:00:00Z"));
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
    match[9] ?? "00",
    match[10] ?? "00",
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

function canonicalPublishedAt(value: string): string {
  const match = DATE_TIME.exec(value);
  if (!match) {
    return value;
  }
  const [
    ,
    yearText,
    monthText,
    dayText,
    hourText,
    minuteText,
    secondText,
    fractionText = "",
    zoneText,
    offsetHourText = "00",
    offsetMinuteText = "00",
  ] = match;
  const year = Number(yearText);
  const month = Number(monthText);
  const day = Number(dayText);
  const hour = Number(hourText);
  const minute = Number(minuteText);
  const second = Number(secondText);
  const offsetDirection = zoneText?.startsWith("-") ? -1 : 1;
  const offsetMinutes =
    zoneText === "Z"
      ? 0
      : offsetDirection *
        (Number(offsetHourText) * 60 + Number(offsetMinuteText));
  const local = new Date(0);
  local.setUTCFullYear(year, month - 1, day);
  local.setUTCHours(hour, minute, second, 0);
  const utc = new Date(local.valueOf() - offsetMinutes * 60_000);
  const fractionalMicroseconds = fractionText.padEnd(6, "0");
  const fraction =
    Number(fractionalMicroseconds) === 0 ? "" : "." + fractionalMicroseconds;
  return utc.toISOString().slice(0, 19) + fraction + "Z";
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
    if (
      previous === undefined ||
      current === undefined ||
      previous >= current
    ) {
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
    provenance: {
      ...opportunity.provenance,
      published_at: canonicalPublishedAt(opportunity.provenance.published_at),
    },
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

export async function learningCatalogIsSafe(value: unknown): Promise<boolean> {
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

function optionalBoundedText(value: unknown): boolean {
  return value === null || boundedText(value, 1, 100);
}

function enumFiltersAreSafe(
  value: unknown,
  allowed: readonly string[],
): value is string[] {
  return (
    uniqueStrings(
      value,
      0,
      8,
      (item): item is string =>
        typeof item === "string" && allowed.includes(item),
    ) && stringsAreStrictlySorted(value)
  );
}

function appliedQueryIsSafe(
  value: unknown,
): value is AppliedLearningCatalogQuery {
  const candidate = record(value);
  return (
    candidate !== null &&
    hasExactKeys(candidate, APPLIED_QUERY_KEYS) &&
    optionalBoundedText(candidate.query) &&
    optionalBoundedText(candidate.prerequisite_query) &&
    uniqueStrings(
      candidate.topics,
      0,
      8,
      (item): item is string => typeof item === "string" && TOPIC.test(item),
    ) &&
    stringsAreStrictlySorted(candidate.topics as string[]) &&
    enumFiltersAreSafe(candidate.levels, [
      "introductory",
      "intermediate",
      "advanced",
    ]) &&
    enumFiltersAreSafe(candidate.kinds, [
      "course",
      "lesson",
      "lab",
      "project",
    ]) &&
    enumFiltersAreSafe(candidate.availabilities, [
      "available",
      "planned",
      "unavailable",
    ]) &&
    (candidate.minimum_minutes === null ||
      (Number.isInteger(candidate.minimum_minutes) &&
        Number(candidate.minimum_minutes) >= 1 &&
        Number(candidate.minimum_minutes) <= 1440)) &&
    (candidate.maximum_minutes === null ||
      (Number.isInteger(candidate.maximum_minutes) &&
        Number(candidate.maximum_minutes) >= 1 &&
        Number(candidate.maximum_minutes) <= 1440)) &&
    (candidate.minimum_minutes === null ||
      candidate.maximum_minutes === null ||
      Number(candidate.minimum_minutes) <= Number(candidate.maximum_minutes)) &&
    ["catalog", "title", "duration_ascending", "duration_descending"].includes(
      String(candidate.sort),
    ) &&
    Number.isInteger(candidate.page_size) &&
    Number(candidate.page_size) >= 1 &&
    Number(candidate.page_size) <= 50
  );
}

async function sourceFingerprintsAreCoherent(
  records: readonly LearningOpportunity[],
): Promise<boolean> {
  for (const opportunity of records) {
    if (
      (await sha256(sourceMeaning(opportunity))) !==
      opportunity.source_fingerprint
    ) {
      return false;
    }
  }
  return true;
}

export async function learningCatalogQueryPageIsSafe(
  value: unknown,
  request: LearningCatalogQueryParameters,
): Promise<boolean> {
  const candidate = record(value);
  if (
    candidate === null ||
    !hasExactKeys(candidate, QUERY_PAGE_KEYS) ||
    candidate.schema_version !== "1.0.0" ||
    typeof candidate.projection_generation !== "string" ||
    !DIGEST.test(candidate.projection_generation) ||
    !validDateTime(candidate.projected_at) ||
    !appliedQueryIsSafe(candidate.applied_query) ||
    !Number.isInteger(candidate.total_matches) ||
    Number(candidate.total_matches) < 0 ||
    Number(candidate.total_matches) > 500 ||
    !Array.isArray(candidate.records) ||
    candidate.records.length >
      Number((candidate.applied_query as Record<string, unknown>).page_size) ||
    candidate.records.length > Number(candidate.total_matches) ||
    (candidate.next_cursor !== null &&
      (typeof candidate.next_cursor !== "string" ||
        candidate.next_cursor.length > 1024 ||
        !CURSOR.test(candidate.next_cursor))) ||
    !candidate.records.every((item) =>
      opportunityIsSafe(item, candidate.projected_at as string),
    )
  ) {
    return false;
  }
  const records = candidate.records as LearningOpportunity[];
  const totalMatches = Number(candidate.total_matches);
  const pageSize = Number(
    (candidate.applied_query as Record<string, unknown>).page_size,
  );
  const hasNextCursor = candidate.next_cursor !== null;
  const isFirstPage = request.cursor === undefined;
  const paginationIsCoherent =
    (totalMatches === 0
      ? records.length === 0 && !hasNextCursor
      : records.length > 0) &&
    (!hasNextCursor ||
      (records.length === pageSize && totalMatches > records.length)) &&
    (!isFirstPage ||
      (records.length === Math.min(totalMatches, pageSize) &&
        hasNextCursor === (totalMatches > pageSize)));
  return (
    paginationIsCoherent &&
    new Set(records.map((item) => item.opportunity_id)).size ===
      records.length &&
    (await sourceFingerprintsAreCoherent(records))
  );
}

export function queryPageHref(
  query: AppliedLearningCatalogQuery,
  cursor?: string,
): string {
  const parameters = new URLSearchParams();
  if (query.query !== null) parameters.set("query", query.query);
  if (query.prerequisite_query !== null) {
    parameters.set("prerequisite_query", query.prerequisite_query);
  }
  for (const topic of query.topics) parameters.append("topic", topic);
  for (const level of query.levels) parameters.append("level", level);
  for (const kind of query.kinds) parameters.append("kind", kind);
  for (const availability of query.availabilities) {
    parameters.append("availability", availability);
  }
  if (query.minimum_minutes !== null) {
    parameters.set("minimum_minutes", String(query.minimum_minutes));
  }
  if (query.maximum_minutes !== null) {
    parameters.set("maximum_minutes", String(query.maximum_minutes));
  }
  if (query.sort !== "catalog") parameters.set("sort", query.sort);
  if (query.page_size !== 20)
    parameters.set("page_size", String(query.page_size));
  if (cursor) parameters.set("cursor", cursor);
  const encoded = parameters.toString();
  return encoded ? `/learn?${encoded}` : "/learn";
}

export function opportunityCanOpen(opportunity: LearningOpportunity): boolean {
  return (
    opportunity.kind === "lesson" && opportunity.availability === "available"
  );
}

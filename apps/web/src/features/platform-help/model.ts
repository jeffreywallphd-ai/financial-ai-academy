import type { components, operations } from "../../generated/api-client";

export type PlatformHelpSearchPage =
  components["schemas"]["PlatformHelpSearchPageResponseModel"];
export type PlatformHelpSearchResult =
  components["schemas"]["PlatformHelpSearchResultModel"];
export type PlatformHelpTopic =
  components["schemas"]["PlatformHelpTopicResponseModel"];
export type PlatformHelpBodyNode = PlatformHelpTopic["body"][number];
export type PlatformHelpTopicKind = PlatformHelpSearchResult["topic_kind"];
export type PlatformHelpSearchParameters = NonNullable<
  operations["searchPlatformHelp"]["parameters"]["query"]
>;

export type PlatformHelpSearchSelection = {
  parameters: PlatformHelpSearchParameters;
  href: string;
};

export type PlatformHelpTopicSelection = {
  topicId: string;
  topicVersion: string;
  returnTo: string;
};

export type PlatformHelpSearchRouteState =
  | { status: "loading" }
  | {
      status: "ready";
      page: PlatformHelpSearchPage;
      selection: PlatformHelpSearchSelection;
    }
  | { status: "unauthorized" | "forbidden" | "unavailable" }
  | { status: "invalid-query" | "stale-cursor" | "invalid-response" }
  | { status: "unexpected" };

export type PlatformHelpTopicRouteState =
  | { status: "loading" }
  | {
      status: "ready";
      topic: PlatformHelpTopic;
      selection: PlatformHelpTopicSelection;
    }
  | { status: "unauthorized" | "forbidden" | "unavailable" }
  | { status: "invalid-selection" | "not-found" | "invalid-response" }
  | { status: "unexpected" };

const IDENTIFIER = /^[a-z0-9][a-z0-9._-]{2,63}$/;
const VERSION = /^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$/;
const DIGEST = /^[a-f0-9]{64}$/;
const CURSOR = /^[A-Za-z0-9_-]{1,4096}$/;
const DATE = /^(\d{4})-(\d{2})-(\d{2})$/;
const TOPIC_KINDS = new Set([
  "glossary",
  "help",
  "method",
  "limitation",
  "troubleshooting",
]);
const SOURCE_AREAS = new Set([
  "product",
  "domain",
  "contract",
  "architecture",
  "risk",
  "method",
]);

function record(value: unknown): Record<string, unknown> | null {
  return typeof value === "object" && value !== null && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : null;
}

function hasExactKeys(
  value: Record<string, unknown>,
  required: readonly string[],
  optional: readonly string[] = [],
): boolean {
  const actual = Object.keys(value);
  return (
    required.every((key) => actual.includes(key)) &&
    actual.every((key) => required.includes(key) || optional.includes(key))
  );
}

function containsUnsafeControl(value: string): boolean {
  for (const character of value) {
    if (/[\p{Cc}\p{Cs}\p{Co}\p{Cn}]/u.test(character)) return true;
    if (/\p{Cf}/u.test(character) && character !== "‌" && character !== "‍") {
      return true;
    }
  }
  return false;
}

function boundedText(
  value: unknown,
  minimum: number,
  maximum: number,
): value is string {
  return (
    typeof value === "string" &&
    value.length >= minimum &&
    value.length <= maximum &&
    !containsUnsafeControl(value)
  );
}

function validDate(value: unknown): value is string {
  if (typeof value !== "string") return false;
  const match = DATE.exec(value);
  if (!match) return false;
  const year = Number(match[1]);
  const month = Number(match[2]);
  const day = Number(match[3]);
  if (month < 1 || month > 12 || day < 1) return false;
  return day <= new Date(Date.UTC(year, month, 0)).getUTCDate();
}

function validDateTime(value: unknown): value is string {
  return (
    typeof value === "string" &&
    /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-]\d{2}:\d{2})$/.test(
      value,
    ) &&
    validDate(value.slice(0, 10)) &&
    !Number.isNaN(Date.parse(value))
  );
}

function uniqueBy<T>(values: readonly T[], key: (value: T) => string): boolean {
  const keys = values.map(key);
  return keys.length === new Set(keys).size;
}

function applicabilityIsSafe(value: unknown): boolean {
  const item = record(value);
  return (
    item !== null &&
    hasExactKeys(item, ["scope_key", "label"]) &&
    typeof item.scope_key === "string" &&
    IDENTIFIER.test(item.scope_key) &&
    boundedText(item.label, 1, 160)
  );
}

function publicationIsSafe(value: unknown): boolean {
  const item = record(value);
  if (
    item === null ||
    !hasExactKeys(item, ["state", "reviewed_on", "updated_at"]) ||
    item.state !== "approved" ||
    !validDate(item.reviewed_on) ||
    !validDateTime(item.updated_at)
  ) {
    return false;
  }
  return item.reviewed_on <= item.updated_at.slice(0, 10);
}

function sourceReferenceIsSafe(value: unknown): boolean {
  const item = record(value);
  return (
    item !== null &&
    hasExactKeys(item, [
      "source_key",
      "title",
      "area",
      "source_version",
      "content_fingerprint",
    ]) &&
    typeof item.source_key === "string" &&
    IDENTIFIER.test(item.source_key) &&
    boundedText(item.title, 1, 200) &&
    typeof item.area === "string" &&
    SOURCE_AREAS.has(item.area) &&
    boundedText(item.source_version, 1, 80) &&
    typeof item.content_fingerprint === "string" &&
    DIGEST.test(item.content_fingerprint)
  );
}

function commonTopicProjectionIsSafe(value: Record<string, unknown>): boolean {
  const applicability = value.applicability;
  const sources = value.source_references;
  return (
    typeof value.topic_id === "string" &&
    IDENTIFIER.test(value.topic_id) &&
    typeof value.topic_version === "string" &&
    VERSION.test(value.topic_version) &&
    typeof value.topic_kind === "string" &&
    TOPIC_KINDS.has(value.topic_kind) &&
    boundedText(value.title, 1, 160) &&
    boundedText(value.summary, 20, 500) &&
    (value.glossary_term === undefined ||
      value.glossary_term === null ||
      boundedText(value.glossary_term, 1, 120)) &&
    Array.isArray(applicability) &&
    applicability.length >= 1 &&
    applicability.length <= 20 &&
    applicability.every(applicabilityIsSafe) &&
    uniqueBy(applicability, (item) => String(record(item)?.scope_key)) &&
    publicationIsSafe(value.publication) &&
    Array.isArray(sources) &&
    sources.length >= 1 &&
    sources.length <= 20 &&
    sources.every(sourceReferenceIsSafe) &&
    uniqueBy(sources, (item) => String(record(item)?.source_key)) &&
    typeof value.topic_digest === "string" &&
    DIGEST.test(value.topic_digest)
  );
}

const SEARCH_RESULT_KEYS = [
  "topic_id",
  "topic_version",
  "topic_kind",
  "title",
  "summary",
  "applicability",
  "publication",
  "source_references",
  "topic_digest",
] as const;

function searchResultIsSafe(value: unknown): boolean {
  const item = record(value);
  return (
    item !== null &&
    hasExactKeys(item, SEARCH_RESULT_KEYS, ["glossary_term"]) &&
    commonTopicProjectionIsSafe(item)
  );
}

export function platformHelpSearchPageIsSafe(
  value: unknown,
  expected: PlatformHelpSearchParameters,
): value is PlatformHelpSearchPage {
  const page = record(value);
  if (
    page === null ||
    !hasExactKeys(
      page,
      ["schema_version", "corpus_digest", "query", "results", "next_cursor"],
      ["topic_kind"],
    ) ||
    page.schema_version !== "1.0.0" ||
    typeof page.corpus_digest !== "string" ||
    !DIGEST.test(page.corpus_digest) ||
    !boundedText(page.query, 0, 200) ||
    (page.topic_kind ?? null) !== (expected.topic_kind ?? null) ||
    (page.next_cursor !== null &&
      (typeof page.next_cursor !== "string" || !CURSOR.test(page.next_cursor))) ||
    !Array.isArray(page.results) ||
    page.results.length > 50 ||
    !page.results.every(searchResultIsSafe)
  ) {
    return false;
  }
  return uniqueBy(page.results, (item) => {
    const result = record(item);
    return `${String(result?.topic_id)}@${String(result?.topic_version)}`;
  });
}

function bodyNodeIsSafe(value: unknown): boolean {
  const node = record(value);
  if (node === null || typeof node.node_kind !== "string") return false;
  switch (node.node_kind) {
    case "heading":
      return (
        hasExactKeys(node, ["node_kind", "level", "text"]) &&
        typeof node.level === "number" &&
        Number.isInteger(node.level) &&
        node.level >= 2 &&
        node.level <= 4 &&
        boundedText(node.text, 1, 160)
      );
    case "paragraph":
      return (
        hasExactKeys(node, ["node_kind", "text"]) &&
        boundedText(node.text, 1, 2000)
      );
    case "list":
      return (
        hasExactKeys(node, ["node_kind", "list_kind", "items"]) &&
        (node.list_kind === "ordered" || node.list_kind === "unordered") &&
        Array.isArray(node.items) &&
        node.items.length >= 1 &&
        node.items.length <= 30 &&
        node.items.every((item) => boundedText(item, 1, 500))
      );
    case "note":
      return (
        hasExactKeys(node, ["node_kind", "note_kind", "text"]) &&
        ["educational", "limitation", "warning"].includes(
          String(node.note_kind),
        ) &&
        boundedText(node.text, 1, 1000)
      );
    case "topic_reference":
      return (
        hasExactKeys(node, [
          "node_kind",
          "topic_id",
          "topic_version",
          "label",
        ]) &&
        typeof node.topic_id === "string" &&
        IDENTIFIER.test(node.topic_id) &&
        typeof node.topic_version === "string" &&
        VERSION.test(node.topic_version) &&
        boundedText(node.label, 1, 160)
      );
    default:
      return false;
  }
}

function relatedTopicIsSafe(value: unknown): boolean {
  const item = record(value);
  return (
    item !== null &&
    hasExactKeys(item, ["topic_id", "topic_version", "relationship"]) &&
    typeof item.topic_id === "string" &&
    IDENTIFIER.test(item.topic_id) &&
    typeof item.topic_version === "string" &&
    VERSION.test(item.topic_version) &&
    ["see_also", "prerequisite", "explains"].includes(
      String(item.relationship),
    )
  );
}

const TOPIC_KEYS = [
  "schema_version",
  "topic_id",
  "topic_version",
  "topic_kind",
  "title",
  "summary",
  "keywords",
  "body",
  "applicability",
  "publication",
  "source_references",
  "related_topics",
  "topic_digest",
] as const;

export function platformHelpTopicIsSafe(
  value: unknown,
  expectedId: string,
  expectedVersion: string,
): value is PlatformHelpTopic {
  const topic = record(value);
  if (
    topic === null ||
    !hasExactKeys(topic, TOPIC_KEYS, ["glossary_term"]) ||
    topic.schema_version !== "1.0.0" ||
    !commonTopicProjectionIsSafe(topic) ||
    topic.topic_id !== expectedId ||
    topic.topic_version !== expectedVersion ||
    !Array.isArray(topic.keywords) ||
    topic.keywords.length > 16 ||
    !topic.keywords.every((item) => boundedText(item, 1, 80)) ||
    new Set(topic.keywords).size !== topic.keywords.length ||
    !Array.isArray(topic.body) ||
    topic.body.length < 1 ||
    topic.body.length > 100 ||
    !topic.body.every(bodyNodeIsSafe) ||
    !Array.isArray(topic.related_topics) ||
    topic.related_topics.length > 20 ||
    !topic.related_topics.every(relatedTopicIsSafe)
  ) {
    return false;
  }
  return uniqueBy(topic.related_topics, (item) => {
    const related = record(item);
    return `${String(related?.topic_id)}@${String(related?.topic_version)}`;
  });
}

export function platformHelpSearchHref(
  parameters: PlatformHelpSearchParameters,
): string {
  const query = new URLSearchParams();
  if (parameters.query) query.set("query", parameters.query);
  if (parameters.topic_kind) query.set("topic_kind", parameters.topic_kind);
  if (parameters.page_size !== undefined) {
    query.set("page_size", String(parameters.page_size));
  }
  if (parameters.cursor) query.set("cursor", parameters.cursor);
  const text = query.toString();
  return text ? `/help?${text}` : "/help";
}

export function platformHelpTopicHref(
  topicId: string,
  topicVersion: string,
  returnTo: string,
): string {
  const query = new URLSearchParams({ return_to: returnTo });
  return `/help/topics/${topicId}/versions/${topicVersion}?${query.toString()}`;
}

export function topicKindLabel(value: PlatformHelpTopicKind): string {
  return {
    glossary: "Meaning",
    help: "How-to help",
    method: "Method",
    limitation: "Limitation",
    troubleshooting: "Problem solving",
  }[value];
}

export function relationshipLabel(
  value: PlatformHelpTopic["related_topics"][number]["relationship"],
): string {
  return {
    see_also: "See also",
    prerequisite: "Read first",
    explains: "Explains",
  }[value];
}

export function readableDate(value: string): string {
  return new Intl.DateTimeFormat(undefined, {
    year: "numeric",
    month: "long",
    day: "numeric",
    timeZone: "UTC",
  }).format(new Date(`${value}T00:00:00Z`));
}

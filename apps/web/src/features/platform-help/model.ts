import type { components, operations } from "../../generated/api-client";

export type PlatformHelpSearchPage =
  components["schemas"]["PlatformHelpSearchPageResponseModel"];
export type PlatformHelpSearchResult =
  components["schemas"]["PlatformHelpSearchResultModel"];
export type PlatformHelpTopic =
  components["schemas"]["PlatformHelpTopicResponseModel"];
export type PlatformHelpBodyNode = PlatformHelpTopic["body"][number];
export type PlatformHelpTopicKind = PlatformHelpSearchResult["topic_kind"];
export type ContextualHelp =
  components["schemas"]["ContextualHelpResponseModel"];
export type FeatureGuidance =
  components["schemas"]["FeatureGuidanceResponseModel"];
export type FeatureGuidanceAction =
  FeatureGuidance["guidance"]["actions"][number];
export type FeatureGuidanceActionKind = FeatureGuidanceAction["action_kind"];
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
  returnLabel: string;
};

export type ContextualHelpReadOutcome =
  | { status: "ready"; context: ContextualHelp }
  | { status: "unavailable" };

export type ContextualHelpReader = (
  contextKey: string,
  contextVersion: string,
  signal: AbortSignal,
) => Promise<ContextualHelpReadOutcome>;

export type FeatureGuidanceReadOutcome =
  | { status: "ready"; resolution: FeatureGuidance }
  | { status: "unavailable" };

export type FeatureGuidanceReader = (
  surfaceKey: string,
  conditionKey: string,
  mappingVersion: string,
  signal: AbortSignal,
) => Promise<FeatureGuidanceReadOutcome>;

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
const CONTEXT_PURPOSES = new Set([
  "method",
  "source",
  "data_meaning",
  "ai_boundary",
  "education_boundary",
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

export function platformHelpTextIsSafe(
  value: unknown,
  minimum: number,
  maximum: number,
): value is string {
  return (
    typeof value === "string" &&
    [...value].length >= minimum &&
    [...value].length <= maximum &&
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
    platformHelpTextIsSafe(item.label, 1, 160)
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
    platformHelpTextIsSafe(item.title, 1, 200) &&
    typeof item.area === "string" &&
    SOURCE_AREAS.has(item.area) &&
    platformHelpTextIsSafe(item.source_version, 1, 80) &&
    typeof item.content_fingerprint === "string" &&
    DIGEST.test(item.content_fingerprint)
  );
}

function contextualHelpReferenceIsSafe(value: unknown): boolean {
  const item = record(value);
  return (
    item !== null &&
    hasExactKeys(item, ["topic_id", "topic_version", "purpose", "label"]) &&
    typeof item.topic_id === "string" &&
    IDENTIFIER.test(item.topic_id) &&
    typeof item.topic_version === "string" &&
    VERSION.test(item.topic_version) &&
    typeof item.purpose === "string" &&
    CONTEXT_PURPOSES.has(item.purpose) &&
    platformHelpTextIsSafe(item.label, 1, 160)
  );
}

export function contextualHelpIsSafe(
  value: unknown,
  expectedKey: string,
  expectedVersion: string,
): value is ContextualHelp {
  const context = record(value);
  if (
    context === null ||
    !hasExactKeys(context, [
      "schema_version",
      "context_key",
      "context_version",
      "feature_label",
      "applicability",
      "help_references",
      "publication",
      "source_references",
      "context_digest",
    ]) ||
    context.schema_version !== "1.0.0" ||
    context.context_key !== expectedKey ||
    context.context_version !== expectedVersion ||
    typeof context.context_key !== "string" ||
    !IDENTIFIER.test(context.context_key) ||
    typeof context.context_version !== "string" ||
    !VERSION.test(context.context_version) ||
    !platformHelpTextIsSafe(context.feature_label, 1, 160) ||
    !Array.isArray(context.applicability) ||
    context.applicability.length < 1 ||
    context.applicability.length > 20 ||
    !context.applicability.every(applicabilityIsSafe) ||
    !uniqueBy(context.applicability, (item) =>
      String(record(item)?.scope_key),
    ) ||
    !Array.isArray(context.help_references) ||
    context.help_references.length < 1 ||
    context.help_references.length > 10 ||
    !context.help_references.every(contextualHelpReferenceIsSafe) ||
    !uniqueBy(context.help_references, (item) => {
      const reference = record(item);
      return `${String(reference?.topic_id)}@${String(reference?.topic_version)}`;
    }) ||
    !uniqueBy(context.help_references, (item) =>
      String(record(item)?.purpose),
    ) ||
    !publicationIsSafe(context.publication) ||
    !Array.isArray(context.source_references) ||
    context.source_references.length < 1 ||
    context.source_references.length > 20 ||
    !context.source_references.every(sourceReferenceIsSafe) ||
    !uniqueBy(context.source_references, (item) =>
      String(record(item)?.source_key),
    ) ||
    typeof context.context_digest !== "string" ||
    !DIGEST.test(context.context_digest)
  ) {
    return false;
  }
  return true;
}

const FEATURE_STATUSES = new Set(["limited", "unavailable", "degraded"]);
const FEATURE_ACTION_KINDS = new Set([
  "retry_unchanged_request",
  "reload_current_state",
  "return_to_owning_task",
  "download_inert_artifact",
  "open_help_topic",
]);

function featureGuidanceActionIsSafe(value: unknown): boolean {
  const action = record(value);
  if (
    action === null ||
    typeof action.action_kind !== "string" ||
    !FEATURE_ACTION_KINDS.has(action.action_kind) ||
    !platformHelpTextIsSafe(action.label, 1, 120)
  ) {
    return false;
  }
  return action.action_kind === "open_help_topic"
    ? hasExactKeys(action, [
        "action_kind",
        "label",
        "topic_id",
        "topic_version",
      ]) &&
        typeof action.topic_id === "string" &&
        IDENTIFIER.test(action.topic_id) &&
        typeof action.topic_version === "string" &&
        VERSION.test(action.topic_version)
    : hasExactKeys(action, ["action_kind", "label"]);
}

function canonicalJson(value: unknown): string {
  if (Array.isArray(value)) {
    return `[${value.map(canonicalJson).join(",")}]`;
  }
  const item = record(value);
  if (item !== null) {
    return `{${Object.keys(item)
      .sort()
      .map((key) => `${JSON.stringify(key)}:${canonicalJson(item[key])}`)
      .join(",")}}`;
  }
  return JSON.stringify(value);
}

async function digestWithout(
  value: Record<string, unknown>,
  field: string,
): Promise<string> {
  const canonical = Object.fromEntries(
    Object.entries(value).filter(([key]) => key !== field),
  );
  const bytes = await globalThis.crypto.subtle.digest(
    "SHA-256",
    new TextEncoder().encode(canonicalJson(canonical)),
  );
  return [...new Uint8Array(bytes)]
    .map((item) => item.toString(16).padStart(2, "0"))
    .join("");
}

export async function featureGuidanceIsSafe(
  value: unknown,
  expectedSurfaceKey: string,
  expectedConditionKey: string,
  expectedMappingVersion: string,
): Promise<boolean> {
  const resolution = record(value);
  const mapping = record(resolution?.mapping);
  const guidance = record(resolution?.guidance);
  if (
    resolution === null ||
    !hasExactKeys(resolution, ["mapping", "guidance"]) ||
    mapping === null ||
    guidance === null ||
    !hasExactKeys(mapping, [
      "schema_version",
      "surface_key",
      "condition_key",
      "mapping_version",
      "guidance_id",
      "guidance_version",
      "publication",
      "source_references",
      "mapping_digest",
    ]) ||
    mapping.schema_version !== "1.0.0" ||
    mapping.surface_key !== expectedSurfaceKey ||
    mapping.condition_key !== expectedConditionKey ||
    mapping.mapping_version !== expectedMappingVersion ||
    typeof mapping.surface_key !== "string" ||
    !IDENTIFIER.test(mapping.surface_key) ||
    typeof mapping.condition_key !== "string" ||
    !IDENTIFIER.test(mapping.condition_key) ||
    typeof mapping.mapping_version !== "string" ||
    !VERSION.test(mapping.mapping_version) ||
    typeof mapping.guidance_id !== "string" ||
    !IDENTIFIER.test(mapping.guidance_id) ||
    typeof mapping.guidance_version !== "string" ||
    !VERSION.test(mapping.guidance_version) ||
    !publicationIsSafe(mapping.publication) ||
    !Array.isArray(mapping.source_references) ||
    mapping.source_references.length < 1 ||
    mapping.source_references.length > 20 ||
    !mapping.source_references.every(sourceReferenceIsSafe) ||
    !uniqueBy(mapping.source_references, (item) =>
      String(record(item)?.source_key),
    ) ||
    typeof mapping.mapping_digest !== "string" ||
    !DIGEST.test(mapping.mapping_digest) ||
    !hasExactKeys(guidance, [
      "schema_version",
      "guidance_id",
      "guidance_version",
      "status",
      "heading",
      "reason",
      "outcome",
      "actions",
      "help_references",
      "applicability",
      "publication",
      "source_references",
      "guidance_digest",
    ]) ||
    guidance.schema_version !== "1.0.0" ||
    guidance.guidance_id !== mapping.guidance_id ||
    guidance.guidance_version !== mapping.guidance_version ||
    typeof guidance.status !== "string" ||
    !FEATURE_STATUSES.has(guidance.status) ||
    !platformHelpTextIsSafe(guidance.heading, 1, 120) ||
    !platformHelpTextIsSafe(guidance.reason, 1, 500) ||
    !platformHelpTextIsSafe(guidance.outcome, 1, 500) ||
    !Array.isArray(guidance.actions) ||
    guidance.actions.length > 5 ||
    !guidance.actions.every(featureGuidanceActionIsSafe) ||
    !uniqueBy(guidance.actions, (item) => {
      const action = record(item);
      return `${String(action?.action_kind)}:${String(action?.topic_id ?? "")}@${String(action?.topic_version ?? "")}`;
    }) ||
    !Array.isArray(guidance.help_references) ||
    guidance.help_references.length < 1 ||
    guidance.help_references.length > 10 ||
    !guidance.help_references.every(contextualHelpReferenceIsSafe) ||
    !uniqueBy(guidance.help_references, (item) => {
      const reference = record(item);
      return `${String(reference?.topic_id)}@${String(reference?.topic_version)}`;
    }) ||
    !uniqueBy(guidance.help_references, (item) =>
      String(record(item)?.purpose),
    ) ||
    !Array.isArray(guidance.applicability) ||
    guidance.applicability.length < 1 ||
    guidance.applicability.length > 20 ||
    !guidance.applicability.every(applicabilityIsSafe) ||
    !uniqueBy(guidance.applicability, (item) =>
      String(record(item)?.scope_key),
    ) ||
    !publicationIsSafe(guidance.publication) ||
    !Array.isArray(guidance.source_references) ||
    guidance.source_references.length < 1 ||
    guidance.source_references.length > 20 ||
    !guidance.source_references.every(sourceReferenceIsSafe) ||
    !uniqueBy(guidance.source_references, (item) =>
      String(record(item)?.source_key),
    ) ||
    typeof guidance.guidance_digest !== "string" ||
    !DIGEST.test(guidance.guidance_digest)
  ) {
    return false;
  }
  const references = new Set(
    guidance.help_references.map((item) => {
      const reference = record(item);
      return `${String(reference?.topic_id)}@${String(reference?.topic_version)}`;
    }),
  );
  if (
    guidance.actions.some((item) => {
      const action = record(item);
      return (
        action?.action_kind === "open_help_topic" &&
        !references.has(`${String(action.topic_id)}@${String(action.topic_version)}`)
      );
    })
  ) {
    return false;
  }
  try {
    return (
      (await digestWithout(mapping, "mapping_digest")) ===
        mapping.mapping_digest &&
      (await digestWithout(guidance, "guidance_digest")) ===
        guidance.guidance_digest
    );
  } catch {
    return false;
  }
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
    platformHelpTextIsSafe(value.title, 1, 160) &&
    platformHelpTextIsSafe(value.summary, 20, 500) &&
    (value.glossary_term === undefined ||
      value.glossary_term === null ||
      platformHelpTextIsSafe(value.glossary_term, 1, 120)) &&
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
    !platformHelpTextIsSafe(page.query, 0, 200) ||
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
        platformHelpTextIsSafe(node.text, 1, 160)
      );
    case "paragraph":
      return (
        hasExactKeys(node, ["node_kind", "text"]) &&
        platformHelpTextIsSafe(node.text, 1, 2000)
      );
    case "list":
      return (
        hasExactKeys(node, ["node_kind", "list_kind", "items"]) &&
        (node.list_kind === "ordered" || node.list_kind === "unordered") &&
        Array.isArray(node.items) &&
        node.items.length >= 1 &&
        node.items.length <= 30 &&
        node.items.every((item) => platformHelpTextIsSafe(item, 1, 500))
      );
    case "note":
      return (
        hasExactKeys(node, ["node_kind", "note_kind", "text"]) &&
        ["educational", "limitation", "warning"].includes(
          String(node.note_kind),
        ) &&
        platformHelpTextIsSafe(node.text, 1, 1000)
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
        platformHelpTextIsSafe(node.label, 1, 160)
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
    !topic.keywords.every((item) => platformHelpTextIsSafe(item, 1, 80)) ||
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

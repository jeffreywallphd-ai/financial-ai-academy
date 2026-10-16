import type { components } from "../../generated/api-client";


export type PracticePresentation =
  components["schemas"]["PracticePresentationResponseModel"];
export type PracticeItem = PracticePresentation["items"][number];

export type PracticeActivityRouteState =
  | { status: "loading" }
  | { status: "ready"; practice: PracticePresentation }
  | { status: "unauthorized" }
  | { status: "forbidden" }
  | { status: "not-found" }
  | { status: "unavailable" }
  | { status: "invalid-content" }
  | { status: "unexpected" };

const DIGEST = /^[a-f0-9]{64}$/;
const IDENTIFIER = /^[a-z0-9][a-z0-9._-]{2,63}$/;
const SEMANTIC_VERSION =
  /^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$/;
const UNSAFE_TEXT = /[<>&]/u;

const ROOT_KEYS = [
  "attempt_policy",
  "definition_digest",
  "instructions",
  "items",
  "package_digest",
  "package_id",
  "package_version",
  "placement_id",
  "practice_id",
  "practice_version",
  "purpose",
  "review_references",
  "schema_version",
  "source_references",
  "title",
] as const;
const POLICY_KEYS = [
  "history_visible",
  "max_attempts",
  "policy_id",
  "policy_version",
  "resume_allowed",
] as const;
const REFERENCE_KEYS = [
  "resource_digest",
  "resource_id",
  "resource_version",
  "title",
] as const;
const OPTION_KEYS = ["label", "option_id"] as const;
const ITEM_COMMON_KEYS = [
  "item_id",
  "item_type",
  "item_version",
  "max_score",
  "prompt",
  "scoring_policy_id",
  "scoring_policy_version",
] as const;

function record(value: unknown): Record<string, unknown> | null {
  return typeof value === "object" && value !== null && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : null;
}

function exactKeys(
  value: Record<string, unknown>,
  expected: readonly string[],
): boolean {
  const actual = Object.keys(value).sort();
  const keys = [...expected].sort();
  return (
    actual.length === keys.length &&
    actual.every((key, index) => key === keys[index])
  );
}

function safeText(value: unknown, maximum: number): value is string {
  const characters = typeof value === "string" ? [...value] : [];
  return (
    typeof value === "string" &&
    value.trim().length > 0 &&
    characters.length <= maximum &&
    !UNSAFE_TEXT.test(value) &&
    !characters.some((character) => {
      const codePoint = character.codePointAt(0) ?? 0;
      return codePoint < 32 || codePoint === 127;
    })
  );
}

function identifier(value: unknown): value is string {
  return typeof value === "string" && IDENTIFIER.test(value);
}

function semanticVersion(value: unknown): value is string {
  return typeof value === "string" && SEMANTIC_VERSION.test(value);
}

function boundedArray(
  value: unknown,
  minimum: number,
  maximum: number,
): value is unknown[] {
  return (
    Array.isArray(value) &&
    value.length >= minimum &&
    value.length <= maximum
  );
}

function optionIsSafe(value: unknown): value is Record<string, unknown> {
  const option = record(value);
  return (
    option !== null &&
    exactKeys(option, OPTION_KEYS) &&
    identifier(option.option_id) &&
    safeText(option.label, 160)
  );
}

function optionsAreSafe(
  value: unknown,
  minimum: number,
  maximum: number,
): boolean {
  if (!boundedArray(value, minimum, maximum)) {
    return false;
  }
  const ids = new Set<string>();
  for (const option of value) {
    if (!optionIsSafe(option) || ids.has(String(option.option_id))) {
      return false;
    }
    ids.add(String(option.option_id));
  }
  return true;
}

function itemIsSafe(value: unknown): value is Record<string, unknown> {
  const item = record(value);
  if (
    item === null ||
    !identifier(item.item_id) ||
    item.item_version !== "1.0.0" ||
    !safeText(item.prompt, 600) ||
    item.scoring_policy_version !== "1.0.0" ||
    item.max_score !== 1
  ) {
    return false;
  }
  switch (item.item_type) {
    case "single_select":
      return (
        exactKeys(item, [...ITEM_COMMON_KEYS, "options"]) &&
        item.scoring_policy_id === "single-select-exact-match" &&
        optionsAreSafe(item.options, 2, 8)
      );
    case "multiple_select":
      return (
        exactKeys(item, [...ITEM_COMMON_KEYS, "options"]) &&
        item.scoring_policy_id === "multiple-select-exact-set" &&
        optionsAreSafe(item.options, 3, 12)
      );
    case "numeric_entry":
      return (
        exactKeys(item, [
          ...ITEM_COMMON_KEYS,
          "allow_negative",
          "scale",
          "unit_label",
        ]) &&
        item.scoring_policy_id === "numeric-exact-or-inclusive-range" &&
        Number.isInteger(item.scale) &&
        Number(item.scale) >= 0 &&
        Number(item.scale) <= 6 &&
        typeof item.allow_negative === "boolean" &&
        safeText(item.unit_label, 160)
      );
    default:
      return false;
  }
}

function referencesAreSafe(value: unknown): boolean {
  if (!boundedArray(value, 1, 8)) {
    return false;
  }
  const ids = new Set<string>();
  for (const candidate of value) {
    const reference = record(candidate);
    if (
      reference === null ||
      !exactKeys(reference, REFERENCE_KEYS) ||
      !identifier(reference.resource_id) ||
      ids.has(String(reference.resource_id)) ||
      !semanticVersion(reference.resource_version) ||
      typeof reference.resource_digest !== "string" ||
      !DIGEST.test(reference.resource_digest) ||
      !safeText(reference.title, 160)
    ) {
      return false;
    }
    ids.add(String(reference.resource_id));
  }
  return true;
}

function policyIsSafe(value: unknown): boolean {
  const policy = record(value);
  return (
    policy !== null &&
    exactKeys(policy, POLICY_KEYS) &&
    policy.policy_id === "formative-retry" &&
    policy.policy_version === "1.0.0" &&
    Number.isInteger(policy.max_attempts) &&
    Number(policy.max_attempts) >= 1 &&
    Number(policy.max_attempts) <= 10 &&
    policy.resume_allowed === true &&
    policy.history_visible === true
  );
}

export function practicePresentationIsSafe(
  value: unknown,
  expectedPlacementId?: string,
): value is PracticePresentation {
  const presentation = record(value);
  if (
    presentation === null ||
    !exactKeys(presentation, ROOT_KEYS) ||
    presentation.schema_version !== "1.0.0" ||
    !identifier(presentation.placement_id) ||
    (expectedPlacementId !== undefined &&
      presentation.placement_id !== expectedPlacementId) ||
    !identifier(presentation.package_id) ||
    !semanticVersion(presentation.package_version) ||
    typeof presentation.package_digest !== "string" ||
    !DIGEST.test(presentation.package_digest) ||
    typeof presentation.definition_digest !== "string" ||
    !DIGEST.test(presentation.definition_digest) ||
    !identifier(presentation.practice_id) ||
    presentation.practice_version !== "1.0.0" ||
    !safeText(presentation.title, 160) ||
    !safeText(presentation.purpose, 600) ||
    !safeText(presentation.instructions, 600) ||
    !policyIsSafe(presentation.attempt_policy) ||
    !referencesAreSafe(presentation.source_references) ||
    !referencesAreSafe(presentation.review_references) ||
    !boundedArray(presentation.items, 1, 20)
  ) {
    return false;
  }
  const itemIds = new Set<string>();
  for (const item of presentation.items) {
    if (!itemIsSafe(item) || itemIds.has(String(item.item_id))) {
      return false;
    }
    itemIds.add(String(item.item_id));
  }
  return true;
}

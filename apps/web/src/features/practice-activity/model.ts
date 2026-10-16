import type { components } from "../../generated/api-client";


export type PracticePresentation =
  components["schemas"]["PracticePresentationResponseModel"];
export type PracticeItem = PracticePresentation["items"][number];
export type PracticeSubmission =
  components["schemas"]["PracticeSubmissionRequestModel"];
export type PracticeSubmissionResult =
  components["schemas"]["PracticeSubmissionResultResponseModel"];

export type PreparedPracticeSubmission = Readonly<{
  body: PracticeSubmission;
  placementId: string;
}>;

export type PracticeSubmissionPreparation =
  | { status: "ready"; submission: PreparedPracticeSubmission }
  | { status: "invalid"; itemId: string };

export type PracticeSubmissionOutcome =
  | { status: "result"; result: PracticeSubmissionResult }
  | { status: "invalid-request" }
  | { status: "unauthorized" }
  | { status: "forbidden" }
  | { status: "not-found" }
  | { status: "stale" }
  | { status: "conflict" }
  | { status: "already-completed" }
  | { status: "unavailable" }
  | { status: "invalid-result" }
  | { status: "unexpected" };

export type PracticeSubmitter = (
  practice: PracticePresentation,
  submission: PreparedPracticeSubmission,
  signal?: AbortSignal,
) => Promise<PracticeSubmissionOutcome>;

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
const UUID =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const UTC_TIMESTAMP =
  /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.(\d{1,6}))?Z$/;
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
const RESULT_ROOT_KEYS = [
  "attempt_id",
  "attempt_policy_id",
  "attempt_policy_version",
  "definition_digest",
  "evidence_id",
  "item_results",
  "max_score",
  "outcome",
  "package_digest",
  "package_id",
  "package_version",
  "placement_id",
  "practice_id",
  "practice_version",
  "review_reference_ids",
  "schema_version",
  "score",
  "submission_id",
  "submitted_at",
] as const;
const RESULT_COMMON_KEYS = [
  "correct",
  "feedback",
  "item_id",
  "item_type",
  "item_version",
  "max_score",
  "score",
  "scoring_policy_id",
  "scoring_policy_version",
] as const;
const FEEDBACK_KEYS = [
  "feedback_id",
  "review_reference_ids",
  "text",
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

function canonicalUtcTimestamp(value: unknown): value is string {
  if (typeof value !== "string") {
    return false;
  }
  const match = UTC_TIMESTAMP.exec(value);
  if (match === null) {
    return false;
  }
  const year = Number(match[1]);
  const month = Number(match[2]);
  const day = Number(match[3]);
  const hour = Number(match[4]);
  const minute = Number(match[5]);
  const second = Number(match[6]);
  if (
    month < 1 ||
    month > 12 ||
    hour > 23 ||
    minute > 59 ||
    second > 59
  ) {
    return false;
  }
  const leapYear =
    year % 400 === 0 || (year % 4 === 0 && year % 100 !== 0);
  const daysByMonth = [
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
  return day >= 1 && day <= (daysByMonth[month - 1] ?? 0);
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

export function canonicalDecimalPattern(
  scale: number,
  allowNegative: boolean,
): string {
  const unsignedInteger = "(?:0|[1-9][0-9]*)";
  if (scale === 0) {
    return allowNegative
      ? "(?:0|[1-9][0-9]*|-[1-9][0-9]*)"
      : unsignedInteger;
  }
  const unsignedDecimal = `${unsignedInteger}\\.[0-9]{${scale}}`;
  if (!allowNegative) {
    return unsignedDecimal;
  }
  const negativeNonzeroDecimal = `-(?!0\\.0{${scale}})(?:0|[1-9][0-9]*)\\.[0-9]{${scale}}`;
  return `(?:${unsignedDecimal}|${negativeNonzeroDecimal})`;
}

function decimalIsCanonical(
  value: string,
  scale: number,
  allowNegative: boolean,
): boolean {
  return new RegExp(
    `^(?:${canonicalDecimalPattern(scale, allowNegative)})$`,
    "u",
  ).test(value);
}

export function preparePracticeSubmission(
  practice: PracticePresentation,
  formData: FormData,
  submissionId: string,
): PracticeSubmissionPreparation {
  const responses: PracticeSubmission["responses"][number][] = [];
  for (const item of practice.items) {
    const values = formData
      .getAll(item.item_id)
      .filter((value): value is string => typeof value === "string");
    if (item.item_type === "single_select") {
      const selected = values[0];
      if (
        values.length !== 1 ||
        selected === undefined ||
        !item.options.some((option) => option.option_id === selected)
      ) {
        return { status: "invalid", itemId: item.item_id };
      }
      responses.push({
        item_id: item.item_id,
        item_type: item.item_type,
        item_version: item.item_version,
        scoring_policy_id: item.scoring_policy_id,
        scoring_policy_version: item.scoring_policy_version,
        selected_option_id: selected,
      });
      continue;
    }
    if (item.item_type === "multiple_select") {
      const selected = new Set(values);
      if (
        values.length === 0 ||
        selected.size !== values.length ||
        values.some(
          (value) =>
            !item.options.some((option) => option.option_id === value),
        )
      ) {
        return { status: "invalid", itemId: item.item_id };
      }
      responses.push({
        item_id: item.item_id,
        item_type: item.item_type,
        item_version: item.item_version,
        scoring_policy_id: item.scoring_policy_id,
        scoring_policy_version: item.scoring_policy_version,
        selected_option_ids: values,
      });
      continue;
    }
    const entered = values[0] ?? "";
    if (
      values.length !== 1 ||
      !decimalIsCanonical(entered, item.scale, item.allow_negative)
    ) {
      return { status: "invalid", itemId: item.item_id };
    }
    responses.push({
      entered_value: entered,
      item_id: item.item_id,
      item_type: item.item_type,
      item_version: item.item_version,
      scoring_policy_id: item.scoring_policy_id,
      scoring_policy_version: item.scoring_policy_version,
    });
  }
  return {
    status: "ready",
    submission: {
      placementId: practice.placement_id,
      body: {
        schema_version: "1.0.0",
        submission_id: submissionId,
        placement_id: practice.placement_id,
        package_id: practice.package_id,
        package_version: practice.package_version,
        package_digest: practice.package_digest,
        definition_digest: practice.definition_digest,
        practice_id: practice.practice_id,
        practice_version: practice.practice_version,
        attempt_policy_id: practice.attempt_policy.policy_id,
        attempt_policy_version: practice.attempt_policy.policy_version,
        responses,
      },
    },
  };
}

function uniqueIdentifiers(
  value: unknown,
  allowed: ReadonlySet<string>,
): value is string[] {
  return (
    boundedArray(value, 1, 8) &&
    value.every((item) => typeof item === "string" && allowed.has(item)) &&
    new Set(value).size === value.length
  );
}

function sameStringSet(first: readonly string[], second: readonly string[]) {
  return (
    first.length === second.length &&
    first.every((value) => second.includes(value)) &&
    new Set(first).size === first.length &&
    new Set(second).size === second.length
  );
}

function resultItemIsSafe(
  value: unknown,
  practiceItem: PracticeItem,
  response: PracticeSubmission["responses"][number],
  reviewIds: ReadonlySet<string>,
): boolean {
  const item = record(value);
  if (
    item === null ||
    !Number.isInteger(item.score) ||
    Number(item.score) < 0 ||
    Number(item.score) > 1 ||
    item.max_score !== 1 ||
    typeof item.correct !== "boolean" ||
    item.correct !== (item.score === 1) ||
    item.item_id !== practiceItem.item_id ||
    item.item_type !== practiceItem.item_type ||
    item.item_version !== practiceItem.item_version ||
    item.scoring_policy_id !== practiceItem.scoring_policy_id ||
    item.scoring_policy_version !== practiceItem.scoring_policy_version
  ) {
    return false;
  }
  const feedback = record(item.feedback);
  if (
    feedback === null ||
    !exactKeys(feedback, FEEDBACK_KEYS) ||
    !identifier(feedback.feedback_id) ||
    !safeText(feedback.text, 600) ||
    !uniqueIdentifiers(feedback.review_reference_ids, reviewIds)
  ) {
    return false;
  }
  if (
    item.item_type === "single_select" &&
    response.item_type === "single_select"
  ) {
    return (
      exactKeys(item, [...RESULT_COMMON_KEYS, "selected_option_id"]) &&
      item.selected_option_id === response.selected_option_id
    );
  }
  if (
    item.item_type === "multiple_select" &&
    response.item_type === "multiple_select"
  ) {
    return (
      exactKeys(item, [...RESULT_COMMON_KEYS, "selected_option_ids"]) &&
      Array.isArray(item.selected_option_ids) &&
      item.selected_option_ids.every(
        (candidate): candidate is string => typeof candidate === "string",
      ) &&
      sameStringSet(
        item.selected_option_ids,
        response.selected_option_ids,
      )
    );
  }
  return (
    item.item_type === "numeric_entry" &&
    response.item_type === "numeric_entry" &&
    exactKeys(item, [...RESULT_COMMON_KEYS, "entered_value"]) &&
    item.entered_value === response.entered_value
  );
}

export function practiceSubmissionResultIsSafe(
  value: unknown,
  practice: PracticePresentation,
  submission: PreparedPracticeSubmission,
): value is PracticeSubmissionResult {
  const result = record(value);
  if (
    result === null ||
    !exactKeys(result, RESULT_ROOT_KEYS) ||
    result.schema_version !== "1.0.0" ||
    typeof result.attempt_id !== "string" ||
    !UUID.test(result.attempt_id) ||
    typeof result.evidence_id !== "string" ||
    !UUID.test(result.evidence_id) ||
    result.submission_id !== submission.body.submission_id ||
    result.placement_id !== practice.placement_id ||
    result.package_id !== practice.package_id ||
    result.package_version !== practice.package_version ||
    result.package_digest !== practice.package_digest ||
    result.definition_digest !== practice.definition_digest ||
    result.practice_id !== practice.practice_id ||
    result.practice_version !== practice.practice_version ||
    result.attempt_policy_id !== practice.attempt_policy.policy_id ||
    result.attempt_policy_version !== practice.attempt_policy.policy_version ||
    !Number.isInteger(result.score) ||
    !Number.isInteger(result.max_score) ||
    Number(result.max_score) !== practice.items.length ||
    Number(result.score) < 0 ||
    Number(result.score) > Number(result.max_score) ||
    (result.outcome !== "all_correct" && result.outcome !== "review_needed") ||
    result.outcome !==
      (result.score === result.max_score ? "all_correct" : "review_needed") ||
    !canonicalUtcTimestamp(result.submitted_at) ||
    !Array.isArray(result.item_results) ||
    result.item_results.length !== practice.items.length
  ) {
    return false;
  }
  const reviewIds = new Set(
    practice.review_references.map((reference) => reference.resource_id),
  );
  if (!uniqueIdentifiers(result.review_reference_ids, reviewIds)) {
    return false;
  }
  let score = 0;
  for (const [index, practiceItem] of practice.items.entries()) {
    const response = submission.body.responses[index];
    const itemResult = result.item_results[index];
    if (
      response === undefined ||
      itemResult === undefined ||
      !resultItemIsSafe(itemResult, practiceItem, response, reviewIds)
    ) {
      return false;
    }
    score += itemResult.score;
  }
  return score === result.score;
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

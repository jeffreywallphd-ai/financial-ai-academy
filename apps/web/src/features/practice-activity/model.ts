import type { components } from "../../generated/api-client";


export type PracticePresentation =
  components["schemas"]["PracticePresentationResponseModel"];
export type PracticeItem = PracticePresentation["items"][number];
export type PracticeSubmission =
  components["schemas"]["PracticeSubmissionRequestModel"];
export type PracticeSubmissionResult =
  components["schemas"]["PracticeSubmissionResultResponseModel"];
export type PracticeProgress =
  components["schemas"]["PracticeProgressResponseModel"];
export type PracticeDraft =
  components["schemas"]["PracticeDraftResponseModel"];
export type PracticeDraftSave =
  components["schemas"]["PracticeDraftSaveRequestModel"];
export type PracticeResponse = PracticeDraftSave["responses"][number];

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
  | { status: "attempt-limit" }
  | { status: "unavailable" }
  | { status: "invalid-result" }
  | { status: "unexpected" };

export type PracticeSubmitter = (
  practice: PracticePresentation,
  submission: PreparedPracticeSubmission,
  signal?: AbortSignal,
) => Promise<PracticeSubmissionOutcome>;

export type PreparedPracticeDraftSave = Readonly<{
  body: PracticeDraftSave;
  placementId: string;
}>;

export type PracticeDraftSavePreparation =
  | { status: "ready"; save: PreparedPracticeDraftSave }
  | { status: "invalid"; itemId: string };

export type PracticeProgressOutcome =
  | { status: "progress"; progress: PracticeProgress }
  | { status: "unauthorized" }
  | { status: "forbidden" }
  | { status: "not-found" }
  | { status: "unavailable" }
  | { status: "invalid-result" }
  | { status: "unexpected" };

export type PracticeProgressReader = (
  practice: PracticePresentation,
  signal?: AbortSignal,
) => Promise<PracticeProgressOutcome>;

export type PracticeDraftSaveOutcome =
  | { status: "saved"; draft: PracticeDraft }
  | { status: "invalid-request" }
  | { status: "unauthorized" }
  | { status: "forbidden" }
  | { status: "not-found" }
  | { status: "conflict" }
  | { status: "unavailable" }
  | { status: "invalid-result" }
  | { status: "unexpected" };

export type PracticeDraftSaver = (
  practice: PracticePresentation,
  save: PreparedPracticeDraftSave,
  signal?: AbortSignal,
) => Promise<PracticeDraftSaveOutcome>;

export type PracticeActivityRouteState =
  | { status: "loading" }
  | {
      status: "ready";
      practice: PracticePresentation;
      progress: PracticeProgress;
    }
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
const PROGRESS_KEYS = [
  "draft",
  "history",
  "placement_id",
  "retry_state",
  "review_targets",
  "schema_version",
] as const;
const DRAFT_KEYS = [
  "attempt_policy_id",
  "attempt_policy_version",
  "definition_digest",
  "package_digest",
  "package_id",
  "package_version",
  "placement_id",
  "practice_id",
  "practice_version",
  "response_fingerprint",
  "responses",
  "revision",
  "saved_at",
  "schema_version",
] as const;
const RETRY_KEYS = [
  "attempt_policy_id",
  "attempt_policy_version",
  "attempts_remaining",
  "attempts_used",
  "can_retry",
  "definition_digest",
  "max_attempts",
  "package_digest",
  "package_id",
  "package_version",
  "placement_id",
  "practice_id",
  "practice_version",
  "schema_version",
  "state",
] as const;
const HISTORY_KEYS = [
  "attempt_policy_id",
  "attempt_policy_version",
  "attempts",
  "definition_digest",
  "package_digest",
  "package_id",
  "package_version",
  "placement_id",
  "practice_id",
  "practice_version",
  "schema_version",
  "source_digest",
] as const;
const HISTORY_ATTEMPT_KEYS = [
  "attempt_id",
  "attempt_order",
  "completed_at",
  "event_id",
  "evidence_id",
  "item_summaries",
  "max_score",
  "outcome",
  "score",
  "submission_id",
] as const;
const HISTORY_ITEM_KEYS = [
  "correct",
  "item_id",
  "item_type",
  "item_version",
  "max_score",
  "review_reference_ids",
  "score",
  "scoring_policy_id",
  "scoring_policy_version",
] as const;
const REVIEW_TARGET_KEYS = [
  "practice_placement_id",
  "resource_digest",
  "resource_id",
  "resource_title",
  "resource_version",
  "schema_version",
  "state",
] as const;
const REVIEW_DESTINATION_KEYS = [
  "package_digest",
  "package_id",
  "package_version",
  "placement_id",
] as const;
const RESPONSE_COMMON_KEYS = [
  "item_id",
  "item_type",
  "item_version",
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

function scopeMatches(
  value: Record<string, unknown>,
  practice: PracticePresentation,
): boolean {
  return (
    value.placement_id === practice.placement_id &&
    value.package_id === practice.package_id &&
    value.package_version === practice.package_version &&
    value.package_digest === practice.package_digest &&
    value.definition_digest === practice.definition_digest &&
    value.practice_id === practice.practice_id &&
    value.practice_version === practice.practice_version &&
    value.attempt_policy_id === practice.attempt_policy.policy_id &&
    value.attempt_policy_version === practice.attempt_policy.policy_version
  );
}

function responseIsSafe(
  value: unknown,
  item: PracticeItem,
): value is PracticeResponse {
  const response = record(value);
  if (
    response === null ||
    response.item_id !== item.item_id ||
    response.item_type !== item.item_type ||
    response.item_version !== item.item_version ||
    response.scoring_policy_id !== item.scoring_policy_id ||
    response.scoring_policy_version !== item.scoring_policy_version
  ) {
    return false;
  }
  if (item.item_type === "single_select") {
    return (
      exactKeys(response, [...RESPONSE_COMMON_KEYS, "selected_option_id"]) &&
      typeof response.selected_option_id === "string" &&
      item.options.some(
        (option) => option.option_id === response.selected_option_id,
      )
    );
  }
  if (item.item_type === "multiple_select") {
    if (
      !exactKeys(response, [...RESPONSE_COMMON_KEYS, "selected_option_ids"]) ||
      !boundedArray(response.selected_option_ids, 1, item.options.length)
    ) {
      return false;
    }
    const selected = response.selected_option_ids;
    return (
      selected.every(
        (candidate): candidate is string =>
          typeof candidate === "string" &&
          item.options.some((option) => option.option_id === candidate),
      ) && new Set(selected).size === selected.length
    );
  }
  return (
    exactKeys(response, [...RESPONSE_COMMON_KEYS, "entered_value"]) &&
    typeof response.entered_value === "string" &&
    decimalIsCanonical(
      response.entered_value,
      item.scale,
      item.allow_negative,
    )
  );
}

function responsesAreSafe(
  value: unknown,
  practice: PracticePresentation,
): value is PracticeResponse[] {
  if (!boundedArray(value, 0, practice.items.length)) {
    return false;
  }
  const seen = new Set<string>();
  for (const response of value) {
    const candidate = record(response);
    if (candidate === null || typeof candidate.item_id !== "string") {
      return false;
    }
    const index = practice.items.findIndex(
      (item) => item.item_id === candidate.item_id,
    );
    if (
      index < 0 ||
      seen.has(candidate.item_id) ||
      !responseIsSafe(response, practice.items[index]!)
    ) {
      return false;
    }
    seen.add(candidate.item_id);
  }
  return true;
}

export function practiceDraftIsSafe(
  value: unknown,
  practice: PracticePresentation,
): value is PracticeDraft {
  const draft = record(value);
  return (
    draft !== null &&
    exactKeys(draft, DRAFT_KEYS) &&
    draft.schema_version === "1.0.0" &&
    scopeMatches(draft, practice) &&
    responsesAreSafe(draft.responses, practice) &&
    Number.isInteger(draft.revision) &&
    Number(draft.revision) >= 1 &&
    canonicalUtcTimestamp(draft.saved_at) &&
    typeof draft.response_fingerprint === "string" &&
    DIGEST.test(draft.response_fingerprint)
  );
}

function responseMatches(
  actual: PracticeResponse,
  expected: PracticeResponse,
): boolean {
  if (
    actual.item_id !== expected.item_id ||
    actual.item_type !== expected.item_type ||
    actual.item_version !== expected.item_version ||
    actual.scoring_policy_id !== expected.scoring_policy_id ||
    actual.scoring_policy_version !== expected.scoring_policy_version
  ) {
    return false;
  }
  if (
    actual.item_type === "single_select" &&
    expected.item_type === "single_select"
  ) {
    return actual.selected_option_id === expected.selected_option_id;
  }
  if (
    actual.item_type === "multiple_select" &&
    expected.item_type === "multiple_select"
  ) {
    return sameStringSet(
      actual.selected_option_ids,
      expected.selected_option_ids,
    );
  }
  return (
    actual.item_type === "numeric_entry" &&
    expected.item_type === "numeric_entry" &&
    actual.entered_value === expected.entered_value
  );
}

export function practiceDraftSaveResultIsSafe(
  value: unknown,
  practice: PracticePresentation,
  prepared: PreparedPracticeDraftSave,
): value is PracticeDraft {
  if (
    !practiceDraftIsSafe(value, practice) ||
    prepared.placementId !== practice.placement_id ||
    value.responses.length !== prepared.body.responses.length ||
    value.responses.some((response) => {
      const expected = prepared.body.responses.find(
        (candidate) => candidate.item_id === response.item_id,
      );
      return expected === undefined || !responseMatches(response, expected);
    })
  ) {
    return false;
  }
  const expectedRevision = prepared.body.expected_revision;
  return value.revision >= Math.max(1, expectedRevision);
}

function retryStateIsSafe(
  value: unknown,
  practice: PracticePresentation,
): boolean {
  const retry = record(value);
  if (
    retry === null ||
    !exactKeys(retry, RETRY_KEYS) ||
    retry.schema_version !== "1.0.0" ||
    !scopeMatches(retry, practice) ||
    retry.max_attempts !== practice.attempt_policy.max_attempts ||
    !Number.isInteger(retry.attempts_used) ||
    !Number.isInteger(retry.attempts_remaining)
  ) {
    return false;
  }
  const used = Number(retry.attempts_used);
  const remaining = Number(retry.attempts_remaining);
  const maximum = practice.attempt_policy.max_attempts;
  return (
    used >= 0 &&
    remaining >= 0 &&
    used + remaining === maximum &&
    retry.can_retry === (remaining > 0) &&
    retry.state === (remaining > 0 ? "available" : "exhausted")
  );
}

function historyItemIsSafe(
  value: unknown,
  practiceItem: PracticeItem,
  reviewIds: ReadonlySet<string>,
): boolean {
  const item = record(value);
  return (
    item !== null &&
    exactKeys(item, HISTORY_ITEM_KEYS) &&
    item.item_id === practiceItem.item_id &&
    item.item_type === practiceItem.item_type &&
    item.item_version === practiceItem.item_version &&
    item.scoring_policy_id === practiceItem.scoring_policy_id &&
    item.scoring_policy_version === practiceItem.scoring_policy_version &&
    item.max_score === 1 &&
    (item.score === 0 || item.score === 1) &&
    item.correct === (item.score === 1) &&
    boundedArray(item.review_reference_ids, 0, 8) &&
    item.review_reference_ids.every(
      (candidate): candidate is string =>
        typeof candidate === "string" && reviewIds.has(candidate),
    ) &&
    new Set(item.review_reference_ids).size ===
      item.review_reference_ids.length
  );
}

function historyIsSafe(
  value: unknown,
  practice: PracticePresentation,
): boolean {
  const history = record(value);
  if (
    history === null ||
    !exactKeys(history, HISTORY_KEYS) ||
    history.schema_version !== "1.0.0" ||
    !scopeMatches(history, practice) ||
    typeof history.source_digest !== "string" ||
    !DIGEST.test(history.source_digest) ||
    !boundedArray(history.attempts, 0, practice.attempt_policy.max_attempts)
  ) {
    return false;
  }
  const reviewIds = new Set(
    practice.review_references.map((reference) => reference.resource_id),
  );
  const eventIds = new Set<string>();
  const attemptIds = new Set<string>();
  const evidenceIds = new Set<string>();
  const submissionIds = new Set<string>();
  for (const [index, valueAttempt] of history.attempts.entries()) {
    const attempt = record(valueAttempt);
    if (
      attempt === null ||
      !exactKeys(attempt, HISTORY_ATTEMPT_KEYS) ||
      attempt.attempt_order !== index + 1 ||
      typeof attempt.event_id !== "string" ||
      !UUID.test(attempt.event_id) ||
      typeof attempt.attempt_id !== "string" ||
      !UUID.test(attempt.attempt_id) ||
      typeof attempt.evidence_id !== "string" ||
      !UUID.test(attempt.evidence_id) ||
      typeof attempt.submission_id !== "string" ||
      !UUID.test(attempt.submission_id) ||
      !Number.isInteger(attempt.score) ||
      !Number.isInteger(attempt.max_score) ||
      attempt.max_score !== practice.items.length ||
      Number(attempt.score) < 0 ||
      Number(attempt.score) > Number(attempt.max_score) ||
      attempt.outcome !==
        (attempt.score === attempt.max_score ? "all_correct" : "review_needed") ||
      !canonicalUtcTimestamp(attempt.completed_at) ||
      !Array.isArray(attempt.item_summaries) ||
      attempt.item_summaries.length !== practice.items.length ||
      attempt.item_summaries.some(
        (summary, itemIndex) =>
          !historyItemIsSafe(
            summary,
            practice.items[itemIndex]!,
            reviewIds,
          ),
      )
    ) {
      return false;
    }
    const summaries = attempt.item_summaries.map((summary) => record(summary)!);
    const summaryScore = summaries.reduce(
      (total, summary) => total + Number(summary.score),
      0,
    );
    const summaryMaximum = summaries.reduce(
      (total, summary) => total + Number(summary.max_score),
      0,
    );
    if (
      summaryScore !== attempt.score ||
      summaryMaximum !== attempt.max_score
    ) {
      return false;
    }
    const identities = [
      [eventIds, attempt.event_id],
      [attemptIds, attempt.attempt_id],
      [evidenceIds, attempt.evidence_id],
      [submissionIds, attempt.submission_id],
    ] as const;
    for (const [seen, identity] of identities) {
      if (seen.has(identity)) {
        return false;
      }
      seen.add(identity);
    }
  }
  return true;
}

function reviewTargetIsSafe(
  value: unknown,
  practice: PracticePresentation,
): boolean {
  const target = record(value);
  if (
    target === null ||
    target.schema_version !== "1.0.0" ||
    target.practice_placement_id !== practice.placement_id ||
    !identifier(target.resource_id) ||
    !semanticVersion(target.resource_version) ||
    typeof target.resource_digest !== "string" ||
    !DIGEST.test(target.resource_digest) ||
    !safeText(target.resource_title, 240)
  ) {
    return false;
  }
  const reference = practice.review_references.find(
    (candidate) => candidate.resource_id === target.resource_id,
  );
  if (
    reference === undefined ||
    reference.resource_version !== target.resource_version ||
    reference.resource_digest !== target.resource_digest ||
    reference.title !== target.resource_title
  ) {
    return false;
  }
  if (target.state === "available") {
    if (!exactKeys(target, [...REVIEW_TARGET_KEYS, "destination"])) {
      return false;
    }
    const destination = record(target.destination);
    if (destination === null) {
      return false;
    }
    const hasSection = Object.hasOwn(destination, "section_id");
    return (
      exactKeys(
        destination,
        hasSection
          ? [...REVIEW_DESTINATION_KEYS, "section_id"]
          : REVIEW_DESTINATION_KEYS,
      ) &&
      identifier(destination.placement_id) &&
      identifier(destination.package_id) &&
      semanticVersion(destination.package_version) &&
      typeof destination.package_digest === "string" &&
      DIGEST.test(destination.package_digest) &&
      (!hasSection ||
        destination.section_id === null ||
        identifier(destination.section_id))
    );
  }
  return (
    target.state === "unavailable" &&
    exactKeys(target, [...REVIEW_TARGET_KEYS, "unavailable_reason"]) &&
    (target.unavailable_reason === "mapping_not_found" ||
      target.unavailable_reason === "destination_not_available" ||
      target.unavailable_reason === "version_mismatch")
  );
}

export function practiceProgressIsSafe(
  value: unknown,
  practice: PracticePresentation,
): value is PracticeProgress {
  const progress = record(value);
  const hasSchemaVersion =
    progress !== null && Object.hasOwn(progress, "schema_version");
  if (
    progress === null ||
    !exactKeys(
      progress,
      hasSchemaVersion
        ? PROGRESS_KEYS
        : PROGRESS_KEYS.filter((key) => key !== "schema_version"),
    ) ||
    (hasSchemaVersion && progress.schema_version !== "1.0.0") ||
    progress.placement_id !== practice.placement_id ||
    (progress.draft !== null &&
      !practiceDraftIsSafe(progress.draft, practice)) ||
    !retryStateIsSafe(progress.retry_state, practice) ||
    !historyIsSafe(progress.history, practice) ||
    !boundedArray(progress.review_targets, 0, 8)
  ) {
    return false;
  }
  const retry = record(progress.retry_state)!;
  const history = record(progress.history)!;
  const attempts = history.attempts as unknown[];
  if (Number(retry.attempts_used) !== attempts.length) {
    return false;
  }
  const ids = new Set<string>();
  const actualReviewIds: string[] = [];
  for (const target of progress.review_targets) {
    if (!reviewTargetIsSafe(target, practice)) {
      return false;
    }
    const resourceId = String(record(target)?.resource_id);
    if (ids.has(resourceId)) {
      return false;
    }
    ids.add(resourceId);
    actualReviewIds.push(resourceId);
  }
  const expectedReviewIds: string[] = [];
  const expectedReviewIdSet = new Set<string>();
  const latestAttempt = record(attempts.at(-1));
  if (latestAttempt !== null) {
    for (const summaryValue of latestAttempt.item_summaries as unknown[]) {
      const summary = record(summaryValue)!;
      if (summary.correct) {
        continue;
      }
      for (const reviewId of summary.review_reference_ids as string[]) {
        if (!expectedReviewIdSet.has(reviewId)) {
          expectedReviewIdSet.add(reviewId);
          expectedReviewIds.push(reviewId);
        }
      }
    }
  }
  return (
    actualReviewIds.length === expectedReviewIds.length &&
    actualReviewIds.every(
      (resourceId, index) => resourceId === expectedReviewIds[index],
    )
  );
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

export function preparePracticeDraftSave(
  practice: PracticePresentation,
  formData: FormData,
  expectedRevision: number,
): PracticeDraftSavePreparation {
  const responses: PracticeResponse[] = [];
  for (const item of practice.items) {
    const values = formData
      .getAll(item.item_id)
      .filter((value): value is string => typeof value === "string");
    if (item.item_type === "single_select") {
      if (values.length === 0) {
        continue;
      }
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
      if (values.length === 0) {
        continue;
      }
      const selected = new Set(values);
      if (
        selected.size !== values.length ||
        values.some(
          (candidate) =>
            !item.options.some((option) => option.option_id === candidate),
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
    if (values.length === 1 && entered.length === 0) {
      continue;
    }
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
    save: {
      placementId: practice.placement_id,
      body: {
        schema_version: "1.0.0",
        placement_id: practice.placement_id,
        package_id: practice.package_id,
        package_version: practice.package_version,
        package_digest: practice.package_digest,
        definition_digest: practice.definition_digest,
        practice_id: practice.practice_id,
        practice_version: practice.practice_version,
        attempt_policy_id: practice.attempt_policy.policy_id,
        attempt_policy_version: practice.attempt_policy.policy_version,
        expected_revision: expectedRevision,
        responses,
      },
    },
  };
}

export function savedResponseForItem(
  draft: PracticeDraft | null,
  itemId: string,
): PracticeResponse | undefined {
  return draft?.responses.find((response) => response.item_id === itemId);
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

import type { components } from "../../generated/api-client";

export type CurriculumGraph =
  components["schemas"]["CurriculumGraphResponseModel"];
export type CurriculumObjective =
  components["schemas"]["CurriculumObjectiveResponseModel"];
export type CurriculumCompetency =
  components["schemas"]["CurriculumCompetencyResponseModel"];
export type CurriculumActivity =
  components["schemas"]["CurriculumActivityResponseModel"];
export type CurriculumBranch =
  components["schemas"]["CurriculumBranchResponseModel"];
export type CurriculumRelationship =
  components["schemas"]["CurriculumRelationshipResponseModel"];

export interface CurriculumGraphSelection {
  curriculumId: string;
  curriculumVersion: string;
}

export type CurriculumGraphRouteState =
  | { status: "loading" }
  | { status: "ready"; graph: CurriculumGraph }
  | { status: "invalid-selection" }
  | { status: "unauthorized" }
  | { status: "forbidden" }
  | { status: "not-found" }
  | { status: "unavailable" }
  | { status: "invalid-response" }
  | { status: "unexpected" };

const IDENTIFIER = /^[a-z0-9][a-z0-9._-]{2,63}$/;
const SEMANTIC_VERSION =
  /^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?$/;
const DIGEST = /^[a-f0-9]{64}$/;
const SOURCE_REFERENCE = /^[a-z][a-z0-9+.-]{1,31}:\S{1,255}$/;
const DATE_TIME =
  /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.(\d{1,6}))?(Z|[+-](\d{2}):(\d{2}))$/;

const GRAPH_KEYS = [
  "activities",
  "branches",
  "competencies",
  "curriculum_id",
  "curriculum_version",
  "graph_digest",
  "objectives",
  "publication_state",
  "published_at",
  "relationships",
  "schema_version",
  "source_references",
  "summary",
  "title",
] as const;
const OBJECTIVE_KEYS = ["description", "objective_id", "title"] as const;
const COMPETENCY_KEYS = ["competency_id", "description", "title"] as const;
const ACTIVITY_KEYS = ["activity_id", "kind", "reference", "title"] as const;
const LESSON_REFERENCE_KEYS = [
  "package_digest",
  "package_id",
  "package_version",
  "placement_id",
  "reference_kind",
] as const;
const ASSESSMENT_REFERENCE_KEYS = [
  "assessment_id",
  "assessment_version",
  "definition_digest",
  "placement_id",
  "reference_kind",
] as const;
const BRANCH_KEYS = ["activity_ids", "branch_id", "kind", "title"] as const;
const RELATIONSHIP_KEYS = [
  "kind",
  "relationship_id",
  "source_id",
  "target_id",
] as const;
const PRESENTATION_KEYS = [
  "activity_ids",
  "branch_ids",
  "competency_ids",
  "objective_ids",
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

function validDateTime(value: unknown): value is string {
  if (typeof value !== "string") return false;
  const match = DATE_TIME.exec(value);
  if (!match) return false;
  const month = Number(match[2]);
  const day = Number(match[3]);
  const hour = Number(match[4]);
  const minute = Number(match[5]);
  const second = Number(match[6]);
  const offsetHour = Number(match[9] ?? "0");
  const offsetMinute = Number(match[10] ?? "0");
  const daysInMonth = new Date(
    Date.UTC(Number(match[1]), month, 0),
  ).getUTCDate();
  return (
    month >= 1 &&
    month <= 12 &&
    day >= 1 &&
    day <= daysInMonth &&
    hour <= 23 &&
    minute <= 59 &&
    second <= 59 &&
    offsetHour <= 23 &&
    offsetMinute <= 59 &&
    !Number.isNaN(Date.parse(value))
  );
}

function identifier(value: unknown): value is string {
  return typeof value === "string" && IDENTIFIER.test(value);
}

function version(value: unknown): value is string {
  return typeof value === "string" && SEMANTIC_VERSION.test(value);
}

function digest(value: unknown): value is string {
  return typeof value === "string" && DIGEST.test(value);
}

function uniqueArray(
  value: unknown,
  minimum: number,
  maximum: number,
  itemIsSafe: (item: unknown) => boolean,
): value is unknown[] {
  return (
    Array.isArray(value) &&
    value.length >= minimum &&
    value.length <= maximum &&
    value.every(itemIsSafe) &&
    new Set(value).size === value.length
  );
}

function objectiveIsSafe(value: unknown): boolean {
  const candidate = record(value);
  return (
    candidate !== null &&
    hasExactKeys(candidate, OBJECTIVE_KEYS) &&
    identifier(candidate.objective_id) &&
    boundedText(candidate.title, 1, 240) &&
    boundedText(candidate.description, 1, 1000)
  );
}

function competencyIsSafe(value: unknown): boolean {
  const candidate = record(value);
  return (
    candidate !== null &&
    hasExactKeys(candidate, COMPETENCY_KEYS) &&
    identifier(candidate.competency_id) &&
    boundedText(candidate.title, 1, 240) &&
    boundedText(candidate.description, 1, 1000)
  );
}

function activityIsSafe(value: unknown): boolean {
  const candidate = record(value);
  const reference = record(candidate?.reference);
  if (
    candidate === null ||
    reference === null ||
    !hasExactKeys(candidate, ACTIVITY_KEYS) ||
    !identifier(candidate.activity_id) ||
    !boundedText(candidate.title, 1, 240)
  ) {
    return false;
  }
  if (candidate.kind === "lesson") {
    return (
      hasExactKeys(reference, LESSON_REFERENCE_KEYS) &&
      reference.reference_kind === "lesson_placement" &&
      identifier(reference.placement_id) &&
      identifier(reference.package_id) &&
      version(reference.package_version) &&
      digest(reference.package_digest)
    );
  }
  return (
    candidate.kind === "assessment" &&
    hasExactKeys(reference, ASSESSMENT_REFERENCE_KEYS) &&
    reference.reference_kind === "assessment_placement" &&
    identifier(reference.placement_id) &&
    identifier(reference.assessment_id) &&
    version(reference.assessment_version) &&
    digest(reference.definition_digest)
  );
}

function branchIsSafe(value: unknown): boolean {
  const candidate = record(value);
  return (
    candidate !== null &&
    hasExactKeys(candidate, BRANCH_KEYS) &&
    identifier(candidate.branch_id) &&
    boundedText(candidate.title, 1, 240) &&
    ["required", "optional"].includes(String(candidate.kind)) &&
    uniqueArray(candidate.activity_ids, 1, 500, identifier)
  );
}

function relationshipIsSafe(value: unknown): boolean {
  const candidate = record(value);
  return (
    candidate !== null &&
    hasExactKeys(candidate, RELATIONSHIP_KEYS) &&
    identifier(candidate.relationship_id) &&
    [
      "objective_competency",
      "activity_develops_competency",
      "activity_assesses_competency",
      "competency_prerequisite",
      "activity_prerequisite",
    ].includes(String(candidate.kind)) &&
    identifier(candidate.source_id) &&
    identifier(candidate.target_id) &&
    candidate.source_id !== candidate.target_id
  );
}

function idsAreUnique(
  values: readonly Record<string, unknown>[],
  key: string,
): boolean {
  const ids = values.map((value) => value[key]);
  return new Set(ids).size === ids.length;
}

function presentationOrderIsSafe(
  value: unknown,
  allowed: Readonly<Record<keyof PresentationIds, ReadonlySet<string>>>,
): boolean {
  if (value === undefined || value === null) return true;
  const candidate = record(value);
  if (
    candidate === null ||
    Object.keys(candidate).some((key) => !PRESENTATION_KEYS.includes(key as never))
  ) {
    return false;
  }
  return PRESENTATION_KEYS.every((key) => {
    if (!(key in candidate)) return true;
    return uniqueArray(candidate[key], 0, 500, (item) =>
      identifier(item) && allowed[key].has(item),
    );
  });
}

interface PresentationIds {
  objective_ids: ReadonlySet<string>;
  competency_ids: ReadonlySet<string>;
  activity_ids: ReadonlySet<string>;
  branch_ids: ReadonlySet<string>;
}

export function parseCurriculumGraphSelection(
  curriculumId: unknown,
  curriculumVersion: unknown,
  url: string,
): CurriculumGraphSelection | null {
  let request: URL;
  try {
    request = new URL(url);
  } catch {
    return null;
  }
  return identifier(curriculumId) &&
    version(curriculumVersion) &&
    request.search === "" &&
    request.hash === ""
    ? { curriculumId, curriculumVersion }
    : null;
}

export function curriculumGraphIsSafe(
  value: unknown,
  expected: CurriculumGraphSelection,
): value is CurriculumGraph {
  const candidate = record(value);
  if (candidate === null) return false;
  const expectedKeys =
    "presentation_order" in candidate
      ? [...GRAPH_KEYS, "presentation_order"]
      : GRAPH_KEYS;
  if (
    !hasExactKeys(candidate, expectedKeys) ||
    candidate.schema_version !== "1.0.0" ||
    candidate.curriculum_id !== expected.curriculumId ||
    candidate.curriculum_version !== expected.curriculumVersion ||
    !identifier(candidate.curriculum_id) ||
    !version(candidate.curriculum_version) ||
    !boundedText(candidate.title, 1, 240) ||
    !boundedText(candidate.summary, 20, 500) ||
    candidate.publication_state !== "approved" ||
    !validDateTime(candidate.published_at) ||
    !uniqueArray(candidate.source_references, 1, 20, (item) =>
      typeof item === "string" && SOURCE_REFERENCE.test(item),
    ) ||
    !Array.isArray(candidate.objectives) ||
    candidate.objectives.length < 1 ||
    candidate.objectives.length > 100 ||
    !candidate.objectives.every(objectiveIsSafe) ||
    !Array.isArray(candidate.competencies) ||
    candidate.competencies.length < 1 ||
    candidate.competencies.length > 200 ||
    !candidate.competencies.every(competencyIsSafe) ||
    !Array.isArray(candidate.activities) ||
    candidate.activities.length < 1 ||
    candidate.activities.length > 500 ||
    !candidate.activities.every(activityIsSafe) ||
    !Array.isArray(candidate.branches) ||
    candidate.branches.length > 100 ||
    !candidate.branches.every(branchIsSafe) ||
    !Array.isArray(candidate.relationships) ||
    candidate.relationships.length > 2000 ||
    !candidate.relationships.every(relationshipIsSafe) ||
    !digest(candidate.graph_digest)
  ) {
    return false;
  }

  const objectives = candidate.objectives as Record<string, unknown>[];
  const competencies = candidate.competencies as Record<string, unknown>[];
  const activities = candidate.activities as Record<string, unknown>[];
  const branches = candidate.branches as Record<string, unknown>[];
  const relationships = candidate.relationships as Record<string, unknown>[];
  if (
    !idsAreUnique(objectives, "objective_id") ||
    !idsAreUnique(competencies, "competency_id") ||
    !idsAreUnique(activities, "activity_id") ||
    !idsAreUnique(branches, "branch_id") ||
    !idsAreUnique(relationships, "relationship_id")
  ) {
    return false;
  }

  const ids: PresentationIds = {
    objective_ids: new Set(objectives.map((item) => String(item.objective_id))),
    competency_ids: new Set(
      competencies.map((item) => String(item.competency_id)),
    ),
    activity_ids: new Set(activities.map((item) => String(item.activity_id))),
    branch_ids: new Set(branches.map((item) => String(item.branch_id))),
  };
  if (!presentationOrderIsSafe(candidate.presentation_order, ids)) return false;
  if (
    branches.some((branch) =>
      (branch.activity_ids as string[]).some((id) => !ids.activity_ids.has(id)),
    )
  ) {
    return false;
  }

  return relationships.every((relationship) => {
    const source = String(relationship.source_id);
    const target = String(relationship.target_id);
    switch (relationship.kind) {
      case "objective_competency":
        return ids.objective_ids.has(source) && ids.competency_ids.has(target);
      case "activity_develops_competency":
      case "activity_assesses_competency":
        return ids.activity_ids.has(source) && ids.competency_ids.has(target);
      case "competency_prerequisite":
        return ids.competency_ids.has(source) && ids.competency_ids.has(target);
      case "activity_prerequisite":
        return ids.activity_ids.has(source) && ids.activity_ids.has(target);
      default:
        return false;
    }
  });
}

function ordered<T>(
  items: readonly T[],
  identifierOf: (item: T) => string,
  hints: readonly string[] | undefined,
): readonly T[] {
  if (!hints?.length) return items;
  const rank = new Map(hints.map((id, index) => [id, index]));
  return items
    .map((item, index) => ({ item, index }))
    .sort((left, right) => {
      const leftRank = rank.get(identifierOf(left.item));
      const rightRank = rank.get(identifierOf(right.item));
      if (leftRank === undefined && rightRank === undefined)
        return left.index - right.index;
      if (leftRank === undefined) return 1;
      if (rightRank === undefined) return -1;
      return leftRank - rightRank;
    })
    .map(({ item }) => item);
}

export function curriculumGraphPresentation(graph: CurriculumGraph) {
  return {
    objectives: ordered(
      graph.objectives,
      (item) => item.objective_id,
      graph.presentation_order?.objective_ids,
    ),
    competencies: ordered(
      graph.competencies,
      (item) => item.competency_id,
      graph.presentation_order?.competency_ids,
    ),
    activities: ordered(
      graph.activities,
      (item) => item.activity_id,
      graph.presentation_order?.activity_ids,
    ),
    branches: ordered(
      graph.branches,
      (item) => item.branch_id,
      graph.presentation_order?.branch_ids,
    ),
  };
}

import type { components } from "../../generated/api-client";


export type Lesson =
  components["schemas"]["LessonReadingResponseModel"];

export type LessonRouteState =
  | { status: "loading" }
  | { status: "ready"; lesson: Lesson }
  | { status: "unauthorized" }
  | { status: "forbidden" }
  | { status: "not-found" }
  | { status: "unavailable" }
  | { status: "invalid-content" }
  | { status: "unexpected" };

interface NodeBudget {
  remaining: number;
}

const DIGEST = /^[a-f0-9]{64}$/;
const ASSET_LOCATOR =
  /^\/api\/v1\/content\/assets\/[a-z0-9][a-z0-9._-]{2,63}$/;

function record(value: unknown): Record<string, unknown> | null {
  return typeof value === "object" && value !== null
    ? (value as Record<string, unknown>)
    : null;
}

function nonEmptyString(value: unknown): value is string {
  return typeof value === "string" && value.trim().length > 0;
}

function safeHttpsLocator(value: unknown): value is string {
  if (!nonEmptyString(value)) {
    return false;
  }
  try {
    const parsed = new URL(value);
    return (
      parsed.protocol === "https:" &&
      !parsed.username &&
      !parsed.password
    );
  } catch {
    return false;
  }
}

function inlineNodesAreSafe(
  value: unknown,
  sourceIds: ReadonlySet<string>,
  assetIds: ReadonlySet<string>,
  budget: NodeBudget,
  depth: number,
): boolean {
  if (!Array.isArray(value) || depth > 16) {
    return false;
  }
  return value.every((node) =>
    inlineNodeIsSafe(
      node,
      sourceIds,
      assetIds,
      budget,
      depth + 1,
    ),
  );
}

function inlineNodeIsSafe(
  value: unknown,
  sourceIds: ReadonlySet<string>,
  assetIds: ReadonlySet<string>,
  budget: NodeBudget,
  depth: number,
): boolean {
  if (budget.remaining <= 0) {
    return false;
  }
  budget.remaining -= 1;
  const node = record(value);
  if (!node) {
    return false;
  }
  switch (node.kind) {
    case "text":
    case "code":
      return typeof node.value === "string";
    case "soft_break":
    case "hard_break":
      return true;
    case "emphasis":
    case "strong":
      return inlineNodesAreSafe(
        node.children,
        sourceIds,
        assetIds,
        budget,
        depth,
      );
    case "source_link":
      return (
        nonEmptyString(node.source_id) &&
        sourceIds.has(node.source_id) &&
        safeHttpsLocator(node.href) &&
        inlineNodesAreSafe(
          node.children,
          sourceIds,
          assetIds,
          budget,
          depth,
        )
      );
    case "asset_image":
      return (
        nonEmptyString(node.asset_id) &&
        assetIds.has(node.asset_id) &&
        nonEmptyString(node.alt_text)
      );
    default:
      return false;
  }
}

function bodyNodesAreSafe(
  value: unknown,
  sourceIds: ReadonlySet<string>,
  assetIds: ReadonlySet<string>,
  budget: NodeBudget,
  depth: number,
): boolean {
  if (!Array.isArray(value) || depth > 16) {
    return false;
  }
  return value.every((node) =>
    bodyNodeIsSafe(
      node,
      sourceIds,
      assetIds,
      budget,
      depth + 1,
    ),
  );
}

function bodyNodeIsSafe(
  value: unknown,
  sourceIds: ReadonlySet<string>,
  assetIds: ReadonlySet<string>,
  budget: NodeBudget,
  depth: number,
): boolean {
  if (budget.remaining <= 0) {
    return false;
  }
  budget.remaining -= 1;
  const node = record(value);
  if (!node) {
    return false;
  }
  switch (node.kind) {
    case "heading":
      return (
        Number.isInteger(node.level) &&
        Number(node.level) >= 1 &&
        Number(node.level) <= 6 &&
        inlineNodesAreSafe(
          node.children,
          sourceIds,
          assetIds,
          budget,
          depth,
        )
      );
    case "paragraph":
      return inlineNodesAreSafe(
        node.children,
        sourceIds,
        assetIds,
        budget,
        depth,
      );
    case "code_block":
      return (
        typeof node.code === "string" &&
        (node.language === null ||
          node.language === undefined ||
          typeof node.language === "string")
      );
    case "thematic_break":
      return true;
    case "bullet_list":
    case "ordered_list": {
      if (
        node.kind === "ordered_list" &&
        (!Number.isInteger(node.start) || Number(node.start) < 1)
      ) {
        return false;
      }
      if (!Array.isArray(node.items)) {
        return false;
      }
      return node.items.every((item) => {
        const itemRecord = record(item);
        return (
          itemRecord !== null &&
          bodyNodesAreSafe(
            itemRecord.blocks,
            sourceIds,
            assetIds,
            budget,
            depth,
          )
        );
      });
    }
    default:
      return false;
  }
}

export function lessonContentIsSafe(lesson: Lesson): boolean {
  if (
    !nonEmptyString(lesson.title) ||
    !nonEmptyString(lesson.package_id) ||
    !nonEmptyString(lesson.package_version) ||
    !DIGEST.test(lesson.package_digest) ||
    lesson.objectives.length === 0 ||
    lesson.objectives.some((objective) => !nonEmptyString(objective))
  ) {
    return false;
  }
  const sourceIds = new Set<string>();
  for (const source of lesson.sources) {
    if (
      !nonEmptyString(source.source_id) ||
      sourceIds.has(source.source_id) ||
      !nonEmptyString(source.title) ||
      !nonEmptyString(source.publisher) ||
      !safeHttpsLocator(source.locator)
    ) {
      return false;
    }
    sourceIds.add(source.source_id);
  }
  const assetIds = new Set<string>();
  for (const asset of lesson.assets) {
    if (
      !nonEmptyString(asset.asset_id) ||
      assetIds.has(asset.asset_id) ||
      !nonEmptyString(asset.alt_text) ||
      !DIGEST.test(asset.sha256) ||
      !ASSET_LOCATOR.test(asset.locator)
    ) {
      return false;
    }
    assetIds.add(asset.asset_id);
  }
  return bodyNodesAreSafe(
    lesson.body,
    sourceIds,
    assetIds,
    { remaining: 5_000 },
    0,
  );
}

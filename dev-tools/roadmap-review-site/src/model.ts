export type PlanningStatus =
  | "captured"
  | "ready"
  | "active"
  | "verifying"
  | "complete"
  | "superseded"
  | "unknown";

export interface PlanningNode {
  id: string;
  kind: string;
  status: PlanningStatus | string;
  title: string;
  source: string;
  parent?: string | null;
  dependencies: Array<{ target: string; type: string }>;
  manifest: string[];
  decision_gates?: string[];
  document?: RoadmapDocument | null;
}

export type RoadmapDocumentBlock =
  | { type: "heading"; level: number; text: string }
  | { type: "paragraph" | "list-item" | "code"; text: string }
  | { type: "table-row"; cells: string[] };

export interface RoadmapDocument {
  source: string;
  blocks: RoadmapDocumentBlock[];
}

export interface RoadmapSlice extends Partial<PlanningNode> {
  id: string;
  refined: boolean;
  work: PlanningNode[];
}

export interface RoadmapCapability extends PlanningNode {
  slices: RoadmapSlice[];
}

export interface RoadmapCandidate {
  key: string;
  order: number;
  title: string;
  description: string;
  planning_id: string | null;
  planned: boolean;
  capability: PlanningNode | null;
  slices: RoadmapSlice[];
}

export interface BlockedCapability {
  id: string;
  reasons: string[];
  incomplete_dependencies: string[];
  remediation: string;
}

export interface CompatibilityPair {
  left: string;
  right: string;
  decision: "compatible" | "incompatible" | "unknown";
  confidence: string;
  reasons: Array<{ code: string; evidence: string[] }>;
  remediation: string;
}

export interface RoadmapReview {
  schema_version: "roadmap-review-v1";
  catalog_count: number;
  candidates: RoadmapCandidate[];
  internal_capabilities: RoadmapCapability[];
  ordering: {
    ready: Array<{ id: string; reasons: string[] }>;
    blocked: BlockedCapability[];
    completed: string[];
    in_progress: string[];
    proposed_order: string[];
    unresolved_ties: string[][];
    constraints: { accepted_sequence: string[]; stable_id_order_is_authority: boolean };
  };
  compatibility: {
    pairs: CompatibilityPair[];
    parallel_safe_sets: string[][];
    isolated_or_unresolved: string[];
    compatible_pair_count: number;
    incompatible_pair_count: number;
    unknown_pair_count: number;
  };
  graph_issues: Array<{ code?: string; subject?: string }>;
  diagnostics: Array<{ code?: string; subject?: string; blocking?: boolean }>;
  source_fingerprint: string;
}

export interface RoadmapEnvelope {
  outcome: string;
  code: string;
  message: string;
  data: { review: RoadmapReview };
}

export interface CandidateFilters {
  query: string;
  planning: "all" | "planned" | "unplanned";
  status: string;
}

export interface RoadmapCounts {
  total: number;
  planned: number;
  unplanned: number;
  byStatus: Record<string, number>;
}

export type RoadmapRoute =
  | { kind: "overview" }
  | { kind: "candidate"; candidate: RoadmapCandidate }
  | { kind: "capability"; capability: RoadmapCapability; candidate: RoadmapCandidate | null }
  | { kind: "slice"; slice: RoadmapSlice; capability: RoadmapCapability; candidate: RoadmapCandidate | null }
  | { kind: "work"; work: PlanningNode; slice: RoadmapSlice; capability: RoadmapCapability; candidate: RoadmapCandidate | null }
  | { kind: "not-found"; requestedPath: string };

export function assertRoadmapEnvelope(value: unknown): RoadmapEnvelope {
  if (!value || typeof value !== "object") throw new Error("Roadmap response is not an object.");
  const envelope = value as Partial<RoadmapEnvelope>;
  const review = envelope.data?.review;
  if (
    envelope.outcome !== "succeeded" ||
    review?.schema_version !== "roadmap-review-v1" ||
    !Array.isArray(review.candidates) ||
    review.candidates.length !== review.catalog_count
  ) {
    throw new Error("Roadmap response is missing or incompatible.");
  }
  return envelope as RoadmapEnvelope;
}

export function roadmapCounts(review: RoadmapReview): RoadmapCounts {
  const byStatus: Record<string, number> = {};
  let planned = 0;
  for (const candidate of review.candidates) {
    if (candidate.planned) planned += 1;
    const status = candidate.capability?.status ?? "unplanned";
    byStatus[status] = (byStatus[status] ?? 0) + 1;
  }
  return { total: review.candidates.length, planned, unplanned: review.candidates.length - planned, byStatus };
}

export function filterCandidates(
  candidates: RoadmapCandidate[],
  filters: CandidateFilters,
): RoadmapCandidate[] {
  const query = filters.query.trim().toLocaleLowerCase();
  return candidates.filter((candidate) => {
    if (filters.planning === "planned" && !candidate.planned) return false;
    if (filters.planning === "unplanned" && candidate.planned) return false;
    const status = candidate.capability?.status ?? "unplanned";
    if (filters.status !== "all" && status !== filters.status) return false;
    if (!query) return true;
    return [candidate.title, candidate.description, candidate.key, candidate.planning_id ?? ""]
      .join(" ")
      .toLocaleLowerCase()
      .includes(query);
  });
}

export function statusFor(review: RoadmapReview, id: string): string {
  const candidate = review.candidates.find((item) => item.planning_id === id);
  const internal = review.internal_capabilities.find((item) => item.id === id);
  return candidate?.capability?.status ?? internal?.status ?? "unknown";
}

export function titleFor(review: RoadmapReview, id: string): string {
  const candidate = review.candidates.find((item) => item.planning_id === id);
  const internal = review.internal_capabilities.find((item) => item.id === id);
  return candidate?.title ?? internal?.title ?? id;
}

export function compatibilityCounts(review: RoadmapReview): Record<string, number> {
  return review.compatibility.pairs.reduce<Record<string, number>>((counts, pair) => {
    counts[pair.decision] = (counts[pair.decision] ?? 0) + 1;
    return counts;
  }, { compatible: 0, incompatible: 0, unknown: 0 });
}

function capabilities(review: RoadmapReview): Array<{ capability: RoadmapCapability; candidate: RoadmapCandidate | null }> {
  const mapped = review.candidates.flatMap((candidate) => candidate.capability ? [{ capability: { ...candidate.capability, slices: candidate.slices }, candidate }] : []);
  const internal = review.internal_capabilities.map((capability) => ({ capability, candidate: null }));
  return [...mapped, ...internal];
}

export function resolveRoadmapRoute(review: RoadmapReview, pathname: string): RoadmapRoute {
  if (pathname === "/" || pathname === "/index.html") return { kind: "overview" };
  const match = /^\/(capability|cap|slice|work)\/([A-Za-z0-9-]+)$/.exec(pathname);
  if (!match) return { kind: "not-found", requestedPath: pathname };
  const routeKind = match[1];
  const identifier = match[2];
  if (!routeKind || !identifier) return { kind: "not-found", requestedPath: pathname };
  if (routeKind === "capability") {
    const candidate = review.candidates.find((item) => item.key === identifier);
    return candidate ? { kind: "candidate", candidate } : { kind: "not-found", requestedPath: pathname };
  }
  const allCapabilities = capabilities(review);
  if (routeKind === "cap") {
    const entry = allCapabilities.find((item) => item.capability.id === identifier);
    return entry ? { kind: "capability", ...entry } : { kind: "not-found", requestedPath: pathname };
  }
  for (const entry of allCapabilities) {
    for (const slice of entry.capability.slices) {
      if (routeKind === "slice" && slice.id === identifier) return { kind: "slice", slice, ...entry };
      if (routeKind === "work") {
        const work = slice.work.find((item) => item.id === identifier);
        if (work) return { kind: "work", work, slice, ...entry };
      }
    }
  }
  return { kind: "not-found", requestedPath: pathname };
}

export type PlanningStatus =
  | "captured"
  | "shaping"
  | "ready"
  | "active"
  | "verifying"
  | "complete"
  | "decision-blocked"
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

export interface RoadmapDecision {
  id: string;
  kind: "decision-request";
  status: PlanningStatus | string;
  title: string;
  source: string;
  dependencies: Array<{ target: string; type: string }>;
  decision_record: string | null;
  decision_made: boolean;
  document?: RoadmapDocument | null;
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

export interface CurrentAllocationLane {
  unit_id: string;
  allocation_state: "in-progress" | "proposed";
  lifecycle_status: string;
}

export interface CurrentAllocation {
  schema_version: "roadmap-current-allocation-v1";
  source_schema_version: "portfolio-allocation-v1";
  level: "capability";
  lanes: CurrentAllocationLane[];
  parallel_groups: string[][];
  unresolved_pairs: Array<{
    left: string;
    right: string;
    decision: string;
    reason_codes: string[];
    remediation: string;
  }>;
  constraints: {
    grants_authority: false;
    acquires_file_leases: false;
    creates_agents: false;
    mutates_branches: false;
    future_order_is_global_lock: false;
  };
}

export interface RoadmapReview {
  schema_version: "roadmap-review-v1";
  catalog_count: number;
  candidates: RoadmapCandidate[];
  internal_capabilities: RoadmapCapability[];
  decisions: RoadmapDecision[];
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
  current_allocation: CurrentAllocation;
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
  | { kind: "decision"; decision: RoadmapDecision }
  | { kind: "not-found"; requestedPath: string };

export function assertRoadmapEnvelope(value: unknown): RoadmapEnvelope {
  if (!value || typeof value !== "object") throw new Error("Roadmap response is not an object.");
  const envelope = value as Partial<RoadmapEnvelope>;
  const review = envelope.data?.review;
  const decisions = Array.isArray(review?.decisions) ? review.decisions : [];
  const decisionIds = decisions.map((decision) => decision.id);
  const invalidDecision = decisions.some((decision) =>
    !decision ||
    typeof decision.id !== "string" ||
    !decision.id ||
    decision.kind !== "decision-request" ||
    typeof decision.status !== "string" ||
    typeof decision.title !== "string" ||
    !decision.title ||
    typeof decision.source !== "string" ||
    !decision.source ||
    !Array.isArray(decision.dependencies) ||
    (decision.decision_record !== null && typeof decision.decision_record !== "string") ||
    typeof decision.decision_made !== "boolean" ||
    decision.decision_made !== (decision.status === "complete")
  );
  const allocation = review?.current_allocation;
  const lanes = Array.isArray(allocation?.lanes) ? allocation.lanes : [];
  const groups = Array.isArray(allocation?.parallel_groups) ? allocation.parallel_groups : [];
  const unresolvedPairs = Array.isArray(allocation?.unresolved_pairs) ? allocation.unresolved_pairs : [];
  const laneIds = lanes.map((lane) => lane.unit_id);
  const groupedIds = groups.every((group) => Array.isArray(group)) ? groups.flat() : [];
  const groupById = new Map<string, number>();
  groups.forEach((group, index) => group.forEach((id) => groupById.set(id, index)));
  const invalidUnresolvedPair = unresolvedPairs.some((pair) =>
    !pair ||
    !laneIds.includes(pair.left) ||
    !laneIds.includes(pair.right) ||
    pair.left === pair.right ||
    !["unknown", "incompatible"].includes(pair.decision) ||
    !Array.isArray(pair.reason_codes) ||
    typeof pair.remediation !== "string" ||
    groupById.get(pair.left) === groupById.get(pair.right)
  );
  if (
    envelope.outcome !== "succeeded" ||
    review?.schema_version !== "roadmap-review-v1" ||
    !Array.isArray(review.candidates) ||
    review.candidates.length !== review.catalog_count ||
    !Array.isArray(review.decisions) ||
    decisionIds.length !== new Set(decisionIds).size ||
    invalidDecision ||
    allocation?.schema_version !== "roadmap-current-allocation-v1" ||
    allocation?.source_schema_version !== "portfolio-allocation-v1" ||
    allocation?.level !== "capability" ||
    !Array.isArray(allocation.lanes) ||
    !Array.isArray(allocation.parallel_groups) ||
    !Array.isArray(allocation.unresolved_pairs) ||
    allocation?.constraints?.grants_authority !== false ||
    allocation?.constraints?.acquires_file_leases !== false ||
    allocation?.constraints?.creates_agents !== false ||
    allocation?.constraints?.mutates_branches !== false ||
    allocation?.constraints?.future_order_is_global_lock !== false ||
    lanes.some((lane) => !lane.unit_id || !["in-progress", "proposed"].includes(lane.allocation_state)) ||
    groups.some((group) => !Array.isArray(group) || group.length === 0) ||
    laneIds.length !== new Set(laneIds).size ||
    groupedIds.length !== new Set(groupedIds).size ||
    groupedIds.length !== laneIds.length ||
    groupedIds.some((id) => !laneIds.includes(id)) ||
    invalidUnresolvedPair
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
  const match = /^\/(capability|cap|slice|work|decision)\/([A-Za-z0-9-]+)$/.exec(pathname);
  if (!match) return { kind: "not-found", requestedPath: pathname };
  const routeKind = match[1];
  const identifier = match[2];
  if (!routeKind || !identifier) return { kind: "not-found", requestedPath: pathname };
  if (routeKind === "capability") {
    const candidate = review.candidates.find((item) => item.key === identifier);
    return candidate ? { kind: "candidate", candidate } : { kind: "not-found", requestedPath: pathname };
  }
  if (routeKind === "decision") {
    const decision = review.decisions.find((item) => item.id === identifier);
    return decision ? { kind: "decision", decision } : { kind: "not-found", requestedPath: pathname };
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

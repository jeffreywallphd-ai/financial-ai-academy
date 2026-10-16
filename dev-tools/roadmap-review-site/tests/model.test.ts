import { assertRoadmapEnvelope, compatibilityCounts, filterCandidates, resolveRoadmapRoute, roadmapCounts, type RoadmapReview } from "../src/model.js";

function review(): RoadmapReview {
  const candidates = Array.from({ length: 26 }, (_, index) => ({
    key: `candidate-${index + 1}`,
    order: index + 1,
    title: `Candidate ${index + 1}`,
    description: index === 0 ? "Foundational learning" : "Future capability",
    planning_id: index < 2 ? `PLAN-${index + 1}` : null,
    planned: index < 2,
    capability: index < 2 ? {
      id: `PLAN-${index + 1}`,
      kind: "capability",
      status: index === 0 ? "ready" : "complete",
      title: `Plan ${index + 1}`,
      source: `plans/${index + 1}.md`,
      dependencies: [],
      manifest: [],
    } : null,
    slices: [],
  }));
  return {
    schema_version: "roadmap-review-v1",
    catalog_count: 26,
    candidates,
    internal_capabilities: [],
    ordering: {
      ready: [{ id: "PLAN-1", reasons: ["ready"] }],
      blocked: [],
      completed: ["PLAN-2"],
      in_progress: [],
      proposed_order: ["PLAN-1", "PLAN-2"],
      unresolved_ties: [["PLAN-1", "PLAN-2"]],
      constraints: { accepted_sequence: [], stable_id_order_is_authority: false },
    },
    compatibility: {
      pairs: [
        { left: "PLAN-1", right: "PLAN-2", decision: "unknown", confidence: "low", reasons: [{ code: "evidence.missing", evidence: [] }], remediation: "Refine evidence." },
      ],
      parallel_safe_sets: [],
      isolated_or_unresolved: ["PLAN-1", "PLAN-2"],
      compatible_pair_count: 0,
      incompatible_pair_count: 0,
      unknown_pair_count: 1,
    },
    current_allocation: {
      schema_version: "roadmap-current-allocation-v1",
      source_schema_version: "portfolio-allocation-v1",
      level: "capability",
      lanes: [{ unit_id: "PLAN-1", allocation_state: "proposed", lifecycle_status: "ready" }],
      parallel_groups: [["PLAN-1"]],
      unresolved_pairs: [],
      constraints: { grants_authority: false, acquires_file_leases: false, creates_agents: false, mutates_branches: false, future_order_is_global_lock: false },
    },
    graph_issues: [],
    diagnostics: [],
    source_fingerprint: "sha256:test",
  };
}

describe("roadmap overview model", () => {
  it("accounts for all candidates and truthful planning states", () => {
    expect(roadmapCounts(review())).toEqual({
      total: 26,
      planned: 2,
      unplanned: 24,
      byStatus: { ready: 1, complete: 1, unplanned: 24 },
    });
  });

  it("filters by text, planning coverage, and lifecycle without changing input", () => {
    const value = review();
    expect(filterCandidates(value.candidates, { query: "foundational", planning: "all", status: "all" })).toHaveLength(1);
    expect(filterCandidates(value.candidates, { query: "", planning: "unplanned", status: "all" })).toHaveLength(24);
    expect(filterCandidates(value.candidates, { query: "", planning: "planned", status: "complete" })).toHaveLength(1);
    expect(value.candidates).toHaveLength(26);
  });

  it("keeps unknown compatibility separate from safe evidence", () => {
    const value = review();
    expect(compatibilityCounts(value)).toEqual({ compatible: 0, incompatible: 0, unknown: 1 });
    expect(value.compatibility.parallel_safe_sets).toEqual([]);
  });

  it("rejects malformed or count-drifted envelopes", () => {
    expect(() => assertRoadmapEnvelope({ outcome: "succeeded", data: { review: { ...review(), catalog_count: 25 } } })).toThrow(/missing or incompatible/);
    const missingAllocation: Partial<RoadmapReview> = { ...review() };
    delete missingAllocation.current_allocation;
    expect(() => assertRoadmapEnvelope({ outcome: "succeeded", data: { review: missingAllocation } })).toThrow(/missing or incompatible/);
    const inconsistent = review();
    inconsistent.current_allocation.parallel_groups = [["PLAN-2"]];
    expect(() => assertRoadmapEnvelope({ outcome: "succeeded", data: { review: inconsistent } })).toThrow(/missing or incompatible/);
    const contradictory = review();
    contradictory.current_allocation.lanes.push({ unit_id: "PLAN-2", allocation_state: "proposed", lifecycle_status: "complete" });
    contradictory.current_allocation.parallel_groups = [["PLAN-1", "PLAN-2"]];
    contradictory.current_allocation.unresolved_pairs = [{
      left: "PLAN-1", right: "PLAN-2", decision: "unknown", reason_codes: ["evidence.missing"], remediation: "Refine evidence.",
    }];
    expect(() => assertRoadmapEnvelope({ outcome: "succeeded", data: { review: contradictory } })).toThrow(/missing or incompatible/);
    contradictory.current_allocation.parallel_groups = [["PLAN-1"], ["PLAN-2"]];
    expect(assertRoadmapEnvelope({ outcome: "succeeded", data: { review: contradictory } }).data.review.current_allocation.parallel_groups).toHaveLength(2);
    expect(() => assertRoadmapEnvelope(null)).toThrow(/not an object/);
  });

  it("resolves only projected stable route identifiers", () => {
    const value = review();
    expect(resolveRoadmapRoute(value, "/capability/candidate-1").kind).toBe("candidate");
    expect(resolveRoadmapRoute(value, "/cap/PLAN-1").kind).toBe("capability");
    expect(resolveRoadmapRoute(value, "/cap/../secret").kind).toBe("not-found");
    expect(resolveRoadmapRoute(value, "/work/MISSING").kind).toBe("not-found");
  });
});

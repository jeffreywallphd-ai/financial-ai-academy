import { initializeTheme, loadRoadmap, mountRoadmap, mountRoadmapRoute } from "../src/app.js";
import type { RoadmapEnvelope, RoadmapReview } from "../src/model.js";

function clickByText(root: ParentNode, label: string): void {
  const button = Array.from(root.querySelectorAll("button")).find((item) => item.textContent === label);
  if (!(button instanceof HTMLButtonElement)) throw new Error(`Missing button: ${label}`);
  button.click();
}

function fixture(): RoadmapReview {
  const candidates = Array.from({ length: 26 }, (_, index) => ({
    key: `capability-${index + 1}`,
    order: index + 1,
    title: index === 0 ? "Structured lessons" : `Capability ${index + 1}`,
    description: `Description ${index + 1}`,
    planning_id: index === 0 ? "CAP-X" : null,
    planned: index === 0,
    capability: index === 0 ? {
      id: "CAP-X", kind: "capability", status: "ready", title: "Plan X", source: "plan.md", dependencies: [], manifest: ["SLICE-X"], decision_gates: ["DECISION-A", "DECISION-MISSING"],
      document: { source: "plan.md", blocks: [{ type: "heading", level: 1, text: "Capability plan" }, { type: "paragraph", text: "Current capability detail." }] },
    } : null,
    slices: index === 0 ? [{
      id: "SLICE-X", refined: true, kind: "slice", status: "active", title: "Slice X", source: "slice.md", dependencies: [], manifest: [], decision_gates: ["DECISION-B"],
      document: { source: "slice.md", blocks: [{ type: "list-item", text: "Safe list item" }, { type: "table-row", cells: ["Header", "Value"] }, { type: "table-row", cells: ["State", "Active"] }] },
      work: [{
        id: "WORK-X", kind: "work", status: "complete", title: "Work X", source: "work.md", dependencies: [], manifest: [], decision_gates: ["DECISION-A"],
        document: { source: "work.md", blocks: [{ type: "code", text: "<script>window.attacked = true</script>" }] },
      }],
    }] : [],
  }));
  return {
    schema_version: "roadmap-review-v1",
    catalog_count: 26,
    candidates,
    internal_capabilities: [{
      id: "CONTROL-X", kind: "capability", status: "complete", title: "Control plane", source: "control.md", dependencies: [], manifest: ["CONTROL-SLICE"],
      slices: [{ id: "CONTROL-SLICE", refined: false, work: [] }],
      document: { source: "control.md", blocks: [{ type: "paragraph", text: "Internal capability detail." }] },
    }],
    decisions: [
      { id: "DECISION-A", kind: "decision-request", status: "complete", title: "Choose A", source: "decisions/a.md", dependencies: [], decision_record: "records/a.md", decision_made: true, document: { source: "decisions/a.md", blocks: [{ type: "paragraph", text: "<script>window.attacked = true</script>" }] } },
      { id: "DECISION-B", kind: "decision-request", status: "captured", title: "Choose B", source: "decisions/b.md", dependencies: [{ target: "DECISION-A", type: "hard" }], decision_record: null, decision_made: false, document: { source: "decisions/b.md", blocks: [{ type: "paragraph", text: "Decision B detail." }] } },
    ],
    ordering: {
      ready: [{ id: "CAP-X", reasons: ["ready"] }],
      blocked: [{ id: "CAP-FUTURE", reasons: ["dependencies.incomplete"], incomplete_dependencies: ["CAP-X"], remediation: "Complete CAP-X." }], completed: ["CONTROL-X"], in_progress: [], proposed_order: ["CAP-X", "CONTROL-X", "CAP-FUTURE"],
      unresolved_ties: [["CAP-X", "CONTROL-X"]], constraints: { accepted_sequence: [], stable_id_order_is_authority: false },
    },
    compatibility: {
      pairs: [{ left: "CAP-X", right: "CONTROL-X", decision: "compatible", confidence: "high", reasons: [{ code: "scope.disjoint", evidence: ["CAP-X", "CONTROL-X"] }], remediation: "None." }],
      parallel_safe_sets: [["CAP-X", "CONTROL-X"]], isolated_or_unresolved: [], compatible_pair_count: 1, incompatible_pair_count: 0, unknown_pair_count: 0,
    },
    current_allocation: {
      schema_version: "roadmap-current-allocation-v1",
      source_schema_version: "portfolio-allocation-v1",
      level: "capability",
      lanes: [
        { unit_id: "CONTROL-X", allocation_state: "in-progress", lifecycle_status: "complete" },
        { unit_id: "CAP-X", allocation_state: "proposed", lifecycle_status: "ready" },
      ],
      parallel_groups: [["CONTROL-X", "CAP-X"]],
      unresolved_pairs: [],
      constraints: { grants_authority: false, acquires_file_leases: false, creates_agents: false, mutates_branches: false, future_order_is_global_lock: false },
    },
    graph_issues: [], diagnostics: [], source_fingerprint: "sha256:fixture",
  };
}

describe("roadmap overview DOM", () => {
  beforeEach(() => {
    document.body.replaceChildren();
  });

  it("renders all 26 candidates, authority language, order, and unknown evidence", () => {
    const root = document.createElement("main");
    document.body.append(root);
    mountRoadmap(root, fixture());
    expect(root.querySelector(".results-status")?.textContent).toBe("Showing 26 of 26 product capabilities.");
    expect(Array.from(root.querySelectorAll("a")).filter((link) => link.getAttribute("href")?.startsWith("/capability/"))).toHaveLength(27);
    expect(root.textContent).toContain("make future ordering a global lock");
    expect(root.textContent).toContain("CONTROL-X + CAP-X");
    expect(root.textContent).toContain("do not replace any of the 26");
    const orderLinks = Array.from(root.querySelectorAll(".order-list .order-link")).map((link) => link.textContent);
    expect(orderLinks).toEqual(["CONTROL-X: Control plane", "CAP-X: Structured lessons"]);
    const firstOrderItem = root.querySelector(".order-list .order-item");
    expect(firstOrderItem?.textContent).toContain("in progress");
    expect(firstOrderItem?.textContent).toContain("Planning status: complete");
    expect(firstOrderItem?.querySelector('[aria-label="Current work state: in progress"]')).toBeTruthy();
    expect(root.querySelector(".order-list")?.textContent).not.toContain("CAP-FUTURE");
    expect(root.textContent).toContain("CAP-FUTURE");
    expect(root.querySelectorAll(".order-list .card-meta")).toHaveLength(2);
  });

  it("distinguishes sequential current lanes without treating unknown pairs as safe", () => {
    const root = document.createElement("main");
    document.body.append(root);
    const value = fixture();
    value.current_allocation.parallel_groups = [["CONTROL-X"], ["CAP-X"]];
    value.compatibility.pairs[0] = { left: "CAP-X", right: "CONTROL-X", decision: "unknown", confidence: "low", reasons: [{ code: "evidence.scope-incomplete", evidence: ["CAP-X"] }], remediation: "Refine." };
    value.compatibility.parallel_safe_sets = [];
    mountRoadmap(root, value);
    expect(root.textContent).toContain("Sequential current lanes");
    expect(root.textContent).toContain("No evidence-backed parallel CAP lane is currently available");
    expect(root.querySelector(".order-list")?.textContent).toContain("Sequential lane 1");
    expect(root.querySelector(".order-list")?.textContent).toContain("Sequential lane 2");
  });

  it("filters accessibly and restores the complete catalog", () => {
    const root = document.createElement("main");
    document.body.append(root);
    mountRoadmap(root, fixture());
    const search = root.querySelector<HTMLInputElement>('input[name="query"]')!;
    search.value = "Structured";
    search.dispatchEvent(new Event("input", { bubbles: true }));
    expect(root.querySelector(".results-status")?.textContent).toBe("Showing 1 of 26 product capabilities.");
    clickByText(root, "Clear filters");
    return new Promise<void>((resolve) => window.setTimeout(() => {
      expect(root.querySelector(".results-status")?.textContent).toBe("Showing 26 of 26 product capabilities.");
      resolve();
    }));
  });

  it("shows a bounded retry state when refresh fails", async () => {
    const root = document.createElement("main");
    document.body.append(root);
    const fetcher = async () => new Response("failure", { status: 503 });
    await loadRoadmap(root, fetcher as typeof fetch);
    expect(root.querySelector('[role="alert"]')).toBeTruthy();
    expect(Array.from(root.querySelectorAll("button")).some((button) => button.textContent === "Try again")).toBe(true);
  });

  it("loads a compatible envelope and supports equivalent theme choices", async () => {
    document.body.innerHTML = '<select id="theme-select"><option value="system">System</option><option value="light">Light</option><option value="dark">Dark</option></select><main id="test-root"></main>';
    const root = document.querySelector<HTMLElement>("#test-root")!;
    const envelope: RoadmapEnvelope = { outcome: "succeeded", code: "ok", message: "ok", data: { review: fixture() } };
    await loadRoadmap(root, (async () => new Response(JSON.stringify(envelope), { status: 200, headers: { "Content-Type": "application/json" } })) as typeof fetch);
    expect(root.querySelector(".results-status")?.textContent).toBe("Showing 26 of 26 product capabilities.");
    const memory = new Map<string, string>();
    initializeTheme({ getItem: (key) => memory.get(key) ?? null, setItem: (key, value) => { memory.set(key, value); } });
    const theme = document.querySelector<HTMLSelectElement>("#theme-select")!;
    theme.value = "dark";
    theme.dispatchEvent(new Event("change", { bubbles: true }));
    expect(document.documentElement.dataset.theme).toBe("dark");
    expect(memory.get("roadmap-review-theme")).toBe("dark");
  });

  it("navigates candidate, slice, and work details with inert plan content", () => {
    const root = document.createElement("main");
    document.body.append(root);
    const value = fixture();
    mountRoadmapRoute(root, value, "/capability/capability-1");
    expect(root.querySelector("h1")?.textContent).toBe("Structured lessons");
    expect(root.querySelector('a[href="/slice/SLICE-X"]')).toBeTruthy();
    expect(root.querySelector('a[href="/decision/DECISION-A"]')).toBeTruthy();
    expect(root.querySelector('[aria-label="Decision status: complete"]')).toBeTruthy();
    expect(root.textContent).toContain("DECISION-MISSING: decision request not found");
    expect(root.textContent).toContain("Current capability detail.");

    mountRoadmapRoute(root, value, "/slice/SLICE-X");
    expect(root.querySelector('a[href="/work/WORK-X"]')).toBeTruthy();
    expect(root.querySelector('a[href="/decision/DECISION-A"]')).toBeTruthy();
    expect(root.querySelector('a[href="/decision/DECISION-B"]')).toBeTruthy();
    expect(root.textContent).toContain("Safe list item");
    expect(root.querySelector("table")).toBeTruthy();

    mountRoadmapRoute(root, value, "/work/WORK-X");
    expect(root.textContent).toContain("<script>window.attacked = true</script>");
    expect(root.querySelector("script")).toBeNull();
  });

  it("shows dynamic decision details for recorded and deferred outcomes", () => {
    const root = document.createElement("main");
    document.body.append(root);
    const value = fixture();
    mountRoadmapRoute(root, value, "/decision/DECISION-A");
    expect(root.querySelector("h1")?.textContent).toBe("DECISION-A: Choose A");
    expect(root.textContent).toContain("Decision recordedYes");
    expect(root.textContent).toContain("A decision outcome is recorded");
    expect(root.textContent).toContain("does not display private approval or reviewer records");
    expect(root.textContent).toContain("<script>window.attacked = true</script>");
    expect(root.querySelector("script")).toBeNull();

    mountRoadmapRoute(root, value, "/decision/DECISION-B");
    expect(root.textContent).toContain("Decision recordedNo");
    expect(root.textContent).toContain("No decision outcome is recorded yet");
    expect(root.textContent).toContain("No separate canonical record linked");
  });

  it("keeps unplanned and unrefined entries useful and bounds unknown routes", () => {
    const root = document.createElement("main");
    document.body.append(root);
    const value = fixture();
    mountRoadmapRoute(root, value, "/capability/capability-2");
    expect(root.textContent).toContain("No governed CAP package");

    mountRoadmapRoute(root, value, "/slice/CONTROL-SLICE");
    expect(root.textContent).toContain("has not been refined");
    expect(root.textContent).toContain("does not block review of other work");

    mountRoadmapRoute(root, value, "/work/UNKNOWN");
    expect(root.querySelector('[role="alert"]')).toBeTruthy();
    expect(root.querySelector('a[href="/"]')?.textContent).toBe("Return to all capabilities");
  });
});

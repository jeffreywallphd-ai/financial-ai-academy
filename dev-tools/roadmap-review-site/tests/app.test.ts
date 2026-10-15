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
      id: "CAP-X", kind: "capability", status: "ready", title: "Plan X", source: "plan.md", dependencies: [], manifest: ["SLICE-X"],
      document: { source: "plan.md", blocks: [{ type: "heading", level: 1, text: "Capability plan" }, { type: "paragraph", text: "Current capability detail." }] },
    } : null,
    slices: index === 0 ? [{
      id: "SLICE-X", refined: true, kind: "slice", status: "active", title: "Slice X", source: "slice.md", dependencies: [], manifest: [],
      document: { source: "slice.md", blocks: [{ type: "list-item", text: "Safe list item" }, { type: "table-row", cells: ["Header", "Value"] }, { type: "table-row", cells: ["State", "Active"] }] },
      work: [{
        id: "WORK-X", kind: "work", status: "complete", title: "Work X", source: "work.md", dependencies: [], manifest: [],
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
    ordering: {
      ready: [{ id: "CAP-X", reasons: ["ready"] }],
      blocked: [], completed: ["CONTROL-X"], in_progress: [], proposed_order: ["CAP-X", "CONTROL-X"],
      unresolved_ties: [["CAP-X", "CONTROL-X"]], constraints: { accepted_sequence: [], stable_id_order_is_authority: false },
    },
    compatibility: {
      pairs: [{ left: "CAP-X", right: "CONTROL-X", decision: "unknown", confidence: "low", reasons: [{ code: "evidence.scope-incomplete", evidence: ["CAP-X"] }], remediation: "Refine." }],
      parallel_safe_sets: [], isolated_or_unresolved: ["CAP-X", "CONTROL-X"], compatible_pair_count: 0, incompatible_pair_count: 0, unknown_pair_count: 1,
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
    expect(root.textContent).toContain("dependency-aware proposal, not accepted priority");
    expect(root.textContent).toContain("Unknown evidence is not treated as safe");
    expect(root.textContent).toContain("do not replace any of the 26");
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
    expect(root.textContent).toContain("Current capability detail.");

    mountRoadmapRoute(root, value, "/slice/SLICE-X");
    expect(root.querySelector('a[href="/work/WORK-X"]')).toBeTruthy();
    expect(root.textContent).toContain("Safe list item");
    expect(root.querySelector("table")).toBeTruthy();

    mountRoadmapRoute(root, value, "/work/WORK-X");
    expect(root.textContent).toContain("<script>window.attacked = true</script>");
    expect(root.querySelector("script")).toBeNull();
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

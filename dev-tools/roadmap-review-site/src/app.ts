import {
  assertRoadmapEnvelope,
  compatibilityCounts,
  filterCandidates,
  roadmapCounts,
  resolveRoadmapRoute,
  statusFor,
  titleFor,
  type CandidateFilters,
  type PlanningNode,
  type RoadmapCandidate,
  type RoadmapCapability,
  type RoadmapDocument,
  type RoadmapReview,
  type RoadmapSlice,
} from "./model.js";

type Theme = "system" | "light" | "dark";

function element<K extends keyof HTMLElementTagNameMap>(
  tag: K,
  className = "",
  text = "",
): HTMLElementTagNameMap[K] {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text) node.textContent = text;
  return node;
}

function labelledSection(title: string, id: string): [HTMLElement, HTMLElement] {
  const section = element("section", "panel");
  section.setAttribute("aria-labelledby", id);
  const heading = element("h2", "section-heading", title);
  heading.id = id;
  section.append(heading);
  return [section, heading];
}

function statusBadge(status: string, label = "Planning state"): HTMLElement {
  const badge = element("span", `status status--${status}`, status.replaceAll("-", " "));
  badge.setAttribute("aria-label", `${label}: ${status.replaceAll("-", " ")}`);
  return badge;
}

function candidateCard(candidate: RoadmapCandidate): HTMLLIElement {
  const item = element("li", "capability-card");
  const top = element("div", "capability-card__top");
  top.append(element("span", "sequence", String(candidate.order).padStart(2, "0")));
  top.append(statusBadge(candidate.capability?.status ?? "unplanned"));
  const title = element("h3", "card-title");
  const link = element("a", "card-link", candidate.title);
  link.href = `/capability/${encodeURIComponent(candidate.key)}`;
  title.append(link);
  const description = element("p", "card-description", candidate.description);
  const metadata = element("p", "card-meta");
  metadata.textContent = candidate.planned
    ? `${candidate.planning_id} · ${candidate.slices.length} declared slice${candidate.slices.length === 1 ? "" : "s"}`
    : "No formal CAP package yet";
  item.append(top, title, description, metadata);
  return item;
}

function renderOrder(review: RoadmapReview): HTMLElement {
  const [section] = labelledSection("Proposed capability order", "order-heading");
  const note = element(
    "p",
    "authority-note",
    "These current lanes mirror the default control-plane allocation proposal. They do not accept priority, grant authority, acquire a lease, or make future ordering a global lock.",
  );
  section.append(note);
  const list = element("ol", "order-list");
  const groupById = new Map<string, { group: string[]; position: number }>();
  review.current_allocation.parallel_groups.forEach((group, index) => {
    group.forEach((id) => groupById.set(id, { group, position: index + 1 }));
  });
  for (const lane of review.current_allocation.lanes) {
    const id = lane.unit_id;
    const item = element("li", "order-item");
    const link = element("a", "order-link", `${id}: ${titleFor(review, id)}`);
    const candidate = review.candidates.find((entry) => entry.planning_id === id);
    link.href = candidate ? `/capability/${encodeURIComponent(candidate.key)}` : `/cap/${encodeURIComponent(id)}`;
    const group = groupById.get(id);
    const laneLabel = group && group.group.length > 1
      ? `Parallel-safe group ${group.position}`
      : `Sequential lane ${group?.position ?? review.current_allocation.lanes.indexOf(lane) + 1}`;
    const lifecycle = lane.lifecycle_status || statusFor(review, id);
    item.append(
      link,
      statusBadge(lane.allocation_state, "Current work state"),
      element("span", "card-meta", `${laneLabel} · Planning status: ${lifecycle}`),
    );
    list.append(item);
  }
  if (review.current_allocation.lanes.length) {
    section.append(list);
  } else {
    section.append(element("p", "empty-state", "No capability is currently active or dependency-ready. Future ordering remains advisory."));
  }
  if (review.ordering.unresolved_ties.length) {
    const heading = element("h3", "subheading", "Unresolved ties");
    const ties = element("ul", "plain-list");
    for (const group of review.ordering.unresolved_ties) {
      ties.append(element("li", "", `${group.join(", ")} — no relative product priority has been accepted.`));
    }
    section.append(heading, ties);
  }
  return section;
}

function renderBlockers(review: RoadmapReview): HTMLElement {
  const [section] = labelledSection("Current blockers", "blockers-heading");
  if (!review.ordering.blocked.length) {
    section.append(element("p", "empty-state", "No capability is currently dependency-blocked."));
    return section;
  }
  const wrapper = element("div", "table-scroll");
  const table = element("table", "data-table");
  const caption = element("caption", "visually-hidden", "Capabilities blocked by incomplete dependencies");
  const head = element("thead");
  const headRow = element("tr");
  for (const label of ["Capability", "Incomplete dependencies", "Next condition"]) {
    headRow.append(element("th", "", label));
  }
  head.append(headRow);
  const body = element("tbody");
  for (const blocker of review.ordering.blocked) {
    const row = element("tr");
    row.append(
      element("th", "", blocker.id),
      element("td", "", blocker.incomplete_dependencies.join(", ") || "Not specified"),
      element("td", "", blocker.remediation),
    );
    body.append(row);
  }
  table.append(caption, head, body);
  wrapper.append(table);
  section.append(wrapper);
  return section;
}

function renderParallelism(review: RoadmapReview): HTMLElement {
  const [section] = labelledSection("Parallel work evidence", "parallel-heading");
  const counts = compatibilityCounts(review);
  const summary = element("div", "metric-grid");
  for (const [label, value] of [
    ["Compatible pairs", counts.compatible],
    ["Incompatible pairs", counts.incompatible],
    ["Unknown pairs", counts.unknown],
  ] as const) {
    const metric = element("div", "metric");
    metric.append(element("strong", "metric__value", String(value)), element("span", "metric__label", label));
    summary.append(metric);
  }
  section.append(summary);
  const parallelGroups = review.current_allocation.parallel_groups.filter((group) => group.length > 1);
  const sequentialGroups = review.current_allocation.parallel_groups.filter((group) => group.length === 1);
  if (parallelGroups.length) {
    const lanes = element("ul", "lane-list");
    for (const lane of parallelGroups) {
      lanes.append(element("li", "lane", lane.join(" + ")));
    }
    section.append(element("h3", "subheading", "Evidence-backed parallel lanes"), lanes);
  } else {
    section.append(
      element(
        "p",
        "empty-state",
        "No evidence-backed parallel CAP lane is currently available. Unknown evidence is not treated as safe.",
      ),
    );
  }
  if (sequentialGroups.length) {
    const lanes = element("ul", "lane-list");
    for (const lane of sequentialGroups) {
      lanes.append(element("li", "lane", lane[0] ?? ""));
    }
    section.append(element("h3", "subheading", "Sequential current lanes"), lanes);
  }
  const details = element("details", "evidence-details");
  details.append(element("summary", "", "Review incompatible and unknown pairs"));
  const pairList = element("ul", "plain-list");
  for (const pair of review.compatibility.pairs.filter((item) => item.decision !== "compatible")) {
    const codes = pair.reasons.map((reason) => reason.code).join(", ");
    pairList.append(element("li", "", `${pair.left} + ${pair.right}: ${pair.decision} (${codes}).`));
  }
  details.append(pairList);
  section.append(details);
  return section;
}

function renderInternalCapabilities(review: RoadmapReview): HTMLElement {
  const [section] = labelledSection("Internal enabling capabilities", "internal-heading");
  section.append(
    element(
      "p",
      "section-intro",
      "These governed CAPs enable delivery but do not replace any of the 26 product capability candidates.",
    ),
  );
  const list = element("ul", "compact-card-list");
  for (const capability of review.internal_capabilities) {
    const item = element("li", "compact-card");
    const link = element("a", "card-link", `${capability.id}: ${capability.title}`);
    link.href = `/cap/${encodeURIComponent(capability.id)}`;
    item.append(link, statusBadge(capability.status));
    list.append(item);
  }
  section.append(list);
  return section;
}

function breadcrumbs(items: Array<{ label: string; href?: string }>): HTMLElement {
  const navigation = element("nav", "breadcrumbs");
  navigation.setAttribute("aria-label", "Breadcrumb");
  const list = element("ol");
  for (const item of items) {
    const listItem = element("li");
    if (item.href) {
      const link = element("a", "", item.label);
      link.href = item.href;
      listItem.append(link);
    } else {
      listItem.textContent = item.label;
      listItem.setAttribute("aria-current", "page");
    }
    list.append(listItem);
  }
  navigation.append(list);
  return navigation;
}

function planDocument(documentValue: RoadmapDocument | null | undefined): HTMLElement {
  const [section] = labelledSection("Plan details", "plan-details-heading");
  if (!documentValue || !documentValue.blocks.length) {
    section.append(element("p", "empty-state", "No public plan details are available for this artifact."));
    return section;
  }
  const content = element("div", "plan-document");
  let index = 0;
  while (index < documentValue.blocks.length) {
    const block = documentValue.blocks[index];
    if (!block) break;
    if (block.type === "heading") {
      const level = Math.min(6, Math.max(2, block.level + 1));
      const heading = document.createElement(`h${level}`);
      heading.textContent = block.text;
      content.append(heading);
      index += 1;
      continue;
    }
    if (block.type === "paragraph") {
      content.append(element("p", "", block.text));
      index += 1;
      continue;
    }
    if (block.type === "code") {
      const pre = element("pre");
      pre.append(element("code", "", block.text));
      content.append(pre);
      index += 1;
      continue;
    }
    if (block.type === "list-item") {
      const list = element("ul");
      while (documentValue.blocks[index]?.type === "list-item") {
        const item = documentValue.blocks[index];
        if (item?.type === "list-item") list.append(element("li", "", item.text));
        index += 1;
      }
      content.append(list);
      continue;
    }
    const table = element("table", "data-table plan-table");
    table.append(element("caption", "visually-hidden", "Plan table"));
    const head = element("thead");
    const body = element("tbody");
    let rowIndex = 0;
    while (documentValue.blocks[index]?.type === "table-row") {
      const rowBlock = documentValue.blocks[index];
      const row = element("tr");
      if (rowBlock?.type === "table-row") {
        for (const cell of rowBlock.cells) row.append(element(rowIndex === 0 ? "th" : "td", "", cell));
      }
      (rowIndex === 0 ? head : body).append(row);
      rowIndex += 1;
      index += 1;
    }
    table.append(head, body);
    const scroll = element("div", "table-scroll");
    scroll.append(table);
    content.append(scroll);
  }
  const source = element("p", "document-source");
  source.append("Projected from ", element("code", "", documentValue.source));
  section.append(content, source);
  return section;
}

function artifactFacts(node: PlanningNode): HTMLElement {
  const facts = element("dl", "fact-grid");
  const rows: Array<[string, string]> = [
    ["Planning ID", node.id],
    ["Lifecycle", node.status],
    ["Dependencies", node.dependencies.map((item) => `${item.target} (${item.type})`).join(", ") || "None declared"],
    ["Decision gates", node.decision_gates?.join(", ") || "None declared"],
    ["Source", node.source],
  ];
  for (const [term, description] of rows) {
    facts.append(element("dt", "", term), element("dd", "", description));
  }
  return facts;
}

function sliceList(capability: RoadmapCapability): HTMLElement {
  const [section] = labelledSection("Declared slices", "declared-slices-heading");
  if (!capability.slices.length) {
    section.append(element("p", "empty-state", "This capability declares no slices."));
    return section;
  }
  const list = element("ol", "detail-list");
  for (const slice of capability.slices) {
    const item = element("li", "detail-list__item");
    const title = slice.refined && slice.title ? `${slice.id}: ${slice.title}` : `${slice.id}: detailed plan not refined yet`;
    const link = element("a", "card-link", title);
    link.href = `/slice/${encodeURIComponent(slice.id)}`;
    item.append(link, statusBadge(slice.refined ? slice.status ?? "unknown" : "captured"));
    list.append(item);
  }
  section.append(list);
  return section;
}

function detailActions(root: HTMLElement, review: RoadmapReview): HTMLElement {
  const actions = element("section", "review-actions");
  actions.setAttribute("aria-label", "Detail refresh and source status");
  const refresh = element("button", "primary-button", "Refresh current sources");
  refresh.type = "button";
  refresh.addEventListener("click", () => void loadRoadmap(root));
  const fingerprint = element("p", "source-fingerprint");
  fingerprint.append("Source fingerprint ", element("code", "", review.source_fingerprint));
  actions.append(refresh, fingerprint);
  return actions;
}

function capabilityPage(
  root: HTMLElement,
  review: RoadmapReview,
  capability: RoadmapCapability,
  candidate: RoadmapCandidate | null,
): void {
  const headingText = candidate?.title ?? capability.title;
  const heading = element("h1", "page-heading", headingText);
  const header = element("header", "detail-header");
  header.append(element("p", "eyebrow", candidate ? "Product capability plan" : "Internal enabling capability"), heading);
  if (candidate) header.append(element("p", "hero-copy", candidate.description));
  header.append(statusBadge(capability.status), artifactFacts(capability));
  root.append(
    breadcrumbs([{ label: "All capabilities", href: "/" }, { label: headingText }]),
    header,
    detailActions(root, review),
    sliceList(capability),
    planDocument(capability.document),
  );
}

function candidatePage(root: HTMLElement, review: RoadmapReview, candidate: RoadmapCandidate): void {
  if (candidate.capability) {
    capabilityPage(root, review, { ...candidate.capability, slices: candidate.slices }, candidate);
    return;
  }
  const header = element("header", "detail-header");
  header.append(
    element("p", "eyebrow", "Product capability candidate"),
    element("h1", "page-heading", candidate.title),
    element("p", "hero-copy", candidate.description),
    statusBadge("unplanned"),
    element(
      "p",
      "empty-state",
      "No governed CAP package, dependencies, slice manifest, implementation order, or parallel-safety evidence has been established for this candidate.",
    ),
  );
  root.append(
    breadcrumbs([{ label: "All capabilities", href: "/" }, { label: candidate.title }]),
    header,
    detailActions(root, review),
  );
}

function slicePage(
  root: HTMLElement,
  review: RoadmapReview,
  slice: RoadmapSlice,
  capability: RoadmapCapability,
  candidate: RoadmapCandidate | null,
): void {
  const parentLabel = candidate?.title ?? capability.title;
  const parentHref = candidate ? `/capability/${encodeURIComponent(candidate.key)}` : `/cap/${encodeURIComponent(capability.id)}`;
  const header = element("header", "detail-header");
  header.append(
    element("p", "eyebrow", "Vertical slice"),
    element("h1", "page-heading", slice.refined && slice.title ? `${slice.id}: ${slice.title}` : slice.id),
    statusBadge(slice.refined ? slice.status ?? "unknown" : "captured"),
  );
  root.append(
    breadcrumbs([{ label: "All capabilities", href: "/" }, { label: parentLabel, href: parentHref }, { label: slice.id }]),
    header,
    detailActions(root, review),
  );
  if (!slice.refined) {
    root.append(element("p", "empty-state", "This declared slice has not been refined into a detailed SLI artifact yet. It remains navigable and does not block review of other work."));
    return;
  }
  if (slice.source && slice.dependencies && slice.manifest) root.append(artifactFacts(slice as PlanningNode));
  const [workSection] = labelledSection("Associated work", "associated-work-heading");
  if (!slice.work.length) {
    workSection.append(element("p", "empty-state", "No work packets are currently associated with this slice."));
  } else {
    const workList = element("ul", "detail-list");
    for (const work of slice.work) {
      const item = element("li", "detail-list__item");
      const link = element("a", "card-link", `${work.id}: ${work.title}`);
      link.href = `/work/${encodeURIComponent(work.id)}`;
      item.append(link, statusBadge(work.status));
      workList.append(item);
    }
    workSection.append(workList);
  }
  root.append(workSection, planDocument(slice.document));
}

function workPage(
  root: HTMLElement,
  review: RoadmapReview,
  work: PlanningNode,
  slice: RoadmapSlice,
  capability: RoadmapCapability,
  candidate: RoadmapCandidate | null,
): void {
  const parentLabel = candidate?.title ?? capability.title;
  const parentHref = candidate ? `/capability/${encodeURIComponent(candidate.key)}` : `/cap/${encodeURIComponent(capability.id)}`;
  const header = element("header", "detail-header");
  header.append(element("p", "eyebrow", "Agent work packet"), element("h1", "page-heading", `${work.id}: ${work.title}`), statusBadge(work.status));
  root.append(
    breadcrumbs([
      { label: "All capabilities", href: "/" },
      { label: parentLabel, href: parentHref },
      { label: slice.id, href: `/slice/${encodeURIComponent(slice.id)}` },
      { label: work.id },
    ]),
    header,
    detailActions(root, review),
    artifactFacts(work),
    planDocument(work.document),
  );
}

export function mountRoadmapRoute(root: HTMLElement, review: RoadmapReview, pathname: string): void {
  const route = resolveRoadmapRoute(review, pathname);
  if (route.kind === "overview") {
    mountRoadmap(root, review);
    return;
  }
  root.replaceChildren();
  root.removeAttribute("aria-busy");
  if (route.kind === "candidate") candidatePage(root, review, route.candidate);
  else if (route.kind === "capability") capabilityPage(root, review, route.capability, route.candidate);
  else if (route.kind === "slice") slicePage(root, review, route.slice, route.capability, route.candidate);
  else if (route.kind === "work") workPage(root, review, route.work, route.slice, route.capability, route.candidate);
  else {
    const panel = element("section", "error-panel");
    panel.setAttribute("role", "alert");
    panel.append(
      element("h1", "page-heading", "Roadmap entry not found"),
      element("p", "", `No projected roadmap entry matches ${route.requestedPath}.`),
    );
    const link = element("a", "primary-link", "Return to all capabilities");
    link.href = "/";
    panel.append(link);
    root.append(panel);
  }
}

export function mountRoadmap(root: HTMLElement, review: RoadmapReview): void {
  root.replaceChildren();
  root.removeAttribute("aria-busy");

  const header = element("section", "hero");
  header.setAttribute("aria-labelledby", "page-heading");
  header.append(
    element("p", "eyebrow", "Dynamic planning review"),
    Object.assign(element("h1", "page-heading", "All product capabilities, one current view"), { id: "page-heading" }),
    element(
      "p",
      "hero-copy",
      "Browse the structured capability catalog and current governed planning projection. Placement is explanatory; source plans remain authoritative.",
    ),
  );
  const counts = roadmapCounts(review);
  const countGrid = element("div", "count-grid");
  for (const [value, label] of [
    [counts.total, "catalog candidates"],
    [counts.planned, "with formal CAPs"],
    [counts.unplanned, "not yet planned"],
  ] as const) {
    const card = element("div", "count-card");
    card.append(element("strong", "count-card__value", String(value)), element("span", "count-card__label", label));
    countGrid.append(card);
  }
  header.append(countGrid);

  const [catalog] = labelledSection("Product capability catalog", "catalog-heading");
  catalog.classList.add("catalog-panel");
  const controls = element("form", "filters");
  controls.setAttribute("role", "search");
  controls.addEventListener("submit", (event) => event.preventDefault());
  const searchLabel = element("label", "field");
  searchLabel.append(element("span", "", "Search"));
  const search = element("input");
  search.type = "search";
  search.name = "query";
  search.placeholder = "Title, description, key, or CAP ID";
  searchLabel.append(search);
  const planningLabel = element("label", "field");
  planningLabel.append(element("span", "", "Planning coverage"));
  const planning = element("select");
  planning.name = "planning";
  for (const [value, label] of [["all", "All"], ["planned", "Formal CAP"], ["unplanned", "Not yet planned"]] as const) {
    const option = element("option", "", label);
    option.value = value;
    planning.append(option);
  }
  planningLabel.append(planning);
  const statusLabel = element("label", "field");
  statusLabel.append(element("span", "", "Lifecycle state"));
  const status = element("select");
  status.name = "status";
  const statuses = ["all", ...Object.keys(counts.byStatus).sort()];
  for (const value of statuses) {
    const option = element("option", "", value === "all" ? "All states" : value.replaceAll("-", " "));
    option.value = value;
    status.append(option);
  }
  statusLabel.append(status);
  const reset = element("button", "secondary-button", "Clear filters");
  reset.type = "reset";
  controls.append(searchLabel, planningLabel, statusLabel, reset);
  const resultStatus = element("p", "results-status");
  resultStatus.setAttribute("role", "status");
  resultStatus.setAttribute("aria-live", "polite");
  const list = element("ul", "capability-grid");
  const filters: CandidateFilters = { query: "", planning: "all", status: "all" };
  const renderCandidates = (): void => {
    list.replaceChildren();
    const visible = filterCandidates(review.candidates, filters);
    resultStatus.textContent = `Showing ${visible.length} of ${review.catalog_count} product capabilities.`;
    for (const candidate of visible) list.append(candidateCard(candidate));
    if (!visible.length) list.append(element("li", "empty-state", "No capabilities match these filters."));
  };
  search.addEventListener("input", () => { filters.query = search.value; renderCandidates(); });
  planning.addEventListener("change", () => {
    filters.planning = planning.value as CandidateFilters["planning"];
    renderCandidates();
  });
  status.addEventListener("change", () => { filters.status = status.value; renderCandidates(); });
  controls.addEventListener("reset", () => {
    window.setTimeout(() => {
      filters.query = "";
      filters.planning = "all";
      filters.status = "all";
      renderCandidates();
    });
  });
  renderCandidates();
  catalog.append(controls, resultStatus, list);

  const operations = element("section", "review-actions");
  operations.setAttribute("aria-label", "Roadmap refresh and source status");
  const refresh = element("button", "primary-button", "Refresh current sources");
  refresh.type = "button";
  refresh.addEventListener("click", () => void loadRoadmap(root));
  const source = element("p", "source-fingerprint");
  source.append("Source fingerprint ", element("code", "", review.source_fingerprint));
  operations.append(refresh, source);

  const evidenceLayout = element("div", "two-column");
  evidenceLayout.append(renderOrder(review), renderBlockers(review));
  root.append(header, operations, catalog, evidenceLayout, renderParallelism(review), renderInternalCapabilities(review));
}

export function showRoadmapError(root: HTMLElement, message: string): void {
  root.replaceChildren();
  root.removeAttribute("aria-busy");
  const panel = element("section", "error-panel");
  panel.setAttribute("role", "alert");
  panel.append(
    element("h1", "page-heading", "Roadmap unavailable"),
    element("p", "", message),
  );
  const retry = element("button", "primary-button", "Try again");
  retry.type = "button";
  retry.addEventListener("click", () => void loadRoadmap(root));
  panel.append(retry);
  root.append(panel);
}

export async function loadRoadmap(
  root: HTMLElement,
  fetcher: typeof fetch = fetch,
  pathname: string = window.location.pathname,
): Promise<void> {
  root.setAttribute("aria-busy", "true");
  try {
    const response = await fetcher("/api/roadmap", { headers: { Accept: "application/json" }, cache: "no-store" });
    if (!response.ok) throw new Error(`The local review service returned ${response.status}.`);
    const envelope = assertRoadmapEnvelope(await response.json());
    mountRoadmapRoute(root, envelope.data.review, pathname);
  } catch (error) {
    showRoadmapError(root, error instanceof Error ? error.message : "The current roadmap could not be loaded.");
  }
}

export function initializeTheme(storage: Pick<Storage, "getItem" | "setItem"> = localStorage): void {
  const select = document.querySelector<HTMLSelectElement>("#theme-select");
  if (!select) return;
  const saved = storage.getItem("roadmap-review-theme");
  const theme: Theme = saved === "light" || saved === "dark" || saved === "system" ? saved : "system";
  document.documentElement.dataset.theme = theme;
  select.value = theme;
  select.addEventListener("change", () => {
    const next = select.value as Theme;
    document.documentElement.dataset.theme = next;
    storage.setItem("roadmap-review-theme", next);
  });
}

const root = document.querySelector<HTMLElement>("#roadmap");
if (root) {
  initializeTheme();
  void loadRoadmap(root);
}

import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";
import type { Page, Route } from "@playwright/test";
import { createHash } from "node:crypto";

const origin = {
  origin_type: "learning",
  project_brief_schema_version: "1.0.0",
  package_id: "intro-risk-return-project",
  package_version: "1.0.0",
  package_digest: "a".repeat(64),
  brief_id: "risk-return-project",
  brief_version: "1.0.0",
  brief_digest: "b".repeat(64),
  curriculum_id: "financial-foundations",
  curriculum_version: "1.0.0",
  curriculum_digest: "c".repeat(64),
  placement_id: "risk-return-project-primary",
  placement_version: "1.0.0",
  placement_digest: "d".repeat(64),
  brief_title: "Compare investment choices",
  brief_purpose: "Practice a structured educational comparison.",
};
const option = { title: origin.brief_title, purpose: origin.brief_purpose, origin };
const independent = {
  schema_version: "1.0.0",
  project_id: "project-independent",
  learner_id: "learner-a",
  title: "My independent research",
  charter: "Compare reviewed evidence.",
  origin: { origin_type: "independent" },
  lifecycle: "active",
  revision: 1,
  created_at: "2026-10-16T20:00:00Z",
  updated_at: "2026-10-16T20:00:00Z",
};

function json(route: Route, status: number, body: unknown) {
  return route.fulfill({ status, contentType: "application/json", body: JSON.stringify(body) });
}

function canonicalJson(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map(canonicalJson).join(",")}]`;
  if (typeof value === "object" && value !== null) {
    const record = value as Record<string, unknown>;
    return `{${Object.keys(record).filter((key) => record[key] !== null && record[key] !== undefined).sort()
      .map((key) => `${JSON.stringify(key)}:${canonicalJson(record[key])}`).join(",")}}`;
  }
  return JSON.stringify(value);
}

function canonicalDigest(value: unknown): string {
  return createHash("sha256").update(canonicalJson(value), "utf8").digest("hex");
}

async function mockProjects(page: Page, postBodies: Record<string, unknown>[], options: {
  beforeCreateResponse?: () => Promise<void>;
  firstCreateStatus?: 409 | 503;
  staleStartOption?: boolean;
} = {}) {
  let created: Record<string, unknown> | null = null;
  let creates = 0;
  let workspaceRevision = 1;
  const notes: Record<string, unknown>[] = [];
  const references: Record<string, unknown>[] = [];
  const artifacts: Record<string, unknown>[] = [];
  const snapshots: Record<string, unknown>[] = [];
  let acceptedEvidence: Record<string, unknown> | null = null;
  let artifactBytes = "";
  const workspace = (projectId: string) => ({
    schema_version: "1.0.0", project_id: projectId, learner_id: "learner-a", workspace_revision: workspaceRevision,
    notes, references, artifacts, domain_links: [], created_at: "2026-10-16T20:00:00Z", updated_at: `2026-10-16T20:${String(workspaceRevision).padStart(2, "0")}:00Z`,
  });
  await page.route("**/api/v1/session/single-profile", (route) => json(route, 201, {
    status: "ready", authentication_method: "single_profile", expires_at: "2026-10-16T22:00:00Z",
  }));
  await page.route("**/api/v1/projects**", async (route) => {
    const request = route.request();
    const url = new URL(request.url());
    if (request.method() === "POST" && url.pathname === "/api/v1/projects") {
      const body = request.postDataJSON() as Record<string, unknown>;
      postBodies.push(body);
      creates += 1;
      await options.beforeCreateResponse?.();
      if (options.firstCreateStatus && creates === 1) return json(route, options.firstCreateStatus, { code: options.firstCreateStatus === 409 ? "idempotency_conflict" : "unavailable" });
      created = {
        schema_version: "1.0.0", project_id: "project-learning", learner_id: "learner-a",
        title: body.title, charter: body.charter, origin: body.origin, lifecycle: "active", revision: 1,
        created_at: "2026-10-16T21:00:00Z", updated_at: "2026-10-16T21:00:00Z",
      };
      return json(route, 200, created);
    }
    const workspaceMatch = /^\/api\/v1\/projects\/([^/]+)\/workspace$/.exec(url.pathname);
    if (request.method() === "GET" && workspaceMatch) return json(route, 200, workspace(workspaceMatch[1]!));
    const mutationMatch = /^\/api\/v1\/projects\/([^/]+)\/workspace\/mutations$/.exec(url.pathname);
    if (request.method() === "POST" && mutationMatch) {
      const body = request.postDataJSON() as { mutation: Record<string, unknown> };
      postBodies.push(body as unknown as Record<string, unknown>);
      workspaceRevision += 1;
      if (body.mutation.operation === "add_note") notes.push({ note_id: `note-${notes.length + 1}`, note_version: 1, title: body.mutation.title, body: body.mutation.body, created_at: "2026-10-16T20:01:00Z", updated_at: "2026-10-16T20:01:00Z" });
      if (body.mutation.operation === "add_reference") references.push({ reference_id: `source-${references.length + 1}`, reference_version: 1, title: body.mutation.title, url: body.mutation.url, source_name: body.mutation.source_name, created_at: "2026-10-16T20:01:00Z", updated_at: "2026-10-16T20:01:00Z" });
      return json(route, 200, workspace(mutationMatch[1]!));
    }
    const artifactCollectionMatch = /^\/api\/v1\/projects\/([^/]+)\/artifacts$/.exec(url.pathname);
    if (request.method() === "POST" && artifactCollectionMatch) {
      const body = request.postDataJSON() as { content_base64: string; intent: { mutation: { artifact: Record<string, unknown> } } };
      postBodies.push(body as unknown as Record<string, unknown>);
      artifactBytes = Buffer.from(body.content_base64, "base64").toString("utf8");
      workspaceRevision += 1;
      artifacts.push({ ...body.intent.mutation.artifact, artifact_id: `artifact-${artifacts.length + 1}`, artifact_version: 1, created_at: "2026-10-16T20:02:00Z" });
      return json(route, 200, workspace(artifactCollectionMatch[1]!));
    }
    const artifactDownloadMatch = /^\/api\/v1\/projects\/([^/]+)\/artifacts\/([^/]+)\/versions\/(\d+)$/.exec(url.pathname);
    if (request.method() === "GET" && artifactDownloadMatch) return route.fulfill({ status: 200, contentType: "application/octet-stream", body: artifactBytes });
    const snapshotCollectionMatch = /^\/api\/v1\/projects\/([^/]+)\/snapshots$/.exec(url.pathname);
    if (request.method() === "POST" && snapshotCollectionMatch) {
      const body = request.postDataJSON() as Record<string, unknown>;
      postBodies.push(body);
      const snapshotMaterial = { project_id: snapshotCollectionMatch[1], learner_id: "learner-a", project_revision: 1, project_shell_digest: "e".repeat(64), workspace_revision: workspaceRevision, workspace_created_at: "2026-10-16T20:00:00Z", workspace_updated_at: workspace(snapshotCollectionMatch[1]!).updated_at, notes: notes.map((note) => ({ record_id: note.note_id, record_version: 1, record_digest: canonicalDigest(note) })), references: references.map((reference) => ({ record_id: reference.reference_id, record_version: 1, record_digest: canonicalDigest(reference) })), artifacts: artifacts.map((artifact) => ({ artifact_id: artifact.artifact_id, artifact_version: 1, manifest_digest: canonicalDigest(artifact), content_digest: artifact.content_digest, byte_count: artifact.byte_count })), domain_links: [] };
      const record = { schema_version: "1.0.0", snapshot_id: `snapshot-${snapshots.length + 1}`, snapshot_digest: canonicalDigest(snapshotMaterial), closed_at: "2026-10-16T20:03:00Z", snapshot: snapshotMaterial };
      snapshots.push(record);
      return json(route, 200, record);
    }
    if (request.method() === "GET" && snapshotCollectionMatch) return json(route, 200, { records: snapshots });
    const candidateMatch = /^\/api\/v1\/projects\/([^/]+)\/snapshots\/([^/]+)\/submission-candidate$/.exec(url.pathname);
    if (request.method() === "GET" && candidateMatch) {
      const snapshotRecord = snapshots.find((item) => item.snapshot_id === candidateMatch[2]) as { snapshot_digest?: string; closed_at?: string; snapshot?: { workspace_revision?: number } } | undefined;
      if (!snapshotRecord) return json(route, 404, { code: "not_found" });
      const resources = [
        ...notes.map((note) => ({ resource_kind: "note", resource_id: note.note_id, resource_version: 1, record_digest: canonicalDigest(note) })),
        ...references.map((reference) => ({ resource_kind: "source", resource_id: reference.reference_id, resource_version: 1, record_digest: canonicalDigest(reference) })),
        ...artifacts.map((artifact) => ({ resource_kind: "artifact", resource_id: artifact.artifact_id, resource_version: 1, record_digest: canonicalDigest(artifact), content_digest: artifact.content_digest, byte_count: artifact.byte_count })),
      ];
      return json(route, 200, {
        schema_version: "1.0.0",
        project: { project_id: candidateMatch[1], project_revision: 1, project_shell_digest: "e".repeat(64), snapshot_id: candidateMatch[2], snapshot_digest: snapshotRecord.snapshot_digest, workspace_revision: snapshotRecord.snapshot?.workspace_revision, closed_at: snapshotRecord.closed_at },
        origin: {
          package_id: origin.package_id, package_version: origin.package_version, package_digest: origin.package_digest,
          brief_id: origin.brief_id, brief_version: origin.brief_version, brief_digest: origin.brief_digest,
          curriculum_id: origin.curriculum_id, curriculum_version: origin.curriculum_version, curriculum_digest: origin.curriculum_digest,
          placement_id: origin.placement_id, placement_version: origin.placement_version, placement_digest: origin.placement_digest,
        },
        policy_id: "assessment-project-closure", policy_version: "1.0.0",
        milestones: [
          { milestone_id: "milestone-one", milestone_version: "1.0.0", sequence: 1, title: "Compare the evidence" },
          { milestone_id: "milestone-two", milestone_version: "1.0.0", sequence: 2, title: "Explain the comparison" },
        ],
        resources,
      });
    }
    const submissionCollectionMatch = /^\/api\/v1\/projects\/([^/]+)\/snapshots\/([^/]+)\/submissions$/.exec(url.pathname);
    if (request.method() === "POST" && submissionCollectionMatch) {
      const body = request.postDataJSON() as Record<string, unknown>;
      postBodies.push(body);
      acceptedEvidence = {
        schema_version: "1.0.0", evidence_id: "evidence-one", learner_id: "learner-a", submission_id: body.submission_id,
        project_id: submissionCollectionMatch[1], snapshot_id: submissionCollectionMatch[2], snapshot_digest: (body.source as Record<string, unknown>).snapshot_digest,
        brief_id: origin.brief_id, brief_version: origin.brief_version, brief_digest: origin.brief_digest,
        placement_id: origin.placement_id, placement_version: origin.placement_version, placement_digest: origin.placement_digest,
        policy_id: "assessment-project-closure", policy_version: "1.0.0", milestone_evidence: body.milestone_evidence,
        milestone_ids: (body.milestone_evidence as { milestone_id: string }[]).map((item) => item.milestone_id), request_fingerprint: "f".repeat(64), occurrence: 1, accepted_sequence: 1,
        submitted_at: "2026-10-16T20:05:00Z",
      };
      return json(route, 200, { validation: { schema_version: "1.0.0", status: "accepted", request_fingerprint: "f".repeat(64), issues: [] }, evidence: acceptedEvidence });
    }
    const exactSubmissionMatch = /^\/api\/v1\/projects\/([^/]+)\/submissions\/([^/]+)$/.exec(url.pathname);
    if (request.method() === "GET" && exactSubmissionMatch) return acceptedEvidence && acceptedEvidence.submission_id === exactSubmissionMatch[2]
      ? json(route, 200, acceptedEvidence)
      : json(route, 404, { code: "not_found" });
    const historyMatch = /^\/api\/v1\/projects\/([^/]+)\/submissions$/.exec(url.pathname);
    if (request.method() === "GET" && historyMatch) return json(route, 200, {
      schema_version: "1.0.0", project_id: historyMatch[1], items: acceptedEvidence ? [{
        evidence_id: acceptedEvidence.evidence_id, submission_id: acceptedEvidence.submission_id,
        snapshot_id: acceptedEvidence.snapshot_id, snapshot_digest: acceptedEvidence.snapshot_digest,
        request_fingerprint: acceptedEvidence.request_fingerprint, occurrence: 1, submitted_at: acceptedEvidence.submitted_at,
      }] : [],
    });
    const completionMatch = /^\/api\/v1\/projects\/([^/]+)\/completion$/.exec(url.pathname);
    if (request.method() === "GET" && completionMatch) return json(route, 200, {
      projection_version: "1.0.0", project_id: completionMatch[1], completed: acceptedEvidence !== null,
      completion_meaning: acceptedEvidence ? "bounded_project_activity_completed" : "not_completed",
      source_digest: "b".repeat(64), rebuilt_at: "2026-10-16T20:06:00Z",
      history: acceptedEvidence ? [{
        event_id: "event-one", evidence_id: acceptedEvidence.evidence_id, submission_id: acceptedEvidence.submission_id,
        snapshot_id: acceptedEvidence.snapshot_id, snapshot_digest: acceptedEvidence.snapshot_digest,
        brief_id: origin.brief_id, brief_version: origin.brief_version, brief_digest: origin.brief_digest,
        placement_id: origin.placement_id, placement_version: origin.placement_version, placement_digest: origin.placement_digest,
        policy_id: "assessment-project-closure", policy_version: "1.0.0", milestone_ids: acceptedEvidence.milestone_ids,
        request_fingerprint: acceptedEvidence.request_fingerprint, occurrence: 1, accepted_sequence: 1,
        submitted_at: acceptedEvidence.submitted_at, occurred_at: "2026-10-16T20:05:00Z",
      }] : [],
    });
    const exportMatch = /^\/api\/v1\/projects\/([^/]+)\/snapshots\/([^/]+)\/export$/.exec(url.pathname);
    if (request.method() === "GET" && exportMatch) {
      const snapshotRecord = snapshots.find((item) => item.snapshot_id === exportMatch[2]);
      const artifactFiles = artifacts.map((artifact) => ({ artifact_id: artifact.artifact_id, artifact_version: 1, byte_count: artifact.byte_count, content_digest: artifact.content_digest, logical_path: artifact.logical_path, manifest_digest: canonicalDigest(artifact), media_type: artifact.media_type }));
      const exportMaterial = { format: "project-evidence-manifest-v1", project_id: exportMatch[1], snapshot_id: exportMatch[2], snapshot_digest: snapshotRecord?.snapshot_digest, snapshot_record: snapshotRecord, workspace_record: workspace(exportMatch[1]!), artifact_files: artifactFiles, excluded_artifacts: [] };
      return json(route, 200, { manifest: { schema_version: "1.0.0", export_id: "export-one", export_digest: canonicalDigest(exportMaterial), generated_at: "2026-10-16T20:04:00Z", export: exportMaterial }, files: artifacts.map((artifact) => ({ artifact_id: artifact.artifact_id, artifact_version: 1, content_base64: Buffer.from(artifactBytes).toString("base64"), logical_path: artifact.logical_path })) });
    }
    if (url.pathname === "/api/v1/projects/start-options") return json(route, 200, { records: [option] });
    if (url.pathname === `/api/v1/projects/start-options/${origin.placement_id}`) return options.staleStartOption ? json(route, 400, { code: "stale_source" }) : json(route, 200, option);
    if (url.pathname === "/api/v1/projects") return json(route, 200, { records: [independent] });
    if (url.pathname === "/api/v1/projects/project-learning" && created) return json(route, 200, created);
    if (url.pathname === "/api/v1/projects/project-independent") return json(route, 200, independent);
    return json(route, 404, { code: "not_found" });
  });
}

test("lists, starts, and reopens a learning Project through public APIs", async ({ page }) => {
  const posts: Record<string, unknown>[] = [];
  await mockProjects(page, posts);
  await page.goto("/projects");
  await expect(page.getByRole("heading", { level: 1, name: "Projects" })).toBeVisible();
  await expect(page.getByText("My independent research")).toBeVisible();
  await expect(page.getByText(option.title)).toBeVisible();
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);

  const lightText = await page.locator("main").innerText();
  await page.getByLabel("Theme").selectOption("dark");
  expect(await page.locator("main").innerText()).toBe(lightText);
  await page.getByRole("link", { name: "Start project" }).click();
  await page.getByLabel(/What do you want/i).fill("Apply the learning brief to reviewed evidence.");
  const requestPromise = page.waitForRequest((request) => request.method() === "POST" && new URL(request.url()).pathname === "/api/v1/projects");
  await page.getByRole("button", { name: "Create Project" }).click();
  const createRequest = await requestPromise;

  await expect(page).toHaveURL(/\/projects\/project-learning$/);
  await expect(page.getByRole("heading", { level: 1, name: option.title, exact: true })).toBeVisible();
  const submitted = createRequest.postDataJSON() as Record<string, unknown>;
  expect(submitted).not.toHaveProperty("learner_id");
  expect(submitted.origin).toEqual(origin);
  await page.getByText("Technical record").click();
  await expect(page.getByText(origin.placement_digest)).toBeVisible();
  await expect(page.getByText(origin.package_digest)).toBeVisible();
  await expect(page.getByText(origin.curriculum_digest)).toBeVisible();
  await expect(page.getByText(origin.project_brief_schema_version, { exact: true })).toBeVisible();
});

test("reuses one retry key for unchanged intent", async ({ page }) => {
  const posts: Record<string, unknown>[] = [];
  await mockProjects(page, posts, { firstCreateStatus: 503 });
  await page.goto(`/projects/new?placement=${origin.placement_id}`);
  await page.getByLabel(/What do you want/i).fill("First bounded purpose.");
  const firstRequestPromise = page.waitForRequest((request) => request.method() === "POST" && new URL(request.url()).pathname === "/api/v1/projects");
  await page.getByRole("button", { name: "Create Project" }).click();
  const firstRequest = await firstRequestPromise;
  await expect(page.getByText("Project not created")).toBeVisible();
  await expect(page.getByLabel(/What do you want/i)).toHaveValue("First bounded purpose.");
  const firstKey = (firstRequest.postDataJSON() as Record<string, unknown>).idempotency_key;

  const retryRequestPromise = page.waitForRequest((request) => request.method() === "POST" && new URL(request.url()).pathname === "/api/v1/projects");
  await page.getByRole("button", { name: "Create Project" }).click();
  const retryRequest = await retryRequestPromise;
  await expect(page).toHaveURL(/\/projects\/project-learning$/);
  expect((retryRequest.postDataJSON() as Record<string, unknown>).idempotency_key).toBe(firstKey);
});

test("uses a fresh request after an idempotency conflict", async ({ page }) => {
  const posts: Record<string, unknown>[] = [];
  await mockProjects(page, posts, { firstCreateStatus: 409 });
  await page.goto(`/projects/new?placement=${origin.placement_id}`);
  await page.getByLabel(/What do you want/i).fill("First bounded purpose.");
  await page.getByRole("button", { name: "Create Project" }).click();
  await expect(page.getByText(/fresh request/i)).toBeVisible();

  await page.getByRole("button", { name: "Create Project" }).click();

  await expect(page).toHaveURL(/\/projects\/project-learning$/);
  expect(posts[1]?.idempotency_key).not.toBe(posts[0]?.idempotency_key);
});

test("keeps the submitted Project draft fixed while the response is pending", async ({ page }) => {
  let release!: () => void;
  const pending = new Promise<void>((resolve) => { release = resolve; });
  await mockProjects(page, [], { beforeCreateResponse: () => pending });
  await page.goto("/projects/new");
  await page.getByLabel("Project title").fill("Delayed response");
  await page.getByLabel(/What do you want/i).fill("Keep this exact request fixed.");
  const submit = page.getByRole("button", { name: "Create Project" }).click();

  await expect(page.getByLabel("Project title")).toBeDisabled();
  await expect(page.getByLabel(/What do you want/i)).toBeDisabled();
  release();
  await submit;
  await expect(page).toHaveURL(/\/projects\/project-learning$/);
});

test("returns a stale learning choice to current Projects", async ({ page }) => {
  await mockProjects(page, [], { staleStartOption: true });
  await page.goto(`/projects/new?placement=${origin.placement_id}`);

  await expect(page.getByText("Project not found")).toBeVisible();
  await page.getByRole("button", { name: "Return to Projects" }).click();
  await expect(page).toHaveURL(/\/projects$/);
});

test("reflows at narrow width and keeps plain language outside technical records", async ({ page }) => {
  await mockProjects(page, []);
  await page.setViewportSize({ width: 375, height: 720 });
  await page.goto("/projects");
  const dimensions = await page.evaluate(() => ({ viewport: document.documentElement.clientWidth, content: document.documentElement.scrollWidth }));
  expect(dimensions.content).toBeLessThanOrEqual(dimensions.viewport);
  await expect(page.locator("main")).not.toContainText(/database|idempotency|object storage|foreign key/i);
  await page.emulateMedia({ reducedMotion: "reduce", forcedColors: "active" });
  await page.getByRole("link", { name: "Start project" }).focus();
  expect(await page.getByRole("link", { name: "Start project" }).evaluate((element) => getComputedStyle(element).outlineStyle)).not.toBe("none");
});

test("saves Project work, keeps files inert, closes a snapshot, and continues working", async ({ page }) => {
  const posts: Record<string, unknown>[] = [];
  await mockProjects(page, posts);
  await page.goto("/projects/project-independent");
  await expect(page.getByRole("heading", { level: 2, name: "Notes" })).toBeVisible();
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);

  await page.getByLabel("Note title").fill("Evidence notes");
  await page.getByLabel("Note", { exact: true }).fill("Compare the reviewed source with the learner-created table.");
  await page.getByRole("button", { name: "Save note" }).click();
  await expect(page.getByRole("heading", { level: 3, name: "Evidence notes" })).toBeVisible();

  await page.getByLabel("File", { exact: true }).setInputFiles({ name: "evidence.txt", mimeType: "text/plain", buffer: Buffer.from("evidence") });
  await page.getByLabel("File format").selectOption("text/plain");
  await page.getByLabel("Source title", { exact: true }).last().fill("Learner evidence");
  await page.getByRole("button", { name: "Add file" }).click();
  await expect(page.getByRole("heading", { level: 3, name: "evidence.txt" })).toBeVisible();
  await expect(page.getByText(/does not run, expand, or actively preview/i).first()).toBeVisible();
  const artifactDownload = page.waitForEvent("download");
  await page.getByRole("button", { name: "Download original file" }).click();
  await expect((await artifactDownload).suggestedFilename()).toBe("evidence.txt");

  await page.getByRole("button", { name: "Save checkpoint" }).click();
  await expect(page.getByRole("heading", { level: 3, name: /Checkpoint from/ })).toBeVisible();
  await expect(page.getByText(/It contains 1 notes/)).toBeVisible();
  const evidenceDownload = page.waitForEvent("download");
  await page.getByRole("button", { name: "Download evidence record" }).click();
  await expect((await evidenceDownload).suggestedFilename()).toBe("project-independent-snapshot-1-evidence.json");

  await page.getByLabel("Note title").last().fill("Continued work");
  await page.getByLabel("Note", { exact: true }).last().fill("This change follows the closed snapshot.");
  await page.getByRole("button", { name: "Save note" }).click();
  await expect(page.getByRole("heading", { level: 3, name: "Continued work" })).toBeVisible();
  await expect(page.getByText(/It contains 1 notes/)).toBeVisible();
  await page.getByRole("button", { name: "Save checkpoint" }).click();
  await expect(page.getByRole("heading", { level: 3, name: /Checkpoint from/ })).toHaveCount(2);

  const mutationBodies = posts.filter((body) => "mutation" in body);
  expect(mutationBodies).toHaveLength(2);
  for (const body of mutationBodies) expect(body).not.toHaveProperty("learner_id");
  expect(posts.some((body) => "content_base64" in body)).toBe(true);
  const checkpointBodies = posts.filter((body) => "expected_project_revision" in body);
  expect(checkpointBodies).toHaveLength(2);
  expect(new Set(checkpointBodies.map((body) => body.idempotency_key)).size).toBe(2);
});

test("denies every direct learning-evidence route for an independent Project", async ({ page }) => {
  await mockProjects(page, []);
  for (const query of ["", "?snapshot=snapshot-one", "?submission=submission-one"]) {
    await page.goto(`/projects/project-independent/learning${query}`);
    await expect(page.getByRole("heading", { name: "Project not found" })).toBeVisible();
    await expect(page.locator("main")).not.toContainText(/learning record|accepted checkpoint|submit for learning/i);
  }
});

test("submits a learning Project checkpoint and reopens the accepted evidence", async ({ page }) => {
  const posts: Record<string, unknown>[] = [];
  await mockProjects(page, posts);
  await page.setViewportSize({ width: 375, height: 720 });
  await page.goto(`/projects/new?placement=${origin.placement_id}`);
  await page.getByLabel(/What do you want/i).fill("Apply the learning brief to evidence.");
  await page.getByRole("button", { name: "Create Project" }).click();
  await page.getByLabel("Note title").fill("Comparison evidence");
  await page.getByLabel("Note", { exact: true }).fill("A bounded comparison with no recommendation.");
  await page.getByRole("button", { name: "Save note" }).click();
  await expect(page.getByRole("heading", { level: 3, name: "Comparison evidence" })).toBeVisible();
  const secondNote = page.getByRole("group", { name: "Add a note" });
  await secondNote.getByLabel("Note title").fill("Explanation evidence");
  await secondNote.getByLabel("Note", { exact: true }).fill("An explanation kept separate from the comparison.");
  await secondNote.getByRole("button", { name: "Save note" }).click();
  await expect(page.getByRole("heading", { level: 3, name: "Explanation evidence" })).toBeVisible();
  await page.getByRole("button", { name: "Save checkpoint" }).click();
  await page.getByRole("link", { name: "Submit for learning" }).click();

  await expect(page.getByRole("heading", { name: "Choose evidence for each milestone" })).toBeVisible();
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  const dimensions = await page.evaluate(() => ({ viewport: document.documentElement.clientWidth, content: document.documentElement.scrollWidth }));
  expect(dimensions.content).toBeLessThanOrEqual(dimensions.viewport);
  const lightText = await page.locator("main").innerText();
  await page.getByLabel("Theme").selectOption("dark");
  expect(await page.locator("main").innerText()).toBe(lightText);
  await page.emulateMedia({ reducedMotion: "reduce", forcedColors: "active" });
  await page.getByLabel("Saved note note-1 — version 1").first().check();
  await page.getByLabel("Saved note note-2 — version 1").nth(1).check();
  const submitButton = page.getByRole("button", { name: "Submit checkpoint" });
  await submitButton.focus();
  await page.keyboard.press("Tab");
  await page.keyboard.press("Shift+Tab");
  expect(await submitButton.evaluate((element) => getComputedStyle(element).outlineStyle)).not.toBe("none");
  const submission = page.waitForRequest((request) => request.method() === "POST" && new URL(request.url()).pathname.endsWith("/submissions"));
  await page.getByRole("button", { name: "Submit checkpoint" }).click();
  const submitted = await submission;

  await expect(page).toHaveURL(/\/learning\?submission=/);
  await expect(page.getByRole("heading", { name: "Submitted checkpoint" })).toBeVisible();
  await expect(page.getByText(/does not grade its quality, show mastery, or provide financial advice/i)).toBeVisible();
  const body = submitted.postDataJSON() as Record<string, unknown>;
  expect(body).not.toHaveProperty("learner_id");
  expect(body).toEqual(expect.objectContaining({ policy_id: "assessment-project-closure", milestone_evidence: [
    expect.objectContaining({ milestone_id: "milestone-one", resources: [expect.objectContaining({ resource_id: "note-1" })] }),
    expect.objectContaining({ milestone_id: "milestone-two", resources: [expect.objectContaining({ resource_id: "note-2" })] }),
  ] }));
});

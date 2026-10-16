import { describe, expect, it, vi } from "vitest";

import type { FinancialAcademyApiClient } from "../../src/generated/api-client";
import {
  createProjectArtifactDownloader,
  createProjectCreateAction,
  createProjectCreateLoader,
  createProjectDetailLoader,
  createProjectListLoader,
  createProjectSnapshotExporter,
  createProjectWorkspaceAction,
} from "../../src/features/project-workspace/api";
import {
  learningStartOptionListIsSafe,
  projectListIsSafe,
  projectSnapshotListIsSafe,
  projectWorkspaceIsSafe,
  type LearningProjectStartOption,
  type ProjectArtifact,
  type ProjectShell,
  type ProjectSnapshot,
  type ProjectWorkspace,
} from "../../src/features/project-workspace/model";
import type { SingleProfileSession } from "../../src/platform/auth/singleProfileSession";

const origin = {
  origin_type: "learning" as const,
  project_brief_schema_version: "1.0.0" as const,
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

const option: LearningProjectStartOption = {
  title: origin.brief_title,
  purpose: origin.brief_purpose,
  origin,
};

const project: ProjectShell = {
  schema_version: "1.0.0",
  project_id: "project-alpha",
  learner_id: "learner-a",
  title: "Évidence comparison",
  charter: "Compare sources without making an investment recommendation.",
  origin: { origin_type: "independent" },
  lifecycle: "active",
  revision: 1,
  created_at: "2026-10-16T20:00:00Z",
  updated_at: "2026-10-16T20:00:00+00:00",
};
const workspace: ProjectWorkspace = {
  schema_version: "1.0.0",
  project_id: project.project_id,
  learner_id: project.learner_id,
  workspace_revision: 3,
  notes: [{ note_id: "note-one", note_version: 2, title: "Résumé", body: "First line\nSecond line", created_at: "2026-10-16T20:00:00Z", updated_at: "2026-10-16T20:01:00Z" }],
  references: [{ reference_id: "source-one", reference_version: 1, title: "Reviewed source", url: "https://example.test/research", source_name: "Example publisher", created_at: "2026-10-16T20:00:00Z", updated_at: "2026-10-16T20:00:00Z" }],
  artifacts: [],
  domain_links: [],
  created_at: "2026-10-16T20:00:00Z",
  updated_at: "2026-10-16T20:01:00Z",
};
const snapshot: ProjectSnapshot = {
  schema_version: "1.0.0",
  snapshot_id: "snapshot-one",
  snapshot_digest: "f".repeat(64),
  closed_at: "2026-10-16T20:02:00Z",
  snapshot: {
    project_id: project.project_id,
    learner_id: project.learner_id,
    project_revision: project.revision,
    project_shell_digest: "a".repeat(64),
    workspace_revision: workspace.workspace_revision,
    workspace_created_at: workspace.created_at,
    workspace_updated_at: workspace.updated_at,
    notes: [{ record_id: "note-one", record_version: 2, record_digest: "b".repeat(64) }],
    references: [], artifacts: [], domain_links: [],
  },
};

function response(status: number, data?: unknown) {
  return { data, error: undefined, response: new Response(null, { status }) };
}

function session() {
  return {
    ensure: vi.fn().mockResolvedValue({ status: "ready" }),
    invalidate: vi.fn(),
  } as unknown as SingleProfileSession;
}

describe("Project response validation", () => {
  it("accepts empty, varied, reordered, Unicode, and boundary-length records", () => {
    const second = {
      ...project,
      project_id: "project-zeta",
      title: "T".repeat(120),
      charter: "C".repeat(4000),
      created_at: "2024-02-29T12:00:00-05:00",
    };
    expect(projectListIsSafe({ records: [] })).toBe(true);
    expect(projectListIsSafe({ records: [second, project] })).toBe(true);
    expect(learningStartOptionListIsSafe({ records: [] })).toBe(true);
    expect(learningStartOptionListIsSafe({ records: [option] })).toBe(true);
  });

  it.each([
    ["unknown envelope field", { records: [project], private_owner: "hidden" }],
    ["duplicate Project", { records: [project, project] }],
    ["invalid calendar time", { records: [{ ...project, created_at: "2026-02-31T12:00:00Z" }] }],
    ["technical extra field", { records: [{ ...project, storage_path: "private" }] }],
  ])("rejects %s without accepting a partial list", (_label, value) => {
    expect(projectListIsSafe(value)).toBe(false);
  });

  it("rejects duplicate or client-altered learning choices", () => {
    expect(learningStartOptionListIsSafe({ records: [option, option] })).toBe(false);
    expect(learningStartOptionListIsSafe({ records: [{ ...option, title: "Changed" }] })).toBe(false);
  });

  it("accepts flexible correlated workspaces and snapshots without a fixture count", () => {
    expect(projectWorkspaceIsSafe({ ...workspace, notes: [], references: [], artifacts: [], domain_links: [] }, project)).toBe(true);
    expect(projectWorkspaceIsSafe(workspace, project)).toBe(true);
    expect(projectSnapshotListIsSafe({ records: [] }, project)).toBe(true);
    expect(projectSnapshotListIsSafe({ records: [snapshot] }, project)).toBe(true);
  });

  it.each([
    ["private workspace field", { ...workspace, object_key: "private" }],
    ["wrong learner", { ...workspace, learner_id: "learner-other" }],
    ["duplicate notes", { ...workspace, notes: [workspace.notes[0], workspace.notes[0]] }],
    ["unsafe source address", { ...workspace, references: [{ ...workspace.references[0], url: "http://example.test" }] }],
  ])("rejects %s as a complete workspace", (_label, value) => {
    expect(projectWorkspaceIsSafe(value, project)).toBe(false);
  });

  it("rejects a snapshot list that is duplicated, uncorrelated, or technically extended", () => {
    expect(projectSnapshotListIsSafe({ records: [snapshot, snapshot] }, project)).toBe(false);
    expect(projectSnapshotListIsSafe({ records: [{ ...snapshot, snapshot: { ...snapshot.snapshot, learner_id: "learner-other" } }] }, project)).toBe(false);
    expect(projectSnapshotListIsSafe({ records: [{ ...snapshot, storage_path: "private" }] }, project)).toBe(false);
  });
});

describe("Project generated-client loaders and action", () => {
  it("loads independent records and learning choices without assuming a fixture count or order", async () => {
    const get = vi.fn()
      .mockResolvedValueOnce(response(200, { records: [project] }))
      .mockResolvedValueOnce(response(200, { records: [option] }));
    const loader = createProjectListLoader({ GET: get } as unknown as FinancialAcademyApiClient, session());
    const result = await loader({ request: new Request("http://localhost/projects") } as never);

    expect(result).toEqual({ status: "ready", projects: [project], options: [option] });
    expect(get).toHaveBeenCalledWith("/api/v1/projects", expect.objectContaining({ signal: expect.any(AbortSignal) }));
    expect(get).toHaveBeenCalledWith("/api/v1/projects/start-options", expect.objectContaining({ signal: expect.any(AbortSignal) }));
  });

  it("rejects unknown create URL state before session or API work", async () => {
    const selectedSession = session();
    const get = vi.fn();
    const loader = createProjectCreateLoader({ GET: get } as unknown as FinancialAcademyApiClient, selectedSession);
    const result = await loader({ request: new Request("http://localhost/projects/new?owner=client") } as never);

    expect(result).toEqual({ status: "invalid-selection" });
    expect(selectedSession.ensure).not.toHaveBeenCalled();
    expect(get).not.toHaveBeenCalled();
  });

  it("returns stale learning choices to the current Projects list", async () => {
    const get = vi.fn().mockResolvedValue(response(400, { code: "stale_source" }));
    const loader = createProjectCreateLoader({ GET: get } as unknown as FinancialAcademyApiClient, session());

    const result = await loader({ request: new Request(`http://localhost/projects/new?placement=${origin.placement_id}`) } as never);

    expect(result).toEqual({ status: "invalid-selection" });
  });

  it("resolves exact learning origin again before create and never submits learner authority", async () => {
    const get = vi.fn().mockResolvedValue(response(200, option));
    const post = vi.fn().mockResolvedValue(response(200, { ...project, project_id: "project-learning", origin }));
    const action = createProjectCreateAction({ GET: get, POST: post } as unknown as FinancialAcademyApiClient, session());
    const form = new FormData();
    form.set("title", "My comparison");
    form.set("charter", "Apply the approved brief.");
    form.set("placement_id", origin.placement_id);
    form.set("idempotency_key", "11111111-1111-4111-8111-111111111111");

    const result = await action({ request: new Request("http://localhost/projects/new", { body: form, method: "POST" }) } as never);

    expect(result).toBeInstanceOf(Response);
    expect((result as Response).headers.get("location")).toBe("/projects/project-learning");
    const submitted = post.mock.calls[0]?.[1]?.body as Record<string, unknown>;
    expect(submitted).not.toHaveProperty("learner_id");
    expect(submitted.origin).toEqual(origin);
    expect(submitted.idempotency_key).toBe("11111111-1111-4111-8111-111111111111");
  });

  it("does not classify an idempotency conflict as an unchanged retry", async () => {
    const get = vi.fn().mockResolvedValue(response(200, option));
    const post = vi.fn().mockResolvedValue(response(409, { code: "idempotency_conflict" }));
    const action = createProjectCreateAction({ GET: get, POST: post } as unknown as FinancialAcademyApiClient, session());
    const form = new FormData();
    form.set("title", "My comparison");
    form.set("charter", "Apply the approved brief.");
    form.set("placement_id", origin.placement_id);
    form.set("idempotency_key", "11111111-1111-4111-8111-111111111111");

    const result = await action({ request: new Request("http://localhost/projects/new", { body: form, method: "POST" }) } as never);

    expect(result).toEqual(expect.objectContaining({ status: "error", kind: "conflict" }));
  });

  it("opens the Project shell, workspace, and snapshot list as one closed view", async () => {
    const get = vi.fn()
      .mockResolvedValueOnce(response(200, project))
      .mockResolvedValueOnce(response(200, workspace))
      .mockResolvedValueOnce(response(200, { records: [snapshot] }));
    const loader = createProjectDetailLoader({ GET: get } as unknown as FinancialAcademyApiClient, session());

    const result = await loader({ request: new Request(`http://localhost/projects/${project.project_id}`), params: { projectId: project.project_id } } as never);

    expect(result).toEqual({ status: "ready", project, workspace, snapshots: [snapshot] });
    expect(get).toHaveBeenCalledTimes(3);
  });

  it("rejects one malformed member rather than displaying a partial workspace", async () => {
    const get = vi.fn()
      .mockResolvedValueOnce(response(200, project))
      .mockResolvedValueOnce(response(200, { ...workspace, learner_id: "learner-other" }))
      .mockResolvedValueOnce(response(200, { records: [] }));
    const loader = createProjectDetailLoader({ GET: get } as unknown as FinancialAcademyApiClient, session());

    expect(await loader({ request: new Request(`http://localhost/projects/${project.project_id}`), params: { projectId: project.project_id } } as never)).toEqual({ status: "invalid-response" });
  });

  it("sends a note through the generated mutation operation without learner authority", async () => {
    const post = vi.fn().mockResolvedValue(response(200, { ...workspace, workspace_revision: 4 }));
    const action = createProjectWorkspaceAction({ POST: post } as unknown as FinancialAcademyApiClient, session());
    const form = new FormData();
    form.set("intent", "add-note");
    form.set("idempotency_key", "11111111-1111-4111-8111-111111111111");
    form.set("expected_workspace_revision", "3");
    form.set("title", "A bounded note");
    form.set("body", "  Évidence and interpretation stay separate.\n");

    const result = await action({ request: new Request(`http://localhost/projects/${project.project_id}`, { method: "POST", body: form }), params: { projectId: project.project_id } } as never);

    expect(result).toBeInstanceOf(Response);
    expect(post).toHaveBeenCalledWith("/api/v1/projects/{project_id}/workspace/mutations", expect.objectContaining({
      body: expect.objectContaining({ expected_workspace_revision: 3, idempotency_key: "11111111-1111-4111-8111-111111111111", mutation: { operation: "add_note", title: "A bounded note", body: "  Évidence and interpretation stay separate.\r\n" } }),
    }));
    expect(post.mock.calls[0]?.[1]?.body).not.toHaveProperty("learner_id");
  });

  it("reports a stale revision without treating it as an accepted retry", async () => {
    const post = vi.fn().mockResolvedValue({ data: undefined, error: { code: "stale_revision" }, response: new Response(null, { status: 409 }) });
    const action = createProjectWorkspaceAction({ POST: post } as unknown as FinancialAcademyApiClient, session());
    const form = new FormData();
    form.set("intent", "add-note"); form.set("idempotency_key", "retry-key"); form.set("expected_workspace_revision", "3"); form.set("title", "Note"); form.set("body", "Body");

    expect(await action({ request: new Request(`http://localhost/projects/${project.project_id}`, { method: "POST", body: form }), params: { projectId: project.project_id } } as never)).toEqual({ status: "error", kind: "stale", intent: "note", idempotencyKey: "retry-key" });
  });

  it("checks downloaded inert bytes against the accepted count and fingerprint", async () => {
    const bytes = new TextEncoder().encode("evidence").buffer;
    const digest = [...new Uint8Array(await crypto.subtle.digest("SHA-256", bytes))].map((value) => value.toString(16).padStart(2, "0")).join("");
    const artifact: ProjectArtifact = { artifact_id: "artifact-one", artifact_version: 1, artifact_kind: "supporting_file", logical_path: "notes/evidence.txt", media_type: "text/plain", inspection_mode: "plain_text", byte_count: bytes.byteLength, content_digest: digest, provenance: { source_type: "learner_created", source_title: "Evidence" }, assumptions: [], created_at: workspace.created_at };
    const get = vi.fn().mockResolvedValue(response(200, bytes));
    const download = createProjectArtifactDownloader({ GET: get } as unknown as FinancialAcademyApiClient, session());

    expect(await download(project.project_id, artifact)).toEqual({ status: "ready", bytes, fileName: "evidence.txt", mediaType: "text/plain" });
    get.mockResolvedValueOnce(response(200, new TextEncoder().encode("changed").buffer));
    expect(await download(project.project_id, artifact)).toEqual({ status: "invalid-response" });
  });

  it("exports only a complete correlated checkpoint bundle", async () => {
    const bundle = { manifest: { schema_version: "1.0.0", export_id: "export-one", export_digest: "a".repeat(64), generated_at: "2026-10-16T20:03:00Z", export: { format: "project-evidence-manifest-v1", project_id: project.project_id, snapshot_id: snapshot.snapshot_id, snapshot_digest: snapshot.snapshot_digest, snapshot_record: snapshot, workspace_record: workspace, artifact_files: [], excluded_artifacts: [] } }, files: [] };
    const get = vi.fn().mockResolvedValue(response(200, bundle));
    const exportSnapshot = createProjectSnapshotExporter({ GET: get } as unknown as FinancialAcademyApiClient, session());

    const exported = await exportSnapshot(project.project_id, snapshot.snapshot_id);
    expect(exported).toEqual(expect.objectContaining({ status: "ready", fileName: `${project.project_id}-${snapshot.snapshot_id}-evidence.json` }));
    get.mockResolvedValueOnce(response(200, { ...bundle, private_storage_path: "hidden" }));
    expect(await exportSnapshot(project.project_id, snapshot.snapshot_id)).toEqual({ status: "invalid-response" });
  });
});

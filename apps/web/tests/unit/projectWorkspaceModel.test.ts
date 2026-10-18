import { describe, expect, it, vi } from "vitest";

import type { FinancialAcademyApiClient } from "../../src/generated/api-client";
import {
  createProjectArtifactDownloader,
  createProjectCreateAction,
  createProjectCreateLoader,
  createProjectDetailLoader,
  createProjectListLoader,
  createProjectLearningAction,
  createProjectLearningLoader,
  createProjectSnapshotExporter,
  createProjectWorkspaceAction,
} from "../../src/features/project-workspace/api";
import {
  learningStartOptionListIsSafe,
  projectListIsSafe,
  projectActivityCompletionIsSafe,
  projectCompletionHistoryIsSafe,
  projectLearningSelection,
  projectSubmissionCandidateIsSafe,
  projectSnapshotListIsSafe,
  projectTimestampsRepresentSameInstant,
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
const learningProject: ProjectShell = { ...project, project_id: "project-learning", origin };
const submissionCandidate = {
  schema_version: "1.0.0" as const,
  project: {
    project_id: learningProject.project_id, project_revision: 1, project_shell_digest: "e".repeat(64),
    snapshot_id: snapshot.snapshot_id, snapshot_digest: snapshot.snapshot_digest, workspace_revision: 3,
    closed_at: snapshot.closed_at,
  },
  origin: {
    package_id: origin.package_id, package_version: origin.package_version, package_digest: origin.package_digest,
    brief_id: origin.brief_id, brief_version: origin.brief_version, brief_digest: origin.brief_digest,
    curriculum_id: origin.curriculum_id, curriculum_version: origin.curriculum_version, curriculum_digest: origin.curriculum_digest,
    placement_id: origin.placement_id, placement_version: origin.placement_version, placement_digest: origin.placement_digest,
  },
  policy_id: "assessment-project-closure" as const,
  policy_version: "1.0.0" as const,
  milestones: [{ milestone_id: "milestone-one", milestone_version: "1.0.0", sequence: 1, title: "Compare evidence" }],
  resources: [{ resource_kind: "note" as const, resource_id: "note-one", resource_version: 2, record_digest: "b".repeat(64) }],
};
const variedSubmissionCandidate = {
  ...submissionCandidate,
  milestones: [
    submissionCandidate.milestones[0],
    { milestone_id: "milestone-two", milestone_version: "1.0.0", sequence: 2, title: "Explain the comparison" },
  ],
  resources: [
    ...submissionCandidate.resources,
    { resource_kind: "artifact" as const, resource_id: "artifact-one", resource_version: 1, record_digest: "d".repeat(64), content_digest: "e".repeat(64), byte_count: 128 },
  ],
};
const emptyHistory = { schema_version: "1.0.0" as const, project_id: learningProject.project_id, items: [] };
const emptyCompletion = {
  projection_version: "1.0.0" as const, project_id: learningProject.project_id, completed: false,
  completion_meaning: "not_completed" as const, source_digest: "c".repeat(64), rebuilt_at: snapshot.closed_at, history: [],
};

function response(status: number, data?: unknown) {
  return { data, error: undefined, response: new Response(null, { status }) };
}

function formDataStub(entries: Record<string, unknown>): FormData {
  const values = new Map(Object.entries(entries));
  return {
    get: (name: string) => values.get(name) ?? null,
    getAll: (name: string) => values.has(name) ? [values.get(name)] : [],
    keys: () => values.keys(),
  } as unknown as FormData;
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

async function canonicalDigest(value: unknown): Promise<string> {
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(canonicalJson(value)));
  return [...new Uint8Array(digest)].map((item) => item.toString(16).padStart(2, "0")).join("");
}

function base64(bytes: Uint8Array): string {
  return btoa(String.fromCharCode(...bytes));
}

async function exportBundle(exportedWorkspace: ProjectWorkspace = workspace, content = new Map<string, Uint8Array>()) {
  const noteReferences = await Promise.all(exportedWorkspace.notes.map(async (note) => ({ record_id: note.note_id, record_version: note.note_version, record_digest: await canonicalDigest(note) })));
  const sourceReferences = await Promise.all(exportedWorkspace.references.map(async (reference) => ({ record_id: reference.reference_id, record_version: reference.reference_version, record_digest: await canonicalDigest(reference) })));
  const artifactReferences = await Promise.all(exportedWorkspace.artifacts.map(async (artifact) => ({ artifact_id: artifact.artifact_id, artifact_version: artifact.artifact_version, manifest_digest: await canonicalDigest(artifact), content_digest: artifact.content_digest, byte_count: artifact.byte_count })));
  const linkReferences = await Promise.all(exportedWorkspace.domain_links.map(async (link) => ({ link_id: link.link_id, record_digest: await canonicalDigest(link), owner_reference_digest: link.owner_reference_digest })));
  const snapshotMaterial = { project_id: project.project_id, learner_id: project.learner_id, project_revision: project.revision, project_shell_digest: "a".repeat(64), workspace_revision: exportedWorkspace.workspace_revision, workspace_created_at: exportedWorkspace.created_at, workspace_updated_at: exportedWorkspace.updated_at, notes: noteReferences, references: sourceReferences, artifacts: artifactReferences, domain_links: linkReferences };
  const snapshotRecord = { schema_version: "1.0.0" as const, snapshot_id: snapshot.snapshot_id, snapshot_digest: await canonicalDigest(snapshotMaterial), closed_at: snapshot.closed_at, snapshot: snapshotMaterial };
  const artifactFiles = await Promise.all(exportedWorkspace.artifacts.filter((artifact) => content.has(artifact.artifact_id)).map(async (artifact) => ({ artifact_id: artifact.artifact_id, artifact_version: artifact.artifact_version, manifest_digest: await canonicalDigest(artifact), logical_path: artifact.logical_path, media_type: artifact.media_type, byte_count: artifact.byte_count, content_digest: artifact.content_digest })));
  const excludedArtifacts = exportedWorkspace.artifacts.filter((artifact) => !content.has(artifact.artifact_id)).map((artifact) => ({ artifact_id: artifact.artifact_id, artifact_version: artifact.artifact_version, reason: "content_unavailable" as const }));
  const material = { format: "project-evidence-manifest-v1" as const, project_id: project.project_id, snapshot_id: snapshot.snapshot_id, snapshot_digest: snapshotRecord.snapshot_digest, snapshot_record: snapshotRecord, workspace_record: exportedWorkspace, artifact_files: artifactFiles, excluded_artifacts: excludedArtifacts };
  const files = exportedWorkspace.artifacts.filter((artifact) => content.has(artifact.artifact_id)).map((artifact) => ({ artifact_id: artifact.artifact_id, artifact_version: artifact.artifact_version, content_base64: base64(content.get(artifact.artifact_id)!), logical_path: artifact.logical_path }));
  return { manifest: { schema_version: "1.0.0" as const, export_id: "export-one", export_digest: await canonicalDigest(material), generated_at: "2026-10-16T20:03:00Z", export: material }, files };
}

function session() {
  return {
    ensure: vi.fn().mockResolvedValue({ status: "ready" }),
    invalidate: vi.fn(),
  } as unknown as SingleProfileSession;
}

describe("Project response validation", () => {
  it("compares canonical Project timestamps without losing microseconds", () => {
    expect(projectTimestampsRepresentSameInstant("2026-10-18T01:21:20.8629Z", "2026-10-18T01:21:20.862900Z")).toBe(true);
    expect(projectTimestampsRepresentSameInstant("2026-10-18T01:21:20Z", "2026-10-18T01:21:20.000000Z")).toBe(true);
    expect(projectTimestampsRepresentSameInstant("2026-10-18T01:21:20.862900Z", "2026-10-18T01:21:20.862901Z")).toBe(false);
    expect(projectTimestampsRepresentSameInstant("2026-10-18T01:21:20.8629+00:00", "2026-10-18T01:21:20.862900Z")).toBe(false);
    expect(projectTimestampsRepresentSameInstant("not-a-time", "2026-10-18T01:21:20Z")).toBe(false);
  });

  it("validates closed Project learning candidates, empty history, and bounded completion", () => {
    expect(projectSubmissionCandidateIsSafe(submissionCandidate, learningProject, snapshot.snapshot_id)).toBe(true);
    expect(projectSubmissionCandidateIsSafe(variedSubmissionCandidate, learningProject, snapshot.snapshot_id)).toBe(true);
    expect(projectSubmissionCandidateIsSafe({
      ...variedSubmissionCandidate,
      resources: [...variedSubmissionCandidate.resources, { resource_kind: "domain_resource", resource_id: "market-observation", resource_as_of: "2026-10-16T20:00:00Z", record_digest: "c".repeat(64), owner_reference_digest: "d".repeat(64) }],
    }, learningProject, snapshot.snapshot_id)).toBe(true);
    expect(projectCompletionHistoryIsSafe(emptyHistory, learningProject.project_id)).toBe(true);
    expect(projectActivityCompletionIsSafe(emptyCompletion, learningProject.project_id)).toBe(true);
    const { projection_version: _projectionVersion, ...missingProjectionVersion } = emptyCompletion;
    expect(projectActivityCompletionIsSafe(missingProjectionVersion, learningProject.project_id)).toBe(false);
    expect(projectSubmissionCandidateIsSafe({ ...submissionCandidate, private_path: "hidden" }, learningProject, snapshot.snapshot_id)).toBe(false);
    expect(projectSubmissionCandidateIsSafe({ ...submissionCandidate, resources: [submissionCandidate.resources[0], submissionCandidate.resources[0]] }, learningProject, snapshot.snapshot_id)).toBe(false);
    expect(projectActivityCompletionIsSafe({ ...emptyCompletion, completed: true }, learningProject.project_id)).toBe(false);
  });

  it("accepts only one exact Project learning selector", () => {
    expect(projectLearningSelection("http://localhost/projects/project-learning/learning")).toEqual({ mode: "overview" });
    expect(projectLearningSelection("http://localhost/projects/project-learning/learning?snapshot=snapshot-one")).toEqual({ mode: "snapshot", snapshotId: "snapshot-one" });
    expect(projectLearningSelection("http://localhost/projects/project-learning/learning?submission=submission-one")).toEqual({ mode: "submission", submissionId: "submission-one" });
    expect(projectLearningSelection("http://localhost/projects/project-learning/learning?snapshot=snapshot-one&submission=submission-one")).toBeNull();
    expect(projectLearningSelection("http://localhost/projects/project-learning/learning?owner=learner-a")).toBeNull();
  });

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
    ["credential-bearing source address", { ...workspace, references: [{ ...workspace.references[0], url: "https://user:secret@example.test" }] }],
  ])("rejects %s as a complete workspace", (_label, value) => {
    expect(projectWorkspaceIsSafe(value, project)).toBe(false);
  });

  it.each(["../evidence.txt", "notes//evidence.txt", "notes/COM¹.txt", "notes/evidence.", "notes/e\u0301vidence.txt"])(
    "rejects noncanonical artifact path %s",
    (logicalPath) => {
      const invalidArtifact = {
        artifact_id: "artifact-one",
        artifact_version: 1,
        artifact_kind: "supporting_file",
        logical_path: logicalPath,
        media_type: "text/plain",
        inspection_mode: "plain_text",
        byte_count: 8,
        content_digest: "e".repeat(64),
        provenance: { source_type: "learner_created", source_title: "Evidence" },
        assumptions: [],
        created_at: workspace.created_at,
      };
      expect(projectWorkspaceIsSafe({ ...workspace, artifacts: [invalidArtifact] }, project)).toBe(false);
    },
  );

  it("enforces artifact inspection, classification, and provenance semantics on responses", () => {
    const baseArtifact = {
      artifact_id: "artifact-one", artifact_version: 1, artifact_kind: "supporting_file", logical_path: "evidence.json",
      media_type: "application/json", inspection_mode: "metadata_only", byte_count: 2, content_digest: "e".repeat(64),
      provenance: { source_type: "learner_created", source_title: "Evidence" }, assumptions: [], created_at: workspace.created_at,
    };
    expect(projectWorkspaceIsSafe({ ...workspace, artifacts: [baseArtifact] }, project)).toBe(true);
    expect(projectWorkspaceIsSafe({ ...workspace, artifacts: [{ ...baseArtifact, inspection_mode: "plain_text" }] }, project)).toBe(false);
    expect(projectWorkspaceIsSafe({ ...workspace, artifacts: [{ ...baseArtifact, artifact_kind: "result" }] }, project)).toBe(false);
    expect(projectWorkspaceIsSafe({ ...workspace, artifacts: [{ ...baseArtifact, result_classification: "predicted" }] }, project)).toBe(false);
    expect(projectWorkspaceIsSafe({ ...workspace, artifacts: [{ ...baseArtifact, provenance: { source_type: "external", source_title: "Evidence" } }] }, project)).toBe(false);
  });

  it("rejects repeated artifact identities and case-folded logical path aliases", () => {
    const baseArtifact: ProjectArtifact = {
      artifact_id: "artifact-one", artifact_version: 1, artifact_kind: "supporting_file", logical_path: "Data/Foo.csv",
      media_type: "text/csv", inspection_mode: "plain_text", byte_count: 2, content_digest: "e".repeat(64),
      provenance: { source_type: "learner_created", source_title: "Evidence" }, assumptions: [], created_at: workspace.created_at,
    };
    expect(projectWorkspaceIsSafe({
      ...workspace,
      artifacts: [baseArtifact, { ...baseArtifact, artifact_version: 2, logical_path: "Data/Bar.csv" }],
    }, project)).toBe(false);
    expect(projectWorkspaceIsSafe({
      ...workspace,
      artifacts: [baseArtifact, { ...baseArtifact, artifact_id: "artifact-two", logical_path: "data/foo.csv" }],
    }, project)).toBe(false);
    expect(projectWorkspaceIsSafe({
      ...workspace,
      artifacts: [
        { ...baseArtifact, logical_path: "Data/Straße.csv" },
        { ...baseArtifact, artifact_id: "artifact-two", logical_path: "data/STRASSE.csv" },
      ],
    }, project)).toBe(false);
    expect(projectWorkspaceIsSafe({
      ...workspace,
      artifacts: [
        { ...baseArtifact, logical_path: "data/ı.csv" },
        { ...baseArtifact, artifact_id: "artifact-two", logical_path: "data/i.csv" },
      ],
    }, project)).toBe(true);
  });

  it("rejects a snapshot list that is duplicated, uncorrelated, or technically extended", () => {
    expect(projectSnapshotListIsSafe({ records: [snapshot, snapshot] }, project)).toBe(false);
    expect(projectSnapshotListIsSafe({ records: [{ ...snapshot, snapshot: { ...snapshot.snapshot, learner_id: "learner-other" } }] }, project)).toBe(false);
    expect(projectSnapshotListIsSafe({ records: [{ ...snapshot, storage_path: "private" }] }, project)).toBe(false);
  });
});

describe("Project generated-client loaders and action", () => {
  it("opens an exact learning checkpoint with generated public clients", async () => {
    const get = vi.fn()
      .mockResolvedValueOnce(response(200, learningProject))
      .mockResolvedValueOnce(response(200, emptyCompletion))
      .mockResolvedValueOnce(response(200, submissionCandidate));
    const loader = createProjectLearningLoader({ GET: get } as unknown as FinancialAcademyApiClient, session());
    const result = await loader({
      request: new Request(`http://localhost/projects/${learningProject.project_id}/learning?snapshot=${snapshot.snapshot_id}`),
      params: { projectId: learningProject.project_id },
    } as never);

    expect(result).toEqual(expect.objectContaining({ status: "ready", candidate: submissionCandidate, selection: { mode: "snapshot", snapshotId: snapshot.snapshot_id } }));
    expect(get).toHaveBeenCalledWith("/api/v1/projects/{project_id}/completion", expect.objectContaining({ params: { path: { project_id: learningProject.project_id } } }));
  });

  it("rejects ambiguous learning selectors before session or API work", async () => {
    const selectedSession = session();
    const get = vi.fn();
    const loader = createProjectLearningLoader({ GET: get } as unknown as FinancialAcademyApiClient, selectedSession);
    const result = await loader({
      request: new Request(`http://localhost/projects/${learningProject.project_id}/learning?snapshot=${snapshot.snapshot_id}&submission=submission-one`),
      params: { projectId: learningProject.project_id },
    } as never);
    expect(result).toEqual({ status: "invalid-selection" });
    expect(selectedSession.ensure).not.toHaveBeenCalled();
    expect(get).not.toHaveBeenCalled();
  });

  it.each([
    ["overview", ""],
    ["snapshot", `?snapshot=${snapshot.snapshot_id}`],
    ["submission", "?submission=submission-one"],
  ])("denies every independent Project learning %s before loading completion data", async (_mode, query) => {
    const get = vi.fn().mockResolvedValueOnce(response(200, project));
    const loader = createProjectLearningLoader({ GET: get } as unknown as FinancialAcademyApiClient, session());
    const result = await loader({
      request: new Request(`http://localhost/projects/${project.project_id}/learning${query}`),
      params: { projectId: project.project_id },
    } as never);

    expect(result).toEqual({ status: "not-found" });
    expect(get).toHaveBeenCalledOnce();
    expect(get).toHaveBeenCalledWith("/api/v1/projects/{project_id}", expect.anything());
  });

  it("accepts several retained submissions and rejects a safe but uncorrelated completion history", async () => {
    const first = {
      event_id: "event-one", evidence_id: "evidence-one", submission_id: "submission-one",
      snapshot_id: snapshot.snapshot_id, snapshot_digest: snapshot.snapshot_digest,
      brief_id: origin.brief_id, brief_version: origin.brief_version, brief_digest: origin.brief_digest,
      placement_id: origin.placement_id, placement_version: origin.placement_version, placement_digest: origin.placement_digest,
      policy_id: "assessment-project-closure" as const, policy_version: "1.0.0" as const,
      milestone_ids: ["milestone-one"], request_fingerprint: "1".repeat(64), occurrence: 1,
      accepted_sequence: 1, submitted_at: snapshot.closed_at, occurred_at: snapshot.closed_at,
    };
    const second = {
      ...first, event_id: "event-two", evidence_id: "evidence-two", submission_id: "submission-two",
      request_fingerprint: "2".repeat(64), occurrence: 2, accepted_sequence: 2,
      submitted_at: "2026-10-18T01:21:20.862900Z", occurred_at: "2026-10-18T01:21:20.862900Z",
      supersedes_submission_id: "submission-one",
    };
    const completion = {
      ...emptyCompletion, completed: true, completion_meaning: "bounded_project_activity_completed" as const,
      history: [first, second],
    };
    const history = {
      schema_version: "1.0.0" as const, project_id: learningProject.project_id,
      items: [
        {
          evidence_id: first.evidence_id, submission_id: first.submission_id, snapshot_id: first.snapshot_id,
          snapshot_digest: first.snapshot_digest, request_fingerprint: first.request_fingerprint,
          occurrence: first.occurrence, submitted_at: first.submitted_at,
        },
        {
          evidence_id: second.evidence_id, submission_id: second.submission_id, snapshot_id: second.snapshot_id,
          snapshot_digest: second.snapshot_digest, request_fingerprint: second.request_fingerprint,
          occurrence: second.occurrence, submitted_at: "2026-10-18T01:21:20.8629Z",
          supersedes_submission_id: second.supersedes_submission_id,
        },
      ],
    };
    const get = vi.fn()
      .mockResolvedValueOnce(response(200, learningProject))
      .mockResolvedValueOnce(response(200, completion))
      .mockResolvedValueOnce(response(200, history));
    const loader = createProjectLearningLoader({ GET: get } as unknown as FinancialAcademyApiClient, session());
    const request = { request: new Request(`http://localhost/projects/${learningProject.project_id}/learning`), params: { projectId: learningProject.project_id } } as never;

    expect(await loader(request)).toEqual(expect.objectContaining({ status: "ready", history }));

    get.mockReset();
    get.mockResolvedValueOnce(response(200, learningProject))
      .mockResolvedValueOnce(response(200, completion))
      .mockResolvedValueOnce(response(200, { ...history, items: [history.items[0], { ...history.items[1], submitted_at: "2026-10-18T01:21:20.862901Z" }] }));
    expect(await loader(request)).toEqual({ status: "invalid-response" });
  });

  it("reopens the candidate and submits only candidate-owned evidence", async () => {
    const evidence = {
      schema_version: "1.0.0", evidence_id: "evidence-one", learner_id: "learner-a", submission_id: "submission-one",
      project_id: learningProject.project_id, snapshot_id: snapshot.snapshot_id, snapshot_digest: snapshot.snapshot_digest,
      brief_id: origin.brief_id, brief_version: origin.brief_version, brief_digest: origin.brief_digest,
      placement_id: origin.placement_id, placement_version: origin.placement_version, placement_digest: origin.placement_digest,
      policy_id: "assessment-project-closure", policy_version: "1.0.0",
      milestone_evidence: [
        { milestone_id: "milestone-one", resources: [variedSubmissionCandidate.resources[0]] },
        { milestone_id: "milestone-two", resources: [variedSubmissionCandidate.resources[1]] },
      ], milestone_ids: ["milestone-one", "milestone-two"],
      request_fingerprint: "f".repeat(64), occurrence: 1, accepted_sequence: 1, submitted_at: snapshot.closed_at,
    };
    const outcome = { validation: { schema_version: "1.0.0", status: "accepted", request_fingerprint: "f".repeat(64), issues: [] }, evidence };
    const get = vi.fn().mockResolvedValueOnce(response(200, learningProject)).mockResolvedValueOnce(response(200, variedSubmissionCandidate));
    const post = vi.fn().mockResolvedValue(response(200, outcome));
    const action = createProjectLearningAction({ GET: get, POST: post } as unknown as FinancialAcademyApiClient, session());
    const form = new FormData();
    form.set("submission_id", "submission-one");
    form.append("selection", "milestone-one:0");
    form.append("selection", "milestone-two:1");
    const result = await action({
      request: new Request(`http://localhost/projects/${learningProject.project_id}/learning?snapshot=${snapshot.snapshot_id}`, { method: "POST", body: form }),
      params: { projectId: learningProject.project_id },
    } as never);

    expect(result).toBeInstanceOf(Response);
    expect((result as Response).headers.get("location")).toBe(`/projects/${learningProject.project_id}/learning?submission=submission-one`);
    const body = post.mock.calls[0]?.[1]?.body as Record<string, unknown>;
    expect(body).not.toHaveProperty("learner_id");
    expect(body).toEqual(expect.objectContaining({
      submission_id: "submission-one",
      milestone_evidence: [
        { milestone_id: "milestone-one", resources: [variedSubmissionCandidate.resources[0]] },
        { milestone_id: "milestone-two", resources: [variedSubmissionCandidate.resources[1]] },
      ],
    }));
  });

  it("retains the exact request and choices after a refused submission", async () => {
    const get = vi.fn().mockResolvedValueOnce(response(200, learningProject)).mockResolvedValueOnce(response(200, submissionCandidate));
    const post = vi.fn().mockResolvedValue(response(200, {
      validation: { schema_version: "1.0.0", status: "refused", issues: [{ code: "assessment.project.missing_milestone", reference: "milestone-one", message: "Add evidence for this milestone." }] },
      evidence: null,
    }));
    const action = createProjectLearningAction({ GET: get, POST: post } as unknown as FinancialAcademyApiClient, session());
    const form = new FormData();
    form.set("submission_id", "submission-one"); form.append("selection", "milestone-one:0");
    const result = await action({ request: new Request(`http://localhost/projects/${learningProject.project_id}/learning?snapshot=${snapshot.snapshot_id}`, { method: "POST", body: form }), params: { projectId: learningProject.project_id } } as never);
    expect(result).toEqual(expect.objectContaining({ status: "error", kind: "refused", submissionId: "submission-one", selections: ["milestone-one:0"] }));
  });

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

  it("rejects source credentials before calling the workspace API", async () => {
    const selectedSession = session();
    const post = vi.fn();
    const action = createProjectWorkspaceAction({ POST: post } as unknown as FinancialAcademyApiClient, selectedSession);
    const form = new FormData();
    form.set("intent", "add-reference");
    form.set("idempotency_key", "11111111-1111-4111-8111-111111111111");
    form.set("expected_workspace_revision", "3");
    form.set("title", "Unsafe source");
    form.set("url", "https://user:secret@example.test/research");
    form.set("source_name", "Example publisher");

    expect(await action({ request: new Request(`http://localhost/projects/${project.project_id}`, { method: "POST", body: form }), params: { projectId: project.project_id } } as never)).toEqual({ status: "error", kind: "invalid-input", intent: "reference", idempotencyKey: "11111111-1111-4111-8111-111111111111" });
    expect(selectedSession.ensure).toHaveBeenCalledOnce();
    expect(post).not.toHaveBeenCalled();
  });

  it("submits non-text files as metadata-only and enforces artifact evidence combinations", async () => {
    const selectedSession = session();
    const post = vi.fn().mockResolvedValue(response(200, workspace));
    const action = createProjectWorkspaceAction({ POST: post } as unknown as FinancialAcademyApiClient, selectedSession);
    const form = formDataStub({
      intent: "add-artifact", idempotency_key: "11111111-1111-4111-8111-111111111111", expected_workspace_revision: "3",
      file: { name: "result.json", size: 2, arrayBuffer: async () => new TextEncoder().encode("{}").buffer }, artifact_kind: "result", result_classification: "simulated",
      source_type: "external", source_title: "Reviewed dataset", source_version: "2026.10", media_type: "application/json", assumptions: "Synthetic values",
    });

    const request = { formData: async () => form, signal: new AbortController().signal };
    const result = await action({ request, params: { projectId: project.project_id } } as never);

    expect(result).toEqual(expect.objectContaining({ status: 302 }));
    const submitted = post.mock.calls[0]?.[1]?.body as { intent: { mutation: { artifact: Record<string, unknown> } } };
    expect(submitted.intent.mutation.artifact).toEqual(expect.objectContaining({ inspection_mode: "metadata_only", result_classification: "simulated" }));

    for (const [kind, resultClass, sourceType, sourceVersion] of [
      ["result", "", "learner_created", ""],
      ["dataset", "predicted", "learner_created", ""],
      ["dataset", "", "supplied", ""],
    ] as const) {
      const invalid = formDataStub({
        intent: "add-artifact", idempotency_key: "22222222-2222-4222-8222-222222222222", expected_workspace_revision: "3",
        file: { name: "evidence.txt", size: 1, arrayBuffer: async () => new TextEncoder().encode("x").buffer }, artifact_kind: kind, result_classification: resultClass,
        source_type: sourceType, source_title: "Evidence", source_version: sourceVersion, media_type: "text/plain", assumptions: "",
      });
      expect(await action({ request: { formData: async () => invalid, signal: new AbortController().signal }, params: { projectId: project.project_id } } as never)).toEqual(expect.objectContaining({ status: "error", kind: "invalid-input", intent: "artifact" }));
    }
    expect(post).toHaveBeenCalledTimes(1);
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
    const bundle = await exportBundle();
    const get = vi.fn().mockResolvedValue(response(200, bundle));
    const exportSnapshot = createProjectSnapshotExporter({ GET: get } as unknown as FinancialAcademyApiClient, session());

    const exported = await exportSnapshot(project.project_id, snapshot.snapshot_id);
    expect(exported).toEqual(expect.objectContaining({ status: "ready", fileName: `${project.project_id}-${snapshot.snapshot_id}-evidence.json` }));
    get.mockResolvedValueOnce(response(200, { ...bundle, private_storage_path: "hidden" }));
    expect(await exportSnapshot(project.project_id, snapshot.snapshot_id)).toEqual({ status: "invalid-response" });
  });

  it("rejects substituted evidence and artifact metadata even when outer digests are updated", async () => {
    const bytes = new TextEncoder().encode("evidence");
    const contentDigest = [...new Uint8Array(await crypto.subtle.digest("SHA-256", bytes))].map((item) => item.toString(16).padStart(2, "0")).join("");
    const artifact: ProjectArtifact = { artifact_id: "artifact-one", artifact_version: 1, artifact_kind: "supporting_file", logical_path: "notes/evidence.txt", media_type: "text/plain", inspection_mode: "plain_text", byte_count: bytes.byteLength, content_digest: contentDigest, provenance: { source_type: "learner_created", source_title: "Evidence" }, assumptions: [], created_at: workspace.created_at };
    const valid = await exportBundle({ ...workspace, artifacts: [artifact] }, new Map([[artifact.artifact_id, bytes]]));
    const substitutedMaterial = {
      ...valid.manifest.export,
      workspace_record: {
        ...valid.manifest.export.workspace_record,
        notes: valid.manifest.export.workspace_record.notes.map((note, index) => index === 0 ? { ...note, body: "Substituted evidence" } : note),
      },
    };
    const substituted = { ...valid, manifest: { ...valid.manifest, export: substitutedMaterial, export_digest: await canonicalDigest(substitutedMaterial) } };
    const get = vi.fn().mockResolvedValue(response(200, substituted));
    const exportSnapshot = createProjectSnapshotExporter({ GET: get } as unknown as FinancialAcademyApiClient, session());
    expect(await exportSnapshot(project.project_id, snapshot.snapshot_id)).toEqual({ status: "invalid-response" });

    const changedFileMaterial = {
      ...valid.manifest.export,
      artifact_files: valid.manifest.export.artifact_files.map((file, index) => index === 0 ? { ...file, logical_path: "notes/other.txt" } : file),
    };
    const changedFile = {
      manifest: { ...valid.manifest, export: changedFileMaterial, export_digest: await canonicalDigest(changedFileMaterial) },
      files: valid.files.map((file, index) => index === 0 ? { ...file, logical_path: "notes/other.txt" } : file),
    };
    get.mockResolvedValueOnce(response(200, changedFile));
    expect(await exportSnapshot(project.project_id, snapshot.snapshot_id)).toEqual({ status: "invalid-response" });
  });

  it("rejects changed excluded-artifact snapshot facts even when all outer digests are updated", async () => {
    const artifact: ProjectArtifact = {
      artifact_id: "artifact-one", artifact_version: 1, artifact_kind: "supporting_file", logical_path: "notes/evidence.txt",
      media_type: "text/plain", inspection_mode: "plain_text", byte_count: 8, content_digest: "e".repeat(64),
      provenance: { source_type: "learner_created", source_title: "Evidence" }, assumptions: [], created_at: workspace.created_at,
    };
    const valid = await exportBundle({ ...workspace, artifacts: [artifact] });
    const changedSnapshotMaterial = {
      ...valid.manifest.export.snapshot_record.snapshot,
      artifacts: valid.manifest.export.snapshot_record.snapshot.artifacts.map((reference, index) => index === 0
        ? { ...reference, byte_count: reference.byte_count + 1, content_digest: "f".repeat(64) }
        : reference),
    };
    const changedSnapshotRecord = {
      ...valid.manifest.export.snapshot_record,
      snapshot: changedSnapshotMaterial,
      snapshot_digest: await canonicalDigest(changedSnapshotMaterial),
    };
    const changedMaterial = {
      ...valid.manifest.export,
      snapshot_digest: changedSnapshotRecord.snapshot_digest,
      snapshot_record: changedSnapshotRecord,
    };
    const changed = {
      ...valid,
      manifest: { ...valid.manifest, export: changedMaterial, export_digest: await canonicalDigest(changedMaterial) },
    };
    const get = vi.fn().mockResolvedValue(response(200, changed));
    const exportSnapshot = createProjectSnapshotExporter({ GET: get } as unknown as FinancialAcademyApiClient, session());

    expect(valid.manifest.export.excluded_artifacts).toHaveLength(1);
    expect(await exportSnapshot(project.project_id, snapshot.snapshot_id)).toEqual({ status: "invalid-response" });
  });
});

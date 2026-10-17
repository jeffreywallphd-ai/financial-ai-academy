import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useState } from "react";
import { createMemoryRouter, MemoryRouter, RouterProvider } from "react-router";
import { describe, expect, it } from "vitest";

import { ProjectCreatePage } from "../../src/features/project-workspace/ProjectCreatePage";
import { ProjectDetailPage } from "../../src/features/project-workspace/ProjectDetailPage";
import { ProjectListPage } from "../../src/features/project-workspace/ProjectListPage";
import { ProjectSubmissionPage } from "../../src/features/project-workspace/ProjectSubmissionPage";
import type { LearningProjectStartOption, ProjectActivityCompletion, ProjectCompletionEvidence, ProjectCompletionHistory, ProjectShell, ProjectSnapshot, ProjectSubmissionCandidate, ProjectWorkspace } from "../../src/features/project-workspace/model";

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
const option: LearningProjectStartOption = { title: origin.brief_title, purpose: origin.brief_purpose, origin };
const project: ProjectShell = {
  schema_version: "1.0.0",
  project_id: "project-alpha",
  learner_id: "learner-a",
  title: "My comparison",
  charter: "Compare evidence without making an investment recommendation.",
  origin,
  lifecycle: "active",
  revision: 1,
  created_at: "2026-10-16T20:00:00Z",
  updated_at: "2026-10-16T20:00:00Z",
};
const workspace: ProjectWorkspace = {
  schema_version: "1.0.0",
  project_id: project.project_id,
  learner_id: project.learner_id,
  workspace_revision: 1,
  notes: [],
  references: [],
  artifacts: [],
  domain_links: [],
  created_at: "2026-10-16T20:00:00Z",
  updated_at: "2026-10-16T20:00:00Z",
};
const downloadArtifact = async () => ({ status: "unavailable" as const });
const exportSnapshot = async () => ({ status: "unavailable" as const });
const submissionCandidate: ProjectSubmissionCandidate = {
  schema_version: "1.0.0",
  project: { project_id: project.project_id, project_revision: 1, project_shell_digest: "e".repeat(64), snapshot_id: "snapshot-one", snapshot_digest: "f".repeat(64), workspace_revision: 1, closed_at: workspace.updated_at },
  origin: {
    package_id: origin.package_id, package_version: origin.package_version, package_digest: origin.package_digest,
    brief_id: origin.brief_id, brief_version: origin.brief_version, brief_digest: origin.brief_digest,
    curriculum_id: origin.curriculum_id, curriculum_version: origin.curriculum_version, curriculum_digest: origin.curriculum_digest,
    placement_id: origin.placement_id, placement_version: origin.placement_version, placement_digest: origin.placement_digest,
  },
  policy_id: "assessment-project-closure", policy_version: "1.0.0",
  milestones: [{ milestone_id: "milestone-one", milestone_version: "1.0.0", sequence: 1, title: "Compare the evidence" }],
  resources: [{ resource_kind: "note", resource_id: "note-one", resource_version: 1, record_digest: "a".repeat(64) }],
};
const variedSubmissionCandidate: ProjectSubmissionCandidate = {
  ...submissionCandidate,
  milestones: [
    submissionCandidate.milestones[0]!,
    { milestone_id: "milestone-two", milestone_version: "1.0.0", sequence: 2, title: "Explain the comparison" },
  ],
  resources: [
    submissionCandidate.resources[0]!,
    { resource_kind: "source", resource_id: "source-one", resource_version: 3, record_digest: "b".repeat(64) },
    { resource_kind: "artifact", resource_id: "artifact-one", resource_version: 2, record_digest: "c".repeat(64), content_digest: "d".repeat(64), byte_count: 256 },
    { resource_kind: "domain_resource", resource_id: "observation-one", resource_as_of: workspace.updated_at, record_digest: "e".repeat(64), owner_reference_digest: "f".repeat(64) },
  ],
};
const submissionHistory: ProjectCompletionHistory = { schema_version: "1.0.0", project_id: project.project_id, items: [] };
const projectCompletion: ProjectActivityCompletion = { projection_version: "1.0.0", project_id: project.project_id, completed: false, completion_meaning: "not_completed", source_digest: "b".repeat(64), rebuilt_at: workspace.updated_at, history: [] };

describe("Project learner pages", () => {
  it("presents a checkpoint as plain-language, keyboard-reachable milestone choices", async () => {
    const submissions: FormData[] = [];
    const router = createMemoryRouter([{ path: "/projects/:projectId/learning", action: async ({ request }) => { submissions.push(await request.formData()); return null; }, element: <ProjectSubmissionPage actionState={undefined} busy={false} candidate={variedSubmissionCandidate} completion={projectCompletion} evidence={undefined} history={submissionHistory} project={project} selection={{ mode: "snapshot", snapshotId: "snapshot-one" }} submissionId="submission-one" /> }], { initialEntries: [`/projects/${project.project_id}/learning?snapshot=snapshot-one`] });
    render(<RouterProvider router={router} />);
    const user = userEvent.setup();

    expect(screen.getByRole("heading", { level: 2, name: "Choose evidence for each milestone" })).toBeVisible();
    expect(screen.getByRole("group", { name: /Compare the evidence/ })).toBeVisible();
    expect(document.body.textContent).not.toMatch(/idempotency|database|object storage/i);
    await user.click(screen.getAllByLabelText("Saved note note-one — version 1")[0]!);
    await user.click(screen.getAllByLabelText("Saved source source-one — version 3")[1]!);
    await user.click(screen.getByRole("button", { name: "Submit checkpoint" }));
    await waitFor(() => expect(submissions).toHaveLength(1));
    expect(submissions[0]?.get("submission_id")).toBe("submission-one");
    expect(submissions[0]?.getAll("selection")).toEqual(["milestone-one:0", "milestone-two:1"]);
  });

  it("keeps refused choices selected and rotates authority only after a correction", async () => {
    const router = createMemoryRouter([{ path: "/projects/:projectId/learning", element: <ProjectSubmissionPage actionState={{ status: "error", kind: "refused", submissionId: "submission-one", selections: ["milestone-one:0"], issues: [{ code: "assessment.project.missing_milestone", reference: "milestone-one", message: "Add evidence for this milestone." }] }} busy={false} candidate={submissionCandidate} completion={projectCompletion} evidence={undefined} history={submissionHistory} project={project} selection={{ mode: "snapshot", snapshotId: "snapshot-one" }} submissionId="new-submission" /> }], { initialEntries: [`/projects/${project.project_id}/learning?snapshot=snapshot-one`] });
    render(<RouterProvider router={router} />);
    expect(screen.getByRole("heading", { name: "Checkpoint not submitted" })).toHaveFocus();
    expect(screen.getByLabelText("Saved note note-one — version 1")).toBeChecked();
    expect(screen.getByText("Add evidence for this milestone.")).toBeVisible();
    const request = () => document.querySelector<HTMLInputElement>('input[name="submission_id"]')?.value;
    expect(request()).toBe("submission-one");
    await userEvent.setup().click(screen.getByLabelText("Saved note note-one — version 1"));
    expect(request()).not.toBe("submission-one");
  });

  it("keeps uncertain unchanged retries on the same submission authority", async () => {
    const submissions: FormData[] = [];
    const router = createMemoryRouter([{ path: "/projects/:projectId/learning", action: async ({ request }) => { submissions.push(await request.formData()); return null; }, element: <ProjectSubmissionPage actionState={{ status: "error", kind: "unavailable", submissionId: "submission-one", selections: ["milestone-one:0"] }} busy={false} candidate={submissionCandidate} completion={projectCompletion} evidence={undefined} history={submissionHistory} project={project} selection={{ mode: "snapshot", snapshotId: "snapshot-one" }} submissionId="new-submission" /> }], { initialEntries: [`/projects/${project.project_id}/learning?snapshot=snapshot-one`] });
    render(<RouterProvider router={router} />);

    expect(screen.getByLabelText("Saved note note-one — version 1")).toBeChecked();
    expect(document.querySelector<HTMLInputElement>('input[name="submission_id"]')?.value).toBe("submission-one");
    await userEvent.setup().click(screen.getByRole("button", { name: "Submit checkpoint" }));
    await waitFor(() => expect(submissions).toHaveLength(1));
    expect(submissions[0]?.get("submission_id")).toBe("submission-one");
  });

  it("keeps complete safe evidence identity and provenance in progressive disclosure", async () => {
    const evidence: ProjectCompletionEvidence = {
      schema_version: "1.0.0", evidence_id: "evidence-one", learner_id: project.learner_id,
      submission_id: "submission-one", project_id: project.project_id,
      snapshot_id: submissionCandidate.project.snapshot_id, snapshot_digest: submissionCandidate.project.snapshot_digest,
      brief_id: origin.brief_id, brief_version: origin.brief_version, brief_digest: origin.brief_digest,
      placement_id: origin.placement_id, placement_version: origin.placement_version, placement_digest: origin.placement_digest,
      policy_id: "assessment-project-closure", policy_version: "1.0.0",
      milestone_evidence: [{ milestone_id: "milestone-one", resources: variedSubmissionCandidate.resources }],
      milestone_ids: ["milestone-one"], request_fingerprint: "9".repeat(64), occurrence: 2,
      accepted_sequence: 3, supersedes_submission_id: "submission-zero", submitted_at: workspace.updated_at,
    };
    render(<MemoryRouter><ProjectSubmissionPage actionState={undefined} busy={false} candidate={undefined} completion={{ ...projectCompletion, completed: true, completion_meaning: "bounded_project_activity_completed", history: [{
      event_id: "event-one", evidence_id: evidence.evidence_id, submission_id: evidence.submission_id,
      snapshot_id: evidence.snapshot_id, snapshot_digest: evidence.snapshot_digest,
      brief_id: evidence.brief_id, brief_version: evidence.brief_version, brief_digest: evidence.brief_digest,
      placement_id: evidence.placement_id, placement_version: evidence.placement_version, placement_digest: evidence.placement_digest,
      policy_id: evidence.policy_id, policy_version: evidence.policy_version, milestone_ids: evidence.milestone_ids,
      request_fingerprint: evidence.request_fingerprint, occurrence: evidence.occurrence,
      accepted_sequence: evidence.accepted_sequence, supersedes_submission_id: "submission-zero",
      submitted_at: evidence.submitted_at, occurred_at: evidence.submitted_at,
    }] }} evidence={evidence} history={{ schema_version: "1.0.0", project_id: project.project_id, items: [{
      evidence_id: evidence.evidence_id, submission_id: evidence.submission_id, snapshot_id: evidence.snapshot_id,
      snapshot_digest: evidence.snapshot_digest, request_fingerprint: evidence.request_fingerprint,
      occurrence: evidence.occurrence, supersedes_submission_id: "submission-zero", submitted_at: evidence.submitted_at,
    }] }} project={project} selection={{ mode: "submission", submissionId: evidence.submission_id }} submissionId="new-submission" /></MemoryRouter>);
    const user = userEvent.setup();

    await user.click(screen.getAllByText("Technical record").at(-1)!);
    expect(screen.getByText("Saved file artifact-one — version 2")).toBeVisible();
    expect(screen.getByText("Connected record observation-one — as of Oct 16, 2026")).toBeVisible();
    await user.click(screen.getByText("Submission technical record"));
    expect(screen.getAllByText(evidence.snapshot_digest)).not.toHaveLength(0);
    expect(screen.getAllByText(evidence.brief_digest)).not.toHaveLength(0);
    expect(screen.getAllByText(evidence.placement_digest)).not.toHaveLength(0);
    expect(screen.getByText("submission-zero")).toBeVisible();
    for (const disclosure of screen.getAllByText("Technical identity")) await user.click(disclosure);
    expect(screen.getByText("256 bytes")).toBeVisible();
    expect(screen.getAllByText("f".repeat(64))).not.toHaveLength(0);
  });

  it("renders zero or several records without assuming one fixture", () => {
    const { rerender } = render(<MemoryRouter><ProjectListPage options={[]} projects={[]} /></MemoryRouter>);
    expect(screen.getByText("You have not started a Project yet.")).toBeVisible();
    expect(screen.getByText(/No learning-based Project is available/)).toBeVisible();

    rerender(<MemoryRouter><ProjectListPage options={[option]} projects={[project, { ...project, project_id: "project-beta", title: "Unicode café" }]} /></MemoryRouter>);
    expect(screen.getAllByRole("link", { name: "Open project" })).toHaveLength(2);
    expect(screen.getByRole("link", { name: "Start project" })).toHaveAttribute("href", `/projects/new?placement=${origin.placement_id}`);
    expect(screen.getByText("Unicode café")).toBeVisible();
  });

  it("keeps exact provenance in a keyboard-reachable technical record", async () => {
    const user = userEvent.setup();
    const router = createMemoryRouter([{ path: "/projects/:projectId", element: <ProjectDetailPage actionState={undefined} busy={false} downloadArtifact={downloadArtifact} exportSnapshot={exportSnapshot} project={project} snapshots={[]} workspace={workspace} /> }], { initialEntries: [`/projects/${project.project_id}`] });
    render(<RouterProvider router={router} />);
    expect(screen.getByRole("heading", { level: 1, name: project.title })).toBeVisible();
    expect(screen.getByText(origin.brief_title, { exact: true })).toBeVisible();
    expect(screen.getByText(project.project_id)).not.toBeVisible();
    await user.click(screen.getByText("Technical record"));
    expect(screen.getByText(project.project_id)).toBeVisible();
    expect(screen.getByText(origin.placement_digest)).toBeVisible();
    expect(screen.getByText(origin.package_digest)).toBeVisible();
    expect(screen.getByText(origin.curriculum_digest)).toBeVisible();
    expect(screen.getByText(origin.project_brief_schema_version)).toBeVisible();
    expect(document.body.textContent).not.toMatch(/database|object storage|foreign key/i);
  });

  it("shows flexible workspace records, inert file limits, and snapshot continuation in plain language", async () => {
    const user = userEvent.setup();
    const varied: ProjectWorkspace = {
      ...workspace,
      workspace_revision: 7,
      notes: [{ note_id: "note-cafe", note_version: 2, title: "Résumé", body: "Line one\nLine two", created_at: workspace.created_at, updated_at: workspace.updated_at }],
      references: [{ reference_id: "source-one", reference_version: 1, title: "Reviewed source", url: "https://example.test/source", source_name: "Example publisher", created_at: workspace.created_at, updated_at: workspace.updated_at }],
      artifacts: [{ artifact_id: "artifact-one", artifact_version: 1, artifact_kind: "dataset", logical_path: "data/café.csv", media_type: "text/csv", inspection_mode: "plain_text", byte_count: 8, content_digest: "e".repeat(64), provenance: { source_type: "external", source_title: "Learner table", source_url: "https://example.test/data", source_version: "2026.10", source_digest: "c".repeat(64), license: "Research terms", use_constraints: "Educational analysis only" }, environment: { name: "External tool", version: "1.0", dependency_digest: "d".repeat(64) }, assumptions: ["Educational example"], created_at: workspace.created_at }],
      domain_links: [{ link_id: "link-one", link_type: "context", owner_module: "portfolio", resource_type: "simulated_portfolio", resource_id: "portfolio-one", resource_version: "1.0.0", owner_reference_digest: "a".repeat(64), target_status: "available", provenance: "Validated by the owning module.", validated_at: workspace.created_at, created_at: workspace.created_at }],
    };
    const snapshot: ProjectSnapshot = { schema_version: "1.0.0", snapshot_id: "snapshot-one", snapshot_digest: "f".repeat(64), closed_at: workspace.updated_at, snapshot: { project_id: project.project_id, learner_id: project.learner_id, project_revision: 1, project_shell_digest: "a".repeat(64), workspace_revision: 6, workspace_created_at: workspace.created_at, workspace_updated_at: workspace.updated_at, notes: [], references: [], artifacts: [], domain_links: [] } };
    const router = createMemoryRouter([{ path: "/projects/:projectId", element: <ProjectDetailPage actionState={undefined} busy={false} downloadArtifact={downloadArtifact} exportSnapshot={exportSnapshot} project={project} snapshots={[snapshot]} workspace={varied} /> }], { initialEntries: [`/projects/${project.project_id}`] });
    render(<RouterProvider router={router} />);

    expect(screen.getByText("Résumé")).toBeVisible();
    expect(document.querySelector(".project-preserved-text")?.textContent).toBe("Line one\nLine two");
    expect(screen.getByRole("link", { name: "Open source in a new tab" })).toHaveAttribute("href", "https://example.test/source");
    expect(screen.getByRole("button", { name: "Download original file" })).toBeVisible();
    expect(screen.getAllByText(/does not run, expand, or actively preview/i)).not.toHaveLength(0);
    expect(screen.getByText(/It contains 0 notes/)).toBeVisible();
    expect(screen.getByRole("button", { name: "Save checkpoint" })).toBeVisible();

    const filePanel = screen.getByRole("heading", { name: "data/café.csv" }).closest("li")!;
    await user.click(within(filePanel).getByText("Technical record"));
    expect(within(filePanel).getByText("https://example.test/data")).toBeVisible();
    expect(within(filePanel).getByText("Research terms")).toBeVisible();
    expect(within(filePanel).getByText("Educational example")).toBeVisible();
    expect(within(filePanel).getByText(/External tool@1.0/)).toBeVisible();
    const linkPanel = screen.getByRole("heading", { name: "simulated_portfolio" }).closest("li")!;
    await user.click(within(linkPanel).getByText("Technical record"));
    expect(within(linkPanel).getByText("link-one")).toBeVisible();
    expect(within(linkPanel).getByText(/portfolio-one/)).toBeVisible();
  });

  it("rotates checkpoint retry authority when its bound revisions change", async () => {
    const user = userEvent.setup();
    function RevisionHarness() {
      const [revision, setRevision] = useState(1);
      const [retryShown, setRetryShown] = useState(false);
      return <><button onClick={() => setRetryShown(true)} type="button">Show retry</button><button onClick={() => setRevision(2)} type="button">Advance work</button><ProjectDetailPage actionState={retryShown ? { status: "error", kind: "unavailable", intent: "snapshot", idempotencyKey: "previous" } : undefined} busy={false} downloadArtifact={downloadArtifact} exportSnapshot={exportSnapshot} project={project} snapshots={[]} workspace={{ ...workspace, workspace_revision: revision }} /></>;
    }
    const router = createMemoryRouter([{ path: "/projects/:projectId", element: <RevisionHarness /> }], { initialEntries: [`/projects/${project.project_id}`] });
    render(<RouterProvider router={router} />);
    const checkpointForm = () => screen.getByRole("button", { name: "Save checkpoint" }).closest("form")!;
    const keyInput = () => checkpointForm().querySelector<HTMLInputElement>('input[name="idempotency_key"]')!;
    const initial = keyInput().value;

    await user.click(screen.getByRole("button", { name: "Show retry" }));
    expect(keyInput().value).toBe(initial);

    await user.click(screen.getByRole("button", { name: "Advance work" }));
    expect(keyInput().value).not.toBe(initial);
  });

  it("submits one bounded note intent and explains stale work without overwriting it", async () => {
    const submissions: FormData[] = [];
    const router = createMemoryRouter([{ path: "/projects/:projectId", action: async ({ request }) => { const form = await request.formData(); submissions.push(form); return { status: "error" as const, kind: "stale" as const, intent: "note" as const, idempotencyKey: String(form.get("idempotency_key")) }; }, element: <ProjectDetailPage actionState={{ status: "error", kind: "stale", intent: "note", idempotencyKey: "old-key" }} busy={false} downloadArtifact={downloadArtifact} exportSnapshot={exportSnapshot} project={project} snapshots={[]} workspace={workspace} /> }], { initialEntries: [`/projects/${project.project_id}`] });
    render(<RouterProvider router={router} />);
    const user = userEvent.setup();

    expect(screen.getByText(/earlier work is still protected/i)).toBeVisible();
    await user.type(screen.getByLabelText("Note title"), "My note");
    await user.type(screen.getByLabelText("Note"), "A bounded observation.");
    await user.click(screen.getByRole("button", { name: "Save note" }));

    await waitFor(() => expect(submissions).toHaveLength(1));
    expect(submissions[0]?.get("intent")).toBe("add-note");
    expect(submissions[0]?.get("expected_workspace_revision")).toBe("1");
    expect(submissions[0]?.has("learner_id")).toBe(false);
  });

  it("keeps one retry key for unchanged input and replaces it after intent changes", async () => {
    const user = userEvent.setup();
    const firstKey = "11111111-1111-4111-8111-111111111111";
    const router = createMemoryRouter([{ path: "/projects/new", element: <ProjectCreatePage actionState={{ status: "error", kind: "unavailable", idempotencyKey: firstKey }} idempotencyKey={firstKey} option={option} /> }], { initialEntries: ["/projects/new"] });
    const { container } = render(<RouterProvider router={router} />);
    const hidden = container.querySelector<HTMLInputElement>('input[name="idempotency_key"]');
    expect(hidden?.value).toBe(firstKey);
    expect(screen.getByText(/unchanged retry will not create a duplicate/i)).toBeVisible();

    await user.type(screen.getByLabelText(/What do you want/i), "Compare two reviewed sources.");
    expect(hidden?.value).not.toBe(firstKey);
    expect(screen.getByLabelText("Project title")).toHaveValue(option.title);
    expect(document.body.textContent).not.toMatch(/idempotency|placement id|schema/i);
  });

  it("uses a fresh key after the server reports a changed request", () => {
    const previousKey = "11111111-1111-4111-8111-111111111111";
    const router = createMemoryRouter([{ path: "/projects/new", element: <ProjectCreatePage actionState={{ status: "error", kind: "conflict", idempotencyKey: previousKey, draft: { title: "My comparison", charter: "Compare two sources." } }} idempotencyKey={previousKey} option={option} /> }], { initialEntries: ["/projects/new"] });
    const { container } = render(<RouterProvider router={router} />);

    expect(container.querySelector<HTMLInputElement>('input[name="idempotency_key"]')?.value).not.toBe(previousKey);
    expect(screen.getByText(/fresh request/i)).toBeVisible();
  });

  it("keeps material fields fixed while a create request is pending", async () => {
    const user = userEvent.setup();
    let finish!: () => void;
    const action = () => new Promise<null>((resolve) => { finish = () => resolve(null); });
    const router = createMemoryRouter([{ path: "/projects/new", action, element: <ProjectCreatePage actionState={undefined} idempotencyKey="11111111-1111-4111-8111-111111111111" option={null} /> }], { initialEntries: ["/projects/new"] });
    render(<RouterProvider router={router} />);
    await user.type(screen.getByLabelText("Project title"), "Delayed response");
    await user.type(screen.getByLabelText(/What do you want/i), "Keep this exact request fixed.");

    await user.click(screen.getByRole("button", { name: "Create Project" }));

    await waitFor(() => expect(screen.getByLabelText("Project title")).toBeDisabled());
    expect(screen.getByLabelText(/What do you want/i)).toBeDisabled();
    finish();
    await waitFor(() => expect(screen.getByLabelText("Project title")).toBeEnabled());
  });
});

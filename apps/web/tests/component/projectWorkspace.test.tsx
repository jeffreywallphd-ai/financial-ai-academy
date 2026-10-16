import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { createMemoryRouter, MemoryRouter, RouterProvider } from "react-router";
import { describe, expect, it } from "vitest";

import { ProjectCreatePage } from "../../src/features/project-workspace/ProjectCreatePage";
import { ProjectDetailPage } from "../../src/features/project-workspace/ProjectDetailPage";
import { ProjectListPage } from "../../src/features/project-workspace/ProjectListPage";
import type { LearningProjectStartOption, ProjectShell, ProjectSnapshot, ProjectWorkspace } from "../../src/features/project-workspace/model";

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

describe("Project learner pages", () => {
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
    const varied: ProjectWorkspace = {
      ...workspace,
      workspace_revision: 7,
      notes: [{ note_id: "note-cafe", note_version: 2, title: "Résumé", body: "Line one\nLine two", created_at: workspace.created_at, updated_at: workspace.updated_at }],
      references: [{ reference_id: "source-one", reference_version: 1, title: "Reviewed source", url: "https://example.test/source", source_name: "Example publisher", created_at: workspace.created_at, updated_at: workspace.updated_at }],
      artifacts: [{ artifact_id: "artifact-one", artifact_version: 1, artifact_kind: "dataset", logical_path: "data/café.csv", media_type: "text/csv", inspection_mode: "plain_text", byte_count: 8, content_digest: "e".repeat(64), provenance: { source_type: "learner_created", source_title: "Learner table" }, assumptions: ["Educational example"], created_at: workspace.created_at }],
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

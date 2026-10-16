import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { createMemoryRouter, MemoryRouter, RouterProvider } from "react-router";
import { describe, expect, it } from "vitest";

import { ProjectCreatePage } from "../../src/features/project-workspace/ProjectCreatePage";
import { ProjectDetailPage } from "../../src/features/project-workspace/ProjectDetailPage";
import { ProjectListPage } from "../../src/features/project-workspace/ProjectListPage";
import type { LearningProjectStartOption, ProjectShell } from "../../src/features/project-workspace/model";

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
    render(<MemoryRouter><ProjectDetailPage project={project} /></MemoryRouter>);
    expect(screen.getByRole("heading", { level: 1, name: project.title })).toBeVisible();
    expect(screen.getByText(origin.brief_title, { exact: true })).toBeVisible();
    expect(screen.getByText(project.project_id)).not.toBeVisible();
    await user.click(screen.getByText("Technical record"));
    expect(screen.getByText(project.project_id)).toBeVisible();
    expect(screen.getByText(origin.placement_digest)).toBeVisible();
    expect(document.body.textContent).not.toMatch(/database|object storage|foreign key/i);
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
});

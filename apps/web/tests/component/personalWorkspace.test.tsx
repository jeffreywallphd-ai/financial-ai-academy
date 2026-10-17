import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import {
  createMemoryRouter,
  RouterProvider,
} from "react-router";
import { describe, expect, it, vi } from "vitest";

import {
  PersonalWorkspacePage,
  SaveLearningPage,
} from "../../src/features/personal-workspace/PersonalWorkspacePage";
import type {
  PersonalWorkspace,
  PersonalWorkspaceExporter,
  PersonalWorkspaceQueryResult,
  SaveSelection,
  WorkspaceActionState,
  WorkspaceSearchValues,
} from "../../src/features/personal-workspace/model";


const provenance = {
  published_by: "Financial AI Academy",
  published_at: "2026-10-17T10:00:00Z",
  content_reviewed_on: "2026-10-17",
  educational_use_notice: "Educational content only.",
};

const workspace: PersonalWorkspace = {
  schema_version: "1.0.0",
  workspace_id: "workspace-one",
  learner_id: "learner-one",
  revision: 4,
  records: [
    {
      record_kind: "note",
      record_id: "note-one",
      title: "Risk and return",
      body: "Keep risk and possible reward separate from a promise of results.",
      archived: false,
      created_at: "2026-10-17T10:01:00Z",
      updated_at: "2026-10-17T10:01:00Z",
      target: {
        reference_kind: "learning_opportunity",
        owner_module: "curriculum",
        opportunity_id: "risk-return-basics",
        placement_id: "risk-return-primary",
        package_id: "risk-return-package",
        package_version: "1.0.0",
        package_digest: "a".repeat(64),
        source_fingerprint: "b".repeat(64),
        title: "Risk and return basics",
        destination: "/learn/placements/risk-return-primary",
        target_status: "available",
        validated_at: "2026-10-17T10:01:00Z",
        provenance,
      },
    },
    {
      record_kind: "bookmark",
      record_id: "bookmark-one",
      label: null,
      archived: true,
      created_at: "2026-10-17T10:02:00Z",
      updated_at: "2026-10-17T10:03:00Z",
      target: {
        reference_kind: "placed_lesson",
        owner_module: "curriculum",
        placement_id: "cash-flow-primary",
        package_id: "cash-flow-package",
        package_version: "2.0.0",
        package_digest: "c".repeat(64),
        title: "Cash flow basics",
        destination: "/learn/placements/cash-flow-primary",
        target_status: "available",
        validated_at: "2026-10-17T10:02:00Z",
        provenance,
      },
    },
  ],
  collections: [{
    collection_id: "collection-one",
    title: "Foundations",
    member_record_ids: ["bookmark-one", "note-one"],
    created_at: "2026-10-17T10:03:00Z",
    updated_at: "2026-10-17T10:04:00Z",
  }],
  created_at: "2026-10-17T10:00:00Z",
  updated_at: "2026-10-17T10:04:00Z",
  workspace_digest: "d".repeat(64),
};

const projectWorkspace: PersonalWorkspace = {
  ...workspace,
  records: [
    {
      record_kind: "bookmark",
      record_id: "project-workspace-one",
      label: null,
      archived: false,
      created_at: "2026-10-17T13:00:00Z",
      updated_at: "2026-10-17T13:00:00Z",
      target: {
        reference_kind: "project_workspace",
        owner_module: "project",
        project_id: "project.research-1",
        title: "Compare allocation assumptions",
        lifecycle: "active",
        project_revision: 2,
        workspace_revision: 4,
        destination: "/projects/project.research-1#workspace",
        target_status: "available",
        validated_at: "2026-10-17T13:00:00Z",
      },
    },
    {
      record_kind: "bookmark",
      record_id: "project-snapshot-one",
      label: "Baseline checkpoint",
      archived: false,
      created_at: "2026-10-17T13:00:00Z",
      updated_at: "2026-10-17T13:00:00Z",
      target: {
        reference_kind: "project_snapshot",
        owner_module: "project",
        project_id: "project.research-1",
        snapshot_id: "snapshot.baseline-1",
        title: "Compare allocation assumptions",
        lifecycle: "active",
        project_revision: 2,
        workspace_revision: 4,
        snapshot_digest: "e".repeat(64),
        closed_at: "2026-10-17T12:45:00Z",
        destination: "/projects/project.research-1#snapshot-snapshot.baseline-1",
        target_status: "available",
        validated_at: "2026-10-17T13:00:00Z",
      },
    },
    {
      record_kind: "bookmark",
      record_id: "project-artifact-one",
      label: "Allocation inputs",
      archived: false,
      created_at: "2026-10-17T13:00:00Z",
      updated_at: "2026-10-17T13:00:00Z",
      target: {
        reference_kind: "project_artifact",
        owner_module: "project",
        project_id: "project.research-1",
        artifact_id: "artifact.allocation-inputs",
        artifact_version: 3,
        title: "Compare allocation assumptions",
        lifecycle: "active",
        project_revision: 2,
        workspace_revision: 4,
        artifact_kind: "dataset",
        logical_path: "evidence/allocation-inputs.csv",
        media_type: "text/csv",
        inspection_mode: "plain_text",
        byte_count: 1842,
        content_digest: "f".repeat(64),
        created_at: "2026-10-17T12:30:00Z",
        destination: "/projects/project.research-1#artifact-artifact.allocation-inputs-v3",
        target_status: "available",
        validated_at: "2026-10-17T13:00:00Z",
      },
    },
  ],
  collections: [],
  updated_at: "2026-10-17T13:00:00Z",
  workspace_digest: "9".repeat(64),
};

function renderWorkspace(
  submissions: FormData[] = [],
  actionState?: WorkspaceActionState,
  value: PersonalWorkspace = workspace,
  result?: PersonalWorkspaceQueryResult,
  search?: WorkspaceSearchValues,
  exportWorkspace: PersonalWorkspaceExporter = async () => ({ status: "unavailable" }),
) {
  const router = createMemoryRouter([{
    path: "/saved-learning",
    action: async ({ request }) => {
      submissions.push(await request.formData());
      return null;
    },
    element: <PersonalWorkspacePage actionState={actionState} busy={false} exportWorkspace={exportWorkspace} result={result} search={search} workspace={value} />,
  }], { initialEntries: ["/saved-learning"] });
  return render(<RouterProvider router={router} />);
}

describe("Saved learning pages", () => {
  it("downloads only a matching closed export and shows its bounded technical record", async () => {
    const createObjectURL = vi.fn().mockReturnValue("blob:saved-learning");
    const revokeObjectURL = vi.fn();
    const click = vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => undefined);
    Object.defineProperty(URL, "createObjectURL", { configurable: true, value: createObjectURL });
    Object.defineProperty(URL, "revokeObjectURL", { configurable: true, value: revokeObjectURL });
    const exporter = vi.fn<PersonalWorkspaceExporter>().mockResolvedValue({
      status: "ready",
      content: JSON.stringify({ schema_version: "1.0.0" }),
      export: {
        schema_version: "1.0.0",
        generated_at: "2026-10-17T13:01:00Z",
        workspace,
        workspace_digest: workspace.workspace_digest,
      },
      fileName: "saved-learning-export.json",
    });
    renderWorkspace([], undefined, workspace, undefined, undefined, exporter);

    await userEvent.setup().click(screen.getByRole("button", { name: "Download saved learning" }));

    await waitFor(() => expect(exporter).toHaveBeenCalledWith(workspace.revision, workspace.workspace_digest));
    expect(createObjectURL).toHaveBeenCalledWith(expect.any(Blob));
    expect(click).toHaveBeenCalledOnce();
    expect(revokeObjectURL).toHaveBeenCalledWith("blob:saved-learning");
    const status = screen.getByText("Your Saved learning download is ready.").closest('[role="status"]') as HTMLElement;
    expect(status).toHaveTextContent("download is ready");
    await userEvent.setup().click(within(status).getByText("Technical record"));
    expect(screen.getByText("2026-10-17T13:01:00Z")).toBeVisible();
    expect(screen.getAllByText(workspace.workspace_digest)).not.toHaveLength(0);
    click.mockRestore();
  });

  it("does not download a response prepared from a changed workspace", async () => {
    const exporter = vi.fn<PersonalWorkspaceExporter>().mockResolvedValue({ status: "changed" });
    renderWorkspace([], undefined, workspace, undefined, undefined, exporter);

    await userEvent.setup().click(screen.getByRole("button", { name: "Download saved learning" }));

    expect(await screen.findByText(/Refresh this page/)).toBeVisible();
    expect(exporter).toHaveBeenCalledWith(workspace.revision, workspace.workspace_digest);
  });

  it.each([
    ["record-limit", "Saved learning is full", "up to 200"],
    ["collection-limit", "Collection limit reached", "up to 50"],
    ["collection-member-limit", "Collection is full", "up to 100"],
  ] as const)("keeps recovery controls available for %s", (kind, heading, detail) => {
    renderWorkspace([], { status: "error", kind, intent: "workspace-change" });
    expect(screen.getByRole("heading", { name: heading })).toBeVisible();
    expect(screen.getByRole("alert")).toHaveTextContent(detail);
    expect(screen.getAllByText("Remove saved record").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Remove collection").length).toBeGreaterThan(0);
  });

  it("leads with learner meaning and keeps exact facts in keyboard-reachable technical records", async () => {
    renderWorkspace();
    const user = userEvent.setup();

    expect(screen.getByRole("heading", { level: 1, name: "Saved learning" })).toBeVisible();
    expect(screen.getByRole("heading", { level: 3, name: "Risk and return" })).toBeVisible();
    expect(screen.getByText("Bookmark · Archived")).toBeVisible();
    expect(screen.getByRole("link", { name: "Risk and return basics" })).toHaveAttribute("href", "/learn/placements/risk-return-primary");
    expect(document.body.textContent).not.toMatch(/database|foreign key|idempotency/i);

    const note = screen.getByRole("heading", { name: "Risk and return" }).closest("li");
    await user.click(within(note as HTMLElement).getByText("Technical record"));
    expect(within(note as HTMLElement).getByText("risk-return-basics")).toBeVisible();
    expect(within(note as HTMLElement).getByText("a".repeat(64))).toBeVisible();
    expect(within(note as HTMLElement).getByText("curriculum")).toBeVisible();
    expect(within(note as HTMLElement).getByText("available")).toBeVisible();
    expect(within(note as HTMLElement).getByText("Educational content only.")).toBeVisible();
    expect(within(note as HTMLElement).getAllByText("2026-10-17T10:01:00Z", { selector: "time" })).toHaveLength(3);
  });

  it("shows closed search controls and plain source status without hiding exact facts", () => {
    renderWorkspace();
    expect(screen.getByRole("heading", { name: "Find saved learning" })).toBeVisible();
    expect(screen.getByLabelText("Search words")).toBeVisible();
    expect(screen.getByLabelText("Saved item")).toHaveValue("");
    expect(screen.getByLabelText("Source area")).toHaveValue("");
    expect(screen.getByLabelText("Source type")).toHaveValue("");
    expect(screen.getByLabelText("Source status")).toHaveValue("");
    expect(screen.getByLabelText("Saved status")).toHaveValue("");
    expect(screen.getByLabelText("Collection")).toHaveValue("");
    expect(screen.getByLabelText("Order")).toHaveValue("workspace_order");
    expect(screen.getAllByText("Ready to open.")).toHaveLength(2);
    expect(screen.getAllByRole("link", { name: "Open saved source" })).toHaveLength(2);
  });

  it("retains stale and unavailable records but suppresses unsafe resume and partial reorder", async () => {
    const submissions: FormData[] = [];
    const records = projectWorkspace.records.map((record, index) => ({
      ...record,
      target: {
        ...record.target,
        target_status: index === 0 ? "stale" as const : "unavailable" as const,
      },
    }));
    const value: PersonalWorkspace = {
      ...projectWorkspace,
      records,
      revision: 5,
    };
    const result: PersonalWorkspaceQueryResult = {
      schema_version: "1.0.0",
      workspace_revision: 5,
      query_digest: "1".repeat(64),
      applied_query: {
        schema_version: "1.0.0",
        target_statuses: ["stale"],
        sort: "workspace_order",
        limit: 50,
      },
      records: [records[0]!],
      next_cursor: "next_cursor",
    };
    renderWorkspace(
      submissions,
      undefined,
      value,
      result,
      { targetStatus: "stale" },
    );
    const user = userEvent.setup();
    const card = screen.getByRole("heading", {
      name: "Compare allocation assumptions",
    }).closest("li") as HTMLElement;

    expect(within(card).getByText("Saved details changed.")).toBeVisible();
    expect(within(card).queryByRole("link", { name: "Open saved source" })).not.toBeInTheDocument();
    expect(within(card).queryByRole("button", { name: "Move earlier" })).not.toBeInTheDocument();
    expect(within(card).queryByRole("button", { name: "Move later" })).not.toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Show more results" })).toHaveAttribute(
      "href",
      "/saved-learning?status=stale&cursor=next_cursor",
    );

    await user.click(within(card).getByRole("button", { name: "Check source" }));
    await waitFor(() => expect(submissions).toHaveLength(1));
    expect(Object.fromEntries(submissions[0]!.entries())).toEqual(expect.objectContaining({
      operation: "refresh_reference",
      record_id: "project-workspace-one",
      expected_revision: "5",
    }));
    expect(submissions[0]?.has("target_status")).toBe(false);
    expect(submissions[0]?.has("owner_module")).toBe(false);
    expect(submissions[0]?.has("project_id")).toBe(false);
  });

  it("never turns a complete but permuted query page into reorder authority", () => {
    renderWorkspace(
      [],
      undefined,
      workspace,
      {
        schema_version: "1.0.0",
        workspace_revision: workspace.revision,
        query_digest: "1".repeat(64),
        applied_query: {
          schema_version: "1.0.0",
          sort: "workspace_order",
          limit: 50,
        },
        records: [...workspace.records].reverse(),
        next_cursor: null,
      },
    );
    expect(screen.queryByRole("button", { name: "Move earlier" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Move later" })).not.toBeInTheDocument();
  });

  it("explains a valid search with no matching items", () => {
    renderWorkspace(
      [],
      undefined,
      workspace,
      {
        schema_version: "1.0.0",
        workspace_revision: workspace.revision,
        query_digest: "1".repeat(64),
        applied_query: {
          schema_version: "1.0.0",
          text: "missing",
          sort: "workspace_order",
          limit: 50,
        },
        records: [],
        next_cursor: null,
      },
      { text: "missing" },
    );
    expect(screen.getByText(/No saved items match these filters/i)).toBeVisible();
    expect(screen.getByRole("link", { name: "Clear filters" })).toHaveAttribute(
      "href",
      "/saved-learning",
    );
  });

  it("shows every safe Project reference kind without adding Project save controls", async () => {
    renderWorkspace([], undefined, projectWorkspace);
    const user = userEvent.setup();

    for (const heading of [
      "Compare allocation assumptions",
      "Baseline checkpoint",
      "Allocation inputs",
    ]) {
      const record = screen.getByRole("heading", { name: heading }).closest("li");
      await user.click(within(record as HTMLElement).getByText("Technical record"));
    }

    expect(screen.getAllByText("project.research-1")).toHaveLength(3);
    expect(screen.getByText("snapshot.baseline-1")).toBeVisible();
    expect(screen.getByText("e".repeat(64))).toBeVisible();
    expect(screen.getByText("artifact.allocation-inputs")).toBeVisible();
    expect(screen.getByText("evidence/allocation-inputs.csv")).toBeVisible();
    expect(screen.getByText("f".repeat(64))).toBeVisible();
    expect(screen.queryByRole("button", { name: /save project/i })).not.toBeInTheDocument();
  });

  it("applies the existing order, archive, restore, and removal controls to Project records", async () => {
    const submissions: FormData[] = [];
    const value: PersonalWorkspace = {
      ...projectWorkspace,
      records: projectWorkspace.records.map((record, index) => index === 1 ? { ...record, archived: true } : record),
    };
    renderWorkspace(submissions, undefined, value);
    const user = userEvent.setup();
    const workspaceRecord = screen.getByRole("heading", { name: "Compare allocation assumptions" }).closest("li") as HTMLElement;
    const checkpointRecord = screen.getByRole("heading", { name: "Baseline checkpoint" }).closest("li") as HTMLElement;
    const artifactRecord = screen.getByRole("heading", { name: "Allocation inputs" }).closest("li") as HTMLElement;

    await user.click(within(workspaceRecord).getByRole("button", { name: "Archive record" }));
    await user.click(within(checkpointRecord).getByRole("button", { name: "Restore record" }));
    await user.click(within(workspaceRecord).getByRole("button", { name: "Move later" }));
    await user.click(within(artifactRecord).getByText("Remove saved record", { selector: "summary" }));
    await user.click(within(artifactRecord).getByRole("button", { name: "Remove saved record" }));

    await waitFor(() => expect(submissions).toHaveLength(4));
    expect(submissions.map((form) => form.get("operation"))).toEqual([
      "archive_record",
      "restore_record",
      "reorder_records",
      "remove_record",
    ]);
    expect(submissions[2]?.getAll("record_ids")).toEqual([
      "project-snapshot-one",
      "project-workspace-one",
      "project-artifact-one",
    ]);
    expect(submissions[3]?.get("record_id")).toBe("project-artifact-one");
  });

  it("submits current revision, stable request authority, ordered records, and collection membership", async () => {
    const submissions: FormData[] = [];
    renderWorkspace(submissions);
    const user = userEvent.setup();
    const note = screen.getByRole("heading", { name: "Risk and return" }).closest("li");

    const title = within(note as HTMLElement).getByLabelText("Note title");
    await user.clear(title);
    await user.type(title, "Risk notes updated");
    await user.click(within(note as HTMLElement).getByRole("button", { name: "Save note changes" }));
    await waitFor(() => expect(submissions).toHaveLength(1));
    expect(submissions[0]?.get("operation")).toBe("update_note");
    expect(submissions[0]?.get("expected_revision")).toBe("4");
    expect(submissions[0]?.get("record_id")).toBe("note-one");
    expect(submissions[0]?.get("idempotency_key")).toMatch(/^[a-f0-9-]{36}$/);

    await user.click(within(note as HTMLElement).getByRole("button", { name: "Move later" }));
    await waitFor(() => expect(submissions).toHaveLength(2));
    expect(submissions[1]?.getAll("record_ids")).toEqual(["bookmark-one", "note-one"]);

    const collection = screen.getByRole("heading", { name: "Foundations" }).closest("section");
    await user.click(within(collection as HTMLElement).getByRole("button", { name: "Save collection items" }));
    await waitFor(() => expect(submissions).toHaveLength(3));
    expect(submissions[2]?.getAll("member_record_ids")).toEqual(["bookmark-one", "note-one"]);

    await user.click(within(collection as HTMLElement).getByRole("button", { name: "Move Risk and return earlier in collection" }));
    await user.click(within(collection as HTMLElement).getByRole("button", { name: "Save collection items" }));
    await waitFor(() => expect(submissions).toHaveLength(4));
    expect(submissions[3]?.getAll("member_record_ids")).toEqual(["note-one", "bookmark-one"]);
  });

  it("exposes every saved-record and collection change through bounded forms", async () => {
    const submissions: FormData[] = [];
    renderWorkspace(submissions);
    const user = userEvent.setup();
    const note = screen.getByRole("heading", { name: "Risk and return" }).closest("li") as HTMLElement;
    const bookmark = screen.getByRole("heading", { name: "Cash flow basics" }).closest("li") as HTMLElement;
    const collection = screen.getByRole("heading", { name: "Foundations" }).closest("section") as HTMLElement;

    const label = within(bookmark).getByLabelText("Personal label");
    await user.type(label, "Review next week");
    await user.click(within(bookmark).getByRole("button", { name: "Save bookmark changes" }));
    await waitFor(() => expect(submissions).toHaveLength(1));
    expect(Object.fromEntries(submissions[0]!.entries())).toEqual(expect.objectContaining({
      operation: "update_bookmark",
      record_id: "bookmark-one",
      label: "Review next week",
    }));

    await user.click(within(note).getByRole("button", { name: "Archive record" }));
    await user.click(within(bookmark).getByRole("button", { name: "Restore record" }));
    await waitFor(() => expect(submissions).toHaveLength(3));
    expect(submissions[1]?.get("operation")).toBe("archive_record");
    expect(submissions[2]?.get("operation")).toBe("restore_record");

    await user.click(within(note).getByText("Remove saved record", { selector: "summary" }));
    await user.click(within(note).getByRole("button", { name: "Remove saved record" }));
    await waitFor(() => expect(submissions).toHaveLength(4));
    expect(Object.fromEntries(submissions[3]!.entries())).toEqual(expect.objectContaining({
      operation: "remove_record",
      record_id: "note-one",
    }));

    await user.type(screen.getAllByLabelText("Collection name")[0]!, "Next steps");
    await user.click(screen.getByRole("button", { name: "Create collection" }));
    await user.click(screen.getByRole("button", { name: "Create collection" }));
    const existingName = within(collection).getByLabelText("Collection name");
    await user.clear(existingName);
    await user.type(existingName, "Core ideas");
    await user.click(within(collection).getByRole("button", { name: "Rename collection" }));
    await user.click(within(collection).getByText("Remove collection", { selector: "summary" }));
    await user.click(within(collection).getByRole("button", { name: "Remove collection" }));
    await waitFor(() => expect(submissions).toHaveLength(8));
    expect(submissions[4]?.get("idempotency_key")).not.toBe(submissions[5]?.get("idempotency_key"));
    expect(submissions.slice(4).map((form) => form.get("operation"))).toEqual([
      "create_collection",
      "create_collection",
      "rename_collection",
      "remove_collection",
    ]);
  });

  it("explains an empty workspace and destructive boundaries without technical language", () => {
    renderWorkspace([], undefined, { ...workspace, records: [], collections: [], revision: 1 });
    expect(screen.getByText(/not saved any learning yet/i)).toBeVisible();
    expect(screen.getByText(/No collections yet/i)).toBeVisible();
    expect(screen.getByRole("link", { name: "Choose learning to save" })).toHaveAttribute("href", "/learn");
  });

  it("focuses a task-first stale response and preserves a safe next action", () => {
    renderWorkspace([], {
      status: "error",
      kind: "stale",
      intent: "update:note-one",
      preparedRequest: {
        schema_version: "1.0.0",
        idempotency_key: "request-one",
        expected_revision: 3,
        mutation: { operation: "update_note", record_id: "note-one", title: "Risk and return", body: "Old body" },
      },
    });
    expect(screen.getByRole("heading", { name: "Saved learning changed" })).toHaveFocus();
    expect(screen.getByRole("alert")).toHaveTextContent(/Refresh the page/);
  });

  it("creates notes and bookmarks from a fixed lesson selector without learner or source facts", async () => {
    const submissions: FormData[] = [];
    const selection: SaveSelection = { kind: "placed_lesson", placementId: "cash-flow-primary", returnTo: "/learn/placements/cash-flow-primary" };
    const router = createMemoryRouter([{
      path: "/saved-learning/new",
      action: async ({ request }) => {
        submissions.push(await request.formData());
        return null;
      },
      element: <SaveLearningPage busy={false} selection={selection} workspace={workspace} />,
    }], { initialEntries: ["/saved-learning/new"] });
    render(<RouterProvider router={router} />);
    const user = userEvent.setup();

    await user.type(screen.getByLabelText("Note title"), "Cash flow reminder");
    await user.type(screen.getByLabelText("Note", { exact: true }), "Separate cash movement from accounting income.");
    await user.click(screen.getByRole("button", { name: "Save note" }));
    await waitFor(() => expect(submissions).toHaveLength(1));
    expect(Object.fromEntries(submissions[0]!.entries())).toEqual(expect.objectContaining({
      operation: "create_note",
      reference_kind: "placed_lesson",
      placement_id: "cash-flow-primary",
      expected_revision: "4",
    }));
    expect(submissions[0]?.has("learner_id")).toBe(false);
    expect(submissions[0]?.has("package_digest")).toBe(false);

    await user.click(screen.getByRole("button", { name: "Save bookmark" }));
    await waitFor(() => expect(submissions).toHaveLength(2));
    expect(submissions[1]?.get("label")).toBe("");
    expect(screen.getByRole("link", { name: "Return to lesson" })).toHaveAttribute("href", "/learn/placements/cash-flow-primary");
  });

  it.each([
    ["Project", { kind: "project_workspace", projectId: "project.research-1", returnTo: "/projects/project.research-1#workspace" }, { reference_kind: "project_workspace", project_id: "project.research-1" }],
    ["checkpoint", { kind: "project_snapshot", projectId: "project.research-1", snapshotId: "snapshot.baseline-1", returnTo: "/projects/project.research-1#snapshot-snapshot.baseline-1" }, { reference_kind: "project_snapshot", project_id: "project.research-1", snapshot_id: "snapshot.baseline-1" }],
    ["file record", { kind: "project_artifact", projectId: "project.research-1", artifactId: "artifact.allocation-inputs", artifactVersion: 3, returnTo: "/projects/project.research-1#artifact-artifact.allocation-inputs-v3" }, { reference_kind: "project_artifact", project_id: "project.research-1", artifact_id: "artifact.allocation-inputs", artifact_version: "3" }],
  ] as const)("submits the exact %s selector without learner or Project content", async (objectName, selection, expected) => {
    const submissions: FormData[] = [];
    const router = createMemoryRouter([{
      path: "/saved-learning/new",
      action: async ({ request }) => {
        submissions.push(await request.formData());
        return null;
      },
      element: <SaveLearningPage busy={false} selection={selection as SaveSelection} workspace={workspace} />,
    }], { initialEntries: ["/saved-learning/new"] });
    render(<RouterProvider router={router} />);
    const user = userEvent.setup();

    expect(screen.getByRole("heading", { name: `Save this ${objectName}` })).toBeVisible();
    expect(screen.getByRole("link", { name: "Return to Project" })).toHaveAttribute("href", selection.returnTo);
    await user.click(screen.getByRole("button", { name: "Save bookmark" }));
    await waitFor(() => expect(submissions).toHaveLength(1));
    expect(Object.fromEntries(submissions[0]!.entries())).toEqual(expect.objectContaining(expected));
    expect(submissions[0]?.has("learner_id")).toBe(false);
    expect(submissions[0]?.has("project_title")).toBe(false);
    expect(submissions[0]?.has("project_charter")).toBe(false);
  });

  it("retries the complete immutable request after revalidation and uses a fresh request after an edit", async () => {
    const submissions: FormData[] = [];
    const selection: SaveSelection = { kind: "placed_lesson", placementId: "cash-flow-primary", returnTo: "/learn" };
    const actionState: WorkspaceActionState = {
      status: "error",
      kind: "unavailable",
      intent: "create-note",
      preparedRequest: {
        schema_version: "1.0.0",
        idempotency_key: "original-request",
        expected_revision: 4,
        mutation: {
          operation: "create_note",
          selector: { reference_kind: "placed_lesson", placement_id: "cash-flow-primary" },
          title: "Cash flow reminder",
          body: "Track the movement of cash.",
        },
      },
    };
    const router = createMemoryRouter([{
      path: "/saved-learning/new",
      action: async ({ request }) => {
        submissions.push(await request.formData());
        return null;
      },
      element: <SaveLearningPage actionState={actionState} busy={false} selection={selection} workspace={{ ...workspace, revision: 5 }} />,
    }], { initialEntries: ["/saved-learning/new"] });
    render(<RouterProvider router={router} />);
    const user = userEvent.setup();

    await user.click(screen.getByRole("button", { name: "Save note" }));
    await waitFor(() => expect(submissions).toHaveLength(1));
    expect(submissions[0]?.get("idempotency_key")).toBe("original-request");
    expect(submissions[0]?.get("expected_revision")).toBe("4");

    await user.type(screen.getByLabelText("Note", { exact: true }), " More detail.");
    await user.click(screen.getByRole("button", { name: "Save note" }));
    await waitFor(() => expect(submissions).toHaveLength(2));
    expect(submissions[1]?.get("idempotency_key")).not.toBe("original-request");
    expect(submissions[1]?.get("expected_revision")).toBe("5");
  });
});

import { describe, expect, it, vi } from "vitest";

import type { FinancialAcademyApiClient } from "../../src/generated/api-client";
import {
  createPersonalWorkspaceAction,
  createPersonalWorkspaceLoader,
} from "../../src/features/personal-workspace/api";
import {
  parseSaveSelection,
  parseWorkspaceSearch,
  personalWorkspaceIsSafe,
  personalWorkspaceQueriesMatch,
  personalWorkspaceQueryDigest,
  personalWorkspaceQueryResultIsSafe,
  type PersonalWorkspaceQuery,
  workspaceSearchHref,
} from "../../src/features/personal-workspace/model";
import type { SingleProfileSession } from "../../src/platform/auth/singleProfileSession";


const provenance = {
  published_by: "Financial AI Academy",
  published_at: "2026-10-17T10:00:00Z",
  content_reviewed_on: "2026-10-17",
  educational_use_notice: "Educational content only.",
};

const note = {
  record_kind: "note",
  record_id: "note-one",
  title: "Risk and return",
  body: "Remember the relationship between uncertainty and possible outcomes.",
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
};

const bookmark = {
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
};

const projectWorkspaceTarget = {
  reference_kind: "project_workspace",
  owner_module: "project",
  project_id: "project.research-1",
  title: "Allocation research",
  lifecycle: "active",
  project_revision: 4,
  workspace_revision: 7,
  destination: "/projects/project.research-1#workspace",
  target_status: "available",
  validated_at: "2026-10-17T10:03:00Z",
};

const projectSnapshotTarget = {
  ...projectWorkspaceTarget,
  reference_kind: "project_snapshot",
  snapshot_id: "snapshot.baseline-1",
  snapshot_digest: "e".repeat(64),
  closed_at: "2026-10-17T10:02:00Z",
  destination:
    "/projects/project.research-1#snapshot-snapshot.baseline-1",
};

const projectArtifactTarget = {
  ...projectWorkspaceTarget,
  reference_kind: "project_artifact",
  artifact_id: "artifact.inputs-1",
  artifact_version: 3,
  artifact_kind: "dataset",
  logical_path: "evidence/allocation-inputs.csv",
  media_type: "text/csv",
  inspection_mode: "plain_text",
  byte_count: 4096,
  content_digest: "f".repeat(64),
  created_at: "2026-10-17T10:02:00Z",
  destination:
    "/projects/project.research-1#artifact-artifact.inputs-1-v3",
};

const workspace = {
  schema_version: "1.0.0",
  workspace_id: "workspace-one",
  learner_id: "learner-one",
  revision: 4,
  records: [note, bookmark],
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

function workspaceWithTarget(target: Record<string, unknown>) {
  return {
    ...workspace,
    records: [{ ...note, target }],
    collections: [],
  };
}

function queryResult(
  records: readonly unknown[] = workspace.records,
  revision = workspace.revision,
  appliedQuery: PersonalWorkspaceQuery = {
    schema_version: "1.0.0",
    sort: "workspace_order",
    limit: 50,
  },
) {
  return {
    schema_version: "1.0.0",
    workspace_revision: revision,
    query_digest: "1".repeat(64),
    applied_query: appliedQuery,
    records,
    next_cursor: null,
  };
}

async function correlatedQueryResult(
  records: readonly unknown[] = workspace.records,
  revision = workspace.revision,
  appliedQuery: PersonalWorkspaceQuery = {
    schema_version: "1.0.0",
    sort: "workspace_order",
    limit: 50,
  },
) {
  return {
    ...queryResult(records, revision, appliedQuery),
    query_digest: await personalWorkspaceQueryDigest(appliedQuery),
  };
}

function session(): SingleProfileSession {
  return {
    ensure: vi.fn().mockResolvedValue({ status: "ready" }),
    invalidate: vi.fn(),
  } as unknown as SingleProfileSession;
}

function accepted(data: unknown, status = 200) {
  return {
    data: status === 200 ? data : undefined,
    error: status === 200 ? undefined : data,
    response: new Response(null, { status }),
  };
}

describe("Personal workspace browser model", () => {
  it("accepts canonical Unicode boundaries, multiline notes, tabs, and an empty bookmark label", () => {
    expect(personalWorkspaceIsSafe({
      ...workspace,
      records: [
        {
          ...note,
          title: "📈".repeat(120),
          body: `${"📚".repeat(7_990)}\n\tstudy`,
        },
        { ...bookmark, label: "" },
      ],
    })).toBe(true);
  });

  it.each([
    ["Project workspace", projectWorkspaceTarget],
    ["Project snapshot", projectSnapshotTarget],
    ["Project artifact", projectArtifactTarget],
  ])("accepts a closed %s reference returned by the public API", (_name, target) => {
    expect(personalWorkspaceIsSafe(workspaceWithTarget(target))).toBe(true);
  });

  it.each(["stale", "unavailable"] as const)(
    "accepts every closed reference family with %s status",
    (targetStatus) => {
      for (const target of [
        { ...note.target, target_status: targetStatus },
        { ...bookmark.target, target_status: targetStatus },
        { ...projectWorkspaceTarget, target_status: targetStatus },
        { ...projectSnapshotTarget, target_status: targetStatus },
        { ...projectArtifactTarget, target_status: targetStatus },
      ]) {
        expect(personalWorkspaceIsSafe(workspaceWithTarget(target))).toBe(true);
      }
    },
  );

  it("maps one closed browser search into the generated query contract", () => {
    const parsed = parseWorkspaceSearch(new URL(
      "https://academy.test/saved-learning?q=Caf%C3%A9+risk&record=note&source=project&kind=project_artifact&status=stale&archive=active&collection=collection-one&sort=updated_desc&limit=25&cursor=cursor_1",
    ));
    expect(parsed).toEqual({
      search: {
        text: "Café risk",
        recordKind: "note",
        ownerModule: "project",
        referenceKind: "project_artifact",
        targetStatus: "stale",
        archived: "active",
        collectionId: "collection-one",
        limit: 25,
        sort: "updated_desc",
        cursor: "cursor_1",
      },
      query: {
        schema_version: "1.0.0",
        text: "café risk",
        record_kinds: ["note"],
        owner_modules: ["project"],
        reference_kinds: ["project_artifact"],
        target_statuses: ["stale"],
        archived: false,
        collection_id: "collection-one",
        sort: "updated_desc",
        limit: 25,
        cursor: "cursor_1",
      },
    });
    expect(workspaceSearchHref(parsed!.search, "next_cursor")).toBe(
      "/saved-learning?q=Caf%C3%A9+risk&record=note&source=project&kind=project_artifact&status=stale&archive=active&collection=collection-one&sort=updated_desc&limit=25&cursor=next_cursor",
    );
  });

  it.each([
    "owner=learner-one",
    "status=missing",
    "record=note&record=bookmark",
    "limit=0",
    `cursor=${"a".repeat(513)}`,
    `q=${encodeURIComponent("x".repeat(241))}`,
    `q=${encodeURIComponent("\u0085\u001c\u001d\u001e\u001f")}`,
    `q=${encodeURIComponent(" \t\n")}`,
  ])("rejects unsafe browser query %s before session or API access", async (query) => {
    const profile = session();
    const get = vi.fn();
    const post = vi.fn();
    const loader = createPersonalWorkspaceLoader(
      { GET: get, POST: post } as unknown as FinancialAcademyApiClient,
      profile,
    );
    expect(await loader({ request: new Request(`http://localhost/saved-learning?${query}`) } as never)).toEqual({ status: "invalid-query" });
    expect(profile.ensure).not.toHaveBeenCalled();
    expect(get).not.toHaveBeenCalled();
    expect(post).not.toHaveBeenCalled();
  });

  it("closes query results without accepting private, duplicate, or malformed data", () => {
    expect(personalWorkspaceQueryResultIsSafe(queryResult())).toBe(true);
    expect(personalWorkspaceQueryResultIsSafe({ ...queryResult(), actor_id: "private" })).toBe(false);
    expect(personalWorkspaceQueryResultIsSafe(queryResult([note, note]))).toBe(false);
    expect(personalWorkspaceQueryResultIsSafe({
      ...queryResult(),
      next_cursor: "not+a+cursor",
    })).toBe(false);
  });

  it("reproduces canonical query meaning and digest across Unicode normalization", async () => {
    const requested: PersonalWorkspaceQuery = {
      schema_version: "1.0.0",
      text: "  Cafe\u0301   STRAẞE  ",
      record_kinds: ["note", "bookmark"],
      sort: "workspace_order",
      limit: 1,
      cursor: "cursor_1",
    };
    const applied: PersonalWorkspaceQuery = {
      schema_version: "1.0.0",
      text: "café strasse",
      record_kinds: ["bookmark", "note"],
      sort: "workspace_order",
      limit: 1,
      cursor: "cursor_1",
    };
    expect(personalWorkspaceQueriesMatch(requested, applied)).toBe(true);
    expect(await personalWorkspaceQueryDigest({
      schema_version: "1.0.0",
      text: "risk",
      limit: 1,
    })).toBe("f0323a7ae326cc52e2ce9787f0aeebfda5edec9c835fe37d75c247514bfb06e5");
    expect(await personalWorkspaceQueryDigest(requested)).toBe(
      await personalWorkspaceQueryDigest(applied),
    );
    expect(personalWorkspaceQueriesMatch(
      { schema_version: "1.0.0", text: "I ı ſ ꭰ" },
      { schema_version: "1.0.0", text: "i ı s Ꭰ" },
    )).toBe(true);
    for (const whitespace of ["\u0085", "\u001c", "\u001d", "\u001e", "\u001f"]) {
      expect(personalWorkspaceQueriesMatch(
        { schema_version: "1.0.0", text: `risk${whitespace}return` },
        { schema_version: "1.0.0", text: "risk return" },
      )).toBe(true);
    }
    expect(personalWorkspaceQueriesMatch(
      { schema_version: "1.0.0", text: "risk\ufeffreturn" },
      { schema_version: "1.0.0", text: "risk\ufeffreturn" },
    )).toBe(true);
    expect(personalWorkspaceQueriesMatch(
      { schema_version: "1.0.0", text: "risk\ufeffreturn" },
      { schema_version: "1.0.0", text: "risk return" },
    )).toBe(false);
    expect(parseWorkspaceSearch(new URL(
      `https://academy.test/saved-learning?q=${encodeURIComponent("risk\u0085return")}`,
    ))?.query.text).toBe("risk return");
    expect(parseWorkspaceSearch(new URL(
      `https://academy.test/saved-learning?q=${encodeURIComponent("risk\ufeffreturn")}`,
    ))?.query.text).toBe("risk\ufeffreturn");
  });

  it.each([
    ["private Project field", { ...projectWorkspaceTarget, storage_key: "private/object" }],
    ["mismatched Project destination", { ...projectWorkspaceTarget, destination: "/projects/project.other#workspace" }],
    ["invalid snapshot time", { ...projectSnapshotTarget, closed_at: "2026-10-17T10:04:00Z" }],
    ["invalid validation time", { ...projectWorkspaceTarget, validated_at: "2026-10-17T10:03:60Z" }],
    ["noncanonical artifact path", { ...projectArtifactTarget, logical_path: "../secret.csv" }],
    ["invalid artifact time", { ...projectArtifactTarget, created_at: "2026-10-17T10:04:00Z" }],
    ["overlong artifact", { ...projectArtifactTarget, byte_count: 10_485_761 }],
    ["unknown artifact kind", { ...projectArtifactTarget, artifact_kind: "executable" }],
    ["unknown media type", { ...projectArtifactTarget, media_type: "application/x-msdownload" }],
    ["unknown inspection mode", { ...projectArtifactTarget, inspection_mode: "execute" }],
  ])("rejects a %s without accepting a partial Project reference", (_name, target) => {
    expect(personalWorkspaceIsSafe(workspaceWithTarget(target))).toBe(false);
  });

  it.each([
    ["unknown record union", { ...workspace, records: [{ ...note, record_kind: "file" }] }],
    ["missing nullable label", { ...workspace, records: [{ ...bookmark, label: undefined }] }],
    ["unsafe destination", { ...workspace, records: [{ ...note, target: { ...note.target, destination: "https://example.com/lesson" } }] }],
    ["mismatched destination", { ...workspace, records: [{ ...note, target: { ...note.target, destination: "/learn/placements/another-placement" } }] }],
    ["duplicate record", { ...workspace, records: [note, note] }],
    ["dangling collection member", { ...workspace, collections: [{ ...workspace.collections[0], member_record_ids: ["missing"] }] }],
    ["invalid time", { ...workspace, updated_at: "yesterday" }],
    ["invalid calendar date", { ...workspace, records: [{ ...note, target: { ...note.target, provenance: { ...note.target.provenance, content_reviewed_on: "2026-02-31" } } }] }],
    ["invalid digest", { ...workspace, workspace_digest: "not-a-digest" }],
    ["uppercase platform identifier", { ...workspace, workspace_id: "Workspace-one" }],
    ["short curriculum identifier", { ...workspace, records: [{ ...note, target: { ...note.target, placement_id: "x" } }] }],
    ["invalid package version", { ...workspace, records: [{ ...note, target: { ...note.target, package_version: "v1" } }] }],
    ["overlong note title", { ...workspace, records: [{ ...note, title: "a".repeat(121) }] }],
    ["NUL in a note", { ...workspace, records: [{ ...note, body: "before\u0000after" }] }],
    ["unknown workspace property", { ...workspace, extra_fact: true }],
    ["unknown record property", { ...workspace, records: [{ ...note, extra_fact: true }] }],
  ])("rejects %s without accepting a partial view", (_name, candidate) => {
    expect(personalWorkspaceIsSafe(candidate)).toBe(false);
  });

  it("accepts only one bounded opportunity or lesson selector", () => {
    expect(parseSaveSelection(new URL("https://academy.test/saved-learning/new?kind=opportunity&opportunity=risk-return-basics&placement=risk-return-primary&return=%2Flearn%2Fopportunities%2Frisk-return-basics"))).toEqual({
      kind: "learning_opportunity",
      opportunityId: "risk-return-basics",
      placementId: "risk-return-primary",
      returnTo: "/learn/opportunities/risk-return-basics",
    });
    expect(parseSaveSelection(new URL("https://academy.test/saved-learning/new?kind=lesson&placement=cash-flow-primary"))).toEqual({
      kind: "placed_lesson",
      placementId: "cash-flow-primary",
      returnTo: "/learn",
    });
    expect(parseSaveSelection(new URL("https://academy.test/saved-learning/new?kind=lesson&kind=opportunity&placement=cash-flow-primary"))).toBeUndefined();
    expect(parseSaveSelection(new URL("https://academy.test/saved-learning/new?kind=opportunity&placement=cash-flow-primary"))).toBeUndefined();
    expect(parseSaveSelection(new URL("https://academy.test/saved-learning/new?kind=lesson&placement=cash-flow-primary&return=%2Flearning-admin"))).toEqual({
      kind: "placed_lesson",
      placementId: "cash-flow-primary",
      returnTo: "/learn",
    });
  });

  it("accepts only complete Project selectors and derives their safe destinations", () => {
    expect(parseSaveSelection(new URL("https://academy.test/saved-learning/new?kind=project_workspace&project=project.research-1"))).toEqual({
      kind: "project_workspace",
      projectId: "project.research-1",
      returnTo: "/projects/project.research-1#workspace",
    });
    expect(parseSaveSelection(new URL("https://academy.test/saved-learning/new?kind=project_snapshot&project=project.research-1&snapshot=snapshot.baseline-1"))).toEqual({
      kind: "project_snapshot",
      projectId: "project.research-1",
      snapshotId: "snapshot.baseline-1",
      returnTo: "/projects/project.research-1#snapshot-snapshot.baseline-1",
    });
    expect(parseSaveSelection(new URL("https://academy.test/saved-learning/new?kind=project_artifact&project=project.research-1&artifact=artifact.allocation-inputs&version=3"))).toEqual({
      kind: "project_artifact",
      projectId: "project.research-1",
      artifactId: "artifact.allocation-inputs",
      artifactVersion: 3,
      returnTo: "/projects/project.research-1#artifact-artifact.allocation-inputs-v3",
    });
    for (const query of [
      "kind=project_workspace",
      "kind=project_workspace&project=Project-Unsafe",
      "kind=project_snapshot&project=project.research-1",
      "kind=project_snapshot&project=project.research-1&snapshot=snapshot.baseline-1&artifact=artifact.one",
      "kind=project_snapshot&project=project.research-1&snapshot=snapshot.baseline-1&snapshot=snapshot.other",
      "kind=project_artifact&project=project.research-1&artifact=artifact.allocation-inputs&version=0",
      "kind=project_artifact&project=project.research-1&artifact=artifact.allocation-inputs&version=03",
      "kind=project_artifact&project=project.research-1&artifact=artifact.allocation-inputs&version=3&version=4",
      "kind=project_artifact&project=project.research-1&artifact=artifact.allocation-inputs&version=9007199254740992",
      "kind=project_workspace&project=project.research-1&return=%2Fprojects%2Fanother",
      "kind=project_workspace&project=project.research-1&owner=learner-one",
      "kind=project_workspace&project=project.research-1&extra=ignored",
      "kind=project_workspace&project=project.research-1&project=project.other",
    ]) {
      expect(parseSaveSelection(new URL(`https://academy.test/saved-learning/new?${query}`))).toBeUndefined();
    }
  });

  it.each([
    ["create note", [["operation", "create_note"], ["reference_kind", "learning_opportunity"], ["opportunity_id", "risk-return-basics"], ["placement_id", "risk-return-primary"], ["title", "Risk note"], ["body", "Keep evidence and interpretation separate."]], { operation: "create_note", selector: { reference_kind: "learning_opportunity", opportunity_id: "risk-return-basics", placement_id: "risk-return-primary" }, title: "Risk note", body: "Keep evidence and interpretation separate." }],
    ["create bookmark", [["operation", "create_bookmark"], ["reference_kind", "placed_lesson"], ["placement_id", "cash-flow-primary"], ["label", ""]], { operation: "create_bookmark", selector: { reference_kind: "placed_lesson", placement_id: "cash-flow-primary" }, label: "" }],
    ["create Project note", [["operation", "create_note"], ["reference_kind", "project_workspace"], ["project_id", "project.research-1"], ["title", "Project note"], ["body", "Review the current workspace."]], { operation: "create_note", selector: { reference_kind: "project_workspace", project_id: "project.research-1" }, title: "Project note", body: "Review the current workspace." }],
    ["create checkpoint bookmark", [["operation", "create_bookmark"], ["reference_kind", "project_snapshot"], ["project_id", "project.research-1"], ["snapshot_id", "snapshot.baseline-1"], ["label", "Baseline checkpoint"]], { operation: "create_bookmark", selector: { reference_kind: "project_snapshot", project_id: "project.research-1", snapshot_id: "snapshot.baseline-1" }, label: "Baseline checkpoint" }],
    ["create file bookmark", [["operation", "create_bookmark"], ["reference_kind", "project_artifact"], ["project_id", "project.research-1"], ["artifact_id", "artifact.allocation-inputs"], ["artifact_version", "3"], ["label", "Allocation inputs"]], { operation: "create_bookmark", selector: { reference_kind: "project_artifact", project_id: "project.research-1", artifact_id: "artifact.allocation-inputs", artifact_version: 3 }, label: "Allocation inputs" }],
    ["update note", [["operation", "update_note"], ["record_id", "note-one"], ["title", "Updated"], ["body", "Updated body"]], { operation: "update_note", record_id: "note-one", title: "Updated", body: "Updated body" }],
    ["update bookmark", [["operation", "update_bookmark"], ["record_id", "bookmark-one"], ["label", "Review"]], { operation: "update_bookmark", record_id: "bookmark-one", label: "Review" }],
    ["create collection", [["operation", "create_collection"], ["title", "Next steps"]], { operation: "create_collection", title: "Next steps" }],
    ["rename collection", [["operation", "rename_collection"], ["collection_id", "collection-one"], ["title", "Core ideas"]], { operation: "rename_collection", collection_id: "collection-one", title: "Core ideas" }],
    ["remove collection", [["operation", "remove_collection"], ["collection_id", "collection-one"]], { operation: "remove_collection", collection_id: "collection-one" }],
    ["set collection members", [["operation", "set_collection_members"], ["collection_id", "collection-one"], ["member_record_ids", "note-one"], ["member_record_ids", "bookmark-one"]], { operation: "set_collection_members", collection_id: "collection-one", member_record_ids: ["note-one", "bookmark-one"] }],
    ["reorder records", [["operation", "reorder_records"], ["record_ids", "bookmark-one"], ["record_ids", "note-one"]], { operation: "reorder_records", record_ids: ["bookmark-one", "note-one"] }],
    ["archive record", [["operation", "archive_record"], ["record_id", "note-one"]], { operation: "archive_record", record_id: "note-one" }],
    ["restore record", [["operation", "restore_record"], ["record_id", "bookmark-one"]], { operation: "restore_record", record_id: "bookmark-one" }],
    ["remove record", [["operation", "remove_record"], ["record_id", "note-one"]], { operation: "remove_record", record_id: "note-one" }],
    ["check source", [["operation", "refresh_reference"], ["record_id", "note-one"]], { operation: "refresh_reference", record_id: "note-one" }],
  ] as const)("maps the %s form to the generated public mutation", async (_name, fields, mutation) => {
    const post = vi.fn().mockResolvedValue(accepted(workspace));
    const action = createPersonalWorkspaceAction({ POST: post } as unknown as FinancialAcademyApiClient, session());
    const form = new FormData();
    form.set("form_intent", "test-mutation");
    form.set("idempotency_key", "11111111-1111-4111-8111-111111111111");
    form.set("expected_revision", "4");
    for (const [name, value] of fields) form.append(name, value);

    const result = await action({ request: new Request("http://localhost/saved-learning", { method: "POST", body: form }) } as never);

    expect(result).toBeInstanceOf(Response);
    expect(post).toHaveBeenCalledWith("/api/v1/personal-workspace/mutations", expect.objectContaining({
      body: {
        schema_version: "1.0.0",
        idempotency_key: "11111111-1111-4111-8111-111111111111",
        expected_revision: 4,
        mutation,
      },
    }));
    expect(post.mock.calls[0]?.[1]?.body).not.toHaveProperty("learner_id");
    expect(post.mock.calls[0]?.[1]?.body).not.toHaveProperty("workspace_id");
  });

  it.each([
    ["cross-variant Project field", [["reference_kind", "project_workspace"], ["project_id", "project.research-1"], ["snapshot_id", "snapshot.baseline-1"]]],
    ["unknown owner field", [["reference_kind", "project_workspace"], ["project_id", "project.research-1"], ["owner", "learner-one"]]],
    ["duplicated Project ID", [["reference_kind", "project_workspace"], ["project_id", "project.research-1"], ["project_id", "project.other"]]],
    ["duplicated artifact version", [["reference_kind", "project_artifact"], ["project_id", "project.research-1"], ["artifact_id", "artifact.inputs-1"], ["artifact_version", "3"], ["artifact_version", "4"]]],
    ["Project field on a Curriculum selector", [["reference_kind", "placed_lesson"], ["placement_id", "cash-flow-primary"], ["project_id", "project.research-1"]]],
  ] as const)("rejects a create form with a %s before session or API access", async (_name, selectorFields) => {
    const post = vi.fn();
    const profile = session();
    const action = createPersonalWorkspaceAction(
      { POST: post } as unknown as FinancialAcademyApiClient,
      profile,
    );
    const form = new FormData();
    form.set("form_intent", "create-bookmark");
    form.set("idempotency_key", "11111111-1111-4111-8111-111111111111");
    form.set("expected_revision", "4");
    form.set("operation", "create_bookmark");
    form.set("label", "Review later");
    for (const [name, value] of selectorFields) form.append(name, value);

    expect(await action({ request: new Request("http://localhost/saved-learning/new", { method: "POST", body: form }) } as never)).toEqual(expect.objectContaining({ kind: "invalid" }));
    expect(profile.ensure).not.toHaveBeenCalled();
    expect(post).not.toHaveBeenCalled();
  });

  it("returns the same validated mutation for an unchanged uncertain-response retry", async () => {
    const post = vi.fn().mockResolvedValue(accepted({ code: "unavailable" }, 503));
    const action = createPersonalWorkspaceAction({ POST: post } as unknown as FinancialAcademyApiClient, session());
    const form = new FormData();
    form.set("form_intent", "create-note");
    form.set("idempotency_key", "11111111-1111-4111-8111-111111111111");
    form.set("expected_revision", "4");
    form.set("operation", "create_note");
    form.set("reference_kind", "placed_lesson");
    form.set("placement_id", "cash-flow-primary");
    form.set("title", "Cash flow reminder");
    form.set("body", "Track the movement of cash.");

    expect(await action({ request: new Request("http://localhost/saved-learning/new", { method: "POST", body: form }) } as never)).toEqual(expect.objectContaining({
      status: "error",
      kind: "unavailable",
      preparedRequest: {
        schema_version: "1.0.0",
        idempotency_key: "11111111-1111-4111-8111-111111111111",
        expected_revision: 4,
        mutation: {
          operation: "create_note",
          selector: { reference_kind: "placed_lesson", placement_id: "cash-flow-primary" },
          title: "Cash flow reminder",
          body: "Track the movement of cash.",
        },
      },
    }));
  });

  it("accepts valid Project references through the real loader and action response guards", async () => {
    const projectWorkspace = workspaceWithTarget(projectSnapshotTarget);
    const get = vi.fn().mockResolvedValue(accepted(projectWorkspace));
    const query = await correlatedQueryResult(projectWorkspace.records, projectWorkspace.revision);
    const queryPost = vi.fn().mockResolvedValue(accepted(query));
    const loader = createPersonalWorkspaceLoader(
      { GET: get, POST: queryPost } as unknown as FinancialAcademyApiClient,
      session(),
    );
    expect(await loader({ request: new Request("http://localhost/saved-learning") } as never)).toEqual({
      status: "ready",
      workspace: projectWorkspace,
      query: {
        schema_version: "1.0.0",
        sort: "workspace_order",
        limit: 50,
      },
      result: query,
      search: {},
    });
    expect(queryPost).toHaveBeenCalledWith(
      "/api/v1/personal-workspace/query",
      expect.objectContaining({
        body: {
          schema_version: "1.0.0",
          sort: "workspace_order",
          limit: 50,
        },
      }),
    );

    const post = vi.fn().mockResolvedValue(accepted(projectWorkspace));
    const action = createPersonalWorkspaceAction(
      { POST: post } as unknown as FinancialAcademyApiClient,
      session(),
    );
    const form = new FormData();
    form.set("form_intent", "update-note");
    form.set("idempotency_key", "request-project-response");
    form.set("expected_revision", "4");
    form.set("operation", "update_note");
    form.set("record_id", "note-one");
    form.set("title", "Updated");
    form.set("body", "Updated body");
    expect(await action({ request: new Request("http://localhost/saved-learning", { method: "POST", body: form }) } as never)).toBeInstanceOf(Response);
  });

  it("rejects a query result from another workspace revision", async () => {
    const profile = session();
    const loader = createPersonalWorkspaceLoader(
      {
        GET: vi.fn().mockResolvedValue(accepted(workspace)),
        POST: vi.fn().mockResolvedValue(accepted(await correlatedQueryResult(workspace.records, 5))),
      } as unknown as FinancialAcademyApiClient,
      profile,
    );
    expect(await loader({ request: new Request("http://localhost/saved-learning") } as never)).toEqual({ status: "invalid-response" });
  });

  it.each([
    ["filter", { text: "other", sort: "updated_desc", limit: 1, cursor: "cursor_1" }, undefined],
    ["sort", { text: "risk", sort: "title_asc", limit: 1, cursor: "cursor_1" }, undefined],
    ["cursor", { text: "risk", sort: "updated_desc", limit: 1, cursor: "cursor_2" }, undefined],
    ["digest", { text: "risk", sort: "updated_desc", limit: 1, cursor: "cursor_1" }, "f".repeat(64)],
  ])("rejects a query response with mismatched %s meaning", async (_name, changed, digest) => {
    const appliedQuery: PersonalWorkspaceQuery = {
      schema_version: "1.0.0",
      ...changed,
    } as PersonalWorkspaceQuery;
    const result = await correlatedQueryResult([note], workspace.revision, appliedQuery);
    const loader = createPersonalWorkspaceLoader(
      {
        GET: vi.fn().mockResolvedValue(accepted(workspace)),
        POST: vi.fn().mockResolvedValue(accepted({
          ...result,
          ...(digest === undefined ? {} : { query_digest: digest }),
        })),
      } as unknown as FinancialAcademyApiClient,
      session(),
    );
    expect(await loader({
      request: new Request("http://localhost/saved-learning?q=risk&sort=updated_desc&limit=1&cursor=cursor_1"),
    } as never)).toEqual({ status: "invalid-response" });
  });

  it("rejects caller-supplied refresh authority fields", async () => {
    const post = vi.fn();
    const profile = session();
    const action = createPersonalWorkspaceAction(
      { POST: post } as unknown as FinancialAcademyApiClient,
      profile,
    );
    const form = new FormData();
    form.set("form_intent", "refresh:note-one");
    form.set("idempotency_key", "refresh-note-one");
    form.set("expected_revision", "4");
    form.set("operation", "refresh_reference");
    form.set("record_id", "note-one");
    form.set("target_status", "available");
    expect(await action({ request: new Request("http://localhost/saved-learning", { method: "POST", body: form }) } as never)).toEqual(expect.objectContaining({ kind: "invalid" }));
    expect(profile.ensure).not.toHaveBeenCalled();
    expect(post).not.toHaveBeenCalled();
  });

  it("rejects private or malformed Project fields through the real loader and action response guards", async () => {
    const privateWorkspace = workspaceWithTarget({
      ...projectWorkspaceTarget,
      permission_claim: "project.owner",
    });
    const loader = createPersonalWorkspaceLoader(
      { GET: vi.fn().mockResolvedValue(accepted(privateWorkspace)) } as unknown as FinancialAcademyApiClient,
      session(),
    );
    expect(await loader({ request: new Request("http://localhost/saved-learning") } as never)).toEqual({ status: "invalid-response" });

    const malformedWorkspace = workspaceWithTarget({
      ...projectArtifactTarget,
      logical_path: "C:\\private\\secret.csv",
    });
    const action = createPersonalWorkspaceAction(
      { POST: vi.fn().mockResolvedValue(accepted(malformedWorkspace)) } as unknown as FinancialAcademyApiClient,
      session(),
    );
    const form = new FormData();
    form.set("form_intent", "update-note");
    form.set("idempotency_key", "request-invalid-project-response");
    form.set("expected_revision", "4");
    form.set("operation", "update_note");
    form.set("record_id", "note-one");
    form.set("title", "Updated");
    form.set("body", "Updated body");
    expect(await action({ request: new Request("http://localhost/saved-learning", { method: "POST", body: form }) } as never)).toEqual(expect.objectContaining({ kind: "invalid-response" }));
  });

  it("accepts canonical Unicode request lengths and rejects invalid identifiers and excess members", async () => {
    const post = vi.fn().mockResolvedValue(accepted(workspace));
    const action = createPersonalWorkspaceAction({ POST: post } as unknown as FinancialAcademyApiClient, session());
    const valid = new FormData();
    valid.set("form_intent", "create-note");
    valid.set("idempotency_key", "request-unicode");
    valid.set("expected_revision", "4");
    valid.set("operation", "create_note");
    valid.set("reference_kind", "placed_lesson");
    valid.set("placement_id", "cash-flow-primary");
    valid.set("title", "📈".repeat(120));
    valid.set("body", "Line one\n\tLine two");
    expect(await action({ request: new Request("http://localhost/saved-learning/new", { method: "POST", body: valid }) } as never)).toBeInstanceOf(Response);

    const invalidId = new FormData();
    for (const [name, value] of valid.entries()) invalidId.append(name, value);
    invalidId.set("idempotency_key", "request-invalid-id");
    invalidId.set("placement_id", "Cash-Flow");
    expect(await action({ request: new Request("http://localhost/saved-learning/new", { method: "POST", body: invalidId }) } as never)).toEqual(expect.objectContaining({ kind: "invalid" }));

    const excess = new FormData();
    excess.set("form_intent", "members");
    excess.set("idempotency_key", "request-members");
    excess.set("expected_revision", "4");
    excess.set("operation", "set_collection_members");
    excess.set("collection_id", "collection-one");
    for (let index = 0; index < 101; index += 1) {
      excess.append("member_record_ids", `record-${index}`);
    }
    expect(await action({ request: new Request("http://localhost/saved-learning", { method: "POST", body: excess }) } as never)).toEqual(expect.objectContaining({ kind: "invalid" }));
  });
});

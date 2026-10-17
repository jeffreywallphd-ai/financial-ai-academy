import { describe, expect, it, vi } from "vitest";

import type { FinancialAcademyApiClient } from "../../src/generated/api-client";
import { createPersonalWorkspaceAction } from "../../src/features/personal-workspace/api";
import {
  parseSaveSelection,
  personalWorkspaceIsSafe,
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
  it("accepts varied closed records, nullable labels, order, and compatible extra facts", () => {
    expect(personalWorkspaceIsSafe({
      ...workspace,
      compatible_future_fact: "ignored",
      records: workspace.records.map((record, index) => ({
        ...record,
        compatible_record_fact: index,
      })),
    })).toBe(true);
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

  it.each([
    ["create note", [["operation", "create_note"], ["reference_kind", "learning_opportunity"], ["opportunity_id", "risk-return-basics"], ["placement_id", "risk-return-primary"], ["title", "Risk note"], ["body", "Keep evidence and interpretation separate."]], { operation: "create_note", selector: { reference_kind: "learning_opportunity", opportunity_id: "risk-return-basics", placement_id: "risk-return-primary" }, title: "Risk note", body: "Keep evidence and interpretation separate." }],
    ["create bookmark", [["operation", "create_bookmark"], ["reference_kind", "placed_lesson"], ["placement_id", "cash-flow-primary"], ["label", ""]], { operation: "create_bookmark", selector: { reference_kind: "placed_lesson", placement_id: "cash-flow-primary" }, label: null }],
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
      idempotencyKey: "11111111-1111-4111-8111-111111111111",
      retryMutation: {
        operation: "create_note",
        selector: { reference_kind: "placed_lesson", placement_id: "cash-flow-primary" },
        title: "Cash flow reminder",
        body: "Track the movement of cash.",
      },
    }));
  });
});

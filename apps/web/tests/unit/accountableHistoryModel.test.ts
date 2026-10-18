import { describe, expect, it } from "vitest";

import {
  accountableHistoryDocumentIsSafe,
  portableEvidenceExportIsSafe,
  type AccountableHistoryDocument,
  type CompletionHistoryRequest,
  type PortableEvidenceExport,
  type PublishedLessonHistoryRequest,
} from "../../src/features/accountable-history/model";

const request = {
  schema_version: "1.0.0",
  root_kind: "published_lesson",
  package_id: "intro-risk-return",
  package_version: "1.0.0",
  package_digest: "8".repeat(64),
} satisfies PublishedLessonHistoryRequest;

const document = {
  schema_version: "1.0.0",
  purpose: "learner_review",
  root: {
    root_kind: "published_lesson",
    resource_id: "intro-risk-return",
    resource_version: "1.0.0",
  },
  state: "valid",
  title: "Source and history",
  summary: "This view shows the available source and history for the lesson.",
  source_lineage_digest: "1".repeat(64),
  entries: [
    {
      sequence: 1,
      entry_id: "source-économie",
      role: "source",
      title: "Reviewed source",
      explanation: "This source was used to prepare the lesson.",
      owner_module: "content",
      resource_kind: "educational_source",
      resource_id: "source-économie",
      resource_version: "2026.08.05",
      integrity_digest: "2".repeat(64),
      recorded_at: "2026-08-05T11:30:00-04:00",
      validation_status: "validated",
    },
    {
      sequence: 2,
      entry_id: "lesson",
      role: "published",
      title: "Published lesson",
      explanation: "The lesson was published from the reviewed source.",
      owner_module: "content",
      resource_kind: "published_lesson",
      resource_id: "intro-risk-return",
      resource_version: "1.0.0",
      integrity_digest: "3".repeat(64),
      recorded_at: "2026-08-05T16:00:00Z",
      validation_status: "validated",
    },
  ],
  transformations: [
    {
      source_entry_id: "lesson",
      target_entry_id: "source-économie",
      relation: "published_from",
    },
  ],
  missing_links: [],
  diagnostics: [],
  redactions: [
    { category: "owner_payload", count: 2 },
    { category: "storage_details", count: 2 },
  ],
  history_digest: "4".repeat(64),
} satisfies AccountableHistoryDocument;

function clone<T>(value: T): T {
  return structuredClone(value);
}

describe("accountable history runtime validation", () => {
  it("accepts variable Unicode history that preserves exact invariants", () => {
    expect(accountableHistoryDocumentIsSafe(document, request)).toBe(true);
  });

  it.each([
    [
      "wrong owner",
      (value: Record<string, any>) => {
        value.entries[0].owner_module = "audit";
      },
    ],
    [
      "wrong sequence",
      (value: Record<string, any>) => {
        value.entries[1].sequence = 3;
      },
    ],
    [
      "broken connection",
      (value: Record<string, any>) => {
        value.transformations[0].target_entry_id = "missing";
      },
    ],
    [
      "missing time offset",
      (value: Record<string, any>) => {
        value.entries[0].recorded_at = "2026-08-05T11:30:00";
      },
    ],
    [
      "unknown field",
      (value: Record<string, any>) => {
        value.learner_id = "private";
      },
    ],
    [
      "wrong root",
      (value: Record<string, any>) => {
        value.root.resource_id = "other-lesson";
      },
    ],
    [
      "missing matching root entry",
      (value: Record<string, any>) => {
        value.entries[1].resource_id = "other-lesson";
      },
    ],
    [
      "wrong matching root version",
      (value: Record<string, any>) => {
        value.entries[1].resource_version = "2.0.0";
      },
    ],
  ])("rejects %s without weakening the rest of the shape", (_name, change) => {
    const changed = clone(document) as unknown as Record<string, any>;
    change(changed);
    expect(accountableHistoryDocumentIsSafe(changed, request)).toBe(false);
  });

  it("requires exactly one disclosed entry to match the lesson root", () => {
    const changed = clone(document) as unknown as Record<string, any>;
    changed.entries.push({
      ...clone(changed.entries[1]),
      sequence: 3,
      entry_id: "duplicate-lesson",
    });
    expect(accountableHistoryDocumentIsSafe(changed, request)).toBe(false);
  });

  it("requires exactly one disclosed entry to match the completion root", () => {
    const completionRequest = {
      schema_version: "1.0.0",
      root_kind: "knowledge_check_completion",
      placement_id: "placement-1",
      evidence_id: "evidence-1",
      occurrence: 2,
    } satisfies CompletionHistoryRequest;
    const completionDocument = clone(document) as unknown as Record<
      string,
      any
    >;
    completionDocument.root = {
      root_kind: "knowledge_check_completion",
      resource_id: "evidence-1",
      occurrence: 2,
    };
    completionDocument.entries[1] = {
      ...completionDocument.entries[1],
      entry_id: "completion",
      role: "recorded",
      owner_module: "assessment",
      resource_kind: "completion_evidence",
      resource_id: "evidence-1",
      occurrence: 2,
    };
    delete completionDocument.entries[1].resource_version;
    completionDocument.transformations[0].source_entry_id = "completion";

    expect(
      accountableHistoryDocumentIsSafe(completionDocument, completionRequest),
    ).toBe(true);
    completionDocument.entries[1].occurrence = 1;
    expect(
      accountableHistoryDocumentIsSafe(completionDocument, completionRequest),
    ).toBe(false);
  });

  it.each([
    "0000-01-01T00:00:00Z",
    "2026-02-29T12:00:00Z",
    "2026-02-30T12:00:00Z",
    "2026-13-01T12:00:00Z",
    "2026-01-01T24:00:00Z",
    "2026-01-01T12:60:00Z",
    "2026-01-01T12:00:60Z",
    "2026-01-01T12:00:00+24:00",
    "2026-01-01T12:00:00+01:60",
  ])("rejects impossible history time %s", (recordedAt) => {
    const changed = clone(document) as unknown as Record<string, any>;
    changed.entries[0].recorded_at = recordedAt;
    expect(accountableHistoryDocumentIsSafe(changed, request)).toBe(false);
  });

  it.each([
    "2024-02-29T23:59:59.123456Z",
    "2026-01-01T00:00:00+23:59",
  ])("accepts valid history time %s", (recordedAt) => {
    const changed = clone(document) as unknown as Record<string, any>;
    changed.entries[0].recorded_at = recordedAt;
    expect(accountableHistoryDocumentIsSafe(changed, request)).toBe(true);
  });

  it("accepts only a root-matched portable wrapper with canonical UTC export time", () => {
    const portableDocument = {
      ...clone(document),
      purpose: "portable_evidence",
      title: "Portable evidence record",
      history_digest: "5".repeat(64),
    } satisfies AccountableHistoryDocument;
    const portable = {
      schema_version: "1.0.0",
      media_type:
        "application/vnd.financial-ai-academy.accountable-history+json",
      filename_stem: "lesson-1234abcd",
      exported_at: "2026-08-05T16:15:01Z",
      document_digest: portableDocument.history_digest,
      document: portableDocument,
    } satisfies PortableEvidenceExport;

    expect(portableEvidenceExportIsSafe(portable, request)).toBe(true);
    expect(
      portableEvidenceExportIsSafe(
        {
          ...portable,
          exported_at: "2026-08-05T16:15:01+00:00",
        },
        request,
      ),
    ).toBe(false);
    expect(
      portableEvidenceExportIsSafe(
        {
          ...portable,
          exported_at: "2026-02-30T16:15:01Z",
        },
        request,
      ),
    ).toBe(false);
    expect(
      portableEvidenceExportIsSafe(
        {
          ...portable,
          document_digest: "6".repeat(64),
        },
        request,
      ),
    ).toBe(false);
    expect(
      portableEvidenceExportIsSafe(
        {
          ...portable,
          document: {
            ...portable.document,
            root: { ...portable.document.root, resource_id: "other-lesson" },
          },
        },
        request,
      ),
    ).toBe(false);
  });
});

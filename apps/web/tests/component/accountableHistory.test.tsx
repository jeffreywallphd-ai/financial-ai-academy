import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { AccountableHistoryPanel } from "../../src/features/accountable-history/AccountableHistoryPanel";
import type {
  AccountableHistoryExporter,
  AccountableHistoryReader,
} from "../../src/features/accountable-history/api";
import type {
  AccountableHistoryDocument,
  PortableEvidenceExport,
  PublishedLessonHistoryRequest,
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
    resource_id: request.package_id,
    resource_version: request.package_version,
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
      resource_id: request.package_id,
      resource_version: request.package_version,
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
  redactions: [{ category: "owner_payload", count: 2 }],
  history_digest: "4".repeat(64),
} satisfies AccountableHistoryDocument;

const unavailableExporter: AccountableHistoryExporter = async () => ({
  status: "unavailable",
});

afterEach(() => {
  vi.restoreAllMocks();
});

function renderPanel(
  readHistory: AccountableHistoryReader,
  exportHistory: AccountableHistoryExporter = unavailableExporter,
) {
  render(
    <AccountableHistoryPanel
      contextLabel="published lesson"
      exportHistory={exportHistory}
      readHistory={readHistory}
      request={request}
    />,
  );
}

describe("AccountableHistoryPanel", () => {
  it("loads only after the learner asks and preserves the exact root request", async () => {
    const readHistory = vi
      .fn<AccountableHistoryReader>()
      .mockResolvedValue({ status: "ready", document });
    renderPanel(readHistory);

    expect(readHistory).not.toHaveBeenCalled();
    expect(
      screen.getByRole("heading", { name: "Source and history" }),
    ).toBeVisible();

    await userEvent
      .setup()
      .click(screen.getByRole("button", { name: "Show source and history" }));

    await waitFor(() => expect(readHistory).toHaveBeenCalledOnce());
    expect(readHistory.mock.calls[0]?.[0]).toEqual(request);
    expect(readHistory.mock.calls[0]?.[1]).toBeInstanceOf(AbortSignal);
    expect(screen.getByText("Available history")).toBeVisible();
    expect(
      screen.getByRole("heading", { name: "Reviewed source" }),
    ).toBeVisible();
    expect(
      screen.getByText(
        "Private, protected, and internal details stay with their source records.",
      ),
    ).toBeVisible();
  });

  it("keeps exact identifiers and integrity codes inside a technical disclosure", async () => {
    renderPanel(async () => ({ status: "ready", document }));
    const user = userEvent.setup();
    await user.click(
      screen.getByRole("button", { name: "Show source and history" }),
    );

    const summary = await screen.findByText("Technical record");
    const details = summary.closest("details");
    expect(details).not.toHaveAttribute("open");
    expect(screen.getByText(document.history_digest)).not.toBeVisible();

    await user.click(summary);
    expect(details).toHaveAttribute("open");
    const technical = within(details as HTMLDetailsElement);
    expect(technical.getAllByText(request.package_id)).not.toHaveLength(0);
    expect(technical.getByText(document.history_digest)).toBeVisible();
    expect(technical.getByText("published_from")).toBeVisible();
  });

  it("explains incomplete history in plain language while retaining exact notes", async () => {
    const incomplete = {
      ...document,
      state: "incomplete",
      entries: document.entries.map((entry, index) =>
        index === 0
          ? { ...entry, validation_status: "incomplete" as const }
          : entry,
      ),
      missing_links: [
        {
          source_entry_id: "source-économie",
          target_reference: "source-archive",
          relation: "published_from",
          reason: "unavailable",
          explanation: "The source archive could not be reached.",
        },
      ],
      diagnostics: [
        {
          code: "missing_reference",
          reference: "source-archive",
          explanation: "One earlier record was not available.",
        },
      ],
    } satisfies AccountableHistoryDocument;
    renderPanel(async () => ({ status: "ready", document: incomplete }));

    await userEvent
      .setup()
      .click(screen.getByRole("button", { name: "Show source and history" }));

    expect(
      await screen.findByText("Some history is unavailable"),
    ).toBeVisible();
    expect(
      screen.getByText("The source archive could not be reached."),
    ).toBeVisible();
    expect(
      screen.getByText("One earlier record was not available."),
    ).toBeVisible();
    expect(screen.getByText("missing_reference")).not.toBeVisible();
    expect(screen.getByText("unavailable")).not.toBeVisible();
  });

  it("offers bounded retry for temporary failure and no retry for forbidden access", async () => {
    const readHistory = vi
      .fn<AccountableHistoryReader>()
      .mockResolvedValueOnce({ status: "unavailable" })
      .mockResolvedValueOnce({ status: "ready", document });
    renderPanel(readHistory);
    const user = userEvent.setup();

    await user.click(
      screen.getByRole("button", { name: "Show source and history" }),
    );
    await user.click(await screen.findByRole("button", { name: "Try again" }));
    expect(await screen.findByText("Available history")).toBeVisible();
    expect(readHistory).toHaveBeenCalledTimes(2);

    const { unmount } = render(
      <AccountableHistoryPanel
        contextLabel="published lesson"
        exportHistory={unavailableExporter}
        readHistory={async () => ({ status: "forbidden" })}
        request={request}
      />,
    );
    const panels = screen.getAllByRole("button", {
      name: "Show source and history",
    });
    await user.click(panels.at(-1)!);
    expect(
      await screen.findByText(/not available with this learner access/i),
    ).toBeVisible();
    expect(
      screen.queryByRole("button", { name: "Try again" }),
    ).not.toBeInTheDocument();
    unmount();
  });

  it("downloads only the separately returned portable evidence record", async () => {
    const portableDocument = {
      ...document,
      purpose: "portable_evidence",
      title: "Portable evidence record",
      history_digest: "5".repeat(64),
    } satisfies AccountableHistoryDocument;
    const record = {
      schema_version: "1.0.0",
      media_type:
        "application/vnd.financial-ai-academy.accountable-history+json",
      filename_stem: "lesson-1234abcd",
      exported_at: "2026-08-05T16:15:01Z",
      document_digest: portableDocument.history_digest,
      document: portableDocument,
    } satisfies PortableEvidenceExport;
    const createObjectURL = vi.fn().mockReturnValue("blob:accountable-history");
    const revokeObjectURL = vi.fn();
    const click = vi
      .spyOn(HTMLAnchorElement.prototype, "click")
      .mockImplementation(() => undefined);
    Object.defineProperty(URL, "createObjectURL", {
      configurable: true,
      value: createObjectURL,
    });
    Object.defineProperty(URL, "revokeObjectURL", {
      configurable: true,
      value: revokeObjectURL,
    });
    const exportHistory = vi
      .fn<AccountableHistoryExporter>()
      .mockResolvedValue({ status: "ready", record });
    renderPanel(async () => ({ status: "ready", document }), exportHistory);
    const user = userEvent.setup();

    await user.click(
      screen.getByRole("button", { name: "Show source and history" }),
    );
    await user.click(
      await screen.findByRole("button", { name: "Download evidence record" }),
    );

    await waitFor(() => expect(exportHistory).toHaveBeenCalledOnce());
    expect(exportHistory.mock.calls[0]?.[0]).toEqual(request);
    expect(createObjectURL).toHaveBeenCalledWith(expect.any(Blob));
    expect(click).toHaveBeenCalledOnce();
    expect(revokeObjectURL).toHaveBeenCalledWith("blob:accountable-history");
    expect(screen.getByText(/download is ready/i)).toBeVisible();
  });
});

import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router";
import { describe, expect, it, vi } from "vitest";

import {
  PlatformHelpSearchPage,
  PlatformHelpTopicPage,
} from "../../src/features/platform-help/PlatformHelpPage";
import { ContextualHelpLinks } from "../../src/features/platform-help/ContextualHelpLinks";
import { FeatureGuidanceExplanation } from "../../src/features/platform-help/FeatureGuidanceExplanation";
import { createFeatureGuidanceReader } from "../../src/features/platform-help/api";
import {
  featureGuidanceIsSafe,
  type FeatureGuidance,
} from "../../src/features/platform-help/model";
import {
  PlatformHelpSearchRouteView,
  PlatformHelpTopicRouteView,
} from "../../src/features/platform-help/PlatformHelpRoute";
import {
  contextualHelpFixture,
  platformHelpSearchFixture,
  platformHelpTopicFixture,
} from "./platformHelpFixture";

const searchSelection = {
  parameters: {
    query: "calculations",
    topic_kind: "method" as const,
    page_size: 20,
  },
  href: "/help?query=calculations&topic_kind=method&page_size=20",
};

function canonicalJson(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map(canonicalJson).join(",")}]`;
  if (typeof value === "object" && value !== null) {
    const item = value as Record<string, unknown>;
    return `{${Object.keys(item)
      .sort()
      .map((key) => `${JSON.stringify(key)}:${canonicalJson(item[key])}`)
      .join(",")}}`;
  }
  return JSON.stringify(value) ?? "null";
}

async function digestWithout(
  value: Record<string, unknown>,
  field: string,
): Promise<string> {
  const document = Object.fromEntries(
    Object.entries(value).filter(([key]) => key !== field),
  );
  const digest = await crypto.subtle.digest(
    "SHA-256",
    new TextEncoder().encode(canonicalJson(document)),
  );
  return [...new Uint8Array(digest)]
    .map((item) => item.toString(16).padStart(2, "0"))
    .join("");
}

async function featureGuidanceFixture(): Promise<FeatureGuidance> {
  const publication = {
    state: "approved",
    reviewed_on: "2026-10-18",
    updated_at: "2026-10-18T00:00:00Z",
  } as const;
  const source = {
    source_key: "safe-recovery",
    title: "Safe recovery source",
    area: "architecture" as const,
    source_version: "2026-10-18",
    content_fingerprint: "a".repeat(64),
  };
  const mapping: Record<string, unknown> = {
    schema_version: "1.0.0",
    surface_key: "practice-activity",
    condition_key: "write-outcome-uncertain",
    mapping_version: "1.0.0",
    guidance_id: "practice-write-uncertain",
    guidance_version: "1.0.0",
    publication,
    source_references: [source],
    mapping_digest: "0".repeat(64),
  };
  const guidance: Record<string, unknown> = {
    schema_version: "1.0.0",
    guidance_id: "practice-write-uncertain",
    guidance_version: "1.0.0",
    status: "degraded",
    heading: "The result of this save is uncertain",
    reason: "The response was unavailable after the save was sent.",
    outcome: "Your answers may already be saved. No different request was sent.",
    actions: [
      {
        action_kind: "retry_unchanged_request",
        label: "Try the same save again",
      },
      {
        action_kind: "reload_current_state",
        label: "Reload saved progress",
      },
      {
        action_kind: "open_help_topic",
        label: "Review safe recovery",
        topic_id: "safe-recovery",
        topic_version: "1.0.0",
      },
    ],
    help_references: [
      {
        topic_id: "safe-recovery",
        topic_version: "1.0.0",
        purpose: "method",
        label: "Safe recovery",
      },
    ],
    applicability: [
      { scope_key: "practice-activity", label: "Practice saves" },
    ],
    publication,
    source_references: [source],
    guidance_digest: "0".repeat(64),
  };
  mapping.mapping_digest = await digestWithout(mapping, "mapping_digest");
  guidance.guidance_digest = await digestWithout(guidance, "guidance_digest");
  return { mapping, guidance } as FeatureGuidance;
}

async function withCurrentFeatureGuidanceDigests(
  value: FeatureGuidance,
): Promise<FeatureGuidance> {
  const candidate = structuredClone(value) as unknown as {
    mapping: Record<string, unknown>;
    guidance: Record<string, unknown>;
  };
  candidate.mapping.mapping_digest = await digestWithout(
    candidate.mapping,
    "mapping_digest",
  );
  candidate.guidance.guidance_digest = await digestWithout(
    candidate.guidance,
    "guidance_digest",
  );
  return candidate as unknown as FeatureGuidance;
}

async function variedFeatureGuidanceFixture(): Promise<FeatureGuidance> {
  const candidate = structuredClone(await featureGuidanceFixture()) as unknown as {
    mapping: Record<string, unknown>;
    guidance: Record<string, unknown>;
  };
  candidate.guidance.heading = "Review what happened before continuing";
  candidate.guidance.reason = "The response ended before confirmation arrived.";
  candidate.guidance.outcome = "The same request may already be saved.";
  candidate.guidance.actions = [
    {
      action_kind: "open_help_topic",
      label: "Review source history",
      topic_id: "source-and-history",
      topic_version: "1.0.0",
    },
    {
      action_kind: "return_to_owning_task",
      label: "Return to practice",
    },
    {
      action_kind: "retry_unchanged_request",
      label: "Retry the same request",
    },
    {
      action_kind: "open_help_topic",
      label: "Review safe recovery",
      topic_id: "safe-recovery",
      topic_version: "1.0.0",
    },
  ];
  candidate.guidance.help_references = [
    {
      topic_id: "source-and-history",
      topic_version: "1.0.0",
      purpose: "source",
      label: "Source and history",
    },
    {
      topic_id: "safe-recovery",
      topic_version: "1.0.0",
      purpose: "method",
      label: "Safe recovery",
    },
  ];
  candidate.guidance.applicability = [
    { scope_key: "practice-save", label: "Practice saves" },
    { scope_key: "practice-submit", label: "Practice submissions" },
  ];
  return withCurrentFeatureGuidanceDigests(
    candidate as unknown as FeatureGuidance,
  );
}

describe("PlatformHelpSearchPage", () => {
  it("shows plain-language reviewed results in API order", () => {
    render(
      <MemoryRouter>
        <PlatformHelpSearchPage
          page={platformHelpSearchFixture}
          selection={searchSelection}
        />
      </MemoryRouter>,
    );

    expect(
      screen.getByRole("heading", { name: "Understand how the Academy works" }),
    ).toBeVisible();
    expect(screen.getByRole("searchbox", { name: "Search the guide" })).toHaveValue(
      "calculations",
    );
    expect(screen.getByRole("combobox", { name: "Type of help" })).toHaveValue(
      "method",
    );
    expect(screen.getByRole("article")).toHaveTextContent(
      "How platform methods stay reproducible",
    );
    expect(screen.getByRole("article")).toHaveTextContent(
      "Last updated October 18, 2026",
    );
    expect(screen.getByText("Publication details")).toBeVisible();
    expect(screen.getByRole("link", { name: "Read this topic" })).toHaveAttribute(
      "href",
      "/help/topics/platform-methods/versions/1.0.0?return_to=%2Fhelp%3Fquery%3Dcalculations%26topic_kind%3Dmethod%26page_size%3D20",
    );
    expect(screen.getByRole("link", { name: "Show more topics" })).toHaveAttribute(
      "href",
      "/help?query=calculations&topic_kind=method&page_size=20&cursor=eyJ2IjoxfQ",
    );
    expect(document.body.textContent).not.toMatch(/slug|payload|endpoint/i);
  });

  it("provides a useful empty result without inventing a recommendation", () => {
    render(
      <MemoryRouter>
        <PlatformHelpSearchPage
          page={{ ...platformHelpSearchFixture, results: [], next_cursor: null }}
          selection={searchSelection}
        />
      </MemoryRouter>,
    );

    expect(screen.getByRole("heading", { name: "No matching topics" })).toBeVisible();
    expect(screen.getByRole("link", { name: "Clear search" })).toHaveAttribute(
      "href",
      "/help",
    );
    expect(document.body.textContent).not.toMatch(/recommended for you/i);
  });
});

describe("PlatformHelpTopicPage", () => {
  it("renders only typed inert content and exact same-guide links", async () => {
    const user = userEvent.setup();
    render(
      <MemoryRouter>
        <PlatformHelpTopicPage
          selection={{
            topicId: "platform-methods",
            topicVersion: "1.0.0",
            returnTo: "/help?query=calculations&page_size=20",
            returnLabel: "Return to platform guide",
          }}
          topic={platformHelpTopicFixture}
        />
      </MemoryRouter>,
    );

    expect(
      screen.getByRole("heading", { name: "How platform methods stay reproducible" }),
    ).toBeVisible();
    expect(screen.getByRole("heading", { name: "What the platform records" })).toBeVisible();
    expect(screen.getByText("Known limit")).toBeVisible();
    expect(screen.getByRole("link", { name: "Read the education boundary" })).toHaveAttribute(
      "href",
      "/help/topics/education-not-advice/versions/1.0.0?return_to=%2Fhelp%3Fquery%3Dcalculations%26page_size%3D20",
    );
    expect(screen.getByRole("link", { name: "Return to platform guide" })).toHaveAttribute(
      "href",
      "/help?query=calculations&page_size=20",
    );
    expect(document.querySelector("script")).toBeNull();

    await user.click(screen.getByText("Technical record"));
    const details = screen.getByText("Technical record").closest("details");
    expect(details).not.toBeNull();
    expect(within(details as HTMLElement).getByText("platform-methods@1.0.0")).toBeVisible();
    expect(
      within(details as HTMLElement).getByText(
        platformHelpTopicFixture.source_references[0]!.content_fingerprint,
      ),
    ).toBeVisible();
    expect(
      within(details as HTMLElement).getByText(
        platformHelpTopicFixture.publication.updated_at,
      ),
    ).toBeVisible();
  });
});

describe("ContextualHelpLinks", () => {
  it("renders every server-owned label in order with an exact safe return", async () => {
    render(
      <MemoryRouter initialEntries={["/learn/placements/lesson-one"]}>
        <ContextualHelpLinks
          contextKey="lesson-publication"
          readContextualHelp={vi.fn().mockResolvedValue({
            status: "ready",
            context: contextualHelpFixture,
          })}
        />
      </MemoryRouter>,
    );

    expect(
      await screen.findByRole("heading", {
        name: "Questions about Lesson publication details",
      }),
    ).toBeVisible();
    const links = screen.getAllByRole("link");
    expect(links).toHaveLength(2);
    expect(links[0]).toHaveTextContent("How to use source and history details");
    expect(links[0]).toHaveAttribute(
      "href",
      "/help/topics/source-and-history/versions/1.0.0?return_to=%2Flearn%2Fplacements%2Flesson-one",
    );
  });

  it("leaves the feature unchanged when optional contextual Help is unavailable", async () => {
    render(
      <MemoryRouter initialEntries={["/preferences/assistance"]}>
        <main>
          <h1>AI help and reminders</h1>
          <ContextualHelpLinks
            contextKey="ai-assistance"
            readContextualHelp={vi.fn().mockResolvedValue({
              status: "unavailable",
            })}
          />
        </main>
      </MemoryRouter>,
    );

    expect(screen.getByRole("heading", { name: "AI help and reminders" })).toBeVisible();
    expect(
      screen.queryByRole("heading", { name: /Questions about/ }),
    ).toBeNull();
  });
});

describe("FeatureGuidanceExplanation", () => {
  it("rejects stale digests, mapping-record mismatch, and unknown shapes", async () => {
    const resolution = await featureGuidanceFixture();
    expect(
      await featureGuidanceIsSafe(
        resolution,
        "practice-activity",
        "write-outcome-uncertain",
        "1.0.0",
      ),
    ).toBe(true);
    expect(
      await featureGuidanceIsSafe(
        {
          ...resolution,
          guidance: {
            ...resolution.guidance,
            reason: "Changed after the digest was issued.",
          },
        },
        "practice-activity",
        "write-outcome-uncertain",
        "1.0.0",
      ),
    ).toBe(false);

    const staleMapping = structuredClone(resolution) as unknown as {
      mapping: Record<string, unknown>;
      guidance: Record<string, unknown>;
    };
    staleMapping.mapping.mapping_digest = "f".repeat(64);
    expect(
      await featureGuidanceIsSafe(
        staleMapping,
        "practice-activity",
        "write-outcome-uncertain",
        "1.0.0",
      ),
    ).toBe(false);

    const mismatched = structuredClone(resolution) as unknown as {
      mapping: Record<string, unknown>;
      guidance: Record<string, unknown>;
    };
    mismatched.mapping.guidance_id = "different-guidance";
    const signedMismatch = await withCurrentFeatureGuidanceDigests(
      mismatched as unknown as FeatureGuidance,
    );
    expect(
      await featureGuidanceIsSafe(
        signedMismatch,
        "practice-activity",
        "write-outcome-uncertain",
        "1.0.0",
      ),
    ).toBe(false);

    const extended = structuredClone(resolution) as unknown as {
      mapping: Record<string, unknown>;
      guidance: Record<string, unknown>;
    };
    extended.guidance.internal_route = "private/guidance";
    const signedExtended = await withCurrentFeatureGuidanceDigests(
      extended as unknown as FeatureGuidance,
    );
    expect(
      await featureGuidanceIsSafe(
        signedExtended,
        "practice-activity",
        "write-outcome-uncertain",
        "1.0.0",
      ),
    ).toBe(false);
  });

  it("renews once after 401 and repeats the exact read without a third request", async () => {
    const resolution = await featureGuidanceFixture();
    const get = vi
      .fn()
      .mockResolvedValueOnce({ response: { status: 401 } })
      .mockResolvedValueOnce({ response: { status: 200 }, data: resolution });
    const ensure = vi.fn().mockResolvedValue({ status: "ready" });
    const invalidate = vi.fn();
    const reader = createFeatureGuidanceReader(
      { GET: get } as never,
      { ensure, invalidate } as never,
    );
    const signal = new AbortController().signal;

    expect(
      await reader(
        "practice-activity",
        "write-outcome-uncertain",
        "1.0.0",
        signal,
      ),
    ).toEqual({ status: "ready", resolution });
    expect(invalidate).toHaveBeenCalledOnce();
    expect(ensure).toHaveBeenCalledWith(signal);
    expect(get).toHaveBeenCalledTimes(2);
    expect(get.mock.calls[1]).toEqual(get.mock.calls[0]);
  });

  it("collapses repeated denial and failed renewal while propagating aborts", async () => {
    const repeatedGet = vi
      .fn()
      .mockResolvedValue({ response: { status: 401 } });
    const repeatedEnsure = vi.fn().mockResolvedValue({ status: "ready" });
    const repeatedReader = createFeatureGuidanceReader(
      { GET: repeatedGet } as never,
      { ensure: repeatedEnsure, invalidate: vi.fn() } as never,
    );
    expect(
      await repeatedReader(
        "practice-activity",
        "write-outcome-uncertain",
        "1.0.0",
        new AbortController().signal,
      ),
    ).toEqual({ status: "unavailable" });
    expect(repeatedGet).toHaveBeenCalledTimes(2);
    expect(repeatedEnsure).toHaveBeenCalledOnce();

    const failedGet = vi.fn().mockResolvedValue({ response: { status: 401 } });
    const failedEnsure = vi.fn().mockResolvedValue({
      status: "error",
      kind: "unavailable",
    });
    const failedReader = createFeatureGuidanceReader(
      { GET: failedGet } as never,
      { ensure: failedEnsure, invalidate: vi.fn() } as never,
    );
    expect(
      await failedReader(
        "practice-activity",
        "write-outcome-uncertain",
        "1.0.0",
        new AbortController().signal,
      ),
    ).toEqual({ status: "unavailable" });
    expect(failedGet).toHaveBeenCalledOnce();

    const controller = new AbortController();
    controller.abort();
    const abortError = new DOMException("The request was aborted.", "AbortError");
    const abortedReader = createFeatureGuidanceReader(
      { GET: vi.fn().mockRejectedValue(abortError) } as never,
      { ensure: vi.fn(), invalidate: vi.fn() } as never,
    );
    await expect(
      abortedReader(
        "practice-activity",
        "write-outcome-uncertain",
        "1.0.0",
        controller.signal,
      ),
    ).rejects.toBe(abortError);
  });

  it("preserves exact reader correlation for a valid response", async () => {
    const resolution = await featureGuidanceFixture();

    const get = vi.fn().mockResolvedValue({
      response: { status: 200 },
      data: resolution,
    });
    const reader = createFeatureGuidanceReader(
      { GET: get } as never,
      { ensure: vi.fn(), invalidate: vi.fn() } as never,
    );
    const outcome = await reader(
      "practice-activity",
      "write-outcome-uncertain",
      "1.0.0",
      new AbortController().signal,
    );
    expect(outcome).toEqual({ status: "ready", resolution });
    expect(get).toHaveBeenCalledWith(
      "/api/v1/guidance/feature-guidance/{surface_key}/conditions/{condition_key}/versions/{mapping_version}",
      expect.objectContaining({
        params: {
          path: {
            surface_key: "practice-activity",
            condition_key: "write-outcome-uncertain",
            mapping_version: "1.0.0",
          },
        },
      }),
    );
  });

  it("renders server-owned meaning in order and only feature-owned actions", async () => {
    const user = userEvent.setup();
    const resolution = await variedFeatureGuidanceFixture();
    expect(
      await featureGuidanceIsSafe(
        resolution,
        "practice-activity",
        "write-outcome-uncertain",
        "1.0.0",
      ),
    ).toBe(true);
    const retry = vi.fn();
    render(
      <MemoryRouter initialEntries={["/learn/placements/practice-one/practice"]}>
        <FeatureGuidanceExplanation
          actionHandlers={{ retry_unchanged_request: retry }}
          conditionKey="write-outcome-uncertain"
          readFeatureGuidance={vi.fn().mockResolvedValue({
            status: "ready",
            resolution,
          })}
          surfaceKey="practice-activity"
        />
      </MemoryRouter>,
    );

    expect(
      await screen.findByRole("heading", {
        level: 3,
        name: "Review what happened before continuing",
      }),
    ).toBeVisible();
    expect(screen.getByText(/same request may already be saved/i)).toBeVisible();
    const actionList = screen.getByRole("heading", { level: 4, name: "What you can do" })
      .nextElementSibling;
    expect(actionList).not.toBeNull();
    expect(
      within(actionList as HTMLElement)
        .getAllByRole("listitem")
        .map((item) => item.textContent),
    ).toEqual([
      "Review source history",
      "Retry the same request",
      "Review safe recovery",
    ]);
    await user.click(screen.getByRole("button", { name: "Retry the same request" }));
    expect(retry).toHaveBeenCalledOnce();
    expect(screen.queryByRole("button", { name: "Return to practice" })).toBeNull();
    expect(screen.getByRole("link", { name: "Review source history" })).toHaveAttribute(
      "href",
      "/help/topics/source-and-history/versions/1.0.0?return_to=%2Flearn%2Fplacements%2Fpractice-one%2Fpractice",
    );
    expect(screen.getByRole("link", { name: "Review safe recovery" })).toHaveAttribute(
      "href",
      "/help/topics/safe-recovery/versions/1.0.0?return_to=%2Flearn%2Fplacements%2Fpractice-one%2Fpractice",
    );
  });

  it("leaves the owning task unchanged when optional Guidance is unavailable", async () => {
    render(
      <MemoryRouter>
        <main>
          <h1>Continue your practice</h1>
          <FeatureGuidanceExplanation
            conditionKey="write-outcome-uncertain"
            readFeatureGuidance={vi.fn().mockResolvedValue({
              status: "unavailable",
            })}
            surfaceKey="practice-activity"
          />
        </main>
      </MemoryRouter>,
    );

    expect(screen.getByRole("heading", { name: "Continue your practice" })).toBeVisible();
    expect(screen.queryByText("What this limit means")).toBeNull();
  });
});

describe("platform help bounded route states", () => {
  it("offers local recovery for stale search state", async () => {
    const onClear = vi.fn();
    const user = userEvent.setup();
    render(
      <PlatformHelpSearchRouteView
        onClear={onClear}
        onRetry={vi.fn()}
        state={{ status: "stale-cursor" }}
      />,
    );

    await user.click(screen.getByRole("button", { name: "Start a fresh search" }));
    expect(onClear).toHaveBeenCalledOnce();
  });

  it("does not substitute another topic version when the exact one is absent", () => {
    render(
      <PlatformHelpTopicRouteView
        onReturn={vi.fn()}
        onRetry={vi.fn()}
        state={{ status: "not-found" }}
      />,
    );

    expect(screen.getByRole("heading", { name: "Help topic not found" })).toBeVisible();
    expect(screen.getByText(/No other version was substituted/)).toBeVisible();
  });
});

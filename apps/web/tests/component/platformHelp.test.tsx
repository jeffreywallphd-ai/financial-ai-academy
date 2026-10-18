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
  it("validates both digests and preserves exact reader correlation", async () => {
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
    const resolution = await featureGuidanceFixture();
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
        name: "The result of this save is uncertain",
      }),
    ).toBeVisible();
    expect(screen.getByText(/may already be saved/)).toBeVisible();
    await user.click(screen.getByRole("button", { name: "Try the same save again" }));
    expect(retry).toHaveBeenCalledOnce();
    expect(screen.queryByRole("button", { name: "Reload saved progress" })).toBeNull();
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

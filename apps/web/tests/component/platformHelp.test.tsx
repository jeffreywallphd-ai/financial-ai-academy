import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router";
import { describe, expect, it, vi } from "vitest";

import {
  PlatformHelpSearchPage,
  PlatformHelpTopicPage,
} from "../../src/features/platform-help/PlatformHelpPage";
import {
  PlatformHelpSearchRouteView,
  PlatformHelpTopicRouteView,
} from "../../src/features/platform-help/PlatformHelpRoute";
import {
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

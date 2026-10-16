import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router";
import { describe, expect, it, vi } from "vitest";

import { CurriculumGraphPage } from "../../src/features/curriculum-graph/CurriculumGraphPage";
import {
  CurriculumGraphLoadingState,
  CurriculumGraphRouteView,
} from "../../src/features/curriculum-graph/CurriculumGraphRoute";
import {
  curriculumGraphFixture,
  navigationStateFixture,
} from "./curriculumGraphFixture";

function renderGraph() {
  return render(
    <MemoryRouter>
      <CurriculumGraphPage
        graph={curriculumGraphFixture}
        navigationState={navigationStateFixture}
      />
    </MemoryRouter>,
  );
}

describe("CurriculumGraphPage", () => {
  it("shows the approved learning path and separate activity status without implying authority", async () => {
    const user = userEvent.setup();
    renderGraph();

    expect(
      screen.getByRole("heading", { level: 1, name: "Investing Foundations" }),
    ).toBeVisible();
    expect(screen.getByText("Approved")).toBeVisible();
    expect(
      screen.getByText(
        /do not measure mastery or competency and do not recommend a path/,
      ),
    ).toBeVisible();
    expect(
      screen.getByRole("heading", { name: "Learning groups and activities" }),
    ).toBeVisible();
    expect(
      screen.getByRole("heading", { name: "How the activities connect" }),
    ).toBeVisible();
    expect(screen.getAllByText("Ready").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Finished").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Optional").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Blocked").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Not in a group").length).toBeGreaterThan(0);
    expect(
      screen.getAllByText(
        "This activity is an optional part of the learning path.",
      ).length,
    ).toBeGreaterThan(0);
    expect(screen.queryByText("Mastery")).toBeNull();
    expect(screen.getByRole("button", { name: "Review lesson" })).toBeVisible();
    expect(screen.getByRole("button", { name: "Start lesson" })).toBeVisible();

    const pageRecord = within(
      document.querySelector(".curriculum-graph__provenance")!,
    );
    await user.click(pageRecord.getByText("Technical record"));
    expect(
      pageRecord.getByText("investing-foundations@1.0.0"),
    ).toBeVisible();
    expect(pageRecord.getByText("f".repeat(64))).toBeVisible();
    expect(
      pageRecord.getByText("content:intro-risk-return@1.0.0"),
    ).toBeVisible();
    const graphSchema = pageRecord.getByText(
      "Graph schema version",
    ).parentElement;
    const navigationSchema = pageRecord.getByText(
      "Navigation schema version",
    ).parentElement;
    expect(graphSchema).not.toBeNull();
    expect(navigationSchema).not.toBeNull();
    if (!graphSchema || !navigationSchema) {
      throw new Error("Expected graph and navigation schema records.");
    }
    expect(
      within(graphSchema).getByText(curriculumGraphFixture.schema_version),
    ).toBeVisible();
    expect(
      within(navigationSchema).getByText(navigationStateFixture.schema_version),
    ).toBeVisible();
    expect(
      pageRecord.getByText(navigationStateFixture.evaluated_at),
    ).toBeVisible();
    expect(
      pageRecord.getByText(
        `${navigationStateFixture.policy_id}@${navigationStateFixture.policy_version}`,
      ),
    ).toBeVisible();
    expect(
      pageRecord.getByText(navigationStateFixture.source_set_digest),
    ).toBeVisible();
    expect(
      pageRecord.getByText(navigationStateFixture.projection_digest),
    ).toBeVisible();

    const [firstActivity] = screen.getAllByRole("article");
    expect(firstActivity).toBeDefined();
    if (!firstActivity) throw new Error("Expected at least one activity.");
    await user.click(within(firstActivity).getByText("Technical record"));
    expect(
      within(firstActivity).getByText(/intro-risk-return@1\.0\.0/),
    ).toBeVisible();
    expect(within(firstActivity).getByText("a".repeat(64))).toBeVisible();
    expect(within(firstActivity).getByText("activity_completed")).toBeVisible();
    expect(within(firstActivity).getByText("branch-core")).toBeVisible();
    expect(
      within(firstActivity).getByText(
        "The retained completion evidence records this activity as completed.",
      ),
    ).toBeVisible();
  });

  it("defaults to a semantic list and keeps every fact when switching to the peer map", async () => {
    const user = userEvent.setup();
    renderGraph();

    const listButton = screen.getByRole("button", { name: "List view" });
    const mapButton = screen.getByRole("button", { name: "Map view" });
    expect(listButton).toHaveAttribute("aria-pressed", "true");
    const list = screen.getByTestId("curriculum-graph-list");
    const listText = list.textContent;
    const expectedActivityCards = curriculumGraphFixture.activities.reduce(
      (count, activity) =>
        count +
        Math.max(
          1,
          curriculumGraphFixture.branches.filter((branch) =>
            branch.activity_ids.includes(activity.activity_id),
          ).length,
        ),
      0,
    );
    expect(within(list).getAllByRole("article")).toHaveLength(
      expectedActivityCards,
    );
    expect(
      within(list).getByRole("heading", {
        name: "Activities outside learning groups",
      }),
    ).toBeVisible();

    await user.click(mapButton);
    expect(mapButton).toHaveAttribute("aria-pressed", "true");
    expect(listButton).toHaveAttribute("aria-pressed", "false");
    const map = screen.getByTestId("curriculum-graph-map");
    expect(map.textContent).toBe(listText);
    expect(within(map).getAllByRole("article")).toHaveLength(
      expectedActivityCards,
    );
  });

  it("renders valid graphs without presentation hints or branch assumptions", () => {
    const flexibleGraph = {
      ...structuredClone(curriculumGraphFixture),
      presentation_order: null,
      branches: [],
      relationships: [],
    };
    render(
      <MemoryRouter>
        <CurriculumGraphPage
          graph={flexibleGraph}
          navigationState={navigationStateFixture}
        />
      </MemoryRouter>,
    );

    expect(
      screen.getByText(/does not use groups/i),
    ).toBeVisible();
    expect(
      screen.getByText(/does not list any connections/i),
    ).toBeVisible();
    expect(screen.getAllByRole("article")).toHaveLength(
      curriculumGraphFixture.activities.length,
    );
  });

  it("offers only server-checked lesson actions and preserves them in the peer map", async () => {
    const user = userEvent.setup();
    const onLaunch = vi.fn();
    render(
      <MemoryRouter>
        <CurriculumGraphPage
          graph={curriculumGraphFixture}
          navigationState={navigationStateFixture}
          onLaunch={onLaunch}
        />
      </MemoryRouter>,
    );

    await user.click(screen.getByRole("button", { name: "Review lesson" }));
    expect(onLaunch).toHaveBeenCalledWith("activity-risk-return-lesson");
    for (const heading of screen.getAllByRole("heading", {
      level: 4,
      name: "Explore diversification",
    })) {
      expect(heading.closest("article")).not.toHaveTextContent(
        /start lesson|review lesson/i,
      );
    }
    expect(
      screen.getByRole("heading", {
        name: "Check risk and return understanding",
      }).closest("article"),
    ).not.toHaveTextContent(/start lesson|review lesson/i);

    await user.click(screen.getByRole("button", { name: "Map view" }));
    expect(screen.getByRole("button", { name: "Review lesson" })).toBeVisible();
    expect(screen.getByRole("button", { name: "Start lesson" })).toBeVisible();
  });

  it("marks refreshed current position in text and non-color semantics", async () => {
    const user = userEvent.setup();
    render(
      <MemoryRouter>
        <CurriculumGraphPage
          currentActivityId="activity-risk-return-lesson"
          graph={curriculumGraphFixture}
          launchState={{
            status: "blocked",
            activityId: "activity-risk-return-lesson",
          }}
          navigationState={navigationStateFixture}
        />
      </MemoryRouter>,
    );

    const current = screen.getByText("Current activity").closest("article");
    expect(current).toHaveAttribute("aria-current", "step");
    expect(current).toHaveTextContent(/not ready to open/i);

    await user.click(screen.getByRole("button", { name: "Map view" }));
    expect(screen.getByText("Current activity").closest("article")).toHaveAttribute(
      "aria-current",
      "step",
    );
  });
});

describe("CurriculumGraphRouteView", () => {
  it("describes loading in learner task terms", () => {
    render(<CurriculumGraphLoadingState />);

    const status = screen.getByRole("status");
    expect(
      within(status).getByRole("heading", {
        name: "Loading your learning path",
      }),
    ).toBeVisible();
    expect(status).toHaveTextContent(/current activities and their status/i);
    expect(status).not.toHaveTextContent(
      /curriculum graph|navigation|projection|server|session establishment/i,
    );
  });

  it.each([
    ["invalid-selection", "Learning path link unavailable"],
    ["unauthorized", "Learner access required"],
    ["forbidden", "Learning path access unavailable"],
    ["not-found", "Learning path version not found"],
    ["unavailable", "Learning path temporarily unavailable"],
    ["invalid-response", "Learning path unavailable"],
    ["unexpected", "Something went wrong"],
  ] as const)("renders the bounded %s state", (status, title) => {
    render(
      <MemoryRouter>
        <CurriculumGraphRouteView
          onCatalog={vi.fn()}
          onRetry={vi.fn()}
          state={{ status }}
        />
      </MemoryRouter>,
    );
    expect(screen.getByRole("heading", { name: title })).toBeVisible();
    expect(screen.queryByText("Investing Foundations")).toBeNull();
    expect(
      screen.getByRole("heading", { name: title }).parentElement,
    ).not.toHaveTextContent(
      /curriculum graph|navigation state|projection|server/i,
    );
  });

  it("provides bounded retry and return actions", async () => {
    const user = userEvent.setup();
    const onRetry = vi.fn();
    const onCatalog = vi.fn();
    const { rerender } = render(
      <MemoryRouter>
        <CurriculumGraphRouteView
          onCatalog={onCatalog}
          onRetry={onRetry}
          state={{ status: "unavailable" }}
        />
      </MemoryRouter>,
    );
    await user.click(screen.getByRole("button", { name: "Try again" }));
    expect(onRetry).toHaveBeenCalledOnce();

    rerender(
      <MemoryRouter>
        <CurriculumGraphRouteView
          onCatalog={onCatalog}
          onRetry={onRetry}
          state={{ status: "not-found" }}
        />
      </MemoryRouter>,
    );
    await user.click(
      screen.getByRole("button", { name: "Return to learning library" }),
    );
    expect(onCatalog).toHaveBeenCalledOnce();
  });
});

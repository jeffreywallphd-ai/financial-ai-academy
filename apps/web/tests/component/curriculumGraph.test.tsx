import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router";
import { describe, expect, it, vi } from "vitest";

import { CurriculumGraphPage } from "../../src/features/curriculum-graph/CurriculumGraphPage";
import { CurriculumGraphRouteView } from "../../src/features/curriculum-graph/CurriculumGraphRoute";
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
    expect(screen.queryByRole("link", { name: /open|start|launch/i })).toBeNull();

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
});

describe("CurriculumGraphRouteView", () => {
  it.each([
    ["invalid-selection", "Curriculum graph link unavailable"],
    ["unauthorized", "Learner session required"],
    ["forbidden", "Curriculum graph access unavailable"],
    ["not-found", "Curriculum graph version not found"],
    ["unavailable", "Curriculum graph temporarily unavailable"],
    ["invalid-response", "Curriculum graph response unavailable"],
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
      screen.getByRole("button", { name: "Return to catalog" }),
    );
    expect(onCatalog).toHaveBeenCalledOnce();
  });
});

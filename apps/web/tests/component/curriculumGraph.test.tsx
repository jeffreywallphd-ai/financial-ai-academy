import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router";
import { describe, expect, it, vi } from "vitest";

import { CurriculumGraphPage } from "../../src/features/curriculum-graph/CurriculumGraphPage";
import { CurriculumGraphRouteView } from "../../src/features/curriculum-graph/CurriculumGraphRoute";
import { curriculumGraphFixture } from "./curriculumGraphFixture";

function renderGraph() {
  return render(
    <MemoryRouter>
      <CurriculumGraphPage graph={curriculumGraphFixture} />
    </MemoryRouter>,
  );
}

describe("CurriculumGraphPage", () => {
  it("shows the exact reviewed graph and provenance without implying learner state", () => {
    renderGraph();

    expect(
      screen.getByRole("heading", { level: 1, name: "Investing Foundations" }),
    ).toBeVisible();
    expect(screen.getByText("investing-foundations@1.0.0")).toBeVisible();
    expect(screen.getByText("Approved")).toBeVisible();
    expect(
      screen.getByText(
        /does not calculate eligibility, completion, mastery, or a personalized path/,
      ),
    ).toBeVisible();
    expect(screen.getByText("f".repeat(64))).toBeInTheDocument();
    expect(screen.getByText("content:intro-risk-return@1.0.0")).toBeVisible();
    expect(screen.queryByText(/you are eligible/i)).toBeNull();
    expect(screen.queryByText(/you completed/i)).toBeNull();
    expect(screen.queryByRole("link", { name: /open|start|launch/i })).toBeNull();
  });

  it("defaults to a semantic list and keeps every fact when switching to the peer map", async () => {
    const user = userEvent.setup();
    renderGraph();

    const listButton = screen.getByRole("button", { name: "List view" });
    const mapButton = screen.getByRole("button", { name: "Map view" });
    expect(listButton).toHaveAttribute("aria-pressed", "true");
    const list = screen.getByTestId("curriculum-graph-list");
    const listText = list.textContent;
    expect(within(list).getAllByRole("article")).toHaveLength(6);
    expect(
      within(list).getByRole("heading", {
        name: "Activities outside branch groupings",
      }),
    ).toBeVisible();
    expect(
      within(list).getAllByRole("heading", {
        name: "Explore diversification",
      }),
    ).toHaveLength(3);

    await user.click(mapButton);
    expect(mapButton).toHaveAttribute("aria-pressed", "true");
    expect(listButton).toHaveAttribute("aria-pressed", "false");
    const map = screen.getByTestId("curriculum-graph-map");
    expect(map.textContent).toBe(listText);
    expect(within(map).getAllByRole("article")).toHaveLength(6);
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
        <CurriculumGraphPage graph={flexibleGraph} />
      </MemoryRouter>,
    );

    expect(
      screen.getByText(/does not define branch groupings/i),
    ).toBeVisible();
    expect(screen.getByText(/No relationships are declared/i)).toBeVisible();
    expect(screen.getAllByRole("article")).toHaveLength(5);
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

import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router";
import { describe, expect, it, vi } from "vitest";

import { LearningCatalogPage } from "../../src/features/learning-catalog/LearningCatalogPage";
import { LearningCatalogRouteView } from "../../src/features/learning-catalog/LearningCatalogRoute";
import {
  availableOpportunity,
  learningQueryPageFixture,
  plannedOpportunity,
} from "./learningCatalogFixture";

function renderCatalog(page = learningQueryPageFixture) {
  return render(
    <MemoryRouter>
      <LearningCatalogPage page={page} />
    </MemoryRouter>,
  );
}

describe("LearningCatalogPage", () => {
  it("preserves the supplied order and presents exact facts and provenance", () => {
    renderCatalog();

    const cards = screen.getAllByRole("article");
    expect(cards).toHaveLength(2);
    const firstCard = cards[0];
    const secondCard = cards[1];
    if (!firstCard || !secondCard) {
      throw new Error("Expected two catalog cards.");
    }
    expect(
      within(firstCard).getByRole("heading", { level: 2 }),
    ).toHaveTextContent("Cash Flow Basics");
    expect(
      within(secondCard).getByRole("heading", { level: 2 }),
    ).toHaveTextContent("Portfolio Project");
    expect(screen.getByText("cash-flow-basics@1.2.0")).toBeVisible();
    expect(screen.getAllByText(/Financial AI Academy/)).not.toHaveLength(0);
    expect(
      screen.getByText("The exact reviewed lesson is available."),
    ).toBeVisible();
  });

  it("links only an available lesson to its exact destination", () => {
    renderCatalog();

    expect(
      screen.getByRole("link", { name: "Open exact lesson" }),
    ).toHaveAttribute("href", "/learn/placements/cash-flow-basics-primary");
    const plannedCard = screen
      .getByRole("heading", { name: plannedOpportunity.title })
      .closest("article");
    expect(plannedCard).not.toBeNull();
    expect(
      within(plannedCard as HTMLElement).queryByRole("link", {
        name: "Open exact lesson",
      }),
    ).toBeNull();
    expect(
      within(plannedCard as HTMLElement).getByRole("link", {
        name: "View details",
      }),
    ).toHaveAttribute(
      "href",
      "/learn/opportunities/portfolio-project-planned?return_to=%2Flearn",
    );
    expect(
      within(plannedCard as HTMLElement).getByText(
        plannedOpportunity.availability_reason,
      ),
    ).toBeVisible();
  });

  it("renders an educational empty state without inventing recommendations", () => {
    renderCatalog({
      ...learningQueryPageFixture,
      records: [],
      total_matches: 0,
    });

    expect(
      screen.getByRole("heading", {
        name: "No opportunities match this query",
      }),
    ).toBeVisible();
    expect(screen.queryByRole("article")).not.toBeInTheDocument();
    expect(document.body.textContent).not.toMatch(/recommended for you/i);
  });

  it("exposes optional native query controls and preserves canonical paging state", () => {
    renderCatalog({
      ...learningQueryPageFixture,
      applied_query: {
        ...learningQueryPageFixture.applied_query,
        query: "cash flow",
        levels: ["introductory"],
        page_size: 17,
      },
      next_cursor: `cursor.${"d".repeat(64)}`,
    });

    expect(
      screen.getByRole("searchbox", { name: "Search opportunities" }),
    ).toHaveValue("cash flow");
    expect(screen.getByRole("button", { name: "Apply query" })).toBeVisible();
    expect(
      screen.getByRole("spinbutton", { name: "Results per page" }),
    ).toHaveValue(17);
    expect(screen.getByRole("link", { name: "Clear filters" })).toHaveAttribute(
      "href",
      "/learn",
    );
    expect(screen.getByRole("link", { name: "Next page" })).toHaveAttribute(
      "href",
      `/learn?query=cash+flow&level=introductory&page_size=17&cursor=cursor.${"d".repeat(64)}`,
    );
    expect(
      screen.getAllByRole("link", { name: "View details" })[0],
    ).toHaveAttribute(
      "href",
      "/learn/opportunities/cash-flow-basics-primary?return_to=%2Flearn%3Fquery%3Dcash%2Bflow%26level%3Dintroductory%26page_size%3D17",
    );
  });

  it("builds a bounded transient comparison in learner selection order", async () => {
    const user = userEvent.setup();
    renderCatalog();

    const compare = screen.getByRole("button", { name: "Compare selected" });
    expect(compare).toBeDisabled();

    await user.click(
      screen.getByRole("checkbox", { name: "Compare Portfolio Project" }),
    );
    expect(compare).toBeDisabled();
    await user.click(
      screen.getByRole("checkbox", { name: "Compare Cash Flow Basics" }),
    );

    expect(compare).toBeEnabled();
    expect(screen.getByText("2 of 4 selected. Ready to compare.")).toBeVisible();
    const form = compare.closest("form");
    expect(form).not.toBeNull();
    expect(form).toHaveAttribute("action", "/learn/opportunities/compare");
    expect(form).toHaveAttribute("method", "get");
    expect(
      Array.from(
        (form as HTMLFormElement).querySelectorAll<HTMLInputElement>(
          'input[name="opportunity"]',
        ),
        (input) => input.value,
      ),
    ).toEqual(["portfolio-project-planned", "cash-flow-basics-primary"]);
    expect(
      (form as HTMLFormElement).querySelector<HTMLInputElement>(
        'input[name="return_to"]',
      ),
    ).toHaveValue("/learn");

    await user.click(screen.getByRole("button", { name: "Clear comparison" }));
    expect(compare).toBeDisabled();
    expect(
      (form as HTMLFormElement).querySelectorAll('input[name="opportunity"]'),
    ).toHaveLength(0);
  });

  it("prevents a fifth comparison selection without requiring saved state", async () => {
    const user = userEvent.setup();
    const records = Array.from({ length: 5 }, (_, index) => ({
      ...availableOpportunity,
      opportunity_id: `comparison-option-${index + 1}`,
      placement_id: `comparison-option-${index + 1}`,
      destination: `/learn/placements/comparison-option-${index + 1}`,
      title: `Comparison Option ${index + 1}`,
    }));
    renderCatalog({
      ...learningQueryPageFixture,
      records,
      total_matches: records.length,
    });

    for (let index = 1; index <= 4; index += 1) {
      await user.click(
        screen.getByRole("checkbox", {
          name: `Compare Comparison Option ${index}`,
        }),
      );
    }

    expect(
      screen.getByRole("checkbox", { name: "Compare Comparison Option 5" }),
    ).toBeDisabled();
    expect(screen.getByText("4 of 4 selected. Ready to compare.")).toBeVisible();
  });

  it("does not carry transient selections onto a different result page", async () => {
    const user = userEvent.setup();
    const rendered = renderCatalog();
    await user.click(
      screen.getByRole("checkbox", { name: "Compare Cash Flow Basics" }),
    );
    await user.click(
      screen.getByRole("checkbox", { name: "Compare Portfolio Project" }),
    );
    expect(screen.getByText("2 of 4 selected. Ready to compare.")).toBeVisible();

    rendered.rerender(
      <MemoryRouter>
        <LearningCatalogPage
          page={{
            ...learningQueryPageFixture,
            records: [plannedOpportunity],
            total_matches: 1,
          }}
        />
      </MemoryRouter>,
    );

    expect(
      screen.getByText(
        "0 of 4 selected. Select at least 2 opportunities to compare.",
      ),
    ).toBeVisible();
    expect(
      screen.getByRole("checkbox", { name: "Compare Portfolio Project" }),
    ).not.toBeChecked();
    expect(
      screen.getByRole("button", { name: "Compare selected" }),
    ).toBeDisabled();
  });
});

describe("LearningCatalogRouteView", () => {
  it.each([
    ["unauthorized", "Learner session required"],
    ["forbidden", "Catalog access unavailable"],
    ["unavailable", "Catalog temporarily unavailable"],
    ["invalid-query", "Query could not be applied"],
    ["stale-cursor", "Catalog results changed"],
    ["invalid-response", "Catalog response unavailable"],
    ["unexpected", "Something went wrong"],
  ] as const)("renders bounded %s state", (status, heading) => {
    render(<LearningCatalogRouteView onRetry={vi.fn()} state={{ status }} />);

    expect(
      screen.getByRole("heading", { level: 1, name: heading }),
    ).toBeVisible();
    expect(screen.queryByText("Cash Flow Basics")).not.toBeInTheDocument();
    expect(document.body.textContent).not.toContain("a".repeat(64));
  });
});

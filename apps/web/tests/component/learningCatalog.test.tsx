import { render, screen, within } from "@testing-library/react";
import { MemoryRouter } from "react-router";
import { describe, expect, it, vi } from "vitest";

import { LearningCatalogPage } from "../../src/features/learning-catalog/LearningCatalogPage";
import { LearningCatalogRouteView } from "../../src/features/learning-catalog/LearningCatalogRoute";
import {
  learningCatalogFixture,
  plannedOpportunity,
} from "./learningCatalogFixture";

function renderCatalog(catalog = learningCatalogFixture) {
  return render(
    <MemoryRouter>
      <LearningCatalogPage catalog={catalog} />
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
    expect(within(firstCard).getByRole("heading", { level: 2 })).toHaveTextContent(
      "Cash Flow Basics",
    );
    expect(within(secondCard).getByRole("heading", { level: 2 })).toHaveTextContent(
      "Portfolio Project",
    );
    expect(screen.getByText("cash-flow-basics@1.2.0")).toBeVisible();
    expect(screen.getAllByText(/Financial AI Academy/)).not.toHaveLength(0);
  });

  it("links only an available lesson to its exact destination", () => {
    renderCatalog();

    expect(screen.getByRole("link", { name: "Open exact lesson" })).toHaveAttribute(
      "href",
      "/learn/placements/cash-flow-basics-primary",
    );
    const plannedCard = screen
      .getByRole("heading", { name: plannedOpportunity.title })
      .closest("article");
    expect(plannedCard).not.toBeNull();
    expect(within(plannedCard as HTMLElement).queryByRole("link")).toBeNull();
    expect(
      within(plannedCard as HTMLElement).getByText(
        plannedOpportunity.availability_reason,
      ),
    ).toBeVisible();
  });

  it("renders an educational empty state without inventing recommendations", () => {
    renderCatalog({ ...learningCatalogFixture, records: [] });

    expect(
      screen.getByRole("heading", { name: "No approved opportunities yet" }),
    ).toBeVisible();
    expect(screen.queryByRole("article")).not.toBeInTheDocument();
    expect(document.body.textContent).not.toMatch(/recommended for you/i);
  });
});

describe("LearningCatalogRouteView", () => {
  it.each([
    ["unauthorized", "Learner session required"],
    ["forbidden", "Catalog access unavailable"],
    ["unavailable", "Catalog temporarily unavailable"],
    ["invalid-response", "Catalog response unavailable"],
    ["unexpected", "Something went wrong"],
  ] as const)("renders bounded %s state", (status, heading) => {
    render(
      <LearningCatalogRouteView
        onRetry={vi.fn()}
        state={{ status }}
      />,
    );

    expect(screen.getByRole("heading", { level: 1, name: heading })).toBeVisible();
    expect(screen.queryByText("Cash Flow Basics")).not.toBeInTheDocument();
    expect(document.body.textContent).not.toContain("a".repeat(64));
  });
});

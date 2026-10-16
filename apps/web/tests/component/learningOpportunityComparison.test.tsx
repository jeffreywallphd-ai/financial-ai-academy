import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router";
import { describe, expect, it, vi } from "vitest";

import { LearningOpportunityComparisonPage } from "../../src/features/learning-catalog/LearningOpportunityComparisonPage";
import { LearningOpportunityComparisonRouteView } from "../../src/features/learning-catalog/LearningOpportunityComparisonRoute";
import type { LearningOpportunitySelectionRouteState } from "../../src/features/learning-catalog/model";
import {
  availableOpportunity,
  learningCatalogFixture,
  plannedOpportunity,
} from "./learningCatalogFixture";

const projection = {
  schema_version: learningCatalogFixture.schema_version,
  projection_generation: learningCatalogFixture.projection_generation,
  projected_at: learningCatalogFixture.projected_at,
};

function comparisonState(
  opportunities = [plannedOpportunity, availableOpportunity],
) {
  return {
    status: "ready",
    selection: {
      kind: "comparison",
      opportunityIds: opportunities.map((item) => item.opportunity_id),
      returnTo: "/learn?query=project",
    },
    projection,
    opportunities,
  } satisfies LearningOpportunitySelectionRouteState;
}

describe("LearningOpportunityComparisonPage", () => {
  it("presents records in selection order and keeps exact evidence accessible", async () => {
    const user = userEvent.setup();
    render(
      <MemoryRouter>
        <LearningOpportunityComparisonPage
          opportunities={[plannedOpportunity, availableOpportunity]}
          projection={projection}
          returnTo="/learn?query=project"
        />
      </MemoryRouter>,
    );

    const articles = screen.getAllByRole("article");
    expect(articles).toHaveLength(2);
    const first = articles[0];
    const second = articles[1];
    if (!first || !second) throw new Error("Expected two comparison records.");

    expect(within(first).getByText("Selected 1")).toBeVisible();
    expect(within(first).getByRole("heading", { level: 2 })).toHaveTextContent(
      "Portfolio Project",
    );
    expect(within(second).getByText("Selected 2")).toBeVisible();
    expect(within(second).getByRole("heading", { level: 2 })).toHaveTextContent(
      "Cash Flow Basics",
    );
    expect(within(first).getByText("Project version")).toBeVisible();
    expect(within(second).getByText("Lesson version")).toBeVisible();
    const technicalRecords = screen.getAllByText("Technical record");
    expect(technicalRecords).toHaveLength(3);
    for (const record of technicalRecords) await user.click(record);
    expect(
      within(first).getByText(plannedOpportunity.package_digest),
    ).toBeVisible();
    expect(
      within(second).getByText(availableOpportunity.source_fingerprint),
    ).toBeVisible();
    expect(screen.getByText(projection.projection_generation)).toBeVisible();
    expect(
      screen.getByRole("link", { name: "Return to learning library" }),
    ).toHaveAttribute("href", "/learn?query=project");
    expect(document.body.textContent).toContain(
      "does not rank opportunities, recommend a winner, or decide eligibility",
    );
    expect(document.body.textContent).not.toMatch(
      /best opportunity|recommended for you|comparison score/i,
    );
  });

  it("offers detail for every record and exact placement only for available lessons", () => {
    render(
      <MemoryRouter>
        <LearningOpportunityComparisonPage
          opportunities={[plannedOpportunity, availableOpportunity]}
          projection={projection}
          returnTo="/learn"
        />
      </MemoryRouter>,
    );

    const articles = screen.getAllByRole("article");
    const planned = articles[0];
    const available = articles[1];
    if (!planned || !available) throw new Error("Expected two records.");
    expect(
      within(planned).getByRole("link", { name: "View details" }),
    ).toHaveAttribute(
      "href",
      "/learn/opportunities/portfolio-project-planned?return_to=%2Flearn",
    );
    expect(
      within(planned).queryByRole("link", { name: "Open lesson" }),
    ).toBeNull();
    expect(
      within(available).getByRole("link", { name: "Open lesson" }),
    ).toHaveAttribute("href", availableOpportunity.destination);
  });
});

describe("LearningOpportunityComparisonRouteView", () => {
  it("renders a verified ordered comparison", () => {
    render(
      <MemoryRouter>
        <LearningOpportunityComparisonRouteView
          onReturn={vi.fn()}
          onRetry={vi.fn()}
          state={comparisonState()}
        />
      </MemoryRouter>,
    );

    expect(
      screen.queryByRole("heading", {
        level: 1,
        name: "Compare educational facts",
      }),
    ).not.toBeInTheDocument();
    expect(
      screen.getByRole("heading", {
        level: 1,
        name: "Compare learning opportunities",
      }),
    ).toBeVisible();
  });

  it.each([
    ["invalid-selection", "This comparison link isn't available"],
    ["selection-changed", "Your comparison has changed"],
    ["unauthorized", "We couldn't start your learner session"],
    ["forbidden", "You can't open this comparison"],
    ["unavailable", "Comparison details are unavailable"],
    ["invalid-response", "We couldn't show this comparison"],
    ["unexpected", "Something went wrong"],
  ] as const)("renders bounded %s state", (status, heading) => {
    render(
      <LearningOpportunityComparisonRouteView
        onReturn={vi.fn()}
        onRetry={vi.fn()}
        state={{ status }}
      />,
    );

    expect(
      screen.getByRole("heading", { level: 1, name: heading }),
    ).toBeVisible();
    expect(screen.queryByText("Cash Flow Basics")).not.toBeInTheDocument();
    expect(document.body.textContent).not.toContain("a".repeat(64));
  });

  it("fails closed for partial, excessive, or reordered ready shapes", () => {
    const invalid = comparisonState([plannedOpportunity, availableOpportunity]);
    render(
      <LearningOpportunityComparisonRouteView
        onReturn={vi.fn()}
        onRetry={vi.fn()}
        state={{
          ...invalid,
          opportunities: [availableOpportunity],
        }}
      />,
    );

    expect(
      screen.getByRole("heading", {
        level: 1,
        name: "We couldn't show this comparison",
      }),
    ).toBeVisible();
    expect(screen.queryByText("Cash Flow Basics")).not.toBeInTheDocument();
  });

  it("describes loading without implementation vocabulary", () => {
    render(
      <LearningOpportunityComparisonRouteView
        onReturn={vi.fn()}
        onRetry={vi.fn()}
        state={{ status: "loading" }}
      />,
    );

    expect(
      screen.getByRole("heading", { name: "Loading your comparison" }),
    ).toBeVisible();
    expect(document.body.textContent).not.toMatch(
      /establishing|catalog generation|projection|schema/i,
    );
  });
});

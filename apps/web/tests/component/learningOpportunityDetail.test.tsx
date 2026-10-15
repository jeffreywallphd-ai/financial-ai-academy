import { render, screen, within } from "@testing-library/react";
import { MemoryRouter } from "react-router";
import { describe, expect, it, vi } from "vitest";

import { LearningOpportunityDetailPage } from "../../src/features/learning-catalog/LearningOpportunityDetailPage";
import { LearningOpportunityDetailRouteView } from "../../src/features/learning-catalog/LearningOpportunityDetailRoute";
import type {
  LearningOpportunity,
  LearningOpportunitySelectionRouteState,
} from "../../src/features/learning-catalog/model";
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

function renderDetail(
  opportunity: LearningOpportunity = availableOpportunity,
  returnTo = "/learn?query=cash",
) {
  return render(
    <MemoryRouter>
      <LearningOpportunityDetailPage
        opportunity={opportunity}
        projection={projection}
        returnTo={returnTo}
      />
    </MemoryRouter>,
  );
}

describe("LearningOpportunityDetailPage", () => {
  it("presents exact current facts, provenance, limitations, and destinations", () => {
    renderDetail();

    expect(
      screen.getByRole("heading", { level: 1, name: "Cash Flow Basics" }),
    ).toBeVisible();
    expect(screen.getByText("cash-flow-basics-primary")).toBeVisible();
    expect(screen.getByText("cash-flow-basics@1.2.0")).toBeVisible();
    expect(screen.getByText(availableOpportunity.package_digest)).toBeVisible();
    expect(
      screen.getByText(availableOpportunity.source_fingerprint),
    ).toBeVisible();
    expect(
      screen.getByText(learningCatalogFixture.projection_generation),
    ).toBeVisible();
    expect(
      screen.getByText(availableOpportunity.provenance.educational_use_notice),
    ).toBeVisible();
    expect(
      screen.getByText(availableOpportunity.availability_reason),
    ).toBeVisible();
    expect(
      screen.getByRole("link", { name: "Open exact lesson" }),
    ).toHaveAttribute("href", availableOpportunity.destination);
    expect(
      screen.getByRole("link", { name: "Return to catalog" }),
    ).toHaveAttribute("href", "/learn?query=cash");
    expect(document.body.textContent).not.toMatch(/recommended for you/i);
    expect(document.body.textContent).not.toMatch(/eligible/i);
  });

  it("keeps planned and non-lesson kinds honest and non-executable", () => {
    renderDetail(plannedOpportunity, "/learn");

    const actions = screen.getByRole("complementary", {
      name: "Opportunity availability and actions",
    });
    expect(
      within(actions).getByText(plannedOpportunity.availability_reason),
    ).toBeVisible();
    expect(
      within(actions).queryByRole("link", { name: "Open exact lesson" }),
    ).toBeNull();
    expect(
      within(actions).getByRole("link", { name: "Return to catalog" }),
    ).toHaveAttribute("href", "/learn");
  });
});

describe("LearningOpportunityDetailRouteView", () => {
  it("renders one verified detail selection", () => {
    const state = {
      status: "ready",
      selection: {
        kind: "detail",
        opportunityIds: [availableOpportunity.opportunity_id],
        returnTo: "/learn",
      },
      projection,
      opportunities: [availableOpportunity],
    } satisfies LearningOpportunitySelectionRouteState;

    render(
      <MemoryRouter>
        <LearningOpportunityDetailRouteView
          onReturn={vi.fn()}
          onRetry={vi.fn()}
          state={state}
        />
      </MemoryRouter>,
    );

    expect(
      screen.getByRole("heading", { level: 1, name: "Cash Flow Basics" }),
    ).toBeVisible();
  });

  it.each([
    ["invalid-selection", "Opportunity link unavailable"],
    ["selection-changed", "Opportunity changed"],
    ["unauthorized", "Learner session required"],
    ["forbidden", "Opportunity access unavailable"],
    ["unavailable", "Opportunity temporarily unavailable"],
    ["invalid-response", "Opportunity response unavailable"],
    ["unexpected", "Something went wrong"],
  ] as const)("renders bounded %s state", (status, heading) => {
    render(
      <LearningOpportunityDetailRouteView
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

  it("fails closed when a ready state is not one exact detail record", () => {
    render(
      <LearningOpportunityDetailRouteView
        onReturn={vi.fn()}
        onRetry={vi.fn()}
        state={{
          status: "ready",
          selection: {
            kind: "comparison",
            opportunityIds: [
              availableOpportunity.opportunity_id,
              plannedOpportunity.opportunity_id,
            ],
            returnTo: "/learn",
          },
          projection,
          opportunities: [availableOpportunity, plannedOpportunity],
        }}
      />,
    );

    expect(
      screen.getByRole("heading", {
        level: 1,
        name: "Opportunity response unavailable",
      }),
    ).toBeVisible();
    expect(screen.queryByText("Cash Flow Basics")).not.toBeInTheDocument();
  });
});

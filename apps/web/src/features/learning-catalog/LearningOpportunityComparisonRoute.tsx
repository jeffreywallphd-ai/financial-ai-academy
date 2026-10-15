import {
  useLoaderData,
  useNavigate,
  useNavigation,
  useRevalidator,
} from "react-router";

import { StatusPanel } from "../../components/StatusPanel";
import { LearningOpportunityComparisonPage } from "./LearningOpportunityComparisonPage";
import type { LearningOpportunitySelectionRouteState } from "./model";

type ComparisonRouteState =
  | LearningOpportunitySelectionRouteState
  | { status: "loading" };

export function LearningOpportunityComparisonLoadingState() {
  return (
    <section
      aria-atomic="true"
      aria-live="polite"
      className="catalog-loading"
      role="status"
    >
      <p className="eyebrow">Current learning opportunities</p>
      <h1>Loading comparison</h1>
      <p>
        Establishing the private learner session and checking the complete
        current catalog generation.
      </p>
      <div aria-hidden="true" className="loading-placeholder" />
      <span className="visually-hidden">Comparison loading in progress.</span>
    </section>
  );
}

export function LearningOpportunityComparisonRouteView({
  onReturn,
  onRetry,
  state,
}: {
  onReturn: () => void;
  onRetry: () => void;
  state: ComparisonRouteState;
}) {
  switch (state.status) {
    case "loading":
      return <LearningOpportunityComparisonLoadingState />;
    case "ready": {
      const ids = state.selection.opportunityIds;
      const shapeIsValid =
        state.selection.kind === "comparison" &&
        ids.length >= 2 &&
        ids.length <= 4 &&
        state.opportunities.length === ids.length &&
        state.opportunities.every(
          (opportunity, index) => opportunity.opportunity_id === ids[index],
        );
      if (!shapeIsValid) {
        return (
          <StatusPanel
            actionLabel="Return to catalog"
            description="The selected opportunities did not have a valid comparison shape, so no partial records were displayed."
            icon="error-circle"
            onAction={onReturn}
            title="Comparison response unavailable"
            tone="danger"
          />
        );
      }
      return (
        <LearningOpportunityComparisonPage
          opportunities={state.opportunities}
          projection={state.projection}
          returnTo={state.selection.returnTo}
        />
      );
    }
    case "invalid-selection":
      return (
        <StatusPanel
          actionLabel="Return to catalog"
          description="Select two through four distinct current opportunities. No catalog record or client-supplied fact was displayed."
          icon="info-circle"
          onAction={onReturn}
          title="Comparison link unavailable"
          tone="info"
        />
      );
    case "selection-changed":
      return (
        <StatusPanel
          actionLabel="Return to catalog"
          description="At least one selection is not in the current catalog generation. A partial comparison was not substituted."
          icon="info-circle"
          onAction={onReturn}
          title="Comparison changed"
          tone="info"
        />
      );
    case "unauthorized":
      return (
        <StatusPanel
          actionLabel="Try again"
          description="A private learner session could not be established. No comparison details were shown."
          icon="lock"
          onAction={onRetry}
          title="Learner session required"
          tone="warning"
        />
      );
    case "forbidden":
      return (
        <StatusPanel
          actionLabel="Return to catalog"
          description="This local learner profile is not permitted to compare the selected opportunities."
          icon="lock"
          onAction={onReturn}
          title="Comparison access unavailable"
          tone="warning"
        />
      );
    case "unavailable":
      return (
        <StatusPanel
          actionLabel="Try again"
          description="The current comparison could not be loaded right now. No stale or partial records were displayed."
          icon="warning-triangle"
          onAction={onRetry}
          title="Comparison temporarily unavailable"
          tone="warning"
        />
      );
    case "invalid-response":
      return (
        <StatusPanel
          actionLabel="Return to catalog"
          description="The catalog response did not pass its safety checks, so no partial comparison was displayed."
          icon="error-circle"
          onAction={onReturn}
          title="Comparison response unavailable"
          tone="danger"
        />
      );
    case "unexpected":
      return (
        <StatusPanel
          actionLabel="Try again"
          description="The comparison could not be completed safely. No technical or private details were displayed."
          icon="error-circle"
          onAction={onRetry}
          title="Something went wrong"
          tone="danger"
        />
      );
  }
}

export function LearningOpportunityComparisonRoute() {
  const state = useLoaderData<LearningOpportunitySelectionRouteState>();
  const navigate = useNavigate();
  const navigation = useNavigation();
  const revalidator = useRevalidator();
  const displayedState =
    navigation.state === "loading" || revalidator.state === "loading"
      ? ({ status: "loading" } as const)
      : state;
  return (
    <LearningOpportunityComparisonRouteView
      onReturn={() => void navigate("/learn")}
      onRetry={() => revalidator.revalidate()}
      state={displayedState}
    />
  );
}

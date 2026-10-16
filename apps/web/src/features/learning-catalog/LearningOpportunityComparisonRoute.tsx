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
  LearningOpportunitySelectionRouteState | { status: "loading" };

export function LearningOpportunityComparisonLoadingState() {
  return (
    <section
      aria-atomic="true"
      aria-live="polite"
      className="catalog-loading"
      role="status"
    >
      <p className="eyebrow">Learning opportunities</p>
      <h1>Loading your comparison</h1>
      <p>Starting your learner session and checking the current details.</p>
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
            actionLabel="Return to learning library"
            description="We couldn't safely compare these opportunities. No incomplete details were shown."
            icon="error-circle"
            onAction={onReturn}
            title="We couldn't show this comparison"
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
          actionLabel="Return to learning library"
          description="Choose two to four different opportunities from the current learning library. No learning details were shown."
          icon="info-circle"
          onAction={onReturn}
          title="This comparison link isn't available"
          tone="info"
        />
      );
    case "selection-changed":
      return (
        <StatusPanel
          actionLabel="Return to learning library"
          description="At least one selection is no longer in the current learning library. No incomplete comparison was shown."
          icon="info-circle"
          onAction={onReturn}
          title="Your comparison has changed"
          tone="info"
        />
      );
    case "unauthorized":
      return (
        <StatusPanel
          actionLabel="Try again"
          description="We couldn't start your learner session. No private learning details were shown."
          icon="lock"
          onAction={onRetry}
          title="We couldn't start your learner session"
          tone="warning"
        />
      );
    case "forbidden":
      return (
        <StatusPanel
          actionLabel="Return to learning library"
          description="Your learner profile can't compare these opportunities. Return to the learning library to choose others."
          icon="lock"
          onAction={onReturn}
          title="You can't open this comparison"
          tone="warning"
        />
      );
    case "unavailable":
      return (
        <StatusPanel
          actionLabel="Try again"
          description="We couldn't load this comparison. No old or incomplete details were shown. Try again."
          icon="warning-triangle"
          onAction={onRetry}
          title="Comparison details are unavailable"
          tone="warning"
        />
      );
    case "invalid-response":
      return (
        <StatusPanel
          actionLabel="Return to learning library"
          description="We couldn't safely show this comparison. No incomplete details were shown."
          icon="error-circle"
          onAction={onReturn}
          title="We couldn't show this comparison"
          tone="danger"
        />
      );
    case "unexpected":
      return (
        <StatusPanel
          actionLabel="Try again"
          description="We couldn't load this comparison. No technical or private details were shown. Try again."
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

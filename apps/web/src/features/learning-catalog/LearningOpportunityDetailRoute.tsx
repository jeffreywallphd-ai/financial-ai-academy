import {
  useLoaderData,
  useNavigate,
  useNavigation,
  useRevalidator,
} from "react-router";

import { StatusPanel } from "../../components/StatusPanel";
import { LearningOpportunityDetailPage } from "./LearningOpportunityDetailPage";
import type { LearningOpportunitySelectionRouteState } from "./model";

type DetailRouteState =
  LearningOpportunitySelectionRouteState | { status: "loading" };

export function LearningOpportunityDetailLoadingState() {
  return (
    <section
      aria-atomic="true"
      aria-live="polite"
      className="catalog-loading"
      role="status"
    >
      <p className="eyebrow">Current learning opportunity</p>
      <h1>Loading opportunity details</h1>
      <p>
        Establishing the private learner session and checking the current
        catalog generation.
      </p>
      <div aria-hidden="true" className="loading-placeholder" />
      <span className="visually-hidden">Opportunity loading in progress.</span>
    </section>
  );
}

export function LearningOpportunityDetailRouteView({
  onReturn,
  onRetry,
  state,
}: {
  onReturn: () => void;
  onRetry: () => void;
  state: DetailRouteState;
}) {
  switch (state.status) {
    case "loading":
      return <LearningOpportunityDetailLoadingState />;
    case "ready": {
      const opportunity = state.opportunities[0];
      if (
        state.selection.kind !== "detail" ||
        state.opportunities.length !== 1 ||
        opportunity === undefined
      ) {
        return (
          <StatusPanel
            actionLabel="Return to catalog"
            description="The selected opportunity did not have a valid detail shape, so no partial record was displayed."
            icon="error-circle"
            onAction={onReturn}
            title="Opportunity response unavailable"
            tone="danger"
          />
        );
      }
      return (
        <LearningOpportunityDetailPage
          opportunity={opportunity}
          projection={state.projection}
          returnTo={state.selection.returnTo}
        />
      );
    }
    case "invalid-selection":
      return (
        <StatusPanel
          actionLabel="Return to catalog"
          description="The opportunity link is not valid. No catalog record or client-supplied detail was displayed."
          icon="info-circle"
          onAction={onReturn}
          title="Opportunity link unavailable"
          tone="info"
        />
      );
    case "selection-changed":
      return (
        <StatusPanel
          actionLabel="Return to catalog"
          description="This opportunity is not in the current catalog generation. A different or partial record was not substituted."
          icon="info-circle"
          onAction={onReturn}
          title="Opportunity changed"
          tone="info"
        />
      );
    case "unauthorized":
      return (
        <StatusPanel
          actionLabel="Try again"
          description="A private learner session could not be established. No opportunity details were shown."
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
          description="This local learner profile is not permitted to inspect the selected opportunity."
          icon="lock"
          onAction={onReturn}
          title="Opportunity access unavailable"
          tone="warning"
        />
      );
    case "unavailable":
      return (
        <StatusPanel
          actionLabel="Try again"
          description="The current opportunity could not be loaded right now. No stale or partial record was displayed."
          icon="warning-triangle"
          onAction={onRetry}
          title="Opportunity temporarily unavailable"
          tone="warning"
        />
      );
    case "invalid-response":
      return (
        <StatusPanel
          actionLabel="Return to catalog"
          description="The catalog response did not pass its safety checks, so no partial opportunity was displayed."
          icon="error-circle"
          onAction={onReturn}
          title="Opportunity response unavailable"
          tone="danger"
        />
      );
    case "unexpected":
      return (
        <StatusPanel
          actionLabel="Try again"
          description="The opportunity could not be completed safely. No technical or private details were displayed."
          icon="error-circle"
          onAction={onRetry}
          title="Something went wrong"
          tone="danger"
        />
      );
  }
}

export function LearningOpportunityDetailRoute() {
  const state = useLoaderData<LearningOpportunitySelectionRouteState>();
  const navigate = useNavigate();
  const navigation = useNavigation();
  const revalidator = useRevalidator();
  const displayedState =
    navigation.state === "loading" || revalidator.state === "loading"
      ? ({ status: "loading" } as const)
      : state;
  return (
    <LearningOpportunityDetailRouteView
      onReturn={() => void navigate("/learn")}
      onRetry={() => revalidator.revalidate()}
      state={displayedState}
    />
  );
}

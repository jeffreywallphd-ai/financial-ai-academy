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
      <p className="eyebrow">Learning opportunity</p>
      <h1>Loading this opportunity</h1>
      <p>Checking the current details for this opportunity.</p>
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
            actionLabel="Return to learning library"
            description="We couldn't safely show this opportunity. No incomplete details were shown."
            icon="error-circle"
            onAction={onReturn}
            title="We couldn't show this opportunity"
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
          actionLabel="Return to learning library"
          description="This link doesn't identify a learning opportunity. No learning details were shown."
          icon="info-circle"
          onAction={onReturn}
          title="This opportunity link isn't available"
          tone="info"
        />
      );
    case "selection-changed":
      return (
        <StatusPanel
          actionLabel="Return to learning library"
          description="This opportunity is no longer in the current learning library. No replacement or incomplete details were shown."
          icon="info-circle"
          onAction={onReturn}
          title="This opportunity has changed"
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
          description="Your learner profile can't open these details. Return to the learning library to choose another opportunity."
          icon="lock"
          onAction={onReturn}
          title="You can't open this opportunity"
          tone="warning"
        />
      );
    case "unavailable":
      return (
        <StatusPanel
          actionLabel="Try again"
          description="We couldn't load this opportunity. No old or incomplete details were shown. Try again."
          icon="warning-triangle"
          onAction={onRetry}
          title="Opportunity details are unavailable"
          tone="warning"
        />
      );
    case "invalid-response":
      return (
        <StatusPanel
          actionLabel="Return to learning library"
          description="We couldn't safely show these opportunity details. No incomplete details were shown."
          icon="error-circle"
          onAction={onReturn}
          title="We couldn't show this opportunity"
          tone="danger"
        />
      );
    case "unexpected":
      return (
        <StatusPanel
          actionLabel="Try again"
          description="We couldn't load this opportunity. No technical or private details were shown. Try again."
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

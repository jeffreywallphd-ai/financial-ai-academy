import {
  useLoaderData,
  useNavigate,
  useNavigation,
  useRevalidator,
} from "react-router";

import { StatusPanel } from "../../components/StatusPanel";
import { CurriculumGraphPage } from "./CurriculumGraphPage";
import type { CurriculumGraphRouteState } from "./model";

export function CurriculumGraphLoadingState() {
  return (
    <section
      aria-atomic="true"
      aria-live="polite"
      className="curriculum-graph-loading"
      role="status"
    >
      <p className="eyebrow">Approved curriculum graph</p>
      <h1>Loading curriculum structure</h1>
      <p>
        Establishing the private learner session and reading the exact reviewed
        graph version.
      </p>
      <div aria-hidden="true" className="loading-placeholder" />
      <span className="visually-hidden">Curriculum graph loading in progress.</span>
    </section>
  );
}

export function CurriculumGraphRouteView({
  onCatalog,
  onRetry,
  state,
}: {
  onCatalog: () => void;
  onRetry: () => void;
  state: CurriculumGraphRouteState;
}) {
  switch (state.status) {
    case "loading":
      return <CurriculumGraphLoadingState />;
    case "ready":
      return <CurriculumGraphPage graph={state.graph} />;
    case "invalid-selection":
      return (
        <StatusPanel
          actionLabel="Return to catalog"
          description="The curriculum graph link does not identify one supported exact version. No graph data was requested."
          icon="error-circle"
          onAction={onCatalog}
          title="Curriculum graph link unavailable"
          tone="warning"
        />
      );
    case "unauthorized":
      return (
        <StatusPanel
          actionLabel="Try again"
          description="A private learner session could not be established. No curriculum graph details were shown."
          icon="lock"
          onAction={onRetry}
          title="Learner session required"
          tone="warning"
        />
      );
    case "forbidden":
      return (
        <StatusPanel
          description="This local learner profile is not permitted to view the requested curriculum graph."
          icon="lock"
          title="Curriculum graph access unavailable"
          tone="warning"
        />
      );
    case "not-found":
      return (
        <StatusPanel
          actionLabel="Return to catalog"
          description="That exact approved curriculum graph version is not available. No alternate or latest version was substituted."
          icon="info-circle"
          onAction={onCatalog}
          title="Curriculum graph version not found"
          tone="info"
        />
      );
    case "unavailable":
      return (
        <StatusPanel
          actionLabel="Try again"
          description="The exact curriculum graph could not be loaded right now. No stale or partial structure was displayed."
          icon="warning-triangle"
          onAction={onRetry}
          title="Curriculum graph temporarily unavailable"
          tone="warning"
        />
      );
    case "invalid-response":
      return (
        <StatusPanel
          description="The curriculum graph response did not pass its safety checks, so no partial structure was displayed."
          icon="error-circle"
          title="Curriculum graph response unavailable"
          tone="danger"
        />
      );
    case "unexpected":
      return (
        <StatusPanel
          actionLabel="Try again"
          description="The curriculum graph request could not be completed safely. No technical or private details were displayed."
          icon="error-circle"
          onAction={onRetry}
          title="Something went wrong"
          tone="danger"
        />
      );
  }
}

export function CurriculumGraphRoute() {
  const state = useLoaderData<CurriculumGraphRouteState>();
  const navigate = useNavigate();
  const navigation = useNavigation();
  const revalidator = useRevalidator();
  const displayedState =
    navigation.state === "loading" || revalidator.state === "loading"
      ? ({ status: "loading" } as const)
      : state;
  return (
    <CurriculumGraphRouteView
      onCatalog={() => void navigate("/learn")}
      onRetry={() => revalidator.revalidate()}
      state={displayedState}
    />
  );
}

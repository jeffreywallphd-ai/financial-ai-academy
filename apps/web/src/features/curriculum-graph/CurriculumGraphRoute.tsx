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
      <p className="eyebrow">Approved learning path</p>
      <h1>Loading your learning path</h1>
      <p>Getting the current activities and their status.</p>
      <div aria-hidden="true" className="loading-placeholder" />
      <span className="visually-hidden">Learning path loading in progress.</span>
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
      return (
        <CurriculumGraphPage
          graph={state.graph}
          navigationState={state.navigationState}
        />
      );
    case "invalid-selection":
      return (
        <StatusPanel
          actionLabel="Return to learning library"
          description="This link does not point to a supported learning path version. No learning-path details were requested."
          icon="error-circle"
          onAction={onCatalog}
          title="Learning path link unavailable"
          tone="warning"
        />
      );
    case "unauthorized":
      return (
        <StatusPanel
          actionLabel="Try again"
          description="We could not confirm your learner access. No learning-path details were shown."
          icon="lock"
          onAction={onRetry}
          title="Learner access required"
          tone="warning"
        />
      );
    case "forbidden":
      return (
        <StatusPanel
          description="This learner profile cannot view the requested learning path."
          icon="lock"
          title="Learning path access unavailable"
          tone="warning"
        />
      );
    case "not-found":
      return (
        <StatusPanel
          actionLabel="Return to learning library"
          description="That exact approved learning path version could not be found. We did not substitute another version."
          icon="info-circle"
          onAction={onCatalog}
          title="Learning path version not found"
          tone="info"
        />
      );
    case "unavailable":
      return (
        <StatusPanel
          actionLabel="Try again"
          description="We could not load the complete learning path and current activity status together. No older or partial details were shown."
          icon="warning-triangle"
          onAction={onRetry}
          title="Learning path temporarily unavailable"
          tone="warning"
        />
      );
    case "invalid-response":
      return (
        <StatusPanel
          description="We could not safely show the complete learning path and current activity status. No partial details were shown."
          icon="error-circle"
          title="Learning path unavailable"
          tone="danger"
        />
      );
    case "unexpected":
      return (
        <StatusPanel
          actionLabel="Try again"
          description="We could not open this learning path safely. No technical or private details were shown."
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

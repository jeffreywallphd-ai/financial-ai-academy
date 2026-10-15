import {
  useLoaderData,
  useNavigate,
  useNavigation,
  useRevalidator,
} from "react-router";

import { StatusPanel } from "../../components/StatusPanel";
import { LearningCatalogPage } from "./LearningCatalogPage";
import type { LearningCatalogRouteState } from "./model";

export function LearningCatalogLoadingState() {
  return (
    <section
      aria-atomic="true"
      aria-live="polite"
      className="catalog-loading"
      role="status"
    >
      <p className="eyebrow">Approved learning catalog</p>
      <h1>Loading learning opportunities</h1>
      <p>
        Establishing the private learner session and checking reviewed content.
      </p>
      <div aria-hidden="true" className="loading-placeholder" />
      <span className="visually-hidden">Catalog loading in progress.</span>
    </section>
  );
}

export function LearningCatalogRouteView({
  onRetry,
  state,
}: {
  onRetry: () => void;
  state: LearningCatalogRouteState;
}) {
  switch (state.status) {
    case "loading":
      return <LearningCatalogLoadingState />;
    case "ready":
      return <LearningCatalogPage page={state.page} />;
    case "unauthorized":
      return (
        <StatusPanel
          actionLabel="Try again"
          description="A private learner session could not be established. No catalog details were shown."
          icon="lock"
          onAction={onRetry}
          title="Learner session required"
          tone="warning"
        />
      );
    case "forbidden":
      return (
        <StatusPanel
          description="This local learner profile is not permitted to browse the learning catalog."
          icon="lock"
          title="Catalog access unavailable"
          tone="warning"
        />
      );
    case "unavailable":
      return (
        <StatusPanel
          actionLabel="Try again"
          description="The approved catalog could not be loaded right now. No stale or partial list was displayed."
          icon="warning-triangle"
          onAction={onRetry}
          title="Catalog temporarily unavailable"
          tone="warning"
        />
      );
    case "invalid-query":
      return (
        <StatusPanel
          actionLabel="Clear query"
          description="The catalog query is not valid. Clear it and try bounded optional filters again."
          icon="error-circle"
          onAction={onRetry}
          title="Query could not be applied"
          tone="warning"
        />
      );
    case "stale-cursor":
      return (
        <StatusPanel
          actionLabel="Start fresh"
          description="The catalog changed after this page was created. Start a fresh query rather than using stale results."
          icon="warning-triangle"
          onAction={onRetry}
          title="Catalog results changed"
          tone="warning"
        />
      );
    case "invalid-response":
      return (
        <StatusPanel
          description="The catalog response did not pass its safety checks, so no partial opportunities were displayed."
          icon="error-circle"
          title="Catalog response unavailable"
          tone="danger"
        />
      );
    case "unexpected":
      return (
        <StatusPanel
          actionLabel="Try again"
          description="The catalog could not be completed safely. No technical or private details were displayed."
          icon="error-circle"
          onAction={onRetry}
          title="Something went wrong"
          tone="danger"
        />
      );
  }
}

export function LearningCatalogRoute() {
  const state = useLoaderData<LearningCatalogRouteState>();
  const navigate = useNavigate();
  const navigation = useNavigation();
  const revalidator = useRevalidator();
  const displayedState =
    navigation.state === "loading" || revalidator.state === "loading"
      ? ({ status: "loading" } as const)
      : state;
  return (
    <LearningCatalogRouteView
      onRetry={() => {
        if (
          state.status === "invalid-query" ||
          state.status === "stale-cursor"
        ) {
          void navigate("/learn");
        } else {
          revalidator.revalidate();
        }
      }}
      state={displayedState}
    />
  );
}

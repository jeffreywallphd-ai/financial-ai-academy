import { useLoaderData, useRevalidator } from "react-router";

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
      return <LearningCatalogPage catalog={state.catalog} />;
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
  const revalidator = useRevalidator();
  const displayedState =
    revalidator.state === "loading" && state.status !== "ready"
      ? ({ status: "loading" } as const)
      : state;
  return (
    <LearningCatalogRouteView
      onRetry={() => revalidator.revalidate()}
      state={displayedState}
    />
  );
}

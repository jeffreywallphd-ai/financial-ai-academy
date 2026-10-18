import {
  useLoaderData,
  useNavigate,
  useNavigation,
  useRevalidator,
} from "react-router";

import { StatusPanel } from "../../components/StatusPanel";
import { PlatformHelpSearchPage, PlatformHelpTopicPage } from "./PlatformHelpPage";
import type {
  PlatformHelpSearchRouteState,
  PlatformHelpTopicRouteState,
} from "./model";

export function PlatformHelpLoadingState() {
  return (
    <section
      aria-atomic="true"
      aria-live="polite"
      className="help-loading"
      role="status"
    >
      <p className="eyebrow">Reviewed platform guide</p>
      <h1>Loading platform help</h1>
      <p>Checking the private session and reviewed guide.</p>
      <div aria-hidden="true" className="loading-placeholder" />
      <span className="visually-hidden">Platform help is loading.</span>
    </section>
  );
}

function SharedFailure({
  onRetry,
  status,
}: {
  onRetry: () => void;
  status: "unauthorized" | "forbidden" | "unavailable" | "invalid-response" | "unexpected";
}) {
  switch (status) {
    case "unauthorized":
      return (
        <StatusPanel
          actionLabel="Try again"
          description="A private learner session could not be established. No guide content was shown."
          icon="lock"
          onAction={onRetry}
          title="Learner session required"
          tone="warning"
        />
      );
    case "forbidden":
      return (
        <StatusPanel
          description="This learner profile cannot open the platform guide."
          icon="lock"
          title="Platform guide unavailable"
          tone="warning"
        />
      );
    case "unavailable":
      return (
        <StatusPanel
          actionLabel="Try again"
          description="The reviewed platform guide could not be loaded right now. No partial content was shown."
          icon="warning-triangle"
          onAction={onRetry}
          title="Platform guide temporarily unavailable"
          tone="warning"
        />
      );
    case "invalid-response":
      return (
        <StatusPanel
          description="The guide did not pass its safety checks, so no partial content was shown."
          icon="error-circle"
          title="Platform guide response unavailable"
          tone="danger"
        />
      );
    case "unexpected":
      return (
        <StatusPanel
          actionLabel="Try again"
          description="The guide could not be completed safely. No technical or private details were displayed."
          icon="error-circle"
          onAction={onRetry}
          title="Something went wrong"
          tone="danger"
        />
      );
  }
}

export function PlatformHelpSearchRouteView({
  onClear,
  onRetry,
  state,
}: {
  onClear: () => void;
  onRetry: () => void;
  state: PlatformHelpSearchRouteState;
}) {
  switch (state.status) {
    case "loading":
      return <PlatformHelpLoadingState />;
    case "ready":
      return <PlatformHelpSearchPage page={state.page} selection={state.selection} />;
    case "invalid-query":
      return (
        <StatusPanel
          actionLabel="Clear search"
          description="The guide search is not valid. Clear it and try again."
          icon="error-circle"
          onAction={onClear}
          title="Search could not be applied"
          tone="warning"
        />
      );
    case "stale-cursor":
      return (
        <StatusPanel
          actionLabel="Start a fresh search"
          description="The guide changed after this results page was created. Start again to use the reviewed guide."
          icon="warning-triangle"
          onAction={onClear}
          title="Guide results changed"
          tone="warning"
        />
      );
    default:
      return <SharedFailure onRetry={onRetry} status={state.status} />;
  }
}

export function PlatformHelpSearchRoute() {
  const state = useLoaderData<PlatformHelpSearchRouteState>();
  const navigate = useNavigate();
  const navigation = useNavigation();
  const revalidator = useRevalidator();
  const displayed =
    navigation.state === "loading" || revalidator.state === "loading"
      ? ({ status: "loading" } as const)
      : state;
  return (
    <PlatformHelpSearchRouteView
      onClear={() => void navigate("/help")}
      onRetry={() => revalidator.revalidate()}
      state={displayed}
    />
  );
}

export function PlatformHelpTopicRouteView({
  onReturn,
  onRetry,
  state,
}: {
  onReturn: () => void;
  onRetry: () => void;
  state: PlatformHelpTopicRouteState;
}) {
  switch (state.status) {
    case "loading":
      return <PlatformHelpLoadingState />;
    case "ready":
      return <PlatformHelpTopicPage selection={state.selection} topic={state.topic} />;
    case "invalid-selection":
      return (
        <StatusPanel
          actionLabel="Open platform guide"
          description="This platform guide link is not valid. Use the guide to choose a reviewed topic."
          icon="error-circle"
          onAction={onReturn}
          title="Help link unavailable"
          tone="warning"
        />
      );
    case "not-found":
      return (
        <StatusPanel
          actionLabel="Open platform guide"
          description="That exact reviewed topic is not available. No other version was substituted."
          icon="info-circle"
          onAction={onReturn}
          title="Help topic not found"
          tone="info"
        />
      );
    default:
      return <SharedFailure onRetry={onRetry} status={state.status} />;
  }
}

export function PlatformHelpTopicRoute() {
  const state = useLoaderData<PlatformHelpTopicRouteState>();
  const navigate = useNavigate();
  const navigation = useNavigation();
  const revalidator = useRevalidator();
  const displayed =
    navigation.state === "loading" || revalidator.state === "loading"
      ? ({ status: "loading" } as const)
      : state;
  const returnTo = state.status === "ready" ? state.selection.returnTo : "/help";
  return (
    <PlatformHelpTopicRouteView
      onReturn={() => void navigate(returnTo)}
      onRetry={() => revalidator.revalidate()}
      state={displayed}
    />
  );
}

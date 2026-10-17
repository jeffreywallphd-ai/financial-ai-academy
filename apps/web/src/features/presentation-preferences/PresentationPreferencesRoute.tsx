import {
  useActionData,
  useLoaderData,
  useNavigate,
  useNavigation,
  useRevalidator,
} from "react-router";

import { StatusPanel } from "../../components/StatusPanel";
import type {
  PresentationPreferencesActionState,
  PresentationPreferencesExporter,
  PresentationPreferencesRouteState,
} from "./model";
import { PresentationPreferencesPage } from "./PresentationPreferencesPage";


export function PresentationPreferencesLoadingState() {
  return (
    <section
      aria-atomic="true"
      aria-live="polite"
      className="display-preferences-loading"
      role="status"
    >
      <p className="eyebrow">Your display</p>
      <h1>Loading display and accessibility settings</h1>
      <p>Checking the choices saved for this learner profile.</p>
      <div aria-hidden="true" className="loading-placeholder" />
      <span className="visually-hidden">Display settings loading in progress.</span>
    </section>
  );
}

function Failure({
  onReturn,
  onRetry,
  status,
}: {
  onReturn: () => void;
  onRetry: () => void;
  status: Exclude<PresentationPreferencesRouteState, { status: "ready" }>["status"];
}) {
  if (status === "unauthorized") {
    return <StatusPanel actionLabel="Try again" description="We couldn't start your learner session. The application is using its standard accessible display." icon="lock" onAction={onRetry} title="Learner session needed" tone="warning" />;
  }
  if (status === "forbidden") {
    return <StatusPanel actionLabel="Return to learning library" description="This learner profile cannot change saved display choices. Your browser theme and the standard accessible display remain available." icon="lock" onAction={onReturn} title="Display settings unavailable" tone="warning" />;
  }
  if (status === "not-found") {
    return <StatusPanel actionLabel="Return to learning library" description="These saved display choices are no longer available. No partial details were shown." icon="info-circle" onAction={onReturn} title="Display settings not found" tone="info" />;
  }
  if (status === "invalid-response") {
    return <StatusPanel actionLabel="Try again" description="We couldn't safely use the saved display response. The application is using a complete safe display instead." icon="error-circle" onAction={onRetry} title="Display settings could not be shown" tone="danger" />;
  }
  if (status === "unavailable") {
    return <StatusPanel actionLabel="Try again" description="Saved display choices could not be loaded right now. The standard accessible display and local theme remain usable." icon="warning-triangle" onAction={onRetry} title="Display settings temporarily unavailable" tone="warning" />;
  }
  return <StatusPanel actionLabel="Try again" description="The page could not be completed safely. No technical or private details were displayed." icon="error-circle" onAction={onRetry} title="Something went wrong" tone="danger" />;
}

export function PresentationPreferencesRoute({
  exportPreferences,
}: {
  exportPreferences: PresentationPreferencesExporter;
}) {
  const state = useLoaderData<PresentationPreferencesRouteState>();
  const actionState = useActionData<PresentationPreferencesActionState>();
  const navigation = useNavigation();
  const navigate = useNavigate();
  const revalidator = useRevalidator();
  if (navigation.state === "loading" || revalidator.state === "loading") {
    return <PresentationPreferencesLoadingState />;
  }
  return state.status === "ready" ? (
    <PresentationPreferencesPage
      actionState={actionState}
      busy={navigation.state === "submitting"}
      exportPreferences={exportPreferences}
      history={state.history}
      profile={state.profile}
    />
  ) : (
    <Failure
      onReturn={() => void navigate("/learn")}
      onRetry={() => revalidator.revalidate()}
      status={state.status}
    />
  );
}

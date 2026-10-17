import {
  useActionData,
  useLoaderData,
  useNavigate,
  useNavigation,
  useRevalidator,
} from "react-router";

import { StatusPanel } from "../../components/StatusPanel";
import type {
  LearnerPreferencesActionState,
  LearnerPreferencesExporter,
  LearnerPreferencesRouteState,
} from "./model";
import { LearnerPreferencesPage } from "./LearnerPreferencesPage";


export function LearnerPreferencesLoadingState() {
  return (
    <section aria-atomic="true" aria-live="polite" className="preferences-loading" role="status">
      <p className="eyebrow">Your learning</p>
      <h1>Loading your learning preferences</h1>
      <p>Checking your current goals, experience, and interests.</p>
      <div aria-hidden="true" className="loading-placeholder" />
      <span className="visually-hidden">Learning preferences loading in progress.</span>
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
  status: Exclude<LearnerPreferencesRouteState, { status: "ready" }>["status"];
}) {
  if (status === "unauthorized") {
    return <StatusPanel actionLabel="Try again" description="We couldn't start your learner session. No private learning preferences were shown." icon="lock" onAction={onRetry} title="Learner session needed" tone="warning" />;
  }
  if (status === "forbidden") {
    return <StatusPanel actionLabel="Return to learning library" description="This learner profile cannot use Learning preferences. No private details were shown." icon="lock" onAction={onReturn} title="Learning preferences unavailable" tone="warning" />;
  }
  if (status === "not-found") {
    return <StatusPanel actionLabel="Return to learning library" description="This learning-preference profile is no longer available. No partial details were shown." icon="info-circle" onAction={onReturn} title="Learning preferences not found" tone="info" />;
  }
  if (status === "invalid-response") {
    return <StatusPanel actionLabel="Return to learning library" description="We couldn't safely show this learning-preference response. No partial private details were displayed." icon="error-circle" onAction={onReturn} title="Learning preferences could not be shown" tone="danger" />;
  }
  if (status === "unavailable") {
    return <StatusPanel actionLabel="Try again" description="Learning preferences could not be loaded right now. No old or partial profile was displayed." icon="warning-triangle" onAction={onRetry} title="Learning preferences temporarily unavailable" tone="warning" />;
  }
  return <StatusPanel actionLabel="Try again" description="The page could not be completed safely. No technical or private details were displayed." icon="error-circle" onAction={onRetry} title="Something went wrong" tone="danger" />;
}

export function LearnerPreferencesRoute({
  exportPreferences,
}: {
  exportPreferences: LearnerPreferencesExporter;
}) {
  const state = useLoaderData<LearnerPreferencesRouteState>();
  const actionState = useActionData<LearnerPreferencesActionState>();
  const navigation = useNavigation();
  const navigate = useNavigate();
  const revalidator = useRevalidator();
  if (navigation.state === "loading" || revalidator.state === "loading") {
    return <LearnerPreferencesLoadingState />;
  }
  return state.status === "ready" ? (
    <LearnerPreferencesPage
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

import {
  useActionData,
  useLoaderData,
  useNavigate,
  useNavigation,
  useRevalidator,
} from "react-router";

import { StatusPanel } from "../../components/StatusPanel";
import type {
  SaveLearningRouteState,
  WorkspaceActionState,
  WorkspaceRouteState,
} from "./model";
import {
  PersonalWorkspacePage,
  SaveLearningPage,
} from "./PersonalWorkspacePage";


export function PersonalWorkspaceLoadingState() {
  return (
    <section aria-atomic="true" aria-live="polite" className="saved-learning-loading" role="status">
      <p className="eyebrow">Saved learning</p>
      <h1>Loading your saved learning</h1>
      <p>Checking your current private notes, bookmarks, and collections.</p>
      <div aria-hidden="true" className="loading-placeholder" />
      <span className="visually-hidden">Saved learning loading in progress.</span>
    </section>
  );
}

function Failure({
  onReturn,
  onRetry,
  returnLabel,
  status,
}: {
  onReturn: () => void;
  onRetry: () => void;
  returnLabel: string;
  status: string;
}) {
  if (status === "unauthorized") {
    return <StatusPanel actionLabel="Try again" description="We couldn't start your learner session. No private saved-learning details were shown." icon="lock" onAction={onRetry} title="Learner session needed" tone="warning" />;
  }
  if (status === "forbidden") {
    return <StatusPanel actionLabel={returnLabel} description="This learner profile cannot use Saved learning. No private details were shown." icon="lock" onAction={onReturn} title="Saved learning unavailable" tone="warning" />;
  }
  if (status === "invalid-selection" || status === "not-found") {
    return <StatusPanel actionLabel={returnLabel} description="This item is not available to save. No other saved work was changed." icon="info-circle" onAction={onReturn} title="Item not available" tone="info" />;
  }
  if (status === "invalid-query") {
    return <StatusPanel actionLabel="Clear filters" description="These search filters could not be used safely. Clear them and try your search again." icon="warning-triangle" onAction={onReturn} title="Search could not be shown" tone="warning" />;
  }
  if (status === "invalid-response") {
    return <StatusPanel actionLabel={returnLabel} description="We couldn't safely show this saved-learning response. No partial private details were displayed." icon="error-circle" onAction={onReturn} title="Saved learning could not be shown" tone="danger" />;
  }
  if (status === "unavailable") {
    return <StatusPanel actionLabel="Try again" description="Saved learning could not be loaded right now. No old or partial records were displayed." icon="warning-triangle" onAction={onRetry} title="Saved learning temporarily unavailable" tone="warning" />;
  }
  return <StatusPanel actionLabel="Try again" description="The page could not be completed safely. No technical or private details were displayed." icon="error-circle" onAction={onRetry} title="Something went wrong" tone="danger" />;
}

export function PersonalWorkspaceRoute() {
  const state = useLoaderData<WorkspaceRouteState>();
  const actionState = useActionData<WorkspaceActionState>();
  const navigation = useNavigation();
  const navigate = useNavigate();
  const revalidator = useRevalidator();
  if (navigation.state === "loading" || revalidator.state === "loading") {
    return <PersonalWorkspaceLoadingState />;
  }
  return state.status === "ready" ? (
    <PersonalWorkspacePage actionState={actionState} busy={navigation.state === "submitting"} result={state.result} search={state.search} workspace={state.workspace} />
  ) : (
    <Failure onReturn={() => void navigate(state.status === "invalid-query" ? "/saved-learning" : "/learn")} onRetry={() => revalidator.revalidate()} returnLabel="Return to learning library" status={state.status} />
  );
}

export function SaveLearningRoute() {
  const state = useLoaderData<SaveLearningRouteState>();
  const actionState = useActionData<WorkspaceActionState>();
  const navigation = useNavigation();
  const navigate = useNavigate();
  const revalidator = useRevalidator();
  if (navigation.state === "loading" || revalidator.state === "loading") {
    return <PersonalWorkspaceLoadingState />;
  }
  return state.status === "ready" ? (
    <SaveLearningPage actionState={actionState} busy={navigation.state === "submitting"} selection={state.selection} workspace={state.workspace} />
  ) : (
    <Failure onReturn={() => void navigate("/saved-learning")} onRetry={() => revalidator.revalidate()} returnLabel="Open Saved learning" status={state.status} />
  );
}

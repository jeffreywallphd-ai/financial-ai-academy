import { useActionData, useLoaderData, useNavigate, useNavigation, useRevalidator } from "react-router";

import { StatusPanel } from "../../components/StatusPanel";
import type { ContextualHelpReader } from "../platform-help/model";
import { unavailableContextualHelpReader } from "../platform-help/ContextualHelpLinks";
import type { ProjectArtifact, ProjectCreateActionState, ProjectCreateRouteState, ProjectDetailRouteState, ProjectDownloadOutcome, ProjectExportOutcome, ProjectLearningActionState, ProjectLearningRouteState, ProjectListRouteState, ProjectWorkspaceActionState } from "./model";
import { ProjectCreatePage } from "./ProjectCreatePage";
import { ProjectDetailPage } from "./ProjectDetailPage";
import { ProjectListPage } from "./ProjectListPage";
import { ProjectSubmissionPage } from "./ProjectSubmissionPage";

export function ProjectLoadingState() {
  return <section aria-atomic="true" aria-live="polite" className="project-loading" role="status"><p className="eyebrow">Projects</p><h1>Loading your Projects</h1><p>Checking your current private Project records.</p><div aria-hidden="true" className="loading-placeholder" /><span className="visually-hidden">Projects loading in progress.</span></section>;
}

function Failure({ onAction, status }: { onAction: () => void; status: string }) {
  if (status === "unauthorized") return <StatusPanel actionLabel="Try again" description="We could not open your private learner view. No Project details were shown." icon="lock" onAction={onAction} title="Private learner view required" tone="warning" />;
  if (status === "forbidden") return <StatusPanel description="This learner profile cannot use Projects." icon="lock" title="Project access unavailable" tone="warning" />;
  if (status === "not-found" || status === "invalid-selection") return <StatusPanel actionLabel="Return to Projects" description="That Project or learning choice is not available. No private details were shown." icon="info-circle" onAction={onAction} title="Project not found" tone="info" />;
  if (status === "invalid-response") return <StatusPanel description="The Project response did not pass its safety checks, so no partial details were displayed." icon="error-circle" title="Project response unavailable" tone="danger" />;
  if (status === "unavailable") return <StatusPanel actionLabel="Try again" description="Projects could not be loaded right now. No stale or partial records were displayed." icon="warning-triangle" onAction={onAction} title="Projects temporarily unavailable" tone="warning" />;
  return <StatusPanel actionLabel="Try again" description="The page could not be completed safely. No technical or private details were displayed." icon="error-circle" onAction={onAction} title="Something went wrong" tone="danger" />;
}

export function ProjectListRoute() {
  const state = useLoaderData<ProjectListRouteState>();
  const navigation = useNavigation();
  const revalidator = useRevalidator();
  if (navigation.state === "loading" || revalidator.state === "loading") return <ProjectLoadingState />;
  return state.status === "ready"
    ? <ProjectListPage options={state.options} projects={state.projects} />
    : <Failure onAction={() => revalidator.revalidate()} status={state.status} />;
}

export function ProjectDetailRoute({
  downloadArtifact,
  exportSnapshot,
  readContextualHelp = unavailableContextualHelpReader,
}: {
  downloadArtifact: (projectId: string, artifact: ProjectArtifact) => Promise<ProjectDownloadOutcome>;
  exportSnapshot: (projectId: string, snapshotId: string) => Promise<ProjectExportOutcome>;
  readContextualHelp?: ContextualHelpReader;
}) {
  const state = useLoaderData<ProjectDetailRouteState>();
  const actionState = useActionData<ProjectWorkspaceActionState>();
  const navigation = useNavigation();
  const navigate = useNavigate();
  const revalidator = useRevalidator();
  if (navigation.state === "loading" || revalidator.state === "loading") return <ProjectLoadingState />;
  return state.status === "ready"
    ? <ProjectDetailPage actionState={actionState} busy={navigation.state === "submitting"} downloadArtifact={downloadArtifact} exportSnapshot={exportSnapshot} project={state.project} readContextualHelp={readContextualHelp} snapshots={state.snapshots} workspace={state.workspace} />
    : <Failure onAction={() => state.status === "not-found" || state.status === "invalid-selection" ? void navigate("/projects") : revalidator.revalidate()} status={state.status} />;
}

export function ProjectCreateRoute() {
  const state = useLoaderData<ProjectCreateRouteState>();
  const actionState = useActionData<ProjectCreateActionState>();
  const navigation = useNavigation();
  const navigate = useNavigate();
  const revalidator = useRevalidator();
  if (navigation.state === "loading" || revalidator.state === "loading") return <ProjectLoadingState />;
  return state.status === "ready"
    ? <ProjectCreatePage actionState={actionState} idempotencyKey={state.idempotencyKey} option={state.option} />
    : <Failure onAction={() => state.status === "invalid-selection" ? void navigate("/projects") : revalidator.revalidate()} status={state.status} />;
}

export function ProjectLearningRoute() {
  const state = useLoaderData<ProjectLearningRouteState>();
  const actionState = useActionData<ProjectLearningActionState>();
  const navigation = useNavigation();
  const navigate = useNavigate();
  const revalidator = useRevalidator();
  if (navigation.state === "loading" || revalidator.state === "loading") return <ProjectLoadingState />;
  return state.status === "ready"
    ? <ProjectSubmissionPage actionState={actionState} busy={navigation.state === "submitting"} candidate={state.candidate} completion={state.completion} evidence={state.evidence} history={state.history} project={state.project} selection={state.selection} submissionId={state.submissionId} />
    : <Failure onAction={() => state.status === "not-found" || state.status === "invalid-selection" ? void navigate("/projects") : revalidator.revalidate()} status={state.status} />;
}

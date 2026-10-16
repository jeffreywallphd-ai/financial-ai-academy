import { useEffect, useRef, useState } from "react";
import {
  useLoaderData,
  useNavigate,
  useNavigation,
  useRevalidator,
} from "react-router";

import { StatusPanel } from "../../components/StatusPanel";
import { CurriculumGraphPage } from "./CurriculumGraphPage";
import type {
  ActivityLaunchResult,
  ActivityLaunchViewState,
  CurriculumGraph,
  CurriculumGraphRouteState,
  NavigationState,
} from "./model";

export type CurriculumActivityLauncher = (
  graph: CurriculumGraph,
  navigationState: NavigationState,
  activityId: string,
  signal: AbortSignal,
) => Promise<ActivityLaunchResult>;

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
  launchState = { status: "idle" },
  onCatalog,
  onLaunch = () => undefined,
  onRetry,
  state,
}: {
  launchState?: ActivityLaunchViewState;
  onCatalog: () => void;
  onLaunch?: (activityId: string) => void;
  onRetry: () => void;
  state: CurriculumGraphRouteState;
}) {
  switch (state.status) {
    case "loading":
      return <CurriculumGraphLoadingState />;
    case "ready":
      return (
        <CurriculumGraphPage
          currentActivityId={state.currentActivityId}
          graph={state.graph}
          launchState={launchState}
          navigationState={state.navigationState}
          onLaunch={onLaunch}
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

export function CurriculumGraphRoute({
  launchActivity,
}: {
  launchActivity: CurriculumActivityLauncher;
}) {
  const state = useLoaderData<CurriculumGraphRouteState>();
  const navigate = useNavigate();
  const navigation = useNavigation();
  const revalidator = useRevalidator();
  const controllerRef = useRef<AbortController | null>(null);
  const [launchState, setLaunchState] = useState<ActivityLaunchViewState>({
    status: "idle",
  });
  useEffect(
    () => () => {
      controllerRef.current?.abort();
    },
    [],
  );
  const onLaunch = async (activityId: string) => {
    if (state.status !== "ready") return;
    controllerRef.current?.abort();
    const controller = new AbortController();
    controllerRef.current = controller;
    setLaunchState({ status: "launching", activityId });
    let result: ActivityLaunchResult;
    try {
      result = await launchActivity(
        state.graph,
        state.navigationState,
        activityId,
        controller.signal,
      );
    } catch {
      if (controller.signal.aborted) return;
      setLaunchState({ status: "unavailable", activityId });
      return;
    }
    if (controller.signal.aborted) return;
    if (result.status === "ready") {
      await navigate(result.destination);
      return;
    }
    setLaunchState(result);
  };
  const displayedState =
    navigation.state === "loading" || revalidator.state === "loading"
      ? ({ status: "loading" } as const)
      : state;
  return (
    <CurriculumGraphRouteView
      launchState={launchState}
      onCatalog={() => void navigate("/learn")}
      onLaunch={(activityId) => void onLaunch(activityId)}
      onRetry={() => revalidator.revalidate()}
      state={displayedState}
    />
  );
}

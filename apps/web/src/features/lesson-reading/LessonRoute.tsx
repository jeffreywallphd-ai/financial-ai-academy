import { useLoaderData, useRevalidator } from "react-router";

import { StatusPanel } from "../../components/StatusPanel";
import { KnowledgeCheck } from "./KnowledgeCheck";
import { LessonReadingPage } from "./LessonReadingPage";
import type { LessonRouteState } from "./model";


export function LessonLoadingState() {
  return (
    <section
      aria-atomic="true"
      aria-live="polite"
      className="lesson-loading"
      role="status"
    >
      <p className="eyebrow">Financial foundations lesson</p>
      <h1>Opening your lesson</h1>
      <p>Starting your learner session and opening the reviewed lesson.</p>
      <div aria-hidden="true" className="loading-placeholder" />
      <span className="visually-hidden">Lesson loading in progress.</span>
    </section>
  );
}

export function LessonRouteView({
  onRetry,
  state,
}: {
  onRetry: () => void;
  state: LessonRouteState;
}) {
  switch (state.status) {
    case "loading":
      return <LessonLoadingState />;
    case "ready":
      return (
        <LessonReadingPage
          knowledgeCheck={
            <KnowledgeCheck placementId={state.lesson.placement_id} />
          }
          lesson={state.lesson}
        />
      );
    case "unauthorized":
      return (
        <StatusPanel
          actionLabel="Try again"
          description="We couldn't start your learner session. No private learning details were shown."
          icon="lock"
          onAction={onRetry}
          title="We couldn't start your learner session"
          tone="warning"
        />
      );
    case "forbidden":
      return (
        <StatusPanel
          description="This learner profile does not have access to the requested lesson. No lesson details were shown."
          icon="lock"
          title="You don't have access to this lesson"
          tone="warning"
        />
      );
    case "not-found":
      return (
        <StatusPanel
          description="We couldn't find this lesson version. We did not substitute a different or newer lesson."
          icon="info-circle"
          title="Lesson not found"
          tone="info"
        />
      );
    case "unavailable":
      return (
        <StatusPanel
          actionLabel="Try again"
          description="We couldn't open this lesson right now. Your learning record was not changed."
          icon="warning-triangle"
          onAction={onRetry}
          title="Lesson temporarily unavailable"
          tone="warning"
        />
      );
    case "invalid-content":
      return (
        <StatusPanel
          description="This lesson did not pass our safety checks, so we did not show partial content."
          icon="error-circle"
          title="We couldn't show this lesson safely"
          tone="danger"
        />
      );
    case "unexpected":
      return (
        <StatusPanel
          actionLabel="Try again"
          description="We couldn't open this lesson. No private learning details were shown."
          icon="error-circle"
          onAction={onRetry}
          title="We couldn't open this lesson"
          tone="danger"
        />
      );
  }
}

export function LessonRoute() {
  const state = useLoaderData<LessonRouteState>();
  const revalidator = useRevalidator();
  const displayedState =
    revalidator.state === "loading" && state.status !== "ready"
      ? ({ status: "loading" } as const)
      : state;
  return (
    <LessonRouteView
      onRetry={() => revalidator.revalidate()}
      state={displayedState}
    />
  );
}

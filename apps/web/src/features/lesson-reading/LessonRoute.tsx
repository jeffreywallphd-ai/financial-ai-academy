import { useLoaderData, useRevalidator } from "react-router";

import { StatusPanel } from "../../components/StatusPanel";
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
      <p className="eyebrow">Approved financial foundations lesson</p>
      <h1>Opening your lesson</h1>
      <p>
        Establishing the private learner session and loading the exact
        reviewed version.
      </p>
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
      return <LessonReadingPage lesson={state.lesson} />;
    case "unauthorized":
      return (
        <StatusPanel
          actionLabel="Try again"
          description="A private learner session could not be established. No lesson details were shown."
          icon="lock"
          onAction={onRetry}
          title="Learner session required"
          tone="warning"
        />
      );
    case "forbidden":
      return (
        <StatusPanel
          description="This local learner profile is not permitted to open the requested lesson."
          icon="lock"
          title="Lesson access unavailable"
          tone="warning"
        />
      );
    case "not-found":
      return (
        <StatusPanel
          description="The requested placement is not available. A different or newer lesson was not substituted."
          icon="info-circle"
          title="Lesson not found"
          tone="info"
        />
      );
    case "unavailable":
      return (
        <StatusPanel
          actionLabel="Try again"
          description="The exact lesson could not be opened right now. Your learning record was not changed."
          icon="warning-triangle"
          onAction={onRetry}
          title="Lesson temporarily unavailable"
          tone="warning"
        />
      );
    case "invalid-content":
      return (
        <StatusPanel
          description="This lesson did not pass the safe reading checks, so no partial content was displayed."
          icon="error-circle"
          title="Lesson content unavailable"
          tone="danger"
        />
      );
    case "unexpected":
      return (
        <StatusPanel
          actionLabel="Try again"
          description="The lesson could not be completed safely. No technical or private details were displayed."
          icon="error-circle"
          onAction={onRetry}
          title="Something went wrong"
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

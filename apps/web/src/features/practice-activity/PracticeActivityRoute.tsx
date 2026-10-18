import { useLoaderData, useRevalidator } from "react-router";

import { StatusPanel } from "../../components/StatusPanel";
import type {
  ContextualHelpReader,
  FeatureGuidanceReader,
} from "../platform-help/model";
import { unavailableContextualHelpReader } from "../platform-help/ContextualHelpLinks";
import { unavailableFeatureGuidanceReader } from "../platform-help/FeatureGuidanceExplanation";
import type {
  PracticeActivityRouteState,
  PracticeDraftSaver,
  PracticeProgressReader,
  PracticeSubmitter,
} from "./model";
import { PracticeActivityPage } from "./PracticeActivityPage";


export function PracticeActivityLoadingState() {
  return (
    <section
      aria-atomic="true"
      aria-live="polite"
      className="practice-loading"
      role="status"
    >
      <p className="eyebrow">Practice activity</p>
      <h1>Opening this practice activity</h1>
      <p>Starting your learner session and opening the activity.</p>
      <div aria-hidden="true" className="loading-placeholder" />
      <span className="visually-hidden">Practice activity loading.</span>
    </section>
  );
}

export function PracticeActivityRouteView({
  onRetry,
  readProgress,
  readContextualHelp = unavailableContextualHelpReader,
  readFeatureGuidance = unavailableFeatureGuidanceReader,
  saveDraft,
  state,
  submitPractice,
}: {
  onRetry: () => void;
  readProgress: PracticeProgressReader;
  readContextualHelp?: ContextualHelpReader;
  readFeatureGuidance?: FeatureGuidanceReader;
  saveDraft: PracticeDraftSaver;
  state: PracticeActivityRouteState;
  submitPractice: PracticeSubmitter;
}) {
  switch (state.status) {
    case "loading":
      return <PracticeActivityLoadingState />;
    case "ready":
      return (
        <PracticeActivityPage
          practice={state.practice}
          progress={state.progress}
          readContextualHelp={readContextualHelp}
          readFeatureGuidance={readFeatureGuidance}
          readProgress={readProgress}
          saveDraft={saveDraft}
          submitPractice={submitPractice}
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
          description="This learner profile does not have access to the requested activity. No practice details were shown."
          icon="lock"
          title="You don't have access to this activity"
          tone="warning"
        />
      );
    case "not-found":
      return (
        <StatusPanel
          description="We couldn't find this practice activity. We did not substitute a different version."
          icon="info-circle"
          title="Practice activity not found"
          tone="info"
        />
      );
    case "unavailable":
      return (
        <StatusPanel
          actionLabel="Try again"
          description="We couldn't open this practice activity right now. Your learning record was not changed."
          icon="warning-triangle"
          onAction={onRetry}
          title="Practice activity temporarily unavailable"
          tone="warning"
        />
      );
    case "invalid-content":
      return (
        <StatusPanel
          description="This activity did not pass our safety checks, so we did not show partial questions or choices."
          icon="error-circle"
          title="We couldn't show this activity safely"
          tone="danger"
        />
      );
    case "unexpected":
      return (
        <StatusPanel
          actionLabel="Try again"
          description="We couldn't open this practice activity. No private learning details were shown."
          icon="error-circle"
          onAction={onRetry}
          title="We couldn't open this activity"
          tone="danger"
        />
      );
  }
}

export function PracticeActivityRoute({
  readProgress,
  readContextualHelp = unavailableContextualHelpReader,
  readFeatureGuidance = unavailableFeatureGuidanceReader,
  saveDraft,
  submitPractice,
}: {
  readProgress: PracticeProgressReader;
  readContextualHelp?: ContextualHelpReader;
  readFeatureGuidance?: FeatureGuidanceReader;
  saveDraft: PracticeDraftSaver;
  submitPractice: PracticeSubmitter;
}) {
  const state = useLoaderData<PracticeActivityRouteState>();
  const revalidator = useRevalidator();
  const displayedState =
    revalidator.state === "loading" && state.status !== "ready"
      ? ({ status: "loading" } as const)
      : state;
  return (
    <PracticeActivityRouteView
      onRetry={() => revalidator.revalidate()}
      readProgress={readProgress}
      readContextualHelp={readContextualHelp}
      readFeatureGuidance={readFeatureGuidance}
      saveDraft={saveDraft}
      state={displayedState}
      submitPractice={submitPractice}
    />
  );
}

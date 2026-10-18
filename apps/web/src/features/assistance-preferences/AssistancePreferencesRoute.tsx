import {
  useActionData,
  useLoaderData,
  useNavigation,
  useRevalidator,
} from "react-router";

import type {
  AssistancePreferencesActionState,
  AssistancePreferencesExporter,
  AssistancePreferencesRouteState,
  LocalReminderExporter,
} from "./model";
import { AssistancePreferencesPage } from "./AssistancePreferencesPage";


export function AssistancePreferencesLoadingState() {
  return (
    <section
      aria-atomic="true"
      aria-live="polite"
      className="assistance-preferences-loading"
      role="status"
    >
      <p className="eyebrow">Your choices</p>
      <h1>Loading AI help and reminder choices</h1>
      <p>Checking the learner profile and this browser separately.</p>
      <div aria-hidden="true" className="loading-placeholder" />
      <span className="visually-hidden">Choice loading in progress.</span>
    </section>
  );
}

export function AssistancePreferencesRoute({
  exportLocalReminder,
  exportPreferences,
}: {
  exportLocalReminder: LocalReminderExporter;
  exportPreferences: AssistancePreferencesExporter;
}) {
  const state = useLoaderData<AssistancePreferencesRouteState>();
  const actionState = useActionData<AssistancePreferencesActionState>();
  const navigation = useNavigation();
  const revalidator = useRevalidator();
  if (navigation.state === "loading" || revalidator.state === "loading") {
    return <AssistancePreferencesLoadingState />;
  }
  return (
    <AssistancePreferencesPage
      actionState={actionState}
      busy={navigation.state === "submitting"}
      exportLocalReminder={exportLocalReminder}
      exportPreferences={exportPreferences}
      onRetry={() => revalidator.revalidate()}
      state={state}
    />
  );
}

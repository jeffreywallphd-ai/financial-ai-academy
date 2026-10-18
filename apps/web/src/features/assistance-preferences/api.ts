import {
  redirect,
  type ActionFunctionArgs,
  type LoaderFunctionArgs,
} from "react-router";

import type { FinancialAcademyApiClient } from "../../generated/api-client";
import type { SingleProfileSession } from "../../platform/auth/singleProfileSession";
import {
  exportLocalReminderPreference,
  readLocalReminderPreference,
  replaceLocalReminderPreference,
  resetLocalReminderPreference,
  type LocalReminderPreferenceStorage,
} from "../../platform/reminders/localReminderPreference";
import {
  assistancePreferenceExportIsSafe,
  assistancePreferenceProfileIsSafe,
  publicErrorCode,
  type AssistancePreferenceExport,
  type AssistancePreferenceProfile,
  type AssistancePreferencesActionState,
  type AssistancePreferencesExportOutcome,
  type AssistancePreferencesRouteState,
  type LocalReminderState,
  type PreparedAssistancePreferenceRequest,
} from "./model";


const IDENTIFIER = /^[a-z0-9][a-z0-9._-]{2,63}$/;

function serverFailure(
  status: number,
): AssistancePreferencesRouteState["server"] {
  if (status === 401) return { status: "unauthorized" };
  if (status === 403) return { status: "forbidden" };
  if (status === 404) return { status: "not-found" };
  if (status === 409 || status === 503) return { status: "unavailable" };
  return { status: "unexpected" };
}

async function readServerExport(
  client: FinancialAcademyApiClient,
  session: SingleProfileSession,
  signal?: AbortSignal,
  retryUnauthorized = true,
): Promise<AssistancePreferencesRouteState["server"]> {
  const established = await session.ensure(signal);
  if (established.status === "error") return { status: established.kind };
  try {
    const result = await client.GET(
      "/api/v1/learner-assistance-preferences/export",
      signal ? { signal } : {},
    );
    if (result.response.status === 200) {
      const value = result.data as AssistancePreferenceExport | undefined;
      if (!value || !(await assistancePreferenceExportIsSafe(value))) {
        return { status: "invalid-response" };
      }
      return {
        status: "ready",
        export: value,
        history: value.history,
        profile: value.profile,
      };
    }
    if (retryUnauthorized && result.response.status === 401) {
      session.invalidate();
      return readServerExport(client, session, signal, false);
    }
    return serverFailure(result.response.status);
  } catch (error) {
    if (signal?.aborted) throw error;
    return { status: "unavailable" };
  }
}

async function readLocal(
  storage: Pick<LocalReminderPreferenceStorage, "getItem">,
  now: () => string,
): Promise<LocalReminderState> {
  try {
    return await readLocalReminderPreference(storage, now());
  } catch {
    return { status: "unavailable" };
  }
}

export function createAssistancePreferencesLoader(
  client: FinancialAcademyApiClient,
  session: SingleProfileSession,
  storage: Pick<LocalReminderPreferenceStorage, "getItem">,
  now: () => string,
) {
  return async ({ request }: LoaderFunctionArgs): Promise<AssistancePreferencesRouteState> => {
    const [local, server] = await Promise.all([
      readLocal(storage, now),
      readServerExport(client, session, request.signal),
    ]);
    return { local, server };
  };
}

function exactFields(form: FormData, allowed: readonly string[]): boolean {
  const accepted = new Set(allowed);
  return [...form.keys()].every((key) => accepted.has(key));
}

function single(form: FormData, name: string): string | undefined {
  if (form.getAll(name).length !== 1) return undefined;
  const value = form.get(name);
  return typeof value === "string" ? value : undefined;
}

function expectedRevision(form: FormData): number | undefined {
  const value = Number(single(form, "expected_revision"));
  return Number.isSafeInteger(value) && value >= 1 ? value : undefined;
}

function preparedServerRequest(form: FormData): {
  intent: "reset" | "save";
  request: PreparedAssistancePreferenceRequest;
} | undefined {
  const formIntent = single(form, "form_intent");
  const idempotencyKey = single(form, "idempotency_key");
  const revision = expectedRevision(form);
  if (!idempotencyKey || !IDENTIFIER.test(idempotencyKey) || revision === undefined) {
    return undefined;
  }
  if (formIntent === "server-reset") {
    if (
      !exactFields(form, [
        "confirm_reset",
        "expected_revision",
        "form_intent",
        "idempotency_key",
        "operation",
      ]) ||
      single(form, "operation") !== "reset_profile" ||
      single(form, "confirm_reset") !== "reset"
    ) return undefined;
    return {
      intent: "reset",
      request: {
        schema_version: "1.0.0",
        idempotency_key: idempotencyKey,
        expected_revision: revision,
        mutation: { operation: "reset_profile" },
      },
    };
  }
  if (
    formIntent !== "server-save" ||
    !exactFields(form, [
      "assistance_mode",
      "expected_revision",
      "form_intent",
      "idempotency_key",
      "operation",
    ]) ||
    single(form, "operation") !== "replace_preferences"
  ) return undefined;
  const mode = single(form, "assistance_mode");
  if (mode !== "off" && mode !== "on_request") return undefined;
  return {
    intent: "save",
    request: {
      schema_version: "1.0.0",
      idempotency_key: idempotencyKey,
      expected_revision: revision,
      mutation: { operation: "replace_preferences", assistance_mode: mode },
    },
  };
}

function actionFailure(
  authority: "local" | "server",
  kind: AssistancePreferencesActionState["kind"],
  intent: "reset" | "save",
  preparedRequest?: PreparedAssistancePreferenceRequest,
): AssistancePreferencesActionState {
  return preparedRequest
    ? { status: "error", authority, kind, intent, preparedRequest }
    : { status: "error", authority, kind, intent };
}

async function changeLocal(
  form: FormData,
  storage: LocalReminderPreferenceStorage,
  now: () => string,
): Promise<Response | AssistancePreferencesActionState> {
  const formIntent = single(form, "form_intent");
  const intent = formIntent === "local-reset" ? "reset" : "save";
  const allowed = intent === "reset"
    ? ["confirm_reset", "form_intent"]
    : ["form_intent", "reminder_mode"];
  if (!exactFields(form, allowed)) return actionFailure("local", "invalid", intent);
  if (intent === "reset" && single(form, "confirm_reset") !== "reset") {
    return actionFailure("local", "invalid", intent);
  }
  const mode = single(form, "reminder_mode");
  if (intent === "save" && mode !== "off" && mode !== "in_app_when_available") {
    return actionFailure("local", "invalid", intent);
  }
  const current = await readLocal(storage, now);
  if (!current.envelope || current.status === "unavailable") {
    return actionFailure("local", "unavailable", intent);
  }
  try {
    if (intent === "reset") {
      await resetLocalReminderPreference(storage, current.envelope, now());
    } else {
      await replaceLocalReminderPreference(
        storage,
        current.envelope,
        mode as "off" | "in_app_when_available",
        now(),
      );
    }
    return redirect("/preferences/assistance");
  } catch (error) {
    const code = error instanceof Error && "code" in error
      ? String((error as { code: unknown }).code)
      : "";
    return actionFailure(
      "local",
      code === "no_change" ? "no-change" : code.startsWith("invalid_") ? "invalid" : "unavailable",
      intent,
    );
  }
}

export function createAssistancePreferencesAction(
  client: FinancialAcademyApiClient,
  session: SingleProfileSession,
  storage: LocalReminderPreferenceStorage,
  now: () => string,
) {
  return async ({ request }: ActionFunctionArgs) => {
    const form = await request.formData();
    const formIntent = single(form, "form_intent");
    if (formIntent === "local-save" || formIntent === "local-reset") {
      return changeLocal(form, storage, now);
    }
    const parsed = preparedServerRequest(form);
    const attemptedIntent = formIntent === "server-reset" ? "reset" : "save";
    if (!parsed) return actionFailure("server", "invalid", attemptedIntent);

    const established = await session.ensure(request.signal);
    if (established.status === "error") {
      return actionFailure("server", established.kind, parsed.intent, parsed.request);
    }
    try {
      let result = await client.POST(
        "/api/v1/learner-assistance-preferences/mutations",
        { body: parsed.request, signal: request.signal },
      );
      if (result.response.status === 401) {
        session.invalidate();
        const renewed = await session.ensure(request.signal);
        if (renewed.status === "error") {
          return actionFailure("server", renewed.kind, parsed.intent, parsed.request);
        }
        result = await client.POST(
          "/api/v1/learner-assistance-preferences/mutations",
          { body: parsed.request, signal: request.signal },
        );
      }
      if (result.response.status === 200) {
        const profile = result.data as AssistancePreferenceProfile | undefined;
        const expectedMode = parsed.request.mutation.operation === "reset_profile"
          ? "off"
          : parsed.request.mutation.assistance_mode;
        if (
          !profile ||
          !(await assistancePreferenceProfileIsSafe(profile)) ||
          profile.revision !== parsed.request.expected_revision + 1 ||
          profile.assistance_mode !== expectedMode
        ) return actionFailure(
          "server",
          "invalid-response",
          parsed.intent,
          parsed.request,
        );
        return redirect("/preferences/assistance");
      }
      if (result.response.status === 401) {
        return actionFailure("server", "unauthorized", parsed.intent, parsed.request);
      }
      if (result.response.status === 403) {
        return actionFailure("server", "forbidden", parsed.intent, parsed.request);
      }
      if (result.response.status === 404) {
        return actionFailure("server", "not-found", parsed.intent, parsed.request);
      }
      if (result.response.status === 409) {
        const kind = publicErrorCode(result.error) === "stale_revision" ? "stale" : "conflict";
        return actionFailure("server", kind, parsed.intent, parsed.request);
      }
      if (result.response.status === 422) {
        return actionFailure("server", "invalid", parsed.intent);
      }
      if (result.response.status === 503) {
        return actionFailure("server", "unavailable", parsed.intent, parsed.request);
      }
      return actionFailure(
        "server",
        "unexpected",
        parsed.intent,
        parsed.request,
      );
    } catch (error) {
      if (request.signal.aborted) throw error;
      return actionFailure("server", "unavailable", parsed.intent, parsed.request);
    }
  };
}

export function createAssistancePreferencesExporter(
  client: FinancialAcademyApiClient,
  session: SingleProfileSession,
) {
  return async (
    expectedRevision: number,
    expectedDigest: string,
  ): Promise<AssistancePreferencesExportOutcome> => {
    const result = await readServerExport(client, session);
    if (result.status !== "ready") return { status: result.status };
    if (
      result.profile.revision !== expectedRevision ||
      result.profile.profile_digest !== expectedDigest
    ) return { status: "changed" };
    return {
      status: "ready",
      content: `${JSON.stringify(result.export, null, 2)}\n`,
      fileName: "ai-help-preference.json",
    };
  };
}

export function createLocalReminderExporter(
  storage: Pick<LocalReminderPreferenceStorage, "getItem">,
  now: () => string,
) {
  return async (): Promise<AssistancePreferencesExportOutcome> => {
    const result = await readLocal(storage, now);
    if (!result.envelope || result.status === "unavailable") {
      return { status: "unavailable" };
    }
    try {
      return {
        status: "ready",
        content: `${await exportLocalReminderPreference(result.envelope)}\n`,
        fileName: "this-browser-reminder-choice.json",
      };
    } catch {
      return { status: "invalid-response" };
    }
  };
}

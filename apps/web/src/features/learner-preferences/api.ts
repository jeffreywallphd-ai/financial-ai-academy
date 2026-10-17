import {
  redirect,
  type ActionFunctionArgs,
  type LoaderFunctionArgs,
} from "react-router";

import type { FinancialAcademyApiClient } from "../../generated/api-client";
import type { SingleProfileSession } from "../../platform/auth/singleProfileSession";
import {
  learnerPreferenceExportIsSafe,
  learnerPreferenceHistoryIsSafe,
  learnerPreferenceProfileIsSafe,
  preferenceMutationErrorCode,
  type LearnerPreferenceMutation,
  type LearnerPreferenceExport,
  type LearnerPreferenceHistory,
  type LearnerPreferenceProfile,
  type LearnerPreferencesActionFailure,
  type LearnerPreferencesActionState,
  type LearnerPreferencesExporter,
  type LearnerPreferencesRouteState,
  type PreparedPreferenceRequest,
} from "./model";


const IDENTIFIER = /^[a-z0-9][a-z0-9._-]{2,63}$/;

function loaderFailure(status: number): Exclude<LearnerPreferencesRouteState, { status: "ready" }> {
  if (status === 401) return { status: "unauthorized" };
  if (status === 403) return { status: "forbidden" };
  if (status === 404) return { status: "not-found" };
  if (status === 409 || status === 503) return { status: "unavailable" };
  return { status: "unexpected" };
}

async function readPreferenceBundle(
  client: FinancialAcademyApiClient,
  session: SingleProfileSession,
  signal: AbortSignal,
  retryUnauthorized: boolean,
): Promise<LearnerPreferencesRouteState> {
  try {
    const [profileResult, historyResult] = await Promise.all([
      client.GET("/api/v1/learner-preferences", { signal }),
      client.GET("/api/v1/learner-preferences/history", { signal }),
    ]);
    if (profileResult.response.status === 200 && historyResult.response.status === 200) {
      const profile = profileResult.data as LearnerPreferenceProfile | undefined;
      const history = historyResult.data as LearnerPreferenceHistory | undefined;
      if (
        !profile ||
        !history ||
        !(await learnerPreferenceProfileIsSafe(profile)) ||
        !learnerPreferenceHistoryIsSafe(history, profile)
      ) return { status: "invalid-response" };
      return {
        status: "ready",
        profile,
        history,
      };
    }
    if (
      retryUnauthorized &&
      (profileResult.response.status === 401 || historyResult.response.status === 401)
    ) {
      session.invalidate();
      const renewed = await session.ensure(signal);
      if (renewed.status === "error") return { status: renewed.kind };
      return readPreferenceBundle(client, session, signal, false);
    }
    return loaderFailure(
      profileResult.response.status !== 200
        ? profileResult.response.status
        : historyResult.response.status,
    );
  } catch (error) {
    if (signal.aborted) throw error;
    return { status: "unavailable" };
  }
}

export function createLearnerPreferencesLoader(
  client: FinancialAcademyApiClient,
  session: SingleProfileSession,
) {
  return async ({ request }: LoaderFunctionArgs): Promise<LearnerPreferencesRouteState> => {
    const established = await session.ensure(request.signal);
    if (established.status === "error") return { status: established.kind };
    return readPreferenceBundle(client, session, request.signal, true);
  };
}

function text(value: FormDataEntryValue | null, minimum: number, maximum: number): string | undefined {
  if (typeof value !== "string") return undefined;
  const length = Array.from(value).length;
  return length >= minimum && length <= maximum ? value : undefined;
}

function required(form: FormData, name: string, maximum: number): string | undefined {
  return form.getAll(name).length === 1 ? text(form.get(name), 1, maximum) : undefined;
}

function optional(form: FormData, name: string, maximum: number): string | null | undefined {
  if (form.getAll(name).length !== 1) return undefined;
  const value = form.get(name);
  if (value === "") return null;
  return text(value, 1, maximum);
}

function identifier(form: FormData, name: string): string | undefined {
  const value = required(form, name, 64);
  return value && IDENTIFIER.test(value) ? value : undefined;
}

function exactFields(form: FormData, allowed: readonly string[]): boolean {
  const set = new Set(allowed);
  return [...form.keys()].every((key) => set.has(key));
}

function orderedIdentifiers(form: FormData): string[] | undefined {
  const values = form.getAll("ordered_ids");
  if (
    values.some((value) => typeof value !== "string" || !IDENTIFIER.test(value)) ||
    new Set(values).size !== values.length
  ) return undefined;
  return values as string[];
}

function mutationFromForm(form: FormData): LearnerPreferenceMutation | undefined {
  const operation = required(form, "operation", 32);
  const common = ["form_intent", "idempotency_key", "expected_revision", "operation"];
  if (operation === "create_goal" || operation === "update_goal") {
    const title = required(form, "title", 160);
    const detail = optional(form, "detail", 2_000);
    const fields = operation === "update_goal" ? [...common, "entry_id", "title", "detail"] : [...common, "title", "detail"];
    const entryId = operation === "update_goal" ? identifier(form, "entry_id") : undefined;
    if (!exactFields(form, fields) || !title || detail === undefined || (operation === "update_goal" && !entryId)) return undefined;
    return operation === "create_goal"
      ? { operation, title, detail }
      : { operation, entry_id: entryId!, title, detail };
  }
  if (operation === "archive_goal" || operation === "restore_goal") {
    const entryId = identifier(form, "entry_id");
    return exactFields(form, [...common, "entry_id"]) && entryId
      ? { operation, entry_id: entryId }
      : undefined;
  }
  if (operation === "remove_goal" || operation === "remove_experience" || operation === "remove_interest") {
    const entryId = identifier(form, "entry_id");
    return exactFields(form, [...common, "entry_id", "confirm_remove"]) &&
      entryId &&
      form.getAll("confirm_remove").length === 1 &&
      form.get("confirm_remove") === "remove"
      ? { operation, entry_id: entryId }
      : undefined;
  }
  if (operation === "reorder_goals" || operation === "reorder_experience" || operation === "reorder_interests") {
    const orderedIds = orderedIdentifiers(form);
    const maximum = operation === "reorder_interests" ? 50 : 20;
    return exactFields(form, [...common, "ordered_ids"]) && orderedIds && orderedIds.length <= maximum
      ? { operation, ordered_ids: orderedIds }
      : undefined;
  }
  if (operation === "create_experience" || operation === "update_experience") {
    const subject = required(form, "subject", 120);
    const level = required(form, "level", 32);
    const detail = optional(form, "detail", 1_000);
    const fields = operation === "update_experience" ? [...common, "entry_id", "subject", "level", "detail"] : [...common, "subject", "level", "detail"];
    const entryId = operation === "update_experience" ? identifier(form, "entry_id") : undefined;
    if (
      !exactFields(form, fields) || !subject || detail === undefined ||
      (level !== "new" && level !== "some_experience" && level !== "experienced") ||
      (operation === "update_experience" && !entryId)
    ) return undefined;
    return operation === "create_experience"
      ? { operation, subject, level, detail }
      : { operation, entry_id: entryId!, subject, level, detail };
  }
  if (operation === "create_interest" || operation === "rename_interest") {
    const label = required(form, "label", 120);
    const fields = operation === "rename_interest" ? [...common, "entry_id", "label"] : [...common, "label"];
    const entryId = operation === "rename_interest" ? identifier(form, "entry_id") : undefined;
    if (!exactFields(form, fields) || !label || (operation === "rename_interest" && !entryId)) return undefined;
    return operation === "create_interest"
      ? { operation, label }
      : { operation, entry_id: entryId!, label };
  }
  if (operation === "reset_profile") {
    return exactFields(form, [...common, "confirm_reset"]) &&
      form.getAll("confirm_reset").length === 1 &&
      form.get("confirm_reset") === "reset"
      ? { operation }
      : undefined;
  }
  return undefined;
}

function actionFailure(
  kind: LearnerPreferencesActionFailure,
  intent: string,
  preparedRequest?: PreparedPreferenceRequest,
): LearnerPreferencesActionState {
  return preparedRequest
    ? { status: "error", kind, intent, preparedRequest }
    : { status: "error", kind, intent };
}

function failureFromResult(
  status: number,
  error: unknown,
  intent: string,
  preparedRequest: PreparedPreferenceRequest,
): LearnerPreferencesActionState {
  if (status === 401) return actionFailure("unauthorized", intent, preparedRequest);
  if (status === 403) return actionFailure("forbidden", intent, preparedRequest);
  if (status === 404) return actionFailure("not-found", intent, preparedRequest);
  if (status === 400 || status === 422) return actionFailure("invalid", intent, preparedRequest);
  if (status === 503) return actionFailure("unavailable", intent, preparedRequest);
  if (status === 409) {
    const code = preferenceMutationErrorCode(error);
    if (code === "stale_revision") return actionFailure("stale", intent, preparedRequest);
    if (code === "preference_limit") return actionFailure("limit", intent);
    return actionFailure("conflict", intent, preparedRequest);
  }
  return actionFailure("unexpected", intent, preparedRequest);
}

async function sendMutation(
  client: FinancialAcademyApiClient,
  session: SingleProfileSession,
  signal: AbortSignal,
  body: PreparedPreferenceRequest,
  intent: string,
  retryUnauthorized: boolean,
): Promise<Response | LearnerPreferencesActionState> {
  try {
    const result = await client.POST("/api/v1/learner-preferences/mutations", { body, signal });
    if (result.response.status === 200) {
      return result.data && await learnerPreferenceProfileIsSafe(result.data)
        ? redirect("/preferences/learning")
        : actionFailure("invalid-response", intent, body);
    }
    if (result.response.status === 401 && retryUnauthorized) {
      session.invalidate();
      const renewed = await session.ensure(signal);
      if (renewed.status === "ready") return sendMutation(client, session, signal, body, intent, false);
      return actionFailure(renewed.kind, intent, body);
    }
    return failureFromResult(result.response.status, result.error, intent, body);
  } catch (error) {
    if (signal.aborted) throw error;
    return actionFailure("unavailable", intent, body);
  }
}

export function createLearnerPreferencesAction(
  client: FinancialAcademyApiClient,
  session: SingleProfileSession,
) {
  return async ({ request }: ActionFunctionArgs): Promise<Response | LearnerPreferencesActionState> => {
    const form = await request.formData();
    const intent = required(form, "form_intent", 180) ?? "preference-change";
    const idempotencyKey = identifier(form, "idempotency_key");
    const revisionText = required(form, "expected_revision", 20);
    const expectedRevision = revisionText ? Number(revisionText) : Number.NaN;
    const mutation = mutationFromForm(form);
    if (!idempotencyKey || !Number.isSafeInteger(expectedRevision) || expectedRevision < 1 || !mutation) {
      return actionFailure("invalid", intent);
    }
    const preparedRequest: PreparedPreferenceRequest = {
      schema_version: "1.0.0",
      idempotency_key: idempotencyKey,
      expected_revision: expectedRevision,
      mutation,
    };
    const established = await session.ensure(request.signal);
    if (established.status === "error") return actionFailure(established.kind, intent, preparedRequest);
    return sendMutation(client, session, request.signal, preparedRequest, intent, true);
  };
}

async function exportPreferences(
  client: FinancialAcademyApiClient,
  session: SingleProfileSession,
  expectedRevision: number,
  expectedDigest: string,
  retryUnauthorized: boolean,
): ReturnType<LearnerPreferencesExporter> {
  try {
    const result = await client.GET("/api/v1/learner-preferences/export", {});
    if (result.response.status === 200) {
      const exported = result.data as LearnerPreferenceExport | undefined;
      if (!exported || !(await learnerPreferenceExportIsSafe(exported))) return { status: "invalid-response" };
      if (exported.profile.revision !== expectedRevision || exported.profile.profile_digest !== expectedDigest) {
        return { status: "changed" };
      }
      return {
        status: "ready",
        content: JSON.stringify(exported, null, 2),
        export: exported,
        fileName: "learning-preferences-export.json",
      };
    }
    if (result.response.status === 401 && retryUnauthorized) {
      session.invalidate();
      const renewed = await session.ensure();
      if (renewed.status === "ready") return exportPreferences(client, session, expectedRevision, expectedDigest, false);
      return { status: renewed.kind };
    }
    if (result.response.status === 401) return { status: "unauthorized" };
    if (result.response.status === 403) return { status: "forbidden" };
    if (result.response.status === 404 || result.response.status === 409 || result.response.status === 503) return { status: "unavailable" };
    return { status: "unexpected" };
  } catch {
    return { status: "unavailable" };
  }
}

export function createLearnerPreferencesExporter(
  client: FinancialAcademyApiClient,
  session: SingleProfileSession,
): LearnerPreferencesExporter {
  return async (expectedRevision, expectedDigest) => {
    const established = await session.ensure();
    if (established.status === "error") return { status: established.kind };
    return exportPreferences(client, session, expectedRevision, expectedDigest, true);
  };
}

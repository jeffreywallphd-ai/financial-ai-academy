import {
  redirect,
  type ActionFunctionArgs,
  type LoaderFunctionArgs,
} from "react-router";

import type { FinancialAcademyApiClient } from "../../generated/api-client";
import type { SingleProfileSession } from "../../platform/auth/singleProfileSession";
import {
  BASELINE_PRESENTATION,
  presentationPreferenceExportIsSafe,
  presentationPreferenceProfileIsSafe,
  presentationSettingsEqual,
  presentationSettingsFromProfile,
  publicErrorCode,
  type PreparedPresentationPreferenceRequest,
  type PresentationPreferenceExport,
  type PresentationPreferenceProfile,
  type PresentationPreferencesActionState,
  type PresentationPreferencesExportOutcome,
  type PresentationPreferencesRouteState,
} from "./model";


const IDENTIFIER = /^[a-z0-9][a-z0-9._-]{2,63}$/;

function routeFailure(
  status: number,
): Exclude<PresentationPreferencesRouteState, { status: "ready" }> {
  if (status === 401) return { status: "unauthorized" };
  if (status === 403) return { status: "forbidden" };
  if (status === 404) return { status: "not-found" };
  if (status === 409 || status === 503) return { status: "unavailable" };
  return { status: "unexpected" };
}

async function readExportBundle(
  client: FinancialAcademyApiClient,
  session: SingleProfileSession,
  signal: AbortSignal,
  retryUnauthorized: boolean,
): Promise<PresentationPreferencesRouteState> {
  try {
    const result = await client.GET(
      "/api/v1/learner-presentation-preferences/export",
      { signal },
    );
    if (result.response.status === 200) {
      const value = result.data as PresentationPreferenceExport | undefined;
      if (!value || !(await presentationPreferenceExportIsSafe(value))) {
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
      const renewed = await session.ensure(signal);
      if (renewed.status === "error") return { status: renewed.kind };
      return readExportBundle(client, session, signal, false);
    }
    return routeFailure(result.response.status);
  } catch (error) {
    if (signal.aborted) throw error;
    return { status: "unavailable" };
  }
}

export function createPresentationPreferencesLoader(
  client: FinancialAcademyApiClient,
  session: SingleProfileSession,
) {
  return async ({ request }: LoaderFunctionArgs): Promise<PresentationPreferencesRouteState> => {
    const established = await session.ensure(request.signal);
    if (established.status === "error") return { status: established.kind };
    return readExportBundle(client, session, request.signal, true);
  };
}

export function createPresentationProfileReader(
  client: FinancialAcademyApiClient,
  session: SingleProfileSession,
) {
  return async (signal: AbortSignal): Promise<PresentationPreferenceProfile | null> => {
    const established = await session.ensure(signal);
    if (established.status === "error") return null;
    try {
      let result = await client.GET(
        "/api/v1/learner-presentation-preferences",
        { signal },
      );
      if (result.response.status === 401) {
        session.invalidate();
        const renewed = await session.ensure(signal);
        if (renewed.status === "error") return null;
        result = await client.GET(
          "/api/v1/learner-presentation-preferences",
          { signal },
        );
      }
      const profile = result.data as PresentationPreferenceProfile | undefined;
      return result.response.status === 200 &&
        profile &&
        await presentationPreferenceProfileIsSafe(profile)
        ? profile
        : null;
    } catch (error) {
      if (signal.aborted) throw error;
      return null;
    }
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

function preparedRequestFromForm(
  form: FormData,
): { intent: "reset" | "save"; request: PreparedPresentationPreferenceRequest } | undefined {
  const intent = single(form, "form_intent");
  const idempotencyKey = single(form, "idempotency_key");
  const revision = expectedRevision(form);
  if (!idempotencyKey || !IDENTIFIER.test(idempotencyKey) || revision === undefined) {
    return undefined;
  }
  if (intent === "reset") {
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
      intent,
      request: {
        schema_version: "1.0.0",
        idempotency_key: idempotencyKey,
        expected_revision: revision,
        mutation: { operation: "reset_profile" },
      },
    };
  }
  if (intent !== "save" || !exactFields(form, [
    "expected_revision",
    "form_intent",
    "idempotency_key",
    "motion",
    "operation",
    "reading_width",
    "text_size",
    "text_spacing",
  ])) return undefined;
  const textSize = single(form, "text_size");
  const textSpacing = single(form, "text_spacing");
  const readingWidth = single(form, "reading_width");
  const motion = single(form, "motion");
  if (
    single(form, "operation") !== "replace_preferences" ||
    (textSize !== "default" && textSize !== "larger") ||
    (textSpacing !== "default" && textSpacing !== "increased") ||
    (readingWidth !== "standard" && readingWidth !== "focused") ||
    (motion !== "system" && motion !== "reduce")
  ) return undefined;
  return {
    intent,
    request: {
      schema_version: "1.0.0",
      idempotency_key: idempotencyKey,
      expected_revision: revision,
      mutation: {
        operation: "replace_preferences",
        text_size: textSize,
        text_spacing: textSpacing,
        reading_width: readingWidth,
        motion,
      },
    },
  };
}

function actionFailure(
  kind: PresentationPreferencesActionState["kind"],
  intent: PresentationPreferencesActionState["intent"],
  preparedRequest?: PreparedPresentationPreferenceRequest,
): PresentationPreferencesActionState {
  return preparedRequest
    ? { status: "error", kind, intent, preparedRequest }
    : { status: "error", kind, intent };
}

export function createPresentationPreferencesAction(
  client: FinancialAcademyApiClient,
  session: SingleProfileSession,
) {
  return async ({ request }: ActionFunctionArgs) => {
    const form = await request.formData();
    const parsed = preparedRequestFromForm(form);
    const attemptedIntent = single(form, "form_intent") === "reset" ? "reset" : "save";
    if (!parsed) return actionFailure("invalid", attemptedIntent);

    const established = await session.ensure(request.signal);
    if (established.status === "error") {
      return actionFailure(established.kind, parsed.intent, parsed.request);
    }
    try {
      let result = await client.POST(
        "/api/v1/learner-presentation-preferences/mutations",
        { body: parsed.request, signal: request.signal },
      );
      if (result.response.status === 401) {
        session.invalidate();
        const renewed = await session.ensure(request.signal);
        if (renewed.status === "error") {
          return actionFailure(renewed.kind, parsed.intent, parsed.request);
        }
        result = await client.POST(
          "/api/v1/learner-presentation-preferences/mutations",
          { body: parsed.request, signal: request.signal },
        );
      }
      if (result.response.status === 200) {
        const profile = result.data as PresentationPreferenceProfile | undefined;
        const expectedSettings = parsed.request.mutation.operation === "reset_profile"
          ? BASELINE_PRESENTATION
          : {
              motion: parsed.request.mutation.motion,
              reading_width: parsed.request.mutation.reading_width,
              text_size: parsed.request.mutation.text_size,
              text_spacing: parsed.request.mutation.text_spacing,
            };
        if (
          !profile ||
          !(await presentationPreferenceProfileIsSafe(profile)) ||
          profile.revision !== parsed.request.expected_revision + 1 ||
          !presentationSettingsEqual(
            presentationSettingsFromProfile(profile),
            expectedSettings,
          )
        ) return actionFailure("invalid-response", parsed.intent);
        return redirect("/preferences/display");
      }
      if (result.response.status === 401) {
        return actionFailure("unauthorized", parsed.intent, parsed.request);
      }
      if (result.response.status === 403) {
        return actionFailure("forbidden", parsed.intent, parsed.request);
      }
      if (result.response.status === 404) {
        return actionFailure("not-found", parsed.intent, parsed.request);
      }
      if (result.response.status === 409) {
        const kind = publicErrorCode(result.error) === "stale_revision" ? "stale" : "conflict";
        return actionFailure(kind, parsed.intent, parsed.request);
      }
      if (result.response.status === 422) {
        return actionFailure("invalid", parsed.intent);
      }
      if (result.response.status === 503) {
        return actionFailure("unavailable", parsed.intent, parsed.request);
      }
      return actionFailure("unexpected", parsed.intent);
    } catch (error) {
      if (request.signal.aborted) throw error;
      return actionFailure("unavailable", parsed.intent, parsed.request);
    }
  };
}

async function readExportForDownload(
  client: FinancialAcademyApiClient,
  session: SingleProfileSession,
): Promise<PresentationPreferenceExport | PresentationPreferencesExportOutcome> {
  const established = await session.ensure();
  if (established.status === "error") return { status: established.kind };
  try {
    let result = await client.GET("/api/v1/learner-presentation-preferences/export");
    if (result.response.status === 401) {
      session.invalidate();
      const renewed = await session.ensure();
      if (renewed.status === "error") return { status: renewed.kind };
      result = await client.GET("/api/v1/learner-presentation-preferences/export");
    }
    if (result.response.status === 401) return { status: "unauthorized" };
    if (result.response.status === 403) return { status: "forbidden" };
    if (result.response.status !== 200) {
      return result.response.status === 503
        ? { status: "unavailable" }
        : { status: "unexpected" };
    }
    const value = result.data as PresentationPreferenceExport | undefined;
    return value && await presentationPreferenceExportIsSafe(value)
      ? value
      : { status: "invalid-response" };
  } catch {
    return { status: "unavailable" };
  }
}

export function createPresentationPreferencesExporter(
  client: FinancialAcademyApiClient,
  session: SingleProfileSession,
) {
  return async (
    expectedRevision: number,
    expectedDigest: string,
  ): Promise<PresentationPreferencesExportOutcome> => {
    const result = await readExportForDownload(client, session);
    if ("status" in result) return result;
    if (
      result.profile.revision !== expectedRevision ||
      result.profile.profile_digest !== expectedDigest
    ) return { status: "changed" };
    return {
      status: "ready",
      content: `${JSON.stringify(result, null, 2)}\n`,
      export: result,
      fileName: "display-accessibility-settings.json",
    };
  };
}

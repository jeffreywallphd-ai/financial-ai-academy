import { redirect, type ActionFunctionArgs, type LoaderFunctionArgs } from "react-router";

import type { components, FinancialAcademyApiClient } from "../../generated/api-client";
import type { SingleProfileSession } from "../../platform/auth/singleProfileSession";
import {
  learningProjectStartOptionIsSafe,
  learningStartOptionListIsSafe,
  projectIdentifierIsSafe,
  projectListIsSafe,
  projectShellIsSafe,
  type ProjectCreateActionState,
  type ProjectCreateRouteState,
  type ProjectDetailRouteState,
  type ProjectListRouteState,
} from "./model";

function stateFromStatus(status: number): "unauthorized" | "forbidden" | "unavailable" | "unexpected" {
  if (status === 401) return "unauthorized";
  if (status === 403) return "forbidden";
  if (status === 409 || status === 503) return "unavailable";
  return "unexpected";
}

async function ensure(session: SingleProfileSession, signal: AbortSignal) {
  return session.ensure(signal);
}

async function readProjectList(
  client: FinancialAcademyApiClient,
  session: SingleProfileSession,
  signal: AbortSignal,
  retryUnauthorized: boolean,
): Promise<ProjectListRouteState> {
  try {
    const [projects, options] = await Promise.all([
      client.GET("/api/v1/projects", { signal }),
      client.GET("/api/v1/projects/start-options", { signal }),
    ]);
    if (projects.response.status === 200 && options.response.status === 200) {
      return projects.data && options.data && projectListIsSafe(projects.data) && learningStartOptionListIsSafe(options.data)
        ? { status: "ready", projects: projects.data.records, options: options.data.records }
        : { status: "invalid-response" };
    }
    if ((projects.response.status === 401 || options.response.status === 401) && retryUnauthorized) {
      session.invalidate();
      const renewed = await ensure(session, signal);
      if (renewed.status === "error") return { status: renewed.kind };
      return readProjectList(client, session, signal, false);
    }
    return { status: stateFromStatus(projects.response.status === 200 ? options.response.status : projects.response.status) };
  } catch (error) {
    if (signal.aborted) throw error;
    return { status: "unavailable" };
  }
}

export function createProjectListLoader(client: FinancialAcademyApiClient, session: SingleProfileSession) {
  return async ({ request }: LoaderFunctionArgs): Promise<ProjectListRouteState> => {
    const established = await ensure(session, request.signal);
    if (established.status === "error") return { status: established.kind };
    return readProjectList(client, session, request.signal, true);
  };
}

async function readProjectDetail(
  client: FinancialAcademyApiClient,
  session: SingleProfileSession,
  signal: AbortSignal,
  projectId: string,
  retryUnauthorized: boolean,
): Promise<ProjectDetailRouteState> {
  try {
    const result = await client.GET("/api/v1/projects/{project_id}", { params: { path: { project_id: projectId } }, signal });
    if (result.response.status === 200) {
      return result.data && projectShellIsSafe(result.data) && result.data.project_id === projectId
        ? { status: "ready", project: result.data }
        : { status: "invalid-response" };
    }
    if (result.response.status === 401 && retryUnauthorized) {
      session.invalidate();
      const renewed = await ensure(session, signal);
      if (renewed.status === "error") return { status: renewed.kind };
      return readProjectDetail(client, session, signal, projectId, false);
    }
    if (result.response.status === 404) return { status: "not-found" };
    return { status: stateFromStatus(result.response.status) };
  } catch (error) {
    if (signal.aborted) throw error;
    return { status: "unavailable" };
  }
}

export function createProjectDetailLoader(client: FinancialAcademyApiClient, session: SingleProfileSession) {
  return async ({ request, params }: LoaderFunctionArgs): Promise<ProjectDetailRouteState> => {
    if (!projectIdentifierIsSafe(params.projectId)) return { status: "invalid-selection" };
    const established = await ensure(session, request.signal);
    if (established.status === "error") return { status: established.kind };
    return readProjectDetail(client, session, request.signal, params.projectId, true);
  };
}

function selectedPlacement(url: string): string | null | undefined {
  const parameters = new URL(url).searchParams;
  if ([...parameters.keys()].some((key) => key !== "placement")) return null;
  const values = parameters.getAll("placement");
  if (values.length === 0) return undefined;
  return values.length === 1 && projectIdentifierIsSafe(values[0]) ? values[0] : null;
}

async function readStartOption(
  client: FinancialAcademyApiClient,
  session: SingleProfileSession,
  signal: AbortSignal,
  placementId: string,
  retryUnauthorized: boolean,
): Promise<ProjectCreateRouteState> {
  try {
    const result = await client.GET("/api/v1/projects/start-options/{placement_id}", {
      params: { path: { placement_id: placementId } },
      signal,
    });
    if (result.response.status === 200) {
      return result.data && learningProjectStartOptionIsSafe(result.data) && result.data.origin.placement_id === placementId
        ? { status: "ready", option: result.data, idempotencyKey: crypto.randomUUID().toLowerCase() }
        : { status: "invalid-response" };
    }
    if (result.response.status === 401 && retryUnauthorized) {
      session.invalidate();
      const renewed = await ensure(session, signal);
      if (renewed.status === "error") return { status: renewed.kind };
      return readStartOption(client, session, signal, placementId, false);
    }
    if (result.response.status === 400 || result.response.status === 404) {
      return { status: "invalid-selection" };
    }
    return { status: stateFromStatus(result.response.status) };
  } catch (error) {
    if (signal.aborted) throw error;
    return { status: "unavailable" };
  }
}

export function createProjectCreateLoader(client: FinancialAcademyApiClient, session: SingleProfileSession) {
  return async ({ request }: LoaderFunctionArgs): Promise<ProjectCreateRouteState> => {
    const placementId = selectedPlacement(request.url);
    if (placementId === null) return { status: "invalid-selection" };
    const established = await ensure(session, request.signal);
    if (established.status === "error") return { status: established.kind };
    return placementId === undefined
      ? { status: "ready", option: null, idempotencyKey: crypto.randomUUID().toLowerCase() }
      : readStartOption(client, session, request.signal, placementId, true);
  };
}

function actionError(
  kind: ProjectCreateActionState["kind"],
  idempotencyKey: string,
  draft?: { title: string; charter: string },
): ProjectCreateActionState {
  return { status: "error", kind, idempotencyKey, ...(draft ? { draft } : {}) };
}

function oneFormValue(form: FormData, name: string): string | null {
  const values = form.getAll(name);
  return values.length === 1 && typeof values[0] === "string" ? values[0] : null;
}

export function createProjectCreateAction(client: FinancialAcademyApiClient, session: SingleProfileSession) {
  return async ({ request }: ActionFunctionArgs): Promise<Response | ProjectCreateActionState> => {
    const form = await request.formData();
    const allowed = new Set(["title", "charter", "placement_id", "idempotency_key"]);
    const idempotencyKey = oneFormValue(form, "idempotency_key") ?? "invalid";
    if ([...form.keys()].some((key) => !allowed.has(key))) return actionError("invalid-input", idempotencyKey);
    const title = oneFormValue(form, "title")?.trim();
    const charter = oneFormValue(form, "charter")?.trim();
    const placementId = oneFormValue(form, "placement_id");
    if (!title || title.length > 120 || !charter || charter.length > 4000 || !projectIdentifierIsSafe(idempotencyKey)
      || placementId === null || (placementId !== "" && !projectIdentifierIsSafe(placementId))) {
      return actionError("invalid-input", idempotencyKey);
    }
    const draft = { title, charter };
    const established = await ensure(session, request.signal);
    if (established.status === "error") return actionError(established.kind, idempotencyKey, draft);
    let origin: { origin_type: "independent" } | components["schemas"]["LearningProjectOriginModel"] = { origin_type: "independent" };
    if (placementId !== "") {
      const selected = await readStartOption(client, session, request.signal, placementId, true);
      if (selected.status !== "ready") {
        return actionError(selected.status === "invalid-response" ? "invalid-response" : selected.status, idempotencyKey, draft);
      }
      if (selected.option === null) return actionError("invalid-response", idempotencyKey, draft);
      origin = selected.option.origin;
    }
    try {
      const result = await client.POST("/api/v1/projects", {
        body: { schema_version: "1.0.0", idempotency_key: idempotencyKey, title, charter, origin },
        signal: request.signal,
      });
      if (result.response.status === 200) {
        return result.data && projectShellIsSafe(result.data)
          ? redirect(`/projects/${encodeURIComponent(result.data.project_id)}`)
          : actionError("invalid-response", idempotencyKey, draft);
      }
      if (result.response.status === 409) return actionError("conflict", idempotencyKey, draft);
      return actionError(stateFromStatus(result.response.status), idempotencyKey, draft);
    } catch (error) {
      if (request.signal.aborted) throw error;
      return actionError("unavailable", idempotencyKey, draft);
    }
  };
}

import { redirect, type ActionFunctionArgs, type LoaderFunctionArgs } from "react-router";

import type { components, FinancialAcademyApiClient } from "../../generated/api-client";
import type { SingleProfileSession } from "../../platform/auth/singleProfileSession";
import {
  learningProjectStartOptionIsSafe,
  learningStartOptionListIsSafe,
  logicalPathIsSafe,
  projectIdentifierIsSafe,
  projectListIsSafe,
  projectEvidenceExportBindingsAreSafe,
  projectEvidenceExportBundleIsSafe,
  projectSnapshotListIsSafe,
  projectShellIsSafe,
  projectWorkspaceIsSafe,
  type ProjectCreateActionState,
  type ProjectCreateRouteState,
  type ProjectDetailRouteState,
  type ProjectDownloadOutcome,
  type ProjectExportOutcome,
  type ProjectListRouteState,
  type ProjectArtifact,
  type ProjectWorkspaceActionState,
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
    const [projectResult, workspaceResult, snapshotsResult] = await Promise.all([
      client.GET("/api/v1/projects/{project_id}", { params: { path: { project_id: projectId } }, signal }),
      client.GET("/api/v1/projects/{project_id}/workspace", { params: { path: { project_id: projectId } }, signal }),
      client.GET("/api/v1/projects/{project_id}/snapshots", { params: { path: { project_id: projectId } }, signal }),
    ]);
    if (projectResult.response.status === 200 && workspaceResult.response.status === 200 && snapshotsResult.response.status === 200) {
      if (!projectResult.data || !projectShellIsSafe(projectResult.data) || projectResult.data.project_id !== projectId
        || !workspaceResult.data || !projectWorkspaceIsSafe(workspaceResult.data, projectResult.data)
        || !snapshotsResult.data || !projectSnapshotListIsSafe(snapshotsResult.data, projectResult.data)) {
        return { status: "invalid-response" };
      }
      return {
        status: "ready",
        project: projectResult.data,
        workspace: workspaceResult.data,
        snapshots: snapshotsResult.data.records,
      };
    }
    const failedStatus = [projectResult, workspaceResult, snapshotsResult]
      .find((result) => result.response.status !== 200)?.response.status ?? 500;
    if (failedStatus === 401 && retryUnauthorized) {
      session.invalidate();
      const renewed = await ensure(session, signal);
      if (renewed.status === "error") return { status: renewed.kind };
      return readProjectDetail(client, session, signal, projectId, false);
    }
    if (failedStatus === 404) return { status: "not-found" };
    return { status: stateFromStatus(failedStatus) };
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

function workspaceActionError(
  kind: ProjectWorkspaceActionState["kind"],
  intent: ProjectWorkspaceActionState["intent"],
  idempotencyKey: string,
): ProjectWorkspaceActionState {
  return { status: "error", kind, intent, idempotencyKey };
}

function integerFormValue(form: FormData, name: string): number | null {
  const value = oneFormValue(form, name);
  if (value === null || !/^[1-9][0-9]*$/.test(value)) return null;
  const parsed = Number(value);
  return Number.isSafeInteger(parsed) ? parsed : null;
}

function optionalFormValue(form: FormData, name: string): string | undefined {
  const value = oneFormValue(form, name);
  if (value === null) return undefined;
  const trimmed = value.trim();
  return trimmed === "" ? undefined : trimmed;
}

function publicErrorCode(value: unknown): string | null {
  if (typeof value !== "object" || value === null || Array.isArray(value)) return null;
  const code = (value as Record<string, unknown>).code;
  return typeof code === "string" ? code : null;
}

function workspaceFailure(
  status: number,
  error: unknown,
  intent: ProjectWorkspaceActionState["intent"],
  idempotencyKey: string,
): ProjectWorkspaceActionState {
  if (status === 400 || status === 422) return workspaceActionError("invalid-input", intent, idempotencyKey);
  if (status === 401) return workspaceActionError("unauthorized", intent, idempotencyKey);
  if (status === 403) return workspaceActionError("forbidden", intent, idempotencyKey);
  if (status === 404) return workspaceActionError("not-found", intent, idempotencyKey);
  if (status === 409) {
    return workspaceActionError(publicErrorCode(error) === "stale_revision" ? "stale" : "conflict", intent, idempotencyKey);
  }
  if (status === 503) return workspaceActionError("unavailable", intent, idempotencyKey);
  return workspaceActionError("unexpected", intent, idempotencyKey);
}

function validRequestKey(value: string | null): value is string {
  return value !== null && projectIdentifierIsSafe(value);
}

function safeSimpleText(value: string | null, maximum: number): value is string {
  return value !== null && value.length >= 1 && value.length <= maximum && !/[<>\0]/.test(value);
}

function safeBody(value: string | null): value is string {
  return value !== null && value.length >= 1 && value.length <= 20_000 && !value.includes("\0");
}

function safeHttpsUrl(value: string | undefined): value is string {
  if (!value || value.length > 2048) return false;
  try {
    const parsed = new URL(value);
    const authority = value.slice(value.indexOf("//") + 2).split(/[/?#]/, 1)[0] ?? "";
    return parsed.protocol === "https:" && parsed.hostname !== "" && !authority.includes("@");
  } catch {
    return false;
  }
}

function bytesToBase64(bytes: Uint8Array): string {
  let binary = "";
  for (let offset = 0; offset < bytes.length; offset += 32_768) {
    binary += String.fromCharCode(...bytes.subarray(offset, offset + 32_768));
  }
  return btoa(binary);
}

function base64ToBytes(value: string): Uint8Array {
  const binary = atob(value);
  const bytes = new Uint8Array(binary.length);
  for (let index = 0; index < binary.length; index += 1) bytes[index] = binary.charCodeAt(index);
  return bytes;
}

async function sha256(bytes: ArrayBuffer): Promise<string> {
  const result = new Uint8Array(await crypto.subtle.digest("SHA-256", bytes));
  return [...result].map((value) => value.toString(16).padStart(2, "0")).join("");
}

const ARTIFACT_KINDS = new Set(["dataset", "notebook", "code", "environment", "result", "reflection", "supporting_file"]);
const RESULT_CLASSES = new Set(["observed", "calculated", "simulated", "predicted", "generated", "narrative"]);
const SOURCE_TYPES = new Set(["learner_created", "supplied", "external"]);
const MEDIA_TYPES = new Set([
  "application/octet-stream", "application/json", "application/pdf", "application/x-ipynb+json",
  "text/csv", "text/markdown", "text/plain", "text/x-python",
]);

function allowedFields(intent: string): Set<string> {
  const common = ["intent", "idempotency_key", "expected_workspace_revision"];
  if (intent === "add-note") return new Set([...common, "title", "body"]);
  if (intent === "replace-note") return new Set([...common, "note_id", "note_version", "title", "body"]);
  if (intent === "add-reference") return new Set([...common, "title", "url", "source_name", "source_version", "source_digest", "license", "use_constraints"]);
  if (intent === "replace-reference") return new Set([...common, "reference_id", "reference_version", "title", "url", "source_name", "source_version", "source_digest", "license", "use_constraints"]);
  if (intent === "add-artifact") return new Set([...common, "file", "artifact_kind", "result_classification", "source_type", "source_title", "source_url", "source_version", "source_digest", "license", "use_constraints", "assumptions", "media_type"]);
  if (intent === "close-snapshot") return new Set([...common, "expected_project_revision"]);
  return new Set();
}

type WorkspacePostResult = Awaited<ReturnType<FinancialAcademyApiClient["POST"]>>;

async function postWithRenewal(
  operation: () => Promise<WorkspacePostResult>,
  session: SingleProfileSession,
  signal: AbortSignal,
): Promise<WorkspacePostResult> {
  const first = await operation();
  if (first.response.status !== 401) return first;
  session.invalidate();
  const renewed = await ensure(session, signal);
  return renewed.status === "ready" ? operation() : first;
}

export function createProjectWorkspaceAction(client: FinancialAcademyApiClient, session: SingleProfileSession) {
  return async ({ request, params }: ActionFunctionArgs): Promise<Response | ProjectWorkspaceActionState> => {
    const projectId = params.projectId;
    if (!projectIdentifierIsSafe(projectId)) return workspaceActionError("invalid-input", "note", "invalid");
    const form = await request.formData();
    const rawIntent = oneFormValue(form, "intent");
    const intentName = rawIntent === "add-reference" || rawIntent === "replace-reference" ? "reference"
      : rawIntent === "add-artifact" ? "artifact" : rawIntent === "close-snapshot" ? "snapshot" : "note";
    const idempotencyKey = oneFormValue(form, "idempotency_key") ?? "invalid";
    const allowed = rawIntent ? allowedFields(rawIntent) : new Set<string>();
    if (allowed.size === 0 || [...form.keys()].some((key) => !allowed.has(key)) || !validRequestKey(idempotencyKey)) {
      return workspaceActionError("invalid-input", intentName, idempotencyKey);
    }
    const workspaceRevision = integerFormValue(form, "expected_workspace_revision");
    if (workspaceRevision === null) return workspaceActionError("invalid-input", intentName, idempotencyKey);
    const established = await ensure(session, request.signal);
    if (established.status === "error") return workspaceActionError(established.kind, intentName, idempotencyKey);
    try {
      let result: WorkspacePostResult;
      if (rawIntent === "close-snapshot") {
        const projectRevision = integerFormValue(form, "expected_project_revision");
        if (projectRevision === null) return workspaceActionError("invalid-input", "snapshot", idempotencyKey);
        result = await postWithRenewal(() => client.POST("/api/v1/projects/{project_id}/snapshots", {
          params: { path: { project_id: projectId } },
          body: { schema_version: "1.0.0", idempotency_key: idempotencyKey, expected_project_revision: projectRevision, expected_workspace_revision: workspaceRevision },
          signal: request.signal,
        }), session, request.signal);
        if (result.response.status === 200) return redirect(`/projects/${encodeURIComponent(projectId)}#snapshots`);
        return workspaceFailure(result.response.status, result.error, "snapshot", idempotencyKey);
      }

      if (rawIntent === "add-artifact") {
        const fileValue = form.get("file");
        const artifactKind = oneFormValue(form, "artifact_kind");
        const resultClass = optionalFormValue(form, "result_classification");
        const sourceType = oneFormValue(form, "source_type");
        const sourceTitle = oneFormValue(form, "source_title")?.trim() ?? null;
        const mediaType = oneFormValue(form, "media_type");
        if (!fileValue || typeof fileValue === "string" || fileValue.size > 10_485_760 || !logicalPathIsSafe(fileValue.name)
          || !artifactKind || !ARTIFACT_KINDS.has(artifactKind) || !sourceType || !SOURCE_TYPES.has(sourceType)
          || !safeSimpleText(sourceTitle, 160) || !mediaType || !MEDIA_TYPES.has(mediaType)
          || (resultClass !== undefined && !RESULT_CLASSES.has(resultClass))
          || (artifactKind === "result" ? resultClass === undefined : resultClass !== undefined && resultClass !== "narrative")) {
          return workspaceActionError("invalid-input", "artifact", idempotencyKey);
        }
        const sourceUrl = optionalFormValue(form, "source_url");
        const sourceVersion = optionalFormValue(form, "source_version");
        const sourceDigest = optionalFormValue(form, "source_digest");
        const license = optionalFormValue(form, "license");
        const useConstraints = optionalFormValue(form, "use_constraints");
        if ((sourceUrl !== undefined && !safeHttpsUrl(sourceUrl))
          || (sourceVersion !== undefined && !safeSimpleText(sourceVersion, 128))
          || (sourceDigest !== undefined && !/^[a-f0-9]{64}$/.test(sourceDigest))
          || (license !== undefined && !safeSimpleText(license, 160))
          || (useConstraints !== undefined && !safeSimpleText(useConstraints, 1000))
          || (sourceType !== "learner_created" && sourceVersion === undefined && sourceDigest === undefined)) {
          return workspaceActionError("invalid-input", "artifact", idempotencyKey);
        }
        const assumptions = (oneFormValue(form, "assumptions") ?? "").split(/\r?\n/).map((item) => item.trim()).filter(Boolean);
        if (assumptions.length > 20 || assumptions.some((item) => !safeSimpleText(item, 4000))) {
          return workspaceActionError("invalid-input", "artifact", idempotencyKey);
        }
        const content = await fileValue.arrayBuffer();
        const provenance = {
          source_type: sourceType as "learner_created" | "supplied" | "external",
          source_title: sourceTitle,
          ...(sourceUrl ? { source_url: sourceUrl } : {}),
          ...(sourceVersion ? { source_version: sourceVersion } : {}),
          ...(sourceDigest ? { source_digest: sourceDigest } : {}),
          ...(license ? { license } : {}),
          ...(useConstraints ? { use_constraints: useConstraints } : {}),
        };
        const artifact: components["schemas"]["ProjectArtifactInputModel"] = {
          artifact_kind: artifactKind as components["schemas"]["ProjectArtifactInputModel"]["artifact_kind"],
          assumptions,
          byte_count: content.byteLength,
          content_digest: await sha256(content),
          inspection_mode: mediaType.startsWith("text/") ? "plain_text" : "metadata_only",
          logical_path: fileValue.name,
          media_type: mediaType as components["schemas"]["ProjectArtifactInputModel"]["media_type"],
          provenance,
          ...(resultClass ? { result_classification: resultClass as NonNullable<components["schemas"]["ProjectArtifactInputModel"]["result_classification"]> } : {}),
        };
        result = await postWithRenewal(() => client.POST("/api/v1/projects/{project_id}/artifacts", {
          params: { path: { project_id: projectId } }, signal: request.signal,
          body: { content_base64: bytesToBase64(new Uint8Array(content)), intent: { schema_version: "1.0.0", idempotency_key: idempotencyKey, expected_workspace_revision: workspaceRevision, mutation: { operation: "add_artifact", artifact } } },
        }), session, request.signal);
      } else if (rawIntent === "add-note" || rawIntent === "replace-note") {
        const title = oneFormValue(form, "title")?.trim() ?? null;
        const body = oneFormValue(form, "body");
        if (!safeSimpleText(title, 120) || !safeBody(body)) return workspaceActionError("invalid-input", "note", idempotencyKey);
        const mutation: components["schemas"]["AddProjectNoteModel"] | components["schemas"]["ReplaceProjectNoteModel"] = rawIntent === "add-note"
          ? { operation: "add_note", title, body }
          : { operation: "replace_note", note_id: oneFormValue(form, "note_id") ?? "", expected_note_version: integerFormValue(form, "note_version") ?? 0, title, body };
        if (mutation.operation === "replace_note" && (!projectIdentifierIsSafe(mutation.note_id) || mutation.expected_note_version < 1)) {
          return workspaceActionError("invalid-input", "note", idempotencyKey);
        }
        result = await postWithRenewal(() => client.POST("/api/v1/projects/{project_id}/workspace/mutations", {
          params: { path: { project_id: projectId } }, signal: request.signal,
          body: { schema_version: "1.0.0", idempotency_key: idempotencyKey, expected_workspace_revision: workspaceRevision, mutation },
        }), session, request.signal);
      } else {
        const title = oneFormValue(form, "title")?.trim() ?? null;
        const url = optionalFormValue(form, "url");
        const sourceName = oneFormValue(form, "source_name")?.trim() ?? null;
        const sourceVersion = optionalFormValue(form, "source_version");
        const sourceDigest = optionalFormValue(form, "source_digest");
        const license = optionalFormValue(form, "license");
        const useConstraints = optionalFormValue(form, "use_constraints");
        if (!safeSimpleText(title, 160) || !safeHttpsUrl(url) || !safeSimpleText(sourceName, 160)
          || (sourceVersion !== undefined && !safeSimpleText(sourceVersion, 128))
          || (sourceDigest !== undefined && !/^[a-f0-9]{64}$/.test(sourceDigest))
          || (license !== undefined && !safeSimpleText(license, 160))
          || (useConstraints !== undefined && !safeSimpleText(useConstraints, 1000))) {
          return workspaceActionError("invalid-input", "reference", idempotencyKey);
        }
        const common = { title, url, source_name: sourceName, ...(sourceVersion ? { source_version: sourceVersion } : {}), ...(sourceDigest ? { source_digest: sourceDigest } : {}), ...(license ? { license } : {}), ...(useConstraints ? { use_constraints: useConstraints } : {}) };
        const mutation: components["schemas"]["AddProjectReferenceModel"] | components["schemas"]["ReplaceProjectReferenceModel"] = rawIntent === "add-reference"
          ? { operation: "add_reference", ...common }
          : { operation: "replace_reference", reference_id: oneFormValue(form, "reference_id") ?? "", expected_reference_version: integerFormValue(form, "reference_version") ?? 0, ...common };
        if (mutation.operation === "replace_reference" && (!projectIdentifierIsSafe(mutation.reference_id) || mutation.expected_reference_version < 1)) {
          return workspaceActionError("invalid-input", "reference", idempotencyKey);
        }
        result = await postWithRenewal(() => client.POST("/api/v1/projects/{project_id}/workspace/mutations", {
          params: { path: { project_id: projectId } }, signal: request.signal,
          body: { schema_version: "1.0.0", idempotency_key: idempotencyKey, expected_workspace_revision: workspaceRevision, mutation },
        }), session, request.signal);
      }
      if (result.response.status === 200) {
        return result.data && projectWorkspaceIsSafe(result.data) && result.data.project_id === projectId
          ? redirect(`/projects/${encodeURIComponent(projectId)}`)
          : workspaceActionError("invalid-response", intentName, idempotencyKey);
      }
      return workspaceFailure(result.response.status, result.error, intentName, idempotencyKey);
    } catch (error) {
      if (request.signal.aborted) throw error;
      return workspaceActionError("unavailable", intentName, idempotencyKey);
    }
  };
}

function downloadFailure(status: number): Exclude<ProjectDownloadOutcome, { status: "ready" }> {
  if (status === 401) return { status: "unauthorized" };
  if (status === 403) return { status: "forbidden" };
  if (status === 404) return { status: "not-found" };
  if (status === 409 || status === 503) return { status: "unavailable" };
  return { status: "unexpected" };
}

export function createProjectArtifactDownloader(client: FinancialAcademyApiClient, session: SingleProfileSession) {
  return async (projectId: string, artifact: ProjectArtifact): Promise<ProjectDownloadOutcome> => {
    if (!projectIdentifierIsSafe(projectId)) return { status: "not-found" };
    const established = await session.ensure();
    if (established.status === "error") return { status: established.kind };
    try {
      const read = () => client.GET("/api/v1/projects/{project_id}/artifacts/{artifact_id}/versions/{artifact_version}", {
        params: { path: { project_id: projectId, artifact_id: artifact.artifact_id, artifact_version: artifact.artifact_version } },
        parseAs: "arrayBuffer",
      });
      let result = await read();
      if (result.response.status === 401) {
        session.invalidate();
        const renewed = await session.ensure();
        if (renewed.status === "ready") result = await read();
      }
      if (result.response.status !== 200) return downloadFailure(result.response.status);
      const bytes = Object.prototype.toString.call(result.data) === "[object ArrayBuffer]"
        ? result.data as ArrayBuffer
        : null;
      if (!bytes || bytes.byteLength !== artifact.byte_count
        || await sha256(bytes) !== artifact.content_digest) return { status: "invalid-response" };
      const fileName = artifact.logical_path.split("/").at(-1) ?? "project-artifact";
      return { status: "ready", bytes, fileName, mediaType: artifact.media_type };
    } catch {
      return { status: "unavailable" };
    }
  };
}

function exportFailure(status: number): Exclude<ProjectExportOutcome, { status: "ready" }> {
  if (status === 401) return { status: "unauthorized" };
  if (status === 403) return { status: "forbidden" };
  if (status === 404) return { status: "not-found" };
  if (status === 409 || status === 503) return { status: "unavailable" };
  return { status: "unexpected" };
}

export function createProjectSnapshotExporter(client: FinancialAcademyApiClient, session: SingleProfileSession) {
  return async (projectId: string, snapshotId: string): Promise<ProjectExportOutcome> => {
    if (!projectIdentifierIsSafe(projectId) || !projectIdentifierIsSafe(snapshotId)) return { status: "not-found" };
    const established = await session.ensure();
    if (established.status === "error") return { status: established.kind };
    try {
      const read = () => client.GET("/api/v1/projects/{project_id}/snapshots/{snapshot_id}/export", {
        params: { path: { project_id: projectId, snapshot_id: snapshotId } },
      });
      let result = await read();
      if (result.response.status === 401) {
        session.invalidate();
        const renewed = await session.ensure();
        if (renewed.status === "ready") result = await read();
      }
      if (result.response.status !== 200) return exportFailure(result.response.status);
      const data = result.data as unknown;
      if (!projectEvidenceExportBundleIsSafe(data, projectId, snapshotId)
        || !await projectEvidenceExportBindingsAreSafe(data)) return { status: "invalid-response" };
      const included = new Map(data.manifest.export.artifact_files.map((file) => [`${file.artifact_id}@${file.artifact_version}`, file]));
      for (const file of data.files) {
        const expected = included.get(`${file.artifact_id}@${file.artifact_version}`);
        const bytes = base64ToBytes(file.content_base64);
        if (!expected || bytes.byteLength !== expected.byte_count || await sha256(bytes.buffer as ArrayBuffer) !== expected.content_digest) {
          return { status: "invalid-response" };
        }
      }
      return { status: "ready", content: JSON.stringify(data, null, 2), fileName: `${projectId}-${snapshotId}-evidence.json` };
    } catch {
      return { status: "unavailable" };
    }
  };
}

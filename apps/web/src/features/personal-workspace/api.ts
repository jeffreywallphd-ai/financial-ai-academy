import {
  redirect,
  type ActionFunctionArgs,
  type LoaderFunctionArgs,
} from "react-router";

import type {
  FinancialAcademyApiClient,
} from "../../generated/api-client";
import type { SingleProfileSession } from "../../platform/auth/singleProfileSession";
import {
  mutationErrorCode,
  parseSaveSelection,
  personalWorkspaceIsSafe,
  workspaceIdentifierIsSafe,
  type PersonalWorkspaceMutation,
  type SaveLearningRouteState,
  type WorkspaceActionFailure,
  type WorkspaceActionState,
  type WorkspaceRouteState,
} from "./model";


function loaderFailure(status: number): Exclude<WorkspaceRouteState, { status: "ready" }> {
  if (status === 401) return { status: "unauthorized" };
  if (status === 403) return { status: "forbidden" };
  if (status === 404) return { status: "not-found" };
  if (status === 409 || status === 503) return { status: "unavailable" };
  return { status: "unexpected" };
}

async function readWorkspace(
  client: FinancialAcademyApiClient,
  session: SingleProfileSession,
  signal: AbortSignal,
  retryUnauthorized: boolean,
): Promise<WorkspaceRouteState> {
  try {
    const result = await client.GET("/api/v1/personal-workspace", { signal });
    if (result.response.status === 200) {
      return result.data && personalWorkspaceIsSafe(result.data)
        ? { status: "ready", workspace: result.data }
        : { status: "invalid-response" };
    }
    if (result.response.status === 401 && retryUnauthorized) {
      session.invalidate();
      const renewed = await session.ensure(signal);
      if (renewed.status === "error") return { status: renewed.kind };
      return readWorkspace(client, session, signal, false);
    }
    return loaderFailure(result.response.status);
  } catch (error) {
    if (signal.aborted) throw error;
    return { status: "unavailable" };
  }
}

export function createPersonalWorkspaceLoader(
  client: FinancialAcademyApiClient,
  session: SingleProfileSession,
) {
  return async ({ request }: LoaderFunctionArgs): Promise<WorkspaceRouteState> => {
    const established = await session.ensure(request.signal);
    if (established.status === "error") return { status: established.kind };
    return readWorkspace(client, session, request.signal, true);
  };
}

export function createSaveLearningLoader(
  client: FinancialAcademyApiClient,
  session: SingleProfileSession,
) {
  return async ({ request }: LoaderFunctionArgs): Promise<SaveLearningRouteState> => {
    const selection = parseSaveSelection(new URL(request.url));
    if (!selection) return { status: "invalid-selection" };
    const established = await session.ensure(request.signal);
    if (established.status === "error") return { status: established.kind };
    const state = await readWorkspace(client, session, request.signal, true);
    return state.status === "ready"
      ? { ...state, selection }
      : state;
  };
}

function required(form: FormData, name: string, maximum = 10_000): string | undefined {
  const values = form.getAll(name);
  if (values.length !== 1 || typeof values[0] !== "string") return undefined;
  const value = values[0];
  return value.length >= 1 && value.length <= maximum && value.trim().length > 0
    ? value
    : undefined;
}

function optional(form: FormData, name: string, maximum = 200): string | null | undefined {
  const values = form.getAll(name);
  if (values.length !== 1 || typeof values[0] !== "string") return undefined;
  const value = values[0];
  if (value === "") return null;
  return value.length <= maximum && value.trim().length > 0 ? value : undefined;
}

function identifier(form: FormData, name: string): string | undefined {
  const value = required(form, name, 128);
  return value && workspaceIdentifierIsSafe(value) ? value : undefined;
}

function identifiers(form: FormData, name: string): string[] | undefined {
  const values = form.getAll(name);
  if (
    values.some((value) => typeof value !== "string" || !workspaceIdentifierIsSafe(value)) ||
    new Set(values).size !== values.length
  ) {
    return undefined;
  }
  return values as string[];
}

function sourceSelector(form: FormData) {
  const kind = required(form, "reference_kind", 32);
  const placementId = required(form, "placement_id", 64);
  if (!placementId) return undefined;
  if (kind === "placed_lesson") {
    return { reference_kind: kind, placement_id: placementId } as const;
  }
  const opportunityId = required(form, "opportunity_id", 64);
  return kind === "learning_opportunity" && opportunityId
    ? {
        reference_kind: kind,
        opportunity_id: opportunityId,
        placement_id: placementId,
      } as const
    : undefined;
}

function mutationFromForm(form: FormData): PersonalWorkspaceMutation | undefined {
  const operation = required(form, "operation", 40);
  if (operation === "create_note") {
    const selector = sourceSelector(form);
    const title = required(form, "title", 200);
    const body = required(form, "body", 10_000);
    return selector && title && body
      ? { operation, selector, title, body }
      : undefined;
  }
  if (operation === "create_bookmark") {
    const selector = sourceSelector(form);
    const label = optional(form, "label");
    return selector && label !== undefined
      ? { operation, selector, label }
      : undefined;
  }
  if (operation === "update_note") {
    const recordId = identifier(form, "record_id");
    const title = required(form, "title", 200);
    const body = required(form, "body", 10_000);
    return recordId && title && body
      ? { operation, record_id: recordId, title, body }
      : undefined;
  }
  if (operation === "update_bookmark") {
    const recordId = identifier(form, "record_id");
    const label = optional(form, "label");
    return recordId && label !== undefined
      ? { operation, record_id: recordId, label }
      : undefined;
  }
  if (operation === "create_collection") {
    const title = required(form, "title", 200);
    return title ? { operation, title } : undefined;
  }
  if (operation === "rename_collection") {
    const collectionId = identifier(form, "collection_id");
    const title = required(form, "title", 200);
    return collectionId && title
      ? { operation, collection_id: collectionId, title }
      : undefined;
  }
  if (operation === "remove_collection") {
    const collectionId = identifier(form, "collection_id");
    return collectionId
      ? { operation, collection_id: collectionId }
      : undefined;
  }
  if (operation === "set_collection_members") {
    const collectionId = identifier(form, "collection_id");
    const memberRecordIds = identifiers(form, "member_record_ids");
    return collectionId && memberRecordIds
      ? {
          operation,
          collection_id: collectionId,
          member_record_ids: memberRecordIds,
        }
      : undefined;
  }
  if (operation === "reorder_records") {
    const recordIds = identifiers(form, "record_ids");
    return recordIds ? { operation, record_ids: recordIds } : undefined;
  }
  if (
    operation === "archive_record" ||
    operation === "restore_record" ||
    operation === "remove_record"
  ) {
    const recordId = identifier(form, "record_id");
    return recordId ? { operation, record_id: recordId } : undefined;
  }
  return undefined;
}

function actionFailure(
  kind: WorkspaceActionFailure,
  intent: string,
  idempotencyKey: string,
): WorkspaceActionState {
  return { status: "error", kind, intent, idempotencyKey };
}

function failureFromResult(
  status: number,
  error: unknown,
  intent: string,
  idempotencyKey: string,
): WorkspaceActionState {
  if (status === 401) return actionFailure("unauthorized", intent, idempotencyKey);
  if (status === 403) return actionFailure("forbidden", intent, idempotencyKey);
  if (status === 404) return actionFailure("not-found", intent, idempotencyKey);
  if (status === 400 || status === 422) return actionFailure("invalid", intent, idempotencyKey);
  if (status === 503) return actionFailure("unavailable", intent, idempotencyKey);
  if (status === 409) {
    const code = mutationErrorCode(error);
    if (code === "stale_revision") return actionFailure("stale", intent, idempotencyKey);
    if (code === "source_unavailable") return actionFailure("source-unavailable", intent, idempotencyKey);
    return actionFailure("conflict", intent, idempotencyKey);
  }
  return actionFailure("unexpected", intent, idempotencyKey);
}

async function sendMutation(
  client: FinancialAcademyApiClient,
  session: SingleProfileSession,
  signal: AbortSignal,
  body: {
    schema_version: "1.0.0";
    idempotency_key: string;
    expected_revision: number;
    mutation: PersonalWorkspaceMutation;
  },
  intent: string,
  retryUnauthorized: boolean,
): Promise<Response | WorkspaceActionState> {
  try {
    const result = await client.POST("/api/v1/personal-workspace/mutations", {
      body,
      signal,
    });
    if (result.response.status === 200) {
      return result.data && personalWorkspaceIsSafe(result.data)
        ? redirect("/saved-learning")
        : actionFailure("invalid-response", intent, body.idempotency_key);
    }
    if (result.response.status === 401 && retryUnauthorized) {
      session.invalidate();
      const renewed = await session.ensure(signal);
      if (renewed.status === "ready") {
        return sendMutation(client, session, signal, body, intent, false);
      }
      return actionFailure(renewed.kind, intent, body.idempotency_key);
    }
    return failureFromResult(
      result.response.status,
      result.error,
      intent,
      body.idempotency_key,
    );
  } catch (error) {
    if (signal.aborted) throw error;
    return actionFailure("unavailable", intent, body.idempotency_key);
  }
}

export function createPersonalWorkspaceAction(
  client: FinancialAcademyApiClient,
  session: SingleProfileSession,
) {
  return async ({ request }: ActionFunctionArgs): Promise<Response | WorkspaceActionState> => {
    const form = await request.formData();
    const intent = required(form, "form_intent", 180) ?? "workspace-change";
    const idempotencyKey = identifier(form, "idempotency_key") ?? "invalid-request";
    const revisionValue = required(form, "expected_revision", 20);
    const expectedRevision = revisionValue ? Number(revisionValue) : Number.NaN;
    const mutation = mutationFromForm(form);
    if (
      idempotencyKey === "invalid-request" ||
      !Number.isSafeInteger(expectedRevision) ||
      expectedRevision < 1 ||
      !mutation
    ) {
      return actionFailure("invalid", intent, idempotencyKey);
    }
    const established = await session.ensure(request.signal);
    if (established.status === "error") {
      return actionFailure(established.kind, intent, idempotencyKey);
    }
    const result = await sendMutation(
      client,
      session,
      request.signal,
      {
        schema_version: "1.0.0",
        idempotency_key: idempotencyKey,
        expected_revision: expectedRevision,
        mutation,
      },
      intent,
      true,
    );
    return result instanceof Response
      ? result
      : { ...result, retryMutation: mutation };
  };
}

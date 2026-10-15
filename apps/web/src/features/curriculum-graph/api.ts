import type { LoaderFunctionArgs } from "react-router";

import type { FinancialAcademyApiClient } from "../../generated/api-client";
import type { SingleProfileSession } from "../../platform/auth/singleProfileSession";
import type {
  CurriculumGraphRouteState,
  CurriculumGraphSelection,
} from "./model";
import {
  curriculumGraphIsSafe,
  parseCurriculumGraphSelection,
} from "./model";

function sessionFailureState(
  kind: "forbidden" | "unauthorized" | "unavailable" | "unexpected",
): CurriculumGraphRouteState {
  return { status: kind };
}

function responseState(status: number): CurriculumGraphRouteState {
  if (status === 400) return { status: "invalid-selection" };
  if (status === 401) return { status: "unauthorized" };
  if (status === 403) return { status: "forbidden" };
  if (status === 404) return { status: "not-found" };
  if (status === 409 || status === 503) return { status: "unavailable" };
  return { status: "unexpected" };
}

async function readGraph(
  client: FinancialAcademyApiClient,
  session: SingleProfileSession,
  signal: AbortSignal,
  selection: CurriculumGraphSelection,
  retryUnauthorized: boolean,
): Promise<CurriculumGraphRouteState> {
  try {
    const result = await client.GET(
      "/api/v1/curriculum/graphs/{curriculum_id}/versions/{curriculum_version}",
      {
        params: {
          path: {
            curriculum_id: selection.curriculumId,
            curriculum_version: selection.curriculumVersion,
          },
        },
        signal,
      },
    );
    if (result.response.status === 200) {
      return result.data && curriculumGraphIsSafe(result.data, selection)
        ? { status: "ready", graph: result.data }
        : { status: "invalid-response" };
    }
    if (result.response.status === 401 && retryUnauthorized) {
      session.invalidate();
      const renewed = await session.ensure(signal);
      if (renewed.status === "error") return sessionFailureState(renewed.kind);
      return readGraph(client, session, signal, selection, false);
    }
    return responseState(result.response.status);
  } catch (error) {
    if (signal.aborted) throw error;
    return { status: "unavailable" };
  }
}

export function createCurriculumGraphLoader(
  client: FinancialAcademyApiClient,
  session: SingleProfileSession,
) {
  return async ({ request, params }: LoaderFunctionArgs) => {
    const selection = parseCurriculumGraphSelection(
      params.curriculumId,
      params.curriculumVersion,
      request.url,
    );
    if (selection === null) return { status: "invalid-selection" } as const;
    const established = await session.ensure(request.signal);
    if (established.status === "error") {
      return sessionFailureState(established.kind);
    }
    return readGraph(client, session, request.signal, selection, true);
  };
}

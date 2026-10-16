import type { LoaderFunctionArgs } from "react-router";

import type { FinancialAcademyApiClient } from "../../generated/api-client";
import type { SingleProfileSession } from "../../platform/auth/singleProfileSession";
import type { PracticeActivityRouteState } from "./model";
import { practicePresentationIsSafe } from "./model";


function sessionFailureState(
  kind: "forbidden" | "unauthorized" | "unavailable" | "unexpected",
): PracticeActivityRouteState {
  return { status: kind };
}

function responseState(
  status: number,
): Exclude<PracticeActivityRouteState, { status: "ready" | "loading" }> {
  if (status === 401) {
    return { status: "unauthorized" };
  }
  if (status === 403) {
    return { status: "forbidden" };
  }
  if (status === 404) {
    return { status: "not-found" };
  }
  if (status === 400) {
    return { status: "invalid-content" };
  }
  if (status === 409 || status === 503) {
    return { status: "unavailable" };
  }
  return { status: "unexpected" };
}

async function readPractice(
  client: FinancialAcademyApiClient,
  session: SingleProfileSession,
  placementId: string,
  signal: AbortSignal,
  retryUnauthorized: boolean,
): Promise<PracticeActivityRouteState> {
  try {
    const result = await client.GET(
      "/api/v1/curriculum/placements/{placement_id}/practice",
      {
        params: { path: { placement_id: placementId } },
        signal,
      },
    );
    if (result.response.status === 200 && result.data) {
      return practicePresentationIsSafe(result.data, placementId)
        ? { status: "ready", practice: result.data }
        : { status: "invalid-content" };
    }
    if (result.response.status === 401 && retryUnauthorized) {
      session.invalidate();
      const renewed = await session.ensure(signal);
      if (renewed.status === "error") {
        return sessionFailureState(renewed.kind);
      }
      return readPractice(client, session, placementId, signal, false);
    }
    return responseState(result.response.status);
  } catch (error) {
    if (signal.aborted) {
      throw error;
    }
    return { status: "unavailable" };
  }
}

export function createPracticeActivityLoader(
  client: FinancialAcademyApiClient,
  session: SingleProfileSession,
) {
  return async ({
    params,
    request,
  }: LoaderFunctionArgs): Promise<PracticeActivityRouteState> => {
    const placementId = params.placementId;
    if (!placementId) {
      return { status: "not-found" };
    }
    const established = await session.ensure(request.signal);
    if (established.status === "error") {
      return sessionFailureState(established.kind);
    }
    return readPractice(
      client,
      session,
      placementId,
      request.signal,
      true,
    );
  };
}

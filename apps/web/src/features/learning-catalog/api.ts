import type { LoaderFunctionArgs } from "react-router";

import type { FinancialAcademyApiClient } from "../../generated/api-client";
import type { SingleProfileSession } from "../../platform/auth/singleProfileSession";
import type { LearningCatalogRouteState } from "./model";
import { learningCatalogIsSafe } from "./model";

function sessionFailureState(
  kind: "forbidden" | "unauthorized" | "unavailable" | "unexpected",
): LearningCatalogRouteState {
  return { status: kind };
}

function responseState(status: number): LearningCatalogRouteState {
  if (status === 401) {
    return { status: "unauthorized" };
  }
  if (status === 403) {
    return { status: "forbidden" };
  }
  if (status === 400) {
    return { status: "invalid-response" };
  }
  if (status === 409 || status === 503) {
    return { status: "unavailable" };
  }
  return { status: "unexpected" };
}

async function readCatalog(
  client: FinancialAcademyApiClient,
  session: SingleProfileSession,
  signal: AbortSignal,
  retryUnauthorized: boolean,
): Promise<LearningCatalogRouteState> {
  try {
    const result = await client.GET(
      "/api/v1/curriculum/opportunities",
      { signal },
    );
    if (result.response.status === 200 && result.data) {
      return learningCatalogIsSafe(result.data)
        ? { status: "ready", catalog: result.data }
        : { status: "invalid-response" };
    }
    if (result.response.status === 401 && retryUnauthorized) {
      session.invalidate();
      const renewed = await session.ensure(signal);
      if (renewed.status === "error") {
        return sessionFailureState(renewed.kind);
      }
      return readCatalog(client, session, signal, false);
    }
    return responseState(result.response.status);
  } catch (error) {
    if (signal.aborted) {
      throw error;
    }
    return { status: "unavailable" };
  }
}

export function createLearningCatalogLoader(
  client: FinancialAcademyApiClient,
  session: SingleProfileSession,
) {
  return async ({ request }: LoaderFunctionArgs) => {
    const established = await session.ensure(request.signal);
    if (established.status === "error") {
      return sessionFailureState(established.kind);
    }
    return readCatalog(client, session, request.signal, true);
  };
}

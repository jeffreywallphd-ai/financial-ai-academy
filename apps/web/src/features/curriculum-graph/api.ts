import type { LoaderFunctionArgs } from "react-router";

import type { FinancialAcademyApiClient } from "../../generated/api-client";
import type { SingleProfileSession } from "../../platform/auth/singleProfileSession";
import type {
  ActivityLaunchResult,
  CurriculumGraph,
  CurriculumGraphRouteState,
  CurriculumGraphSelection,
  NavigationState,
} from "./model";
import {
  activityLaunchIsSafe,
  curriculumGraphIsSafe,
  lessonDestinationWithReturnContext,
  navigationStateIsSafe,
  parseCurriculumGraphSelection,
} from "./model";

function sessionFailureState(
  kind: "forbidden" | "unauthorized" | "unavailable" | "unexpected",
): CurriculumGraphRouteState {
  return { status: kind };
}

function graphResponseState(status: number): CurriculumGraphRouteState {
  if (status === 400) return { status: "invalid-selection" };
  if (status === 401) return { status: "unauthorized" };
  if (status === 403) return { status: "forbidden" };
  if (status === 404) return { status: "not-found" };
  if (status === 409 || status === 503) return { status: "unavailable" };
  return { status: "unexpected" };
}

function navigationResponseState(status: number): CurriculumGraphRouteState {
  if (status === 400) return { status: "invalid-selection" };
  if (status === 401) return { status: "unauthorized" };
  if (status === 403) return { status: "forbidden" };
  if (status === 404 || status === 409 || status === 503) {
    return { status: "unavailable" };
  }
  return { status: "unexpected" };
}

function launchResponseState(
  status: number,
  activityId: string,
): ActivityLaunchResult {
  if (status === 401) return { status: "unauthorized", activityId };
  if (status === 403) return { status: "forbidden", activityId };
  if (status === 404) return { status: "not-found", activityId };
  if (status === 409) return { status: "blocked", activityId };
  if (status === 400) return { status: "invalid", activityId };
  return { status: "unavailable", activityId };
}

async function readCurriculumState(
  client: FinancialAcademyApiClient,
  session: SingleProfileSession,
  signal: AbortSignal,
  selection: CurriculumGraphSelection,
  retryUnauthorized: boolean,
): Promise<CurriculumGraphRouteState> {
  try {
    const graphResult = await client.GET(
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
    if (graphResult.response.status === 401 && retryUnauthorized) {
      session.invalidate();
      const renewed = await session.ensure(signal);
      if (renewed.status === "error") return sessionFailureState(renewed.kind);
      return readCurriculumState(client, session, signal, selection, false);
    }
    if (graphResult.response.status !== 200) {
      return graphResponseState(graphResult.response.status);
    }
    if (!graphResult.data || !curriculumGraphIsSafe(graphResult.data, selection)) {
      return { status: "invalid-response" };
    }

    const navigationResult = await client.GET(
      "/api/v1/adaptation/curricula/{curriculum_id}/versions/{curriculum_version}/navigation-state",
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
    if (navigationResult.response.status === 401 && retryUnauthorized) {
      session.invalidate();
      const renewed = await session.ensure(signal);
      if (renewed.status === "error") return sessionFailureState(renewed.kind);
      return readCurriculumState(client, session, signal, selection, false);
    }
    if (navigationResult.response.status !== 200) {
      return navigationResponseState(navigationResult.response.status);
    }
    return navigationResult.data &&
      navigationStateIsSafe(navigationResult.data, graphResult.data)
      ? {
          status: "ready",
          graph: graphResult.data,
          navigationState: navigationResult.data,
          ...(selection.selectedActivityId !== undefined &&
          graphResult.data.activities.some(
            (activity) =>
              activity.activity_id === selection.selectedActivityId,
          )
            ? { currentActivityId: selection.selectedActivityId }
            : {}),
        }
      : { status: "invalid-response" };
  } catch (error) {
    if (signal.aborted) throw error;
    return { status: "unavailable" };
  }
}

async function launchCurriculumActivity(
  client: FinancialAcademyApiClient,
  session: SingleProfileSession,
  graph: CurriculumGraph,
  navigationState: NavigationState,
  activityId: string,
  signal: AbortSignal,
  retryUnauthorized: boolean,
): Promise<ActivityLaunchResult> {
  try {
    const result = await client.GET(
      "/api/v1/adaptation/curricula/{curriculum_id}/versions/{curriculum_version}/activities/{activity_id}/launch",
      {
        params: {
          path: {
            curriculum_id: graph.curriculum_id,
            curriculum_version: graph.curriculum_version,
            activity_id: activityId,
          },
        },
        signal,
      },
    );
    if (result.response.status === 401 && retryUnauthorized) {
      session.invalidate();
      const renewed = await session.ensure(signal);
      if (renewed.status === "error") {
        return {
          status:
            renewed.kind === "unexpected" ? "unavailable" : renewed.kind,
          activityId,
        };
      }
      return launchCurriculumActivity(
        client,
        session,
        graph,
        navigationState,
        activityId,
        signal,
        false,
      );
    }
    if (result.response.status !== 200) {
      return launchResponseState(result.response.status, activityId);
    }
    return result.data &&
      activityLaunchIsSafe(
        result.data,
        graph,
        navigationState,
        activityId,
      )
      ? {
          status: "ready",
          activityId,
          destination: lessonDestinationWithReturnContext(result.data),
        }
      : { status: "invalid", activityId };
  } catch (error) {
    if (signal.aborted) throw error;
    return { status: "unavailable", activityId };
  }
}

export function createCurriculumActivityLauncher(
  client: FinancialAcademyApiClient,
  session: SingleProfileSession,
) {
  return async (
    graph: CurriculumGraph,
    navigationState: NavigationState,
    activityId: string,
    signal: AbortSignal,
  ): Promise<ActivityLaunchResult> => {
    const established = await session.ensure(signal);
    if (established.status === "error") {
      return {
        status:
          established.kind === "unexpected"
            ? "unavailable"
            : established.kind,
        activityId,
      };
    }
    return launchCurriculumActivity(
      client,
      session,
      graph,
      navigationState,
      activityId,
      signal,
      true,
    );
  };
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
    return readCurriculumState(
      client,
      session,
      request.signal,
      selection,
      true,
    );
  };
}

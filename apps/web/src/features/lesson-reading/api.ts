import type { LoaderFunctionArgs } from "react-router";

import type { FinancialAcademyApiClient } from "../../generated/api-client";
import type { SingleProfileSession } from "../../platform/auth/singleProfileSession";
import type {
  Lesson,
  LessonReturnContext,
  LessonRouteState,
} from "./model";
import { lessonContentIsSafe, parseLessonReturnContext } from "./model";


function sessionFailureState(
  kind: "forbidden" | "unauthorized" | "unavailable" | "unexpected",
): LessonRouteState {
  switch (kind) {
    case "forbidden":
      return { status: "forbidden" };
    case "unauthorized":
      return { status: "unauthorized" };
    case "unavailable":
      return { status: "unavailable" };
    case "unexpected":
      return { status: "unexpected" };
  }
}

function responseState(
  status: number,
  error: unknown,
): Exclude<LessonRouteState, { status: "ready" | "loading" }> {
  const errorCode =
    typeof error === "object" &&
    error !== null &&
    "code" in error &&
    typeof error.code === "string"
      ? error.code
      : "";
  if (status === 401) {
    return { status: "unauthorized" };
  }
  if (status === 403) {
    return { status: "forbidden" };
  }
  if (status === 404) {
    return { status: "not-found" };
  }
  if (
    errorCode === "invalid_package" ||
    errorCode === "integrity_failure"
  ) {
    return { status: "invalid-content" };
  }
  if (status === 409 || status === 503) {
    return { status: "unavailable" };
  }
  if (status === 400) {
    return { status: "invalid-content" };
  }
  return { status: "unexpected" };
}

async function readLesson(
  client: FinancialAcademyApiClient,
  session: SingleProfileSession,
  placementId: string,
  returnContext: LessonReturnContext | null,
  signal: AbortSignal,
  retryUnauthorized: boolean,
): Promise<LessonRouteState> {
  try {
    const result = await client.GET(
      "/api/v1/curriculum/placements/{placement_id}/lesson",
      {
        params: {
          path: {
            placement_id: placementId,
          },
        },
        signal,
      },
    );
    if (result.response.status === 200 && result.data) {
      const lesson = result.data as Lesson;
      return lessonContentIsSafe(lesson)
        ? { status: "ready", lesson, returnContext }
        : { status: "invalid-content" };
    }
    if (result.response.status === 401 && retryUnauthorized) {
      session.invalidate();
      const renewed = await session.ensure(signal);
      if (renewed.status === "error") {
        return sessionFailureState(renewed.kind);
      }
      return readLesson(
        client,
        session,
        placementId,
        returnContext,
        signal,
        false,
      );
    }
    return responseState(result.response.status, result.error);
  } catch (error) {
    if (signal.aborted) {
      throw error;
    }
    return { status: "unavailable" };
  }
}

export function createLessonLoader(
  client: FinancialAcademyApiClient,
  session: SingleProfileSession,
) {
  return async ({
    params,
    request,
  }: LoaderFunctionArgs): Promise<LessonRouteState> => {
    const placementId = params.placementId;
    if (!placementId) {
      return { status: "not-found" };
    }
    const established = await session.ensure(request.signal);
    if (established.status === "error") {
      return sessionFailureState(established.kind);
    }
    return readLesson(
      client,
      session,
      placementId,
      parseLessonReturnContext(request.url),
      request.signal,
      true,
    );
  };
}

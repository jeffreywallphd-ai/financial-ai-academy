import type { LoaderFunctionArgs } from "react-router";

import type { FinancialAcademyApiClient } from "../../generated/api-client";
import type { SingleProfileSession } from "../../platform/auth/singleProfileSession";
import type { PracticeActivityRouteState } from "./model";
import type {
  PracticePresentation,
  PracticeSubmissionOutcome,
  PracticeSubmitter,
  PreparedPracticeSubmission,
} from "./model";
import {
  practicePresentationIsSafe,
  practiceSubmissionResultIsSafe,
} from "./model";


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

function publicErrorCode(value: unknown): string | null {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    return null;
  }
  const code = (value as Record<string, unknown>).code;
  return typeof code === "string" ? code : null;
}

function submissionFailure(
  status: number,
  error: unknown,
): PracticeSubmissionOutcome {
  const code = publicErrorCode(error);
  if (status === 400) {
    return { status: "invalid-request" };
  }
  if (status === 401) {
    return { status: "unauthorized" };
  }
  if (status === 403) {
    return { status: "forbidden" };
  }
  if (status === 404) {
    return { status: "not-found" };
  }
  if (status === 409) {
    if (code === "already_completed") {
      return { status: "already-completed" };
    }
    if (code === "conflict") {
      return { status: "conflict" };
    }
    return { status: "stale" };
  }
  if (status === 503) {
    return { status: "unavailable" };
  }
  return { status: "unexpected" };
}

async function submitPractice(
  client: FinancialAcademyApiClient,
  session: SingleProfileSession,
  practice: PracticePresentation,
  submission: PreparedPracticeSubmission,
  signal: AbortSignal | undefined,
  retryUnauthorized: boolean,
): Promise<PracticeSubmissionOutcome> {
  try {
    const options = signal
      ? {
          body: submission.body,
          params: { path: { placement_id: submission.placementId } },
          signal,
        }
      : {
          body: submission.body,
          params: { path: { placement_id: submission.placementId } },
        };
    const response = await client.POST(
      "/api/v1/curriculum/placements/{placement_id}/practice/submissions",
      options,
    );
    if (response.response.status === 200 && response.data) {
      return practiceSubmissionResultIsSafe(
        response.data,
        practice,
        submission,
      )
        ? { status: "result", result: response.data }
        : { status: "invalid-result" };
    }
    if (response.response.status === 401 && retryUnauthorized) {
      session.invalidate();
      const renewed = await session.ensure(signal);
      if (renewed.status === "error") {
        return { status: renewed.kind };
      }
      return submitPractice(
        client,
        session,
        practice,
        submission,
        signal,
        false,
      );
    }
    return submissionFailure(response.response.status, response.error);
  } catch (error) {
    if (signal?.aborted) {
      throw error;
    }
    return { status: "unavailable" };
  }
}

export function createPracticeActivitySubmitter(
  client: FinancialAcademyApiClient,
  session: SingleProfileSession,
): PracticeSubmitter {
  return async (practice, submission, signal) => {
    const established = await session.ensure(signal);
    if (established.status === "error") {
      return { status: established.kind };
    }
    return submitPractice(
      client,
      session,
      practice,
      submission,
      signal,
      true,
    );
  };
}

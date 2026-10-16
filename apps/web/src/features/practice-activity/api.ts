import type { LoaderFunctionArgs } from "react-router";

import type { FinancialAcademyApiClient } from "../../generated/api-client";
import type { SingleProfileSession } from "../../platform/auth/singleProfileSession";
import type { PracticeActivityRouteState } from "./model";
import type {
  PracticeDraftSaveOutcome,
  PracticeDraftSaver,
  PracticePresentation,
  PracticeProgressOutcome,
  PracticeProgressReader,
  PracticeSubmissionOutcome,
  PracticeSubmitter,
  PreparedPracticeDraftSave,
  PreparedPracticeSubmission,
} from "./model";
import {
  practiceDraftIsSafe,
  practicePresentationIsSafe,
  practiceProgressIsSafe,
  practiceSubmissionResultIsSafe,
} from "./model";

type PracticeOpeningState =
  | { status: "ready"; practice: PracticePresentation }
  | Exclude<PracticeActivityRouteState, { status: "ready" }>;

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
): Promise<PracticeOpeningState> {
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
    const opened = await readPractice(
      client,
      session,
      placementId,
      request.signal,
      true,
    );
    if (opened.status !== "ready") {
      return opened;
    }
    const progress = await readProgress(
      client,
      session,
      opened.practice,
      request.signal,
      true,
    );
    if (progress.status === "progress") {
      return {
        status: "ready",
        practice: opened.practice,
        progress: progress.progress,
      };
    }
    return progress.status === "invalid-result"
      ? { status: "invalid-content" }
      : progress;
  };
}

async function readProgress(
  client: FinancialAcademyApiClient,
  session: SingleProfileSession,
  practice: PracticePresentation,
  signal: AbortSignal | undefined,
  retryUnauthorized: boolean,
): Promise<PracticeProgressOutcome> {
  try {
    const options = signal
      ? {
          params: { path: { placement_id: practice.placement_id } },
          signal,
        }
      : { params: { path: { placement_id: practice.placement_id } } };
    const response = await client.GET(
      "/api/v1/curriculum/placements/{placement_id}/practice/progress",
      options,
    );
    if (response.response.status === 200 && response.data) {
      return practiceProgressIsSafe(response.data, practice)
        ? { status: "progress", progress: response.data }
        : { status: "invalid-result" };
    }
    if (response.response.status === 401 && retryUnauthorized) {
      session.invalidate();
      const renewed = await session.ensure(signal);
      if (renewed.status === "error") {
        return { status: renewed.kind };
      }
      return readProgress(client, session, practice, signal, false);
    }
    if (response.response.status === 401) {
      return { status: "unauthorized" };
    }
    if (response.response.status === 403) {
      return { status: "forbidden" };
    }
    if (response.response.status === 404) {
      return { status: "not-found" };
    }
    if (response.response.status === 409 || response.response.status === 503) {
      return { status: "unavailable" };
    }
    return { status: "unexpected" };
  } catch (error) {
    if (signal?.aborted) {
      throw error;
    }
    return { status: "unavailable" };
  }
}

export function createPracticeProgressReader(
  client: FinancialAcademyApiClient,
  session: SingleProfileSession,
): PracticeProgressReader {
  return async (practice, signal) => {
    const established = await session.ensure(signal);
    if (established.status === "error") {
      return { status: established.kind };
    }
    return readProgress(client, session, practice, signal, true);
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
    if (code === "attempt_limit_reached") {
      return { status: "attempt-limit" };
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

function draftFailure(status: number): PracticeDraftSaveOutcome {
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
    return { status: "conflict" };
  }
  if (status === 503) {
    return { status: "unavailable" };
  }
  return { status: "unexpected" };
}

async function saveDraft(
  client: FinancialAcademyApiClient,
  session: SingleProfileSession,
  practice: PracticePresentation,
  save: PreparedPracticeDraftSave,
  signal: AbortSignal | undefined,
  retryUnauthorized: boolean,
): Promise<PracticeDraftSaveOutcome> {
  try {
    const options = signal
      ? {
          body: save.body,
          params: { path: { placement_id: save.placementId } },
          signal,
        }
      : {
          body: save.body,
          params: { path: { placement_id: save.placementId } },
        };
    const response = await client.PUT(
      "/api/v1/curriculum/placements/{placement_id}/practice/draft",
      options,
    );
    if (response.response.status === 200 && response.data) {
      return practiceDraftIsSafe(response.data, practice)
        ? { status: "saved", draft: response.data }
        : { status: "invalid-result" };
    }
    if (response.response.status === 401 && retryUnauthorized) {
      session.invalidate();
      const renewed = await session.ensure(signal);
      if (renewed.status === "error") {
        return { status: renewed.kind };
      }
      return saveDraft(client, session, practice, save, signal, false);
    }
    return draftFailure(response.response.status);
  } catch (error) {
    if (signal?.aborted) {
      throw error;
    }
    return { status: "unavailable" };
  }
}

export function createPracticeDraftSaver(
  client: FinancialAcademyApiClient,
  session: SingleProfileSession,
): PracticeDraftSaver {
  return async (practice, save, signal) => {
    const established = await session.ensure(signal);
    if (established.status === "error") {
      return { status: established.kind };
    }
    return saveDraft(client, session, practice, save, signal, true);
  };
}

import type { LoaderFunctionArgs } from "react-router";

import type { FinancialAcademyApiClient } from "../../generated/api-client";
import type { SingleProfileSession } from "../../platform/auth/singleProfileSession";
import {
  platformHelpSearchHref,
  platformHelpSearchPageIsSafe,
  platformHelpTextIsSafe,
  platformHelpTopicIsSafe,
  type PlatformHelpSearchParameters,
  type PlatformHelpSearchRouteState,
  type PlatformHelpSearchSelection,
  type PlatformHelpTopicRouteState,
  type PlatformHelpTopicSelection,
} from "./model";

const SEARCH_PARAMETERS = new Set([
  "query",
  "topic_kind",
  "page_size",
  "cursor",
]);
const TOPIC_KINDS = new Set([
  "glossary",
  "help",
  "method",
  "limitation",
  "troubleshooting",
]);
const IDENTIFIER = /^[a-z0-9][a-z0-9._-]{2,63}$/;
const VERSION = /^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$/;
const CURSOR = /^[A-Za-z0-9_-]{1,4096}$/;

function oneParameter(
  parameters: URLSearchParams,
  name: string,
  maximum: number,
): string | undefined | null {
  const values = parameters.getAll(name);
  if (values.length === 0) return undefined;
  const value = values[0];
  if (
    values.length !== 1 ||
    value === undefined ||
    !platformHelpTextIsSafe(value, 0, maximum)
  ) {
    return null;
  }
  return value;
}

export function parsePlatformHelpSearch(
  url: string,
): PlatformHelpSearchSelection | null {
  let request: URL;
  try {
    request = new URL(url);
  } catch {
    return null;
  }
  if ([...request.searchParams.keys()].some((key) => !SEARCH_PARAMETERS.has(key))) {
    return null;
  }
  const query = oneParameter(request.searchParams, "query", 200);
  const topicKindValue = oneParameter(request.searchParams, "topic_kind", 32);
  const pageSizeText = oneParameter(request.searchParams, "page_size", 2);
  const cursor = oneParameter(request.searchParams, "cursor", 4096);
  if (
    query === null ||
    topicKindValue === null ||
    pageSizeText === null ||
    cursor === null ||
    (topicKindValue !== undefined &&
      topicKindValue !== "" &&
      !TOPIC_KINDS.has(topicKindValue)) ||
    (cursor !== undefined && (cursor === "" || !CURSOR.test(cursor)))
  ) {
    return null;
  }
  const topicKind = topicKindValue === "" ? undefined : topicKindValue;
  let pageSize = 20;
  if (pageSizeText !== undefined) {
    if (!/^[1-9][0-9]?$/.test(pageSizeText)) return null;
    pageSize = Number(pageSizeText);
    if (pageSize > 50) return null;
  }
  const parameters: PlatformHelpSearchParameters = {
    query: query ?? "",
    page_size: pageSize,
    ...(topicKind === undefined
      ? {}
      : {
          topic_kind: topicKind as NonNullable<
            PlatformHelpSearchParameters["topic_kind"]
          >,
        }),
    ...(cursor === undefined ? {} : { cursor }),
  };
  return { parameters, href: platformHelpSearchHref(parameters) };
}

function parseReturnTo(request: URL): string | null {
  const values = request.searchParams.getAll("return_to");
  if (values.length === 0) return "/help";
  const raw = values[0];
  if (values.length !== 1 || raw === undefined || raw.length > 4096) return null;
  let candidate: URL;
  try {
    candidate = new URL(raw, request.origin);
  } catch {
    return null;
  }
  if (
    candidate.origin !== request.origin ||
    candidate.pathname !== "/help" ||
    candidate.username !== "" ||
    candidate.password !== "" ||
    candidate.hash !== ""
  ) {
    return null;
  }
  const parsed = parsePlatformHelpSearch(candidate.toString());
  return parsed?.href ?? null;
}

export function parsePlatformHelpTopicSelection(
  topicId: unknown,
  topicVersion: unknown,
  url: string,
): PlatformHelpTopicSelection | null {
  let request: URL;
  try {
    request = new URL(url);
  } catch {
    return null;
  }
  if (
    typeof topicId !== "string" ||
    !IDENTIFIER.test(topicId) ||
    typeof topicVersion !== "string" ||
    !VERSION.test(topicVersion) ||
    [...request.searchParams.keys()].some((key) => key !== "return_to")
  ) {
    return null;
  }
  const returnTo = parseReturnTo(request);
  return returnTo === null ? null : { topicId, topicVersion, returnTo };
}

function sessionFailure(
  kind: "forbidden" | "unauthorized" | "unavailable" | "unexpected",
): { status: typeof kind } {
  return { status: kind };
}

function searchFailure(status: number): PlatformHelpSearchRouteState {
  if (status === 401) return { status: "unauthorized" };
  if (status === 403) return { status: "forbidden" };
  if (status === 400) return { status: "invalid-query" };
  if (status === 409) return { status: "stale-cursor" };
  if (status === 503) return { status: "unavailable" };
  return { status: "unexpected" };
}

function topicFailure(status: number): PlatformHelpTopicRouteState {
  if (status === 401) return { status: "unauthorized" };
  if (status === 403) return { status: "forbidden" };
  if (status === 400) return { status: "invalid-selection" };
  if (status === 404) return { status: "not-found" };
  if (status === 409 || status === 503) return { status: "unavailable" };
  return { status: "unexpected" };
}

async function readSearch(
  client: FinancialAcademyApiClient,
  session: SingleProfileSession,
  signal: AbortSignal,
  selection: PlatformHelpSearchSelection,
  retryUnauthorized: boolean,
): Promise<PlatformHelpSearchRouteState> {
  try {
    const result = await client.GET("/api/v1/guidance/platform-help", {
      params: { query: selection.parameters },
      signal,
    });
    if (result.response.status === 200 && result.data) {
      return platformHelpSearchPageIsSafe(result.data, selection.parameters)
        ? { status: "ready", page: result.data, selection }
        : { status: "invalid-response" };
    }
    if (result.response.status === 401 && retryUnauthorized) {
      session.invalidate();
      const renewed = await session.ensure(signal);
      if (renewed.status === "error") return sessionFailure(renewed.kind);
      return readSearch(client, session, signal, selection, false);
    }
    return searchFailure(result.response.status);
  } catch (error) {
    if (signal.aborted) throw error;
    return { status: "unavailable" };
  }
}

export function createPlatformHelpSearchLoader(
  client: FinancialAcademyApiClient,
  session: SingleProfileSession,
) {
  return async ({ request }: LoaderFunctionArgs) => {
    const selection = parsePlatformHelpSearch(request.url);
    if (selection === null) return { status: "invalid-query" } as const;
    const established = await session.ensure(request.signal);
    if (established.status === "error") return sessionFailure(established.kind);
    return readSearch(client, session, request.signal, selection, true);
  };
}

async function readTopic(
  client: FinancialAcademyApiClient,
  session: SingleProfileSession,
  signal: AbortSignal,
  selection: PlatformHelpTopicSelection,
  retryUnauthorized: boolean,
): Promise<PlatformHelpTopicRouteState> {
  try {
    const result = await client.GET(
      "/api/v1/guidance/platform-help/{topic_id}/versions/{topic_version}",
      {
        params: {
          path: {
            topic_id: selection.topicId,
            topic_version: selection.topicVersion,
          },
        },
        signal,
      },
    );
    if (result.response.status === 200 && result.data) {
      return platformHelpTopicIsSafe(
        result.data,
        selection.topicId,
        selection.topicVersion,
      )
        ? { status: "ready", topic: result.data, selection }
        : { status: "invalid-response" };
    }
    if (result.response.status === 401 && retryUnauthorized) {
      session.invalidate();
      const renewed = await session.ensure(signal);
      if (renewed.status === "error") return sessionFailure(renewed.kind);
      return readTopic(client, session, signal, selection, false);
    }
    return topicFailure(result.response.status);
  } catch (error) {
    if (signal.aborted) throw error;
    return { status: "unavailable" };
  }
}

export function createPlatformHelpTopicLoader(
  client: FinancialAcademyApiClient,
  session: SingleProfileSession,
) {
  return async ({ request, params }: LoaderFunctionArgs) => {
    const selection = parsePlatformHelpTopicSelection(
      params.topicId,
      params.topicVersion,
      request.url,
    );
    if (selection === null) return { status: "invalid-selection" } as const;
    const established = await session.ensure(request.signal);
    if (established.status === "error") return sessionFailure(established.kind);
    return readTopic(client, session, request.signal, selection, true);
  };
}

import type { LoaderFunctionArgs } from "react-router";

import type { FinancialAcademyApiClient } from "../../generated/api-client";
import type { SingleProfileSession } from "../../platform/auth/singleProfileSession";
import {
  contextualHelpIsSafe,
  platformHelpSearchHref,
  platformHelpSearchPageIsSafe,
  platformHelpTextIsSafe,
  platformHelpTopicIsSafe,
  type ContextualHelpReader,
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
const CONTENT_VERSION =
  /^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?$/;
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

function exactFeatureReturn(
  candidate: URL,
): { href: string; label: string } | null {
  if (
    candidate.username !== "" ||
    candidate.password !== "" ||
    candidate.hash !== ""
  ) {
    return null;
  }
  if (candidate.pathname === "/preferences/assistance") {
    return candidate.search === ""
      ? { href: candidate.pathname, label: "Return to AI help choices" }
      : null;
  }
  const project = /^\/projects\/([a-z0-9][a-z0-9._-]{2,63})$/.exec(
    candidate.pathname,
  );
  if (project) {
    return candidate.search === ""
      ? { href: candidate.pathname, label: "Return to Project" }
      : null;
  }
  const practice =
    /^\/learn\/placements\/([a-z0-9][a-z0-9._-]{2,63})\/practice$/.exec(
      candidate.pathname,
    );
  if (practice) {
    return candidate.search === ""
      ? { href: candidate.pathname, label: "Return to practice" }
      : null;
  }
  const lesson =
    /^\/learn\/placements\/([a-z0-9][a-z0-9._-]{2,63})$/.exec(
      candidate.pathname,
    );
  if (!lesson) return null;
  if (candidate.search === "") {
    return { href: candidate.pathname, label: "Return to lesson" };
  }
  const keys = [...candidate.searchParams.keys()].sort();
  const expected = ["activity_id", "curriculum_id", "curriculum_version"];
  if (
    keys.length !== expected.length ||
    keys.some((key, index) => key !== expected[index]) ||
    expected.some((key) => candidate.searchParams.getAll(key).length !== 1)
  ) {
    return null;
  }
  const activity = candidate.searchParams.get("activity_id");
  const curriculum = candidate.searchParams.get("curriculum_id");
  const version = candidate.searchParams.get("curriculum_version");
  return activity &&
    IDENTIFIER.test(activity) &&
    curriculum &&
    IDENTIFIER.test(curriculum) &&
    version &&
    CONTENT_VERSION.test(version)
    ? {
        href: `${candidate.pathname}?${candidate.searchParams.toString()}`,
        label: "Return to lesson",
      }
    : null;
}

function parseReturnTo(
  request: URL,
): { href: string; label: string } | null {
  const values = request.searchParams.getAll("return_to");
  if (values.length === 0) {
    return { href: "/help", label: "Return to platform guide" };
  }
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
    candidate.username !== "" ||
    candidate.password !== "" ||
    candidate.hash !== ""
  ) {
    return null;
  }
  if (candidate.pathname === "/help") {
    const parsed = parsePlatformHelpSearch(candidate.toString());
    return parsed
      ? { href: parsed.href, label: "Return to platform guide" }
      : null;
  }
  return exactFeatureReturn(candidate);
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
  const returnTarget = parseReturnTo(request);
  return returnTarget === null
    ? null
    : {
        topicId,
        topicVersion,
        returnTo: returnTarget.href,
        returnLabel: returnTarget.label,
      };
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

async function readContextualHelp(
  client: FinancialAcademyApiClient,
  session: SingleProfileSession,
  contextKey: string,
  contextVersion: string,
  signal: AbortSignal,
  retryUnauthorized: boolean,
) {
  if (!IDENTIFIER.test(contextKey) || !VERSION.test(contextVersion)) {
    return { status: "unavailable" } as const;
  }
  try {
    const result = await client.GET(
      "/api/v1/guidance/contextual-help/{context_key}/versions/{context_version}",
      {
        params: {
          path: {
            context_key: contextKey,
            context_version: contextVersion,
          },
        },
        signal,
      },
    );
    if (result.response.status === 200 && result.data) {
      return contextualHelpIsSafe(result.data, contextKey, contextVersion)
        ? ({ status: "ready", context: result.data } as const)
        : ({ status: "unavailable" } as const);
    }
    if (result.response.status === 401 && retryUnauthorized) {
      session.invalidate();
      const renewed = await session.ensure(signal);
      if (renewed.status === "ready") {
        return readContextualHelp(
          client,
          session,
          contextKey,
          contextVersion,
          signal,
          false,
        );
      }
    }
    return { status: "unavailable" } as const;
  } catch (error) {
    if (signal.aborted) throw error;
    return { status: "unavailable" } as const;
  }
}

export function createContextualHelpReader(
  client: FinancialAcademyApiClient,
  session: SingleProfileSession,
): ContextualHelpReader {
  return (contextKey, contextVersion, signal) =>
    readContextualHelp(
      client,
      session,
      contextKey,
      contextVersion,
      signal,
      true,
    );
}

import type { LoaderFunctionArgs } from "react-router";

import type { FinancialAcademyApiClient } from "../../generated/api-client";
import type { SingleProfileSession } from "../../platform/auth/singleProfileSession";
import type {
  LearningCatalogQueryPage,
  LearningCatalogQueryParameters,
  LearningCatalogRouteState,
} from "./model";
import { learningCatalogQueryPageIsSafe } from "./model";

const KNOWN_PARAMETERS = new Set([
  "query",
  "prerequisite_query",
  "topic",
  "level",
  "kind",
  "availability",
  "minimum_minutes",
  "maximum_minutes",
  "sort",
  "page_size",
  "cursor",
]);
const TOPIC = /^[a-z0-9][a-z0-9-]{1,49}$/;
const CURSOR = /^[A-Za-z0-9_-]+\.[a-f0-9]{64}$/;

function sessionFailureState(
  kind: "forbidden" | "unauthorized" | "unavailable" | "unexpected",
): LearningCatalogRouteState {
  return { status: kind };
}

function errorCode(value: unknown): string | null {
  return typeof value === "object" && value !== null && "code" in value
    ? String((value as { code: unknown }).code)
    : null;
}

function responseState(
  status: number,
  error: unknown,
): LearningCatalogRouteState {
  if (status === 401) return { status: "unauthorized" };
  if (status === 403) return { status: "forbidden" };
  if (status === 400) return { status: "invalid-query" };
  if (status === 409 && errorCode(error) === "stale_cursor") {
    return { status: "stale-cursor" };
  }
  if (status === 409 || status === 503) return { status: "unavailable" };
  return { status: "unexpected" };
}

function oneText(
  parameters: URLSearchParams,
  name: string,
  maximum = 100,
): string | undefined | null {
  const values = parameters.getAll(name).filter((value) => value !== "");
  const value = values[0];
  if (values.length === 0) return undefined;
  if (
    values.length !== 1 ||
    value === undefined ||
    value.length > maximum ||
    /[\0\r\n]/.test(value)
  ) {
    return null;
  }
  return value;
}

function repeated(
  parameters: URLSearchParams,
  name: string,
  allowed: (value: string) => boolean,
): string[] | null {
  const values = parameters.getAll(name).filter((value) => value !== "");
  return values.length <= 8 && values.every(allowed) ? values : null;
}

function boundedInteger(
  parameters: URLSearchParams,
  name: string,
  maximum: number,
): number | undefined | null {
  const value = oneText(parameters, name);
  if (value === null) return null;
  if (value === undefined) return undefined;
  if (!/^[1-9][0-9]*$/.test(value)) return null;
  const parsed = Number(value);
  return parsed <= maximum ? parsed : null;
}

export function parseLearningCatalogQuery(
  url: string,
): LearningCatalogQueryParameters | null {
  const parameters = new URL(url).searchParams;
  if ([...parameters.keys()].some((name) => !KNOWN_PARAMETERS.has(name)))
    return null;
  const query = oneText(parameters, "query");
  const prerequisite = oneText(parameters, "prerequisite_query");
  const topics = repeated(parameters, "topic", (value) => TOPIC.test(value));
  const levels = repeated(parameters, "level", (value) =>
    ["introductory", "intermediate", "advanced"].includes(value),
  );
  const kinds = repeated(parameters, "kind", (value) =>
    ["course", "lesson", "lab", "project"].includes(value),
  );
  const availabilities = repeated(parameters, "availability", (value) =>
    ["available", "unavailable", "planned"].includes(value),
  );
  const minimum = boundedInteger(parameters, "minimum_minutes", 1440);
  const maximum = boundedInteger(parameters, "maximum_minutes", 1440);
  const pageSize = boundedInteger(parameters, "page_size", 50);
  const sort = oneText(parameters, "sort");
  const cursor = oneText(parameters, "cursor", 1024);
  if (
    query === null ||
    prerequisite === null ||
    topics === null ||
    levels === null ||
    kinds === null ||
    availabilities === null ||
    minimum === null ||
    maximum === null ||
    pageSize === null ||
    sort === null ||
    cursor === null ||
    (minimum !== undefined && maximum !== undefined && minimum > maximum) ||
    (sort !== undefined &&
      ![
        "catalog",
        "title",
        "duration_ascending",
        "duration_descending",
      ].includes(sort)) ||
    (cursor !== undefined && !CURSOR.test(cursor))
  )
    return null;
  return {
    ...(query === undefined ? {} : { query }),
    ...(prerequisite === undefined ? {} : { prerequisite_query: prerequisite }),
    ...(topics.length === 0 ? {} : { topic: topics }),
    ...(levels.length === 0
      ? {}
      : { level: levels as ("introductory" | "intermediate" | "advanced")[] }),
    ...(kinds.length === 0
      ? {}
      : { kind: kinds as ("course" | "lesson" | "lab" | "project")[] }),
    ...(availabilities.length === 0
      ? {}
      : {
          availability: availabilities as (
            "available" | "unavailable" | "planned"
          )[],
        }),
    ...(minimum === undefined ? {} : { minimum_minutes: minimum }),
    ...(maximum === undefined ? {} : { maximum_minutes: maximum }),
    ...(sort === undefined
      ? {}
      : {
          sort: sort as
            "catalog" | "title" | "duration_ascending" | "duration_descending",
        }),
    ...(pageSize === undefined ? {} : { page_size: pageSize }),
    ...(cursor === undefined ? {} : { cursor }),
  };
}

async function readCatalog(
  client: FinancialAcademyApiClient,
  session: SingleProfileSession,
  signal: AbortSignal,
  query: LearningCatalogQueryParameters,
  retryUnauthorized: boolean,
): Promise<LearningCatalogRouteState> {
  try {
    const result = await client.GET("/api/v1/curriculum/opportunities/query", {
      params: { query },
      signal,
    });
    if (result.response.status === 200 && result.data) {
      return (await learningCatalogQueryPageIsSafe(result.data))
        ? { status: "ready", page: result.data as LearningCatalogQueryPage }
        : { status: "invalid-response" };
    }
    if (result.response.status === 401 && retryUnauthorized) {
      session.invalidate();
      const renewed = await session.ensure(signal);
      if (renewed.status === "error") return sessionFailureState(renewed.kind);
      return readCatalog(client, session, signal, query, false);
    }
    return responseState(result.response.status, result.error);
  } catch (error) {
    if (signal.aborted) throw error;
    return { status: "unavailable" };
  }
}

export function createLearningCatalogLoader(
  client: FinancialAcademyApiClient,
  session: SingleProfileSession,
) {
  return async ({ request }: LoaderFunctionArgs) => {
    const query = parseLearningCatalogQuery(request.url);
    if (query === null) return { status: "invalid-query" } as const;
    const established = await session.ensure(request.signal);
    if (established.status === "error")
      return sessionFailureState(established.kind);
    return readCatalog(client, session, request.signal, query, true);
  };
}

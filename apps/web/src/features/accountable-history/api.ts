import type { FinancialAcademyApiClient } from "../../generated/api-client";
import type { SingleProfileSession } from "../../platform/auth/singleProfileSession";
import {
  accountableHistoryDocumentIsSafe,
  portableEvidenceExportIsSafe,
  type AccountableHistoryExportOutcome,
  type AccountableHistoryReadOutcome,
  type AccountableHistoryRequest,
  type PortableEvidenceExport,
} from "./model";

export type AccountableHistoryReader = (
  request: AccountableHistoryRequest,
  signal: AbortSignal,
) => Promise<AccountableHistoryReadOutcome>;

export type AccountableHistoryExporter = (
  request: AccountableHistoryRequest,
  signal: AbortSignal,
) => Promise<AccountableHistoryExportOutcome>;

function failure(
  status: number,
): Exclude<AccountableHistoryReadOutcome, { status: "ready" }> {
  if (status === 401) return { status: "unauthorized" };
  if (status === 403) return { status: "forbidden" };
  return { status: "unavailable" };
}

async function read(
  client: FinancialAcademyApiClient,
  session: SingleProfileSession,
  request: AccountableHistoryRequest,
  signal: AbortSignal,
  retryUnauthorized: boolean,
): Promise<AccountableHistoryReadOutcome> {
  try {
    const result = await client.POST("/api/v1/audit/accountable-history", {
      body: request,
      signal,
    });
    if (result.response.status === 200 && result.data) {
      return accountableHistoryDocumentIsSafe(result.data, request)
        ? { status: "ready", document: result.data }
        : { status: "invalid-response" };
    }
    if (result.response.status === 401 && retryUnauthorized) {
      session.invalidate();
      const renewed = await session.ensure(signal);
      if (renewed.status === "error")
        return failure(
          renewed.kind === "forbidden"
            ? 403
            : renewed.kind === "unauthorized"
              ? 401
              : 503,
        );
      return read(client, session, request, signal, false);
    }
    return failure(result.response.status);
  } catch (error) {
    if (signal.aborted) throw error;
    return { status: "unavailable" };
  }
}

async function exportRecord(
  client: FinancialAcademyApiClient,
  session: SingleProfileSession,
  request: AccountableHistoryRequest,
  signal: AbortSignal,
  retryUnauthorized: boolean,
): Promise<AccountableHistoryExportOutcome> {
  try {
    const result = await client.POST(
      "/api/v1/audit/accountable-history/export",
      { body: request, signal },
    );
    if (result.response.status === 200 && result.data) {
      const record = result.data as PortableEvidenceExport;
      return portableEvidenceExportIsSafe(record, request)
        ? { status: "ready", record }
        : { status: "invalid-response" };
    }
    if (result.response.status === 401 && retryUnauthorized) {
      session.invalidate();
      const renewed = await session.ensure(signal);
      if (renewed.status === "error")
        return failure(
          renewed.kind === "forbidden"
            ? 403
            : renewed.kind === "unauthorized"
              ? 401
              : 503,
        );
      return exportRecord(client, session, request, signal, false);
    }
    return failure(result.response.status);
  } catch (error) {
    if (signal.aborted) throw error;
    return { status: "unavailable" };
  }
}

export function createAccountableHistoryReader(
  client: FinancialAcademyApiClient,
  session: SingleProfileSession,
): AccountableHistoryReader {
  return (request, signal) => read(client, session, request, signal, true);
}

export function createAccountableHistoryExporter(
  client: FinancialAcademyApiClient,
  session: SingleProfileSession,
): AccountableHistoryExporter {
  return (request, signal) =>
    exportRecord(client, session, request, signal, true);
}

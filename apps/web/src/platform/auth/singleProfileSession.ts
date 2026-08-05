import type { FinancialAcademyApiClient } from "../../generated/api-client";


export type SessionFailureKind =
  | "forbidden"
  | "unauthorized"
  | "unavailable"
  | "unexpected";

export type SessionResult =
  | { status: "ready" }
  | { status: "error"; kind: SessionFailureKind };

export class SingleProfileSession {
  private current: "ready" | "unknown" = "unknown";
  private pending: Promise<SessionResult> | null = null;

  constructor(private readonly client: FinancialAcademyApiClient) {}

  ensure(signal?: AbortSignal): Promise<SessionResult> {
    if (this.current === "ready") {
      return Promise.resolve({ status: "ready" });
    }
    if (!this.pending) {
      this.pending = this.bootstrap(signal).finally(() => {
        this.pending = null;
      });
    }
    return this.pending;
  }

  invalidate() {
    this.current = "unknown";
  }

  private async bootstrap(signal?: AbortSignal): Promise<SessionResult> {
    try {
      const options = signal
        ? {
            body: { limitation_acknowledged: true as const },
            signal,
          }
        : {
            body: { limitation_acknowledged: true as const },
          };
      const result = await this.client.POST(
        "/api/v1/session/single-profile",
        options,
      );
      if (result.response.status === 201 && result.data) {
        this.current = "ready";
        return { status: "ready" };
      }
      if (result.response.status === 401) {
        return { status: "error", kind: "unauthorized" };
      }
      if (result.response.status === 403) {
        return { status: "error", kind: "forbidden" };
      }
      if (
        result.response.status === 409 ||
        result.response.status === 503
      ) {
        return { status: "error", kind: "unavailable" };
      }
      return { status: "error", kind: "unexpected" };
    } catch {
      return { status: "error", kind: "unavailable" };
    }
  }
}

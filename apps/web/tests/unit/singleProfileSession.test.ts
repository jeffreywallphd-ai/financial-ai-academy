import { describe, expect, it, vi } from "vitest";

import type { FinancialAcademyApiClient } from "../../src/generated/api-client";
import { SingleProfileSession } from "../../src/platform/auth/singleProfileSession";


function apiClientWith(post: ReturnType<typeof vi.fn>) {
  return { POST: post } as unknown as FinancialAcademyApiClient;
}

describe("SingleProfileSession", () => {
  it("coalesces bootstrap and reuses only in-memory readiness", async () => {
    const post = vi.fn().mockResolvedValue({
      data: {
        status: "ready",
        authentication_method: "single_profile",
        expires_at: "2026-08-05T12:00:00Z",
      },
      response: new Response(null, { status: 201 }),
    });
    const session = new SingleProfileSession(apiClientWith(post));

    const [first, second] = await Promise.all([
      session.ensure(),
      session.ensure(),
    ]);
    const third = await session.ensure();

    expect(first).toEqual({ status: "ready" });
    expect(second).toEqual({ status: "ready" });
    expect(third).toEqual({ status: "ready" });
    expect(post).toHaveBeenCalledTimes(1);
    expect(post.mock.calls[0]?.[1]).toEqual({
      body: { limitation_acknowledged: true },
    });
  });

  it("maps bounded denials and permits one later retry", async () => {
    const post = vi
      .fn()
      .mockResolvedValueOnce({
        error: { code: "forbidden" },
        response: new Response(null, { status: 403 }),
      })
      .mockResolvedValueOnce({
        data: { status: "ready" },
        response: new Response(null, { status: 201 }),
      });
    const session = new SingleProfileSession(apiClientWith(post));

    expect(await session.ensure()).toEqual({
      status: "error",
      kind: "forbidden",
    });
    expect(await session.ensure()).toEqual({ status: "ready" });
    expect(post).toHaveBeenCalledTimes(2);
  });

  it("redacts network failures into unavailable state", async () => {
    const post = vi
      .fn()
      .mockRejectedValue(new Error("PRIVATE cookie and provider detail"));
    const session = new SingleProfileSession(apiClientWith(post));

    expect(await session.ensure()).toEqual({
      status: "error",
      kind: "unavailable",
    });
  });
});

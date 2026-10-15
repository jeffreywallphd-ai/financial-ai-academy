import { describe, expect, it, vi } from "vitest";

import type { FinancialAcademyApiClient } from "../../src/generated/api-client";
import { createLearningCatalogLoader } from "../../src/features/learning-catalog/api";
import {
  learningCatalogIsSafe,
  opportunityCanOpen,
} from "../../src/features/learning-catalog/model";
import type { SingleProfileSession } from "../../src/platform/auth/singleProfileSession";
import {
  learningCatalogFixture,
  plannedOpportunity,
} from "../component/learningCatalogFixture";

function copyCatalog(): unknown {
  return structuredClone(learningCatalogFixture);
}

function response(status: number, data?: unknown, error?: unknown) {
  return {
    data,
    error,
    response: new Response(null, { status }),
  };
}

describe("learningCatalogIsSafe", () => {
  it("accepts a variable valid record set and a valid empty catalog", () => {
    expect(learningCatalogIsSafe(copyCatalog())).toBe(true);
    expect(
      learningCatalogIsSafe({
        ...structuredClone(learningCatalogFixture),
        records: [],
      }),
    ).toBe(true);
  });

  it.each([
    ["unknown envelope field", (catalog: any) => { catalog.private_owner = "hidden"; }],
    ["unsafe destination", (catalog: any) => { catalog.records[0].destination = "https://example.test/lesson"; }],
    ["duplicate objective", (catalog: any) => { catalog.records[0].objectives.push(catalog.records[0].objectives[0]); }],
    ["mixed projection time", (catalog: any) => { catalog.records[0].projected_at = "2026-10-15T12:01:00Z"; }],
    ["observable order change", (catalog: any) => { catalog.records.reverse(); }],
  ])("rejects %s without accepting a partial list", (_label, mutate) => {
    const catalog = copyCatalog();
    mutate(catalog);
    expect(learningCatalogIsSafe(catalog)).toBe(false);
  });

  it("exposes actions only for exact available lessons", () => {
    const available = learningCatalogFixture.records[0];
    if (!available) {
      throw new Error("Expected an available fixture record.");
    }
    expect(opportunityCanOpen(available)).toBe(true);
    expect(opportunityCanOpen(plannedOpportunity)).toBe(false);
  });
});

describe("createLearningCatalogLoader", () => {
  it("uses the generated queryless operation after session establishment", async () => {
    const get = vi.fn().mockResolvedValue(response(200, copyCatalog()));
    const client = { GET: get } as unknown as FinancialAcademyApiClient;
    const session = {
      ensure: vi.fn().mockResolvedValue({ status: "ready" }),
      invalidate: vi.fn(),
    } as unknown as SingleProfileSession;
    const loader = createLearningCatalogLoader(client, session);

    const result = await loader({
      request: new Request("http://localhost/learn"),
    } as never);

    expect(result.status).toBe("ready");
    expect(get).toHaveBeenCalledWith(
      "/api/v1/curriculum/opportunities",
      expect.objectContaining({ signal: expect.any(AbortSignal) }),
    );
  });

  it("renews once after unauthorized and fails closed on invalid success", async () => {
    const get = vi
      .fn()
      .mockResolvedValueOnce(response(401, undefined, { code: "unauthorized" }))
      .mockResolvedValueOnce(response(200, { schema_version: "1.0.0" }));
    const client = { GET: get } as unknown as FinancialAcademyApiClient;
    const session = {
      ensure: vi.fn().mockResolvedValue({ status: "ready" }),
      invalidate: vi.fn(),
    } as unknown as SingleProfileSession;
    const loader = createLearningCatalogLoader(client, session);

    const result = await loader({
      request: new Request("http://localhost/learn"),
    } as never);

    expect(result).toEqual({ status: "invalid-response" });
    expect(get).toHaveBeenCalledTimes(2);
    expect(session.invalidate).toHaveBeenCalledOnce();
    expect(session.ensure).toHaveBeenCalledTimes(2);
  });
});

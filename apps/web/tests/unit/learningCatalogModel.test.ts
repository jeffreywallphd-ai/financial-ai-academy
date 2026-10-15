import { describe, expect, it, vi } from "vitest";

import type { FinancialAcademyApiClient } from "../../src/generated/api-client";
import { createLearningCatalogLoader } from "../../src/features/learning-catalog/api";
import {
  learningCatalogIsSafe,
  opportunityCanOpen,
} from "../../src/features/learning-catalog/model";
import type {
  LearningCatalog,
  LearningOpportunity,
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

function canonicalJson(value: unknown): string {
  const canonical = (item: unknown): unknown => {
    if (Array.isArray(item)) {
      return item.map(canonical);
    }
    if (typeof item === "object" && item !== null) {
      const objectItem = item as Record<string, unknown>;
      return Object.fromEntries(
        Object.keys(objectItem)
          .sort()
          .map((key) => [key, canonical(objectItem[key])]),
      );
    }
    return item;
  };
  return JSON.stringify(canonical(value));
}

async function digest(value: unknown): Promise<string> {
  const bytes = new TextEncoder().encode(canonicalJson(value));
  const result = await globalThis.crypto.subtle.digest("SHA-256", bytes);
  return [...new Uint8Array(result)]
    .map((byte) => byte.toString(16).padStart(2, "0"))
    .join("");
}

async function catalogWithIntegrity(
  records: readonly LearningOpportunity[],
  projectedAt = learningCatalogFixture.projected_at,
): Promise<LearningCatalog> {
  const coherentRecords: LearningOpportunity[] = [];
  for (const opportunity of records) {
    const { projected_at: _projectedAt, source_fingerprint: _source, ...meaning } =
      opportunity;
    coherentRecords.push({
      ...opportunity,
      projected_at: projectedAt,
      source_fingerprint: await digest(meaning),
    });
  }
  const stableRecords = coherentRecords.map((opportunity) => {
    const { projected_at: _projectedAt, ...stable } = opportunity;
    return stable;
  });
  return {
    schema_version: "1.0.0",
    projection_generation: await digest(stableRecords),
    projected_at: projectedAt,
    records: coherentRecords,
  };
}

describe("learningCatalogIsSafe", () => {
  it("accepts a variable valid record set and a valid empty catalog", async () => {
    await expect(learningCatalogIsSafe(copyCatalog())).resolves.toBe(true);
    await expect(
      learningCatalogIsSafe({
        ...structuredClone(learningCatalogFixture),
        records: [],
        projection_generation:
          "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
      }),
    ).resolves.toBe(true);
  });

  it.each([
    ["unknown envelope field", (catalog: any) => { catalog.private_owner = "hidden"; }],
    ["unsafe destination", (catalog: any) => { catalog.records[0].destination = "https://example.test/lesson"; }],
    ["duplicate objective", (catalog: any) => { catalog.records[0].objectives.push(catalog.records[0].objectives[0]); }],
    ["mixed projection time", (catalog: any) => { catalog.records[0].projected_at = "2026-10-15T12:01:00Z"; }],
    ["observable order change", (catalog: any) => { catalog.records.reverse(); }],
  ])("rejects %s without accepting a partial list", async (_label, mutate) => {
    const catalog = copyCatalog();
    mutate(catalog);
    await expect(learningCatalogIsSafe(catalog)).resolves.toBe(false);
  });

  it("rejects a calendar-invalid datetime rather than normalizing it", async () => {
    const catalog = copyCatalog() as {
      records: Array<{ provenance: { published_at: string } }>;
    };
    const first = catalog.records[0];
    if (!first) {
      throw new Error("Expected a catalog record.");
    }
    first.provenance.published_at = "2026-02-31T12:00:00Z";

    await expect(learningCatalogIsSafe(catalog)).resolves.toBe(false);

    const invalidReviewDate = copyCatalog() as {
      records: Array<{ provenance: { content_reviewed_on: string } }>;
    };
    const invalidReviewRecord = invalidReviewDate.records[0];
    if (!invalidReviewRecord) {
      throw new Error("Expected a catalog record.");
    }
    invalidReviewRecord.provenance.content_reviewed_on = "2026-02-30";
    await expect(learningCatalogIsSafe(invalidReviewDate)).resolves.toBe(false);
  });

  it("accepts a real leap-day timestamp and distinct opportunities sharing a placement", async () => {
    const first = structuredClone(learningCatalogFixture.records[0]);
    if (!first) {
      throw new Error("Expected a catalog record.");
    }
    const alternate = {
      ...structuredClone(first),
      opportunity_id: "cash-flow-basics-alternate",
      title: "Cash Flow Basics: Alternate View",
      provenance: {
        ...first.provenance,
        published_at: "2024-02-29T12:00:00Z",
      },
    };
    first.provenance = {
      ...first.provenance,
      published_at: "2024-02-29T12:00:00Z",
    };
    const catalog = await catalogWithIntegrity(
      [first, alternate],
      "2024-02-29T12:00:00Z",
    );

    await expect(learningCatalogIsSafe(catalog)).resolves.toBe(true);
    expect(catalog.records[0]?.placement_id).toBe(
      catalog.records[1]?.placement_id,
    );
  });

  it("rejects changed owner facts and record order when integrity values are stale", async () => {
    const changedTitle = copyCatalog() as {
      records: Array<{ title: string }>;
    };
    const first = changedTitle.records[0];
    if (!first) {
      throw new Error("Expected a catalog record.");
    }
    first.title = "Épargne et flux de trésorerie";
    await expect(learningCatalogIsSafe(changedTitle)).resolves.toBe(false);

    const reordered = copyCatalog() as { records: unknown[] };
    reordered.records.reverse();
    await expect(learningCatalogIsSafe(reordered)).resolves.toBe(false);
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

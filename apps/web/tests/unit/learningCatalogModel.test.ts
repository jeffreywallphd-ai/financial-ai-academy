import { describe, expect, it, vi } from "vitest";

import type { FinancialAcademyApiClient } from "../../src/generated/api-client";
import {
  createLearningCatalogLoader,
  parseLearningCatalogQuery,
} from "../../src/features/learning-catalog/api";
import {
  learningCatalogIsSafe,
  learningCatalogQueryPageIsSafe,
  opportunityCanOpen,
} from "../../src/features/learning-catalog/model";
import type {
  LearningCatalog,
  LearningOpportunity,
} from "../../src/features/learning-catalog/model";
import type { SingleProfileSession } from "../../src/platform/auth/singleProfileSession";
import {
  learningCatalogFixture,
  learningQueryPageFixture,
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

function canonicalPublishedAtForDigest(value: string): string {
  const fraction = /\.(\d{1,6})(?:Z|[+-]\d{2}:\d{2})$/.exec(value)?.[1];
  const canonicalFraction = fraction ? `.${fraction.padEnd(6, "0")}` : "";
  return `${new Date(value).toISOString().slice(0, 19)}${canonicalFraction}Z`;
}

async function catalogWithIntegrity(
  records: readonly LearningOpportunity[],
  projectedAt = learningCatalogFixture.projected_at,
): Promise<LearningCatalog> {
  const coherentRecords: LearningOpportunity[] = [];
  for (const opportunity of records) {
    const {
      projected_at: _projectedAt,
      source_fingerprint: _source,
      provenance,
      ...meaning
    } = opportunity;
    const canonicalMeaning = {
      ...meaning,
      provenance: {
        ...provenance,
        published_at: canonicalPublishedAtForDigest(provenance.published_at),
      },
    };
    coherentRecords.push({
      ...opportunity,
      projected_at: projectedAt,
      source_fingerprint: await digest(canonicalMeaning),
    });
  }
  const stableRecords = coherentRecords.map((opportunity) => {
    const { projected_at: _projectedAt, provenance, ...stable } = opportunity;
    return {
      ...stable,
      provenance: {
        ...provenance,
        published_at: canonicalPublishedAtForDigest(provenance.published_at),
      },
    };
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
    [
      "unknown envelope field",
      (catalog: any) => {
        catalog.private_owner = "hidden";
      },
    ],
    [
      "unsafe destination",
      (catalog: any) => {
        catalog.records[0].destination = "https://example.test/lesson";
      },
    ],
    [
      "duplicate objective",
      (catalog: any) => {
        catalog.records[0].objectives.push(catalog.records[0].objectives[0]);
      },
    ],
    [
      "mixed projection time",
      (catalog: any) => {
        catalog.records[0].projected_at = "2026-10-15T12:01:00Z";
      },
    ],
    [
      "observable order change",
      (catalog: any) => {
        catalog.records.reverse();
      },
    ],
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

  it.each([
    ["whole seconds", "2026-10-15T08:00:00-04:00"],
    ["fractional seconds", "2026-10-15T08:00:00.1234-04:00"],
  ])(
    "accepts a source fingerprint normalized from %s with an offset",
    async (_label, publishedAt) => {
      const opportunity = structuredClone(learningCatalogFixture.records[0]);
      if (!opportunity) {
        throw new Error("Expected a catalog record.");
      }
      opportunity.provenance = {
        ...opportunity.provenance,
        published_at: publishedAt,
      };
      const catalog = await catalogWithIntegrity([opportunity]);

      await expect(learningCatalogIsSafe(catalog)).resolves.toBe(true);
    },
  );

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
  it("uses the generated query operation with bounded URL parameters", async () => {
    const get = vi
      .fn()
      .mockResolvedValue(
        response(200, structuredClone(learningQueryPageFixture)),
      );
    const client = { GET: get } as unknown as FinancialAcademyApiClient;
    const session = {
      ensure: vi.fn().mockResolvedValue({ status: "ready" }),
      invalidate: vi.fn(),
    } as unknown as SingleProfileSession;
    const loader = createLearningCatalogLoader(client, session);

    const result = await loader({
      request: new Request(
        "http://localhost/learn?query=cash&level=introductory&page_size=10",
      ),
    } as never);

    expect(result.status).toBe("ready");
    expect(get).toHaveBeenCalledWith(
      "/api/v1/curriculum/opportunities/query",
      expect.objectContaining({
        params: {
          query: { query: "cash", level: ["introductory"], page_size: 10 },
        },
        signal: expect.any(AbortSignal),
      }),
    );
  });

  it("rejects malformed URL state before session or API work", async () => {
    const get = vi.fn();
    const session = {
      ensure: vi.fn(),
      invalidate: vi.fn(),
    } as unknown as SingleProfileSession;
    const loader = createLearningCatalogLoader(
      { GET: get } as unknown as FinancialAcademyApiClient,
      session,
    );
    const result = await loader({
      request: new Request(
        "http://localhost/learn?minimum_minutes=40&maximum_minutes=20",
      ),
    } as never);
    expect(result).toEqual({ status: "invalid-query" });
    expect(session.ensure).not.toHaveBeenCalled();
    expect(get).not.toHaveBeenCalled();
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

describe("query page boundaries", () => {
  it("keeps every query control optional for an unfiltered catalog", () => {
    expect(parseLearningCatalogQuery("http://localhost/learn")).toEqual({});
    expect(
      parseLearningCatalogQuery(
        "http://localhost/learn?query=&prerequisite_query=&topic=",
      ),
    ).toEqual({});
  });

  it("accepts the closed page and builds repeated URL values", async () => {
    await expect(
      learningCatalogQueryPageIsSafe(
        structuredClone(learningQueryPageFixture),
        {},
      ),
    ).resolves.toBe(true);
    expect(
      parseLearningCatalogQuery(
        "http://localhost/learn?topic=cash-flow&level=introductory&level=advanced",
      ),
    ).toEqual({
      topic: ["cash-flow"],
      level: ["introductory", "advanced"],
    });
    const cursor = `${"a".repeat(160)}.${"d".repeat(64)}`;
    expect(
      parseLearningCatalogQuery(`http://localhost/learn?cursor=${cursor}`),
    ).toEqual({ cursor });
  });

  it("rejects partial or private query pages", async () => {
    const page = structuredClone(learningQueryPageFixture) as any;
    page.private_ranking = 0.9;
    await expect(learningCatalogQueryPageIsSafe(page, {})).resolves.toBe(false);
  });

  it("rejects contradictory page counts, cursors, and cursor bounds", async () => {
    const missingRecords = {
      ...structuredClone(learningQueryPageFixture),
      records: [],
    };
    await expect(
      learningCatalogQueryPageIsSafe(missingRecords, {}),
    ).resolves.toBe(false);

    const cursorWithoutMatches = {
      ...structuredClone(learningQueryPageFixture),
      records: [],
      total_matches: 0,
      next_cursor: `cursor.${"d".repeat(64)}`,
    };
    await expect(
      learningCatalogQueryPageIsSafe(cursorWithoutMatches, {}),
    ).resolves.toBe(false);

    const validContinuation = {
      ...structuredClone(learningQueryPageFixture),
      applied_query: {
        ...learningQueryPageFixture.applied_query,
        page_size: 2,
      },
      total_matches: 3,
      next_cursor: `cursor.${"d".repeat(64)}`,
    };
    await expect(
      learningCatalogQueryPageIsSafe(validContinuation, {}),
    ).resolves.toBe(true);

    const oversizedCursor = {
      ...validContinuation,
      next_cursor: `${"a".repeat(960)}.${"d".repeat(64)}`,
    };
    await expect(
      learningCatalogQueryPageIsSafe(oversizedCursor, {}),
    ).resolves.toBe(false);
  });
});

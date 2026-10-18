import { describe, expect, it, vi } from "vitest";

import type { FinancialAcademyApiClient } from "../../src/generated/api-client";
import {
  createContextualHelpReader,
  createPlatformHelpSearchLoader,
  createPlatformHelpTopicLoader,
  parsePlatformHelpSearch,
  parsePlatformHelpTopicSelection,
} from "../../src/features/platform-help/api";
import {
  contextualHelpIsSafe,
  platformHelpSearchPageIsSafe,
  platformHelpTopicIsSafe,
} from "../../src/features/platform-help/model";
import type { SingleProfileSession } from "../../src/platform/auth/singleProfileSession";
import {
  contextualHelpFixture,
  platformHelpSearchFixture,
  platformHelpTopicFixture,
} from "../component/platformHelpFixture";

function response(status: number, data?: unknown) {
  return {
    data,
    error: undefined,
    response: new Response(null, { status }),
  };
}

function session(): SingleProfileSession {
  return {
    ensure: vi.fn().mockResolvedValue({ status: "ready" }),
    invalidate: vi.fn(),
  } as unknown as SingleProfileSession;
}

describe("platform help query boundaries", () => {
  it("parses the bounded public search and rejects duplicate or unknown input", () => {
    expect(
      parsePlatformHelpSearch(
        "http://academy.test/help?query=calculations&topic_kind=method&page_size=17",
      ),
    ).toEqual({
      parameters: {
        query: "calculations",
        topic_kind: "method",
        page_size: 17,
      },
      href: "/help?query=calculations&topic_kind=method&page_size=17",
    });
    expect(
      parsePlatformHelpSearch("http://academy.test/help?query=a&query=b"),
    ).toBeNull();
    expect(
      parsePlatformHelpSearch("http://academy.test/help?provider=private"),
    ).toBeNull();
    expect(
      parsePlatformHelpSearch("http://academy.test/help?page_size=51"),
    ).toBeNull();
    expect(
      parsePlatformHelpSearch(
        "http://academy.test/help?query=&topic_kind=&page_size=20",
      ),
    ).toEqual({
      parameters: { query: "", page_size: 20 },
      href: "/help?page_size=20",
    });
  });

  it("counts Unicode code points and preserves the two admitted shaping characters", () => {
    const valid = "😀".repeat(200);
    const selection = parsePlatformHelpSearch(
      `http://academy.test/help?query=${encodeURIComponent(valid)}`,
    );
    expect(selection?.parameters.query).toBe(valid);
    expect(
      parsePlatformHelpSearch(
        `http://academy.test/help?query=${encodeURIComponent("😀".repeat(201))}`,
      ),
    ).toBeNull();
    expect(
      parsePlatformHelpSearch(
        `http://academy.test/help?query=${encodeURIComponent("family‍learning‌notes")}`,
      )?.parameters.query,
    ).toBe("family‍learning‌notes");
  });

  it("accepts only exact topic identities and a safe same-origin return path", () => {
    expect(
      parsePlatformHelpTopicSelection(
        "platform-methods",
        "1.0.0",
        "http://academy.test/help/topics/platform-methods/versions/1.0.0?return_to=%2Fhelp%3Fquery%3Dcalculations",
      ),
    ).toEqual({
      topicId: "platform-methods",
      topicVersion: "1.0.0",
      returnTo: "/help?query=calculations&page_size=20",
      returnLabel: "Return to platform guide",
    });
    expect(
      parsePlatformHelpTopicSelection(
        "source-and-history",
        "1.0.0",
        "http://academy.test/help/topics/source-and-history/versions/1.0.0?return_to=%2Fprojects%2Fproject-one",
      ),
    ).toEqual({
      topicId: "source-and-history",
      topicVersion: "1.0.0",
      returnTo: "/projects/project-one",
      returnLabel: "Return to Project",
    });
    expect(
      parsePlatformHelpTopicSelection(
        "platform-methods",
        "latest",
        "http://academy.test/help",
      ),
    ).toBeNull();
    expect(
      parsePlatformHelpTopicSelection(
        "platform-methods",
        "1.0.0",
        "http://academy.test/help?return_to=https%3A%2F%2Fevil.test%2Fhelp",
      ),
    ).toBeNull();
    expect(
      parsePlatformHelpTopicSelection(
        "platform-methods",
        "1.0.0",
        "http://academy.test/help?return_to=%2Fprojects%2Fproject-one%3Fadmin%3Dtrue",
      ),
    ).toBeNull();
  });
});

describe("platform help response validation", () => {
  it("accepts the closed search and exact-topic fixtures", () => {
    expect(
      platformHelpSearchPageIsSafe(platformHelpSearchFixture, {
        query: "calculations",
        topic_kind: "method",
        page_size: 20,
      }),
    ).toBe(true);
    expect(
      platformHelpTopicIsSafe(
        platformHelpTopicFixture,
        "platform-methods",
        "1.0.0",
      ),
    ).toBe(true);
    expect(
      contextualHelpIsSafe(
        contextualHelpFixture,
        "lesson-publication",
        "1.0.0",
      ),
    ).toBe(true);
  });

  it("rejects substituted, extended, duplicate, or malformed contextual Help", () => {
    const changedIdentity = {
      ...contextualHelpFixture,
      context_key: "practice-result",
    };
    expect(
      contextualHelpIsSafe(changedIdentity, "lesson-publication", "1.0.0"),
    ).toBe(false);
    expect(
      contextualHelpIsSafe(
        { ...contextualHelpFixture, hidden_route: "/admin" },
        "lesson-publication",
        "1.0.0",
      ),
    ).toBe(false);
    expect(
      contextualHelpIsSafe(
        {
          ...contextualHelpFixture,
          help_references: [
            contextualHelpFixture.help_references[0]!,
            contextualHelpFixture.help_references[0]!,
          ],
        },
        "lesson-publication",
        "1.0.0",
      ),
    ).toBe(false);
  });

  it("accepts the server-owned Unicode case-folded query without duplicating ranking rules", () => {
    expect(
      platformHelpSearchPageIsSafe(
        { ...platformHelpSearchFixture, query: "strasse" },
        {
          query: "  Straße ",
          topic_kind: "method",
          page_size: 20,
        },
      ),
    ).toBe(true);
  });

  it("uses code-point bounds for valid astral body text", () => {
    const boundary = structuredClone(platformHelpTopicFixture) as any;
    boundary.body[1].text = "😀".repeat(2000);
    expect(platformHelpTopicIsSafe(boundary, "platform-methods", "1.0.0")).toBe(
      true,
    );

    boundary.body[1].text += "😀";
    expect(platformHelpTopicIsSafe(boundary, "platform-methods", "1.0.0")).toBe(
      false,
    );
  });

  it.each([
    ["extra result field", (value: any) => (value.results[0].provider = "private")],
    ["bad fingerprint", (value: any) => (value.results[0].topic_digest = "bad")],
    ["repeated identity", (value: any) => value.results.push(value.results[0])],
  ])("rejects a search page with %s", (_label, mutate) => {
    const value = structuredClone(platformHelpSearchFixture);
    mutate(value);
    expect(
      platformHelpSearchPageIsSafe(value, {
        query: "calculations",
        topic_kind: "method",
        page_size: 20,
      }),
    ).toBe(false);
  });

  it.each([
    ["unknown body node", (value: any) => value.body.push({ node_kind: "html", html: "<script />" })],
    ["unsafe source field", (value: any) => (value.source_references[0].path = "docs/private.md")],
    ["wrong exact identity", (value: any) => (value.topic_version = "2.0.0")],
    [
      "invalid publication date",
      (value: any) => (value.publication.updated_at = "2026-02-30T00:00:00Z"),
    ],
  ])("rejects a topic with %s", (_label, mutate) => {
    const value = structuredClone(platformHelpTopicFixture);
    mutate(value);
    expect(platformHelpTopicIsSafe(value, "platform-methods", "1.0.0")).toBe(false);
  });
});

describe("platform help loaders", () => {
  it("reads one exact generated contextual-help operation and fails closed", async () => {
    const GET = vi
      .fn()
      .mockResolvedValueOnce(response(200, contextualHelpFixture))
      .mockResolvedValueOnce(
        response(200, { ...contextualHelpFixture, hidden_route: "/admin" }),
      );
    const reader = createContextualHelpReader(
      { GET } as unknown as FinancialAcademyApiClient,
      session(),
    );
    const controller = new AbortController();

    await expect(
      reader("lesson-publication", "1.0.0", controller.signal),
    ).resolves.toEqual({ status: "ready", context: contextualHelpFixture });
    expect(GET).toHaveBeenNthCalledWith(
      1,
      "/api/v1/guidance/contextual-help/{context_key}/versions/{context_version}",
      {
        params: {
          path: {
            context_key: "lesson-publication",
            context_version: "1.0.0",
          },
        },
        signal: controller.signal,
      },
    );
    await expect(
      reader("lesson-publication", "1.0.0", controller.signal),
    ).resolves.toEqual({ status: "unavailable" });
  });

  it("rejects unsafe query categories before session or content access", async () => {
    for (const query of ["unsafe\u0001control", "bidi\u202Etext", "private\uE000text", "unassigned\u0378text"]) {
      const GET = vi.fn();
      const localSession = session();
      const loader = createPlatformHelpSearchLoader(
        { GET } as unknown as FinancialAcademyApiClient,
        localSession,
      );
      const request = new Request(
        `http://academy.test/help?query=${encodeURIComponent(query)}`,
      );

      await expect(
        loader({ request, params: {}, context: {} } as any),
      ).resolves.toEqual({ status: "invalid-query" });
      expect(localSession.ensure).not.toHaveBeenCalled();
      expect(GET).not.toHaveBeenCalled();
    }
  });

  it("does not request help content when session setup is denied", async () => {
    const GET = vi.fn();
    const deniedSession = {
      ensure: vi.fn().mockResolvedValue({ status: "error", kind: "forbidden" }),
      invalidate: vi.fn(),
    } as unknown as SingleProfileSession;
    const loader = createPlatformHelpSearchLoader(
      { GET } as unknown as FinancialAcademyApiClient,
      deniedSession,
    );
    const request = new Request("http://academy.test/help");

    await expect(
      loader({ request, params: {}, context: {} } as any),
    ).resolves.toEqual({ status: "forbidden" });
    expect(GET).not.toHaveBeenCalled();
  });

  it("uses only the generated search operation after the session is ready", async () => {
    const GET = vi.fn().mockResolvedValue(response(200, platformHelpSearchFixture));
    const loader = createPlatformHelpSearchLoader(
      { GET } as unknown as FinancialAcademyApiClient,
      session(),
    );
    const request = new Request(
      "http://academy.test/help?query=calculations&topic_kind=method&page_size=20",
    );

    await expect(
      loader({ request, params: {}, context: {} } as any),
    ).resolves.toMatchObject({ status: "ready" });
    expect(GET).toHaveBeenCalledWith("/api/v1/guidance/platform-help", {
      params: {
        query: {
          query: "calculations",
          topic_kind: "method",
          page_size: 20,
        },
      },
      signal: request.signal,
    });
  });

  it("fails closed for malformed exact content and bounded absence", async () => {
    const invalid = structuredClone(platformHelpTopicFixture) as any;
    invalid.body[0].level = 1;
    const GET = vi
      .fn()
      .mockResolvedValueOnce(response(200, invalid))
      .mockResolvedValueOnce(response(404));
    const loader = createPlatformHelpTopicLoader(
      { GET } as unknown as FinancialAcademyApiClient,
      session(),
    );
    const request = new Request(
      "http://academy.test/help/topics/platform-methods/versions/1.0.0",
    );
    const args = {
      request,
      params: { topicId: "platform-methods", topicVersion: "1.0.0" },
      context: {},
    };

    await expect(loader(args as any)).resolves.toEqual({
      status: "invalid-response",
    });
    await expect(loader(args as any)).resolves.toEqual({ status: "not-found" });
  });
});

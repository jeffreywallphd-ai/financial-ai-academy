import { expect, test } from "@playwright/test";
import { readFile, writeFile } from "node:fs/promises";

import { createFinancialAcademyApiClient } from "../../../src/generated/api-client/client";
import type { components } from "../../../src/generated/api-client/schema";

const PLACEMENT_ID = "intro-risk-return-primary";
const HISTORY_PATH = "/api/v1/audit/accountable-history";
const EXPORT_PATH = "/api/v1/audit/accountable-history/export";
type LessonRequest =
  components["schemas"]["PublishedLessonLineageRequestModel"];
type CompletionRequest =
  components["schemas"]["KnowledgeCheckCompletionLineageRequestModel"];
type HistoryRequest = LessonRequest | CompletionRequest;
type HistoryResponse = components["schemas"]["AccountableHistoryResponseModel"];
type ExportResponse =
  components["schemas"]["PortableEvidenceExportResponseModel"];
type HistoryRequests = {
  lesson: LessonRequest;
  completion: CompletionRequest;
};

function nestedKeys(value: unknown): Set<string> {
  if (Array.isArray(value)) {
    return value.reduce((keys, item) => {
      for (const key of nestedKeys(item)) keys.add(key);
      return keys;
    }, new Set<string>());
  }
  if (typeof value !== "object" || value === null) return new Set<string>();
  const keys = new Set<string>();
  for (const [key, item] of Object.entries(value)) {
    keys.add(key);
    for (const nested of nestedKeys(item)) keys.add(nested);
  }
  return keys;
}

function assertPublicHistory(
  value: HistoryResponse,
  request: HistoryRequest,
  purpose: HistoryResponse["purpose"],
) {
  expect(value.schema_version).toBe("1.0.0");
  expect(value.purpose).toBe(purpose);
  expect(value.root.root_kind).toBe(request.root_kind);
  if (request.root_kind === "published_lesson") {
    expect(value.root).toEqual({
      root_kind: request.root_kind,
      resource_id: request.package_id,
      resource_version: request.package_version,
    });
  } else {
    expect(value.root).toEqual({
      root_kind: request.root_kind,
      resource_id: request.evidence_id,
      occurrence: request.occurrence,
    });
  }
  expect(["valid", "incomplete", "invalid"]).toContain(value.state);
  expect(value.entries.length).toBeGreaterThan(0);
  expect(value.entries.length).toBeLessThanOrEqual(64);
  expect(value.transformations.length).toBeLessThanOrEqual(128);
  expect(value.missing_links.length).toBeLessThanOrEqual(32);
  expect(value.diagnostics.length).toBeLessThanOrEqual(32);
  expect(value.redactions.length).toBeLessThanOrEqual(6);
  expect(value.source_lineage_digest).toMatch(/^[a-f0-9]{64}$/);
  expect(value.history_digest).toMatch(/^[a-f0-9]{64}$/);
  expect(value.entries.map((entry) => entry.sequence)).toEqual(
    value.entries.map((_entry, index) => index + 1),
  );
  const entryIds = new Set(value.entries.map((entry) => entry.entry_id));
  expect(entryIds.size).toBe(value.entries.length);
  for (const transformation of value.transformations) {
    expect(entryIds.has(transformation.source_entry_id)).toBe(true);
    expect(entryIds.has(transformation.target_entry_id)).toBe(true);
  }
  const matchingEntries = value.entries.filter((entry) => {
    if (request.root_kind === "published_lesson") {
      return (
        entry.resource_kind === "published_lesson" &&
        entry.resource_id === request.package_id &&
        entry.resource_version === request.package_version
      );
    }
    return (
      entry.resource_kind === "completion_evidence" &&
      entry.resource_id === request.evidence_id &&
      entry.occurrence === request.occurrence
    );
  });
  expect(matchingEntries).toHaveLength(1);
  expect(
    [...nestedKeys(value)].filter((key) =>
      /^(answer|feedback|learner_id|locator|path|permission|provider_payload|score|session_id|storage)$/.test(
        key,
      ),
    ),
  ).toEqual([]);
}

function assertPublicExport(value: ExportResponse, request: HistoryRequest) {
  expect(value.schema_version).toBe("1.0.0");
  expect(value.media_type).toBe(
    "application/vnd.financial-ai-academy.accountable-history+json",
  );
  expect(value.filename_stem).toMatch(/^[a-z0-9][a-z0-9-]{0,79}$/);
  expect(value.exported_at).toMatch(
    /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?Z$/,
  );
  expect(value.document_digest).toBe(value.document.history_digest);
  assertPublicHistory(value.document, request, "portable_evidence");
}

function assertHistoryRequests(
  value: unknown,
): asserts value is HistoryRequests {
  expect(value).toEqual({
    lesson: expect.objectContaining({
      schema_version: "1.0.0",
      root_kind: "published_lesson",
    }),
    completion: expect.objectContaining({
      schema_version: "1.0.0",
      root_kind: "knowledge_check_completion",
    }),
  });
}

test("generated and ordinary clients receive the same live accountable history", async ({
  request,
}) => {
  const origin =
    process.env.FINANCIAL_AI_ACADEMY_E2E_BASE_URL ?? "http://127.0.0.1:8000";
  const mode = process.env.FINANCIAL_AI_ACADEMY_HISTORY_MODE ?? "all";
  expect(["all", "selectors", "operations"]).toContain(mode);
  const selectorCapturePath =
    process.env.FINANCIAL_AI_ACADEMY_HISTORY_SELECTOR_CAPTURE;
  const generatedClient = createFinancialAcademyApiClient(origin);
  const generatedSession = await generatedClient.POST(
    "/api/v1/session/single-profile",
    {
      body: { limitation_acknowledged: true },
      headers: { Origin: origin, "Sec-Fetch-Site": "same-origin" },
    },
  );
  expect(generatedSession.response.status).toBe(201);
  const setCookie = generatedSession.response.headers.get("set-cookie");
  expect(setCookie).toBeTruthy();
  const generatedHeaders = {
    Cookie: setCookie!.split(";", 1)[0],
    Origin: origin,
    "Sec-Fetch-Site": "same-origin",
  };
  let historyRequests: HistoryRequests;
  if (mode === "selectors" || mode === "all") {
    const lesson = await generatedClient.GET(
      "/api/v1/curriculum/placements/{placement_id}/lesson",
      {
        params: { path: { placement_id: PLACEMENT_ID } },
        headers: generatedHeaders,
      },
    );
    const completion = await generatedClient.GET(
      "/api/v1/curriculum/placements/{placement_id}/completion",
      {
        params: { path: { placement_id: PLACEMENT_ID } },
        headers: generatedHeaders,
      },
    );
    expect(lesson.response.status).toBe(200);
    expect(lesson.data).toBeTruthy();
    expect(completion.response.status).toBe(200);
    expect(completion.data?.history.length).toBeGreaterThan(0);
    const completionIndex = completion.data!.history.length - 1;
    const completionEvidence = completion.data!.history[completionIndex]!;
    historyRequests = {
      lesson: {
        schema_version: "1.0.0",
        root_kind: "published_lesson",
        package_id: lesson.data!.package_id,
        package_version: lesson.data!.package_version,
        package_digest: lesson.data!.package_digest,
      },
      completion: {
        schema_version: "1.0.0",
        root_kind: "knowledge_check_completion",
        placement_id: completion.data!.placement_id,
        evidence_id: completionEvidence.evidence_id,
        occurrence: completionIndex + 1,
      },
    };
    if (selectorCapturePath) {
      await writeFile(
        selectorCapturePath,
        `${JSON.stringify(
          { schema_version: "1.0.0", requests: historyRequests },
          null,
          2,
        )}\n`,
        { encoding: "utf-8", flag: "wx" },
      );
    }
    if (mode === "selectors") return;
  } else {
    expect(selectorCapturePath).toBeTruthy();
    const selectorCapture = JSON.parse(
      await readFile(selectorCapturePath!, "utf-8"),
    ) as { schema_version?: unknown; requests?: unknown };
    expect(selectorCapture.schema_version).toBe("1.0.0");
    assertHistoryRequests(selectorCapture.requests);
    historyRequests = selectorCapture.requests;
  }
  const { lesson: lessonRequest, completion: completionRequest } =
    historyRequests;

  const unauthorized = await request.post(HISTORY_PATH, {
    data: {
      schema_version: "1.0.0",
      root_kind: "published_lesson",
      package_id: "not-authorized",
      package_version: "1.0.0",
      package_digest: "0".repeat(64),
    },
    headers: { Origin: origin, "Sec-Fetch-Site": "same-origin" },
  });
  expect(unauthorized.status()).toBe(401);

  const generatedLesson = await generatedClient.POST(HISTORY_PATH, {
    body: lessonRequest,
    headers: generatedHeaders,
  });
  const generatedCompletion = await generatedClient.POST(HISTORY_PATH, {
    body: completionRequest,
    headers: generatedHeaders,
  });
  const generatedLessonExport = await generatedClient.POST(EXPORT_PATH, {
    body: lessonRequest,
    headers: generatedHeaders,
  });
  const generatedCompletionExport = await generatedClient.POST(EXPORT_PATH, {
    body: completionRequest,
    headers: generatedHeaders,
  });
  expect(generatedLesson.response.status).toBe(200);
  expect(generatedCompletion.response.status).toBe(200);
  expect(generatedLessonExport.response.status).toBe(200);
  expect(generatedCompletionExport.response.status).toBe(200);
  assertPublicHistory(
    generatedLesson.data! as unknown as HistoryResponse,
    lessonRequest,
    "learner_review",
  );
  assertPublicHistory(
    generatedCompletion.data! as unknown as HistoryResponse,
    completionRequest,
    "learner_review",
  );
  assertPublicExport(
    generatedLessonExport.data! as unknown as ExportResponse,
    lessonRequest,
  );
  assertPublicExport(
    generatedCompletionExport.data! as unknown as ExportResponse,
    completionRequest,
  );

  const directSession = await request.post("/api/v1/session/single-profile", {
    data: { limitation_acknowledged: true },
    headers: { Origin: origin, "Sec-Fetch-Site": "same-origin" },
  });
  expect(directSession.status()).toBe(201);
  async function directPost(path: string, body: HistoryRequest) {
    const response = await request.post(path, {
      data: body,
      headers: { Origin: origin, "Sec-Fetch-Site": "same-origin" },
    });
    expect(response.status()).toBe(200);
    return response.json();
  }
  const directLesson = (await directPost(
    HISTORY_PATH,
    lessonRequest,
  )) as HistoryResponse;
  const directCompletion = (await directPost(
    HISTORY_PATH,
    completionRequest,
  )) as HistoryResponse;
  const directLessonExport = (await directPost(
    EXPORT_PATH,
    lessonRequest,
  )) as ExportResponse;
  const directCompletionExport = (await directPost(
    EXPORT_PATH,
    completionRequest,
  )) as ExportResponse;
  expect(directLesson).toEqual(generatedLesson.data);
  expect(directCompletion).toEqual(generatedCompletion.data);
  expect(directLessonExport).toEqual(generatedLessonExport.data);
  expect(directCompletionExport).toEqual(generatedCompletionExport.data);

  const queryDenial = await request.post(`${HISTORY_PATH}?purpose=portable`, {
    data: lessonRequest,
    headers: { Origin: origin, "Sec-Fetch-Site": "same-origin" },
  });
  const guessedCompletion = await request.post(EXPORT_PATH, {
    data: {
      ...completionRequest,
      evidence_id: `${completionRequest.evidence_id}-missing`,
    },
    headers: { Origin: origin, "Sec-Fetch-Site": "same-origin" },
  });
  expect(queryDenial.status()).toBe(400);
  expect(guessedCompletion.status()).toBe(401);
  expect(
    `${await queryDenial.text()}${await guessedCompletion.text()}`,
  ).not.toMatch(
    /answer|feedback|learner_id|locator|permission|provider|score|session_id|storage/i,
  );

  const capturePath = process.env.FINANCIAL_AI_ACADEMY_HISTORY_CAPTURE;
  if (capturePath) {
    await writeFile(
      capturePath,
      `${JSON.stringify(
        {
          schema_version: "1.0.0",
          requests: historyRequests,
          generated: {
            lesson: {
              review: generatedLesson.data,
              export: generatedLessonExport.data,
            },
            completion: {
              review: generatedCompletion.data,
              export: generatedCompletionExport.data,
            },
          },
          direct: {
            lesson: { review: directLesson, export: directLessonExport },
            completion: {
              review: directCompletion,
              export: directCompletionExport,
            },
          },
          denial_statuses: {
            missing_session: unauthorized.status(),
            query: queryDenial.status(),
            guessed_completion: guessedCompletion.status(),
          },
        },
        null,
        2,
      )}\n`,
      { encoding: "utf-8", flag: "wx" },
    );
  }
});

import { expect, test } from "@playwright/test";
import { writeFile } from "node:fs/promises";

import { createFinancialAcademyApiClient } from "../../../src/generated/api-client/client";
import type { components } from "../../../src/generated/api-client/schema";


const PLACEMENT_ID = "intro-risk-return-primary";
const LINEAGE_PATH = "/api/v1/audit/learning-lineage";
type LessonRequest =
  components["schemas"]["PublishedLessonLineageRequestModel"];
type CompletionRequest =
  components["schemas"]["KnowledgeCheckCompletionLineageRequestModel"];
type LineageResponse =
  components["schemas"]["LearningLineageResponseModel"];

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

function assertPublicLineage(
  value: LineageResponse,
  rootKind: LessonRequest["root_kind"] | CompletionRequest["root_kind"],
) {
  expect(value.schema_version).toBe("1.0.0");
  expect(value.root.root_kind).toBe(rootKind);
  expect(value.nodes.length).toBeGreaterThan(0);
  expect(value.nodes.length).toBeLessThanOrEqual(64);
  expect(value.edges.length).toBeLessThanOrEqual(128);
  expect(value.incomplete_links.length).toBeLessThanOrEqual(32);
  expect(value.view_digest).toMatch(/^[a-f0-9]{64}$/);
  expect(
    [...nestedKeys(value)].filter((key) =>
      /^(answer|feedback|learner_id|locator|path|permission|provider_payload|score|session_id|storage)$/.test(
        key,
      ),
    ),
  ).toEqual([]);
}

test("generated and ordinary clients receive the same exact live lineage", async ({
  request,
}) => {
  const origin =
    process.env.FINANCIAL_AI_ACADEMY_E2E_BASE_URL ??
    "http://127.0.0.1:8000";
  const unauthorized = await request.post(LINEAGE_PATH, {
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
  const lesson = await generatedClient.GET(
    "/api/v1/curriculum/placements/{placement_id}/lesson",
    {
      params: { path: { placement_id: PLACEMENT_ID } },
      headers: generatedHeaders,
    },
  );
  expect(lesson.response.status).toBe(200);
  expect(lesson.data).toBeTruthy();
  const completion = await generatedClient.GET(
    "/api/v1/curriculum/placements/{placement_id}/completion",
    {
      params: { path: { placement_id: PLACEMENT_ID } },
      headers: generatedHeaders,
    },
  );
  expect(completion.response.status).toBe(200);
  expect(completion.data?.history.length).toBeGreaterThan(0);
  const completionEvidence =
    completion.data!.history[completion.data!.history.length - 1]!;

  const lessonRequest: LessonRequest = {
    schema_version: "1.0.0",
    root_kind: "published_lesson",
    package_id: lesson.data!.package_id,
    package_version: lesson.data!.package_version,
    package_digest: lesson.data!.package_digest,
  };
  const completionRequest: CompletionRequest = {
    schema_version: "1.0.0",
    root_kind: "knowledge_check_completion",
    placement_id: completion.data!.placement_id,
    evidence_id: completionEvidence.evidence_id,
    occurrence: 1,
  };
  const generatedLesson = await generatedClient.POST(LINEAGE_PATH, {
    body: lessonRequest,
    headers: generatedHeaders,
  });
  const generatedCompletion = await generatedClient.POST(LINEAGE_PATH, {
    body: completionRequest,
    headers: generatedHeaders,
  });
  expect(generatedLesson.response.status).toBe(200);
  expect(generatedCompletion.response.status).toBe(200);
  assertPublicLineage(
    generatedLesson.data! as unknown as LineageResponse,
    "published_lesson",
  );
  assertPublicLineage(
    generatedCompletion.data! as unknown as LineageResponse,
    "knowledge_check_completion",
  );

  const directSession = await request.post("/api/v1/session/single-profile", {
    data: { limitation_acknowledged: true },
    headers: { Origin: origin, "Sec-Fetch-Site": "same-origin" },
  });
  expect(directSession.status()).toBe(201);
  const directLessonResponse = await request.post(LINEAGE_PATH, {
    data: lessonRequest,
    headers: { Origin: origin, "Sec-Fetch-Site": "same-origin" },
  });
  const directCompletionResponse = await request.post(LINEAGE_PATH, {
    data: completionRequest,
    headers: { Origin: origin, "Sec-Fetch-Site": "same-origin" },
  });
  expect(directLessonResponse.status()).toBe(200);
  expect(directCompletionResponse.status()).toBe(200);
  const directLesson = (await directLessonResponse.json()) as LineageResponse;
  const directCompletion =
    (await directCompletionResponse.json()) as LineageResponse;
  assertPublicLineage(directLesson, "published_lesson");
  assertPublicLineage(directCompletion, "knowledge_check_completion");
  expect(directLesson).toEqual(generatedLesson.data);
  expect(directCompletion).toEqual(generatedCompletion.data);

  const queryDenial = await request.post(`${LINEAGE_PATH}?latest=true`, {
    data: lessonRequest,
    headers: { Origin: origin, "Sec-Fetch-Site": "same-origin" },
  });
  expect(queryDenial.status()).toBe(400);
  const guessedCompletion = await request.post(LINEAGE_PATH, {
    data: {
      ...completionRequest,
      evidence_id: `${completionRequest.evidence_id}-missing`,
    },
    headers: { Origin: origin, "Sec-Fetch-Site": "same-origin" },
  });
  expect(guessedCompletion.status()).toBe(401);
  expect(`${await queryDenial.text()}${await guessedCompletion.text()}`).not.toMatch(
    /answer|feedback|learner_id|locator|permission|provider|score|session_id|storage/i,
  );

  const capturePath = process.env.FINANCIAL_AI_ACADEMY_LINEAGE_CAPTURE;
  if (capturePath) {
    await writeFile(
      capturePath,
      `${JSON.stringify(
        {
          schema_version: "1.0.0",
          requests: {
            lesson: lessonRequest,
            completion: completionRequest,
          },
          generated: {
            lesson: generatedLesson.data,
            completion: generatedCompletion.data,
          },
          direct: { lesson: directLesson, completion: directCompletion },
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

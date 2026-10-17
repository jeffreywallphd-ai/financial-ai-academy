import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { resolve } from "node:path";


const generatedRoot = resolve(
  process.cwd(),
  "src",
  "generated",
  "api-client",
);
const schema = await readFile(resolve(generatedRoot, "schema.d.ts"), "utf8");
const client = await readFile(resolve(generatedRoot, "client.ts"), "utf8");
const index = await readFile(resolve(generatedRoot, "index.ts"), "utf8");
const combined = schema + client + index;

assert.match(schema, /^\/\/ @generated/m);
assert.match(schema, /Source: contracts\/api\/openapi\.json/);
assert.match(schema, /export interface paths/);
assert.match(
  schema,
  /\/api\/v1\/curriculum\/placements\/\{placement_id\}\/lesson/,
);
assert.match(schema, /\/api\/v1\/curriculum\/opportunities/);
assert.match(schema, /\/api\/v1\/curriculum\/graphs\/\{curriculum_id\}/);
assert.match(schema, /operations\["getCurriculumGraphVersion"\]/);
assert.match(schema, /CurriculumGraphResponseModel/);
assert.match(
  schema,
  /\/api\/v1\/adaptation\/curricula\/\{curriculum_id\}\/versions\/\{curriculum_version\}\/navigation-state/,
);
assert.match(schema, /operations\["getCurriculumNavigationState"\]/);
assert.match(schema, /NavigationStateResponseModel/);
assert.match(schema, /operations\["browseLearningOpportunities"\]/);
assert.match(schema, /operations\["queryLearningOpportunities"\]/);
assert.match(schema, /LearningOpportunityQueryPageResponseModel/);
assert.match(
  schema,
  /\/api\/v1\/curriculum\/placements\/\{placement_id\}\/practice\/submissions/,
);
assert.match(schema, /operations\["submitPlacedPractice"\]/);
assert.match(schema, /PracticeSubmissionRequestModel/);
assert.match(schema, /PracticeSubmissionResultResponseModel/);
assert.match(
  schema,
  /\/api\/v1\/curriculum\/placements\/\{placement_id\}\/practice\/progress/,
);
assert.match(schema, /operations\["getPlacedPracticeProgress"\]/);
assert.match(schema, /PracticeProgressResponseModel/);
assert.match(
  schema,
  /\/api\/v1\/curriculum\/placements\/\{placement_id\}\/practice\/draft/,
);
assert.match(schema, /operations\["savePlacedPracticeDraft"\]/);
assert.match(schema, /PracticeDraftSaveRequestModel/);
assert.match(schema, /PracticeDraftResponseModel/);
assert.match(schema, /PersonalProjectWorkspaceSelectorModel/);
assert.match(schema, /PersonalProjectSnapshotSelectorModel/);
assert.match(schema, /PersonalProjectArtifactSelectorModel/);
assert.match(schema, /PersonalProjectWorkspaceReferenceModel/);
assert.match(schema, /PersonalProjectSnapshotReferenceModel/);
assert.match(schema, /PersonalProjectArtifactReferenceModel/);
assert.match(schema, /\/api\/v1\/personal-workspace\/query/);
assert.match(schema, /operations\["queryPersonalWorkspace"\]/);
assert.match(schema, /PersonalWorkspaceQueryRequestModel/);
assert.match(schema, /PersonalWorkspaceQueryResponseModel/);
assert.match(schema, /\/api\/v1\/personal-workspace\/export/);
assert.match(schema, /operations\["exportPersonalWorkspace"\]/);
assert.match(schema, /PersonalWorkspaceExportResponseModel/);
assert.match(schema, /PersonalRefreshReferenceModel/);
assert.match(schema, /\/api\/v1\/learner-preferences/);
assert.match(schema, /operations\["getLearnerPreferences"\]/);
assert.match(schema, /operations\["mutateLearnerPreferences"\]/);
assert.match(schema, /operations\["getLearnerPreferenceHistory"\]/);
assert.match(schema, /operations\["exportLearnerPreferences"\]/);
assert.match(schema, /LearnerPreferenceMutationRequestModel/);
assert.match(schema, /LearnerPreferenceExportResponseModel/);
assert.match(schema, /"available" \| "stale" \| "unavailable"/);
for (const model of [
  "PersonalLearningOpportunityReferenceModel",
  "PersonalPlacedLessonReferenceModel",
  "PersonalProjectWorkspaceReferenceModel",
  "PersonalProjectSnapshotReferenceModel",
  "PersonalProjectArtifactReferenceModel",
]) {
  const modelSchema =
    schema.match(
      new RegExp(`readonly "${model}": \\{[\\s\\S]*?^    \\};`, "m"),
    )?.[0] ?? "";
  assert.match(
    modelSchema,
    /readonly "target_status": "available" \| "stale" \| "unavailable"/,
  );
}
for (const model of [
  "PersonalProjectWorkspaceReferenceModel",
  "PersonalProjectSnapshotReferenceModel",
  "PersonalProjectArtifactReferenceModel",
]) {
  assert.doesNotMatch(
    schema.match(
      new RegExp(`readonly "${model}": \\{[\\s\\S]*?^    \\};`, "m"),
    )?.[0] ?? "",
    /readonly "(?:content|content_base64|download_url|object_key|storage_key)"/,
  );
}
assert.doesNotMatch(
  schema.match(
    /readonly "PracticeSubmissionResultResponseModel": \{[\s\S]*?^    \};/m,
  )?.[0] ?? "",
  /learner_id|request_fingerprint/,
);
assert.doesNotMatch(
  schema.match(
    /readonly "PracticeProgressResponseModel": \{[\s\S]*?^    \};/m,
  )?.[0] ?? "",
  /learner_id|correct_answer|evaluator|request_fingerprint/,
);
assert.match(client, /createClient<paths>/);
assert.match(client, /credentials: "same-origin"/);
assert.doesNotMatch(combined, /financial_ai_academy/);
assert.doesNotMatch(combined, /psycopg|postgres|node:http|node:https/i);

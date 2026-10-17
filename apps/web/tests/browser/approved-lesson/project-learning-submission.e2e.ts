import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page } from "@playwright/test";
import { createHash } from "node:crypto";
import { writeFile } from "node:fs/promises";

import type {
  ProjectActivityCompletion,
  ProjectCompletionEvidence,
  ProjectCompletionHistory,
  ProjectShell,
  ProjectSnapshot,
  ProjectSubmissionCandidate,
  ProjectSubmissionOutcome,
} from "../../../src/features/project-workspace/model";


const PROJECT_TITLE = "Compare investment choices";
const PROJECT_CHARTER =
  "Compare educational evidence with explicit limits and without making an investment recommendation.";
const FIRST_NOTE_TITLE = "Café comparison purpose Σ";
const SECOND_NOTE_TITLE = "Risk, return, costs, liquidity, and source quality";
const LATER_NOTE_TITLE = "Evidence after the first checkpoint";
const ARTIFACT_NAME = "risk-return-evidence-Σ.csv";
const ARTIFACT_BYTES = Buffer.from(
  "choice,risk,return,cost,liquidity\nA,variable,uncertain,low,daily\nB,variable,uncertain,medium,monthly\n",
  "utf-8",
);
const ARTIFACT_DIGEST = createHash("sha256").update(ARTIFACT_BYTES).digest("hex");

function projectApi(projectId: string) {
  return `/api/v1/projects/${encodeURIComponent(projectId)}`;
}

function snapshotSummary(snapshot: ProjectSnapshot) {
  return {
    snapshot_id: snapshot.snapshot_id,
    snapshot_digest: snapshot.snapshot_digest,
    workspace_revision: snapshot.snapshot.workspace_revision,
    closed_at: snapshot.closed_at,
  };
}

function projectSummary(project: ProjectShell) {
  if (project.origin.origin_type !== "learning") throw new Error("Expected a learning Project.");
  return {
    schema_version: project.schema_version,
    project_id: project.project_id,
    title: project.title,
    revision: project.revision,
    origin: project.origin,
  };
}

function evidenceWithoutLearner(evidence: ProjectCompletionEvidence) {
  const { learner_id: _learnerId, ...safe } = evidence;
  return safe;
}

function outcomeWithoutLearner(outcome: ProjectSubmissionOutcome) {
  return {
    validation: outcome.validation,
    evidence: outcome.evidence ? evidenceWithoutLearner(outcome.evidence) : null,
  };
}

async function saveNote(page: Page, title: string, body: string) {
  const form = page.getByRole("group", { name: "Add a note" });
  await form.getByLabel("Note title").fill(title);
  await form.getByLabel("Note", { exact: true }).fill(body);
  const response = page.waitForResponse(
    (item: { url(): string; request(): { method(): string } }) =>
      new URL(item.url()).pathname.endsWith("/workspace/mutations")
      && item.request().method() === "POST",
  );
  await form.getByRole("button", { name: "Save note" }).click();
  expect((await response).status()).toBe(200);
  await expect(page.getByRole("heading", { level: 3, name: title })).toBeVisible();
}

test("preserves Project learning submissions through browser, headless, and retained history", async ({
  context,
  page,
}) => {
  await page.goto("/projects");
  await expect(page.getByRole("heading", { level: 1, name: "Projects" })).toBeVisible();
  const sameOriginHeaders = {
    Origin: new URL(page.url()).origin,
    "Sec-Fetch-Site": "same-origin",
  };
  const sessionResponse = await context.request.post("/api/v1/session/single-profile", {
    data: { limitation_acknowledged: true },
    headers: sameOriginHeaders,
  });
  expect([200, 201]).toContain(sessionResponse.status());

  await page.getByRole("link", { name: "Start project" }).click();
  await expect(page.getByRole("heading", { level: 1, name: `Start ${PROJECT_TITLE}` })).toBeVisible();
  await page.getByLabel("What do you want this Project to accomplish?").fill(PROJECT_CHARTER);
  const createResponse = page.waitForResponse(
    (response) => new URL(response.url()).pathname === "/api/v1/projects"
      && response.request().method() === "POST",
  );
  await page.getByRole("button", { name: "Create Project" }).click();
  expect((await createResponse).status()).toBe(200);
  await expect(page.getByRole("heading", { level: 1, name: PROJECT_TITLE })).toBeVisible();

  const projectId = decodeURIComponent(new URL(page.url()).pathname.split("/").at(-1) ?? "");
  expect(projectId).toMatch(/^[a-z0-9][a-z0-9._-]{0,127}$/);
  const api = projectApi(projectId);

  await saveNote(
    page,
    FIRST_NOTE_TITLE,
    "Define the educational purpose, scope, and limits before comparing evidence.",
  );
  await saveNote(
    page,
    SECOND_NOTE_TITLE,
    "Compare the same categories for each choice and identify source-quality limits.",
  );

  const sourceForm = page.getByRole("group", { name: "Add a source" });
  await sourceForm.getByLabel("Source title").fill("Reviewed educational source");
  await sourceForm.getByLabel("Secure web address").fill("https://example.com/education/risk-return");
  await sourceForm.getByLabel("Publisher or source").fill("Example education publisher");
  const sourceResponse = page.waitForResponse(
    (response) => new URL(response.url()).pathname === `${api}/workspace/mutations`
      && response.request().method() === "POST",
  );
  await sourceForm.getByRole("button", { name: "Save source" }).click();
  expect((await sourceResponse).status()).toBe(200);

  const fileForm = page.getByRole("group", { name: "Add a file" });
  await fileForm.getByLabel("File", { exact: true }).setInputFiles({
    name: ARTIFACT_NAME,
    mimeType: "text/csv",
    buffer: ARTIFACT_BYTES,
  });
  await fileForm.getByLabel("What does this file contain?").selectOption("dataset");
  await fileForm.getByLabel("File format").selectOption("text/csv");
  await fileForm.getByLabel("Where did it come from?").selectOption("learner_created");
  await fileForm.getByLabel("Source title").fill("Browser qualification evidence");
  const artifactResponse = page.waitForResponse(
    (response) => new URL(response.url()).pathname === `${api}/artifacts`
      && response.request().method() === "POST",
  );
  await fileForm.getByRole("button", { name: "Add file" }).click();
  expect((await artifactResponse).status()).toBe(200);

  const firstSnapshotResponse = page.waitForResponse(
    (response) => new URL(response.url()).pathname === `${api}/snapshots`
      && response.request().method() === "POST",
  );
  await page.getByRole("button", { name: "Save checkpoint" }).click();
  expect((await firstSnapshotResponse).status()).toBe(200);
  const firstSnapshotsResponse = await context.request.get(`${api}/snapshots`);
  const firstSnapshots = (await firstSnapshotsResponse.json()) as { records: ProjectSnapshot[] };
  expect(firstSnapshots.records).toHaveLength(1);
  const firstSnapshot = firstSnapshots.records[0]!;
  const firstCandidateResponse = await context.request.get(
    `${api}/snapshots/${encodeURIComponent(firstSnapshot.snapshot_id)}/submission-candidate`,
  );
  expect(firstCandidateResponse.status()).toBe(200);
  const firstCandidate = (await firstCandidateResponse.json()) as ProjectSubmissionCandidate;
  expect(firstCandidate.resources.length).toBeGreaterThanOrEqual(4);
  expect(firstCandidate.milestones).toHaveLength(2);

  await page.getByRole("link", { name: "Submit for learning" }).click();
  const firstMilestones = page.locator("fieldset.project-submission-milestone");
  await expect(firstMilestones).toHaveCount(2);
  await firstMilestones.nth(0).getByRole("checkbox").nth(0).check();
  await page.getByRole("button", { name: "Submit checkpoint" }).click();
  const correctionHeading = page.getByRole("heading", { name: "Checkpoint not submitted" });
  await expect(correctionHeading).toBeFocused();
  await expect(page.getByText(/Choose at least one saved item for every milestone/i)).toBeVisible();
  await expect(firstMilestones.nth(0).getByRole("checkbox").nth(0)).toBeChecked();
  await firstMilestones.nth(1).getByRole("checkbox").nth(1).check();

  const firstSubmissionResponse = page.waitForResponse(
    (response) => new URL(response.url()).pathname.endsWith("/submissions")
      && response.request().method() === "POST",
  );
  await page.getByRole("button", { name: "Submit checkpoint" }).click();
  const firstSubmitted = await firstSubmissionResponse;
  expect(firstSubmitted.status()).toBe(200);
  const firstIntent = firstSubmitted.request().postDataJSON() as Record<string, unknown>;
  const firstOutcome = (await firstSubmitted.json()) as ProjectSubmissionOutcome;
  expect(firstOutcome.validation.status).toBe("accepted");
  await expect(page.getByRole("heading", { name: "Submitted checkpoint" })).toBeVisible();

  const firstEndpoint = `${api}/snapshots/${encodeURIComponent(firstSnapshot.snapshot_id)}/submissions`;
  const exactReplayResponse = await context.request.post(firstEndpoint, {
    data: firstIntent,
    headers: sameOriginHeaders,
  });
  expect(exactReplayResponse.status()).toBe(200);
  const exactReplay = (await exactReplayResponse.json()) as ProjectSubmissionOutcome;
  expect(exactReplay).toEqual(firstOutcome);
  const changedIntent = structuredClone(firstIntent) as {
    milestone_evidence: Array<{ resources: unknown[] }>;
  } & Record<string, unknown>;
  changedIntent.milestone_evidence[1]!.resources = [firstCandidate.resources[0]!];
  const changedReplayResponse = await context.request.post(firstEndpoint, {
    data: changedIntent,
    headers: sameOriginHeaders,
  });
  expect(changedReplayResponse.status()).toBe(409);
  const changedReplay = await changedReplayResponse.json();
  expect(changedReplay).toEqual(expect.objectContaining({ code: "conflict", error_version: "1.0" }));

  await page.getByRole("link", { name: "Return to Project" }).click();
  await saveNote(
    page,
    LATER_NOTE_TITLE,
    "The live workspace continues while the accepted first checkpoint remains fixed.",
  );
  const secondSnapshotResponse = page.waitForResponse(
    (response) => new URL(response.url()).pathname === `${api}/snapshots`
      && response.request().method() === "POST",
  );
  await page.getByRole("button", { name: "Save checkpoint" }).click();
  expect((await secondSnapshotResponse).status()).toBe(200);
  const snapshotsResponse = await context.request.get(`${api}/snapshots`);
  const snapshots = (await snapshotsResponse.json()) as { records: ProjectSnapshot[] };
  expect(snapshots.records).toHaveLength(2);
  const secondSnapshot = snapshots.records[1]!;
  expect(secondSnapshot.snapshot_id).not.toBe(firstSnapshot.snapshot_id);
  const secondCandidateResponse = await context.request.get(
    `${api}/snapshots/${encodeURIComponent(secondSnapshot.snapshot_id)}/submission-candidate`,
  );
  expect(secondCandidateResponse.status()).toBe(200);
  const secondCandidate = (await secondCandidateResponse.json()) as ProjectSubmissionCandidate;
  expect(secondCandidate.resources.length).toBeGreaterThan(firstCandidate.resources.length);

  await page.getByRole("link", { name: "Submit for learning" }).last().click();
  const secondMilestones = page.locator("fieldset.project-submission-milestone");
  await secondMilestones.nth(0).getByRole("checkbox").first().check();
  await secondMilestones.nth(1).getByRole("checkbox").last().check();
  const secondSubmissionResponse = page.waitForResponse(
    (response) => new URL(response.url()).pathname.endsWith("/submissions")
      && response.request().method() === "POST",
  );
  await page.getByRole("button", { name: "Submit checkpoint" }).click();
  const secondSubmitted = await secondSubmissionResponse;
  expect(secondSubmitted.status()).toBe(200);
  const secondIntent = secondSubmitted.request().postDataJSON() as Record<string, unknown>;
  const secondOutcome = (await secondSubmitted.json()) as ProjectSubmissionOutcome;
  expect(secondOutcome.validation.status).toBe("accepted");
  expect(secondOutcome.evidence?.supersedes_submission_id).toBe(firstOutcome.evidence?.submission_id);
  await expect(page.getByRole("heading", { name: "Submitted checkpoint" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Accepted checkpoints" })).toBeVisible();
  await expect(page.getByRole("link", { name: "Open submitted evidence" })).toHaveCount(2);
  await expect(page.getByText(/does not grade its quality, show mastery, or provide financial advice/i)).toBeVisible();
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);

  const projectResponse = await context.request.get(api);
  const historyResponse = await context.request.get(`${api}/submissions`);
  const completionResponse = await context.request.get(`${api}/completion`);
  const firstEvidenceResponse = await context.request.get(
    `${api}/submissions/${encodeURIComponent(firstOutcome.evidence!.submission_id)}`,
  );
  const secondEvidenceResponse = await context.request.get(
    `${api}/submissions/${encodeURIComponent(secondOutcome.evidence!.submission_id)}`,
  );
  for (const response of [projectResponse, historyResponse, completionResponse, firstEvidenceResponse, secondEvidenceResponse]) {
    expect(response.status()).toBe(200);
  }
  const project = (await projectResponse.json()) as ProjectShell;
  const history = (await historyResponse.json()) as ProjectCompletionHistory;
  const completion = (await completionResponse.json()) as ProjectActivityCompletion;
  const firstEvidence = (await firstEvidenceResponse.json()) as ProjectCompletionEvidence;
  const secondEvidence = (await secondEvidenceResponse.json()) as ProjectCompletionEvidence;
  expect(firstEvidence).toEqual(firstOutcome.evidence);
  expect(secondEvidence).toEqual(secondOutcome.evidence);
  expect(history.items.map((item) => item.occurrence)).toEqual([1, 2]);
  expect(completion.completed).toBe(true);
  expect(completion.completion_meaning).toBe("bounded_project_activity_completed");
  expect(completion.history).toHaveLength(2);

  await page.goto("/projects");
  await page.getByRole("link", { name: "Create independent project" }).click();
  await page.getByLabel("Project title").fill("Independent denial qualification");
  await page
    .getByLabel("What do you want this Project to accomplish?")
    .fill("Prove that an independent Project cannot gain learning evidence.");
  await page.getByRole("button", { name: "Create Project" }).click();
  const independentProjectId = decodeURIComponent(
    new URL(page.url()).pathname.split("/").at(-1) ?? "",
  );
  expect(independentProjectId).toMatch(/^[a-z0-9][a-z0-9._-]{0,127}$/);
  await page.goto(`/projects/${encodeURIComponent(independentProjectId)}/learning`);
  await expect(page.getByRole("heading", { name: "Project not found" })).toBeVisible();
  await expect(page.locator("main")).not.toContainText(/learning record|accepted checkpoint|submit for learning/i);

  const capturePath = process.env.FINANCIAL_AI_ACADEMY_PROJECT_LEARNING_CAPTURE;
  if (capturePath) {
    await writeFile(
      capturePath,
      `${JSON.stringify({
        project: projectSummary(project),
        independent_project_id: independentProjectId,
        artifact_sha256: ARTIFACT_DIGEST,
        snapshots: snapshots.records.map(snapshotSummary),
        candidates: [firstCandidate, secondCandidate],
        submission_intents: [firstIntent, secondIntent],
        outcomes: [outcomeWithoutLearner(firstOutcome), outcomeWithoutLearner(secondOutcome)],
        exact_replay: outcomeWithoutLearner(exactReplay),
        changed_retry_denial: {
          status: changedReplayResponse.status(),
          document: changedReplay,
        },
        history,
        completion,
        evidence: [evidenceWithoutLearner(firstEvidence), evidenceWithoutLearner(secondEvidence)],
      }, null, 2)}\n`,
      { encoding: "utf-8", flag: "wx" },
    );
  }
});

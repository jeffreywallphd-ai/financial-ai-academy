import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";
import { createHash } from "node:crypto";
import { readFile, writeFile } from "node:fs/promises";

import type {
  ProjectEvidenceExportBundle,
  ProjectShell,
  ProjectSnapshot,
  ProjectWorkspace,
} from "../../../src/features/project-workspace/model";
import {
  projectEvidenceExportBindingsAreSafe,
  projectEvidenceExportBundleIsSafe,
} from "../../../src/features/project-workspace/model";


const PROJECT_TITLE = "Unicode evidence Project";
const PROJECT_CHARTER =
  "Preserve exact, downloadable educational evidence without making an investment recommendation.";
const FIRST_NOTE_TITLE = "Café Σίσυφος Straße İ";
const FIRST_NOTE_BODY = "Compare the exact educational evidence before drawing a conclusion.";
const LATER_NOTE_TITLE = "Work after the checkpoint";
const ARTIFACT_NAME = "Résumé-Σ-data.csv";
const ARTIFACT_BYTES = Buffer.from("scenario,value\nbase,1\n", "utf-8");
const ARTIFACT_DIGEST = createHash("sha256").update(ARTIFACT_BYTES).digest("hex");
const NAVIGATION_API =
  "/api/v1/adaptation/curricula/investing-foundations/versions/1.0.0/navigation-state";
const PRACTICE_PROGRESS_API =
  "/api/v1/curriculum/placements/intro-risk-return-practice/practice/progress";

function projectApi(projectId: string) {
  return `/api/v1/projects/${encodeURIComponent(projectId)}`;
}

function stableExport(bundle: ProjectEvidenceExportBundle) {
  return {
    schemaVersion: bundle.manifest.schema_version,
    exportDigest: bundle.manifest.export_digest,
    export: bundle.manifest.export,
    files: bundle.files,
  };
}

function stableNavigation(value: unknown) {
  if (typeof value !== "object" || value === null || Array.isArray(value)) return value;
  return Object.fromEntries(
    Object.entries(value).filter(
      ([key]) => key !== "evaluated_at" && key !== "projection_digest",
    ),
  );
}

test("preserves an independent Project workspace through the live public API", async ({
  context,
  page,
}) => {
  await page.goto("/projects");
  await expect(page.getByRole("heading", { level: 1, name: "Projects" })).toBeVisible();
  const sessionResponse = await context.request.post(
    "/api/v1/session/single-profile",
    {
      data: { limitation_acknowledged: true },
      headers: {
        Origin: new URL(page.url()).origin,
        "Sec-Fetch-Site": "same-origin",
      },
    },
  );
  expect([200, 201]).toContain(sessionResponse.status());
  const navigationBeforeResponse = await context.request.get(NAVIGATION_API);
  const practiceBeforeResponse = await context.request.get(PRACTICE_PROGRESS_API);
  expect(navigationBeforeResponse.status()).toBe(200);
  expect(practiceBeforeResponse.status()).toBe(200);
  const navigationBefore = await navigationBeforeResponse.json();
  const practiceBefore = await practiceBeforeResponse.json();
  await page.getByRole("link", { name: "Create independent project" }).click();
  await page.getByLabel("Project title").fill(PROJECT_TITLE);
  await page
    .getByLabel("What do you want this Project to accomplish?")
    .fill(PROJECT_CHARTER);
  const createResponse = page.waitForResponse(
    (response) =>
      new URL(response.url()).pathname === "/api/v1/projects" &&
      response.request().method() === "POST",
  );
  await page.getByRole("button", { name: "Create Project" }).click();
  expect((await createResponse).status()).toBe(200);
  await expect(page.getByRole("heading", { level: 1, name: PROJECT_TITLE })).toBeVisible();

  const projectId = decodeURIComponent(new URL(page.url()).pathname.split("/").at(-1) ?? "");
  expect(projectId).toMatch(/^[a-z0-9][a-z0-9._-]{0,127}$/);
  const api = projectApi(projectId);

  await page.getByLabel("Note title").fill(FIRST_NOTE_TITLE);
  await page.getByLabel("Note", { exact: true }).fill(FIRST_NOTE_BODY);
  const noteResponse = page.waitForResponse(
    (response) =>
      new URL(response.url()).pathname === `${api}/workspace/mutations` &&
      response.request().method() === "POST",
  );
  await page.getByRole("button", { name: "Save note" }).click();
  expect((await noteResponse).status()).toBe(200);
  await expect(page.getByRole("heading", { level: 3, name: FIRST_NOTE_TITLE })).toBeVisible();

  const sourceForm = page.getByRole("group", { name: "Add a source" });
  await sourceForm.getByLabel("Source title").fill("Reviewed learning source");
  await sourceForm.getByLabel("Secure web address").fill("https://example.com/learning/evidence");
  await sourceForm.getByLabel("Publisher or source").fill("Example education publisher");
  const sourceResponse = page.waitForResponse(
    (response) =>
      new URL(response.url()).pathname === `${api}/workspace/mutations` &&
      response.request().method() === "POST",
  );
  await sourceForm.getByRole("button", { name: "Save source" }).click();
  expect((await sourceResponse).status()).toBe(200);
  await expect(page.getByRole("heading", { level: 3, name: "Reviewed learning source" })).toBeVisible();

  const fileForm = page.getByRole("group", { name: "Add a file" });
  await fileForm.getByLabel("File", { exact: true }).setInputFiles({
    name: ARTIFACT_NAME,
    mimeType: "text/csv",
    buffer: ARTIFACT_BYTES,
  });
  await fileForm.getByLabel("What does this file contain?").selectOption("dataset");
  await fileForm.getByLabel("File format").selectOption("text/csv");
  await fileForm.getByLabel("Where did it come from?").selectOption("learner_created");
  await fileForm.getByLabel("Source title").fill("Browser qualification dataset");
  const artifactResponse = page.waitForResponse(
    (response) =>
      new URL(response.url()).pathname === `${api}/artifacts` &&
      response.request().method() === "POST",
  );
  await fileForm.getByRole("button", { name: "Add file" }).click();
  expect((await artifactResponse).status()).toBe(200);
  await expect(page.getByRole("heading", { level: 3, name: ARTIFACT_NAME })).toBeVisible();

  const artifactDownload = page.waitForEvent("download");
  await page.getByRole("button", { name: "Download original file" }).click();
  const downloadedArtifact = await artifactDownload;
  expect(downloadedArtifact.suggestedFilename()).toBe(ARTIFACT_NAME);
  expect(await readFile(await downloadedArtifact.path())).toEqual(ARTIFACT_BYTES);
  await expect(page.getByText("Your download is ready.")).toBeVisible();

  const snapshotResponse = page.waitForResponse(
    (response) =>
      new URL(response.url()).pathname === `${api}/snapshots` &&
      response.request().method() === "POST",
  );
  await page.getByRole("button", { name: "Save checkpoint" }).click();
  const closedSnapshotResponse = await snapshotResponse;
  expect(closedSnapshotResponse.status(), await closedSnapshotResponse.text()).toBe(200);
  await expect(page.getByRole("heading", { name: /^Checkpoint from / })).toBeVisible();

  const projectResponse = await context.request.get(api);
  const workspaceAtSnapshotResponse = await context.request.get(`${api}/workspace`);
  const snapshotsResponse = await context.request.get(`${api}/snapshots`);
  expect(projectResponse.status()).toBe(200);
  expect(workspaceAtSnapshotResponse.status()).toBe(200);
  expect(snapshotsResponse.status()).toBe(200);
  const project = (await projectResponse.json()) as ProjectShell;
  const workspaceAtSnapshot = (await workspaceAtSnapshotResponse.json()) as ProjectWorkspace;
  const snapshots = (await snapshotsResponse.json()) as { records: ProjectSnapshot[] };
  expect(snapshots.records).toHaveLength(1);
  const snapshot = snapshots.records[0]!;
  const directExportResponse = await context.request.get(
    `${api}/snapshots/${encodeURIComponent(snapshot.snapshot_id)}/export`,
  );
  expect(directExportResponse.status()).toBe(200);
  const directExport = (await directExportResponse.json()) as ProjectEvidenceExportBundle;
  expect(projectEvidenceExportBundleIsSafe(directExport, projectId, snapshot.snapshot_id)).toBe(true);
  expect(await projectEvidenceExportBindingsAreSafe(directExport)).toBe(true);

  const evidenceDownload = page.waitForEvent("download");
  await page.getByRole("button", { name: "Download evidence record" }).click();
  const downloadedEvidence = await evidenceDownload;
  const browserExport = JSON.parse(
    await readFile(await downloadedEvidence.path(), "utf-8"),
  ) as ProjectEvidenceExportBundle;
  expect(browserExport.manifest.export.snapshot_id).toBe(snapshot.snapshot_id);
  expect(browserExport.manifest.export.workspace_record).toEqual(workspaceAtSnapshot);
  expect(browserExport.files).toHaveLength(1);
  expect(browserExport.files[0]?.content_base64).toBe(ARTIFACT_BYTES.toString("base64"));
  await expect(page.getByText("Your download is ready.")).toBeVisible();

  await page.getByLabel("Note title").last().fill(LATER_NOTE_TITLE);
  await page.getByLabel("Note", { exact: true }).last().fill("The live workspace can continue without changing its fixed checkpoint.");
  const laterNoteResponse = page.waitForResponse(
    (response) =>
      new URL(response.url()).pathname === `${api}/workspace/mutations` &&
      response.request().method() === "POST",
  );
  await page.getByRole("button", { name: "Save note" }).last().click();
  expect((await laterNoteResponse).status()).toBe(200);
  await expect(page.getByRole("heading", { level: 3, name: LATER_NOTE_TITLE })).toBeVisible();

  const currentWorkspaceResponse = await context.request.get(`${api}/workspace`);
  const snapshotDetailResponse = await context.request.get(
    `${api}/snapshots/${encodeURIComponent(snapshot.snapshot_id)}`,
  );
  const exportResponse = await context.request.get(
    `${api}/snapshots/${encodeURIComponent(snapshot.snapshot_id)}/export`,
  );
  expect(currentWorkspaceResponse.status()).toBe(200);
  expect(snapshotDetailResponse.status()).toBe(200);
  expect(exportResponse.status()).toBe(200);
  const currentWorkspace = (await currentWorkspaceResponse.json()) as ProjectWorkspace;
  const snapshotDetail = (await snapshotDetailResponse.json()) as ProjectSnapshot;
  const headlessExport = (await exportResponse.json()) as ProjectEvidenceExportBundle;
  expect(currentWorkspace.workspace_revision).toBeGreaterThan(workspaceAtSnapshot.workspace_revision);
  expect(snapshotDetail).toEqual(snapshot);
  expect(stableExport(headlessExport)).toEqual(stableExport(browserExport));
  expect(currentWorkspace.notes.map((note) => note.title)).toEqual([
    FIRST_NOTE_TITLE,
    LATER_NOTE_TITLE,
  ]);
  expect(currentWorkspace.artifacts[0]?.content_digest).toBe(ARTIFACT_DIGEST);
  const navigationAfterResponse = await context.request.get(NAVIGATION_API);
  const practiceAfterResponse = await context.request.get(PRACTICE_PROGRESS_API);
  expect(navigationAfterResponse.status()).toBe(200);
  expect(practiceAfterResponse.status()).toBe(200);
  const navigationAfter = await navigationAfterResponse.json();
  const practiceAfter = await practiceAfterResponse.json();
  expect(stableNavigation(navigationAfter)).toEqual(stableNavigation(navigationBefore));
  expect(practiceAfter).toEqual(practiceBefore);
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);

  const capturePath = process.env.FINANCIAL_AI_ACADEMY_PROJECT_CAPTURE;
  if (capturePath) {
    await writeFile(
      capturePath,
      `${JSON.stringify(
        {
          project,
          workspace_at_snapshot: workspaceAtSnapshot,
          current_workspace: currentWorkspace,
          snapshot,
          export_bundle: browserExport,
          artifact_sha256: ARTIFACT_DIGEST,
          learning_state_before: {
            navigation: stableNavigation(navigationBefore),
            practice_progress: practiceBefore,
          },
          learning_state_after: {
            navigation: stableNavigation(navigationAfter),
            practice_progress: practiceAfter,
          },
        },
        null,
        2,
      )}\n`,
      { encoding: "utf-8", flag: "wx" },
    );
  }
});

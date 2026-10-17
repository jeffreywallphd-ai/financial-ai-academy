import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";
import { readFile, writeFile } from "node:fs/promises";

import type { PersonalWorkspace } from "../../../src/features/personal-workspace/model";
import type {
  ProjectShell,
  ProjectSnapshot,
  ProjectWorkspace,
} from "../../../src/features/project-workspace/model";


const LESSON_PLACEMENT = "intro-risk-return-primary";
const SAVE_LESSON_PATH =
  `/saved-learning/new?kind=lesson&placement=${LESSON_PLACEMENT}` +
  `&return=%2Flearn%2Fplacements%2F${LESSON_PLACEMENT}`;
const WORKSPACE_API = "/api/v1/personal-workspace";
const MUTATION_API = "/api/v1/personal-workspace/mutations";
const NOTE_TITLE = "Café risk and return notes";
const NOTE_BODY = "Uncertainty and potential reward are related, but neither promises an outcome.";
const BOOKMARK_LABEL = "Review risk and return Σ";
const COLLECTION_TITLE = "Foundations İ";
const PROJECT_NOTE_TITLE = "Project workspace reminders";
const PROJECT_NOTE_BODY = "Keep this Project source connected without copying its working files.";
const SNAPSHOT_LABEL = "Fixed Project checkpoint";
const ARTIFACT_LABEL = "Project dataset record";

type ProjectCapture = {
  project: ProjectShell;
  current_workspace: ProjectWorkspace;
  snapshot: ProjectSnapshot;
};

async function loadProjectCapture(): Promise<ProjectCapture> {
  const capturePath = process.env.FINANCIAL_AI_ACADEMY_PROJECT_CAPTURE;
  if (!capturePath) throw new Error("The live Project capture path is unavailable.");
  return JSON.parse(await readFile(capturePath, "utf-8")) as ProjectCapture;
}

test("preserves Saved learning through the live public API", async ({
  context,
  page,
}) => {
  const projectCapture = await loadProjectCapture();
  const projectId = projectCapture.project.project_id;
  const snapshotId = projectCapture.snapshot.snapshot_id;
  const artifact = projectCapture.current_workspace.artifacts[0];
  if (!artifact) throw new Error("The live Project has no inert file manifest.");

  await page.goto("/saved-learning");
  await expect(page.getByRole("heading", { level: 1, name: "Saved learning" })).toBeVisible();
  await expect(page.getByText("You have not saved any learning yet.")).toBeVisible();

  await page.goto(SAVE_LESSON_PATH);
  await expect(page.getByRole("heading", { level: 1, name: "Save this lesson" })).toBeVisible();
  await page.getByLabel("Note title").fill(NOTE_TITLE);
  await page.getByLabel("Note", { exact: true }).fill(NOTE_BODY);
  const noteResponse = page.waitForResponse(
    (response) =>
      new URL(response.url()).pathname === MUTATION_API &&
      response.request().method() === "POST",
  );
  await page.getByRole("button", { name: "Save note" }).click();
  expect((await noteResponse).status()).toBe(200);
  await expect(page).toHaveURL(/\/saved-learning$/);
  await expect(page.getByRole("heading", { level: 3, name: NOTE_TITLE })).toBeVisible();

  await page.goto(SAVE_LESSON_PATH);
  await page.getByLabel("Personal label").fill(BOOKMARK_LABEL);
  const bookmarkResponse = page.waitForResponse(
    (response) =>
      new URL(response.url()).pathname === MUTATION_API &&
      response.request().method() === "POST",
  );
  await page.getByRole("button", { name: "Save bookmark" }).click();
  expect((await bookmarkResponse).status()).toBe(200);
  await expect(page.getByRole("heading", { level: 3, name: BOOKMARK_LABEL })).toBeVisible();

  await page.goto(`/projects/${encodeURIComponent(projectId)}`);
  const projectSaveLink = page.getByRole("link", { name: "Save Project to Saved learning" });
  await expect(projectSaveLink).toHaveAttribute(
    "href",
    `/saved-learning/new?kind=project_workspace&project=${encodeURIComponent(projectId)}`,
  );
  await projectSaveLink.click();
  await expect(page.getByRole("heading", { level: 1, name: "Save this Project" })).toBeVisible();
  await page.getByLabel("Note title").fill(PROJECT_NOTE_TITLE);
  await page.getByLabel("Note", { exact: true }).fill(PROJECT_NOTE_BODY);
  const projectNoteResponse = page.waitForResponse(
    (response) =>
      new URL(response.url()).pathname === MUTATION_API &&
      response.request().method() === "POST",
  );
  await page.getByRole("button", { name: "Save note" }).click();
  expect((await projectNoteResponse).status()).toBe(200);
  await expect(page.getByRole("heading", { level: 3, name: PROJECT_NOTE_TITLE })).toBeVisible();

  await page.goto(`/projects/${encodeURIComponent(projectId)}`);
  const checkpointSaveLink = page.getByRole("link", {
    name: "Save checkpoint to Saved learning",
  });
  await expect(checkpointSaveLink).toHaveAttribute(
    "href",
    `/saved-learning/new?kind=project_snapshot&project=${encodeURIComponent(projectId)}&snapshot=${encodeURIComponent(snapshotId)}`,
  );
  await checkpointSaveLink.click();
  await expect(page.getByRole("heading", { level: 1, name: "Save this checkpoint" })).toBeVisible();
  await page.getByLabel("Personal label").fill(SNAPSHOT_LABEL);
  const snapshotBookmarkResponse = page.waitForResponse(
    (response) =>
      new URL(response.url()).pathname === MUTATION_API &&
      response.request().method() === "POST",
  );
  await page.getByRole("button", { name: "Save bookmark" }).click();
  expect((await snapshotBookmarkResponse).status()).toBe(200);
  await expect(page.getByRole("heading", { level: 3, name: SNAPSHOT_LABEL })).toBeVisible();

  await page.goto(`/projects/${encodeURIComponent(projectId)}`);
  const artifactSaveLink = page.getByRole("link", { name: "Save file to Saved learning" });
  await expect(artifactSaveLink).toHaveAttribute(
    "href",
    `/saved-learning/new?kind=project_artifact&project=${encodeURIComponent(projectId)}&artifact=${encodeURIComponent(artifact.artifact_id)}&version=${artifact.artifact_version}`,
  );
  await artifactSaveLink.click();
  await expect(page.getByRole("heading", { level: 1, name: "Save this file record" })).toBeVisible();
  await page.getByLabel("Personal label").fill(ARTIFACT_LABEL);
  const artifactBookmarkResponse = page.waitForResponse(
    (response) =>
      new URL(response.url()).pathname === MUTATION_API &&
      response.request().method() === "POST",
  );
  await page.getByRole("button", { name: "Save bookmark" }).click();
  expect((await artifactBookmarkResponse).status()).toBe(200);
  await expect(page.getByRole("heading", { level: 3, name: ARTIFACT_LABEL })).toBeVisible();

  const bookmarkCard = page
    .getByRole("heading", { level: 3, name: BOOKMARK_LABEL })
    .locator("xpath=ancestor::li");
  await bookmarkCard.getByRole("button", { name: "Move earlier" }).click();
  await expect(page.locator(".saved-learning-list > li").first()).toContainText(BOOKMARK_LABEL);

  await page.getByLabel("Collection name").first().fill(COLLECTION_TITLE);
  await page.getByRole("button", { name: "Create collection" }).click();
  const collection = page
    .getByRole("heading", { level: 3, name: COLLECTION_TITLE })
    .locator("xpath=ancestor::section[1]");
  await collection.getByRole("checkbox", { name: NOTE_TITLE }).check();
  await collection.getByRole("checkbox", { name: BOOKMARK_LABEL }).check();
  await collection.getByRole("checkbox", { name: PROJECT_NOTE_TITLE }).check();
  await collection.getByRole("checkbox", { name: SNAPSHOT_LABEL }).check();
  await collection.getByRole("checkbox", { name: ARTIFACT_LABEL }).check();
  await collection
    .getByRole("button", { name: `Move ${BOOKMARK_LABEL} earlier in collection` })
    .click();
  await collection.getByRole("button", { name: "Save collection items" }).click();

  const noteCard = page
    .getByRole("heading", { level: 3, name: NOTE_TITLE })
    .locator("xpath=ancestor::li");
  await noteCard.getByRole("button", { name: "Archive record" }).click();
  await expect(noteCard.getByText("Note · Archived", { exact: true })).toBeVisible();
  const restoreResponse = page.waitForResponse(
    (response) =>
      new URL(response.url()).pathname === MUTATION_API &&
      response.request().method() === "POST",
  );
  await noteCard.getByRole("button", { name: "Restore record" }).click();
  const acceptedRestore = await restoreResponse;
  expect(acceptedRestore.status()).toBe(200);
  const replayRequest = acceptedRestore.request().postDataJSON();
  const acceptedWorkspace = (await acceptedRestore.json()) as PersonalWorkspace;

  await page.reload();
  await expect(page.getByRole("heading", { level: 3, name: NOTE_TITLE })).toBeVisible();
  await expect(page.getByRole("heading", { level: 3, name: BOOKMARK_LABEL })).toBeVisible();
  await expect(page.getByRole("heading", { level: 3, name: PROJECT_NOTE_TITLE })).toBeVisible();
  await expect(page.getByRole("heading", { level: 3, name: SNAPSHOT_LABEL })).toBeVisible();
  await expect(page.getByRole("heading", { level: 3, name: ARTIFACT_LABEL })).toBeVisible();
  const reopenedCollection = page
    .getByRole("heading", { level: 3, name: COLLECTION_TITLE })
    .locator("xpath=ancestor::section[1]");
  await expect(
    reopenedCollection.getByRole("list", {
      name: `Order of saved items in ${COLLECTION_TITLE}`,
    }).getByRole("listitem").first(),
  ).toContainText(BOOKMARK_LABEL);
  const reopenedNote = page
    .getByRole("heading", { level: 3, name: NOTE_TITLE })
    .locator("xpath=ancestor::li");
  await reopenedNote.getByText("Technical record", { exact: true }).click();
  await expect(reopenedNote.getByText(LESSON_PLACEMENT, { exact: true })).toBeVisible();
  const projectNoteCard = page
    .getByRole("heading", { level: 3, name: PROJECT_NOTE_TITLE })
    .locator("xpath=ancestor::li");
  await projectNoteCard.getByText("Technical record", { exact: true }).click();
  await expect(projectNoteCard.getByText(projectId, { exact: true })).toBeVisible();
  const snapshotCard = page
    .getByRole("heading", { level: 3, name: SNAPSHOT_LABEL })
    .locator("xpath=ancestor::li");
  await snapshotCard.getByText("Technical record", { exact: true }).click();
  await expect(snapshotCard.getByText(snapshotId, { exact: true })).toBeVisible();
  await expect(snapshotCard.getByText(projectCapture.snapshot.snapshot_digest, { exact: true })).toBeVisible();
  const artifactCard = page
    .getByRole("heading", { level: 3, name: ARTIFACT_LABEL })
    .locator("xpath=ancestor::li");
  await artifactCard.getByText("Technical record", { exact: true }).click();
  await expect(artifactCard.getByText(artifact.artifact_id, { exact: true })).toBeVisible();
  await expect(artifactCard.getByText(artifact.content_digest, { exact: true })).toBeVisible();
  await expect(artifactCard.getByRole("button", { name: /download|open|run|preview/i })).toHaveCount(0);

  const currentResponse = await context.request.get(WORKSPACE_API);
  expect(currentResponse.status()).toBe(200);
  const currentWorkspace = (await currentResponse.json()) as PersonalWorkspace;
  expect(currentWorkspace).toEqual(acceptedWorkspace);
  expect(currentWorkspace.records).toHaveLength(5);
  expect(currentWorkspace.records.filter((record) => record.record_kind === "note")).toHaveLength(2);
  expect(currentWorkspace.records.filter((record) => record.record_kind === "bookmark")).toHaveLength(3);
  expect(new Set(currentWorkspace.records.map((record) => record.target.reference_kind))).toEqual(
    new Set(["placed_lesson", "project_workspace", "project_snapshot", "project_artifact"]),
  );
  expect(currentWorkspace.collections[0]?.member_record_ids).toHaveLength(5);
  expect(new Set(currentWorkspace.collections[0]?.member_record_ids)).toEqual(
    new Set(currentWorkspace.records.map((record) => record.record_id)),
  );
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);

  const capturePath = process.env.FINANCIAL_AI_ACADEMY_PERSONAL_WORKSPACE_CAPTURE;
  if (capturePath) {
    await writeFile(
      capturePath,
      `${JSON.stringify(
        {
          workspace: currentWorkspace,
          exact_replay_request: replayRequest,
          expected: {
            note_title: NOTE_TITLE,
            note_body: NOTE_BODY,
            bookmark_label: BOOKMARK_LABEL,
            collection_title: COLLECTION_TITLE,
            placement_id: LESSON_PLACEMENT,
            project_id: projectId,
            project_note_title: PROJECT_NOTE_TITLE,
            project_note_body: PROJECT_NOTE_BODY,
            snapshot_id: snapshotId,
            snapshot_label: SNAPSHOT_LABEL,
            snapshot_digest: projectCapture.snapshot.snapshot_digest,
            artifact_id: artifact.artifact_id,
            artifact_version: artifact.artifact_version,
            artifact_label: ARTIFACT_LABEL,
            artifact_digest: artifact.content_digest,
            artifact_byte_count: artifact.byte_count,
          },
        },
        null,
        2,
      )}\n`,
      { encoding: "utf-8", flag: "wx" },
    );
  }
});

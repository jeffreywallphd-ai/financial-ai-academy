import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";
import { writeFile } from "node:fs/promises";

import type { PersonalWorkspace } from "../../../src/features/personal-workspace/model";


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

test("preserves Saved learning through the live public API", async ({
  context,
  page,
}) => {
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

  const currentResponse = await context.request.get(WORKSPACE_API);
  expect(currentResponse.status()).toBe(200);
  const currentWorkspace = (await currentResponse.json()) as PersonalWorkspace;
  expect(currentWorkspace).toEqual(acceptedWorkspace);
  expect(currentWorkspace.records.map((record) => record.record_kind)).toEqual([
    "bookmark",
    "note",
  ]);
  expect(currentWorkspace.collections[0]?.member_record_ids).toEqual([
    currentWorkspace.records[0]?.record_id,
    currentWorkspace.records[1]?.record_id,
  ]);
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
          },
        },
        null,
        2,
      )}\n`,
      { encoding: "utf-8", flag: "wx" },
    );
  }
});

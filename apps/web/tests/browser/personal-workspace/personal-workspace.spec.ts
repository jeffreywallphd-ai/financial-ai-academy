import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page, type Route } from "@playwright/test";


const provenance = {
  published_by: "Financial AI Academy",
  published_at: "2026-10-17T10:00:00Z",
  content_reviewed_on: "2026-10-17",
  educational_use_notice: "Educational content only.",
};

function json(route: Route, status: number, body: unknown) {
  return route.fulfill({
    status,
    contentType: "application/json",
    body: JSON.stringify(body),
  });
}

function emptyWorkspace() {
  return {
    schema_version: "1.0.0",
    workspace_id: "workspace-one",
    learner_id: "learner-one",
    revision: 1,
    records: [] as Record<string, unknown>[],
    collections: [] as Record<string, unknown>[],
    created_at: "2026-10-17T10:00:00Z",
    updated_at: "2026-10-17T10:00:00Z",
    workspace_digest: "d".repeat(64),
  };
}

async function mockSavedLearning(page: Page, options: {
  firstMutationStatus?: number;
  invalidRead?: boolean;
} = {}) {
  let workspace = emptyWorkspace();
  let mutationCount = 0;
  const posts: Record<string, unknown>[] = [];
  await page.route("**/api/v1/**", async (route) => {
    const request = route.request();
    const url = new URL(request.url());
    if (url.pathname === "/api/v1/session/single-profile") {
      return json(route, 201, { learner_id: "learner-one" });
    }
    if (url.pathname === "/api/v1/personal-workspace" && request.method() === "GET") {
      if (options.invalidRead) {
        return json(route, 200, {
          ...workspace,
          collections: [{
            collection_id: "broken",
            title: "Broken",
            member_record_ids: ["missing"],
            created_at: workspace.created_at,
            updated_at: workspace.updated_at,
          }],
        });
      }
      return json(route, 200, workspace);
    }
    if (url.pathname === "/api/v1/personal-workspace/mutations" && request.method() === "POST") {
      const body = request.postDataJSON() as Record<string, unknown>;
      posts.push(body);
      mutationCount += 1;
      if (mutationCount === 1 && options.firstMutationStatus) {
        return json(route, options.firstMutationStatus, { code: "unavailable" });
      }
      const mutation = body.mutation as Record<string, unknown>;
      const now = `2026-10-17T10:${String(workspace.revision).padStart(2, "0")}:00Z`;
      if (mutation.operation === "create_note") {
        const selector = mutation.selector as Record<string, string>;
        workspace.records.push({
          record_kind: "note",
          record_id: `note-${workspace.revision}`,
          title: mutation.title,
          body: mutation.body,
          archived: false,
          created_at: now,
          updated_at: now,
          target: {
            reference_kind: selector.reference_kind,
            owner_module: "curriculum",
            opportunity_id: selector.opportunity_id,
            placement_id: selector.placement_id,
            package_id: "risk-return-package",
            package_version: "1.0.0",
            package_digest: "a".repeat(64),
            source_fingerprint: "b".repeat(64),
            title: "Risk and return basics",
            destination: `/learn/placements/${selector.placement_id}`,
            target_status: "available",
            validated_at: now,
            provenance,
          },
        });
      } else if (mutation.operation === "update_note") {
        workspace.records = workspace.records.map((record) => record.record_id === mutation.record_id
          ? { ...record, title: mutation.title, body: mutation.body, updated_at: now }
          : record);
      } else if (mutation.operation === "archive_record" || mutation.operation === "restore_record") {
        workspace.records = workspace.records.map((record) => record.record_id === mutation.record_id
          ? { ...record, archived: mutation.operation === "archive_record", updated_at: now }
          : record);
      } else if (mutation.operation === "create_collection") {
        workspace.collections.push({
          collection_id: `collection-${workspace.revision}`,
          title: mutation.title,
          member_record_ids: [],
          created_at: now,
          updated_at: now,
        });
      } else if (mutation.operation === "set_collection_members") {
        workspace.collections = workspace.collections.map((collection) => collection.collection_id === mutation.collection_id
          ? { ...collection, member_record_ids: mutation.member_record_ids, updated_at: now }
          : collection);
      }
      workspace = {
        ...workspace,
        revision: workspace.revision + 1,
        updated_at: now,
        workspace_digest: String(workspace.revision + 1).padStart(64, "0"),
      };
      return json(route, 200, workspace);
    }
    return json(route, 404, { code: "not_found" });
  });
  return { posts, workspace: () => workspace };
}

test("saves, edits, organizes, and reopens learning through the generated public API", async ({ page }) => {
  const mocked = await mockSavedLearning(page);
  await page.goto("/saved-learning/new?kind=opportunity&opportunity=risk-return-basics&placement=risk-return-primary&return=%2Flearn%2Fopportunities%2Frisk-return-basics");
  await expect(page.getByRole("heading", { level: 1, name: "Save this learning opportunity" })).toBeVisible();
  await page.getByLabel("Note title").fill("Risk notes");
  await page.getByLabel("Note", { exact: true }).fill("Uncertainty is not a promise of reward.");
  const create = page.waitForRequest((request) => request.method() === "POST" && new URL(request.url()).pathname.endsWith("/personal-workspace/mutations"));
  await page.getByRole("button", { name: "Save note" }).click();
  const createRequest = await create;

  await expect(page).toHaveURL(/\/saved-learning$/);
  await expect(page.getByRole("heading", { level: 3, name: "Risk notes" })).toBeVisible();
  const createBody = createRequest.postDataJSON() as Record<string, unknown>;
  expect(createBody).not.toHaveProperty("learner_id");
  expect(createBody).not.toHaveProperty("workspace_id");
  expect(createBody.mutation).toEqual({
    operation: "create_note",
    selector: {
      reference_kind: "learning_opportunity",
      opportunity_id: "risk-return-basics",
      placement_id: "risk-return-primary",
    },
    title: "Risk notes",
    body: "Uncertainty is not a promise of reward.",
  });

  const record = page.getByRole("heading", { name: "Risk notes" }).locator("xpath=ancestor::li");
  await record.getByLabel("Note title").fill("Risk notes updated");
  await record.getByRole("button", { name: "Save note changes" }).click();
  await expect(page.getByRole("heading", { level: 3, name: "Risk notes updated" })).toBeVisible();
  await page.getByLabel("Collection name").first().fill("Foundations");
  await page.getByRole("button", { name: "Create collection" }).click();
  await expect(page.getByRole("heading", { level: 3, name: "Foundations" })).toBeVisible();
  const collection = page.getByRole("heading", { name: "Foundations" }).locator("xpath=ancestor::section");
  await collection.getByRole("checkbox", { name: "Risk notes updated" }).check();
  await collection.getByRole("button", { name: "Save collection items" }).click();
  await expect.poll(() => mocked.workspace().collections[0]?.member_record_ids).toEqual(["note-1"]);

  const updatedRecord = page.getByRole("heading", { name: "Risk notes updated" }).locator("xpath=ancestor::li");
  await updatedRecord.getByRole("button", { name: "Archive record" }).click();
  await expect(page.getByText("Note · Archived")).toBeVisible();
  await page.reload();
  await expect(page.getByRole("heading", { level: 3, name: "Risk notes updated" })).toBeVisible();

  await updatedRecord.getByText("Technical record").click();
  await expect(updatedRecord.getByText("risk-return-basics")).toBeVisible();
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  const lightText = await page.locator("main").innerText();
  for (const theme of ["dark", "system"] as const) {
    await page.getByLabel("Theme").selectOption(theme);
    expect(await page.locator("main").innerText()).toBe(lightText);
  }
  expect(new Set(mocked.posts.map((body) => body.idempotency_key)).size).toBe(mocked.posts.length);
});

test("reuses an unchanged request after an uncertain response", async ({ page }) => {
  const mocked = await mockSavedLearning(page, { firstMutationStatus: 503 });
  await page.goto("/saved-learning/new?kind=lesson&placement=cash-flow-primary");
  await page.getByLabel("Note title").fill("Cash flow reminder");
  await page.getByLabel("Note", { exact: true }).fill("Track the movement of cash.");
  await page.getByRole("button", { name: "Save note" }).click();
  await expect(page.getByRole("heading", { name: "Change not confirmed" })).toBeFocused();
  await expect(page.getByLabel("Note title")).toHaveValue("Cash flow reminder");
  await page.getByRole("button", { name: "Save note" }).click();
  await expect(page).toHaveURL(/\/saved-learning$/);
  expect(mocked.posts).toHaveLength(2);
  expect(mocked.posts[1]).toEqual(mocked.posts[0]);
});

test("fails closed for malformed private data and preserves responsive accessible recovery", async ({ page }) => {
  await mockSavedLearning(page, { invalidRead: true });
  await page.setViewportSize({ width: 375, height: 720 });
  await page.goto("/saved-learning");
  await expect(page.getByRole("heading", { name: "Saved learning could not be shown" })).toBeVisible();
  await expect(page.locator("main")).not.toContainText("Broken");
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  const dimensions = await page.evaluate(() => ({
    viewport: document.documentElement.clientWidth,
    content: document.documentElement.scrollWidth,
  }));
  expect(dimensions.content).toBeLessThanOrEqual(dimensions.viewport);
  await page.setViewportSize({ width: 1280, height: 900 });
  await page.addStyleTag({ content: "html { font-size: 200% !important; }" });
  const zoomed = await page.evaluate(() => ({
    viewport: document.documentElement.clientWidth,
    content: document.documentElement.scrollWidth,
  }));
  expect(zoomed.content).toBeLessThanOrEqual(zoomed.viewport);
  await page.emulateMedia({ reducedMotion: "reduce", forcedColors: "active" });
  const recovery = page.getByRole("button", { name: "Return to learning library" });
  await recovery.focus();
  expect(await recovery.evaluate((element) => getComputedStyle(element).outlineStyle)).not.toBe("none");
});

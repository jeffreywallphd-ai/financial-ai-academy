import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page, type Route } from "@playwright/test";

import {
  availableOpportunity,
  learningCatalogFixture,
  learningQueryPageFixture,
} from "../../component/learningCatalogFixture";
import { lessonFixture } from "../../component/lessonFixture";


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

function projectWorkspace() {
  const workspace = emptyWorkspace();
  const target = {
    reference_kind: "project_workspace",
    owner_module: "project",
    project_id: "project.research-1",
    title: "Allocation research",
    lifecycle: "active",
    project_revision: 4,
    workspace_revision: 7,
    destination: "/projects/project.research-1#workspace",
    target_status: "available",
    validated_at: "2026-10-17T10:03:00Z",
  };
  return {
    ...workspace,
    revision: 4,
    records: [
      {
        record_kind: "note",
        record_id: "note-allocation",
        title: "Allocation review",
        body: "Review the allocation assumptions.",
        archived: false,
        created_at: "2026-10-17T10:01:00Z",
        updated_at: "2026-10-17T10:01:00Z",
        target: { ...target, target_status: "stale" },
      },
      {
        record_kind: "bookmark",
        record_id: "bookmark-file",
        label: "Closed file",
        archived: false,
        created_at: "2026-10-17T10:02:00Z",
        updated_at: "2026-10-17T10:02:00Z",
        target: {
          ...target,
          reference_kind: "project_artifact",
          artifact_id: "artifact.inputs-1",
          artifact_version: 3,
          artifact_kind: "dataset",
          logical_path: "evidence/allocation-inputs.csv",
          media_type: "text/csv",
          inspection_mode: "plain_text",
          byte_count: 4096,
          content_digest: "f".repeat(64),
          created_at: "2026-10-17T10:02:00Z",
          destination: "/projects/project.research-1#artifact-artifact.inputs-1-v3",
          target_status: "unavailable",
        },
      },
      {
        record_kind: "bookmark",
        record_id: "bookmark-project",
        label: "Project overview",
        archived: true,
        created_at: "2026-10-17T10:03:00Z",
        updated_at: "2026-10-17T10:03:00Z",
        target,
      },
    ],
    updated_at: "2026-10-17T10:03:00Z",
    workspace_digest: "4".padStart(64, "0"),
  };
}

async function mockSavedLearning(page: Page, options: {
  applyFirstMutationBeforeFailure?: boolean;
  firstMutationCode?: string;
  firstMutationStatus?: number;
  initialWorkspace?: ReturnType<typeof emptyWorkspace>;
  invalidRead?: boolean;
  readStatus?: number;
  refreshStatus?: "available" | "stale" | "unavailable";
} = {}) {
  let workspace = structuredClone(options.initialWorkspace ?? emptyWorkspace());
  let mutationCount = 0;
  const posts: Record<string, unknown>[] = [];
  const completed = new Map<string, ReturnType<typeof emptyWorkspace>>();
  await page.route("**/api/v1/**", async (route) => {
    const request = route.request();
    const url = new URL(request.url());
    if (url.pathname === "/api/v1/session/single-profile") {
      return json(route, 201, { learner_id: "learner-one" });
    }
    if (url.pathname === "/api/v1/personal-workspace" && request.method() === "GET") {
      if (options.readStatus) {
        return json(route, options.readStatus, { code: "workspace_unavailable" });
      }
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
    if (url.pathname === "/api/v1/personal-workspace/query" && request.method() === "POST") {
      const body = request.postDataJSON() as Record<string, unknown>;
      let records = [...workspace.records];
      if (typeof body.text === "string") {
        const text = body.text.toLocaleLowerCase();
        records = records.filter((record) => {
          const target = record.target as Record<string, unknown>;
          return [record.title, record.body, record.label, target.title]
            .some((value) => typeof value === "string" && value.toLocaleLowerCase().includes(text));
        });
      }
      const matchOne = (record: Record<string, unknown>, key: "record_kind", values: unknown) =>
        !Array.isArray(values) || values.includes(record[key]);
      const matchTarget = (record: Record<string, unknown>, key: string, values: unknown) => {
        const target = record.target as Record<string, unknown>;
        return !Array.isArray(values) || values.includes(target[key]);
      };
      records = records.filter((record) =>
        matchOne(record, "record_kind", body.record_kinds) &&
        matchTarget(record, "owner_module", body.owner_modules) &&
        matchTarget(record, "reference_kind", body.reference_kinds) &&
        matchTarget(record, "target_status", body.target_statuses) &&
        (typeof body.archived !== "boolean" || record.archived === body.archived));
      if (typeof body.collection_id === "string") {
        const collection = workspace.collections.find((item) => item.collection_id === body.collection_id);
        const members = new Set(collection?.member_record_ids as string[] | undefined);
        records = records.filter((record) => members.has(String(record.record_id)));
      }
      const sort = body.sort ?? "workspace_order";
      const textValue = (record: Record<string, unknown>) =>
        String(record.title ?? record.label ?? "").toLocaleLowerCase();
      if (sort === "updated_desc" || sort === "updated_asc") {
        const direction = sort === "updated_desc" ? -1 : 1;
        records.sort((left, right) => direction * String(left.updated_at).localeCompare(String(right.updated_at)));
      } else if (sort === "title_asc") {
        records.sort((left, right) => textValue(left).localeCompare(textValue(right)));
      } else if (sort === "source_asc") {
        records.sort((left, right) => {
          const leftTarget = left.target as Record<string, unknown>;
          const rightTarget = right.target as Record<string, unknown>;
          return String(leftTarget.title).localeCompare(String(rightTarget.title));
        });
      }
      const offset = typeof body.cursor === "string"
        ? Number.parseInt(body.cursor.replace(/^offset_/, ""), 10)
        : 0;
      const limit = Number(body.limit ?? 50);
      const pageRecords = records.slice(offset, offset + limit);
      const nextOffset = offset + pageRecords.length;
      return json(route, 200, {
        schema_version: "1.0.0",
        workspace_revision: workspace.revision,
        query_digest: "e".repeat(64),
        applied_query: body,
        records: pageRecords,
        next_cursor: nextOffset < records.length ? `offset_${nextOffset}` : null,
      });
    }
    if (url.pathname === "/api/v1/personal-workspace/mutations" && request.method() === "POST") {
      const body = request.postDataJSON() as Record<string, unknown>;
      posts.push(body);
      mutationCount += 1;
      const idempotencyKey = String(body.idempotency_key);
      const earlier = completed.get(idempotencyKey);
      if (earlier) {
        workspace = structuredClone(earlier);
        return json(route, 200, workspace);
      }
      const firstFailure = mutationCount === 1 && options.firstMutationStatus;
      if (firstFailure && !options.applyFirstMutationBeforeFailure) {
        return json(route, options.firstMutationStatus!, { code: options.firstMutationCode ?? "unavailable" });
      }
      const mutation = body.mutation as Record<string, unknown>;
      const now = `2026-10-17T10:${String(workspace.revision).padStart(2, "0")}:00Z`;
      if (mutation.operation === "create_note" || mutation.operation === "create_bookmark") {
        const selector = mutation.selector as Record<string, string>;
        const target = {
          reference_kind: selector.reference_kind,
          owner_module: "curriculum",
          ...(selector.reference_kind === "learning_opportunity"
            ? {
                opportunity_id: selector.opportunity_id,
                source_fingerprint: "b".repeat(64),
              }
            : {}),
          placement_id: selector.placement_id,
          package_id: "risk-return-package",
          package_version: "1.0.0",
          package_digest: "a".repeat(64),
          title: "Risk and return basics",
          destination: `/learn/placements/${selector.placement_id}`,
          target_status: "available",
          validated_at: now,
          provenance,
        };
        workspace.records.push(mutation.operation === "create_note" ? {
          record_kind: "note",
          record_id: `note-${workspace.revision}`,
          title: mutation.title,
          body: mutation.body,
          archived: false,
          created_at: now,
          updated_at: now,
          target,
        } : {
          record_kind: "bookmark",
          record_id: `bookmark-${workspace.revision}`,
          label: mutation.label,
          archived: false,
          created_at: now,
          updated_at: now,
          target,
        });
      } else if (mutation.operation === "update_note") {
        workspace.records = workspace.records.map((record) => record.record_id === mutation.record_id
          ? { ...record, title: mutation.title, body: mutation.body, updated_at: now }
          : record);
      } else if (mutation.operation === "update_bookmark") {
        workspace.records = workspace.records.map((record) => record.record_id === mutation.record_id
          ? { ...record, label: mutation.label, updated_at: now }
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
      } else if (mutation.operation === "rename_collection") {
        workspace.collections = workspace.collections.map((collection) => collection.collection_id === mutation.collection_id
          ? { ...collection, title: mutation.title, updated_at: now }
          : collection);
      } else if (mutation.operation === "remove_collection") {
        workspace.collections = workspace.collections.filter((collection) => collection.collection_id !== mutation.collection_id);
      } else if (mutation.operation === "reorder_records") {
        const byId = new Map(workspace.records.map((record) => [record.record_id, record]));
        workspace.records = (mutation.record_ids as string[]).flatMap((recordId) => {
          const record = byId.get(recordId);
          return record ? [record] : [];
        });
      } else if (mutation.operation === "refresh_reference") {
        workspace.records = workspace.records.map((record) => {
          if (record.record_id !== mutation.record_id) return record;
          const target = record.target as Record<string, unknown>;
          return {
            ...record,
            updated_at: now,
            target: {
              ...target,
              target_status: options.refreshStatus ?? "available",
              validated_at: now,
            },
          };
        });
      } else if (mutation.operation === "remove_record") {
        workspace.records = workspace.records.filter((record) => record.record_id !== mutation.record_id);
        workspace.collections = workspace.collections.map((collection) => ({
          ...collection,
          member_record_ids: (collection.member_record_ids as string[]).filter((recordId) => recordId !== mutation.record_id),
          updated_at: now,
        }));
      }
      workspace = {
        ...workspace,
        revision: workspace.revision + 1,
        updated_at: now,
        workspace_digest: String(workspace.revision + 1).padStart(64, "0"),
      };
      completed.set(idempotencyKey, structuredClone(workspace));
      if (firstFailure) {
        return json(route, options.firstMutationStatus!, { code: options.firstMutationCode ?? "unavailable" });
      }
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
  const collection = page.getByRole("heading", { name: "Foundations" }).locator("xpath=ancestor::section[1]");
  await collection.getByRole("checkbox", { name: "Risk notes updated" }).check();
  await collection.getByRole("button", { name: "Save collection items" }).click();
  await expect.poll(() => mocked.workspace().collections[0]?.member_record_ids).toEqual(["note-1"]);

  const updatedRecord = page.getByRole("heading", { name: "Risk notes updated" }).locator("xpath=ancestor::li");
  await updatedRecord.getByRole("button", { name: "Archive record" }).click();
  await expect(page.getByText("Note · Archived")).toBeVisible();
  await page.getByRole("button", { name: "Restore record" }).click();
  await expect(page.getByText("Note · Archived")).toHaveCount(0);

  await page.goto("/saved-learning/new?kind=lesson&placement=cash-flow-primary");
  await page.getByLabel("Personal label").fill("Cash flow bookmark");
  await page.getByRole("button", { name: "Save bookmark" }).click();
  const bookmark = page.getByRole("heading", { name: "Cash flow bookmark" }).locator("xpath=ancestor::li");
  await bookmark.getByLabel("Personal label").fill("Cash flow review");
  await bookmark.getByRole("button", { name: "Save bookmark changes" }).click();
  await expect(page.getByRole("heading", { name: "Cash flow review" })).toBeVisible();
  await page.getByRole("heading", { name: "Cash flow review" }).locator("xpath=ancestor::li").getByRole("button", { name: "Move earlier" }).click();
  await expect.poll(() => mocked.workspace().records.map((record) => record.record_kind)).toEqual(["bookmark", "note"]);

  const reorderedCollection = page.getByRole("heading", { name: "Foundations" }).locator("xpath=ancestor::section[1]");
  await reorderedCollection.getByRole("checkbox", { name: "Cash flow review" }).check();
  await reorderedCollection.getByRole("button", { name: "Move Cash flow review earlier in collection" }).click();
  await reorderedCollection.getByRole("button", { name: "Save collection items" }).click();
  await expect.poll(() => mocked.workspace().collections[0]?.member_record_ids).toEqual(["bookmark-7", "note-1"]);
  await reorderedCollection.getByLabel("Collection name").fill("Core ideas");
  await reorderedCollection.getByRole("button", { name: "Rename collection" }).click();
  await expect(page.getByRole("heading", { name: "Core ideas" })).toBeVisible();

  const removableBookmark = page.getByRole("heading", { name: "Cash flow review" }).locator("xpath=ancestor::li");
  await removableBookmark.locator("summary", { hasText: "Remove saved record" }).click();
  await removableBookmark.getByRole("button", { name: "Remove saved record" }).click();
  await expect(page.getByRole("heading", { name: "Cash flow review" })).toHaveCount(0);
  const removableCollection = page.getByRole("heading", { name: "Core ideas" }).locator("xpath=ancestor::section[1]");
  await removableCollection.locator("summary", { hasText: "Remove collection" }).click();
  await removableCollection.getByRole("button", { name: "Remove collection" }).click();
  await expect(page.getByRole("heading", { name: "Core ideas" })).toHaveCount(0);

  await page.reload();
  await expect(page.getByRole("heading", { level: 3, name: "Risk notes updated" })).toBeVisible();

  const reopenedRecord = page.getByRole("heading", { name: "Risk notes updated" }).locator("xpath=ancestor::li");
  await reopenedRecord.getByText("Technical record").click();
  await expect(reopenedRecord.getByText("risk-return-basics")).toBeVisible();
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  const lightText = await page.locator("main").innerText();
  for (const theme of ["dark", "system"] as const) {
    await page.getByLabel("Theme").selectOption(theme);
    expect(await page.locator("main").innerText()).toBe(lightText);
  }
  expect(new Set(mocked.posts.map((body) => body.idempotency_key)).size).toBe(mocked.posts.length);
});

test("filters saved sources, suppresses unsafe links, and refreshes through the public API", async ({ page }) => {
  const mocked = await mockSavedLearning(page, {
    initialWorkspace: projectWorkspace(),
    refreshStatus: "available",
  });
  await page.goto("/saved-learning?source=project&status=stale&limit=1");

  await expect(page.getByLabel("Source area")).toHaveValue("project");
  await expect(page.getByLabel("Source status")).toHaveValue("stale");
  await expect(page.getByRole("heading", { name: "Allocation review" })).toBeVisible();
  await expect(page.getByText("Saved details changed.")).toBeVisible();
  await expect(page.getByRole("link", { name: "Open saved source" })).toHaveCount(0);
  await expect(page.getByRole("button", { name: "Move earlier" })).toHaveCount(0);

  const refresh = page.waitForRequest((request) =>
    request.method() === "POST" && new URL(request.url()).pathname.endsWith("/personal-workspace/mutations"));
  await page.getByRole("button", { name: "Check source" }).click();
  const refreshRequest = await refresh;
  await expect(page).toHaveURL(/\/saved-learning$/);
  await expect(page.getByRole("heading", { name: "Allocation review" })).toBeVisible();
  await expect(page.getByRole("link", { name: "Open saved source" }).first()).toBeVisible();
  expect((refreshRequest.postDataJSON() as Record<string, unknown>).mutation).toEqual({
    operation: "refresh_reference",
    record_id: "note-allocation",
  });
  expect(mocked.workspace().records[0]?.target).toMatchObject({ target_status: "available" });
});

test("keeps page size with an opaque continuation and never reorders a partial result", async ({ page }) => {
  await mockSavedLearning(page, { initialWorkspace: projectWorkspace() });
  await page.goto("/saved-learning?source=project&limit=1");

  await expect(page.getByRole("heading", { name: "Allocation review" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Closed file" })).toHaveCount(0);
  await expect(page.getByRole("button", { name: "Move earlier" })).toHaveCount(0);
  const more = page.getByRole("link", { name: "Show more results" });
  await expect(more).toHaveAttribute("href", "/saved-learning?source=project&limit=1&cursor=offset_1");
  await more.click();
  await expect(page.getByRole("heading", { name: "Closed file" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Allocation review" })).toHaveCount(0);
});

test("rejects unknown browser filters before opening a learner session", async ({ page }) => {
  let apiRequests = 0;
  await page.route("**/api/v1/**", async (route) => {
    apiRequests += 1;
    return json(route, 500, { code: "should_not_be_called" });
  });
  await page.goto("/saved-learning?owner=learner-one");
  await expect(page.getByRole("heading", { name: "Search could not be shown" })).toBeVisible();
  expect(apiRequests).toBe(0);
});

test("reuses the complete original request after an accepted write loses its response", async ({ page }) => {
  const mocked = await mockSavedLearning(page, { firstMutationStatus: 503, applyFirstMutationBeforeFailure: true });
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
  expect(mocked.posts[1]?.expected_revision).toBe(1);
  expect(mocked.workspace().revision).toBe(2);
  expect(mocked.workspace().records).toHaveLength(1);
});

test("prepares a fresh request when a learner edits after an uncertain response", async ({ page }) => {
  const mocked = await mockSavedLearning(page, { firstMutationStatus: 503, applyFirstMutationBeforeFailure: true });
  await page.goto("/saved-learning/new?kind=lesson&placement=cash-flow-primary");
  await page.getByLabel("Note title").fill("Cash flow reminder");
  await page.getByLabel("Note", { exact: true }).fill("Track the movement of cash.");
  await page.getByRole("button", { name: "Save note" }).click();
  await expect(page.getByRole("heading", { name: "Change not confirmed" })).toBeFocused();
  await page.locator('textarea[name="body"]').fill("Track the movement of cash and timing.");
  await page.getByRole("button", { name: "Save note" }).click();
  await expect(page).toHaveURL(/\/saved-learning$/);
  expect(mocked.posts).toHaveLength(2);
  expect(mocked.posts[1]?.idempotency_key).not.toBe(mocked.posts[0]?.idempotency_key);
  expect(mocked.posts[1]?.expected_revision).toBe(2);
});

test("explains when a selected learning source is no longer available", async ({ page }) => {
  await mockSavedLearning(page, { firstMutationStatus: 409, firstMutationCode: "source_unavailable" });
  await page.goto("/saved-learning/new?kind=lesson&placement=cash-flow-primary");
  await page.getByRole("button", { name: "Save bookmark" }).click();
  await expect(page.getByRole("heading", { name: "Item not saved" })).toBeFocused();
  await expect(page.getByRole("alert")).toContainText("no longer available");
});

for (const [code, heading] of [
  ["stale_revision", "Saved learning changed"],
  ["idempotency_conflict", "Use a fresh request"],
] as const) {
  test(`gives a bounded recovery for ${code}`, async ({ page }) => {
    await mockSavedLearning(page, { firstMutationStatus: 409, firstMutationCode: code });
    await page.goto("/saved-learning/new?kind=lesson&placement=cash-flow-primary");
    await page.getByRole("button", { name: "Save bookmark" }).click();
    await expect(page.getByRole("heading", { name: heading })).toBeFocused();
  });
}

for (const [status, heading] of [
  [401, "Learner session needed"],
  [403, "Saved learning unavailable"],
  [404, "Item not available"],
] as const) {
  test(`fails closed when workspace loading returns ${status}`, async ({ page }) => {
    await mockSavedLearning(page, { readStatus: status });
    await page.goto("/saved-learning");
    await expect(page.getByRole("heading", { name: heading })).toBeVisible();
    await expect(page.locator("main")).not.toContainText("workspace-one");
  });
}

test("opens the saved-learning flow from opportunity and lesson context", async ({ page }) => {
  await page.route("**/api/v1/session/single-profile", (route) => json(route, 201, {
    status: "ready",
    authentication_method: "single_profile",
    expires_at: "2026-10-17T13:00:00Z",
  }));
  await page.route("**/api/v1/curriculum/opportunities/query*", (route) => json(route, 200, learningQueryPageFixture));
  await page.route("**/api/v1/curriculum/opportunities", (route) => json(route, 200, learningCatalogFixture));
  await page.route("**/api/v1/curriculum/placements/*/lesson", (route) => json(route, 200, lessonFixture));
  await page.route("**/api/v1/curriculum/placements/*/completion", (route) => json(route, 200, {
    projection_version: "1.0.0",
    placement_id: lessonFixture.placement_id,
    completed: false,
    completion_meaning: "not_completed",
    source_digest: "c".repeat(64),
    rebuilt_at: "2026-10-17T12:00:00Z",
    history: [],
  }));
  await page.route("**/api/v1/curriculum/placements/*/knowledge-check**", (route) => json(route, 404, { code: "not_found" }));
  await page.route("**/api/v1/content/assets/risk-spectrum", (route) => route.fulfill({
    status: 200,
    contentType: "image/png",
    body: Buffer.from("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAFgwJ/lA2mWQAAAABJRU5ErkJggg==", "base64"),
  }));

  await page.goto(`/learn/opportunities/${availableOpportunity.opportunity_id}`);
  const opportunityLink = page.getByRole("link", { name: "Save to Saved learning" });
  await expect(opportunityLink).toHaveAttribute(
    "href",
    `/saved-learning/new?kind=opportunity&opportunity=${availableOpportunity.opportunity_id}&placement=${availableOpportunity.placement_id}&return=%2Flearn%2Fopportunities%2F${availableOpportunity.opportunity_id}`,
  );

  await page.goto(`/learn/placements/${lessonFixture.placement_id}`);
  const lessonLink = page.getByRole("link", { name: "Save to Saved learning" });
  await expect(lessonLink).toHaveAttribute(
    "href",
    `/saved-learning/new?kind=lesson&placement=${lessonFixture.placement_id}&return=%2Flearn%2Fplacements%2F${lessonFixture.placement_id}`,
  );
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

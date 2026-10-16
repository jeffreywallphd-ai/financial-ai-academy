import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";
import type { Page, Route } from "@playwright/test";

const origin = {
  origin_type: "learning",
  project_brief_schema_version: "1.0.0",
  package_id: "intro-risk-return-project",
  package_version: "1.0.0",
  package_digest: "a".repeat(64),
  brief_id: "risk-return-project",
  brief_version: "1.0.0",
  brief_digest: "b".repeat(64),
  curriculum_id: "financial-foundations",
  curriculum_version: "1.0.0",
  curriculum_digest: "c".repeat(64),
  placement_id: "risk-return-project-primary",
  placement_version: "1.0.0",
  placement_digest: "d".repeat(64),
  brief_title: "Compare investment choices",
  brief_purpose: "Practice a structured educational comparison.",
};
const option = { title: origin.brief_title, purpose: origin.brief_purpose, origin };
const independent = {
  schema_version: "1.0.0",
  project_id: "project-independent",
  learner_id: "learner-a",
  title: "My independent research",
  charter: "Compare reviewed evidence.",
  origin: { origin_type: "independent" },
  lifecycle: "active",
  revision: 1,
  created_at: "2026-10-16T20:00:00Z",
  updated_at: "2026-10-16T20:00:00Z",
};

function json(route: Route, status: number, body: unknown) {
  return route.fulfill({ status, contentType: "application/json", body: JSON.stringify(body) });
}

async function mockProjects(page: Page, postBodies: Record<string, unknown>[], options: {
  beforeCreateResponse?: () => Promise<void>;
  firstCreateStatus?: 409 | 503;
  staleStartOption?: boolean;
} = {}) {
  let created: Record<string, unknown> | null = null;
  let creates = 0;
  await page.route("**/api/v1/session/single-profile", (route) => json(route, 201, {
    status: "ready", authentication_method: "single_profile", expires_at: "2026-10-16T22:00:00Z",
  }));
  await page.route("**/api/v1/projects**", async (route) => {
    const request = route.request();
    const url = new URL(request.url());
    if (request.method() === "POST" && url.pathname === "/api/v1/projects") {
      const body = request.postDataJSON() as Record<string, unknown>;
      postBodies.push(body);
      creates += 1;
      await options.beforeCreateResponse?.();
      if (options.firstCreateStatus && creates === 1) return json(route, options.firstCreateStatus, { code: options.firstCreateStatus === 409 ? "idempotency_conflict" : "unavailable" });
      created = {
        schema_version: "1.0.0", project_id: "project-learning", learner_id: "learner-a",
        title: body.title, charter: body.charter, origin: body.origin, lifecycle: "active", revision: 1,
        created_at: "2026-10-16T21:00:00Z", updated_at: "2026-10-16T21:00:00Z",
      };
      return json(route, 200, created);
    }
    if (url.pathname === "/api/v1/projects/start-options") return json(route, 200, { records: [option] });
    if (url.pathname === `/api/v1/projects/start-options/${origin.placement_id}`) return options.staleStartOption ? json(route, 400, { code: "stale_source" }) : json(route, 200, option);
    if (url.pathname === "/api/v1/projects") return json(route, 200, { records: [independent] });
    if (url.pathname === "/api/v1/projects/project-learning" && created) return json(route, 200, created);
    return json(route, 404, { code: "not_found" });
  });
}

test("lists, starts, and reopens a learning Project through public APIs", async ({ page }) => {
  const posts: Record<string, unknown>[] = [];
  await mockProjects(page, posts);
  await page.goto("/projects");
  await expect(page.getByRole("heading", { level: 1, name: "Projects" })).toBeVisible();
  await expect(page.getByText("My independent research")).toBeVisible();
  await expect(page.getByText(option.title)).toBeVisible();
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);

  const lightText = await page.locator("main").innerText();
  await page.getByLabel("Theme").selectOption("dark");
  expect(await page.locator("main").innerText()).toBe(lightText);
  await page.getByRole("link", { name: "Start project" }).click();
  await page.getByLabel(/What do you want/i).fill("Apply the learning brief to reviewed evidence.");
  const requestPromise = page.waitForRequest((request) => request.method() === "POST" && new URL(request.url()).pathname === "/api/v1/projects");
  await page.getByRole("button", { name: "Create Project" }).click();
  const createRequest = await requestPromise;

  await expect(page).toHaveURL(/\/projects\/project-learning$/);
  await expect(page.getByRole("heading", { level: 1, name: option.title, exact: true })).toBeVisible();
  const submitted = createRequest.postDataJSON() as Record<string, unknown>;
  expect(submitted).not.toHaveProperty("learner_id");
  expect(submitted.origin).toEqual(origin);
  await page.getByText("Technical record").click();
  await expect(page.getByText(origin.placement_digest)).toBeVisible();
  await expect(page.getByText(origin.package_digest)).toBeVisible();
  await expect(page.getByText(origin.curriculum_digest)).toBeVisible();
  await expect(page.getByText(origin.project_brief_schema_version, { exact: true })).toBeVisible();
});

test("reuses one retry key for unchanged intent", async ({ page }) => {
  const posts: Record<string, unknown>[] = [];
  await mockProjects(page, posts, { firstCreateStatus: 503 });
  await page.goto(`/projects/new?placement=${origin.placement_id}`);
  await page.getByLabel(/What do you want/i).fill("First bounded purpose.");
  const firstRequestPromise = page.waitForRequest((request) => request.method() === "POST" && new URL(request.url()).pathname === "/api/v1/projects");
  await page.getByRole("button", { name: "Create Project" }).click();
  const firstRequest = await firstRequestPromise;
  await expect(page.getByText("Project not created")).toBeVisible();
  await expect(page.getByLabel(/What do you want/i)).toHaveValue("First bounded purpose.");
  const firstKey = (firstRequest.postDataJSON() as Record<string, unknown>).idempotency_key;

  const retryRequestPromise = page.waitForRequest((request) => request.method() === "POST" && new URL(request.url()).pathname === "/api/v1/projects");
  await page.getByRole("button", { name: "Create Project" }).click();
  const retryRequest = await retryRequestPromise;
  await expect(page).toHaveURL(/\/projects\/project-learning$/);
  expect((retryRequest.postDataJSON() as Record<string, unknown>).idempotency_key).toBe(firstKey);
});

test("uses a fresh request after an idempotency conflict", async ({ page }) => {
  const posts: Record<string, unknown>[] = [];
  await mockProjects(page, posts, { firstCreateStatus: 409 });
  await page.goto(`/projects/new?placement=${origin.placement_id}`);
  await page.getByLabel(/What do you want/i).fill("First bounded purpose.");
  await page.getByRole("button", { name: "Create Project" }).click();
  await expect(page.getByText(/fresh request/i)).toBeVisible();

  await page.getByRole("button", { name: "Create Project" }).click();

  await expect(page).toHaveURL(/\/projects\/project-learning$/);
  expect(posts[1]?.idempotency_key).not.toBe(posts[0]?.idempotency_key);
});

test("keeps the submitted Project draft fixed while the response is pending", async ({ page }) => {
  let release!: () => void;
  const pending = new Promise<void>((resolve) => { release = resolve; });
  await mockProjects(page, [], { beforeCreateResponse: () => pending });
  await page.goto("/projects/new");
  await page.getByLabel("Project title").fill("Delayed response");
  await page.getByLabel(/What do you want/i).fill("Keep this exact request fixed.");
  const submit = page.getByRole("button", { name: "Create Project" }).click();

  await expect(page.getByLabel("Project title")).toBeDisabled();
  await expect(page.getByLabel(/What do you want/i)).toBeDisabled();
  release();
  await submit;
  await expect(page).toHaveURL(/\/projects\/project-learning$/);
});

test("returns a stale learning choice to current Projects", async ({ page }) => {
  await mockProjects(page, [], { staleStartOption: true });
  await page.goto(`/projects/new?placement=${origin.placement_id}`);

  await expect(page.getByText("Project not found")).toBeVisible();
  await page.getByRole("button", { name: "Return to Projects" }).click();
  await expect(page).toHaveURL(/\/projects$/);
});

test("reflows at narrow width and keeps plain language outside technical records", async ({ page }) => {
  await mockProjects(page, []);
  await page.setViewportSize({ width: 375, height: 720 });
  await page.goto("/projects");
  const dimensions = await page.evaluate(() => ({ viewport: document.documentElement.clientWidth, content: document.documentElement.scrollWidth }));
  expect(dimensions.content).toBeLessThanOrEqual(dimensions.viewport);
  await expect(page.locator("main")).not.toContainText(/database|idempotency|object storage|foreign key/i);
  await page.emulateMedia({ reducedMotion: "reduce", forcedColors: "active" });
  await page.getByRole("link", { name: "Start project" }).focus();
  expect(await page.getByRole("link", { name: "Start project" }).evaluate((element) => getComputedStyle(element).outlineStyle)).not.toBe("none");
});

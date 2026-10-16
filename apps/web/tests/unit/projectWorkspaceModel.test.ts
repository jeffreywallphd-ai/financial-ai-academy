import { describe, expect, it, vi } from "vitest";

import type { FinancialAcademyApiClient } from "../../src/generated/api-client";
import {
  createProjectCreateAction,
  createProjectCreateLoader,
  createProjectListLoader,
} from "../../src/features/project-workspace/api";
import {
  learningStartOptionListIsSafe,
  projectListIsSafe,
  type LearningProjectStartOption,
  type ProjectShell,
} from "../../src/features/project-workspace/model";
import type { SingleProfileSession } from "../../src/platform/auth/singleProfileSession";

const origin = {
  origin_type: "learning" as const,
  project_brief_schema_version: "1.0.0" as const,
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

const option: LearningProjectStartOption = {
  title: origin.brief_title,
  purpose: origin.brief_purpose,
  origin,
};

const project: ProjectShell = {
  schema_version: "1.0.0",
  project_id: "project-alpha",
  learner_id: "learner-a",
  title: "Évidence comparison",
  charter: "Compare sources without making an investment recommendation.",
  origin: { origin_type: "independent" },
  lifecycle: "active",
  revision: 1,
  created_at: "2026-10-16T20:00:00Z",
  updated_at: "2026-10-16T20:00:00+00:00",
};

function response(status: number, data?: unknown) {
  return { data, error: undefined, response: new Response(null, { status }) };
}

function session() {
  return {
    ensure: vi.fn().mockResolvedValue({ status: "ready" }),
    invalidate: vi.fn(),
  } as unknown as SingleProfileSession;
}

describe("Project response validation", () => {
  it("accepts empty, varied, reordered, Unicode, and boundary-length records", () => {
    const second = {
      ...project,
      project_id: "project-zeta",
      title: "T".repeat(120),
      charter: "C".repeat(4000),
      created_at: "2024-02-29T12:00:00-05:00",
    };
    expect(projectListIsSafe({ records: [] })).toBe(true);
    expect(projectListIsSafe({ records: [second, project] })).toBe(true);
    expect(learningStartOptionListIsSafe({ records: [] })).toBe(true);
    expect(learningStartOptionListIsSafe({ records: [option] })).toBe(true);
  });

  it.each([
    ["unknown envelope field", { records: [project], private_owner: "hidden" }],
    ["duplicate Project", { records: [project, project] }],
    ["invalid calendar time", { records: [{ ...project, created_at: "2026-02-31T12:00:00Z" }] }],
    ["technical extra field", { records: [{ ...project, storage_path: "private" }] }],
  ])("rejects %s without accepting a partial list", (_label, value) => {
    expect(projectListIsSafe(value)).toBe(false);
  });

  it("rejects duplicate or client-altered learning choices", () => {
    expect(learningStartOptionListIsSafe({ records: [option, option] })).toBe(false);
    expect(learningStartOptionListIsSafe({ records: [{ ...option, title: "Changed" }] })).toBe(false);
  });
});

describe("Project generated-client loaders and action", () => {
  it("loads independent records and learning choices without assuming a fixture count or order", async () => {
    const get = vi.fn()
      .mockResolvedValueOnce(response(200, { records: [project] }))
      .mockResolvedValueOnce(response(200, { records: [option] }));
    const loader = createProjectListLoader({ GET: get } as unknown as FinancialAcademyApiClient, session());
    const result = await loader({ request: new Request("http://localhost/projects") } as never);

    expect(result).toEqual({ status: "ready", projects: [project], options: [option] });
    expect(get).toHaveBeenCalledWith("/api/v1/projects", expect.objectContaining({ signal: expect.any(AbortSignal) }));
    expect(get).toHaveBeenCalledWith("/api/v1/projects/start-options", expect.objectContaining({ signal: expect.any(AbortSignal) }));
  });

  it("rejects unknown create URL state before session or API work", async () => {
    const selectedSession = session();
    const get = vi.fn();
    const loader = createProjectCreateLoader({ GET: get } as unknown as FinancialAcademyApiClient, selectedSession);
    const result = await loader({ request: new Request("http://localhost/projects/new?owner=client") } as never);

    expect(result).toEqual({ status: "invalid-selection" });
    expect(selectedSession.ensure).not.toHaveBeenCalled();
    expect(get).not.toHaveBeenCalled();
  });

  it("returns stale learning choices to the current Projects list", async () => {
    const get = vi.fn().mockResolvedValue(response(400, { code: "stale_source" }));
    const loader = createProjectCreateLoader({ GET: get } as unknown as FinancialAcademyApiClient, session());

    const result = await loader({ request: new Request(`http://localhost/projects/new?placement=${origin.placement_id}`) } as never);

    expect(result).toEqual({ status: "invalid-selection" });
  });

  it("resolves exact learning origin again before create and never submits learner authority", async () => {
    const get = vi.fn().mockResolvedValue(response(200, option));
    const post = vi.fn().mockResolvedValue(response(200, { ...project, project_id: "project-learning", origin }));
    const action = createProjectCreateAction({ GET: get, POST: post } as unknown as FinancialAcademyApiClient, session());
    const form = new FormData();
    form.set("title", "My comparison");
    form.set("charter", "Apply the approved brief.");
    form.set("placement_id", origin.placement_id);
    form.set("idempotency_key", "11111111-1111-4111-8111-111111111111");

    const result = await action({ request: new Request("http://localhost/projects/new", { body: form, method: "POST" }) } as never);

    expect(result).toBeInstanceOf(Response);
    expect((result as Response).headers.get("location")).toBe("/projects/project-learning");
    const submitted = post.mock.calls[0]?.[1]?.body as Record<string, unknown>;
    expect(submitted).not.toHaveProperty("learner_id");
    expect(submitted.origin).toEqual(origin);
    expect(submitted.idempotency_key).toBe("11111111-1111-4111-8111-111111111111");
  });

  it("does not classify an idempotency conflict as an unchanged retry", async () => {
    const get = vi.fn().mockResolvedValue(response(200, option));
    const post = vi.fn().mockResolvedValue(response(409, { code: "idempotency_conflict" }));
    const action = createProjectCreateAction({ GET: get, POST: post } as unknown as FinancialAcademyApiClient, session());
    const form = new FormData();
    form.set("title", "My comparison");
    form.set("charter", "Apply the approved brief.");
    form.set("placement_id", origin.placement_id);
    form.set("idempotency_key", "11111111-1111-4111-8111-111111111111");

    const result = await action({ request: new Request("http://localhost/projects/new", { body: form, method: "POST" }) } as never);

    expect(result).toEqual(expect.objectContaining({ status: "error", kind: "conflict" }));
  });
});

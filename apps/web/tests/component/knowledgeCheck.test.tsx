import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import type { FinancialAcademyApiClient } from "../../src/generated/api-client";
import { KnowledgeCheck } from "../../src/features/lesson-reading/KnowledgeCheck";


const presentation = {
  schema_version: "1.0.0" as const,
  placement_id: "intro-risk-return-check",
  package_id: "intro-risk-return",
  package_version: "1.1.0" as const,
  package_digest: "a".repeat(64),
  assessment_id: "risk-return-check-1",
  assessment_version: "1.0.0" as const,
  definition_digest: "b".repeat(64),
  item_type: "single_select" as const,
  item_id: "risk-return-question-1",
  item_version: "1.0.0" as const,
  scoring_policy_id: "single-select-exact-match" as const,
  scoring_policy_version: "1.0.0" as const,
  prompt: "Which statement best describes risk and return?",
  options: [
    {
      option_id: "higher-potential-higher-uncertainty",
      label: "Higher potential return generally comes with higher uncertainty.",
    },
    {
      option_id: "higher-risk-guarantees-return",
      label: "Taking more risk guarantees a higher return.",
    },
  ],
};

const result = {
  schema_version: "1.0.0" as const,
  attempt_id: "55555555-5555-4555-8555-555555555555",
  evidence_id: "66666666-6666-4666-8666-666666666666",
  submission_id: "22222222-2222-4222-8222-222222222222",
  placement_id: presentation.placement_id,
  package_id: presentation.package_id,
  package_version: presentation.package_version,
  package_digest: presentation.package_digest,
  assessment_id: presentation.assessment_id,
  assessment_version: presentation.assessment_version,
  definition_digest: presentation.definition_digest,
  item_id: presentation.item_id,
  item_version: presentation.item_version,
  scoring_policy_id: presentation.scoring_policy_id,
  scoring_policy_version: presentation.scoring_policy_version,
  score: 1,
  max_score: 1 as const,
  correct: true,
  feedback: {
    feedback_id: "risk-return-correct",
    text: "Correct. Risk and potential return should be considered together.",
  },
  submitted_at: "2026-10-15T12:00:00Z",
};

const incompleteCompletion = {
  projection_version: "1.0.0" as const,
  placement_id: presentation.placement_id,
  completed: false,
  completion_meaning: "not_completed" as const,
  source_digest: "c".repeat(64),
  rebuilt_at: "2026-10-15T12:00:00Z",
  history: [],
};

const completionEntry = {
  event_id: "77777777-7777-4777-8777-777777777777",
  attempt_id: result.attempt_id,
  evidence_id: result.evidence_id,
  package_id: presentation.package_id,
  package_version: presentation.package_version,
  package_digest: presentation.package_digest,
  assessment_id: presentation.assessment_id,
  assessment_version: presentation.assessment_version,
  definition_digest: presentation.definition_digest,
  item_id: presentation.item_id,
  item_version: presentation.item_version,
  scoring_policy_id: presentation.scoring_policy_id,
  scoring_policy_version: presentation.scoring_policy_version,
  score: 1,
  max_score: 1 as const,
  completed_at: "2026-10-15T12:00:00Z",
};

const completedCompletion = {
  ...incompleteCompletion,
  completed: true,
  completion_meaning: "bounded_knowledge_check_completed" as const,
  history: [completionEntry],
};

type ApiResult = {
  data?: unknown;
  response: Response;
};

function client({
  completionError = false,
  completionResponse = {
    data: incompleteCompletion,
    response: new Response(null, { status: 200 }),
  },
  post = vi.fn().mockResolvedValue({
    data: result,
    response: new Response(null, { status: 200 }),
  }),
}: {
  completionError?: boolean;
  completionResponse?: ApiResult;
  post?: ReturnType<typeof vi.fn>;
} = {}) {
  const get = vi.fn().mockImplementation(async (path: string) => {
    if (path.endsWith("/completion")) {
      if (completionError) {
        throw new Error("offline");
      }
      return completionResponse;
    }
    return {
      data: presentation,
      response: new Response(null, { status: 200 }),
    };
  });
  return {
    api: {
      GET: get,
      POST: post,
    } as unknown as FinancialAcademyApiClient,
    get,
    post,
  };
}

describe("KnowledgeCheck", () => {
  it("checks retained completion before showing the answer-safe presentation", async () => {
    const { api, get } = client();
    render(
      <KnowledgeCheck
        client={api}
        placementId="intro-risk-return-check"
      />,
    );

    expect(
      await screen.findByRole("heading", { name: "Knowledge check" }),
    ).toBeVisible();
    expect(screen.getAllByRole("radio")).toHaveLength(2);
    expect(document.body.textContent?.toLowerCase()).not.toContain(
      "answer key",
    );
    expect(get.mock.calls.map((call) => call[0])).toEqual([
      "/api/v1/curriculum/placements/{placement_id}/completion",
      "/api/v1/curriculum/placements/{placement_id}/knowledge-check",
    ]);
  });

  it("submits the exact generated contract and displays bounded feedback", async () => {
    const user = userEvent.setup();
    const { api, post } = client();
    render(
      <KnowledgeCheck
        client={api}
        placementId="intro-risk-return-check"
      />,
    );

    await user.click(
      await screen.findByRole("radio", {
        name: /Higher potential return/i,
      }),
    );
    await user.click(screen.getByRole("button", { name: "Check answer" }));

    expect(
      await screen.findByRole("heading", {
        name: "Knowledge check complete",
      }),
    ).toBeVisible();
    expect(screen.getByText(/not mastery or certification/i)).toBeVisible();
    const request = post.mock.calls[0]?.[1];
    expect(request.body.selected_option_id).toBe(
      "higher-potential-higher-uncertainty",
    );
    expect(request.body.learner_id).toBeUndefined();
  });

  it("reuses one submission identity for an unchanged safe retry", async () => {
    const user = userEvent.setup();
    const post = vi
      .fn()
      .mockRejectedValueOnce(new Error("offline"))
      .mockResolvedValueOnce({
        data: result,
        response: new Response(null, { status: 200 }),
      });
    const { api } = client({ post });
    render(
      <KnowledgeCheck
        client={api}
        placementId="intro-risk-return-check"
      />,
    );

    await user.click(
      await screen.findByRole("radio", {
        name: /Higher potential return/i,
      }),
    );
    await user.click(screen.getByRole("button", { name: "Check answer" }));
    expect(await screen.findByRole("alert")).toHaveTextContent(
      /safely reuse this submission/i,
    );
    await user.click(screen.getByRole("button", { name: "Check answer" }));
    await screen.findByRole("heading", { name: "Knowledge check complete" });

    expect(post).toHaveBeenCalledTimes(2);
    expect(post.mock.calls[0]?.[1].body.submission_id).toBe(
      post.mock.calls[1]?.[1].body.submission_id,
    );
  });

  it("reopens exact retained evidence without requesting another presentation", async () => {
    const { api, get, post } = client({
      completionResponse: {
        data: completedCompletion,
        response: new Response(null, { status: 200 }),
      },
    });
    render(
      <KnowledgeCheck
        client={api}
        placementId="intro-risk-return-check"
      />,
    );

    expect(
      await screen.findByRole("heading", {
        name: "Retained lesson completion",
      }),
    ).toBeVisible();
    expect(screen.getByText(/1 of 1/i)).toBeVisible();
    expect(screen.getByText(presentation.package_digest)).toBeVisible();
    expect(screen.getByText(presentation.definition_digest)).toBeVisible();
    expect(screen.getByText(completionEntry.event_id)).toBeVisible();
    expect(screen.getByText(completionEntry.attempt_id)).toBeVisible();
    expect(screen.getByText(completionEntry.evidence_id)).toBeVisible();
    expect(screen.getByText(/not a mastery or certification/i)).toBeVisible();
    expect(screen.getByText(/does not provide investment advice/i)).toBeVisible();
    expect(screen.queryAllByRole("radio")).toHaveLength(0);
    expect(get).toHaveBeenCalledTimes(1);
    expect(post).not.toHaveBeenCalled();
    expect(document.body.textContent).not.toMatch(/selected_option|answer key/i);
  });

  it.each([
    {
      name: "denied",
      options: {
        completionResponse: {
          response: new Response(null, { status: 403 }),
        },
      },
      message: /cannot open this completion record/i,
    },
    {
      name: "malformed",
      options: {
        completionResponse: {
          data: { ...completedCompletion, history: [] },
          response: new Response(null, { status: 200 }),
        },
      },
      message: /did not pass the safe presentation checks/i,
    },
    {
      name: "unavailable",
      options: {
        completionResponse: {
          response: new Response(null, { status: 503 }),
        },
      },
      message: /temporarily unavailable/i,
    },
    {
      name: "network failure",
      options: { completionError: true },
      message: /temporarily unavailable/i,
    },
  ])("fails closed when retained completion is $name", async ({
    message,
    options,
  }) => {
    const { api, get } = client(options);
    render(
      <KnowledgeCheck
        client={api}
        placementId="intro-risk-return-check"
      />,
    );

    expect(
      await screen.findByRole("heading", {
        name: "Completion record unavailable",
      }),
    ).toBeVisible();
    expect(screen.getByText(message)).toBeVisible();
    expect(screen.queryAllByRole("radio")).toHaveLength(0);
    expect(get).toHaveBeenCalledTimes(1);
  });
});

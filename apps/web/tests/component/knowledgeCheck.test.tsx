import { render, screen, within } from "@testing-library/react";
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
  presentationResponse = {
    data: presentation,
    response: new Response(null, { status: 200 }),
  },
  post = vi.fn().mockResolvedValue({
    data: result,
    response: new Response(null, { status: 200 }),
  }),
}: {
  completionError?: boolean;
  completionResponse?: ApiResult;
  presentationResponse?: ApiResult;
  post?: ReturnType<typeof vi.fn>;
} = {}) {
  const get = vi.fn().mockImplementation(async (path: string) => {
    if (path.endsWith("/completion")) {
      if (completionError) {
        throw new Error("offline");
      }
      return completionResponse;
    }
    return presentationResponse;
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
    expect(
      screen.getByText(/does not show mastery or certification/i),
    ).toBeVisible();
    const technicalRecord = screen.getByText("Technical record");
    await user.click(technicalRecord);
    const technicalDetails = technicalRecord.closest("details");
    expect(technicalDetails).toHaveAttribute("open");
    const technical = within(technicalDetails as HTMLElement);
    expect(technical.getByText(result.schema_version)).toBeVisible();
    expect(technical.getByText(result.placement_id)).toBeVisible();
    expect(
      technical.getByText(
        `${presentation.package_id} version ${presentation.package_version}`,
      ),
    ).toBeVisible();
    expect(technical.getByText(presentation.package_digest)).toBeVisible();
    expect(
      technical.getByText(
        `${presentation.assessment_id} version ${presentation.assessment_version}`,
      ),
    ).toBeVisible();
    expect(technical.getByText(presentation.definition_digest)).toBeVisible();
    expect(
      technical.getByText(
        `${presentation.item_id} version ${presentation.item_version}`,
      ),
    ).toBeVisible();
    expect(
      technical.getByText(
        `${presentation.scoring_policy_id} version ${presentation.scoring_policy_version}`,
      ),
    ).toBeVisible();
    expect(technical.getByText(result.attempt_id)).toBeVisible();
    expect(technical.getByText(result.evidence_id)).toBeVisible();
    expect(technical.getByText(result.submission_id)).toBeVisible();
    expect(technical.getByText(result.submitted_at)).toBeVisible();
    expect(technical.getByText(result.feedback.feedback_id)).toBeVisible();
    const request = post.mock.calls[0]?.[1];
    expect(request.body.selected_option_id).toBe(
      "higher-potential-higher-uncertainty",
    );
    expect(request.body.learner_id).toBeUndefined();
  });

  it("keeps incorrect reviewed feedback distinct from mastery", async () => {
    const user = userEvent.setup();
    const incorrectResult = {
      ...result,
      correct: false,
      score: 0,
      feedback: {
        feedback_id: "risk-return-review",
        text: "Review how uncertainty relates to potential return.",
      },
    };
    const { api } = client({
      post: vi.fn().mockResolvedValue({
        data: incorrectResult,
        response: new Response(null, { status: 200 }),
      }),
    });
    render(
      <KnowledgeCheck
        client={api}
        placementId="intro-risk-return-check"
      />,
    );

    await user.click(
      await screen.findByRole("radio", { name: /guarantees a higher return/i }),
    );
    await user.click(screen.getByRole("button", { name: "Check answer" }));

    expect(
      await screen.findByRole("heading", { name: "Review the concept" }),
    ).toBeVisible();
    expect(screen.getByText(incorrectResult.feedback.text)).toBeVisible();
    expect(screen.getByText(/Score: 0 of 1/i)).toBeVisible();
    expect(
      screen.getByText(/does not show mastery or certification/i),
    ).toBeVisible();
  });

  it.each([
    {
      name: "conflicting exact references",
      status: 409,
      message: /page no longer matches.*No new result was recorded/i,
    },
    {
      name: "denied learner session",
      status: 403,
      message: /couldn't check your answer.*No result was recorded/i,
    },
  ])("explains $name without claiming a result", async ({ status, message }) => {
    const user = userEvent.setup();
    const post = vi.fn().mockResolvedValue({
      response: new Response(null, { status }),
    });
    const { api } = client({ post });
    render(
      <KnowledgeCheck
        client={api}
        placementId="intro-risk-return-check"
      />,
    );

    await user.click(
      await screen.findByRole("radio", { name: /Higher potential return/i }),
    );
    await user.click(screen.getByRole("button", { name: "Check answer" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(message);
    expect(post).toHaveBeenCalledTimes(1);
    expect(screen.queryByRole("heading", { name: "Knowledge check complete" })).not.toBeInTheDocument();
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
      /reuse this answer.*duplicate result/i,
    );
    await user.click(screen.getByRole("button", { name: "Check answer" }));
    await screen.findByRole("heading", { name: "Knowledge check complete" });

    expect(post).toHaveBeenCalledTimes(2);
    expect(post.mock.calls[0]?.[1].body.submission_id).toBe(
      post.mock.calls[1]?.[1].body.submission_id,
    );
  });

  it("reopens exact retained evidence without requesting another presentation", async () => {
    const user = userEvent.setup();
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
        name: "Saved lesson completion",
      }),
    ).toBeVisible();
    expect(screen.getByText(/1 of 1/i)).toBeVisible();
    const technicalRecords = screen.getAllByText("Technical record");
    expect(technicalRecords).toHaveLength(2);
    for (const technicalRecord of technicalRecords) {
      await user.click(technicalRecord);
    }
    const completionTechnical = within(
      technicalRecords[0]!.closest("details") as HTMLElement,
    );
    expect(
      completionTechnical.getByText(completedCompletion.projection_version),
    ).toBeVisible();
    expect(
      completionTechnical.getByText(completedCompletion.placement_id),
    ).toBeVisible();
    expect(
      completionTechnical.getByText(completedCompletion.completion_meaning),
    ).toBeVisible();
    expect(
      completionTechnical.getByText(completedCompletion.rebuilt_at),
    ).toBeVisible();
    expect(
      completionTechnical.getByText(completedCompletion.source_digest),
    ).toBeVisible();
    const resultTechnical = within(
      technicalRecords[1]!.closest("details") as HTMLElement,
    );
    expect(
      resultTechnical.getByText(
        `${completionEntry.package_id} version ${completionEntry.package_version}`,
      ),
    ).toBeVisible();
    expect(resultTechnical.getByText(completionEntry.package_digest)).toBeVisible();
    expect(
      resultTechnical.getByText(
        `${completionEntry.assessment_id} version ${completionEntry.assessment_version}`,
      ),
    ).toBeVisible();
    expect(
      resultTechnical.getByText(completionEntry.definition_digest),
    ).toBeVisible();
    expect(
      resultTechnical.getByText(
        `${completionEntry.item_id} version ${completionEntry.item_version}`,
      ),
    ).toBeVisible();
    expect(
      resultTechnical.getByText(
        `${completionEntry.scoring_policy_id} version ${completionEntry.scoring_policy_version}`,
      ),
    ).toBeVisible();
    expect(resultTechnical.getByText(completionEntry.completed_at)).toBeVisible();
    expect(resultTechnical.getByText(completionEntry.event_id)).toBeVisible();
    expect(resultTechnical.getByText(completionEntry.attempt_id)).toBeVisible();
    expect(resultTechnical.getByText(completionEntry.evidence_id)).toBeVisible();
    expect(screen.getByText(/not a mastery or certification/i)).toBeVisible();
    expect(screen.getByText(/does not provide investment advice/i)).toBeVisible();
    expect(screen.queryAllByRole("radio")).toHaveLength(0);
    expect(get).toHaveBeenCalledTimes(1);
    expect(post).not.toHaveBeenCalled();
    expect(document.body.textContent).not.toMatch(/selected_option|answer key/i);
  });

  it("renders every safe saved result without assuming one history item", async () => {
    const user = userEvent.setup();
    const secondEntry = {
      ...completionEntry,
      event_id: "88888888-8888-4888-8888-888888888888",
      attempt_id: "99999999-9999-4999-8999-999999999999",
      evidence_id: "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
      completed_at: "2026-10-15T13:00:00Z",
    };
    const { api } = client({
      completionResponse: {
        data: { ...completedCompletion, history: [completionEntry, secondEntry] },
        response: new Response(null, { status: 200 }),
      },
    });
    render(
      <KnowledgeCheck
        client={api}
        placementId="intro-risk-return-check"
      />,
    );

    await screen.findByRole("heading", { name: "Saved lesson completion" });
    expect(
      screen.getAllByRole("article", { name: /Saved result \d/ }),
    ).toHaveLength(2);
    const technicalRecords = screen.getAllByText("Technical record");
    expect(technicalRecords).toHaveLength(3);
    expect(
      screen.getByLabelText("Technical record for saved result 2"),
    ).toBeVisible();
    await user.click(technicalRecords[2]!);
    expect(screen.getByText(secondEntry.event_id)).toBeVisible();
    expect(screen.getByText(secondEntry.attempt_id)).toBeVisible();
    expect(screen.getByText(secondEntry.evidence_id)).toBeVisible();
  });

  it.each([
    {
      name: "denied",
      options: {
        completionResponse: {
          response: new Response(null, { status: 403 }),
        },
      },
      message: /couldn't open your saved completion/i,
    },
    {
      name: "malformed",
      options: {
        completionResponse: {
          data: { ...completedCompletion, history: [] },
          response: new Response(null, { status: 200 }),
        },
      },
      message: /couldn't safely show your saved completion/i,
    },
    {
      name: "unavailable",
      options: {
        completionResponse: {
          response: new Response(null, { status: 503 }),
        },
      },
      message: /couldn't check for a saved completion/i,
    },
    {
      name: "network failure",
      options: { completionError: true },
      message: /couldn't check for a saved completion/i,
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
        name: "Saved completion unavailable",
      }),
    ).toBeVisible();
    expect(screen.getByText(message)).toBeVisible();
    expect(screen.queryAllByRole("radio")).toHaveLength(0);
    expect(get).toHaveBeenCalledTimes(1);
  });

  it.each([
    {
      name: "denied",
      response: { response: new Response(null, { status: 403 }) },
      message: /couldn't open this knowledge check with your learner session/i,
    },
    {
      name: "malformed",
      response: {
        data: { ...presentation, options: [] },
        response: new Response(null, { status: 200 }),
      },
      message: /couldn't safely show this knowledge check/i,
    },
    {
      name: "unavailable",
      response: { response: new Response(null, { status: 503 }) },
      message: /couldn't open this knowledge check right now/i,
    },
  ])("fails closed when the knowledge check is $name", async ({
    message,
    response,
  }) => {
    const { api, get } = client({ presentationResponse: response });
    render(
      <KnowledgeCheck
        client={api}
        placementId="intro-risk-return-check"
      />,
    );

    expect(
      await screen.findByRole("heading", {
        name: "Knowledge check unavailable",
      }),
    ).toBeVisible();
    expect(screen.getByText(message)).toBeVisible();
    expect(screen.queryAllByRole("radio")).toHaveLength(0);
    expect(get).toHaveBeenCalledTimes(2);
  });
});

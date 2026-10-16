import {
  createFinancialAcademyApiClient,
  type components,
} from "../../src/generated/api-client";


const client = createFinancialAcademyApiClient(
  "http://127.0.0.1:8000",
);

void client.GET("/api/v1/curriculum/opportunities");

type CurriculumGraphResponse =
  components["schemas"]["CurriculumGraphResponseModel"];
type PracticeSubmission =
  components["schemas"]["PracticeSubmissionRequestModel"];
type PracticeSubmissionResult =
  components["schemas"]["PracticeSubmissionResultResponseModel"];
type ProjectCreateRequest =
  components["schemas"]["ProjectCreateRequestModel"];

function exerciseFlexibleCurriculumGraphResponse(
  graph: CurriculumGraphResponse,
): void {
  const sharedOptionalBranches = graph.branches.filter(
    (branch) =>
      branch.kind === "optional" &&
      branch.activity_ids.includes("activity-diversification-reading"),
  );
  const layoutMayBeAbsent = graph.presentation_order;
  void sharedOptionalBranches;
  void layoutMayBeAbsent;
}

void exerciseFlexibleCurriculumGraphResponse;

function exercisePracticeResult(result: PracticeSubmissionResult): void {
  const orderedItemKinds = result.item_results.map((item) => item.item_type);
  const needsReview = result.outcome === "review_needed";
  void orderedItemKinds;
  void needsReview;
}

void exercisePracticeResult;

void client.GET(
  "/api/v1/curriculum/graphs/{curriculum_id}/versions/{curriculum_version}",
  {
    params: {
      path: {
        curriculum_id: "investing-foundations",
        curriculum_version: "1.0.0",
      },
    },
  },
);

const independentProject: ProjectCreateRequest = {
  schema_version: "1.0.0",
  idempotency_key: "compare-evidence-1",
  title: "Compare evidence",
  charter: "Compare educational sources without making a recommendation.",
  origin: { origin_type: "independent" },
};

void client.POST("/api/v1/projects", { body: independentProject });
void client.GET("/api/v1/projects");
void client.GET("/api/v1/projects/{project_id}", {
  params: { path: { project_id: "project-1" } },
});

const practiceSubmission: PracticeSubmission = {
  schema_version: "1.0.0",
  submission_id: "22222222-2222-4222-8222-222222222222",
  placement_id: "risk-return-practice-placement",
  package_id: "intro-risk-return",
  package_version: "2.0.0",
  package_digest: "a".repeat(64),
  definition_digest: "b".repeat(64),
  practice_id: "risk-return-practice",
  practice_version: "1.0.0",
  attempt_policy_id: "formative-retry",
  attempt_policy_version: "1.0.0",
  responses: [
    {
      item_id: "risk-meaning",
      item_version: "1.0.0",
      item_type: "single_select",
      scoring_policy_id: "single-select-exact-match",
      scoring_policy_version: "1.0.0",
      selected_option_id: "uncertainty",
    },
  ],
};

void client.POST(
  "/api/v1/curriculum/placements/{placement_id}/practice/submissions",
  {
    params: {
      path: {
        placement_id: "risk-return-practice-placement",
      },
    },
    body: practiceSubmission,
  },
);

void client.GET(
  "/api/v1/adaptation/curricula/{curriculum_id}/versions/{curriculum_version}/navigation-state",
  {
    params: {
      path: {
        curriculum_id: "investing-foundations",
        curriculum_version: "1.0.0",
      },
    },
  },
);

void client.GET(
  "/api/v1/adaptation/curricula/{curriculum_id}/versions/{curriculum_version}/activities/{activity_id}/launch",
  {
    params: {
      path: {
        curriculum_id: "investing-foundations",
        curriculum_version: "1.0.0",
        activity_id: "activity-risk-return-lesson",
      },
    },
  },
);

void client.GET("/api/v1/curriculum/opportunities/query", {
  params: {
    query: {
      query: "risk return",
      prerequisite_query: "basics",
      topic: ["risk-return", "investing-basics"],
      level: ["introductory"],
      kind: ["lesson"],
      availability: ["available"],
      minimum_minutes: 10,
      maximum_minutes: 30,
      sort: "title",
      page_size: 10,
    },
  },
});

void client.GET(
  "/api/v1/curriculum/placements/{placement_id}/lesson",
  {
    params: {
      path: {
        placement_id: "intro-risk-return-primary",
      },
    },
  },
);

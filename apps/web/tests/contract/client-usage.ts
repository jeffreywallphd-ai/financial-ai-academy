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
type LearningProjectStartOption =
  components["schemas"]["LearningProjectStartOptionResponseModel"];
type ProjectWorkspaceMutation =
  components["schemas"]["ProjectWorkspaceMutationRequestModel"];
type ProjectArtifactUpload =
  components["schemas"]["ProjectArtifactUploadRequestModel"];
type ProjectSnapshotClose =
  components["schemas"]["ProjectSnapshotCloseRequestModel"];
type ProjectSubmission =
  components["schemas"]["ProjectSubmissionRequestModel"];
type ProjectSubmissionResource =
  components["schemas"]["ProjectMilestoneEvidenceRequestModel"]["resources"][number];
type PersonalWorkspaceMutation =
  components["schemas"]["PersonalWorkspaceMutationRequestModel"];
type PersonalWorkspaceQuery =
  components["schemas"]["PersonalWorkspaceQueryRequestModel"];
type LearnerPreferenceMutation =
  components["schemas"]["LearnerPreferenceMutationRequestModel"];

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
void client.GET("/api/v1/projects/start-options");
const learningStart = client.GET(
  "/api/v1/projects/start-options/{placement_id}",
  { params: { path: { placement_id: "risk-return-project-primary" } } },
);
void learningStart.then((result) => {
  const option: LearningProjectStartOption | undefined = result.data;
  void option;
});
void client.GET("/api/v1/projects/{project_id}", {
  params: { path: { project_id: "project-1" } },
});

void client.GET("/api/v1/personal-workspace");
const savedLearningExport = client.GET(
  "/api/v1/personal-workspace/export",
);
void savedLearningExport.then((result) => {
  const exported = result.data;
  if (exported !== undefined) {
    const sameDigest =
      exported.workspace_digest === exported.workspace.workspace_digest;
    const generatedAt = exported.generated_at;
    void sameDigest;
    void generatedAt;
  }
});
const savedLearningNote: PersonalWorkspaceMutation = {
  schema_version: "1.0.0",
  idempotency_key: "saved-learning-note-1",
  expected_revision: 1,
  mutation: {
    operation: "create_note",
    selector: {
      reference_kind: "learning_opportunity",
      opportunity_id: "risk-return-basics",
      placement_id: "risk-return-primary",
    },
    title: "What I want to remember",
    body: "Risk and return need to be considered together.",
  },
};
void client.POST("/api/v1/personal-workspace/mutations", {
  body: savedLearningNote,
});

const savedProjectArtifact: PersonalWorkspaceMutation = {
  schema_version: "1.0.0",
  idempotency_key: "saved-project-artifact-1",
  expected_revision: 2,
  mutation: {
    operation: "create_bookmark",
    selector: {
      reference_kind: "project_artifact",
      project_id: "project-1",
      artifact_id: "artifact-1",
      artifact_version: 1,
    },
    label: "Allocation inputs",
  },
};
void client.POST("/api/v1/personal-workspace/mutations", {
  body: savedProjectArtifact,
});

const savedLearningQuery: PersonalWorkspaceQuery = {
  schema_version: "1.0.0",
  text: "diversification",
  record_kinds: ["note", "bookmark"],
  target_statuses: ["available", "stale"],
  sort: "updated_desc",
  limit: 25,
};
void client.POST("/api/v1/personal-workspace/query", {
  body: savedLearningQuery,
});
void client.POST("/api/v1/personal-workspace/query", {
  body: { ...savedLearningQuery, cursor: "opaque_cursor" },
});

void client.GET("/api/v1/learner-preferences");
void client.GET("/api/v1/learner-preferences/history");
void client.GET("/api/v1/learner-preferences/export");
const learnerPreferenceMutation: LearnerPreferenceMutation = {
  schema_version: "1.0.0",
  idempotency_key: "intent.goal-1",
  expected_revision: 1,
  mutation: {
    operation: "create_goal",
    title: "Explain investment risk with evidence",
    detail: null,
  },
};
void client.POST("/api/v1/learner-preferences/mutations", {
  body: learnerPreferenceMutation,
});

const refreshSavedReference: PersonalWorkspaceMutation = {
  schema_version: "1.0.0",
  idempotency_key: "refresh-saved-reference-1",
  expected_revision: 3,
  mutation: {
    operation: "refresh_reference",
    record_id: "record-1",
  },
};
void client.POST("/api/v1/personal-workspace/mutations", {
  body: refreshSavedReference,
});

const noteMutation: ProjectWorkspaceMutation = {
  schema_version: "1.0.0",
  idempotency_key: "note-1",
  expected_workspace_revision: 1,
  mutation: {
    operation: "add_note",
    title: "Question",
    body: "Compare the evidence without making a recommendation.",
  },
};
void client.GET("/api/v1/projects/{project_id}/workspace", {
  params: { path: { project_id: "project-1" } },
});
void client.POST("/api/v1/projects/{project_id}/workspace/mutations", {
  params: { path: { project_id: "project-1" } },
  body: noteMutation,
});

const artifactUpload: ProjectArtifactUpload = {
  intent: {
    schema_version: "1.0.0",
    idempotency_key: "artifact-1",
    expected_workspace_revision: 2,
    mutation: {
      operation: "add_artifact",
      artifact: {
        artifact_kind: "dataset",
        logical_path: "data/scenario.csv",
        media_type: "text/csv",
        inspection_mode: "plain_text",
        byte_count: 0,
        content_digest: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        provenance: {
          source_type: "learner_created",
          source_title: "Empty scenario fixture",
        },
        assumptions: [],
      },
    },
  },
  content_base64: "",
};
void client.POST("/api/v1/projects/{project_id}/artifacts", {
  params: { path: { project_id: "project-1" } },
  body: artifactUpload,
});
void client.GET(
  "/api/v1/projects/{project_id}/artifacts/{artifact_id}/versions/{artifact_version}",
  {
    params: {
      path: {
        project_id: "project-1",
        artifact_id: "artifact-1",
        artifact_version: 1,
      },
    },
  },
);

const snapshotClose: ProjectSnapshotClose = {
  schema_version: "1.0.0",
  idempotency_key: "snapshot-1",
  expected_project_revision: 1,
  expected_workspace_revision: 3,
};
void client.POST("/api/v1/projects/{project_id}/snapshots", {
  params: { path: { project_id: "project-1" } },
  body: snapshotClose,
});
void client.GET("/api/v1/projects/{project_id}/snapshots", {
  params: { path: { project_id: "project-1" } },
});
void client.GET("/api/v1/projects/{project_id}/snapshots/{snapshot_id}", {
  params: {
    path: { project_id: "project-1", snapshot_id: "snapshot-1" },
  },
});
void client.GET(
  "/api/v1/projects/{project_id}/snapshots/{snapshot_id}/export",
  {
    params: {
      path: { project_id: "project-1", snapshot_id: "snapshot-1" },
    },
  },
);

void client.GET(
  "/api/v1/projects/{project_id}/snapshots/{snapshot_id}/submission-candidate",
  {
    params: {
      path: { project_id: "project-1", snapshot_id: "snapshot-1" },
    },
  },
);

const projectSubmission: ProjectSubmission = {
  schema_version: "1.0.0",
  submission_id: "project-submission-1",
  source: {
    project_id: "project-1",
    snapshot_id: "snapshot-1",
    snapshot_digest: "a".repeat(64),
    brief_id: "risk-return-project",
    brief_version: "1.0.0",
    brief_digest: "b".repeat(64),
    placement_id: "risk-return-project-primary",
    placement_version: "1.0.0",
    placement_digest: "c".repeat(64),
  },
  policy_id: "assessment-project-closure",
  policy_version: "1.0.0",
  milestone_evidence: [
    {
      milestone_id: "define-comparison",
      resources: [
        {
          resource_kind: "note",
          resource_id: "note-1",
          resource_version: 1,
          record_digest: "d".repeat(64),
        },
      ],
    },
  ],
};

const versionedDomainResource: ProjectSubmissionResource = {
  resource_kind: "domain_resource",
  resource_id: "market-observation",
  resource_version: "1.0.0",
  record_digest: "e".repeat(64),
  owner_reference_digest: "f".repeat(64),
};
const asOfDomainResource: ProjectSubmissionResource = {
  resource_kind: "domain_resource",
  resource_id: "market-observation",
  resource_as_of: "2026-10-17T04:00:00Z",
  record_digest: "e".repeat(64),
  owner_reference_digest: "f".repeat(64),
};
// @ts-expect-error A domain resource requires one exact selector.
const missingDomainSelector: ProjectSubmissionResource = {
  resource_kind: "domain_resource",
  resource_id: "market-observation",
  record_digest: "e".repeat(64),
  owner_reference_digest: "f".repeat(64),
};
const conflictingDomainSelectors: ProjectSubmissionResource = {
  resource_kind: "domain_resource",
  resource_id: "market-observation",
  resource_version: "1.0.0",
  // @ts-expect-error A domain resource cannot carry both exact selectors.
  resource_as_of: "2026-10-17T04:00:00Z",
  record_digest: "e".repeat(64),
  owner_reference_digest: "f".repeat(64),
};
void versionedDomainResource;
void asOfDomainResource;
void missingDomainSelector;
void conflictingDomainSelectors;
void client.POST(
  "/api/v1/projects/{project_id}/snapshots/{snapshot_id}/submissions",
  {
    params: {
      path: { project_id: "project-1", snapshot_id: "snapshot-1" },
    },
    body: projectSubmission,
  },
);
void client.GET("/api/v1/projects/{project_id}/submissions", {
  params: { path: { project_id: "project-1" } },
});
void client.GET("/api/v1/projects/{project_id}/completion", {
  params: { path: { project_id: "project-1" } },
});
void client.GET(
  "/api/v1/projects/{project_id}/submissions/{submission_id}",
  {
    params: {
      path: {
        project_id: "project-1",
        submission_id: "project-submission-1",
      },
    },
  },
);

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

import type {
  CurriculumGraph,
  NavigationState,
} from "../../src/features/curriculum-graph/model";

export const curriculumGraphFixture = {
  schema_version: "1.0.0",
  curriculum_id: "investing-foundations",
  curriculum_version: "1.0.0",
  title: "Investing Foundations",
  summary:
    "A bounded educational curriculum for understanding risk, return, and diversification without personalized financial advice.",
  publication_state: "approved",
  published_at: "2026-10-15T00:00:00Z",
  source_references: [
    "content:intro-risk-return@1.0.0",
    "curriculum:investing-foundations@1.0.0",
  ],
  presentation_order: {
    objective_ids: ["objective-diversification", "objective-risk-return"],
    activity_ids: [
      "activity-risk-return-lesson",
      "activity-risk-return-check",
    ],
  },
  objectives: [
    {
      objective_id: "objective-risk-return",
      title: "Relate risk and potential return",
      description:
        "Explain why potential return and risk must be considered together.",
    },
    {
      objective_id: "objective-diversification",
      title: "Describe diversification",
      description:
        "Describe how diversification changes concentration without guaranteeing outcomes.",
    },
  ],
  competencies: [
    {
      competency_id: "competency-risk-return",
      title: "Risk and return reasoning",
      description:
        "Reason about uncertainty, loss, and potential return without treating return as guaranteed.",
    },
    {
      competency_id: "competency-diversification",
      title: "Diversification reasoning",
      description:
        "Recognize concentration and describe diversification as a risk-management concept.",
    },
  ],
  activities: [
    {
      activity_id: "activity-risk-return-lesson",
      title: "Read about risk and return",
      kind: "lesson",
      reference: {
        reference_kind: "lesson_placement",
        placement_id: "intro-risk-return-primary",
        package_id: "intro-risk-return",
        package_version: "1.0.0",
        package_digest: "a".repeat(64),
      },
    },
    {
      activity_id: "activity-risk-return-check",
      title: "Check risk and return understanding",
      kind: "assessment",
      reference: {
        reference_kind: "assessment_placement",
        placement_id: "intro-risk-return-primary",
        assessment_id: "risk-return-check-1",
        assessment_version: "1.0.0",
        definition_digest: "b".repeat(64),
      },
    },
    {
      activity_id: "activity-diversification-reading",
      title: "Explore diversification",
      kind: "lesson",
      reference: {
        reference_kind: "lesson_placement",
        placement_id: "diversification-reading",
        package_id: "diversification-reading",
        package_version: "1.0.0",
        package_digest: "c".repeat(64),
      },
    },
    {
      activity_id: "activity-diversification-check",
      title: "Practice diversification reasoning",
      kind: "assessment",
      reference: {
        reference_kind: "assessment_placement",
        placement_id: "diversification-check",
        assessment_id: "diversification-check",
        assessment_version: "1.0.0",
        definition_digest: "d".repeat(64),
      },
    },
    {
      activity_id: "activity-terms-glossary",
      title: "Review investing terms",
      kind: "lesson",
      reference: {
        reference_kind: "lesson_placement",
        placement_id: "investing-terms-glossary",
        package_id: "investing-terms-glossary",
        package_version: "1.0.0",
        package_digest: "e".repeat(64),
      },
    },
  ],
  branches: [
    {
      branch_id: "branch-core",
      title: "Core learning",
      kind: "required",
      activity_ids: [
        "activity-risk-return-lesson",
        "activity-risk-return-check",
      ],
    },
    {
      branch_id: "branch-explore",
      title: "Explore diversification",
      kind: "optional",
      activity_ids: ["activity-diversification-reading"],
    },
    {
      branch_id: "branch-practice",
      title: "Practice diversification",
      kind: "optional",
      activity_ids: [
        "activity-diversification-reading",
        "activity-diversification-check",
      ],
    },
  ],
  relationships: [
    {
      relationship_id: "relationship-objective-risk",
      kind: "objective_competency",
      source_id: "objective-risk-return",
      target_id: "competency-risk-return",
    },
    {
      relationship_id: "relationship-objective-diversification",
      kind: "objective_competency",
      source_id: "objective-diversification",
      target_id: "competency-diversification",
    },
    {
      relationship_id: "relationship-lesson-develops-risk",
      kind: "activity_develops_competency",
      source_id: "activity-risk-return-lesson",
      target_id: "competency-risk-return",
    },
    {
      relationship_id: "relationship-check-assesses-risk",
      kind: "activity_assesses_competency",
      source_id: "activity-risk-return-check",
      target_id: "competency-risk-return",
    },
    {
      relationship_id: "relationship-risk-before-diversification",
      kind: "competency_prerequisite",
      source_id: "competency-risk-return",
      target_id: "competency-diversification",
    },
    {
      relationship_id: "relationship-lesson-before-check",
      kind: "activity_prerequisite",
      source_id: "activity-risk-return-lesson",
      target_id: "activity-risk-return-check",
    },
  ],
  graph_digest: "f".repeat(64),
} satisfies CurriculumGraph;

export const navigationStateFixture = {
  schema_version: "1.0.0",
  curriculum_id: "investing-foundations",
  curriculum_version: "1.0.0",
  graph_digest: "f".repeat(64),
  policy_id: "deterministic-prerequisite-navigation",
  policy_version: "1.0.0",
  evaluated_at: "2026-10-15T12:30:00Z",
  source_set_digest: "1".repeat(64),
  activity_states: [
    {
      activity_id: "activity-risk-return-lesson",
      completion: "completed",
      eligibility: "eligible",
      requirement: "required",
      availability: "available",
      reasons: [
        {
          code: "activity_completed",
          explanation: "The retained completion evidence records this activity as completed.",
          references: ["activity-risk-return-lesson", "completion:evt-101"],
        },
        {
          code: "required_activity",
          explanation: "The approved curriculum assigns this activity to a required branch.",
          references: ["activity-risk-return-lesson", "branch-core"],
        },
      ],
    },
    {
      activity_id: "activity-risk-return-check",
      completion: "unavailable",
      eligibility: "eligible",
      requirement: "required",
      availability: "available",
      reasons: [
        {
          code: "completion_source_unavailable",
          explanation: "This assessment does not yet expose a retained completion source.",
          references: ["activity-risk-return-check", "completion:assessment"],
        },
        {
          code: "prerequisite_satisfied",
          explanation: "The required preceding lesson is recorded as completed.",
          references: ["activity-risk-return-lesson", "activity-risk-return-check"],
        },
        {
          code: "required_activity",
          explanation: "The approved curriculum assigns this activity to a required branch.",
          references: ["activity-risk-return-check", "branch-core"],
        },
      ],
    },
    {
      activity_id: "activity-diversification-reading",
      completion: "incomplete",
      eligibility: "locked",
      requirement: "optional",
      availability: "available",
      reasons: [
        {
          code: "optional_activity",
          explanation: "The approved curriculum assigns this activity only to optional branches.",
          references: [
            "activity-diversification-reading",
            "branch-explore",
            "branch-practice",
            "objective-diversification",
          ],
        },
        {
          code: "prerequisite_incomplete",
          explanation: "A preceding curriculum activity is not yet complete.",
          references: ["activity-risk-return-check", "activity-diversification-reading"],
        },
      ],
    },
    {
      activity_id: "activity-diversification-check",
      completion: "unavailable",
      eligibility: "locked",
      requirement: "optional",
      availability: "available",
      reasons: [
        {
          code: "completion_source_unavailable",
          explanation: "This assessment does not yet expose a retained completion source.",
          references: ["activity-diversification-check", "completion:assessment"],
        },
        {
          code: "prerequisite_incomplete",
          explanation: "The preceding diversification activity is not yet complete.",
          references: [
            "activity-diversification-reading",
            "activity-diversification-check",
          ],
        },
      ],
    },
    {
      activity_id: "activity-terms-glossary",
      completion: "incomplete",
      eligibility: "eligible",
      requirement: "unassigned",
      availability: "available",
      reasons: [
        {
          code: "unassigned_activity",
          explanation: "This reviewed activity is not assigned to a curriculum branch.",
          references: ["activity-terms-glossary"],
        },
        {
          code: "entry_activity",
          explanation: "This activity has no declared activity prerequisite.",
          references: ["activity-terms-glossary"],
        },
      ],
    },
  ],
  projection_digest: "2".repeat(64),
} satisfies NavigationState;

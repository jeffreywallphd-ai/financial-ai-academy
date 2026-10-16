import type { PracticePresentation } from "../../src/features/practice-activity/model";


export const practiceFixture = {
  schema_version: "1.0.0",
  placement_id: "intro-risk-return-primary",
  package_id: "intro-risk-return",
  package_version: "2.0.0",
  package_digest: "a".repeat(64),
  definition_digest: "b".repeat(64),
  practice_id: "risk-return-practice",
  practice_version: "1.0.0",
  title: "Practice risk and return basics",
  purpose:
    "Check your understanding with formative questions that do not judge an investment choice.",
  instructions: "Review each question and enter the response it asks for.",
  attempt_policy: {
    policy_id: "formative-retry",
    policy_version: "1.0.0",
    max_attempts: 3,
    resume_allowed: true,
    history_visible: true,
  },
  source_references: [
    {
      resource_id: "risk-return-reading",
      resource_version: "1.0.0",
      resource_digest: "c".repeat(64),
      title: "Risk and return reading",
    },
  ],
  review_references: [
    {
      resource_id: "risk-return-review",
      resource_version: "1.0.0",
      resource_digest: "d".repeat(64),
      title: "Review risk and return",
    },
  ],
  items: [
    {
      item_id: "risk-meaning",
      item_version: "1.0.0",
      item_type: "single_select",
      prompt: "Which statement best describes investment risk?",
      scoring_policy_id: "single-select-exact-match",
      scoring_policy_version: "1.0.0",
      max_score: 1,
      options: [
        {
          option_id: "uncertainty",
          label: "Outcomes can differ from what was expected.",
        },
        {
          option_id: "guarantee",
          label: "Every investment has a guaranteed return.",
        },
      ],
    },
    {
      item_id: "risk-factors",
      item_version: "1.0.0",
      item_type: "multiple_select",
      prompt: "Which factors can affect an investment's outcome?",
      scoring_policy_id: "multiple-select-exact-set",
      scoring_policy_version: "1.0.0",
      max_score: 1,
      options: [
        { option_id: "time", label: "Time horizon" },
        { option_id: "market", label: "Market conditions" },
        { option_id: "fees", label: "Fees and costs" },
      ],
    },
    {
      item_id: "simple-return",
      item_version: "1.0.0",
      item_type: "numeric_entry",
      prompt: "Enter the example return as a percentage.",
      scoring_policy_id: "numeric-exact-or-inclusive-range",
      scoring_policy_version: "1.0.0",
      max_score: 1,
      scale: 2,
      unit_label: "percent",
      allow_negative: true,
    },
  ],
} satisfies PracticePresentation;

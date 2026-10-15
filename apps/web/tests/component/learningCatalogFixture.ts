import type {
  LearningCatalog,
  LearningOpportunity,
} from "../../src/features/learning-catalog/model";

export const availableOpportunity = {
  schema_version: "1.0.0",
  opportunity_id: "cash-flow-basics-primary",
  placement_id: "cash-flow-basics-primary",
  destination: "/learn/placements/cash-flow-basics-primary",
  kind: "lesson",
  title: "Cash Flow Basics",
  summary:
    "Learn how cash inflows, outflows, and timing shape a simple financial plan.",
  objectives: [
    "Distinguish cash inflows from cash outflows.",
    "Explain why timing matters in a cash flow plan.",
  ],
  topics: ["cash-flow", "financial-foundations"],
  level: "introductory",
  estimated_minutes: 18,
  prerequisite_summary: "No prior lesson is required.",
  availability: "available",
  availability_reason: "The exact reviewed lesson is available.",
  package_id: "cash-flow-basics",
  package_version: "1.2.0",
  package_digest: "a".repeat(64),
  provenance: {
    published_by: "Financial AI Academy",
    published_at: "2026-10-15T12:00:00Z",
    content_reviewed_on: "2026-10-14",
    educational_use_notice:
      "General educational content; not personalized financial advice.",
  },
  source_fingerprint:
    "25d9d3d9faaad288a7519f79851e06f6eadb83ef9303af251421963eed70005e",
  projected_at: "2026-10-15T12:00:00Z",
} satisfies LearningOpportunity;

export const plannedOpportunity = {
  ...availableOpportunity,
  opportunity_id: "portfolio-project-planned",
  placement_id: "portfolio-project-planned",
  destination: "/learn/placements/portfolio-project-planned",
  kind: "project",
  title: "Portfolio Project",
  summary:
    "Review the intended scope of a future educational portfolio project before it is executable.",
  objectives: ["Describe the future project's educational boundary."],
  topics: ["portfolio-projects"],
  level: "intermediate",
  estimated_minutes: 45,
  prerequisite_summary: "Complete the financial foundations lessons first.",
  availability: "planned",
  availability_reason: "This project is planned but cannot be opened yet.",
  package_id: "portfolio-project",
  package_version: "0.1.0-preview.1",
  package_digest: "c".repeat(64),
  source_fingerprint:
    "e76837c2db1da9550954c86e1222cc23c253b556ef1bc77f338aa40c9e611342",
} satisfies LearningOpportunity;

export const learningCatalogFixture = {
  schema_version: "1.0.0",
  projection_generation:
    "deaaed6da7190fd5ef49a614cb26de64c529538c9edb3069b56b1183bca887c8",
  projected_at: "2026-10-15T12:00:00Z",
  records: [availableOpportunity, plannedOpportunity],
} satisfies LearningCatalog;

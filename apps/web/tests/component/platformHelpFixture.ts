import type {
  ContextualHelp,
  PlatformHelpSearchPage,
  PlatformHelpTopic,
} from "../../src/features/platform-help/model";

export const contextualHelpFixture: ContextualHelp = {
  schema_version: "1.0.0",
  context_key: "lesson-publication",
  context_version: "1.0.0",
  feature_label: "Lesson publication details",
  applicability: [
    {
      scope_key: "lesson-publication",
      label: "Published lesson sources, versions, and review dates",
    },
  ],
  help_references: [
    {
      topic_id: "source-and-history",
      topic_version: "1.0.0",
      purpose: "source",
      label: "How to use source and history details",
    },
    {
      topic_id: "education-not-advice",
      topic_version: "1.0.0",
      purpose: "education_boundary",
      label: "Why this is education, not investment advice",
    },
  ],
  publication: {
    state: "approved",
    reviewed_on: "2026-10-18",
    updated_at: "2026-10-18T00:00:00Z",
  },
  source_references: [
    {
      source_key: "architecture-principles",
      title: "Architecture principles",
      area: "architecture",
      source_version: "2026-10-18",
      content_fingerprint:
        "7ed7fc91381b48fb6b63c66b7f0caf24799fbe46cad8cd0762268ebb58f371ea",
    },
  ],
  context_digest:
    "69f9faa5275e5b4106f7c827692d970fac09fbaf143c0ba68020e46cc1b742c3",
};

export const platformHelpTopicFixture: PlatformHelpTopic = {
  schema_version: "1.0.0",
  topic_id: "platform-methods",
  topic_version: "1.0.0",
  topic_kind: "method",
  title: "How platform methods stay reproducible",
  summary:
    "Financial calculations use exact versioned methods, declared inputs, units, assumptions, and provenance so results can be reproduced and reviewed.",
  keywords: ["methods", "calculations", "provenance", "reproducibility"],
  body: [
    {
      node_kind: "heading",
      level: 2,
      text: "What the platform records",
    },
    {
      node_kind: "paragraph",
      text: "Each result names the method and inputs used to produce it.",
    },
    {
      node_kind: "list",
      list_kind: "unordered",
      items: [
        "Each method has a stable ID and version.",
        "Results retain the input lineage needed for review.",
      ],
    },
    {
      node_kind: "note",
      note_kind: "limitation",
      text: "Calculated values are not observed market facts or personal investment advice.",
    },
    {
      node_kind: "topic_reference",
      topic_id: "education-not-advice",
      topic_version: "1.0.0",
      label: "Read the education boundary",
    },
  ],
  applicability: [
    {
      scope_key: "financial-methods",
      label: "Financial calculations, simulations, scenarios, and backtests",
    },
  ],
  publication: {
    state: "approved",
    reviewed_on: "2026-10-18",
    updated_at: "2026-10-18T00:00:00Z",
  },
  source_references: [
    {
      source_key: "financial-method-architecture",
      title: "Financial method and simulation architecture",
      area: "method",
      source_version: "2026-10-18",
      content_fingerprint:
        "24aca8e940ceb2d31232d3cf27542d5627fe179325eecc75428e384c6812e405",
    },
  ],
  related_topics: [
    {
      topic_id: "education-not-advice",
      topic_version: "1.0.0",
      relationship: "see_also",
    },
  ],
  topic_digest:
    "6655d70772dcdac738a4320257aa707a72a913b3e470cb902510509c95260d0f",
};

export const platformHelpSearchFixture: PlatformHelpSearchPage = {
  schema_version: "1.0.0",
  corpus_digest:
    "3333333333333333333333333333333333333333333333333333333333333333",
  query: "calculations",
  topic_kind: "method",
  results: [
    {
      topic_id: platformHelpTopicFixture.topic_id,
      topic_version: platformHelpTopicFixture.topic_version,
      topic_kind: platformHelpTopicFixture.topic_kind,
      title: platformHelpTopicFixture.title,
      summary: platformHelpTopicFixture.summary,
      applicability: platformHelpTopicFixture.applicability,
      publication: platformHelpTopicFixture.publication,
      source_references: platformHelpTopicFixture.source_references,
      topic_digest: platformHelpTopicFixture.topic_digest,
    },
  ],
  next_cursor: "eyJ2IjoxfQ",
};

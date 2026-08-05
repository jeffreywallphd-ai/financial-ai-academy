import type { Lesson } from "../../src/features/lesson-reading/model";


export const lessonFixture = {
  placement_id: "intro-risk-return-primary",
  package_id: "intro-risk-return",
  package_version: "1.0.0",
  package_digest:
    "576d543b404a7f70f2e5bebee55c32a3f945d8e8da73654c43ef92e656aee008",
  title: "Understanding Risk and Return",
  objectives: [
    "Explain the relationship between investment risk and expected return.",
    "Compare investments without treating past performance as a promise.",
  ],
  body: [
    {
      kind: "heading",
      level: 2,
      children: [{ kind: "text", value: "Risk and expected return" }],
    },
    {
      kind: "paragraph",
      children: [
        { kind: "text", value: "Investing involves " },
        {
          kind: "strong",
          children: [{ kind: "text", value: "uncertainty" }],
        },
        { kind: "text", value: " and " },
        {
          kind: "emphasis",
          children: [{ kind: "text", value: "tradeoffs" }],
        },
        { kind: "soft_break" },
        { kind: "text", value: "that deserve careful study." },
        { kind: "hard_break" },
        {
          kind: "source_link",
          source_id: "sec-risk-return",
          href: "https://www.investor.gov/introduction-investing",
          children: [{ kind: "text", value: "Review the source" }],
        },
      ],
    },
    {
      kind: "bullet_list",
      items: [
        {
          blocks: [
            {
              kind: "paragraph",
              children: [
                { kind: "code", value: "diversification" },
                { kind: "text", value: "Diversification changes risk." },
              ],
            },
          ],
        },
      ],
    },
    {
      kind: "ordered_list",
      start: 1,
      items: [
        {
          blocks: [
            {
              kind: "paragraph",
              children: [
                { kind: "code", value: "expected return" },
              ],
            },
          ],
        },
      ],
    },
    {
      kind: "code_block",
      code: "expected return = weighted outcomes",
      language: "text",
    },
    { kind: "thematic_break" },
    {
      kind: "paragraph",
      children: [
        {
          kind: "asset_image",
          asset_id: "risk-spectrum",
          alt_text: "A labeled spectrum of investment risk.",
        },
      ],
    },
  ],
  sources: [
    {
      source_id: "sec-risk-return",
      title: "Introduction to investing",
      publisher: "U.S. Securities and Exchange Commission",
      locator: "https://www.investor.gov/introduction-investing",
      reviewed_on: "2026-08-04",
      license_note: "Linked for educational reference.",
    },
  ],
  assets: [
    {
      asset_id: "risk-spectrum",
      media_type: "image/png",
      sha256:
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
      alt_text: "A labeled spectrum of investment risk.",
      locator: "/api/v1/content/assets/risk-spectrum",
    },
  ],
  provenance: {
    published_by: "Financial AI Academy",
    published_at: "2026-08-04T12:00:00Z",
    content_reviewed_on: "2026-08-04",
    educational_use_notice:
      "General educational content; not personalized investment advice.",
  },
} satisfies Lesson;

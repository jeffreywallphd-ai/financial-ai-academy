import { createFinancialAcademyApiClient } from "../../src/generated/api-client";


const client = createFinancialAcademyApiClient(
  "http://127.0.0.1:8000",
);

void client.GET("/api/v1/curriculum/opportunities");

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

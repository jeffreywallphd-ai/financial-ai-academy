import { createFinancialAcademyApiClient } from "../../src/generated/api-client";


const client = createFinancialAcademyApiClient(
  "http://127.0.0.1:8000",
);

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

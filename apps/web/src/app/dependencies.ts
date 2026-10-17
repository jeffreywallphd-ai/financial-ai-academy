import { createPresentationProfileReader } from "../features/presentation-preferences/api";
import { createFinancialAcademyApiClient } from "../generated/api-client";
import { SingleProfileSession } from "../platform/auth/singleProfileSession";


export const apiClient = createFinancialAcademyApiClient(window.location.origin);
export const singleProfileSession = new SingleProfileSession(apiClient);
export const presentationProfileReader = createPresentationProfileReader(
  apiClient,
  singleProfileSession,
);

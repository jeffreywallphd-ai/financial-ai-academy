import { createBrowserRouter, redirect } from "react-router";

import { createFinancialAcademyApiClient } from "../generated/api-client";
import { StatusPanel } from "../components/StatusPanel";
import {
  createCurriculumActivityLauncher,
  createCurriculumGraphLoader,
} from "../features/curriculum-graph/api";
import {
  CurriculumGraphLoadingState,
  CurriculumGraphRoute,
} from "../features/curriculum-graph/CurriculumGraphRoute";
import {
  createLearningCatalogLoader,
  createLearningOpportunityComparisonLoader,
  createLearningOpportunityDetailLoader,
} from "../features/learning-catalog/api";
import {
  LearningCatalogLoadingState,
  LearningCatalogRoute,
} from "../features/learning-catalog/LearningCatalogRoute";
import {
  LearningOpportunityDetailLoadingState,
  LearningOpportunityDetailRoute,
} from "../features/learning-catalog/LearningOpportunityDetailRoute";
import {
  LearningOpportunityComparisonLoadingState,
  LearningOpportunityComparisonRoute,
} from "../features/learning-catalog/LearningOpportunityComparisonRoute";
import { createLessonLoader } from "../features/lesson-reading/api";
import {
  LessonLoadingState,
  LessonRoute,
} from "../features/lesson-reading/LessonRoute";
import { SingleProfileSession } from "../platform/auth/singleProfileSession";
import { AppShell } from "./AppShell";

const client = createFinancialAcademyApiClient(window.location.origin);
const session = new SingleProfileSession(client);
const learningCatalogLoader = createLearningCatalogLoader(client, session);
const learningOpportunityDetailLoader = createLearningOpportunityDetailLoader(
  client,
  session,
);
const learningOpportunityComparisonLoader =
  createLearningOpportunityComparisonLoader(client, session);
const lessonLoader = createLessonLoader(client, session);
const curriculumGraphLoader = createCurriculumGraphLoader(client, session);
const curriculumActivityLauncher = createCurriculumActivityLauncher(
  client,
  session,
);

function CurriculumGraphRouteWithDependencies() {
  return (
    <CurriculumGraphRoute launchActivity={curriculumActivityLauncher} />
  );
}

function UnexpectedRouteError() {
  return (
    <StatusPanel
      actionLabel="Reload page"
      description="The page could not be completed safely. No private or technical details were displayed."
      icon="error-circle"
      onAction={() => window.location.reload()}
      title="Page unavailable"
      tone="danger"
    />
  );
}

function NotFoundRoute() {
  return (
    <StatusPanel
      description="This page is not part of the current learning experience."
      icon="info-circle"
      title="Page not found"
      tone="info"
    />
  );
}

export const router = createBrowserRouter([
  {
    path: "/",
    Component: AppShell,
    ErrorBoundary: UnexpectedRouteError,
    children: [
      {
        index: true,
        loader: () => redirect("/learn"),
        Component: LearningCatalogLoadingState,
        HydrateFallback: LearningCatalogLoadingState,
      },
      {
        path: "learn",
        loader: learningCatalogLoader,
        Component: LearningCatalogRoute,
        HydrateFallback: LearningCatalogLoadingState,
      },
      {
        path: "learn/opportunities/compare",
        loader: learningOpportunityComparisonLoader,
        Component: LearningOpportunityComparisonRoute,
        HydrateFallback: LearningOpportunityComparisonLoadingState,
      },
      {
        path: "learn/opportunities/:opportunityId",
        loader: learningOpportunityDetailLoader,
        Component: LearningOpportunityDetailRoute,
        HydrateFallback: LearningOpportunityDetailLoadingState,
      },
      {
        path: "learn/placements/:placementId",
        loader: lessonLoader,
        Component: LessonRoute,
        HydrateFallback: LessonLoadingState,
      },
      {
        path: "learn/curricula/:curriculumId/versions/:curriculumVersion",
        loader: curriculumGraphLoader,
        Component: CurriculumGraphRouteWithDependencies,
        HydrateFallback: CurriculumGraphLoadingState,
      },
      {
        path: "*",
        Component: NotFoundRoute,
      },
    ],
  },
]);

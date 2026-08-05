import {
  createBrowserRouter,
  redirect,
} from "react-router";

import { createFinancialAcademyApiClient } from "../generated/api-client";
import { StatusPanel } from "../components/StatusPanel";
import { createLessonLoader } from "../features/lesson-reading/api";
import {
  LessonLoadingState,
  LessonRoute,
} from "../features/lesson-reading/LessonRoute";
import { SingleProfileSession } from "../platform/auth/singleProfileSession";
import { AppShell } from "./AppShell";


const client = createFinancialAcademyApiClient(window.location.origin);
const session = new SingleProfileSession(client);
const lessonLoader = createLessonLoader(client, session);

function UnexpectedRouteError() {
  return (
    <StatusPanel
      actionLabel="Reload lesson"
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
    HydrateFallback: LessonLoadingState,
    children: [
      {
        index: true,
        loader: () =>
          redirect(
            "/learn/placements/intro-risk-return-primary",
          ),
      },
      {
        path: "learn/placements/:placementId",
        loader: lessonLoader,
        Component: LessonRoute,
      },
      {
        path: "*",
        Component: NotFoundRoute,
      },
    ],
  },
]);

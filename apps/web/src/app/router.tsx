import { createBrowserRouter, redirect } from "react-router";

import { StatusPanel } from "../components/StatusPanel";
import {
  createAccountableHistoryExporter,
  createAccountableHistoryReader,
} from "../features/accountable-history/api";
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
import {
  createPracticeActivityLoader,
  createPracticeActivitySubmitter,
  createPracticeDraftSaver,
  createPracticeProgressReader,
} from "../features/practice-activity/api";
import {
  PracticeActivityLoadingState,
  PracticeActivityRoute,
} from "../features/practice-activity/PracticeActivityRoute";
import {
  createProjectArtifactDownloader,
  createProjectCreateAction,
  createProjectCreateLoader,
  createProjectDetailLoader,
  createProjectListLoader,
  createProjectLearningAction,
  createProjectLearningLoader,
  createProjectSnapshotExporter,
  createProjectWorkspaceAction,
} from "../features/project-workspace/api";
import {
  ProjectCreateRoute,
  ProjectDetailRoute,
  ProjectListRoute,
  ProjectLearningRoute,
  ProjectLoadingState,
} from "../features/project-workspace/ProjectRoutes";
import {
  createPersonalWorkspaceAction,
  createPersonalWorkspaceExporter,
  createPersonalWorkspaceLoader,
  createSaveLearningLoader,
} from "../features/personal-workspace/api";
import {
  PersonalWorkspaceLoadingState,
  PersonalWorkspaceRoute,
  SaveLearningRoute,
} from "../features/personal-workspace/PersonalWorkspaceRoutes";
import {
  createLearnerPreferencesAction,
  createLearnerPreferencesExporter,
  createLearnerPreferencesLoader,
} from "../features/learner-preferences/api";
import {
  LearnerPreferencesLoadingState,
  LearnerPreferencesRoute,
} from "../features/learner-preferences/LearnerPreferencesRoute";
import {
  createPresentationPreferencesAction,
  createPresentationPreferencesExporter,
  createPresentationPreferencesLoader,
} from "../features/presentation-preferences/api";
import {
  PresentationPreferencesLoadingState,
  PresentationPreferencesRoute,
} from "../features/presentation-preferences/PresentationPreferencesRoute";
import {
  createAssistancePreferencesAction,
  createAssistancePreferencesExporter,
  createAssistancePreferencesLoader,
  createLocalReminderExporter,
} from "../features/assistance-preferences/api";
import {
  AssistancePreferencesLoadingState,
  AssistancePreferencesRoute,
} from "../features/assistance-preferences/AssistancePreferencesRoute";
import {
  createContextualHelpReader,
  createFeatureGuidanceReader,
  createPlatformHelpSearchLoader,
  createPlatformHelpTopicLoader,
} from "../features/platform-help/api";
import {
  PlatformHelpLoadingState,
  PlatformHelpSearchRoute,
  PlatformHelpTopicRoute,
} from "../features/platform-help/PlatformHelpRoute";
import { AppShell } from "./AppShell";
import {
  apiClient as client,
  singleProfileSession as session,
} from "./dependencies";

const learningCatalogLoader = createLearningCatalogLoader(client, session);
const learningOpportunityDetailLoader = createLearningOpportunityDetailLoader(
  client,
  session,
);
const learningOpportunityComparisonLoader =
  createLearningOpportunityComparisonLoader(client, session);
const lessonLoader = createLessonLoader(client, session);
const accountableHistoryReader = createAccountableHistoryReader(
  client,
  session,
);
const accountableHistoryExporter = createAccountableHistoryExporter(
  client,
  session,
);
const practiceActivityLoader = createPracticeActivityLoader(client, session);
const practiceActivitySubmitter = createPracticeActivitySubmitter(
  client,
  session,
);
const practiceDraftSaver = createPracticeDraftSaver(client, session);
const practiceProgressReader = createPracticeProgressReader(client, session);
const curriculumGraphLoader = createCurriculumGraphLoader(client, session);
const curriculumActivityLauncher = createCurriculumActivityLauncher(
  client,
  session,
);
const projectListLoader = createProjectListLoader(client, session);
const projectDetailLoader = createProjectDetailLoader(client, session);
const projectWorkspaceAction = createProjectWorkspaceAction(client, session);
const projectArtifactDownloader = createProjectArtifactDownloader(
  client,
  session,
);
const projectSnapshotExporter = createProjectSnapshotExporter(client, session);
const projectCreateLoader = createProjectCreateLoader(client, session);
const projectCreateAction = createProjectCreateAction(client, session);
const projectLearningLoader = createProjectLearningLoader(client, session);
const projectLearningAction = createProjectLearningAction(client, session);
const personalWorkspaceLoader = createPersonalWorkspaceLoader(client, session);
const saveLearningLoader = createSaveLearningLoader(client, session);
const personalWorkspaceAction = createPersonalWorkspaceAction(client, session);
const personalWorkspaceExporter = createPersonalWorkspaceExporter(
  client,
  session,
);
const learnerPreferencesLoader = createLearnerPreferencesLoader(
  client,
  session,
);
const learnerPreferencesAction = createLearnerPreferencesAction(
  client,
  session,
);
const learnerPreferencesExporter = createLearnerPreferencesExporter(
  client,
  session,
);
const presentationPreferencesLoader = createPresentationPreferencesLoader(
  client,
  session,
);
const presentationPreferencesAction = createPresentationPreferencesAction(
  client,
  session,
);
const presentationPreferencesExporter = createPresentationPreferencesExporter(
  client,
  session,
);
const currentTime = () => new Date().toISOString();
const assistancePreferencesLoader = createAssistancePreferencesLoader(
  client,
  session,
  window.localStorage,
  currentTime,
);
const assistancePreferencesAction = createAssistancePreferencesAction(
  client,
  session,
  window.localStorage,
  currentTime,
);
const assistancePreferencesExporter = createAssistancePreferencesExporter(
  client,
  session,
);
const localReminderExporter = createLocalReminderExporter(
  window.localStorage,
  currentTime,
);
const platformHelpSearchLoader = createPlatformHelpSearchLoader(
  client,
  session,
);
const platformHelpTopicLoader = createPlatformHelpTopicLoader(client, session);
const contextualHelpReader = createContextualHelpReader(client, session);
const featureGuidanceReader = createFeatureGuidanceReader(client, session);

function LessonRouteWithDependencies() {
  return (
    <LessonRoute
      exportAccountableHistory={accountableHistoryExporter}
      readAccountableHistory={accountableHistoryReader}
      readContextualHelp={contextualHelpReader}
      readFeatureGuidance={featureGuidanceReader}
    />
  );
}

function CurriculumGraphRouteWithDependencies() {
  return <CurriculumGraphRoute launchActivity={curriculumActivityLauncher} />;
}

function PracticeActivityRouteWithDependencies() {
  return (
    <PracticeActivityRoute
      readContextualHelp={contextualHelpReader}
      readFeatureGuidance={featureGuidanceReader}
      readProgress={practiceProgressReader}
      saveDraft={practiceDraftSaver}
      submitPractice={practiceActivitySubmitter}
    />
  );
}

function ProjectDetailRouteWithDependencies() {
  return (
    <ProjectDetailRoute
      downloadArtifact={projectArtifactDownloader}
      exportSnapshot={projectSnapshotExporter}
      readContextualHelp={contextualHelpReader}
      readFeatureGuidance={featureGuidanceReader}
    />
  );
}

function PersonalWorkspaceRouteWithDependencies() {
  return (
    <PersonalWorkspaceRoute
      exportWorkspace={personalWorkspaceExporter}
      readFeatureGuidance={featureGuidanceReader}
    />
  );
}

function LearnerPreferencesRouteWithDependencies() {
  return (
    <LearnerPreferencesRoute exportPreferences={learnerPreferencesExporter} />
  );
}

function PresentationPreferencesRouteWithDependencies() {
  return (
    <PresentationPreferencesRoute
      exportPreferences={presentationPreferencesExporter}
    />
  );
}

function AssistancePreferencesRouteWithDependencies() {
  return (
    <AssistancePreferencesRoute
      exportLocalReminder={localReminderExporter}
      exportPreferences={assistancePreferencesExporter}
      readContextualHelp={contextualHelpReader}
      readFeatureGuidance={featureGuidanceReader}
    />
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
        path: "preferences/learning",
        loader: learnerPreferencesLoader,
        action: learnerPreferencesAction,
        Component: LearnerPreferencesRouteWithDependencies,
        HydrateFallback: LearnerPreferencesLoadingState,
      },
      {
        path: "preferences/display",
        loader: presentationPreferencesLoader,
        action: presentationPreferencesAction,
        Component: PresentationPreferencesRouteWithDependencies,
        HydrateFallback: PresentationPreferencesLoadingState,
      },
      {
        path: "preferences/assistance",
        loader: assistancePreferencesLoader,
        action: assistancePreferencesAction,
        Component: AssistancePreferencesRouteWithDependencies,
        HydrateFallback: AssistancePreferencesLoadingState,
      },
      {
        path: "saved-learning",
        loader: personalWorkspaceLoader,
        action: personalWorkspaceAction,
        Component: PersonalWorkspaceRouteWithDependencies,
        HydrateFallback: PersonalWorkspaceLoadingState,
      },
      {
        path: "saved-learning/new",
        loader: saveLearningLoader,
        action: personalWorkspaceAction,
        Component: SaveLearningRoute,
        HydrateFallback: PersonalWorkspaceLoadingState,
      },
      {
        path: "projects",
        loader: projectListLoader,
        Component: ProjectListRoute,
        HydrateFallback: ProjectLoadingState,
      },
      {
        path: "projects/new",
        loader: projectCreateLoader,
        action: projectCreateAction,
        Component: ProjectCreateRoute,
        HydrateFallback: ProjectLoadingState,
      },
      {
        path: "projects/:projectId/learning",
        loader: projectLearningLoader,
        action: projectLearningAction,
        Component: ProjectLearningRoute,
        HydrateFallback: ProjectLoadingState,
      },
      {
        path: "projects/:projectId",
        loader: projectDetailLoader,
        action: projectWorkspaceAction,
        Component: ProjectDetailRouteWithDependencies,
        HydrateFallback: ProjectLoadingState,
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
        Component: LessonRouteWithDependencies,
        HydrateFallback: LessonLoadingState,
      },
      {
        path: "learn/placements/:placementId/practice",
        loader: practiceActivityLoader,
        Component: PracticeActivityRouteWithDependencies,
        HydrateFallback: PracticeActivityLoadingState,
      },
      {
        path: "learn/curricula/:curriculumId/versions/:curriculumVersion",
        loader: curriculumGraphLoader,
        Component: CurriculumGraphRouteWithDependencies,
        HydrateFallback: CurriculumGraphLoadingState,
      },
      {
        path: "help",
        loader: platformHelpSearchLoader,
        Component: PlatformHelpSearchRoute,
        HydrateFallback: PlatformHelpLoadingState,
      },
      {
        path: "help/topics/:topicId/versions/:topicVersion",
        loader: platformHelpTopicLoader,
        Component: PlatformHelpTopicRoute,
        HydrateFallback: PlatformHelpLoadingState,
      },
      {
        path: "*",
        Component: NotFoundRoute,
      },
    ],
  },
]);

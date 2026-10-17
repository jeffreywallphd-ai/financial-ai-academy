import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { RouterProvider } from "react-router/dom";

import "../design-system/tokens.css";
import "../design-system/icons/icons.css";
import "../styles/base.css";
import "../styles/app.css";
import "../styles/learning-catalog.css";
import "../styles/curriculum-graph.css";
import "../styles/lesson-reading.css";
import "../styles/practice-activity.css";
import "../styles/project-workspace.css";
import "../styles/personal-workspace.css";
import "../styles/learner-preferences.css";
import "../styles/presentation-preferences.css";
import { PresentationProvider } from "../platform/presentation/presentation";
import { ThemeProvider } from "../platform/theme/theme";
import { presentationProfileReader } from "./dependencies";
import { router } from "./router";


const rootElement = document.getElementById("root");
if (!rootElement) {
  throw new Error("Application root is unavailable.");
}

createRoot(rootElement).render(
  <StrictMode>
    <ThemeProvider>
      <PresentationProvider readProfile={presentationProfileReader}>
        <RouterProvider
          router={router}
        />
      </PresentationProvider>
    </ThemeProvider>
  </StrictMode>,
);

import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { RouterProvider } from "react-router/dom";

import "../design-system/tokens.css";
import "../design-system/icons/icons.css";
import "../styles/base.css";
import "../styles/app.css";
import "../styles/lesson-reading.css";
import { ThemeProvider } from "../platform/theme/theme";
import { router } from "./router";


const rootElement = document.getElementById("root");
if (!rootElement) {
  throw new Error("Application root is unavailable.");
}

createRoot(rootElement).render(
  <StrictMode>
    <ThemeProvider>
      <RouterProvider
        router={router}
      />
    </ThemeProvider>
  </StrictMode>,
);

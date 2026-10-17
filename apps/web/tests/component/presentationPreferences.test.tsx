import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { createMemoryRouter, RouterProvider } from "react-router";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { PresentationPreferencesPage } from "../../src/features/presentation-preferences/PresentationPreferencesPage";
import type {
  PresentationPreferenceExport,
  PresentationPreferenceHistory,
  PresentationPreferenceProfile,
  PresentationPreferencesActionState,
  PresentationPreferencesExporter,
} from "../../src/features/presentation-preferences/model";
import { PresentationProvider } from "../../src/platform/presentation/presentation";
import { ThemeProvider } from "../../src/platform/theme/theme";


const profileFixture: PresentationPreferenceProfile = {
  schema_version: "1.0.0",
  profile_id: "profile.display-1",
  learner_id: "11111111-1111-4111-8111-111111111111",
  revision: 4,
  text_size: "larger",
  text_spacing: "increased",
  reading_width: "focused",
  motion: "reduce",
  created_at: "2026-10-17T20:00:00Z",
  updated_at: "2026-10-17T20:05:00Z",
  profile_digest: "a".repeat(64),
};

const historyFixture: PresentationPreferenceHistory = {
  schema_version: "1.0.0",
  profile_id: profileFixture.profile_id,
  current_revision: profileFixture.revision,
  changes: [{
    schema_version: "1.0.0",
    revision: 4,
    operation: "replace_preferences",
    object_kind: "profile",
    object_id: null,
    occurred_at: profileFixture.updated_at,
    resulting_profile_digest: profileFixture.profile_digest,
  }],
};

const exportFixture: PresentationPreferenceExport = {
  schema_version: "1.0.0",
  purpose: "A portable copy of your display choices.",
  limitations: ["These choices are not medical or competency evidence."],
  exported_at: "2026-10-17T20:06:00Z",
  profile: profileFixture,
  history: historyFixture,
};

function renderPage({
  actionState,
  exporter = async () => ({ status: "unavailable" }),
  profile = profileFixture,
  submissions = [],
}: {
  actionState?: PresentationPreferencesActionState;
  exporter?: PresentationPreferencesExporter;
  profile?: PresentationPreferenceProfile;
  submissions?: FormData[];
} = {}) {
  const router = createMemoryRouter([{
    path: "/preferences/display",
    action: async ({ request }) => {
      submissions.push(await request.formData());
      return null;
    },
    element: (
      <ThemeProvider>
        <PresentationProvider readProfile={async () => profile}>
          <PresentationPreferencesPage
            actionState={actionState}
            busy={false}
            exportPreferences={exporter}
            history={{ ...historyFixture, profile_id: profile.profile_id, current_revision: profile.revision }}
            profile={profile}
          />
        </PresentationProvider>
      </ThemeProvider>
    ),
  }], { initialEntries: ["/preferences/display"] });
  return render(<RouterProvider router={router} />);
}

beforeEach(() => {
  window.localStorage.clear();
});

describe("Display and accessibility page", () => {
  it("uses plain task language and keeps exact records behind a disclosure", async () => {
    renderPage();

    expect(screen.getByRole("heading", { level: 1, name: "Display and accessibility" })).toBeVisible();
    expect(screen.getByRole("heading", { name: "These choices change presentation only" })).toBeVisible();
    expect(screen.getByText(/do not describe a medical condition, measure competency/i)).toBeVisible();
    expect(screen.getByText(/Theme is stored only in this browser/i)).toBeVisible();
    expect(screen.getByText("Technical record")).toBeVisible();
    expect(screen.queryByText(profileFixture.profile_digest)).not.toBeVisible();

    await userEvent.setup().click(screen.getByText("Technical record"));
    expect(screen.getByText(profileFixture.profile_digest)).toBeVisible();
  });

  it("previews complete choices immediately and restores the accepted profile on cancel", async () => {
    renderPage();
    await waitFor(() => expect(document.documentElement).toHaveAttribute("data-text-size", "larger"));
    const user = userEvent.setup();

    await user.click(screen.getByRole("radio", { name: /Use the standard readable size/i }));
    expect(document.documentElement).toHaveAttribute("data-text-size", "default");
    expect(screen.getByText("Previewing unsaved choices.")).toBeVisible();

    await user.click(screen.getByRole("button", { name: "Cancel preview" }));
    expect(document.documentElement).toHaveAttribute("data-text-size", "larger");
    expect(screen.getByText("Saved choices are in use.")).toBeVisible();
  });

  it("submits one complete replacement using the current revision and no learner selector", async () => {
    const submissions: FormData[] = [];
    renderPage({ submissions });
    const user = userEvent.setup();

    await user.click(screen.getByRole("radio", { name: /Use the standard readable size/i }));
    await user.click(screen.getByRole("radio", { name: /Use the standard reading rhythm/i }));
    await user.click(screen.getByRole("radio", { name: /Use the standard reading width/i }));
    await user.click(screen.getByRole("radio", { name: /Follow your device setting/i }));
    await user.click(screen.getByRole("button", { name: "Save display choices" }));

    await waitFor(() => expect(submissions).toHaveLength(1));
    const entries = Object.fromEntries(submissions[0]!.entries());
    expect(entries).toMatchObject({
      form_intent: "save",
      operation: "replace_preferences",
      expected_revision: "4",
      text_size: "default",
      text_spacing: "default",
      reading_width: "standard",
      motion: "system",
    });
    expect(entries.idempotency_key).toMatch(/^[a-z0-9][a-z0-9._-]{2,63}$/);
    expect(entries).not.toHaveProperty("learner_id");
  });

  it("resets saved choices without resetting the browser-local theme", async () => {
    const submissions: FormData[] = [];
    renderPage({ submissions });
    const user = userEvent.setup();

    await user.selectOptions(screen.getByLabelText("Theme"), "dark");
    expect(document.documentElement).toHaveAttribute("data-theme", "dark");
    await user.click(screen.getByRole("checkbox", { name: /resets the four saved display choices/i }));
    await user.click(screen.getByRole("button", { name: "Reset saved display choices" }));

    await waitFor(() => expect(submissions).toHaveLength(1));
    expect(Object.fromEntries(submissions[0]!.entries())).toMatchObject({
      form_intent: "reset",
      operation: "reset_profile",
      confirm_reset: "reset",
      expected_revision: "4",
    });
    expect(document.documentElement).toHaveAttribute("data-theme", "dark");

    await user.click(screen.getByRole("button", { name: "Use device theme" }));
    expect(document.documentElement).toHaveAttribute("data-theme", "system");
  });

  it("downloads only the matching validated export", async () => {
    const createObjectURL = vi.fn().mockReturnValue("blob:display-settings");
    const revokeObjectURL = vi.fn();
    const click = vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => undefined);
    Object.defineProperty(URL, "createObjectURL", { configurable: true, value: createObjectURL });
    Object.defineProperty(URL, "revokeObjectURL", { configurable: true, value: revokeObjectURL });
    const exporter = vi.fn<PresentationPreferencesExporter>().mockResolvedValue({
      status: "ready",
      content: JSON.stringify(exportFixture),
      export: exportFixture,
      fileName: "display-accessibility-settings.json",
    });
    renderPage({ exporter });

    await userEvent.setup().click(screen.getByRole("button", { name: "Download display choices" }));

    await waitFor(() => expect(exporter).toHaveBeenCalledWith(4, profileFixture.profile_digest));
    expect(createObjectURL).toHaveBeenCalledWith(expect.any(Blob));
    expect(click).toHaveBeenCalledOnce();
    expect(revokeObjectURL).toHaveBeenCalledWith("blob:display-settings");
    expect(screen.getByText("Your download is ready.")).toBeVisible();
  });

  it("moves focus to safe recovery guidance after a stale write", async () => {
    renderPage({
      actionState: {
        status: "error",
        kind: "stale",
        intent: "save",
      },
    });

    const heading = await screen.findByRole("heading", { name: "Display choices changed" });
    await waitFor(() => expect(heading).toHaveFocus());
    expect(screen.getByText(/Reload the page, review the current choices/i)).toBeVisible();
  });
});

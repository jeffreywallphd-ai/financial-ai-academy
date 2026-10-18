import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { createMemoryRouter, RouterProvider } from "react-router";
import { describe, expect, it, vi } from "vitest";

import { AssistancePreferencesPage } from "../../src/features/assistance-preferences/AssistancePreferencesPage";
import type {
  AssistancePreferenceHistory,
  AssistancePreferenceProfile,
  AssistancePreferencesActionState,
  AssistancePreferencesExporter,
  AssistancePreferencesRouteState,
  LocalReminderExporter,
} from "../../src/features/assistance-preferences/model";


const profile: AssistancePreferenceProfile = {
  schema_version: "1.0.0",
  profile_id: "profile.assistance-1",
  learner_id: "11111111-1111-4111-8111-111111111111",
  revision: 2,
  assistance_mode: "on_request",
  created_at: "2026-10-17T20:00:00Z",
  updated_at: "2026-10-17T20:05:00Z",
  profile_digest: "a".repeat(64),
};

const history: AssistancePreferenceHistory = {
  schema_version: "1.0.0",
  profile_id: profile.profile_id,
  current_revision: profile.revision,
  changes: [{
    schema_version: "1.0.0",
    revision: 2,
    operation: "replace_preferences",
    object_kind: "profile",
    object_id: null,
    occurred_at: profile.updated_at,
    resulting_profile_digest: profile.profile_digest,
  }],
};

const readyState: AssistancePreferencesRouteState = {
  server: {
    status: "ready",
    profile,
    history,
    export: {
      schema_version: "1.0.0",
      purpose: "A portable copy of your AI-help choice.",
      limitations: ["This choice does not enable an AI service."],
      exported_at: "2026-10-17T20:06:00Z",
      profile,
      history,
    },
  },
  local: {
    status: "ready",
    envelope: {
      schema_version: "1.0.0",
      revision: 2,
      reminder_mode: "in_app_when_available",
      updated_at: "2026-10-17T20:05:00Z",
      changes: [{
        schema_version: "1.0.0",
        revision: 2,
        operation: "replace_preference",
        occurred_at: "2026-10-17T20:05:00Z",
      }],
      integrity_code: "b".repeat(64),
    },
  },
};

function renderPage({
  actionState,
  localExporter = async () => ({ status: "unavailable" }),
  serverExporter = async () => ({ status: "unavailable" }),
  state = readyState,
  submissions = [],
}: {
  actionState?: AssistancePreferencesActionState;
  localExporter?: LocalReminderExporter;
  serverExporter?: AssistancePreferencesExporter;
  state?: AssistancePreferencesRouteState;
  submissions?: FormData[];
} = {}) {
  const router = createMemoryRouter([{
    path: "/preferences/assistance",
    action: async ({ request }) => {
      submissions.push(await request.formData());
      return null;
    },
    element: (
      <AssistancePreferencesPage
        actionState={actionState}
        busy={false}
        exportLocalReminder={localExporter}
        exportPreferences={serverExporter}
        onRetry={() => undefined}
        state={state}
      />
    ),
  }], { initialEntries: ["/preferences/assistance"] });
  return render(<RouterProvider router={router} />);
}

describe("AI help and reminders page", () => {
  it("leads with availability and purpose while keeping technical facts optional", async () => {
    renderPage();

    expect(screen.getByRole("heading", { level: 1, name: "AI help and reminders" })).toBeVisible();
    expect(screen.getByRole("heading", { name: "Nothing runs in the background" })).toBeVisible();
    expect(screen.getByText(/AI help is not available on this screen/i)).toBeVisible();
    expect(screen.getAllByText(/Reminders are not available yet/i)).toHaveLength(2);
    expect(screen.getByText(/not permission to share data or use an AI provider/i)).toBeVisible();
    expect(screen.queryByText(profile.profile_digest)).not.toBeVisible();

    await userEvent.setup().click(screen.getByText("Technical record for AI-help choice"));
    expect(screen.getByText(profile.profile_digest)).toBeVisible();
  });

  it("submits server and local choices through separate closed forms", async () => {
    const submissions: FormData[] = [];
    renderPage({ submissions });
    const user = userEvent.setup();

    await user.click(screen.getByRole("radio", { name: /Do not offer an AI-help action/i }));
    await user.click(screen.getByRole("button", { name: "Save AI-help choice" }));
    await waitFor(() => expect(submissions).toHaveLength(1));
    const server = Object.fromEntries(submissions[0]!.entries());
    expect(server).toMatchObject({
      assistance_mode: "off",
      expected_revision: "2",
      form_intent: "server-save",
      operation: "replace_preferences",
    });
    expect(server.idempotency_key).toMatch(/^[a-z0-9][a-z0-9._-]{2,63}$/);
    expect(server).not.toHaveProperty("learner_id");
    expect(server).not.toHaveProperty("reminder_mode");

    await user.click(screen.getByRole("radio", { name: /Store no future reminder request/i }));
    await user.click(screen.getByRole("button", { name: "Save this-browser choice" }));
    await waitFor(() => expect(submissions).toHaveLength(2));
    expect(Object.fromEntries(submissions[1]!.entries())).toEqual({
      form_intent: "local-save",
      reminder_mode: "off",
    });
  });

  it("requires separate reset confirmations", async () => {
    const submissions: FormData[] = [];
    renderPage({ submissions });
    const user = userEvent.setup();

    expect(screen.getByRole("button", { name: "Reset AI-help choice" })).toBeDisabled();
    await user.click(screen.getByRole("checkbox", { name: /resets only the learner-owned AI-help choice/i }));
    await user.click(screen.getByRole("button", { name: "Reset AI-help choice" }));
    await waitFor(() => expect(submissions).toHaveLength(1));
    expect(Object.fromEntries(submissions[0]!.entries())).toMatchObject({
      confirm_reset: "reset",
      form_intent: "server-reset",
      operation: "reset_profile",
    });

    expect(screen.getByRole("button", { name: "Reset this-browser choice" })).toBeDisabled();
    await user.click(screen.getByRole("checkbox", { name: /resets only the reminder choice in this browser/i }));
    await user.click(screen.getByRole("button", { name: "Reset this-browser choice" }));
    await waitFor(() => expect(submissions).toHaveLength(2));
    expect(Object.fromEntries(submissions[1]!.entries())).toEqual({
      confirm_reset: "reset",
      form_intent: "local-reset",
    });
  });

  it("creates visibly separate downloads", async () => {
    const createObjectURL = vi.fn()
      .mockReturnValueOnce("blob:server")
      .mockReturnValueOnce("blob:local");
    const revokeObjectURL = vi.fn();
    const click = vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => undefined);
    Object.defineProperty(URL, "createObjectURL", { configurable: true, value: createObjectURL });
    Object.defineProperty(URL, "revokeObjectURL", { configurable: true, value: revokeObjectURL });
    const serverExporter = vi.fn<AssistancePreferencesExporter>().mockResolvedValue({
      status: "ready",
      content: "server",
      fileName: "ai-help-preference.json",
    });
    const localExporter = vi.fn<LocalReminderExporter>().mockResolvedValue({
      status: "ready",
      content: "local",
      fileName: "this-browser-reminder-choice.json",
    });
    renderPage({ localExporter, serverExporter });
    const user = userEvent.setup();

    await user.click(screen.getByRole("button", { name: "Download AI-help choice" }));
    await user.click(screen.getByRole("button", { name: "Download this-browser choice" }));

    await waitFor(() => expect(serverExporter).toHaveBeenCalledWith(2, profile.profile_digest));
    expect(localExporter).toHaveBeenCalledOnce();
    expect(click).toHaveBeenCalledTimes(2);
    expect(revokeObjectURL).toHaveBeenCalledWith("blob:server");
    expect(revokeObjectURL).toHaveBeenCalledWith("blob:local");
  });

  it("keeps the local branch usable when the learner API is unavailable", () => {
    renderPage({
      state: { ...readyState, server: { status: "unavailable" } },
    });

    expect(screen.getByRole("heading", { name: "AI-help choice temporarily unavailable" })).toBeVisible();
    expect(screen.getByRole("heading", { name: "Future in-app reminder choice" })).toBeVisible();
    expect(screen.getByRole("radio", { name: /Keep reminders off/i })).toBeEnabled();
  });

  it("focuses bounded recovery guidance without exposing private details", async () => {
    renderPage({
      actionState: {
        status: "error",
        authority: "server",
        kind: "stale",
        intent: "save",
      },
    });

    const heading = screen.getByRole("heading", { name: "AI-help choice changed" });
    await waitFor(() => expect(heading).toHaveFocus());
    expect(screen.getByText(/Reload the page, review the current choice/i)).toBeVisible();
  });
});

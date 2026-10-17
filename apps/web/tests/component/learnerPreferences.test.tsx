import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { createMemoryRouter, RouterProvider } from "react-router";
import { describe, expect, it, vi } from "vitest";

import { LearnerPreferencesPage } from "../../src/features/learner-preferences/LearnerPreferencesPage";
import type {
  LearnerPreferenceExport,
  LearnerPreferenceHistory,
  LearnerPreferenceProfile,
  LearnerPreferencesActionState,
  LearnerPreferencesExporter,
} from "../../src/features/learner-preferences/model";


const preferenceProfileFixture: LearnerPreferenceProfile = {
  schema_version: "1.0.0",
  profile_id: "profile.learning-1",
  learner_id: "11111111-1111-4111-8111-111111111111",
  revision: 4,
  goals: [
    { goal_id: "goal.risk-1", title: "Explain risk and return", detail: "Compare possible outcomes. 📊", archived: false, created_at: "2026-10-17T14:00:00Z", updated_at: "2026-10-17T14:02:00Z" },
    { goal_id: "goal.cash-2", title: "Understand cash flow", detail: null, archived: true, created_at: "2026-10-17T14:01:00Z", updated_at: "2026-10-17T14:03:00Z" },
  ],
  experience: [
    { experience_id: "experience.finance-1", subject: "Personal finance", level: "some_experience", detail: "I have built a budget.", created_at: "2026-10-17T14:04:00Z", updated_at: "2026-10-17T14:04:00Z" },
  ],
  interests: [
    { interest_id: "interest.etf-1", label: "ETF research", created_at: "2026-10-17T14:05:00Z", updated_at: "2026-10-17T14:05:00Z" },
    { interest_id: "interest.behavior-2", label: "Behavioral finance", created_at: "2026-10-17T14:06:00Z", updated_at: "2026-10-17T14:06:00Z" },
  ],
  created_at: "2026-10-17T14:00:00Z",
  updated_at: "2026-10-17T14:06:00Z",
  profile_digest: "a".repeat(64),
};

const preferenceHistoryFixture: LearnerPreferenceHistory = {
  schema_version: "1.0.0",
  profile_id: preferenceProfileFixture.profile_id,
  current_revision: preferenceProfileFixture.revision,
  changes: [{
    schema_version: "1.0.0",
    revision: 4,
    operation: "reorder_interests",
    object_kind: "profile",
    object_id: null,
    occurred_at: "2026-10-17T14:06:00Z",
    resulting_profile_digest: preferenceProfileFixture.profile_digest,
  }],
};

const preferenceExportFixture: LearnerPreferenceExport = {
  schema_version: "1.0.0",
  purpose: "A portable copy of the learning preferences you entered.",
  limitations: ["These statements are not competency evidence."],
  exported_at: "2026-10-17T14:07:00Z",
  profile: preferenceProfileFixture,
  history: preferenceHistoryFixture,
};

function renderPreferences(
  submissions: FormData[] = [],
  actionState: LearnerPreferencesActionState | undefined = undefined,
  profile: LearnerPreferenceProfile = preferenceProfileFixture,
  exporter: LearnerPreferencesExporter = async () => ({ status: "unavailable" }),
) {
  const router = createMemoryRouter([{
    path: "/preferences/learning",
    action: async ({ request }) => {
      submissions.push(await request.formData());
      return null;
    },
    element: (
      <LearnerPreferencesPage
        actionState={actionState}
        busy={false}
        exportPreferences={exporter}
        history={{
          ...preferenceHistoryFixture,
          profile_id: profile.profile_id,
          current_revision: profile.revision,
          changes: preferenceHistoryFixture.changes.filter((change) => change.revision <= profile.revision),
        }}
        profile={profile}
      />
    ),
  }], { initialEntries: ["/preferences/learning"] });
  return render(<RouterProvider router={router} />);
}

describe("Learning preferences page", () => {
  it("leads with learner tasks and keeps exact records available", () => {
    renderPreferences();

    expect(screen.getByRole("heading", { level: 1, name: "Learning preferences" })).toBeVisible();
    expect(screen.getByRole("heading", { name: "You stay in control" })).toBeVisible();
    expect(screen.getByText(/not proof of competency or financial suitability/i)).toBeVisible();
    expect(screen.getByText(preferenceProfileFixture.goals[0]!.title)).toBeVisible();
    expect(screen.getByText("Some experience", { selector: ".preferences-status" })).toBeVisible();
    expect(screen.getByText("Archived")).toBeVisible();
    expect(screen.getAllByText("Technical record").length).toBeGreaterThan(2);
    expect(screen.getAllByText(preferenceProfileFixture.profile_digest).length).toBeGreaterThan(0);
    expect(screen.queryByText("some_experience")).not.toBeInTheDocument();
  });

  it("submits exact generated-client mutation fields for varied Unicode input", async () => {
    const submissions: FormData[] = [];
    renderPreferences(submissions);
    const user = userEvent.setup();

    const addButton = screen.getByRole("button", { name: "Add goal" });
    const addForm = addButton.closest("form") as HTMLFormElement;
    await user.type(within(addForm).getByLabelText("Goal"), "Compare drawdowns 📉");
    await user.type(within(addForm).getByLabelText(/Why this matters/), "Explain loss without predicting a result.");
    await user.click(addButton);

    await waitFor(() => expect(submissions).toHaveLength(1));
    const form = submissions[0]!;
    expect(Object.fromEntries(form.entries())).toMatchObject({
      operation: "create_goal",
      title: "Compare drawdowns 📉",
      detail: "Explain loss without predicting a result.",
      expected_revision: String(preferenceProfileFixture.revision),
      form_intent: "create-goal",
    });
    expect(form.get("idempotency_key")).toMatch(/^[a-f0-9-]{36}$/);
  });

  it("reorders profiles with different valid item counts", async () => {
    const submissions: FormData[] = [];
    renderPreferences(submissions);

    await userEvent.setup().click(screen.getByRole("button", { name: "Move Explain risk and return down" }));

    await waitFor(() => expect(submissions).toHaveLength(1));
    expect(submissions[0]!.get("operation")).toBe("reorder_goals");
    expect(submissions[0]!.getAll("ordered_ids")).toEqual([
      preferenceProfileFixture.goals[1]!.goal_id,
      preferenceProfileFixture.goals[0]!.goal_id,
    ]);
  });

  it("requires explicit reset confirmation and distinguishes preferences from saved work", async () => {
    const submissions: FormData[] = [];
    renderPreferences(submissions);
    const user = userEvent.setup();

    expect(screen.getByText(/does not remove completed learning, saved work, or project evidence/i)).toBeVisible();
    await user.click(screen.getByRole("checkbox", { name: /I understand that this removes/ }));
    await user.click(screen.getByRole("button", { name: "Reset learning preferences" }));

    await waitFor(() => expect(submissions).toHaveLength(1));
    expect(Object.fromEntries(submissions[0]!.entries())).toMatchObject({
      operation: "reset_profile",
      confirm_reset: "reset",
      expected_revision: String(preferenceProfileFixture.revision),
    });
  });

  it("downloads only a matching validated export", async () => {
    const createObjectURL = vi.fn().mockReturnValue("blob:learning-preferences");
    const revokeObjectURL = vi.fn();
    const click = vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => undefined);
    Object.defineProperty(URL, "createObjectURL", { configurable: true, value: createObjectURL });
    Object.defineProperty(URL, "revokeObjectURL", { configurable: true, value: revokeObjectURL });
    const exporter = vi.fn<LearnerPreferencesExporter>().mockResolvedValue({
      status: "ready",
      content: JSON.stringify(preferenceExportFixture),
      export: preferenceExportFixture,
      fileName: "learning-preferences-export.json",
    });
    renderPreferences([], undefined, preferenceProfileFixture, exporter);

    await userEvent.setup().click(screen.getByRole("button", { name: "Download preferences" }));

    await waitFor(() => expect(exporter).toHaveBeenCalledWith(preferenceProfileFixture.revision, preferenceProfileFixture.profile_digest));
    expect(createObjectURL).toHaveBeenCalledWith(expect.any(Blob));
    expect(click).toHaveBeenCalledOnce();
    expect(revokeObjectURL).toHaveBeenCalledWith("blob:learning-preferences");
    expect(screen.getByText(/download is ready/i)).toBeVisible();
  });

  it("shows empty flexible states without creating inferred facts", () => {
    renderPreferences([], undefined, {
      ...preferenceProfileFixture,
      revision: 1,
      goals: [],
      experience: [],
      interests: [],
    });

    expect(screen.getByText("You have not added a learning goal yet.")).toBeVisible();
    expect(screen.getByText("You have not described any experience yet.")).toBeVisible();
    expect(screen.getByText("You have not added an interest yet.")).toBeVisible();
    expect(screen.queryByText(/your competency is/i)).not.toBeInTheDocument();
  });

  it("moves focus to an actionable stale-write message", async () => {
    renderPreferences([], {
      status: "error",
      kind: "stale",
      intent: "create-goal",
      preparedRequest: {
        schema_version: "1.0.0",
        idempotency_key: "request.stale-1",
        expected_revision: 3,
        mutation: { operation: "create_goal", title: "Old goal", detail: null },
      },
    });

    const heading = await screen.findByRole("heading", { name: "Preferences changed" });
    await waitFor(() => expect(heading).toHaveFocus());
    expect(screen.getByText(/Refresh the page, review the current choices/i)).toBeVisible();
  });

  it("reuses the exact prepared request only while an uncertain form is unchanged", async () => {
    const submissions: FormData[] = [];
    const goal = preferenceProfileFixture.goals[0]!;
    renderPreferences(submissions, {
      status: "error",
      kind: "unavailable",
      intent: `update-goal-${goal.goal_id}`,
      preparedRequest: {
        schema_version: "1.0.0",
        idempotency_key: "request.retry-1",
        expected_revision: 3,
        mutation: {
          operation: "update_goal",
          entry_id: goal.goal_id,
          title: goal.title,
          detail: goal.detail,
        },
      },
    });
    const user = userEvent.setup();

    await user.click(screen.getAllByText("Edit goal")[0]!);
    await user.click(screen.getAllByRole("button", { name: "Save goal" })[0]!);

    await waitFor(() => expect(submissions).toHaveLength(1));
    expect(submissions[0]!.get("idempotency_key")).toBe("request.retry-1");
    expect(submissions[0]!.get("expected_revision")).toBe("3");
  });
});

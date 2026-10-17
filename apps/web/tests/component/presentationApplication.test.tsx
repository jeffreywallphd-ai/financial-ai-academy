import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { StrictMode } from "react";
import { describe, expect, it, vi } from "vitest";

import type { PresentationPreferenceProfile } from "../../src/features/presentation-preferences/model";
import {
  PresentationProvider,
  usePresentation,
} from "../../src/platform/presentation/presentation";


const standardProfile: PresentationPreferenceProfile = {
  schema_version: "1.0.0",
  profile_id: "profile.display-1",
  learner_id: "11111111-1111-4111-8111-111111111111",
  revision: 2,
  text_size: "larger",
  text_spacing: "increased",
  reading_width: "focused",
  motion: "reduce",
  created_at: "2026-10-17T20:00:00Z",
  updated_at: "2026-10-17T20:05:00Z",
  profile_digest: "a".repeat(64),
};

function Controls() {
  const presentation = usePresentation();
  return (
    <>
      <output>{presentation.status}</output>
      <button
        onClick={() => presentation.preview({
          motion: "system",
          reading_width: "standard",
          text_size: "default",
          text_spacing: "default",
        })}
        type="button"
      >
        Preview standard
      </button>
      <button onClick={presentation.restore} type="button">Restore accepted</button>
    </>
  );
}

describe("global presentation application", () => {
  it("applies a complete accepted profile, previews a draft, and restores the accepted settings", async () => {
    render(
      <PresentationProvider readProfile={async () => standardProfile}>
        <Controls />
      </PresentationProvider>,
    );

    await waitFor(() => expect(screen.getByText("ready")).toBeVisible());
    expect(document.documentElement).toHaveAttribute("data-text-size", "larger");
    expect(document.documentElement).toHaveAttribute("data-text-spacing", "increased");
    expect(document.documentElement).toHaveAttribute("data-reading-width", "focused");
    expect(document.documentElement).toHaveAttribute("data-motion", "reduce");

    await userEvent.setup().click(screen.getByRole("button", { name: "Preview standard" }));
    expect(document.documentElement).toHaveAttribute("data-text-size", "default");
    expect(document.documentElement).toHaveAttribute("data-motion", "system");

    await userEvent.setup().click(screen.getByRole("button", { name: "Restore accepted" }));
    expect(document.documentElement).toHaveAttribute("data-text-size", "larger");
    expect(document.documentElement).toHaveAttribute("data-motion", "reduce");
  });

  it("uses the complete safe baseline when the service cannot provide a valid profile", async () => {
    render(
      <PresentationProvider readProfile={async () => null}>
        <Controls />
      </PresentationProvider>,
    );

    await waitFor(() => expect(screen.getByText("baseline")).toBeVisible());
    expect(document.documentElement).toHaveAttribute("data-text-size", "default");
    expect(document.documentElement).toHaveAttribute("data-text-spacing", "default");
    expect(document.documentElement).toHaveAttribute("data-reading-width", "standard");
    expect(document.documentElement).toHaveAttribute("data-motion", "system");
  });

  it("starts one profile read after the development StrictMode effect replay", async () => {
    const readProfile = vi.fn().mockResolvedValue(standardProfile);
    render(
      <StrictMode>
        <PresentationProvider readProfile={readProfile}>
          <Controls />
        </PresentationProvider>
      </StrictMode>,
    );

    await waitFor(() => expect(screen.getByText("ready")).toBeVisible());
    expect(readProfile).toHaveBeenCalledOnce();
  });

  it("does not let a slower older startup read replace a newer route profile", async () => {
    let resolveRead: (profile: PresentationPreferenceProfile | null) => void = () => undefined;
    const delayedRead = new Promise<PresentationPreferenceProfile | null>((resolve) => {
      resolveRead = resolve;
    });
    const newer = { ...standardProfile, revision: 5, text_size: "default" as const };

    function AcceptNewer() {
      const presentation = usePresentation();
      return <button onClick={() => presentation.acceptProfile(newer)} type="button">Accept newer</button>;
    }

    render(
      <PresentationProvider readProfile={() => delayedRead}>
        <AcceptNewer />
      </PresentationProvider>,
    );
    await userEvent.setup().click(screen.getByRole("button", { name: "Accept newer" }));
    expect(document.documentElement).toHaveAttribute("data-text-size", "default");

    resolveRead(standardProfile);
    await waitFor(() => expect(document.documentElement).toHaveAttribute("data-text-size", "default"));
  });
});

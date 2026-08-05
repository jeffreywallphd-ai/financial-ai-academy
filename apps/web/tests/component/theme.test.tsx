import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";

import {
  ThemeControl,
  ThemeProvider,
  readThemePreference,
} from "../../src/platform/theme/theme";


describe("theme preference", () => {
  it("defaults invalid or unavailable storage to system", () => {
    expect(
      readThemePreference({ getItem: () => "untrusted-value" }),
    ).toBe("system");
    expect(
      readThemePreference({
        getItem: () => {
          throw new Error("storage unavailable");
        },
      }),
    ).toBe("system");
  });

  it("applies and persists light, dark, and system without changing UI", async () => {
    const user = userEvent.setup();
    render(
      <ThemeProvider>
        <ThemeControl />
        <p>Same educational content</p>
      </ThemeProvider>,
    );
    const control = screen.getByLabelText("Theme");

    expect(document.documentElement).toHaveAttribute(
      "data-theme",
      "system",
    );
    await user.selectOptions(control, "dark");
    expect(document.documentElement).toHaveAttribute(
      "data-theme",
      "dark",
    );
    expect(window.localStorage.getItem("financial-ai-academy.theme")).toBe(
      "dark",
    );
    expect(screen.getByText("Same educational content")).toBeVisible();
    await user.selectOptions(control, "light");
    expect(document.documentElement).toHaveAttribute(
      "data-theme",
      "light",
    );
  });
});

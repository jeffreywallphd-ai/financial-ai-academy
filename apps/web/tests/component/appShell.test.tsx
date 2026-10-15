import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import {
  createMemoryRouter,
  RouterProvider,
} from "react-router";
import { afterEach, describe, expect, it, vi } from "vitest";

import { AppShell } from "../../src/app/AppShell";
import { ThemeProvider } from "../../src/platform/theme/theme";


function mockViewport(drawer: boolean) {
  vi.stubGlobal(
    "matchMedia",
    vi.fn().mockImplementation((query: string) => ({
      matches: drawer && query === "(max-width: 63.99rem)",
      media: query,
      onchange: null,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      addListener: vi.fn(),
      removeListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })),
  );
}

function renderShell() {
  const router = createMemoryRouter(
    [
      {
        path: "/",
        Component: AppShell,
        children: [
          {
            path: "learn/placements/:placementId",
            element: <h1>Lesson content</h1>,
          },
        ],
      },
    ],
    {
      initialEntries: [
        "/learn/placements/intro-risk-return-primary",
      ],
    },
  );
  render(
    <ThemeProvider>
      <RouterProvider router={router} />
    </ThemeProvider>,
  );
}

afterEach(() => {
  vi.unstubAllGlobals();
  document.body.removeAttribute("data-navigation-open");
});

describe("AppShell", () => {
  it("shows the delivered Learn route and labels future areas unavailable", () => {
    mockViewport(false);
    renderShell();

    expect(
      screen.getByRole("navigation", { name: "Primary navigation" }),
    ).toBeVisible();
    expect(screen.getByRole("link", { name: "Learn" })).toHaveAttribute(
      "aria-current",
      "page",
    );
    expect(screen.getByText("Dashboard").closest("[aria-disabled]"))
      .toHaveAttribute("aria-disabled", "true");
    expect(screen.queryByRole("link", { name: "Dashboard" }))
      .not.toBeInTheDocument();
  });

  it("opens and closes the narrow navigation drawer accessibly", async () => {
    mockViewport(true);
    const user = userEvent.setup();
    renderShell();

    const menu = screen.getByRole("button", {
      name: "Open navigation menu",
    });
    const navigation = screen.getByRole("navigation", {
      name: "Primary navigation",
      hidden: true,
    });
    expect(menu).toHaveAttribute("aria-expanded", "false");
    expect(navigation.closest("aside")).toHaveAttribute(
      "aria-hidden",
      "true",
    );

    await user.click(menu);
    expect(menu).toHaveAttribute("aria-expanded", "true");
    expect(navigation.closest("aside")).not.toHaveAttribute(
      "aria-hidden",
    );
    expect(
      screen.getByRole("button", { name: "Close navigation menu" }),
    ).toHaveFocus();

    await user.keyboard("{Escape}");
    expect(menu).toHaveFocus();
    expect(menu).toHaveAttribute("aria-expanded", "false");
  });
});

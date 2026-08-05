import {
  createContext,
  useContext,
  useLayoutEffect,
  useMemo,
  useState,
} from "react";
import type { ReactNode } from "react";

import { Icon } from "../../components/Icon";


export type ThemePreference = "dark" | "light" | "system";

const STORAGE_KEY = "financial-ai-academy.theme";
const THEMES = new Set<ThemePreference>(["dark", "light", "system"]);

interface ThemeContextValue {
  preference: ThemePreference;
  setPreference: (preference: ThemePreference) => void;
}

const ThemeContext = createContext<ThemeContextValue | null>(null);

export function readThemePreference(
  storage: Pick<Storage, "getItem">,
): ThemePreference {
  try {
    const stored = storage.getItem(STORAGE_KEY);
    return stored && THEMES.has(stored as ThemePreference)
      ? (stored as ThemePreference)
      : "system";
  } catch {
    return "system";
  }
}

export function applyThemePreference(
  preference: ThemePreference,
  root: Pick<HTMLElement, "setAttribute"> = document.documentElement,
) {
  root.setAttribute("data-theme", preference);
}

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [preference, setPreferenceState] = useState<ThemePreference>(() =>
    readThemePreference(window.localStorage),
  );

  useLayoutEffect(() => {
    applyThemePreference(preference);
    try {
      window.localStorage.setItem(STORAGE_KEY, preference);
    } catch {
      // Theme remains active in memory when browser storage is unavailable.
    }
  }, [preference]);

  const value = useMemo(
    () => ({
      preference,
      setPreference: setPreferenceState,
    }),
    [preference],
  );

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const value = useContext(ThemeContext);
  if (!value) {
    throw new Error("useTheme must be rendered inside ThemeProvider.");
  }
  return value;
}

export function ThemeControl() {
  const { preference, setPreference } = useTheme();
  return (
    <label className="theme-control">
      <Icon name="theme" />
      <span>Theme</span>
      <select
        aria-label="Theme"
        onChange={(event) =>
          setPreference(event.currentTarget.value as ThemePreference)
        }
        value={preference}
      >
        <option value="system">System</option>
        <option value="light">Light</option>
        <option value="dark">Dark</option>
      </select>
    </label>
  );
}

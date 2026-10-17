import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useLayoutEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";

import type { components } from "../../generated/api-client";


export type PresentationPreferenceProfile =
  components["schemas"]["PresentationPreferenceProfileResponseModel"];

export interface PresentationSettings {
  motion: "reduce" | "system";
  reading_width: "focused" | "standard";
  text_size: "default" | "larger";
  text_spacing: "default" | "increased";
}

export const BASELINE_PRESENTATION: PresentationSettings = {
  motion: "system",
  reading_width: "standard",
  text_size: "default",
  text_spacing: "default",
};

export type PresentationProfileReader = (
  signal: AbortSignal,
) => Promise<PresentationPreferenceProfile | null>;

type PresentationRoot = Pick<HTMLElement, "setAttribute">;

function settingsAreSafe(value: PresentationSettings): boolean {
  return (value.motion === "system" || value.motion === "reduce") &&
    (value.reading_width === "standard" || value.reading_width === "focused") &&
    (value.text_size === "default" || value.text_size === "larger") &&
    (value.text_spacing === "default" || value.text_spacing === "increased");
}

export function presentationSettingsFromProfile(
  profile: PresentationPreferenceProfile,
): PresentationSettings {
  return {
    motion: profile.motion,
    reading_width: profile.reading_width,
    text_size: profile.text_size,
    text_spacing: profile.text_spacing,
  };
}

export function applyPresentationSettings(
  requested: PresentationSettings,
  root: PresentationRoot = document.documentElement,
): PresentationSettings {
  const settings = settingsAreSafe(requested) ? requested : BASELINE_PRESENTATION;
  root.setAttribute("data-text-size", settings.text_size);
  root.setAttribute("data-text-spacing", settings.text_spacing);
  root.setAttribute("data-reading-width", settings.reading_width);
  root.setAttribute("data-motion", settings.motion);
  return settings;
}

interface PresentationContextValue {
  acceptProfile: (profile: PresentationPreferenceProfile) => void;
  accepted: PresentationSettings;
  preview: (settings: PresentationSettings) => void;
  restore: () => void;
  status: "baseline" | "loading" | "ready";
}

const PresentationContext = createContext<PresentationContextValue | null>(null);

export function PresentationProvider({
  children,
  readProfile,
}: {
  children: ReactNode;
  readProfile: PresentationProfileReader;
}) {
  const acceptedProfile = useRef<PresentationPreferenceProfile | null>(null);
  const acceptedSettings = useRef<PresentationSettings>(BASELINE_PRESENTATION);
  const startupReadSuperseded = useRef(false);
  const [accepted, setAccepted] = useState<PresentationSettings>(BASELINE_PRESENTATION);
  const [status, setStatus] = useState<PresentationContextValue["status"]>("loading");

  const restore = useCallback(() => {
    applyPresentationSettings(acceptedSettings.current);
  }, []);

  const preview = useCallback((settings: PresentationSettings) => {
    applyPresentationSettings(settings);
  }, []);

  const applyAcceptedProfile = useCallback((profile: PresentationPreferenceProfile) => {
    if (
      acceptedProfile.current &&
      profile.revision < acceptedProfile.current.revision
    ) return;
    const settings = presentationSettingsFromProfile(profile);
    acceptedProfile.current = profile;
    acceptedSettings.current = settings;
    setAccepted(settings);
    setStatus("ready");
    applyPresentationSettings(settings);
  }, []);

  const acceptProfile = useCallback((profile: PresentationPreferenceProfile) => {
    startupReadSuperseded.current = true;
    applyAcceptedProfile(profile);
  }, [applyAcceptedProfile]);

  useLayoutEffect(() => {
    applyPresentationSettings(BASELINE_PRESENTATION);
  }, []);

  useEffect(() => {
    let active = true;
    const timer = window.setTimeout(() => {
      const controller = new AbortController();
      void readProfile(controller.signal)
        .then((profile) => {
          if (!active) return;
          if (profile && !startupReadSuperseded.current) {
            applyAcceptedProfile(profile);
          } else if (!acceptedProfile.current) {
            acceptedSettings.current = BASELINE_PRESENTATION;
            setAccepted(BASELINE_PRESENTATION);
            setStatus("baseline");
            applyPresentationSettings(BASELINE_PRESENTATION);
          }
        })
        .catch(() => {
          if (active && !acceptedProfile.current) {
            setStatus("baseline");
            applyPresentationSettings(BASELINE_PRESENTATION);
          }
        });
    }, 0);
    return () => {
      active = false;
      window.clearTimeout(timer);
    };
  }, [applyAcceptedProfile, readProfile]);

  const value = useMemo<PresentationContextValue>(() => ({
    acceptProfile,
    accepted,
    preview,
    restore,
    status,
  }), [acceptProfile, accepted, preview, restore, status]);

  return (
    <PresentationContext.Provider value={value}>
      {children}
    </PresentationContext.Provider>
  );
}

export function usePresentation() {
  const value = useContext(PresentationContext);
  if (!value) {
    throw new Error("usePresentation must be rendered inside PresentationProvider.");
  }
  return value;
}

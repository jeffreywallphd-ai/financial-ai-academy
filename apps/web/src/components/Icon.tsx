import iconSpriteUrl from "../design-system/icons/faa-icons.svg?url";


export type IconName =
  | "citation"
  | "close"
  | "error-circle"
  | "external-link"
  | "help"
  | "home"
  | "info-circle"
  | "labs"
  | "learn"
  | "lock"
  | "menu"
  | "practice"
  | "progress"
  | "projects"
  | "refresh"
  | "settings"
  | "shield-check"
  | "theme"
  | "warning-triangle"
  | "workspace";

interface IconProps {
  name: IconName;
  className?: string;
}

export function Icon({ name, className = "" }: IconProps) {
  return (
    <svg
      aria-hidden="true"
      className={("faa-icon " + className).trim()}
      focusable="false"
    >
      <use href={iconSpriteUrl + "#faa-icon-" + name} />
    </svg>
  );
}

import iconSpriteUrl from "../design-system/icons/faa-icons.svg?url";


export type IconName =
  | "citation"
  | "error-circle"
  | "external-link"
  | "info-circle"
  | "learn"
  | "lock"
  | "refresh"
  | "shield-check"
  | "theme"
  | "warning-triangle";

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

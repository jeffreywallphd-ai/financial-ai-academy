import type { IconName } from "./Icon";
import { Icon } from "./Icon";


interface StatusPanelProps {
  actionLabel?: string;
  description: string;
  icon: IconName;
  onAction?: () => void;
  title: string;
  tone: "danger" | "info" | "warning";
}

export function StatusPanel({
  actionLabel,
  description,
  icon,
  onAction,
  title,
  tone,
}: StatusPanelProps) {
  return (
    <section
      aria-atomic="true"
      aria-live={tone === "danger" ? "assertive" : "polite"}
      className={"status-panel status-panel--" + tone}
      role={tone === "danger" ? "alert" : "status"}
    >
      <Icon
        className={
          tone === "danger"
            ? "faa-icon--danger faa-icon--lg"
            : tone === "warning"
              ? "faa-icon--warning faa-icon--lg"
              : "faa-icon--active faa-icon--lg"
        }
        name={icon}
      />
      <div>
        <h1>{title}</h1>
        <p>{description}</p>
        {actionLabel && onAction ? (
          <button
            className="button button--secondary"
            onClick={onAction}
            type="button"
          >
            <Icon name="refresh" />
            {actionLabel}
          </button>
        ) : null}
      </div>
    </section>
  );
}

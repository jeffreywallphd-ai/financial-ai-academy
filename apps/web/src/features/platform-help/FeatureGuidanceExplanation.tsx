import { useEffect, useId, useState } from "react";
import { Link, useLocation } from "react-router";

import {
  platformHelpTopicHref,
  type FeatureGuidance,
  type FeatureGuidanceActionKind,
  type FeatureGuidanceReader,
} from "./model";

type OwnedActionKind = Exclude<FeatureGuidanceActionKind, "open_help_topic">;

export type FeatureGuidanceActionHandlers = Partial<
  Record<OwnedActionKind, () => void>
>;

export const unavailableFeatureGuidanceReader: FeatureGuidanceReader = async () => ({
  status: "unavailable",
});

function returnTarget(pathname: string, search: string): string {
  return pathname === "/saved-learning" ? pathname : `${pathname}${search}`;
}

export function FeatureGuidanceExplanation({
  actionHandlers = {},
  conditionKey,
  headingLevel = 3,
  mappingVersion = "1.0.0",
  readFeatureGuidance,
  surfaceKey,
}: {
  actionHandlers?: FeatureGuidanceActionHandlers;
  conditionKey: string;
  headingLevel?: 2 | 3;
  mappingVersion?: string;
  readFeatureGuidance: FeatureGuidanceReader;
  surfaceKey: string;
}) {
  const headingId = useId();
  const location = useLocation();
  const [resolution, setResolution] = useState<FeatureGuidance | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    setResolution(null);
    void readFeatureGuidance(
      surfaceKey,
      conditionKey,
      mappingVersion,
      controller.signal,
    )
      .then((outcome) => {
        if (!controller.signal.aborted && outcome.status === "ready") {
          setResolution(outcome.resolution);
        }
      })
      .catch(() => {
        // Feature Guidance is optional; the owning task remains usable.
      });
    return () => controller.abort();
  }, [conditionKey, mappingVersion, readFeatureGuidance, surfaceKey]);

  if (resolution === null) return null;
  const actions = resolution.guidance.actions.filter(
    (action) =>
      action.action_kind === "open_help_topic" ||
      actionHandlers[action.action_kind] !== undefined,
  );
  const ExplanationHeading = headingLevel === 2 ? "h2" : "h3";
  const ActionsHeading = headingLevel === 2 ? "h3" : "h4";
  const returnTo = returnTarget(location.pathname, location.search);
  return (
    <aside aria-labelledby={headingId} className="feature-guidance-explanation">
      <p className="eyebrow">What this limit means</p>
      <ExplanationHeading id={headingId}>{resolution.guidance.heading}</ExplanationHeading>
      <p>{resolution.guidance.reason}</p>
      <p>
        <strong>What was protected or may have happened:</strong>{" "}
        {resolution.guidance.outcome}
      </p>
      {actions.length === 0 ? null : (
        <div>
          <ActionsHeading>What you can do</ActionsHeading>
          <ul>
            {actions.map((action) => {
              if (action.action_kind === "open_help_topic") {
                return (
                  <li key={`${action.topic_id}@${action.topic_version}`}>
                    <Link
                      to={platformHelpTopicHref(
                        action.topic_id,
                        action.topic_version,
                        returnTo,
                      )}
                    >
                      {action.label}
                    </Link>
                  </li>
                );
              }
              const handler = actionHandlers[action.action_kind];
              return handler === undefined ? null : (
                <li key={action.action_kind}>
                  <button
                    className="button button--secondary"
                    onClick={handler}
                    type="button"
                  >
                    {action.label}
                  </button>
                </li>
              );
            })}
          </ul>
        </div>
      )}
    </aside>
  );
}

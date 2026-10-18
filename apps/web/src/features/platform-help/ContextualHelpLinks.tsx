import { useEffect, useId, useState } from "react";
import { Link, useLocation } from "react-router";

import {
  platformHelpTopicHref,
  type ContextualHelp,
  type ContextualHelpReader,
} from "./model";

export const unavailableContextualHelpReader: ContextualHelpReader = async () => ({
  status: "unavailable",
});

export function ContextualHelpLinks({
  contextKey,
  contextVersion = "1.0.0",
  readContextualHelp,
}: {
  contextKey: string;
  contextVersion?: string;
  readContextualHelp: ContextualHelpReader;
}) {
  const headingId = useId();
  const location = useLocation();
  const [context, setContext] = useState<ContextualHelp | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    setContext(null);
    void readContextualHelp(
      contextKey,
      contextVersion,
      controller.signal,
    )
      .then((outcome) => {
        if (!controller.signal.aborted && outcome.status === "ready") {
          setContext(outcome.context);
        }
      })
      .catch(() => {
        // Contextual Help is optional; the owning feature remains usable.
      });
    return () => controller.abort();
  }, [contextKey, contextVersion, readContextualHelp]);

  if (context === null) return null;
  const returnTo = `${location.pathname}${location.search}`;
  return (
    <aside aria-labelledby={headingId} className="contextual-help-links">
      <h3 id={headingId}>Questions about {context.feature_label}</h3>
      <ul>
        {context.help_references.map((reference) => (
          <li key={`${reference.topic_id}@${reference.topic_version}`}>
            <Link
              to={platformHelpTopicHref(
                reference.topic_id,
                reference.topic_version,
                returnTo,
              )}
            >
              {reference.label}
            </Link>
          </li>
        ))}
      </ul>
    </aside>
  );
}

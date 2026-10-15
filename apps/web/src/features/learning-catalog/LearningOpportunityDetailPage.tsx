import { Link } from "react-router";

import { Icon } from "../../components/Icon";
import type {
  LearningOpportunity,
  LearningOpportunityProjectionIdentity,
} from "./model";
import { opportunityCanOpen } from "./model";

function label(value: string): string {
  return value
    .split(/[-_]/)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function readableDate(value: string): string {
  return new Intl.DateTimeFormat("en", {
    day: "numeric",
    month: "short",
    timeZone: "UTC",
    year: "numeric",
  }).format(new Date(value));
}

function readableDateTime(value: string): string {
  return new Intl.DateTimeFormat("en", {
    day: "numeric",
    hour: "numeric",
    hour12: true,
    minute: "2-digit",
    month: "short",
    timeZone: "UTC",
    timeZoneName: "short",
    year: "numeric",
  }).format(new Date(value));
}

export function LearningOpportunityDetailPage({
  opportunity,
  projection,
  returnTo,
}: {
  opportunity: LearningOpportunity;
  projection: LearningOpportunityProjectionIdentity;
  returnTo: string;
}) {
  const canOpen = opportunityCanOpen(opportunity);
  return (
    <section className="opportunity-detail">
      <header className="opportunity-detail__header">
        <p className="eyebrow">Current learning opportunity</p>
        <div className="opportunity-detail__badges">
          <span className="catalog-badge">{label(opportunity.kind)}</span>
          <span
            className={
              "catalog-badge catalog-badge--" + opportunity.availability
            }
          >
            {label(opportunity.availability)}
          </span>
        </div>
        <h1>{opportunity.title}</h1>
        <p>{opportunity.summary}</p>
        <p className="opportunity-detail__context">
          Catalog updated{" "}
          <time dateTime={projection.projected_at}>
            {readableDateTime(projection.projected_at)}
          </time>
          . This view uses current deterministic catalog facts, not a
          personalized recommendation or eligibility decision.
        </p>
      </header>

      <div className="opportunity-detail__layout">
        <div className="opportunity-detail__primary">
          <section className="opportunity-detail__panel">
            <h2>Opportunity overview</h2>
            <dl className="opportunity-detail__facts">
              <div>
                <dt>Opportunity ID</dt>
                <dd>
                  <code>{opportunity.opportunity_id}</code>
                </dd>
              </div>
              <div>
                <dt>Kind</dt>
                <dd>{label(opportunity.kind)}</dd>
              </div>
              <div>
                <dt>Level</dt>
                <dd>{label(opportunity.level)}</dd>
              </div>
              <div>
                <dt>Estimated time</dt>
                <dd>
                  <Icon name="clock" />
                  {opportunity.estimated_minutes} minutes
                </dd>
              </div>
              <div>
                <dt>Prerequisites</dt>
                <dd>{opportunity.prerequisite_summary}</dd>
              </div>
              <div>
                <dt>Exact package</dt>
                <dd>
                  <code>
                    {opportunity.package_id}@{opportunity.package_version}
                  </code>
                </dd>
              </div>
            </dl>
          </section>

          <section className="opportunity-detail__panel">
            <h2>Topics and learning objectives</h2>
            <ul
              aria-label={`${opportunity.title} topics`}
              className="catalog-topics"
            >
              {opportunity.topics.map((topic) => (
                <li key={topic}>{label(topic)}</li>
              ))}
            </ul>
            <h3>Learning objectives</h3>
            <ul className="opportunity-detail__objectives">
              {opportunity.objectives.map((objective) => (
                <li key={objective}>{objective}</li>
              ))}
            </ul>
          </section>

          <section className="opportunity-detail__panel">
            <h2>Publication and provenance</h2>
            <p>
              Published by {opportunity.provenance.published_by} on{" "}
              <time dateTime={opportunity.provenance.published_at}>
                {readableDate(opportunity.provenance.published_at)}
              </time>
              . Content reviewed{" "}
              <time dateTime={opportunity.provenance.content_reviewed_on}>
                {readableDate(opportunity.provenance.content_reviewed_on)}
              </time>
              .
            </p>
            <p>{opportunity.provenance.educational_use_notice}</p>
            <dl className="opportunity-detail__technical">
              <div>
                <dt>Package digest</dt>
                <dd>
                  <code>{opportunity.package_digest}</code>
                </dd>
              </div>
              <div>
                <dt>Source fingerprint</dt>
                <dd>
                  <code>{opportunity.source_fingerprint}</code>
                </dd>
              </div>
              <div>
                <dt>Projection generation</dt>
                <dd>
                  <code>{projection.projection_generation}</code>
                </dd>
              </div>
              <div>
                <dt>Discovery schema</dt>
                <dd>
                  <code>{projection.schema_version}</code>
                </dd>
              </div>
            </dl>
          </section>
        </div>

        <aside
          aria-label="Opportunity availability and actions"
          className="opportunity-detail__rail"
        >
          <section className="opportunity-detail__panel">
            <h2>Availability</h2>
            <p className="opportunity-detail__availability">
              <Icon name={canOpen ? "shield-check" : "lock"} />
              <strong>{label(opportunity.availability)}</strong>
            </p>
            <p>{opportunity.availability_reason}</p>
            <div className="opportunity-detail__actions">
              {canOpen ? (
                <Link
                  className="button catalog-open-link"
                  to={opportunity.destination}
                >
                  <Icon name="learn" />
                  Open exact lesson
                </Link>
              ) : null}
              <Link className="button button--secondary" to={returnTo}>
                Return to catalog
              </Link>
            </div>
          </section>
        </aside>
      </div>
    </section>
  );
}

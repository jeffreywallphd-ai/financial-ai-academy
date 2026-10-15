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

function ComparisonCard({
  index,
  opportunity,
  returnTo,
}: {
  index: number;
  opportunity: LearningOpportunity;
  returnTo: string;
}) {
  const canOpen = opportunityCanOpen(opportunity);
  const detailParameters = new URLSearchParams({ return_to: returnTo });
  return (
    <article className="opportunity-comparison__card">
      <p className="eyebrow">Selected {index + 1}</p>
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
      <h2>{opportunity.title}</h2>
      <p>{opportunity.summary}</p>

      <section>
        <h3>Educational facts</h3>
        <dl className="opportunity-comparison__facts">
          <div>
            <dt>Opportunity ID</dt>
            <dd>
              <code>{opportunity.opportunity_id}</code>
            </dd>
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

      <section>
        <h3>Topics and learning objectives</h3>
        <ul
          aria-label={`${opportunity.title} topics`}
          className="catalog-topics"
        >
          {opportunity.topics.map((topic) => (
            <li key={topic}>{label(topic)}</li>
          ))}
        </ul>
        <ul className="opportunity-comparison__objectives">
          {opportunity.objectives.map((objective) => (
            <li key={objective}>{objective}</li>
          ))}
        </ul>
      </section>

      <section>
        <h3>Publication and provenance</h3>
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
        <dl className="opportunity-comparison__technical">
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
        </dl>
      </section>

      <section className="opportunity-comparison__availability">
        <h3>Availability and actions</h3>
        <p>
          <Icon name={canOpen ? "shield-check" : "lock"} />
          <strong>{label(opportunity.availability)}</strong>
        </p>
        <p>{opportunity.availability_reason}</p>
        <div className="opportunity-comparison__actions">
          <Link
            className="button button--secondary"
            to={`/learn/opportunities/${encodeURIComponent(opportunity.opportunity_id)}?${detailParameters.toString()}`}
          >
            <Icon name="info-circle" />
            View details
          </Link>
          {canOpen ? (
            <Link className="button catalog-open-link" to={opportunity.destination}>
              <Icon name="learn" />
              Open exact lesson
            </Link>
          ) : null}
        </div>
      </section>
    </article>
  );
}

export function LearningOpportunityComparisonPage({
  opportunities,
  projection,
  returnTo,
}: {
  opportunities: readonly LearningOpportunity[];
  projection: LearningOpportunityProjectionIdentity;
  returnTo: string;
}) {
  return (
    <section className="opportunity-comparison">
      <header className="opportunity-comparison__header">
        <p className="eyebrow">Current learning opportunities</p>
        <h1>Compare educational facts</h1>
        <p>
          Review exact current facts in your selection order. This comparison
          does not rank opportunities, recommend a winner, or decide eligibility.
        </p>
        <p className="opportunity-comparison__context">
          Catalog updated{" "}
          <time dateTime={projection.projected_at}>
            {readableDateTime(projection.projected_at)}
          </time>
          {" · "}Generation <code>{projection.projection_generation}</code>
          {" · "}Schema <code>{projection.schema_version}</code>
        </p>
        <Link className="button button--secondary" to={returnTo}>
          Return to catalog
        </Link>
      </header>

      <ol aria-label="Selected opportunities in comparison order">
        {opportunities.map((opportunity, index) => (
          <li key={opportunity.opportunity_id}>
            <ComparisonCard
              index={index}
              opportunity={opportunity}
              returnTo={returnTo}
            />
          </li>
        ))}
      </ol>
    </section>
  );
}

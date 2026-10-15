import { Link } from "react-router";

import { Icon } from "../../components/Icon";
import type {
  LearningCatalog,
  LearningOpportunity,
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

function OpportunityCard({
  opportunity,
}: {
  opportunity: LearningOpportunity;
}) {
  const canOpen = opportunityCanOpen(opportunity);
  return (
    <article className="catalog-card">
      <div className="catalog-card__heading">
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
      <p className="catalog-card__summary">{opportunity.summary}</p>
      <ul
        aria-label={opportunity.title + " topics"}
        className="catalog-topics"
      >
        {opportunity.topics.map((topic) => (
          <li key={topic}>{label(topic)}</li>
        ))}
      </ul>
      <dl className="catalog-facts">
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
      <section
        aria-label={opportunity.title + " learning objectives"}
        className="catalog-card__objectives"
      >
        <h3>Learning objectives</h3>
        <ul>
          {opportunity.objectives.map((objective) => (
            <li key={objective}>{objective}</li>
          ))}
        </ul>
      </section>
      <section
        aria-label={opportunity.title + " publication context"}
        className="catalog-card__publication"
      >
        <h3>Publication context</h3>
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
        <details>
          <summary>Technical provenance</summary>
          <dl>
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
        </details>
      </section>
      <p className="catalog-card__availability" role="status">
        <Icon name={canOpen ? "shield-check" : "lock"} />
        {opportunity.availability_reason}
      </p>
      <div className="catalog-card__action">
        {canOpen ? (
          <Link
            className="button catalog-open-link"
            to={opportunity.destination}
          >
            <Icon name="learn" />
            Open exact lesson
          </Link>
        ) : null}
      </div>
    </article>
  );
}

export function LearningCatalogPage({
  catalog,
}: {
  catalog: LearningCatalog;
}) {
  return (
    <section className="learning-catalog">
      <header className="catalog-header">
        <p className="eyebrow">Approved learning catalog</p>
        <h1>Build financial understanding step by step</h1>
        <p>
          Browse reviewed educational opportunities in their published order.
          This catalog does not rank investments or make personalized
          recommendations.
        </p>
        <p className="catalog-header__meta">
          {catalog.records.length}{" "}
          {catalog.records.length === 1 ? "opportunity" : "opportunities"}
          {" · "}Catalog updated{" "}
          <time dateTime={catalog.projected_at}>
            {readableDate(catalog.projected_at)}
          </time>
        </p>
      </header>
      {catalog.records.length === 0 ? (
        <section className="catalog-empty" role="status">
          <Icon className="faa-icon--lg" name="info-circle" />
          <div>
            <h2>No approved opportunities yet</h2>
            <p>
              Nothing has passed the current publication and placement checks.
              Try again after more learning content is reviewed.
            </p>
          </div>
        </section>
      ) : (
        <ul
          aria-label="Approved learning opportunities"
          className="catalog-grid"
        >
          {catalog.records.map((opportunity) => (
            <li key={opportunity.opportunity_id}>
              <OpportunityCard opportunity={opportunity} />
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

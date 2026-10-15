import { Link } from "react-router";

import { Icon } from "../../components/Icon";
import type { LearningCatalogQueryPage, LearningOpportunity } from "./model";
import { opportunityCanOpen, queryPageHref } from "./model";

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
          className={"catalog-badge catalog-badge--" + opportunity.availability}
        >
          {label(opportunity.availability)}
        </span>
      </div>
      <h2>{opportunity.title}</h2>
      <p className="catalog-card__summary">{opportunity.summary}</p>
      <ul aria-label={opportunity.title + " topics"} className="catalog-topics">
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
      <p className="catalog-card__availability">
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

function QueryControls({ page }: { page: LearningCatalogQueryPage }) {
  const query = page.applied_query;
  const topicValues =
    query.topics.length < 8 ? [...query.topics, ""] : query.topics;
  return (
    <form action="/learn" className="catalog-query" method="get" role="search">
      <div className="catalog-query__text">
        <label>
          Search opportunities
          <input
            defaultValue={query.query ?? ""}
            maxLength={100}
            name="query"
            type="search"
          />
        </label>
        <label>
          Search prerequisites
          <input
            defaultValue={query.prerequisite_query ?? ""}
            maxLength={100}
            name="prerequisite_query"
            type="search"
          />
        </label>
        {topicValues.map((topic, index) => (
          <label key={`${topic}-${index}`}>
            {index === 0 ? "Topic slug" : `Additional topic ${index + 1}`}
            <input
              defaultValue={topic}
              maxLength={50}
              name="topic"
              pattern="[a-z0-9][a-z0-9-]{1,49}"
            />
          </label>
        ))}
      </div>
      <div className="catalog-query__filters">
        <label>
          Level
          <select defaultValue={query.levels} multiple name="level" size={3}>
            <option value="introductory">Introductory</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
          </select>
        </label>
        <label>
          Kind
          <select defaultValue={query.kinds} multiple name="kind" size={4}>
            <option value="course">Course</option>
            <option value="lesson">Lesson</option>
            <option value="lab">Lab</option>
            <option value="project">Project</option>
          </select>
        </label>
        <label>
          Availability
          <select
            defaultValue={query.availabilities}
            multiple
            name="availability"
            size={3}
          >
            <option value="available">Available</option>
            <option value="planned">Planned</option>
            <option value="unavailable">Unavailable</option>
          </select>
        </label>
        <label>
          Minimum minutes
          <input
            defaultValue={query.minimum_minutes ?? ""}
            max={1440}
            min={1}
            name="minimum_minutes"
            type="number"
          />
        </label>
        <label>
          Maximum minutes
          <input
            defaultValue={query.maximum_minutes ?? ""}
            max={1440}
            min={1}
            name="maximum_minutes"
            type="number"
          />
        </label>
        <label>
          Sort
          <select defaultValue={query.sort} name="sort">
            <option value="catalog">Catalog order</option>
            <option value="title">Title</option>
            <option value="duration_ascending">Shortest first</option>
            <option value="duration_descending">Longest first</option>
          </select>
        </label>
        <label>
          Results per page
          <select defaultValue={String(query.page_size)} name="page_size">
            <option value="10">10</option>
            <option value="20">20</option>
            <option value="50">50</option>
          </select>
        </label>
      </div>
      <p className="catalog-query__help">
        Use Ctrl or Command to select multiple list values. All filters are
        optional.
      </p>
      <div className="catalog-query__actions">
        <button className="button" type="submit">
          Apply query
        </button>
        <Link className="button button--secondary" to="/learn">
          Clear filters
        </Link>
      </div>
    </form>
  );
}

export function LearningCatalogPage({
  page,
}: {
  page: LearningCatalogQueryPage;
}) {
  return (
    <section className="learning-catalog">
      <header className="catalog-header">
        <p className="eyebrow">Approved learning catalog</p>
        <h1>Build financial understanding step by step</h1>
        <p>
          Search and filter reviewed educational opportunities. Results use
          deterministic catalog facts, not personalized recommendations.
        </p>
        <p className="catalog-header__meta">
          {page.total_matches} {page.total_matches === 1 ? "match" : "matches"}
          {" · "}Showing {page.records.length} on this page
          {" · "}Catalog updated{" "}
          <time dateTime={page.projected_at}>
            {readableDate(page.projected_at)}
          </time>
        </p>
      </header>
      <QueryControls page={page} />
      {page.records.length === 0 ? (
        <section className="catalog-empty" role="status">
          <Icon className="faa-icon--lg" name="info-circle" />
          <div>
            <h2>No opportunities match this query</h2>
            <p>
              Adjust or clear the optional filters. No recommendation or
              alternate ranking was invented.
            </p>
          </div>
        </section>
      ) : (
        <ul
          aria-label="Approved learning opportunities"
          className="catalog-grid"
        >
          {page.records.map((opportunity) => (
            <li key={opportunity.opportunity_id}>
              <OpportunityCard opportunity={opportunity} />
            </li>
          ))}
        </ul>
      )}
      {page.next_cursor ? (
        <nav aria-label="Catalog pages" className="catalog-pagination">
          <Link
            className="button button--secondary"
            to={queryPageHref(page.applied_query, page.next_cursor)}
          >
            Next page
          </Link>
        </nav>
      ) : null}
    </section>
  );
}

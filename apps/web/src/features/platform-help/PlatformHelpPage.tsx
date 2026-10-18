import { Link } from "react-router";

import {
  platformHelpSearchHref,
  platformHelpTopicHref,
  readableDate,
  relationshipLabel,
  topicKindLabel,
  type PlatformHelpBodyNode,
  type PlatformHelpSearchPage as PlatformHelpSearchPageModel,
  type PlatformHelpSearchSelection,
  type PlatformHelpTopic,
  type PlatformHelpTopicSelection,
} from "./model";

function SearchResultCard({
  result,
  returnTo,
}: {
  result: PlatformHelpSearchPageModel["results"][number];
  returnTo: string;
}) {
  return (
    <article className="help-result-card">
      <div className="help-result-card__heading">
        <p className="eyebrow">{topicKindLabel(result.topic_kind)}</p>
        <h2>{result.title}</h2>
      </div>
      {result.glossary_term ? (
        <p className="help-term">Term: {result.glossary_term}</p>
      ) : null}
      <p>{result.summary}</p>
      <p className="help-result-card__applies">
        <strong>Useful for:</strong>{" "}
        {result.applicability.map((item) => item.label).join(", ")}
      </p>
      <Link
        className="button-link"
        to={platformHelpTopicHref(
          result.topic_id,
          result.topic_version,
          returnTo,
        )}
      >
        Read this topic
      </Link>
    </article>
  );
}

export function PlatformHelpSearchPage({
  page,
  selection,
}: {
  page: PlatformHelpSearchPageModel;
  selection: PlatformHelpSearchSelection;
}) {
  const nextHref = page.next_cursor
    ? platformHelpSearchHref({
        ...selection.parameters,
        cursor: page.next_cursor,
      })
    : null;
  return (
    <section className="help-page help-search-page">
      <header className="help-page__intro">
        <p className="eyebrow">Reviewed platform guide</p>
        <h1>Understand how the Academy works</h1>
        <p>
          Find reviewed explanations of features, financial methods, and known
          limits. This guide explains the platform; it does not give personal
          investment advice.
        </p>
      </header>

      <form action="/help" className="help-search" method="get" role="search">
        <div className="help-search__field">
          <label htmlFor="help-query">Search the guide</label>
          <input
            defaultValue={selection.parameters.query ?? ""}
            id="help-query"
            maxLength={200}
            name="query"
            placeholder="For example, calculations or AI help"
            type="search"
          />
        </div>
        <div className="help-search__field">
          <label htmlFor="help-kind">Type of help</label>
          <select
            defaultValue={selection.parameters.topic_kind ?? ""}
            id="help-kind"
            name="topic_kind"
          >
            <option value="">All topics</option>
            <option value="glossary">Meanings</option>
            <option value="help">How-to help</option>
            <option value="method">Methods</option>
            <option value="limitation">Limits</option>
            <option value="troubleshooting">Problem solving</option>
          </select>
        </div>
        <div className="help-search__field help-search__field--small">
          <label htmlFor="help-page-size">Results per page</label>
          <input
            defaultValue={selection.parameters.page_size ?? 20}
            id="help-page-size"
            max={50}
            min={1}
            name="page_size"
            type="number"
          />
        </div>
        <button type="submit">Show topics</button>
      </form>

      <div aria-live="polite" className="help-results-heading">
        <h2 className="help-results-heading__title">
          {page.results.length === 0
            ? "No matching topics"
            : `${page.results.length} reviewed ${page.results.length === 1 ? "topic" : "topics"}`}
        </h2>
        {page.query ? <p>Showing matches for “{page.query}”.</p> : null}
      </div>

      {page.results.length === 0 ? (
        <div className="help-empty">
          <p>
            Try a shorter phrase, choose all topic types, or clear the search.
          </p>
          <Link to="/help">Clear search</Link>
        </div>
      ) : (
        <div className="help-results">
          {page.results.map((result) => (
            <SearchResultCard
              key={`${result.topic_id}@${result.topic_version}`}
              result={result}
              returnTo={selection.href}
            />
          ))}
        </div>
      )}

      {nextHref ? (
        <nav aria-label="Help results pages" className="help-pagination">
          <Link className="button-link" to={nextHref}>
            Show more topics
          </Link>
        </nav>
      ) : null}

      <details className="technical-record">
        <summary>Technical record</summary>
        <dl>
          <div>
            <dt>Guide version</dt>
            <dd>{page.schema_version}</dd>
          </div>
          <div>
            <dt>Guide fingerprint</dt>
            <dd className="technical-value">{page.corpus_digest}</dd>
          </div>
        </dl>
      </details>
    </section>
  );
}

function HeadingNode({ node }: { node: Extract<PlatformHelpBodyNode, { node_kind: "heading" }> }) {
  if (node.level === 2) return <h2>{node.text}</h2>;
  if (node.level === 3) return <h3>{node.text}</h3>;
  return <h4>{node.text}</h4>;
}

function BodyNode({
  node,
  returnTo,
}: {
  node: PlatformHelpBodyNode;
  returnTo: string;
}) {
  switch (node.node_kind) {
    case "heading":
      return <HeadingNode node={node} />;
    case "paragraph":
      return <p>{node.text}</p>;
    case "list": {
      const items = node.items.map((item, index) => (
        <li key={`${index}-${item}`}>{item}</li>
      ));
      return node.list_kind === "ordered" ? <ol>{items}</ol> : <ul>{items}</ul>;
    }
    case "note":
      return (
        <aside className={`help-note help-note--${node.note_kind}`}>
          <strong>
            {node.note_kind === "warning"
              ? "Important"
              : node.note_kind === "limitation"
                ? "Known limit"
                : "Learning note"}
          </strong>
          <p>{node.text}</p>
        </aside>
      );
    case "topic_reference":
      return (
        <p className="help-topic-reference">
          <Link
            to={platformHelpTopicHref(
              node.topic_id,
              node.topic_version,
              returnTo,
            )}
          >
            {node.label}
          </Link>
        </p>
      );
  }
}

export function PlatformHelpTopicPage({
  selection,
  topic,
}: {
  selection: PlatformHelpTopicSelection;
  topic: PlatformHelpTopic;
}) {
  return (
    <article className="help-page help-topic-page">
      <Link className="help-return-link" to={selection.returnTo}>
        Return to platform guide
      </Link>
      <header className="help-page__intro">
        <p className="eyebrow">{topicKindLabel(topic.topic_kind)}</p>
        <h1>{topic.title}</h1>
        {topic.glossary_term ? (
          <p className="help-term">Term: {topic.glossary_term}</p>
        ) : null}
        <p className="help-topic-summary">{topic.summary}</p>
        <p>
          <strong>Useful for:</strong>{" "}
          {topic.applicability.map((item) => item.label).join(", ")}
        </p>
      </header>

      <div className="help-topic-body">
        {topic.body.map((node, index) => (
          <BodyNode
            key={`${index}-${node.node_kind}`}
            node={node}
            returnTo={selection.returnTo}
          />
        ))}
      </div>

      {topic.related_topics.length > 0 ? (
        <section className="help-related" aria-labelledby="related-help-title">
          <h2 id="related-help-title">Related topics</h2>
          <ul>
            {topic.related_topics.map((related) => (
              <li key={`${related.topic_id}@${related.topic_version}`}>
                <span>{relationshipLabel(related.relationship)}: </span>
                <Link
                  to={platformHelpTopicHref(
                    related.topic_id,
                    related.topic_version,
                    selection.returnTo,
                  )}
                >
                  {related.topic_id.replaceAll("-", " ")}
                </Link>
              </li>
            ))}
          </ul>
        </section>
      ) : null}

      <section className="help-publication" aria-labelledby="publication-title">
        <h2 id="publication-title">Publication details</h2>
        <p>
          Approved and reviewed on {readableDate(topic.publication.reviewed_on)}.
        </p>
        <ul>
          {topic.source_references.map((source) => (
            <li key={source.source_key}>
              {source.title} ({source.area})
            </li>
          ))}
        </ul>
      </section>

      <details className="technical-record">
        <summary>Technical record</summary>
        <dl>
          <div>
            <dt>Exact topic</dt>
            <dd>{topic.topic_id}@{topic.topic_version}</dd>
          </div>
          <div>
            <dt>Topic fingerprint</dt>
            <dd className="technical-value">{topic.topic_digest}</dd>
          </div>
          <div>
            <dt>Contract version</dt>
            <dd>{topic.schema_version}</dd>
          </div>
          {topic.source_references.map((source) => (
            <div key={source.source_key}>
              <dt>{source.source_key}@{source.source_version}</dt>
              <dd className="technical-value">{source.content_fingerprint}</dd>
            </div>
          ))}
        </dl>
      </details>
    </article>
  );
}

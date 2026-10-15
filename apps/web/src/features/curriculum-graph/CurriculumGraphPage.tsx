import { useState } from "react";
import { Link } from "react-router";

import { Icon } from "../../components/Icon";
import type {
  CurriculumActivity,
  CurriculumGraph,
  CurriculumRelationship,
} from "./model";
import { curriculumGraphPresentation } from "./model";

type GraphView = "list" | "map";

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

function activityReference(activity: CurriculumActivity): string {
  const reference = activity.reference;
  return reference.reference_kind === "lesson_placement"
    ? `${reference.package_id}@${reference.package_version} · placement ${reference.placement_id}`
    : `${reference.assessment_id}@${reference.assessment_version} · placement ${reference.placement_id}`;
}

function relationshipText(
  relationship: CurriculumRelationship,
  titles: ReadonlyMap<string, string>,
): string {
  const source = titles.get(relationship.source_id) ?? relationship.source_id;
  const target = titles.get(relationship.target_id) ?? relationship.target_id;
  switch (relationship.kind) {
    case "objective_competency":
      return `${source} connects to ${target}`;
    case "activity_develops_competency":
      return `${source} develops ${target}`;
    case "activity_assesses_competency":
      return `${source} assesses ${target}`;
    case "competency_prerequisite":
      return `${source} is a prerequisite for ${target}`;
    case "activity_prerequisite":
      return `${source} comes before ${target}`;
  }
}

function ActivityCard({ activity }: { activity: CurriculumActivity }) {
  return (
    <article className="curriculum-graph__activity">
      <p className="curriculum-graph__badge">{label(activity.kind)}</p>
      <h4>{activity.title}</h4>
      <dl>
        <div>
          <dt>Activity ID</dt>
          <dd>
            <code>{activity.activity_id}</code>
          </dd>
        </div>
        <div>
          <dt>Exact resource</dt>
          <dd>{activityReference(activity)}</dd>
        </div>
      </dl>
    </article>
  );
}

function GraphFacts({ graph, view }: { graph: CurriculumGraph; view: GraphView }) {
  const presentation = curriculumGraphPresentation(graph);
  const activityById = new Map(
    graph.activities.map((activity) => [activity.activity_id, activity]),
  );
  const branchMemberships = new Set(
    graph.branches.flatMap((branch) => branch.activity_ids),
  );
  const unbranchedActivities = presentation.activities.filter(
    (activity) => !branchMemberships.has(activity.activity_id),
  );
  const titles = new Map<string, string>([
    ...graph.objectives.map(
      (item) => [item.objective_id, item.title] as const,
    ),
    ...graph.competencies.map(
      (item) => [item.competency_id, item.title] as const,
    ),
    ...graph.activities.map(
      (item) => [item.activity_id, item.title] as const,
    ),
  ]);

  return (
    <div
      aria-label={`${label(view)} curriculum graph`}
      className={`curriculum-graph__facts curriculum-graph__facts--${view}`}
      data-testid={`curriculum-graph-${view}`}
    >
      <section className="curriculum-graph__section curriculum-graph__objectives">
        <div className="curriculum-graph__section-heading">
          <p className="eyebrow">Purpose</p>
          <h2>Learning objectives</h2>
        </div>
        <ol>
          {presentation.objectives.map((objective) => (
            <li key={objective.objective_id}>
              <h3>{objective.title}</h3>
              <p>{objective.description}</p>
              <code>{objective.objective_id}</code>
            </li>
          ))}
        </ol>
      </section>

      <section className="curriculum-graph__section curriculum-graph__competencies">
        <div className="curriculum-graph__section-heading">
          <p className="eyebrow">Learning outcomes</p>
          <h2>Competencies</h2>
        </div>
        <ol>
          {presentation.competencies.map((competency) => (
            <li key={competency.competency_id}>
              <h3>{competency.title}</h3>
              <p>{competency.description}</p>
              <code>{competency.competency_id}</code>
            </li>
          ))}
        </ol>
      </section>

      <section className="curriculum-graph__section curriculum-graph__branches">
        <div className="curriculum-graph__section-heading">
          <p className="eyebrow">Reviewed structure</p>
          <h2>Learning branches and activities</h2>
        </div>
        {presentation.branches.length === 0 ? (
          <p className="curriculum-graph__empty">
            This curriculum does not define branch groupings. Its activities
            remain visible below.
          </p>
        ) : (
          <ol className="curriculum-graph__branch-list">
            {presentation.branches.map((branch) => (
              <li key={branch.branch_id}>
                <header>
                  <div>
                    <p className="curriculum-graph__badge">
                      {label(branch.kind)} branch
                    </p>
                    <h3>{branch.title}</h3>
                  </div>
                  <code>{branch.branch_id}</code>
                </header>
                <div className="curriculum-graph__activity-grid">
                  {branch.activity_ids.map((activityId) => {
                    const activity = activityById.get(activityId);
                    return activity ? (
                      <ActivityCard
                        activity={activity}
                        key={`${branch.branch_id}:${activityId}`}
                      />
                    ) : null;
                  })}
                </div>
              </li>
            ))}
          </ol>
        )}
        {unbranchedActivities.length > 0 ? (
          <section className="curriculum-graph__unbranched">
            <h3>Activities outside branch groupings</h3>
            <p>
              These reviewed activities belong to the curriculum without a
              branch label.
            </p>
            <div className="curriculum-graph__activity-grid">
              {unbranchedActivities.map((activity) => (
                <ActivityCard activity={activity} key={activity.activity_id} />
              ))}
            </div>
          </section>
        ) : null}
      </section>

      <section className="curriculum-graph__section curriculum-graph__relationships">
        <div className="curriculum-graph__section-heading">
          <p className="eyebrow">Connections</p>
          <h2>Graph relationships</h2>
        </div>
        {graph.relationships.length === 0 ? (
          <p className="curriculum-graph__empty">
            No relationships are declared for this graph version.
          </p>
        ) : (
          <ol>
            {graph.relationships.map((relationship) => (
              <li key={relationship.relationship_id}>
                <p>{relationshipText(relationship, titles)}</p>
                <span>{label(relationship.kind)}</span>
                <code>{relationship.relationship_id}</code>
              </li>
            ))}
          </ol>
        )}
      </section>
    </div>
  );
}

export function CurriculumGraphPage({ graph }: { graph: CurriculumGraph }) {
  const [view, setView] = useState<GraphView>("list");
  return (
    <section className="curriculum-graph">
      <header className="curriculum-graph__header">
        <p className="eyebrow">Approved curriculum graph</p>
        <h1>{graph.title}</h1>
        <p>{graph.summary}</p>
        <dl className="curriculum-graph__identity">
          <div>
            <dt>Exact version</dt>
            <dd>
              <code>
                {graph.curriculum_id}@{graph.curriculum_version}
              </code>
            </dd>
          </div>
          <div>
            <dt>Published</dt>
            <dd>
              <time dateTime={graph.published_at}>
                {readableDate(graph.published_at)}
              </time>
            </dd>
          </div>
          <div>
            <dt>Publication state</dt>
            <dd>{label(graph.publication_state)}</dd>
          </div>
        </dl>
        <p className="curriculum-graph__notice">
          This page presents reviewed curriculum structure only. It does not
          calculate eligibility, completion, mastery, or a personalized path.
        </p>
      </header>

      <div aria-label="Curriculum graph view" className="curriculum-graph__view-control" role="group">
        <button
          aria-pressed={view === "list"}
          className="button"
          onClick={() => setView("list")}
          type="button"
        >
          List view
        </button>
        <button
          aria-pressed={view === "map"}
          className="button"
          onClick={() => setView("map")}
          type="button"
        >
          Map view
        </button>
      </div>

      <GraphFacts graph={graph} view={view} />

      <section className="curriculum-graph__provenance">
        <div className="curriculum-graph__section-heading">
          <p className="eyebrow">Provenance</p>
          <h2>Exact graph record</h2>
        </div>
        <p>
          <Icon name="citation" />
          This graph is displayed from its protected, immutable versioned
          record. Presentation hints affect order only and do not add facts.
        </p>
        <ul aria-label="Curriculum source references">
          {graph.source_references.map((reference) => (
            <li key={reference}>
              <code>{reference}</code>
            </li>
          ))}
        </ul>
        <details>
          <summary>Technical graph identity</summary>
          <dl>
            <div>
              <dt>Schema version</dt>
              <dd>
                <code>{graph.schema_version}</code>
              </dd>
            </div>
            <div>
              <dt>Graph digest</dt>
              <dd>
                <code>{graph.graph_digest}</code>
              </dd>
            </div>
          </dl>
        </details>
      </section>

      <Link className="button button--secondary curriculum-graph__back" to="/learn">
        Return to learning catalog
      </Link>
    </section>
  );
}

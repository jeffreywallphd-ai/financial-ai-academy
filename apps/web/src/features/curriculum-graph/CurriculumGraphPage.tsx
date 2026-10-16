import { useState } from "react";
import { Link } from "react-router";

import { Icon } from "../../components/Icon";
import type {
  ActivityNavigationState,
  CurriculumActivity,
  CurriculumGraph,
  CurriculumRelationship,
  NavigationState,
} from "./model";
import { curriculumGraphPresentation } from "./model";

type GraphView = "list" | "map";

function label(value: string): string {
  return value
    .split(/[-_]/)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function completionLabel(value: ActivityNavigationState["completion"]): string {
  if (value === "completed") return "Finished";
  if (value === "incomplete") return "Not finished";
  return "Status unavailable";
}

function readinessLabel(value: ActivityNavigationState["eligibility"]): string {
  if (value === "eligible") return "Ready";
  if (value === "locked") return "Blocked";
  return "Status unavailable";
}

function requirementLabel(value: ActivityNavigationState["requirement"]): string {
  if (value === "required") return "Required";
  if (value === "optional") return "Optional";
  return "Not in a group";
}

function availabilityLabel(value: ActivityNavigationState["availability"]): string {
  return value === "available" ? "Available" : "Unavailable";
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

function activityDigest(activity: CurriculumActivity): string {
  const reference = activity.reference;
  return reference.reference_kind === "lesson_placement"
    ? reference.package_digest
    : reference.definition_digest;
}

function reasonText(
  reason: ActivityNavigationState["reasons"][number],
): string {
  switch (reason.code) {
    case "activity_completed":
      return "This activity is recorded as finished.";
    case "required_activity":
      return "This activity is a required part of the learning path.";
    case "optional_activity":
      return "This activity is an optional part of the learning path.";
    case "unassigned_activity":
      return "This activity is part of the learning path but is not in a learning group.";
    case "activity_source_unavailable":
      return "The learning material is not available right now.";
    case "completion_source_unavailable":
      return "The system cannot confirm whether this activity is finished.";
    case "entry_activity":
      return "This activity has no required earlier activity.";
    case "prerequisite_incomplete":
      return "Finish an earlier activity before starting this one.";
    case "prerequisite_unavailable":
      return "The system cannot check an earlier activity right now.";
    case "prerequisite_satisfied":
      return "The required earlier activity is finished.";
  }
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

function navigationIcon(state: ActivityNavigationState) {
  if (state.completion === "completed") return "shield-check" as const;
  if (state.eligibility === "locked") return "lock" as const;
  if (
    state.availability === "unavailable" ||
    state.eligibility === "unavailable"
  ) {
    return "warning-triangle" as const;
  }
  return "info-circle" as const;
}

function ActivityCard({
  activity,
  navigationState,
}: {
  activity: CurriculumActivity;
  navigationState: ActivityNavigationState;
}) {
  return (
    <article className="curriculum-graph__activity">
      <p className="curriculum-graph__badge">{label(activity.kind)}</p>
      <h4>{activity.title}</h4>
      <div className="curriculum-graph__navigation-state">
        <h5>
          <Icon name={navigationIcon(navigationState)} />
          Current activity status
        </h5>
        <dl className="curriculum-graph__state-dimensions">
          <div>
            <dt>Progress</dt>
            <dd>{completionLabel(navigationState.completion)}</dd>
          </div>
          <div>
            <dt>Ready to start</dt>
            <dd>{readinessLabel(navigationState.eligibility)}</dd>
          </div>
          <div>
            <dt>Part of your path</dt>
            <dd>{requirementLabel(navigationState.requirement)}</dd>
          </div>
          <div>
            <dt>Learning material</dt>
            <dd>{availabilityLabel(navigationState.availability)}</dd>
          </div>
        </dl>
        <div className="curriculum-graph__state-reasons">
          <h6>Why you see this status</h6>
          <ol>
            {navigationState.reasons.map((reason, index) => (
              <li key={`${reason.code}:${index}`}>
                <p>{reasonText(reason)}</p>
              </li>
            ))}
          </ol>
        </div>
        <details>
          <summary>Technical record</summary>
          <dl>
            <div>
              <dt>Activity ID</dt>
              <dd>
                <code>{activity.activity_id}</code>
              </dd>
            </div>
            <div>
              <dt>Exact resource</dt>
              <dd>
                <code>{activityReference(activity)}</code>
              </dd>
            </div>
            <div>
              <dt>Resource digest</dt>
              <dd>
                <code>{activityDigest(activity)}</code>
              </dd>
            </div>
            <div>
              <dt>Completion state</dt>
              <dd>
                <code>{navigationState.completion}</code>
              </dd>
            </div>
            <div>
              <dt>Eligibility state</dt>
              <dd>
                <code>{navigationState.eligibility}</code>
              </dd>
            </div>
            <div>
              <dt>Requirement state</dt>
              <dd>
                <code>{navigationState.requirement}</code>
              </dd>
            </div>
            <div>
              <dt>Availability state</dt>
              <dd>
                <code>{navigationState.availability}</code>
              </dd>
            </div>
          </dl>
          <ol aria-label={`${activity.title} technical status reasons`}>
            {navigationState.reasons.map((reason, index) => (
              <li key={`${reason.code}:technical:${index}`}>
                <dl>
                  <div>
                    <dt>Reason code</dt>
                    <dd>
                      <code>{reason.code}</code>
                    </dd>
                  </div>
                  <div>
                    <dt>Recorded explanation</dt>
                    <dd>{reason.explanation}</dd>
                  </div>
                </dl>
                <ul aria-label={`${label(reason.code)} references`}>
                  {reason.references.map((reference) => (
                    <li key={reference}>
                      <code>{reference}</code>
                    </li>
                  ))}
                </ul>
              </li>
            ))}
          </ol>
        </details>
      </div>
    </article>
  );
}

function GraphFacts({
  graph,
  navigationState,
  view,
}: {
  graph: CurriculumGraph;
  navigationState: NavigationState;
  view: GraphView;
}) {
  const presentation = curriculumGraphPresentation(graph);
  const activityById = new Map(
    graph.activities.map((activity) => [activity.activity_id, activity]),
  );
  const navigationByActivityId = new Map(
    navigationState.activity_states.map((state) => [state.activity_id, state]),
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
      aria-label={`${label(view)} learning path`}
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
              <details>
                <summary>Technical record</summary>
                <dl>
                  <div>
                    <dt>Objective ID</dt>
                    <dd>
                      <code>{objective.objective_id}</code>
                    </dd>
                  </div>
                </dl>
              </details>
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
              <details>
                <summary>Technical record</summary>
                <dl>
                  <div>
                    <dt>Competency ID</dt>
                    <dd>
                      <code>{competency.competency_id}</code>
                    </dd>
                  </div>
                </dl>
              </details>
            </li>
          ))}
        </ol>
      </section>

      <section className="curriculum-graph__section curriculum-graph__branches">
        <div className="curriculum-graph__section-heading">
          <p className="eyebrow">Your learning path</p>
          <h2>Learning groups and activities</h2>
        </div>
        {presentation.branches.length === 0 ? (
          <p className="curriculum-graph__empty">
            This learning path does not use groups. Its activities remain
            visible below.
          </p>
        ) : (
          <ol className="curriculum-graph__branch-list">
            {presentation.branches.map((branch) => (
              <li key={branch.branch_id}>
                <header>
                  <div>
                    <p className="curriculum-graph__badge">
                      {label(branch.kind)} group
                    </p>
                    <h3>{branch.title}</h3>
                  </div>
                  <details>
                    <summary>Technical record</summary>
                    <dl>
                      <div>
                        <dt>Branch ID</dt>
                        <dd>
                          <code>{branch.branch_id}</code>
                        </dd>
                      </div>
                    </dl>
                  </details>
                </header>
                <div className="curriculum-graph__activity-grid">
                  {branch.activity_ids.map((activityId) => {
                    const activity = activityById.get(activityId);
                    return activity ? (
                      <ActivityCard
                        activity={activity}
                        key={`${branch.branch_id}:${activityId}`}
                        navigationState={navigationByActivityId.get(activityId)!}
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
            <h3>Activities outside learning groups</h3>
            <p>
              These activities are part of the learning path without a group
              label.
            </p>
            <div className="curriculum-graph__activity-grid">
              {unbranchedActivities.map((activity) => (
                <ActivityCard
                  activity={activity}
                  key={activity.activity_id}
                  navigationState={navigationByActivityId.get(
                    activity.activity_id,
                  )!}
                />
              ))}
            </div>
          </section>
        ) : null}
      </section>

      <section className="curriculum-graph__section curriculum-graph__relationships">
        <div className="curriculum-graph__section-heading">
          <p className="eyebrow">Connections</p>
          <h2>How the activities connect</h2>
        </div>
        {graph.relationships.length === 0 ? (
          <p className="curriculum-graph__empty">
            This learning path does not list any connections.
          </p>
        ) : (
          <ol>
            {graph.relationships.map((relationship) => (
              <li key={relationship.relationship_id}>
                <p>{relationshipText(relationship, titles)}</p>
                <details>
                  <summary>Technical record</summary>
                  <dl>
                    <div>
                      <dt>Relationship type</dt>
                      <dd>
                        <code>{relationship.kind}</code>
                      </dd>
                    </div>
                    <div>
                      <dt>Relationship ID</dt>
                      <dd>
                        <code>{relationship.relationship_id}</code>
                      </dd>
                    </div>
                  </dl>
                </details>
              </li>
            ))}
          </ol>
        )}
      </section>
    </div>
  );
}

export function CurriculumGraphPage({
  graph,
  navigationState,
}: {
  graph: CurriculumGraph;
  navigationState: NavigationState;
}) {
  const [view, setView] = useState<GraphView>("list");
  return (
    <section className="curriculum-graph">
      <header className="curriculum-graph__header">
        <p className="eyebrow">Approved learning path</p>
        <h1>{graph.title}</h1>
        <p>{graph.summary}</p>
        <dl className="curriculum-graph__identity">
          <div>
            <dt>Published</dt>
            <dd>
              <time dateTime={graph.published_at}>
                {readableDate(graph.published_at)}
              </time>
            </dd>
          </div>
          <div>
            <dt>Status</dt>
            <dd>{label(graph.publication_state)}</dd>
          </div>
        </dl>
        <p className="curriculum-graph__notice">
          These status details come from the current learning record. They show
          what is finished, required, available, ready, or blocked. They do not
          measure mastery or competency and do not recommend a path.
        </p>
      </header>

      <div aria-label="Learning path view" className="curriculum-graph__view-control" role="group">
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

      <GraphFacts
        graph={graph}
        navigationState={navigationState}
        view={view}
      />

      <section className="curriculum-graph__provenance">
        <div className="curriculum-graph__section-heading">
          <p className="eyebrow">Supporting information</p>
          <h2>Source and technical record</h2>
        </div>
        <p>
          <Icon name="citation" />
          This approved learning path and its current activity status come from
          protected records. The view can change the order on screen, but it
          does not add or change learning facts.
        </p>
        <details>
          <summary>Technical record</summary>
          <dl>
            <div>
              <dt>Curriculum ID and version</dt>
              <dd>
                <code>
                  {graph.curriculum_id}@{graph.curriculum_version}
                </code>
              </dd>
            </div>
            <div>
              <dt>Graph schema version</dt>
              <dd>
                <code>{graph.schema_version}</code>
              </dd>
            </div>
            <div>
              <dt>Navigation schema version</dt>
              <dd>
                <code>{navigationState.schema_version}</code>
              </dd>
            </div>
            <div>
              <dt>Graph digest</dt>
              <dd>
                <code>{graph.graph_digest}</code>
              </dd>
            </div>
            <div>
              <dt>Navigation evaluated at</dt>
              <dd>
                <time dateTime={navigationState.evaluated_at}>
                  <code>{navigationState.evaluated_at}</code>
                </time>
              </dd>
            </div>
            <div>
              <dt>Navigation policy</dt>
              <dd>
                <code>
                  {navigationState.policy_id}@{navigationState.policy_version}
                </code>
              </dd>
            </div>
            <div>
              <dt>Navigation source set digest</dt>
              <dd>
                <code>{navigationState.source_set_digest}</code>
              </dd>
            </div>
            <div>
              <dt>Navigation projection digest</dt>
              <dd>
                <code>{navigationState.projection_digest}</code>
              </dd>
            </div>
          </dl>
          <ul aria-label="Curriculum source references">
            {graph.source_references.map((reference) => (
              <li key={reference}>
                <code>{reference}</code>
              </li>
            ))}
          </ul>
        </details>
      </section>

      <Link className="button button--secondary curriculum-graph__back" to="/learn">
        Return to learning library
      </Link>
    </section>
  );
}

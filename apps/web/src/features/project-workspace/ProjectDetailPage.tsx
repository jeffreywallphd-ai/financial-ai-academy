import { Link } from "react-router";

import type { ProjectShell } from "./model";
import { readableProjectDate } from "./model";

export function ProjectDetailPage({ project }: { project: ProjectShell }) {
  const learning = project.origin.origin_type === "learning" ? project.origin : null;
  return (
    <article className="project-page project-detail">
      <header className="project-page__header">
        <p className="eyebrow">Active Project</p>
        <h1>{project.title}</h1>
        <p>{project.charter}</p>
        <Link className="button button--secondary" to="/projects">Return to Projects</Link>
      </header>
      <section className="project-panel">
        <h2>Project source</h2>
        {learning ? (
          <><p>This Project began with the learning brief <strong>{learning.brief_title}</strong>.</p><p>{learning.brief_purpose}</p></>
        ) : <p>You started this Project from your own idea.</p>}
        <dl className="project-facts">
          <div><dt>Status</dt><dd>Active</dd></div>
          <div><dt>Started</dt><dd><time dateTime={project.created_at}>{readableProjectDate(project.created_at)}</time></dd></div>
          <div><dt>Last updated</dt><dd><time dateTime={project.updated_at}>{readableProjectDate(project.updated_at)}</time></dd></div>
        </dl>
        <details>
          <summary>Technical record</summary>
          <dl className="project-technical">
            <div><dt>Project ID</dt><dd><code>{project.project_id}</code></dd></div>
            <div><dt>Record revision</dt><dd><code>{project.revision}</code></dd></div>
            {learning ? <>
              <div><dt>Learning placement</dt><dd><code>{learning.placement_id}@{learning.placement_version}</code></dd></div>
              <div><dt>Placement digest</dt><dd><code>{learning.placement_digest}</code></dd></div>
              <div><dt>Brief</dt><dd><code>{learning.brief_id}@{learning.brief_version}</code></dd></div>
              <div><dt>Brief digest</dt><dd><code>{learning.brief_digest}</code></dd></div>
            </> : null}
          </dl>
        </details>
      </section>
    </article>
  );
}

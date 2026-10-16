import { Link } from "react-router";

import { Icon } from "../../components/Icon";
import type { LearningProjectStartOption, ProjectShell } from "./model";
import { readableProjectDate } from "./model";

export function ProjectListPage({ projects, options }: { projects: readonly ProjectShell[]; options: readonly LearningProjectStartOption[] }) {
  return (
    <section className="project-page">
      <header className="project-page__header">
        <p className="eyebrow">Your work</p>
        <h1>Projects</h1>
        <p>Build something from a learning brief or start work from your own idea. A Project stays available outside a lesson.</p>
        <Link className="button project-button--primary" to="/projects/new"><Icon name="learn" />Create independent project</Link>
      </header>

      <section aria-labelledby="learning-projects-heading" className="project-section">
        <h2 id="learning-projects-heading">Start from learning</h2>
        {options.length === 0 ? <p className="project-empty">No learning-based Project is available yet. You can still create an independent Project.</p> : (
          <ul className="project-grid">
            {options.map((option) => (
              <li className="project-card" key={option.origin.placement_id}>
                <h3>{option.title}</h3>
                <p>{option.purpose}</p>
                <Link className="button button--secondary" to={`/projects/new?placement=${encodeURIComponent(option.origin.placement_id)}`}>Start project</Link>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section aria-labelledby="current-projects-heading" className="project-section">
        <h2 id="current-projects-heading">Current Projects</h2>
        {projects.length === 0 ? <p className="project-empty">You have not started a Project yet.</p> : (
          <ul className="project-grid">
            {projects.map((project) => (
              <li className="project-card" key={project.project_id}>
                <p className="project-card__meta">Active · Started {readableProjectDate(project.created_at)}</p>
                <h3>{project.title}</h3>
                <p>{project.charter}</p>
                <Link className="button button--secondary" to={`/projects/${encodeURIComponent(project.project_id)}`}>Open project</Link>
              </li>
            ))}
          </ul>
        )}
      </section>
    </section>
  );
}

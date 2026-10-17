import type { ReactNode } from "react";
import { Link } from "react-router";

import { Icon } from "../../components/Icon";
import { LessonBody } from "./LessonBody";
import type { Lesson } from "./model";


const DATE_FORMAT = new Intl.DateTimeFormat("en", {
  dateStyle: "long",
  timeZone: "UTC",
});

function formatDate(value: string) {
  return DATE_FORMAT.format(new Date(value));
}

export function LessonReadingPage({
  knowledgeCheck,
  lesson,
  returnTo,
}: {
  knowledgeCheck?: ReactNode;
  lesson: Lesson;
  returnTo?: string | undefined;
}) {
  return (
    <div className="lesson-layout">
      <article
        aria-labelledby="lesson-title"
        className="lesson-reading-card"
      >
        <header className="lesson-header">
          <p className="eyebrow">
            <Icon className="faa-icon--active" name="learn" />
            Financial foundations lesson
          </p>
          <h1 id="lesson-title">{lesson.title}</h1>
          <p className="lesson-introduction">
            Learn the key ideas with reviewed educational material and clear
            source information.
          </p>
          {returnTo ? (
            <Link className="button button--secondary lesson-return" to={returnTo}>
              Return to learning path
            </Link>
          ) : null}
          <Link
            className="button button--secondary lesson-return"
            to={`/saved-learning/new?kind=lesson&placement=${encodeURIComponent(lesson.placement_id)}&return=${encodeURIComponent(`/learn/placements/${lesson.placement_id}`)}`}
          >
            <Icon name="learn" />
            Save to Saved learning
          </Link>
        </header>

        <section
          aria-labelledby="learning-objectives"
          className="objectives-card"
        >
          <h2 id="learning-objectives">Learning objectives</h2>
          <ul>
            {lesson.objectives.map((objective) => (
              <li key={objective}>{objective}</li>
            ))}
          </ul>
        </section>

        <section aria-labelledby="lesson-content">
          <h2 className="visually-hidden" id="lesson-content">
            Lesson content
          </h2>
          <LessonBody lesson={lesson} />
        </section>

        {knowledgeCheck}

        <section
          aria-labelledby="educational-sources"
          className="sources-section"
        >
          <h2 id="educational-sources">
            <Icon className="faa-icon--accent" name="citation" />
            Educational sources
          </h2>
          <ul className="source-list">
            {lesson.sources.map((source) => (
              <li key={source.source_id}>
                <a
                  href={source.locator}
                  rel="noopener noreferrer"
                  target="_blank"
                >
                  <span>
                    <strong>{source.title}</strong>
                    <span>{source.publisher}</span>
                    <span>Reviewed {formatDate(source.reviewed_on)}</span>
                  </span>
                  <Icon name="external-link" />
                  <span className="visually-hidden">
                    {" "}
                    (opens in a new tab)
                  </span>
                </a>
                {source.license_note ? (
                  <p>{source.license_note}</p>
                ) : null}
              </li>
            ))}
          </ul>
        </section>
      </article>

      <aside
        aria-labelledby="lesson-provenance"
        className="lesson-context-rail"
      >
        <section className="context-card">
          <h2 id="lesson-provenance">
            <Icon className="faa-icon--success" name="shield-check" />
            Publication details
          </h2>
          <dl>
            <div>
              <dt>Published by</dt>
              <dd>{lesson.provenance.published_by}</dd>
            </div>
            <div>
              <dt>Published</dt>
              <dd>{formatDate(lesson.provenance.published_at)}</dd>
            </div>
            <div>
              <dt>Content reviewed</dt>
              <dd>
                {formatDate(lesson.provenance.content_reviewed_on)}
              </dd>
            </div>
          </dl>
          <details>
            <summary>Technical record</summary>
            <dl>
              <div>
                <dt>Lesson package</dt>
                <dd>{lesson.package_id}</dd>
              </div>
              <div>
                <dt>Lesson version</dt>
                <dd>{lesson.package_version}</dd>
              </div>
              <div>
                <dt>Lesson integrity code</dt>
                <dd>
                  <code>{lesson.package_digest}</code>
                </dd>
              </div>
            </dl>
          </details>
        </section>

        <section
          aria-labelledby="educational-use"
          className="context-card context-card--notice"
        >
          <h2 id="educational-use">
            <Icon className="faa-icon--active" name="info-circle" />
            Educational use
          </h2>
          <p>{lesson.provenance.educational_use_notice}</p>
          <p>
            This lesson teaches general concepts. It does not recommend
            buying, selling, or holding any investment.
          </p>
        </section>
      </aside>
    </div>
  );
}

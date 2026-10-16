import { Icon } from "../../components/Icon";
import type { PracticeItem, PracticePresentation } from "./model";


function itemKind(item: PracticeItem): string {
  switch (item.item_type) {
    case "single_select":
      return "Choose one answer";
    case "multiple_select":
      return "Choose all answers that apply";
    case "numeric_entry":
      return "Enter a number";
  }
}

function decimalPattern(scale: number, allowNegative: boolean): string {
  const sign = allowNegative ? "-?" : "";
  return scale === 0
    ? `${sign}[0-9]+`
    : `${sign}[0-9]+\\.[0-9]{${scale}}`;
}

function PracticeResponseControl({
  index,
  item,
}: {
  index: number;
  item: PracticeItem;
}) {
  const descriptionId = `practice-item-${item.item_id}-description`;
  if (item.item_type === "numeric_entry") {
    return (
      <fieldset className="practice-item">
        <legend>
          <span>Question {index + 1}</span>
          {item.prompt}
        </legend>
        <p className="practice-response-kind" id={descriptionId}>
          Enter a number with exactly {item.scale} decimal {item.scale === 1 ? "place" : "places"}. {item.allow_negative ? "Negative values are allowed." : "Use zero or a positive value."} Unit: {item.unit_label}.
        </p>
        <label htmlFor={`practice-item-${item.item_id}`}>
          Your answer ({item.unit_label})
        </label>
        <input
          aria-describedby={descriptionId}
          autoComplete="off"
          id={`practice-item-${item.item_id}`}
          inputMode="decimal"
          name={item.item_id}
          pattern={decimalPattern(item.scale, item.allow_negative)}
          required
          type="text"
        />
      </fieldset>
    );
  }
  return (
    <fieldset className="practice-item">
      <legend>
        <span>Question {index + 1}</span>
        {item.prompt}
      </legend>
      <p className="practice-response-kind" id={descriptionId}>
        {itemKind(item)}.
      </p>
      <div aria-describedby={descriptionId} className="practice-options">
        {item.options.map((option) => (
          <label key={option.option_id}>
            <input
              name={item.item_id}
              required={item.item_type === "single_select"}
              type={item.item_type === "single_select" ? "radio" : "checkbox"}
              value={option.option_id}
            />
            <span>{option.label}</span>
          </label>
        ))}
      </div>
    </fieldset>
  );
}

function TechnicalRecord({ practice }: { practice: PracticePresentation }) {
  return (
    <details>
      <summary>Technical record</summary>
      <dl>
        <div><dt>Data format version</dt><dd>{practice.schema_version}</dd></div>
        <div><dt>Placement</dt><dd>{practice.placement_id}</dd></div>
        <div><dt>Lesson package</dt><dd>{practice.package_id}</dd></div>
        <div><dt>Lesson version</dt><dd>{practice.package_version}</dd></div>
        <div><dt>Lesson integrity code</dt><dd><code>{practice.package_digest}</code></dd></div>
        <div><dt>Practice activity</dt><dd>{practice.practice_id}</dd></div>
        <div><dt>Practice version</dt><dd>{practice.practice_version}</dd></div>
        <div><dt>Practice integrity code</dt><dd><code>{practice.definition_digest}</code></dd></div>
        <div><dt>Attempt policy</dt><dd>{practice.attempt_policy.policy_id} version {practice.attempt_policy.policy_version}</dd></div>
      </dl>
      <h3>Question records</h3>
      {practice.items.map((item, index) => (
        <dl key={item.item_id}>
          <div><dt>Question</dt><dd>{index + 1}</dd></div>
          <div><dt>Question ID</dt><dd>{item.item_id}</dd></div>
          <div><dt>Question version</dt><dd>{item.item_version}</dd></div>
          <div><dt>Response type</dt><dd>{item.item_type}</dd></div>
          <div><dt>Scoring policy</dt><dd>{item.scoring_policy_id} version {item.scoring_policy_version}</dd></div>
          <div><dt>Maximum score</dt><dd>{item.max_score}</dd></div>
          {"options" in item
            ? item.options.map((option) => (
                <div key={option.option_id}>
                  <dt>Choice ID</dt><dd>{option.option_id}</dd>
                </div>
              ))
            : null}
        </dl>
      ))}
      <h3>Resource records</h3>
      {[...practice.source_references, ...practice.review_references].map(
        (reference, index) => (
          <dl key={`${reference.resource_id}-${reference.resource_digest}-${index}`}>
            <div><dt>Resource</dt><dd>{reference.resource_id}</dd></div>
            <div><dt>Resource version</dt><dd>{reference.resource_version}</dd></div>
            <div><dt>Resource integrity code</dt><dd><code>{reference.resource_digest}</code></dd></div>
          </dl>
        ),
      )}
    </details>
  );
}

export function PracticeActivityPage({
  practice,
}: {
  practice: PracticePresentation;
}) {
  return (
    <div className="practice-layout">
      <article aria-labelledby="practice-title" className="practice-card">
        <header className="practice-header">
          <p className="eyebrow">
            <Icon className="faa-icon--active" name="learn" />
            Practice activity
          </p>
          <h1 id="practice-title">{practice.title}</h1>
          <p className="practice-purpose">{practice.purpose}</p>
          <p>{practice.instructions}</p>
        </header>

        <section aria-labelledby="practice-response-status" className="practice-notice">
          <h2 id="practice-response-status">Review and try the questions</h2>
          <p>
            You can enter responses on this page, but this opening step does not check or save them yet.
          </p>
        </section>

        <section aria-labelledby="practice-questions">
          <h2 id="practice-questions">Questions</h2>
          <div className="practice-question-list">
            {practice.items.map((item, index) => (
              <PracticeResponseControl index={index} item={item} key={item.item_id} />
            ))}
          </div>
        </section>

        <section aria-labelledby="practice-resources" className="practice-resources">
          <h2 id="practice-resources">Learning and review material</h2>
          <div className="practice-resource-groups">
            <div>
              <h3>Learning material</h3>
              <ul>{practice.source_references.map((reference) => <li key={reference.resource_id}>{reference.title}</li>)}</ul>
            </div>
            <div>
              <h3>Review material</h3>
              <ul>{practice.review_references.map((reference) => <li key={reference.resource_id}>{reference.title}</li>)}</ul>
            </div>
          </div>
        </section>
      </article>

      <aside aria-label="Practice activity details" className="practice-context-rail">
        <section aria-labelledby="attempt-policy" className="context-card">
          <h2 id="attempt-policy">
            <Icon className="faa-icon--success" name="shield-check" />
            How attempts will work
          </h2>
          <p>You can make up to {practice.attempt_policy.max_attempts} attempts.</p>
          <p>You can pause and return, and you can view earlier attempts.</p>
          <p>Answer checking and saved attempts are not available in this opening step.</p>
        </section>
        <section aria-labelledby="practice-evidence" className="context-card">
          <h2 id="practice-evidence">Activity details</h2>
          <p>
            This activity checks general learning. It does not assess investment suitability, provide investment advice, or show mastery or certification.
          </p>
          <TechnicalRecord practice={practice} />
        </section>
      </aside>
    </div>
  );
}

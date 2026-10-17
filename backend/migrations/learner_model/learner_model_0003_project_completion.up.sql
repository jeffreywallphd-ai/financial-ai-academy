CREATE TABLE learner_model.project_completion_projections (
    learner_id uuid NOT NULL,
    project_id text NOT NULL,
    completed boolean NOT NULL,
    history_count integer NOT NULL,
    source_digest char(64) NOT NULL,
    rebuilt_at timestamptz NOT NULL,
    PRIMARY KEY (learner_id, project_id),
    CONSTRAINT learner_model_project_projection_project_profile
        CHECK (project_id ~ '^[a-z0-9][a-z0-9._-]{0,127}$'),
    CONSTRAINT learner_model_project_projection_history_count
        CHECK (history_count BETWEEN 0 AND 100),
    CONSTRAINT learner_model_project_projection_completion
        CHECK (completed = (history_count > 0)),
    CONSTRAINT learner_model_project_projection_source_digest
        CHECK (source_digest ~ '^[a-f0-9]{64}$')
);

CREATE TABLE learner_model.project_completion_history (
    learner_id uuid NOT NULL,
    project_id text NOT NULL,
    occurrence integer NOT NULL,
    accepted_sequence bigint NOT NULL,
    event_id text NOT NULL,
    evidence_id text NOT NULL,
    submission_id text NOT NULL,
    snapshot_id text NOT NULL,
    snapshot_digest char(64) NOT NULL,
    brief_id text NOT NULL,
    brief_version text NOT NULL,
    brief_digest char(64) NOT NULL,
    placement_id text NOT NULL,
    placement_version text NOT NULL,
    placement_digest char(64) NOT NULL,
    policy_id text NOT NULL,
    policy_version text NOT NULL,
    milestone_ids jsonb NOT NULL,
    request_fingerprint char(64) NOT NULL,
    supersedes_submission_id text,
    submitted_at timestamptz NOT NULL,
    occurred_at timestamptz NOT NULL,
    PRIMARY KEY (learner_id, project_id, occurrence),
    CONSTRAINT learner_model_project_history_projection_fk
        FOREIGN KEY (learner_id, project_id)
        REFERENCES learner_model.project_completion_projections (
            learner_id, project_id
        ) ON DELETE CASCADE,
    CONSTRAINT learner_model_project_history_occurrence
        CHECK (occurrence BETWEEN 1 AND 100),
    CONSTRAINT learner_model_project_history_sequence
        CHECK (accepted_sequence >= 1),
    CONSTRAINT learner_model_project_history_policy
        CHECK (
            policy_id = 'assessment-project-closure'
            AND policy_version = '1.0.0'
        ),
    CONSTRAINT learner_model_project_history_digests
        CHECK (
            snapshot_digest ~ '^[a-f0-9]{64}$'
            AND brief_digest ~ '^[a-f0-9]{64}$'
            AND placement_digest ~ '^[a-f0-9]{64}$'
            AND request_fingerprint ~ '^[a-f0-9]{64}$'
        ),
    CONSTRAINT learner_model_project_history_milestones
        CHECK (
            jsonb_typeof(milestone_ids) = 'array'
            AND jsonb_array_length(milestone_ids) BETWEEN 1 AND 20
        ),
    CONSTRAINT learner_model_project_history_time
        CHECK (occurred_at >= submitted_at),
    UNIQUE (event_id),
    UNIQUE (evidence_id),
    UNIQUE (learner_id, submission_id)
);

COMMENT ON TABLE learner_model.project_completion_projections IS
    'Replaceable Project activity completion rebuilt from Assessment evidence.';
COMMENT ON TABLE learner_model.project_completion_history IS
    'Replaceable public source references; not mastery, grading, or advice.';

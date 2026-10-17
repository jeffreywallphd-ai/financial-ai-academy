CREATE SCHEMA IF NOT EXISTS personal_workspace;

CREATE TABLE personal_workspace.workspaces (
    workspace_id text PRIMARY KEY,
    learner_id text NOT NULL UNIQUE,
    revision integer NOT NULL,
    workspace jsonb NOT NULL,
    created_at timestamptz NOT NULL,
    updated_at timestamptz NOT NULL,
    CONSTRAINT personal_workspace_id_profile
        CHECK (workspace_id ~ '^[a-z0-9][a-z0-9._-]{0,127}$'),
    CONSTRAINT personal_workspace_learner_profile
        CHECK (learner_id ~ '^[a-z0-9][a-z0-9._-]{0,127}$'),
    CONSTRAINT personal_workspace_revision_profile CHECK (revision >= 2),
    CONSTRAINT personal_workspace_shape CHECK (
        jsonb_typeof(workspace) = 'object'
        AND workspace->>'schema_version' = '1.0.0'
        AND workspace->>'workspace_id' = workspace_id
        AND workspace->>'learner_id' = learner_id
        AND (workspace->>'revision')::integer = revision
    ),
    CONSTRAINT personal_workspace_time_profile CHECK (updated_at >= created_at)
);

CREATE TABLE personal_workspace.mutations (
    learner_id text NOT NULL,
    workspace_id text NOT NULL
        REFERENCES personal_workspace.workspaces(workspace_id),
    idempotency_key text NOT NULL,
    request_fingerprint char(64) NOT NULL,
    accepted_workspace jsonb NOT NULL,
    accepted_revision integer NOT NULL,
    PRIMARY KEY (learner_id, idempotency_key),
    CONSTRAINT personal_workspace_mutation_key_profile
        CHECK (idempotency_key ~ '^[a-z0-9][a-z0-9._-]{0,127}$'),
    CONSTRAINT personal_workspace_mutation_fingerprint_profile
        CHECK (request_fingerprint ~ '^[a-f0-9]{64}$'),
    CONSTRAINT personal_workspace_mutation_revision_profile
        CHECK (accepted_revision >= 2),
    CONSTRAINT personal_workspace_mutation_shape CHECK (
        jsonb_typeof(accepted_workspace) = 'object'
        AND accepted_workspace->>'workspace_id' = workspace_id
        AND accepted_workspace->>'learner_id' = learner_id
        AND (accepted_workspace->>'revision')::integer = accepted_revision
    )
);

COMMENT ON TABLE personal_workspace.workspaces IS
    'Learner-owned Personal workspace aggregate with optimistic revision.';
COMMENT ON TABLE personal_workspace.mutations IS
    'Canonical request fingerprints and exact accepted workspace replays.';

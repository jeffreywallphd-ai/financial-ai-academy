CREATE TABLE project.project_workspaces (
    project_id text PRIMARY KEY REFERENCES project.project_shells(project_id),
    learner_id text NOT NULL,
    workspace_revision integer NOT NULL,
    workspace jsonb NOT NULL,
    created_at timestamptz NOT NULL,
    updated_at timestamptz NOT NULL,
    CONSTRAINT project_workspace_learner_profile
        CHECK (learner_id ~ '^[a-z0-9][a-z0-9._-]{0,127}$'),
    CONSTRAINT project_workspace_revision_profile
        CHECK (workspace_revision >= 1),
    CONSTRAINT project_workspace_shape CHECK (
        jsonb_typeof(workspace) = 'object'
        AND workspace->>'schema_version' = '1.0.0'
        AND workspace->>'project_id' = project_id
        AND workspace->>'learner_id' = learner_id
        AND (workspace->>'workspace_revision')::integer = workspace_revision
    ),
    CONSTRAINT project_workspace_time_profile CHECK (updated_at >= created_at),
    UNIQUE (learner_id, project_id)
);

CREATE TABLE project.project_workspace_mutations (
    learner_id text NOT NULL,
    project_id text NOT NULL REFERENCES project.project_workspaces(project_id),
    idempotency_key text NOT NULL,
    request_fingerprint char(64) NOT NULL,
    accepted_workspace jsonb NOT NULL,
    accepted_revision integer NOT NULL,
    PRIMARY KEY (learner_id, project_id, idempotency_key),
    CONSTRAINT project_mutation_key_profile
        CHECK (idempotency_key ~ '^[a-z0-9][a-z0-9._-]{0,127}$'),
    CONSTRAINT project_mutation_fingerprint_profile
        CHECK (request_fingerprint ~ '^[a-f0-9]{64}$'),
    CONSTRAINT project_mutation_revision_profile CHECK (accepted_revision >= 2),
    CONSTRAINT project_mutation_workspace_shape CHECK (
        jsonb_typeof(accepted_workspace) = 'object'
        AND accepted_workspace->>'project_id' = project_id
        AND accepted_workspace->>'learner_id' = learner_id
        AND (accepted_workspace->>'workspace_revision')::integer = accepted_revision
    )
);

CREATE TABLE project.project_artifact_objects (
    learner_id text NOT NULL,
    project_id text NOT NULL REFERENCES project.project_workspaces(project_id),
    artifact_id text NOT NULL,
    artifact_version integer NOT NULL,
    object_key text NOT NULL,
    content_digest char(64) NOT NULL,
    byte_count integer NOT NULL,
    PRIMARY KEY (learner_id, project_id, artifact_id, artifact_version),
    CONSTRAINT project_artifact_id_profile
        CHECK (artifact_id ~ '^[a-z0-9][a-z0-9._-]{0,127}$'),
    CONSTRAINT project_artifact_version_profile CHECK (artifact_version >= 1),
    CONSTRAINT project_artifact_object_key_profile
        CHECK (object_key ~ '^[a-f0-9]{2}/[a-f0-9]{64}$'),
    CONSTRAINT project_artifact_digest_profile
        CHECK (content_digest ~ '^[a-f0-9]{64}$'),
    CONSTRAINT project_artifact_byte_profile
        CHECK (byte_count BETWEEN 0 AND 10485760)
);

CREATE TABLE project.project_snapshots (
    snapshot_id text PRIMARY KEY,
    learner_id text NOT NULL,
    project_id text NOT NULL REFERENCES project.project_workspaces(project_id),
    idempotency_key text NOT NULL,
    request_fingerprint char(64) NOT NULL,
    snapshot_digest char(64) NOT NULL,
    workspace_revision integer NOT NULL,
    snapshot jsonb NOT NULL,
    workspace jsonb NOT NULL,
    closed_at timestamptz NOT NULL,
    UNIQUE (learner_id, project_id, idempotency_key),
    CONSTRAINT project_snapshot_id_profile
        CHECK (snapshot_id ~ '^[a-z0-9][a-z0-9._-]{0,127}$'),
    CONSTRAINT project_snapshot_key_profile
        CHECK (idempotency_key ~ '^[a-z0-9][a-z0-9._-]{0,127}$'),
    CONSTRAINT project_snapshot_fingerprint_profile
        CHECK (request_fingerprint ~ '^[a-f0-9]{64}$'),
    CONSTRAINT project_snapshot_digest_profile
        CHECK (snapshot_digest ~ '^[a-f0-9]{64}$'),
    CONSTRAINT project_snapshot_revision_profile CHECK (workspace_revision >= 1),
    CONSTRAINT project_snapshot_shape CHECK (
        jsonb_typeof(snapshot) = 'object'
        AND snapshot->>'snapshot_id' = snapshot_id
        AND snapshot->>'snapshot_digest' = snapshot_digest
        AND snapshot->'snapshot'->>'project_id' = project_id
        AND snapshot->'snapshot'->>'learner_id' = learner_id
        AND (snapshot->'snapshot'->>'workspace_revision')::integer = workspace_revision
        AND jsonb_typeof(workspace) = 'object'
        AND workspace->>'project_id' = project_id
        AND workspace->>'learner_id' = learner_id
        AND (workspace->>'workspace_revision')::integer = workspace_revision
    )
);

CREATE INDEX project_snapshots_project_order
    ON project.project_snapshots (learner_id, project_id, closed_at, snapshot_id);

CREATE FUNCTION project.reject_project_snapshot_mutation()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE EXCEPTION 'Project snapshots are append-only'
        USING ERRCODE = '55000';
END;
$$;

CREATE TRIGGER project_snapshots_append_only
BEFORE UPDATE OR DELETE ON project.project_snapshots
FOR EACH ROW
EXECUTE FUNCTION project.reject_project_snapshot_mutation();

COMMENT ON TABLE project.project_workspaces IS
    'Project-owned mutable workspace aggregate with optimistic revision.';
COMMENT ON TABLE project.project_artifact_objects IS
    'Opaque content-addressed Project artifact references; bytes remain outside PostgreSQL.';
COMMENT ON TABLE project.project_snapshots IS
    'Immutable digest-bound Project workspace snapshots and exact workspace records.';

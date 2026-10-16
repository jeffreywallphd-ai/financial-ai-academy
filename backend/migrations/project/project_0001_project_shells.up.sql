CREATE SCHEMA IF NOT EXISTS project;

CREATE TABLE project.project_shells (
    project_id text PRIMARY KEY,
    learner_id text NOT NULL,
    idempotency_key text NOT NULL,
    request_fingerprint char(64) NOT NULL,
    schema_version text NOT NULL,
    title text NOT NULL,
    charter text NOT NULL,
    origin jsonb NOT NULL,
    lifecycle text NOT NULL,
    revision integer NOT NULL,
    created_at timestamptz NOT NULL,
    updated_at timestamptz NOT NULL,
    UNIQUE (learner_id, idempotency_key),
    CONSTRAINT project_shell_id_profile
        CHECK (project_id ~ '^[a-z0-9][a-z0-9._-]{0,127}$'),
    CONSTRAINT project_shell_learner_profile
        CHECK (learner_id ~ '^[a-z0-9][a-z0-9._-]{0,127}$'),
    CONSTRAINT project_shell_idempotency_profile
        CHECK (idempotency_key ~ '^[a-z0-9][a-z0-9._-]{0,127}$'),
    CONSTRAINT project_shell_fingerprint_profile
        CHECK (request_fingerprint ~ '^[a-f0-9]{64}$'),
    CONSTRAINT project_shell_schema_profile CHECK (schema_version = '1.0.0'),
    CONSTRAINT project_shell_title_profile CHECK (
        char_length(title) BETWEEN 1 AND 120
        AND title !~ '[<>&[:cntrl:]]'
    ),
    CONSTRAINT project_shell_charter_profile CHECK (
        char_length(charter) BETWEEN 1 AND 4000
        AND charter !~ '[<>&[:cntrl:]]'
    ),
    CONSTRAINT project_shell_origin_profile CHECK (
        jsonb_typeof(origin) = 'object'
        AND origin->>'origin_type' IN ('independent', 'learning')
    ),
    CONSTRAINT project_shell_lifecycle_profile CHECK (lifecycle = 'active'),
    CONSTRAINT project_shell_revision_profile CHECK (revision >= 1),
    CONSTRAINT project_shell_time_profile CHECK (updated_at >= created_at)
);

CREATE INDEX project_shells_learner_order
    ON project.project_shells (learner_id, created_at, project_id);

CREATE FUNCTION project.reject_project_shell_mutation()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE EXCEPTION 'project shells are append-only in workspace v1'
        USING ERRCODE = '55000';
END;
$$;

CREATE TRIGGER project_shells_append_only
BEFORE UPDATE OR DELETE ON project.project_shells
FOR EACH ROW
EXECUTE FUNCTION project.reject_project_shell_mutation();

COMMENT ON TABLE project.project_shells IS
    'Learner-owned immutable Project shell and accepted origin.';

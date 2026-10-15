CREATE SCHEMA IF NOT EXISTS audit;

CREATE TABLE audit.assessment_completion_records (
    audit_id uuid PRIMARY KEY,
    event_id uuid NOT NULL UNIQUE,
    evidence_id uuid NOT NULL UNIQUE,
    attempt_id uuid NOT NULL UNIQUE,
    actor_id uuid NOT NULL,
    action text NOT NULL,
    placement_id text NOT NULL,
    package_id text NOT NULL,
    package_version text NOT NULL,
    package_digest char(64) NOT NULL,
    assessment_id text NOT NULL,
    assessment_version text NOT NULL,
    definition_digest char(64) NOT NULL,
    occurred_at timestamptz NOT NULL,
    integrity_digest char(64) NOT NULL,
    recorded_at timestamptz NOT NULL,
    CONSTRAINT audit_assessment_completion_action
        CHECK (action = 'assessment.knowledge-check.completed'),
    CONSTRAINT audit_package_digest_profile
        CHECK (package_digest ~ '^[a-f0-9]{64}$'),
    CONSTRAINT audit_definition_digest_profile
        CHECK (definition_digest ~ '^[a-f0-9]{64}$'),
    CONSTRAINT audit_integrity_digest_profile
        CHECK (integrity_digest ~ '^[a-f0-9]{64}$')
);

CREATE INDEX audit_assessment_completion_context
    ON audit.assessment_completion_records (
        actor_id, placement_id, occurred_at, event_id
    );

CREATE FUNCTION audit.reject_record_mutation()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE EXCEPTION 'accepted audit records are append-only'
        USING ERRCODE = '55000';
END;
$$;

CREATE TRIGGER audit_assessment_completion_append_only
    BEFORE UPDATE OR DELETE ON audit.assessment_completion_records
    FOR EACH ROW EXECUTE FUNCTION audit.reject_record_mutation();

COMMENT ON TABLE audit.assessment_completion_records IS
    'Integrity/provenance references only; Assessment remains business authority.';

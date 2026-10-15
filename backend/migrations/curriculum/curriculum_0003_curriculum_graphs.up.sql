CREATE TABLE curriculum.curriculum_graph_versions (
    curriculum_id text NOT NULL,
    curriculum_version text NOT NULL,
    graph_digest char(64) NOT NULL,
    published_at timestamptz NOT NULL,
    graph_payload jsonb NOT NULL,
    stored_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (curriculum_id, curriculum_version),
    CONSTRAINT curriculum_graph_id_profile
        CHECK (curriculum_id ~ '^[a-z0-9][a-z0-9._-]{2,63}$'),
    CONSTRAINT curriculum_graph_version_profile
        CHECK (
            curriculum_version ~
            '^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(-[0-9A-Za-z.-]+)?$'
        ),
    CONSTRAINT curriculum_graph_digest_profile
        CHECK (graph_digest ~ '^[a-f0-9]{64}$'),
    CONSTRAINT curriculum_graph_payload_object
        CHECK (jsonb_typeof(graph_payload) = 'object'),
    CONSTRAINT curriculum_graph_payload_schema
        CHECK (graph_payload ->> 'schema_version' = '1.0.0'),
    CONSTRAINT curriculum_graph_payload_approved
        CHECK (graph_payload ->> 'publication_state' = 'approved'),
    CONSTRAINT curriculum_graph_payload_id
        CHECK (graph_payload ->> 'curriculum_id' = curriculum_id),
    CONSTRAINT curriculum_graph_payload_version
        CHECK (graph_payload ->> 'curriculum_version' = curriculum_version),
    CONSTRAINT curriculum_graph_payload_digest
        CHECK (graph_payload ->> 'graph_digest' = graph_digest),
    CONSTRAINT curriculum_graph_payload_published_at
        CHECK (
            (graph_payload ->> 'published_at')::timestamptz = published_at
        )
);

CREATE UNIQUE INDEX curriculum_graph_digest_identity
    ON curriculum.curriculum_graph_versions (graph_digest);

CREATE FUNCTION curriculum.reject_curriculum_graph_version_mutation()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE EXCEPTION 'approved curriculum graph versions are append-only'
        USING ERRCODE = '55000';
END;
$$;

CREATE TRIGGER curriculum_graph_versions_append_only
BEFORE UPDATE OR DELETE ON curriculum.curriculum_graph_versions
FOR EACH ROW
EXECUTE FUNCTION curriculum.reject_curriculum_graph_version_mutation();

COMMENT ON TABLE curriculum.curriculum_graph_versions IS
    'Immutable approved Curriculum graph aggregates; public validation remains authoritative.';

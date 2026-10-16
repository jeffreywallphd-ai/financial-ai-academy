CREATE TABLE curriculum.project_brief_placements (
    placement_id text PRIMARY KEY,
    placement_version text NOT NULL,
    placement_digest char(64) NOT NULL,
    curriculum_id text NOT NULL,
    curriculum_version text NOT NULL,
    curriculum_digest char(64) NOT NULL,
    activity_id text NOT NULL,
    package_id text NOT NULL,
    package_version text NOT NULL,
    package_digest char(64) NOT NULL,
    brief_id text NOT NULL,
    brief_version text NOT NULL,
    brief_digest char(64) NOT NULL,
    project_brief_schema_version text NOT NULL,
    created_at timestamptz NOT NULL,
    CONSTRAINT curriculum_project_brief_placement_id_profile
        CHECK (placement_id ~ '^[a-z0-9][a-z0-9._-]{2,127}$'),
    CONSTRAINT curriculum_project_brief_identity_profile
        CHECK (
            curriculum_id ~ '^[a-z0-9][a-z0-9._-]{2,127}$'
            AND activity_id ~ '^[a-z0-9][a-z0-9._-]{2,127}$'
            AND package_id ~ '^[a-z0-9][a-z0-9._-]{2,127}$'
            AND brief_id ~ '^[a-z0-9][a-z0-9._-]{2,127}$'
        ),
    CONSTRAINT curriculum_project_brief_version_profile
        CHECK (
            placement_version ~ '^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$'
            AND curriculum_version ~ '^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$'
            AND package_version ~ '^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$'
            AND brief_version ~ '^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$'
            AND project_brief_schema_version = '1.0.0'
        ),
    CONSTRAINT curriculum_project_brief_digest_profile
        CHECK (
            placement_digest ~ '^[a-f0-9]{64}$'
            AND curriculum_digest ~ '^[a-f0-9]{64}$'
            AND package_digest ~ '^[a-f0-9]{64}$'
            AND brief_digest ~ '^[a-f0-9]{64}$'
        )
);

CREATE FUNCTION curriculum.reject_project_brief_placement_mutation()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE EXCEPTION 'project brief placements are append-only'
        USING ERRCODE = '55000';
END;
$$;

CREATE TRIGGER curriculum_project_brief_placements_append_only
BEFORE UPDATE OR DELETE ON curriculum.project_brief_placements
FOR EACH ROW
EXECUTE FUNCTION curriculum.reject_project_brief_placement_mutation();

COMMENT ON TABLE curriculum.project_brief_placements IS
    'Immutable exact Curriculum placements for approved learning Project briefs.';

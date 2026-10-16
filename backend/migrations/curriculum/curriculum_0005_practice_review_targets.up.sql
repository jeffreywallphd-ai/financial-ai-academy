CREATE TABLE curriculum.practice_review_targets (
    practice_placement_id text NOT NULL,
    resource_id text NOT NULL,
    resource_version text NOT NULL,
    resource_digest char(64) NOT NULL,
    resource_title text NOT NULL,
    state text NOT NULL,
    destination_placement_id text,
    destination_package_id text,
    destination_package_version text,
    destination_package_digest char(64),
    destination_section_id text,
    unavailable_reason text,
    created_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (
        practice_placement_id,
        resource_id,
        resource_version,
        resource_digest
    ),
    CONSTRAINT curriculum_practice_review_practice_fk
        FOREIGN KEY (practice_placement_id)
        REFERENCES curriculum.practice_placements (placement_id),
    CONSTRAINT curriculum_practice_review_practice_id_profile
        CHECK (practice_placement_id ~ '^[a-z0-9][a-z0-9._-]{2,63}$'),
    CONSTRAINT curriculum_practice_review_resource_id_profile
        CHECK (resource_id ~ '^[a-z0-9][a-z0-9._-]{2,63}$'),
    CONSTRAINT curriculum_practice_review_resource_version_profile
        CHECK (
            resource_version ~
            '^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$'
        ),
    CONSTRAINT curriculum_practice_review_resource_digest_profile
        CHECK (resource_digest ~ '^[a-f0-9]{64}$'),
    CONSTRAINT curriculum_practice_review_resource_title_profile
        CHECK (
            char_length(resource_title) BETWEEN 1 AND 240
            AND resource_title !~ '[<>&[:cntrl:]]'
        ),
    CONSTRAINT curriculum_practice_review_state_profile
        CHECK (state IN ('available', 'unavailable')),
    CONSTRAINT curriculum_practice_review_destination_id_profile
        CHECK (
            destination_placement_id IS NULL
            OR destination_placement_id ~ '^[a-z0-9][a-z0-9._-]{2,63}$'
        ),
    CONSTRAINT curriculum_practice_review_destination_package_profile
        CHECK (
            destination_package_id IS NULL
            OR destination_package_id ~ '^[a-z0-9][a-z0-9._-]{2,63}$'
        ),
    CONSTRAINT curriculum_practice_review_destination_version_profile
        CHECK (
            destination_package_version IS NULL
            OR destination_package_version ~
                '^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$'
        ),
    CONSTRAINT curriculum_practice_review_destination_digest_profile
        CHECK (
            destination_package_digest IS NULL
            OR destination_package_digest ~ '^[a-f0-9]{64}$'
        ),
    CONSTRAINT curriculum_practice_review_section_profile
        CHECK (
            destination_section_id IS NULL
            OR destination_section_id ~ '^[a-z0-9][a-z0-9._-]{2,63}$'
        ),
    CONSTRAINT curriculum_practice_review_reason_profile
        CHECK (
            unavailable_reason IS NULL
            OR unavailable_reason IN (
                'mapping_not_found',
                'destination_not_available',
                'version_mismatch'
            )
        ),
    CONSTRAINT curriculum_practice_review_state_shape
        CHECK (
            (
                state = 'available'
                AND destination_placement_id IS NOT NULL
                AND destination_package_id IS NOT NULL
                AND destination_package_version IS NOT NULL
                AND destination_package_digest IS NOT NULL
                AND unavailable_reason IS NULL
            )
            OR
            (
                state = 'unavailable'
                AND destination_placement_id IS NULL
                AND destination_package_id IS NULL
                AND destination_package_version IS NULL
                AND destination_package_digest IS NULL
                AND destination_section_id IS NULL
                AND unavailable_reason IS NOT NULL
            )
        )
);

CREATE FUNCTION curriculum.reject_practice_review_target_mutation()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE EXCEPTION 'practice review targets are append-only'
        USING ERRCODE = '55000';
END;
$$;

CREATE TRIGGER curriculum_practice_review_targets_append_only
BEFORE UPDATE OR DELETE ON curriculum.practice_review_targets
FOR EACH ROW
EXECUTE FUNCTION curriculum.reject_practice_review_target_mutation();

COMMENT ON TABLE curriculum.practice_review_targets IS
    'Immutable exact review-resource mappings to safe Curriculum destinations.';

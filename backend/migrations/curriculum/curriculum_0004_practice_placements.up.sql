CREATE TABLE curriculum.practice_placements (
    placement_id text PRIMARY KEY
        REFERENCES curriculum.lesson_placements (placement_id)
        ON DELETE RESTRICT,
    package_id text NOT NULL,
    package_version text NOT NULL,
    package_digest char(64) NOT NULL,
    practice_id text NOT NULL,
    practice_version text NOT NULL,
    definition_digest char(64) NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT curriculum_practice_package_digest_profile
        CHECK (package_digest ~ '^[a-f0-9]{64}$'),
    CONSTRAINT curriculum_practice_definition_digest_profile
        CHECK (definition_digest ~ '^[a-f0-9]{64}$')
);

CREATE UNIQUE INDEX curriculum_exact_practice_reference
    ON curriculum.practice_placements (
        package_id,
        package_version,
        package_digest,
        practice_id,
        practice_version,
        definition_digest
    );

COMMENT ON TABLE curriculum.practice_placements IS
    'Curriculum-owned exact Content practice references; no cross-module persistence access.';

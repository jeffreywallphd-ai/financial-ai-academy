CREATE TABLE curriculum.assessment_placements (
    placement_id text PRIMARY KEY
        REFERENCES curriculum.lesson_placements (placement_id)
        ON DELETE RESTRICT,
    package_id text NOT NULL,
    package_version text NOT NULL,
    package_digest char(64) NOT NULL,
    assessment_id text NOT NULL,
    assessment_version text NOT NULL,
    definition_digest char(64) NOT NULL,
    item_id text NOT NULL,
    item_version text NOT NULL,
    scoring_policy_id text NOT NULL,
    scoring_policy_version text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT curriculum_assessment_package_digest_profile
        CHECK (package_digest ~ '^[a-f0-9]{64}$'),
    CONSTRAINT curriculum_assessment_definition_digest_profile
        CHECK (definition_digest ~ '^[a-f0-9]{64}$')
);

CREATE UNIQUE INDEX curriculum_exact_assessment_reference
    ON curriculum.assessment_placements (
        package_id,
        package_version,
        package_digest,
        assessment_id,
        assessment_version,
        definition_digest
    );

COMMENT ON TABLE curriculum.assessment_placements IS
    'Curriculum-owned exact Content and Assessment references; no cross-module persistence access.';


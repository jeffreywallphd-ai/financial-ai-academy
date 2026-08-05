CREATE SCHEMA IF NOT EXISTS curriculum;

CREATE TABLE curriculum.lesson_placements (
    placement_id text PRIMARY KEY,
    package_id text NOT NULL,
    package_version text NOT NULL,
    package_digest char(64) NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT curriculum_package_digest_profile
        CHECK (package_digest ~ '^[a-f0-9]{64}$')
);

CREATE INDEX curriculum_lesson_placement_content_reference
    ON curriculum.lesson_placements (
        package_id,
        package_version,
        package_digest
    );

COMMENT ON TABLE curriculum.lesson_placements IS
    'Curriculum-owned exact Content references; intentionally no cross-module foreign key.';

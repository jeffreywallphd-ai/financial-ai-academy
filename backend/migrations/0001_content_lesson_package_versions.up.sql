CREATE SCHEMA IF NOT EXISTS content;

CREATE TABLE content.lesson_package_versions (
    package_id text NOT NULL,
    package_version text NOT NULL,
    package_digest char(64) NOT NULL,
    publication_state text NOT NULL,
    published_at timestamptz NOT NULL,
    object_key text NOT NULL,
    lesson jsonb NOT NULL,
    PRIMARY KEY (package_id, package_version),
    CONSTRAINT content_package_digest_profile
        CHECK (package_digest ~ '^[a-f0-9]{64}$'),
    CONSTRAINT content_publication_state
        CHECK (publication_state = 'published'),
    CONSTRAINT content_object_key_private_profile
        CHECK (object_key ~ '^[a-f0-9]{2}/[a-f0-9]{64}$')
);

CREATE UNIQUE INDEX content_lesson_package_digest_identity
    ON content.lesson_package_versions (
        package_id,
        package_version,
        package_digest
    );

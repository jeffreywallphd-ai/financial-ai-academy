CREATE TABLE curriculum.lesson_opportunity_classifications (
    opportunity_id text PRIMARY KEY,
    placement_id text NOT NULL,
    summary text NOT NULL,
    topics text[] NOT NULL,
    level text NOT NULL,
    estimated_minutes integer NOT NULL,
    prerequisite_summary text NOT NULL,
    availability text NOT NULL,
    availability_reason text NOT NULL,
    created_at timestamptz NOT NULL,
    CONSTRAINT curriculum_discovery_classification_opportunity_id
        CHECK (opportunity_id ~ '^[a-z0-9][a-z0-9._-]{2,63}$'),
    CONSTRAINT curriculum_discovery_classification_placement_id
        CHECK (placement_id ~ '^[a-z0-9][a-z0-9._-]{2,63}$'),
    CONSTRAINT curriculum_discovery_classification_summary
        CHECK (char_length(summary) BETWEEN 20 AND 500),
    CONSTRAINT curriculum_discovery_classification_topics
        CHECK (cardinality(topics) BETWEEN 1 AND 8),
    CONSTRAINT curriculum_discovery_classification_level
        CHECK (level IN ('introductory', 'intermediate', 'advanced')),
    CONSTRAINT curriculum_discovery_classification_duration
        CHECK (estimated_minutes BETWEEN 1 AND 1440),
    CONSTRAINT curriculum_discovery_classification_prerequisite
        CHECK (char_length(prerequisite_summary) BETWEEN 2 AND 500),
    CONSTRAINT curriculum_discovery_classification_availability
        CHECK (availability IN ('available', 'unavailable', 'planned')),
    CONSTRAINT curriculum_discovery_classification_availability_reason
        CHECK (char_length(availability_reason) BETWEEN 10 AND 500)
);

CREATE TABLE curriculum.discovery_projection_state (
    singleton boolean PRIMARY KEY DEFAULT true,
    generation char(64) NOT NULL UNIQUE,
    projected_at timestamptz NOT NULL,
    record_count integer NOT NULL,
    CONSTRAINT curriculum_discovery_projection_singleton
        CHECK (singleton),
    CONSTRAINT curriculum_discovery_projection_generation
        CHECK (generation ~ '^[a-f0-9]{64}$'),
    CONSTRAINT curriculum_discovery_projection_record_count
        CHECK (record_count BETWEEN 0 AND 500)
);

CREATE TABLE curriculum.discovery_projection_records (
    generation char(64) NOT NULL REFERENCES
        curriculum.discovery_projection_state (generation)
        ON UPDATE CASCADE ON DELETE CASCADE,
    ordinal integer NOT NULL,
    schema_version text NOT NULL,
    opportunity_id text NOT NULL UNIQUE,
    placement_id text NOT NULL,
    destination text NOT NULL,
    kind text NOT NULL,
    title text NOT NULL,
    summary text NOT NULL,
    objectives text[] NOT NULL,
    topics text[] NOT NULL,
    level text NOT NULL,
    estimated_minutes integer NOT NULL,
    prerequisite_summary text NOT NULL,
    availability text NOT NULL,
    availability_reason text NOT NULL,
    package_id text NOT NULL,
    package_version text NOT NULL,
    package_digest char(64) NOT NULL,
    published_by text NOT NULL,
    published_at timestamptz NOT NULL,
    content_reviewed_on date NOT NULL,
    educational_use_notice text NOT NULL,
    source_fingerprint char(64) NOT NULL,
    PRIMARY KEY (generation, ordinal),
    CONSTRAINT curriculum_discovery_record_ordinal
        CHECK (ordinal BETWEEN 0 AND 499),
    CONSTRAINT curriculum_discovery_record_schema
        CHECK (schema_version = '1.0.0'),
    CONSTRAINT curriculum_discovery_record_opportunity_id
        CHECK (opportunity_id ~ '^[a-z0-9][a-z0-9._-]{2,63}$'),
    CONSTRAINT curriculum_discovery_record_placement_id
        CHECK (placement_id ~ '^[a-z0-9][a-z0-9._-]{2,63}$'),
    CONSTRAINT curriculum_discovery_record_destination
        CHECK (destination = '/learn/placements/' || placement_id),
    CONSTRAINT curriculum_discovery_record_kind
        CHECK (kind = 'lesson'),
    CONSTRAINT curriculum_discovery_record_title
        CHECK (char_length(title) BETWEEN 1 AND 240),
    CONSTRAINT curriculum_discovery_record_summary
        CHECK (char_length(summary) BETWEEN 20 AND 500),
    CONSTRAINT curriculum_discovery_record_objectives
        CHECK (cardinality(objectives) BETWEEN 1 AND 20),
    CONSTRAINT curriculum_discovery_record_topics
        CHECK (cardinality(topics) BETWEEN 1 AND 8),
    CONSTRAINT curriculum_discovery_record_level
        CHECK (level IN ('introductory', 'intermediate', 'advanced')),
    CONSTRAINT curriculum_discovery_record_duration
        CHECK (estimated_minutes BETWEEN 1 AND 1440),
    CONSTRAINT curriculum_discovery_record_prerequisite
        CHECK (char_length(prerequisite_summary) BETWEEN 2 AND 500),
    CONSTRAINT curriculum_discovery_record_availability
        CHECK (availability IN ('available', 'unavailable', 'planned')),
    CONSTRAINT curriculum_discovery_record_availability_reason
        CHECK (char_length(availability_reason) BETWEEN 10 AND 500),
    CONSTRAINT curriculum_discovery_record_package_id
        CHECK (package_id ~ '^[a-z0-9][a-z0-9._-]{2,63}$'),
    CONSTRAINT curriculum_discovery_record_package_version
        CHECK (
            package_version ~
            '^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(-[0-9A-Za-z.-]+)?$'
        ),
    CONSTRAINT curriculum_discovery_record_package_digest
        CHECK (package_digest ~ '^[a-f0-9]{64}$'),
    CONSTRAINT curriculum_discovery_record_source_fingerprint
        CHECK (source_fingerprint ~ '^[a-f0-9]{64}$')
);

COMMENT ON TABLE curriculum.lesson_opportunity_classifications IS
    'Curriculum-owned catalog classification for exact lesson placements.';
COMMENT ON TABLE curriculum.discovery_projection_state IS
    'Singleton pointer to one complete rebuildable discovery generation.';
COMMENT ON TABLE curriculum.discovery_projection_records IS
    'Ordered rebuildable discovery records; Content and Curriculum remain authoritative.';

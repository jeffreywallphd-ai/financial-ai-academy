CREATE SCHEMA IF NOT EXISTS identity;

CREATE TABLE identity.installations (
    singleton_key boolean PRIMARY KEY DEFAULT true,
    installation_id uuid NOT NULL UNIQUE,
    mode text NOT NULL,
    limitation_acknowledged boolean NOT NULL,
    created_at timestamptz NOT NULL,
    CONSTRAINT identity_singleton_key CHECK (singleton_key = true),
    CONSTRAINT identity_mode_profile
        CHECK (mode IN ('single_profile', 'built_in', 'oidc'))
);

CREATE TABLE identity.bindings (
    binding_id uuid PRIMARY KEY,
    installation_id uuid NOT NULL
        REFERENCES identity.installations (installation_id),
    actor_id uuid NOT NULL UNIQUE,
    learner_id uuid NOT NULL UNIQUE,
    provider_mode text NOT NULL,
    provider_subject text NOT NULL,
    status text NOT NULL,
    created_at timestamptz NOT NULL,
    CONSTRAINT identity_binding_mode
        CHECK (provider_mode IN ('single_profile', 'built_in', 'oidc')),
    CONSTRAINT identity_binding_status
        CHECK (status IN ('active', 'disabled')),
    UNIQUE (installation_id, provider_mode, provider_subject)
);

CREATE TABLE identity.sessions (
    session_id uuid PRIMARY KEY,
    binding_id uuid NOT NULL
        REFERENCES identity.bindings (binding_id),
    token_hash char(64) NOT NULL UNIQUE,
    authenticated_at timestamptz NOT NULL,
    last_seen_at timestamptz NOT NULL,
    absolute_expires_at timestamptz NOT NULL,
    revoked_at timestamptz NULL,
    CONSTRAINT identity_session_token_hash
        CHECK (token_hash ~ '^[a-f0-9]{64}$'),
    CONSTRAINT identity_session_time_order
        CHECK (
            authenticated_at <= last_seen_at
            AND authenticated_at < absolute_expires_at
        )
);

CREATE INDEX identity_active_session_resolution
    ON identity.sessions (token_hash, absolute_expires_at, last_seen_at)
    WHERE revoked_at IS NULL;

from __future__ import annotations

import pytest

from financial_ai_academy.platform.security.single_profile_policy import (
    RequestPolicyViolation,
    SingleProfileRequestPolicy,
    SingleProfileSecuritySettings,
)


def settings(**updates: object) -> SingleProfileSecuritySettings:
    values: dict[str, object] = {
        "identity_mode": "single_profile",
        "bind_host": "127.0.0.1",
        "public_origin": "http://127.0.0.1:8000",
        "allowed_hosts": ("127.0.0.1:8000", "testserver"),
        "secure_cookie": False,
    }
    values.update(updates)
    return SingleProfileSecuritySettings(**values)


@pytest.mark.parametrize(
    "updates",
    [
        {"identity_mode": "oidc"},
        {"bind_host": "0.0.0.0"},
        {"bind_host": "192.168.1.20"},
        {"public_origin": "http://example.com"},
        {"public_origin": "http://127.0.0.1:8000/path"},
        {"secure_cookie": True},
        {"allowed_hosts": ()},
    ],
)
def test_unsafe_single_profile_configuration_is_rejected(
    updates: dict[str, object],
) -> None:
    with pytest.raises(RequestPolicyViolation):
        SingleProfileRequestPolicy(settings(**updates))


def test_bootstrap_requires_exact_host_origin_and_same_origin_fetch() -> None:
    policy = SingleProfileRequestPolicy(settings())
    policy.verify(
        {
            "host": "127.0.0.1:8000",
            "origin": "http://127.0.0.1:8000",
            "sec-fetch-site": "same-origin",
        },
        state_changing=True,
    )

    for headers in (
        {"host": "attacker.example", "origin": "http://127.0.0.1:8000"},
        {"host": "127.0.0.1:8000", "origin": "https://attacker.example"},
        {
            "host": "127.0.0.1:8000",
            "origin": "http://127.0.0.1:8000",
            "sec-fetch-site": "cross-site",
        },
    ):
        with pytest.raises(RequestPolicyViolation):
            policy.verify(headers, state_changing=True)


@pytest.mark.parametrize(
    "header",
    ["x-actor-id", "x-learner-id", "x-session-id", "x-identity-provider"],
)
def test_client_selected_identity_headers_are_rejected(header: str) -> None:
    policy = SingleProfileRequestPolicy(settings())

    with pytest.raises(RequestPolicyViolation):
        policy.verify(
            {"host": "testserver", header: "client-selected"},
            state_changing=False,
        )

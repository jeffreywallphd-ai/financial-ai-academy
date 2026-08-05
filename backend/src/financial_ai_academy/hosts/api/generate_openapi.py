"""Generate or verify the reviewed OpenAPI snapshot."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from financial_ai_academy.modules.identity.public import (
    IdentityError,
    IdentityErrorCode,
    LearnerContext,
)
from financial_ai_academy.platform.security.single_profile_policy import (
    SingleProfileRequestPolicy,
    SingleProfileSecuritySettings,
)

from .app import ApiServices, create_app


class _SchemaIdentity:
    def bootstrap_single_profile(self, request: object) -> object:
        raise NotImplementedError

    def resolve_session(self, cookie_value: str | None) -> LearnerContext:
        raise IdentityError(
            IdentityErrorCode.UNAUTHORIZED,
            "A valid learner session is required.",
        )

    def revoke_session(self, cookie_value: str | None) -> None:
        raise NotImplementedError

    def health(self) -> bool:
        return True


class _SchemaCurriculum:
    def create_lesson_placement(self, request: object) -> object:
        raise NotImplementedError

    def open_placed_lesson(self, request: object) -> object:
        raise NotImplementedError


def repository_root() -> Path:
    return Path(__file__).resolve().parents[5]


def snapshot_path() -> Path:
    return repository_root() / "contracts/api/openapi.json"


def generate_bytes() -> bytes:
    policy = SingleProfileRequestPolicy(
        SingleProfileSecuritySettings(
            identity_mode="single_profile",
            bind_host="127.0.0.1",
            public_origin="http://127.0.0.1:8000",
            allowed_hosts=("127.0.0.1:8000", "testserver"),
            secure_cookie=False,
        )
    )
    app = create_app(
        ApiServices(
            identity=_SchemaIdentity(),  # type: ignore[arg-type]
            curriculum=_SchemaCurriculum(),  # type: ignore[arg-type]
            request_policy=policy,
        )
    )
    return (
        json.dumps(
            app.openapi(),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + chr(10)
    ).encode("utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args(argv)
    expected = generate_bytes()
    target = snapshot_path()
    if arguments.check:
        if not target.is_file() or target.read_bytes() != expected:
            print(
                "OpenAPI snapshot is stale; run "
                "python -m financial_ai_academy.hosts.api.generate_openapi"
            )
            return 1
        print("OpenAPI snapshot is current.")
        return 0
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(expected)
    print(f"Wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

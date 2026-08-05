"""Check the approved-lesson slice's deterministic security controls."""

from __future__ import annotations

import json
import sys
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[2]


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def main() -> int:
    failures: list[str] = []
    api = (
        REPOSITORY
        / "backend/src/financial_ai_academy/hosts/api/app.py"
    ).read_text(encoding="utf-8")
    policy = (
        REPOSITORY
        / "backend/src/financial_ai_academy/platform/security/"
        "single_profile_policy.py"
    ).read_text(encoding="utf-8")
    local_server = (
        REPOSITORY / "deployments/local/serve.py"
    ).read_text(encoding="utf-8")
    lesson_body = (
        REPOSITORY
        / "contracts/compatibility/lesson-package/v1/approved/"
        "intro-risk-return/lesson.md"
    ).read_text(encoding="utf-8")
    manifest = json.loads(
        (
            REPOSITORY
            / "contracts/compatibility/lesson-package/v1/approved/"
            "intro-risk-return/manifest.json"
        ).read_text(encoding="utf-8")
    )
    denials = json.loads(
        (
            REPOSITORY
            / "contracts/compatibility/lesson-package/v1/cases/denials.json"
        ).read_text(encoding="utf-8")
    )
    e2e = (
        REPOSITORY
        / "apps/web/tests/browser/approved-lesson/"
        "approved-lesson.e2e.ts"
    ).read_text(encoding="utf-8")
    web_source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (REPOSITORY / "apps/web/src").rglob("*")
        if path.suffix in {".ts", ".tsx"}
    )

    require(
        "must bind to a loopback host" in policy
        and "_CLIENT_IDENTITY_HEADERS" in policy,
        "Single-profile loopback and client-identity denial are missing.",
        failures,
    )
    require(
        'httponly=True' in api
        and 'samesite="strict"' in api
        and 'Cache-Control"] = "no-store"' in api,
        "Opaque-cookie or no-store response controls are missing.",
        failures,
    )
    require(
        "Content-Security-Policy" in local_server
        and "frame-ancestors 'none'" in local_server
        and "X-Content-Type-Options" in local_server,
        "Static application security headers are incomplete.",
        failures,
    )
    require(
        'LOOPBACK_HOSTS = frozenset({"127.0.0.1"' in local_server
        and "0.0.0.0" not in local_server,
        "Local qualification is not restricted to loopback.",
        failures,
    )
    denial_ids = {case["id"] for case in denials}
    require(
        {
            "unsafe-traversal",
            "raw-html",
            "unsafe-link",
            "undeclared-image",
            "integrity-mismatch",
            "individual-size-limit",
        }.issubset(denial_ids),
        "The malicious-package corpus is incomplete.",
        failures,
    )
    require(
        all(source["locator"].startswith("https://") for source in manifest["sources"]),
        "Approved educational source locators must use HTTPS.",
        failures,
    )
    require(
        "does not recommend buying, selling, or holding" in lesson_body,
        "The approved fixture lacks the education/advice boundary.",
        failures,
    )
    require(
        not any(
            token in web_source.casefold()
            for token in (
                "dangerouslysetinnerhtml",
                "document.write",
                "<iframe",
            )
        ),
        "The browser source contains an unsafe rendering sink.",
        failures,
    )
    require(
        "content-security-policy" in e2e.casefold()
        and "httpOnly" in e2e
        and "actor_id|learner_id|session_id" in e2e,
        "Live browser security assertions are incomplete.",
        failures,
    )
    require(
        "PRIVATE-SENTINEL" in (
            REPOSITORY
            / "backend/tests/integration/api/"
            "test_single_profile_lesson_api.py"
        ).read_text(encoding="utf-8"),
        "Sentinel redaction evidence is missing.",
        failures,
    )

    if failures:
        for failure in failures:
            print(f"ERROR: {failure}", file=sys.stderr)
        return 1
    print("Approved-lesson security checks passed: 10 control groups.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

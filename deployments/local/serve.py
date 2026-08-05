"""Loopback-only Python composition for local approved-lesson qualification."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Awaitable, Callable
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse


REPOSITORY = Path(__file__).resolve().parents[2]
BACKEND_SOURCE = REPOSITORY / "backend" / "src"
if str(BACKEND_SOURCE) not in sys.path:
    sys.path.insert(0, str(BACKEND_SOURCE))

from financial_ai_academy.bootstrap.composition import (  # noqa: E402
    build_application_services,
)
from financial_ai_academy.bootstrap.settings import (  # noqa: E402
    SingleProfileApplicationSettings,
)
from financial_ai_academy.hosts.api.app import (  # noqa: E402
    ApiServices,
    create_app,
)
from financial_ai_academy.modules.content.public import (  # noqa: E402
    AdmitLessonPackageRequest,
)
from financial_ai_academy.modules.curriculum.public import (  # noqa: E402
    CreateLessonPlacementRequest,
)
from financial_ai_academy.platform.security.single_profile_policy import (  # noqa: E402
    SingleProfileSecuritySettings,
)


LOOPBACK_HOSTS = frozenset({"127.0.0.1", "::1", "localhost"})
PLACEMENT_ID = "intro-risk-return-primary"
APPROVED_FIXTURE = (
    REPOSITORY
    / "contracts"
    / "compatibility"
    / "lesson-package"
    / "v1"
    / "approved"
    / "intro-risk-return"
)


def build_local_app(
    *,
    postgres_dsn: str,
    data_root: Path,
    web_dist: Path,
    host: str,
    port: int,
    seed_approved_fixture: bool,
    serve_static: bool = True,
    public_origin: str | None = None,
    allowed_hosts: tuple[str, ...] | None = None,
) -> FastAPI:
    """Compose the reviewed loopback API with optional static SPA serving."""
    if host not in LOOPBACK_HOSTS:
        raise ValueError("The community single-profile host must be loopback.")
    if not 1 <= port <= 65_535:
        raise ValueError("The application port is outside the valid range.")
    index_file = web_dist / "index.html"
    asset_directory = web_dist / "assets"
    if serve_static and (
        not index_file.is_file() or not asset_directory.is_dir()
    ):
        raise ValueError(
            "Static web artifacts are unavailable; run the reviewed web build."
        )
    data_root.mkdir(parents=True, exist_ok=True)

    origin_host = "127.0.0.1" if host in {"localhost", "::1"} else host
    configured_public_origin = (
        public_origin or f"http://{origin_host}:{port}"
    )
    configured_allowed_hosts = allowed_hosts or (f"{origin_host}:{port}",)
    settings = SingleProfileApplicationSettings(
        postgres_dsn=postgres_dsn,
        object_storage_root=data_root / "objects",
        lesson_schema_dir=(
            REPOSITORY / "contracts" / "learning" / "lesson-package" / "v1"
        ),
        migrations_dir=REPOSITORY / "backend" / "migrations",
        security=SingleProfileSecuritySettings(
            identity_mode="single_profile",
            bind_host=host,
            public_origin=configured_public_origin,
            allowed_hosts=configured_allowed_hosts,
            secure_cookie=False,
        ),
    )
    services = build_application_services(settings, apply_migrations=True)
    if seed_approved_fixture:
        accepted = services.content.admit_lesson_package(
            AdmitLessonPackageRequest(APPROVED_FIXTURE)
        )
        services.curriculum.create_lesson_placement(
            CreateLessonPlacementRequest(
                placement_id=PLACEMENT_ID,
                package_id=accepted.package_id,
                package_version=accepted.package_version,
                package_digest=accepted.package_digest,
            )
        )

    app = create_app(
        ApiServices(
            identity=services.identity,
            curriculum=services.curriculum,
            request_policy=services.request_policy,
        )
    )

    @app.middleware("http")
    async def add_browser_security_headers(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; base-uri 'none'; frame-ancestors 'none'; "
            "form-action 'self'; img-src 'self'; object-src 'none'; "
            "script-src 'self'; style-src 'self'; connect-src 'self'"
        )
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        return response

    if serve_static:
        from fastapi.staticfiles import StaticFiles

        app.mount(
            "/assets",
            StaticFiles(directory=asset_directory, check_dir=True),
            name="static-assets",
        )

        @app.get("/", include_in_schema=False)
        @app.get("/{browser_path:path}", include_in_schema=False)
        def browser_application(browser_path: str = "") -> FileResponse:
            if browser_path == "api" or browser_path.startswith("api/"):
                raise HTTPException(status_code=404)
            return FileResponse(index_file)

    return app


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Serve the loopback-only local qualification profile."
    )
    parser.add_argument("--postgres-dsn", required=True)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument(
        "--web-dist",
        type=Path,
        default=REPOSITORY / "apps" / "web" / "dist",
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--seed-approved-fixture", action="store_true")
    parser.add_argument(
        "--api-only",
        action="store_true",
        help="Serve only the API so a loopback Vite development proxy can serve the SPA.",
    )
    parser.add_argument(
        "--public-origin",
        help="Exact loopback browser origin used for state-changing request checks.",
    )
    parser.add_argument(
        "--allowed-host",
        action="append",
        dest="allowed_hosts",
        help="Allowed Host header; repeat when both proxy and direct readiness access are needed.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    app = build_local_app(
        postgres_dsn=args.postgres_dsn,
        data_root=args.data_root.resolve(),
        web_dist=args.web_dist.resolve(),
        host=args.host,
        port=args.port,
        seed_approved_fixture=args.seed_approved_fixture,
        serve_static=not args.api_only,
        public_origin=args.public_origin,
        allowed_hosts=(
            tuple(args.allowed_hosts) if args.allowed_hosts else None
        ),
    )

    import uvicorn

    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        access_log=False,
        server_header=False,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

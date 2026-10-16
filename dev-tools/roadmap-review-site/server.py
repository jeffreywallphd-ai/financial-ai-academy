"""Read-only loopback host for the dynamic capability roadmap review."""

from __future__ import annotations

import argparse
import ipaddress
import json
import shutil
import subprocess
import sys
from collections.abc import Callable
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


SITE_DIR = Path(__file__).resolve().parent
REPOSITORY_ROOT = SITE_DIR.parents[1]
CONTROL_PLANE = REPOSITORY_ROOT / "dev-tools" / "control-plane"
DEFAULT_OUTPUT = REPOSITORY_ROOT / ".local-codex" / "roadmap-review-site"
if str(CONTROL_PLANE) not in sys.path:
    sys.path.insert(0, str(CONTROL_PLANE))

from financial_academy_roadmap_review import result as roadmap_result  # noqa: E402


ProjectionFactory = Callable[[Path], dict[str, Any]]


def validate_loopback(host: str) -> str:
    """Return a normalized loopback address or reject remote exposure."""

    try:
        address = ipaddress.ip_address(host)
    except ValueError as error:
        raise ValueError("The roadmap review host must be a numeric loopback address.") from error
    if not address.is_loopback:
        raise ValueError("The roadmap review host may bind only to a loopback address.")
    return str(address)


def compile_client(root: Path = REPOSITORY_ROOT, output_dir: Path = DEFAULT_OUTPUT) -> tuple[Path, Path]:
    """Compile typed browser sources into ignored local output."""

    node = shutil.which("node")
    compiler = root / "apps" / "web" / "node_modules" / "typescript" / "bin" / "tsc"
    config = root / "dev-tools" / "roadmap-review-site" / "tsconfig.json"
    if node is None or not compiler.is_file():
        raise RuntimeError(
            "The pinned web TypeScript compiler is unavailable. Run the repository setup, then retry."
        )
    output_dir.mkdir(parents=True, exist_ok=True)
    completed = subprocess.run(
        [node, str(compiler), "-p", str(config), "--outDir", str(output_dir)],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode:
        detail = (completed.stdout + completed.stderr).strip()
        raise RuntimeError(f"Roadmap review client compilation failed.\n{detail}")
    app = output_dir / "app.js"
    model = output_dir / "model.js"
    if not app.is_file() or not model.is_file():
        raise RuntimeError("Roadmap review client compilation did not produce the expected files.")
    return app, model


class RoadmapReviewServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(
        self,
        address: tuple[str, int],
        *,
        repository_root: Path,
        output_dir: Path,
        projection_factory: ProjectionFactory,
    ) -> None:
        self.repository_root = repository_root.resolve()
        self.site_dir = (self.repository_root / "dev-tools" / "roadmap-review-site").resolve()
        self.output_dir = output_dir.resolve()
        self.projection_factory = projection_factory
        super().__init__(address, RoadmapRequestHandler)


class RoadmapRequestHandler(BaseHTTPRequestHandler):
    server: RoadmapReviewServer

    def _headers(self, status: HTTPStatus, content_type: str, length: int, *, no_store: bool = False) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(length))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy", "default-src 'self'; connect-src 'self'; img-src 'self'; style-src 'self'; script-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'")
        if no_store:
            self.send_header("Cache-Control", "no-store")
        self.end_headers()

    def _send_bytes(
        self,
        status: HTTPStatus,
        body: bytes,
        content_type: str,
        *,
        no_store: bool = False,
        include_body: bool = True,
    ) -> None:
        self._headers(status, content_type, len(body), no_store=no_store)
        if include_body:
            self.wfile.write(body)

    def _send_json(
        self,
        status: HTTPStatus,
        value: object,
        *,
        include_body: bool = True,
    ) -> None:
        body = json.dumps(value, ensure_ascii=False, sort_keys=True).encode("utf-8")
        self._send_bytes(
            status,
            body,
            "application/json; charset=utf-8",
            no_store=True,
            include_body=include_body,
        )

    def _static_route(self, path: str) -> tuple[Path, str] | None:
        routes = {
            "/": (self.server.site_dir / "index.html", "text/html; charset=utf-8"),
            "/index.html": (self.server.site_dir / "index.html", "text/html; charset=utf-8"),
            "/static/app.js": (self.server.output_dir / "app.js", "text/javascript; charset=utf-8"),
            "/static/model.js": (self.server.output_dir / "model.js", "text/javascript; charset=utf-8"),
            "/static/styles.css": (self.server.site_dir / "styles.css", "text/css; charset=utf-8"),
            "/assets/tokens.css": (
                self.server.repository_root / "apps" / "web" / "src" / "design-system" / "tokens.css",
                "text/css; charset=utf-8",
            ),
        }
        if path in routes:
            return routes[path]
        segments = path.strip("/").split("/")
        if len(segments) == 2 and segments[0] in {"capability", "cap", "slice", "work", "decision"}:
            value = segments[1]
            if value and all(character.isalnum() or character == "-" for character in value):
                return routes["/"]
        return None

    def _handle(self, *, include_body: bool) -> None:
        parsed = urlsplit(self.path)
        if parsed.query or parsed.fragment:
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "route.not-found"}, include_body=include_body)
            return
        if parsed.path == "/api/roadmap":
            try:
                payload = self.server.projection_factory(self.server.repository_root)
            except Exception:  # The browser receives a bounded failure, while details stay local.
                self.log_error("Roadmap projection failed")
                self._send_json(
                    HTTPStatus.INTERNAL_SERVER_ERROR,
                    {"error": "roadmap.projection-failed", "message": "The current planning sources could not be projected."},
                    include_body=include_body,
                )
                return
            self._send_json(HTTPStatus.OK, payload, include_body=include_body)
            return
        static = self._static_route(parsed.path)
        if static is None:
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "route.not-found"}, include_body=include_body)
            return
        path, content_type = static
        try:
            body = path.read_bytes()
        except OSError:
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "asset.not-found"}, include_body=include_body)
            return
        self._send_bytes(HTTPStatus.OK, body, content_type, include_body=include_body)

    def do_GET(self) -> None:  # noqa: N802
        self._handle(include_body=True)

    def do_HEAD(self) -> None:  # noqa: N802
        self._handle(include_body=False)

    def _deny_mutation(self) -> None:
        body = json.dumps({"error": "method.read-only"}).encode("utf-8")
        self.send_response(HTTPStatus.METHOD_NOT_ALLOWED)
        self.send_header("Allow", "GET, HEAD")
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    do_POST = _deny_mutation
    do_PUT = _deny_mutation
    do_PATCH = _deny_mutation
    do_DELETE = _deny_mutation


def make_server(
    *,
    host: str = "127.0.0.1",
    port: int = 8765,
    repository_root: Path = REPOSITORY_ROOT,
    output_dir: Path = DEFAULT_OUTPUT,
    projection_factory: ProjectionFactory = roadmap_result,
) -> RoadmapReviewServer:
    normalized_host = validate_loopback(host)
    return RoadmapReviewServer(
        (normalized_host, port),
        repository_root=repository_root,
        output_dir=output_dir,
        projection_factory=projection_factory,
    )


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("--host", default="127.0.0.1", help="Numeric loopback address only")
    value.add_argument("--port", type=int, default=8765)
    value.add_argument("--no-compile", action="store_true", help=argparse.SUPPRESS)
    return value


def main(argv: list[str] | None = None) -> int:
    arguments = parser().parse_args(argv)
    try:
        host = validate_loopback(arguments.host)
        if not arguments.no_compile:
            compile_client()
        server = make_server(host=host, port=arguments.port)
    except (OSError, RuntimeError, ValueError) as error:
        print(f"Unable to start roadmap review: {error}", file=sys.stderr)
        return 2
    address, port = server.server_address[:2]
    print(f"Capability roadmap review: http://{address}:{port}")
    print("Read-only and loopback-only. Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping roadmap review.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

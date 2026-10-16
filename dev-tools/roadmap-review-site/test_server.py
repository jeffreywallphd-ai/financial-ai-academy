"""Focused tests for the read-only roadmap review host."""

from __future__ import annotations

import http.client
import importlib.util
import json
import threading
import unittest
from pathlib import Path
from urllib.parse import quote


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("roadmap_review_site_server", HERE / "server.py")
assert SPEC and SPEC.loader
SERVER_MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SERVER_MODULE)


class RoadmapReviewServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        SERVER_MODULE.compile_client()
        cls.server = SERVER_MODULE.make_server(port=0)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.port = cls.server.server_address[1]

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)

    def request(self, method: str, path: str) -> tuple[int, dict[str, str], bytes]:
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=15)
        connection.request(method, path)
        response = connection.getresponse()
        body = response.read()
        headers = {key.lower(): value for key, value in response.getheaders()}
        connection.close()
        return response.status, headers, body

    def test_api_projects_exact_catalog_without_cache(self) -> None:
        status, headers, body = self.request("GET", "/api/roadmap")
        payload = json.loads(body)
        self.assertEqual(status, 200)
        self.assertEqual(headers["cache-control"], "no-store")
        self.assertEqual(payload["data"]["review"]["catalog_count"], 26)
        self.assertEqual(len(payload["data"]["review"]["candidates"]), 26)
        self.assertEqual(len(payload["data"]["review"]["decisions"]), 20)
        decisions = {item["id"]: item for item in payload["data"]["review"]["decisions"]}
        self.assertTrue(decisions["DEC-0013"]["decision_made"])
        self.assertFalse(decisions["DEC-0012"]["decision_made"])
        def keys(value: object) -> set[str]:
            if isinstance(value, dict):
                return {str(key).lower() for key in value} | set().union(*(keys(item) for item in value.values()))
            if isinstance(value, list):
                return set().union(*(keys(item) for item in value))
            return set()

        self.assertTrue({"approver", "reviewer", "reviewer_label", "approval_history"}.isdisjoint(keys(payload)))

    def test_head_and_allowlisted_assets(self) -> None:
        status, headers, body = self.request("HEAD", "/static/app.js")
        self.assertEqual(status, 200)
        self.assertEqual(body, b"")
        self.assertGreater(int(headers["content-length"]), 0)
        status, _, body = self.request("GET", "/assets/tokens.css")
        self.assertEqual(status, 200)
        self.assertIn(b"--faa-color-canvas", body)

    def test_stable_capability_route_serves_shell(self) -> None:
        for path in (
            "/capability/participate-in-structured-lessons",
            "/cap/CAP-0008",
            "/slice/SLI-0036",
            "/work/WRK-0026",
            "/decision/DEC-0013",
        ):
            status, _, body = self.request("GET", path)
            self.assertEqual(status, 200)
            self.assertIn(b'id="roadmap"', body)

    def test_mutations_are_denied(self) -> None:
        for method in ("POST", "PUT", "PATCH", "DELETE"):
            status, headers, body = self.request(method, "/api/roadmap")
            self.assertEqual(status, 405)
            self.assertEqual(headers["allow"], "GET, HEAD")
            self.assertIn(b"method.read-only", body)

    def test_unknown_query_and_traversal_are_not_served(self) -> None:
        for path in ("/api/roadmap?write=true", "/static/unknown.js", "/slice/SLI_0036", "/" + quote("../AGENTS.md")):
            status, _, body = self.request("GET", path)
            self.assertEqual(status, 404)
            self.assertNotIn(b"AI Development Entry Point", body)

    def test_remote_bind_is_refused(self) -> None:
        with self.assertRaisesRegex(ValueError, "loopback"):
            SERVER_MODULE.validate_loopback("0.0.0.0")
        with self.assertRaisesRegex(ValueError, "numeric loopback"):
            SERVER_MODULE.validate_loopback("localhost")

    def test_projection_failure_is_bounded(self) -> None:
        def fail(_: Path) -> dict[str, object]:
            raise RuntimeError("private detail")

        server = SERVER_MODULE.make_server(port=0, projection_factory=fail)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            connection = http.client.HTTPConnection("127.0.0.1", server.server_address[1], timeout=5)
            connection.request("GET", "/api/roadmap")
            response = connection.getresponse()
            body = response.read()
            connection.close()
            self.assertEqual(response.status, 500)
            self.assertNotIn(b"private detail", body)
            self.assertIn(b"roadmap.projection-failed", body)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

    def test_api_reprojects_fresh_sources_without_a_build_step(self) -> None:
        calls = 0

        def changing(_: Path) -> dict[str, object]:
            nonlocal calls
            calls += 1
            return {
                "outcome": "succeeded",
                "data": {"review": {"schema_version": "roadmap-review-v1", "source_fingerprint": f"sha256:{calls}"}},
            }

        server = SERVER_MODULE.make_server(port=0, projection_factory=changing)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            fingerprints: list[str] = []
            for _ in range(2):
                connection = http.client.HTTPConnection("127.0.0.1", server.server_address[1], timeout=5)
                connection.request("GET", "/api/roadmap")
                response = connection.getresponse()
                payload = json.loads(response.read())
                connection.close()
                self.assertEqual(response.status, 200)
                self.assertEqual(response.headers["Cache-Control"], "no-store")
                fingerprints.append(payload["data"]["review"]["source_fingerprint"])
            self.assertEqual(fingerprints, ["sha256:1", "sha256:2"])
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)


if __name__ == "__main__":
    unittest.main(verbosity=2)

"""Project-neutral ports for adapting the control-plane kernel.

Future repositories can reuse the kernel and store by implementing these small
interfaces for their own planning vocabulary, public projection, and candidate
source.  The Financial AI Academy adapter is intentionally outside this file.
"""

from __future__ import annotations

from typing import Any, Protocol


class ProjectionPort(Protocol):
    """A tracked public lifecycle projection participating in a transaction."""

    @property
    def relative_path(self) -> str: ...

    def content_sha256(self) -> str: ...

    def matches(self, updates: dict[str, Any]) -> bool: ...

    def apply(self, updates: dict[str, Any], expected_sha256: str) -> None: ...


class ProjectAdapter(Protocol):
    """Project-specific authority, planning, and projection behavior."""

    def require_delivery_authority(self, work_id: str) -> dict[str, Any]: ...

    def projection(self, work_id: str) -> ProjectionPort: ...

    def initial_work_state(self, work_id: str) -> dict[str, Any]: ...

    def claim_projection_updates(
        self, work_id: str, packet: dict[str, Any]
    ) -> dict[str, Any]: ...

    def submit_projection_updates(
        self, work_id: str, packet: dict[str, Any]
    ) -> dict[str, Any]: ...

    def release_projection_updates(
        self, work_id: str, packet: dict[str, Any]
    ) -> dict[str, Any]: ...


class CandidateAdapter(Protocol):
    """Project-specific candidate identity and scope validation."""

    def current_identity(self) -> dict[str, str]: ...

    def stable_identity(self, candidate: str) -> dict[str, str]: ...

    def is_strict_descendant(self, ancestor: str, descendant: str) -> bool: ...

    def submission(
        self,
        *,
        base_revision: str,
        candidate: str,
        allowed_paths: list[str],
        declared_inputs: list[str],
    ) -> dict[str, Any]: ...

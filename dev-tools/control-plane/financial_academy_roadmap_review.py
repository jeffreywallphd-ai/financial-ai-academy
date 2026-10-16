"""Financial AI Academy adapter for the dynamic roadmap review contract."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
PLANNING_TOOLS = HERE.parent / "planning"
if str(PLANNING_TOOLS) not in sys.path:
    sys.path.insert(0, str(PLANNING_TOOLS))

from planning_model import as_list, as_text, load_artifacts  # noqa: E402

from contracts import ControlError, success
from financial_academy_portfolio import (
    current_capability_authority,
    planning_nodes,
    project,
)
from portfolio_conflicts import analyze_compatibility
from portfolio_allocation import allocate
from portfolio_ordering import plan
from roadmap_review import build_projection


CATALOG_PATH = "docs/product/capability-catalog.json"
EXPECTED_PRODUCT_CAPABILITIES = 26


def _decision_title(text: str, fallback: str) -> str:
    prefix = "# Decision Request:"
    for line in text.splitlines():
        if line.startswith(prefix):
            title = line.removeprefix(prefix).strip()
            return title or fallback
    return fallback


def _repository_reference(root: Path, source: Path, value: str | None) -> str | None:
    if not value:
        return None
    path_value, marker, fragment = value.partition("#")
    root_candidate = (root / path_value).resolve()
    candidate = root_candidate if root_candidate.is_file() else (source.parent / path_value).resolve()
    try:
        confined = candidate.relative_to(root.resolve()).as_posix()
        return f"{confined}{marker}{fragment}"
    except ValueError:
        # The project-neutral projector will reject this unconfined path.
        return value


def _decision_nodes(root: Path, artifacts: list[Any]) -> list[dict[str, Any]]:
    decisions: list[dict[str, Any]] = []
    for artifact in artifacts:
        if artifact.kind != "decision-request":
            continue
        text = artifact.path.read_text(encoding="utf-8")
        decisions.append(
            {
                "id": artifact.identifier,
                "status": artifact.status,
                "title": _decision_title(text, artifact.path.stem),
                "source": artifact.relative_path,
                "dependencies": [
                    {"target": item, "type": "hard"}
                    for item in as_list(artifact.metadata.get("depends_on"))
                ],
                "decision_record": _repository_reference(
                    root,
                    artifact.path,
                    as_text(artifact.metadata.get("decision_record")),
                ),
            }
        )
    return decisions


def _load_catalog(root: Path) -> dict[str, Any]:
    path = root / CATALOG_PATH
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ControlError(
            "roadmap.catalog-unreadable",
            "The machine-readable product capability catalog is unavailable or invalid.",
            {"source": CATALOG_PATH},
            ["Correct docs/product/capability-catalog.json and rerun documentation validation."],
        ) from error
    if not isinstance(value, dict):
        raise ControlError(
            "roadmap.catalog-unreadable",
            "The machine-readable product capability catalog must be a JSON object.",
            {"source": CATALOG_PATH},
            ["Use the capability-catalog-v1 object contract."],
        )
    return value


def projection(root: Path) -> dict[str, Any]:
    graph = project(root)
    nodes = planning_nodes(root)
    artifacts = load_artifacts(root)
    authority_current = current_capability_authority(root)
    ordering = plan(
        graph,
        level="capability",
        authority_current=authority_current,
        explicit_priority=[],
        accepted_sequence=[],
    )
    compatibility = analyze_compatibility(graph, level="capability")
    allocation = allocate(
        graph,
        level="capability",
        authority_current=authority_current,
        explicit_priority=[],
        accepted_sequence=[],
    )
    documents = {
        artifact.identifier: {
            "source": artifact.relative_path,
            "text": artifact.path.read_text(encoding="utf-8"),
        }
        for artifact in artifacts
        if artifact.kind in {"capability", "vertical-slice", "work-packet", "decision-request"}
    }
    return build_projection(
        catalog=_load_catalog(root),
        planning_nodes=nodes,
        documents=documents,
        graph=graph,
        ordering=ordering,
        compatibility=compatibility,
        allocation=allocation,
        decisions=_decision_nodes(root, artifacts),
        expected_catalog_count=EXPECTED_PRODUCT_CAPABILITIES,
    )


def result(root: Path) -> dict[str, Any]:
    review = projection(root)
    return success(
        "roadmap.review-projected",
        f"Projected {review['catalog_count']} product capability candidate(s) for review.",
        data={"review": review},
    )

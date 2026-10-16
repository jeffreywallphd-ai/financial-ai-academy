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

from planning_model import load_artifacts  # noqa: E402

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
        for artifact in load_artifacts(root)
        if artifact.kind in {"capability", "vertical-slice", "work-packet"}
    }
    return build_projection(
        catalog=_load_catalog(root),
        planning_nodes=nodes,
        documents=documents,
        graph=graph,
        ordering=ordering,
        compatibility=compatibility,
        allocation=allocation,
        expected_catalog_count=EXPECTED_PRODUCT_CAPABILITIES,
    )


def result(root: Path) -> dict[str, Any]:
    review = projection(root)
    return success(
        "roadmap.review-projected",
        f"Projected {review['catalog_count']} product capability candidate(s) for review.",
        data={"review": review},
    )

"""Dependency-light conformance runner for curriculum graph v1."""

from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from jsonschema import Draft202012Validator, FormatChecker


SUPPORTED_VERSION = "1.0.0"
TIMESTAMP_PROFILE = re.compile(
    r"^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])"
    r"T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]"
    r"(?:\.[0-9]{1,6})?(?:Z|[+-](?:[01][0-9]|2[0-3]):[0-5][0-9])$"
)


@dataclass(frozen=True, slots=True)
class Diagnostic:
    code: str
    reference: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {
            "code": self.code,
            "reference": _safe_reference(self.reference),
            "message": self.message,
        }


class ConformanceFailure(ValueError):
    def __init__(self, code: str, reference: str, message: str) -> None:
        self.diagnostic = Diagnostic(code, reference, message)
        super().__init__(message)


def _safe_reference(value: object) -> str:
    return (
        str(value)
        .replace(chr(0), "")
        .replace("\r", " ")
        .replace("\n", " ")[:120]
    )


def reject(code: str, reference: str, message: str) -> None:
    raise ConformanceFailure(code, _safe_reference(reference), message)


def repository_root() -> Path:
    return Path(__file__).resolve().parents[4]


def default_schema_dir() -> Path:
    return repository_root() / "contracts/learning/curriculum/v1"


def default_corpus_dir() -> Path:
    return repository_root() / "contracts/compatibility/curriculum-graph/v1"


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        reject(
            "curriculum_graph.schema_invalid",
            path.name,
            "Curriculum graph must be an object.",
        )
    return value


def canonical_published_at(value: object) -> str:
    if not isinstance(value, str) or TIMESTAMP_PROFILE.fullmatch(value) is None:
        raise ValueError("published_at is outside the supported timestamp profile")
    parsed = datetime.fromisoformat(
        value.removesuffix("Z") + ("+00:00" if value.endswith("Z") else "")
    )
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("published_at must contain a numeric UTC offset")
    return (
        parsed.astimezone(timezone.utc)
        .isoformat()
        .removesuffix("+00:00")
        + "Z"
    )


def canonical_graph_bytes(graph: Mapping[str, Any]) -> bytes:
    meaning = deepcopy(
        {key: value for key, value in graph.items() if key != "graph_digest"}
    )
    meaning["published_at"] = canonical_published_at(meaning["published_at"])
    presentation = meaning.get("presentation_order")
    if isinstance(presentation, dict):
        meaning["presentation_order"] = {
            key: value for key, value in presentation.items() if value
        }
    return json.dumps(
        meaning,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def graph_digest(graph: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_graph_bytes(graph)).hexdigest()


def _has_cycle(nodes: set[str], edges: Sequence[tuple[str, str]]) -> bool:
    outgoing: dict[str, list[str]] = {node: [] for node in nodes}
    indegree = {node: 0 for node in nodes}
    for source, target in edges:
        outgoing[source].append(target)
        indegree[target] += 1
    ready = [node for node, count in indegree.items() if count == 0]
    visited = 0
    while ready:
        node = ready.pop()
        visited += 1
        for target in outgoing[node]:
            indegree[target] -= 1
            if indegree[target] == 0:
                ready.append(target)
    return visited != len(nodes)


class CurriculumGraphContractValidator:
    def __init__(self, schema_dir: Path | None = None) -> None:
        root = schema_dir or default_schema_dir()
        self.graph_schema = load_json(root / "graph.schema.json")
        Draft202012Validator.check_schema(self.graph_schema)
        self._graph = Draft202012Validator(
            self.graph_schema,
            format_checker=FormatChecker(),
        )

    @staticmethod
    def _version(graph: Mapping[str, Any]) -> None:
        if graph.get("schema_version") != SUPPORTED_VERSION:
            reject(
                "curriculum_graph.unsupported_version",
                "schema_version",
                "Curriculum graph version is unsupported.",
            )

    def _shape(self, graph: Mapping[str, Any]) -> None:
        error = next(iter(self._graph.iter_errors(graph)), None)
        if error is not None:
            location = ".".join(str(part) for part in error.absolute_path)
            reject(
                "curriculum_graph.schema_invalid",
                location or "curriculum-graph",
                "Curriculum graph is malformed.",
            )

    @staticmethod
    def _timestamp(graph: Mapping[str, Any]) -> None:
        try:
            canonical_published_at(graph["published_at"])
        except (KeyError, TypeError, ValueError):
            reject(
                "curriculum_graph.schema_invalid",
                "published_at",
                "Curriculum graph is malformed.",
            )

    @staticmethod
    def _identities(graph: Mapping[str, Any]) -> dict[str, set[str]]:
        groups = {
            "objective": {
                item["objective_id"] for item in graph["objectives"]
            },
            "competency": {
                item["competency_id"] for item in graph["competencies"]
            },
            "activity": {
                item["activity_id"] for item in graph["activities"]
            },
            "branch": {item["branch_id"] for item in graph["branches"]},
            "relationship": {
                item["relationship_id"] for item in graph["relationships"]
            },
        }
        all_values = [
            *(item["objective_id"] for item in graph["objectives"]),
            *(item["competency_id"] for item in graph["competencies"]),
            *(item["activity_id"] for item in graph["activities"]),
            *(item["branch_id"] for item in graph["branches"]),
            *(item["relationship_id"] for item in graph["relationships"]),
        ]
        if len(all_values) != len(set(all_values)):
            reject(
                "curriculum_graph.duplicate_identity",
                "records",
                "Curriculum graph identities must be unique.",
            )
        return groups

    @staticmethod
    def _branches(graph: Mapping[str, Any], activity_ids: set[str]) -> None:
        membership_kinds: dict[str, set[str]] = {}
        for branch in graph["branches"]:
            for activity_id in branch["activity_ids"]:
                if activity_id not in activity_ids:
                    reject(
                        "curriculum_graph.dangling_reference",
                        branch["branch_id"],
                        "Curriculum branch references an unknown activity.",
                    )
                prior_kinds = membership_kinds.setdefault(activity_id, set())
                if prior_kinds and any(
                    kind != branch["kind"] for kind in prior_kinds
                ):
                    reject(
                        "curriculum_graph.ambiguous_branch_membership",
                        activity_id,
                        "Curriculum activity has ambiguous required branch meaning.",
                    )
                prior_kinds.add(branch["kind"])

    @staticmethod
    def _activity_references(graph: Mapping[str, Any]) -> None:
        for activity in graph["activities"]:
            expected = (
                "lesson_placement"
                if activity["kind"] == "lesson"
                else "assessment_placement"
            )
            if activity["reference"]["reference_kind"] != expected:
                reject(
                    "curriculum_graph.reference_kind_mismatch",
                    activity["activity_id"],
                    "Curriculum activity reference kind does not match.",
                )

    @staticmethod
    def _relationships(
        graph: Mapping[str, Any], groups: Mapping[str, set[str]]
    ) -> None:
        endpoint_types = {
            "objective_competency": ("objective", "competency"),
            "activity_develops_competency": ("activity", "competency"),
            "activity_assesses_competency": ("activity", "competency"),
            "competency_prerequisite": ("competency", "competency"),
            "activity_prerequisite": ("activity", "activity"),
        }
        all_nodes = (
            groups["objective"]
            | groups["competency"]
            | groups["activity"]
            | groups["branch"]
        )
        activities = {
            item["activity_id"]: item for item in graph["activities"]
        }
        competency_edges: list[tuple[str, str]] = []
        activity_edges: list[tuple[str, str]] = []
        for relationship in graph["relationships"]:
            source = relationship["source_id"]
            target = relationship["target_id"]
            if source not in all_nodes or target not in all_nodes:
                reject(
                    "curriculum_graph.dangling_reference",
                    relationship["relationship_id"],
                    "Curriculum relationship references an unknown node.",
                )
            source_type, target_type = endpoint_types[relationship["kind"]]
            if source not in groups[source_type] or target not in groups[target_type]:
                reject(
                    "curriculum_graph.invalid_relationship",
                    relationship["relationship_id"],
                    "Curriculum relationship endpoint type is invalid.",
                )
            if (
                relationship["kind"] == "activity_assesses_competency"
                and activities[source]["kind"] != "assessment"
            ):
                reject(
                    "curriculum_graph.invalid_relationship",
                    relationship["relationship_id"],
                    "Only an assessment activity may assess a competency.",
                )
            if relationship["kind"] == "competency_prerequisite":
                competency_edges.append((source, target))
            if relationship["kind"] == "activity_prerequisite":
                activity_edges.append((source, target))
        if _has_cycle(groups["competency"], competency_edges) or _has_cycle(
            groups["activity"], activity_edges
        ):
            reject(
                "curriculum_graph.prerequisite_cycle",
                "relationships",
                "Curriculum prerequisite relationships must be acyclic.",
            )

    @staticmethod
    def _presentation(
        graph: Mapping[str, Any], groups: Mapping[str, set[str]]
    ) -> None:
        presentation = graph.get("presentation_order", {})
        mappings = {
            "objective_ids": groups["objective"],
            "competency_ids": groups["competency"],
            "activity_ids": groups["activity"],
            "branch_ids": groups["branch"],
        }
        for key, allowed in mappings.items():
            if any(item not in allowed for item in presentation.get(key, [])):
                reject(
                    "curriculum_graph.dangling_reference",
                    key,
                    "Curriculum presentation references an unknown record.",
                )

    def validate_graph(self, graph: Mapping[str, Any]) -> None:
        self._version(graph)
        self._shape(graph)
        self._timestamp(graph)
        groups = self._identities(graph)
        self._activity_references(graph)
        self._branches(graph, groups["activity"])
        self._relationships(graph, groups)
        self._presentation(graph, groups)
        if graph["graph_digest"] != graph_digest(graph):
            reject(
                "curriculum_graph.graph_digest_mismatch",
                "graph_digest",
                "Curriculum graph digest does not match.",
            )


def approved_graph(corpus: Path | None = None) -> dict[str, Any]:
    root = corpus or default_corpus_dir()
    return load_json(root / "approved/graph.json")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=default_corpus_dir())
    arguments = parser.parse_args(argv)
    try:
        graph = approved_graph(arguments.corpus)
        CurriculumGraphContractValidator().validate_graph(graph)
    except (ConformanceFailure, OSError, RuntimeError, ValueError) as error:
        diagnostic = (
            error.diagnostic
            if isinstance(error, ConformanceFailure)
            else Diagnostic(
                "curriculum_graph.internal_error",
                "curriculum-graph",
                "Curriculum graph conformance could not complete.",
            )
        )
        print(
            json.dumps(
                {"valid": False, "diagnostic": diagnostic.as_dict()},
                sort_keys=True,
            )
        )
        return 1
    print(
        json.dumps(
            {
                "valid": True,
                "curriculum_id": graph["curriculum_id"],
                "curriculum_version": graph["curriculum_version"],
                "graph_digest": graph["graph_digest"],
                "activity_count": len(graph["activities"]),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

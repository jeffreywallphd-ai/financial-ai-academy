from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from .runner import (
    ProjectConformanceFailure,
    ProjectContractValidator,
    brief_digest,
)


REPOSITORY = Path(__file__).resolve().parents[4]
CORPUS = REPOSITORY / "contracts/compatibility/project-workspace/v1"
APPROVED = CORPUS / "approved"


def load(name: str) -> dict[str, object]:
    return json.loads((APPROVED / name).read_text(encoding="utf-8"))


def mutate(document: dict[str, object], path: list[str], value: object) -> None:
    current: object = document
    for part in path[:-1]:
        current = current[part]  # type: ignore[index]
    current[path[-1]] = value  # type: ignore[index]


def test_approved_contract_family_conforms() -> None:
    ProjectContractValidator().validate_approved()


@pytest.mark.parametrize(
    "case",
    json.loads((CORPUS / "cases/denials.json").read_text(encoding="utf-8")),
    ids=lambda case: case["case"],
)
def test_denial_corpus_fixes_stable_failures(case: dict[str, object]) -> None:
    validator = ProjectContractValidator()
    name = str(case["kind"])
    document = copy.deepcopy(load(f"{name}.json"))
    mutate(document, case["path"], case["value"])  # type: ignore[arg-type]
    with pytest.raises(ProjectConformanceFailure) as captured:
        if name == "brief":
            validator.validate_brief(document)
        elif name.endswith("intent"):
            validator.validate_intent(document)
        else:
            validator.validate_shell(document)
    assert captured.value.code == case["code"]


@pytest.mark.parametrize("field", ["milestones", "source_references"])
def test_brief_identities_are_unique(field: str) -> None:
    document = copy.deepcopy(load("brief.json"))
    items = document["brief"][field]  # type: ignore[index]
    items.append(copy.deepcopy(items[0]))
    document["brief_digest"] = brief_digest(document)
    with pytest.raises(ProjectConformanceFailure) as captured:
        ProjectContractValidator().validate_brief(document)
    assert captured.value.code == "project.contract.invalid_brief"


@pytest.mark.parametrize(
    ("path", "value"),
    [
        (["brief", "brief_id"], "Uppercase"),
        (["brief", "title"], ""),
        (["brief", "title"], "A" * 121),
        (["brief", "purpose"], "unsafe <markup>"),
        (["brief", "milestones"], []),
        (
            ["brief", "milestones"],
            [
                {"milestone_id": f"step-{index}", "description": "Do it."}
                for index in range(21)
            ],
        ),
        (["brief", "source_references"], []),
    ],
)
def test_brief_resource_limits_fail_closed(
    path: list[str],
    value: object,
) -> None:
    document = copy.deepcopy(load("brief.json"))
    mutate(document, path, value)
    document["brief_digest"] = brief_digest(document)
    with pytest.raises(ProjectConformanceFailure) as captured:
        ProjectContractValidator().validate_brief(document)
    assert captured.value.code == "project.contract.schema_invalid"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("title", ""),
        ("title", "A" * 121),
        ("charter", ""),
        ("charter", "B" * 4001),
        ("charter", "unsafe & markup"),
    ],
)
def test_intent_text_limits_fail_closed(field: str, value: str) -> None:
    document = copy.deepcopy(load("independent-intent.json"))
    document[field] = value
    with pytest.raises(ProjectConformanceFailure) as captured:
        ProjectContractValidator().validate_intent(document)
    assert captured.value.code == "project.contract.schema_invalid"


def test_learning_origin_requires_exact_approved_brief() -> None:
    validator = ProjectContractValidator()
    intent = load("learning-intent.json")
    with pytest.raises(ProjectConformanceFailure) as missing:
        validator.validate_intent(intent)
    assert missing.value.code == "project.contract.learning_brief_required"

    stale = copy.deepcopy(intent)
    stale["origin"]["brief_title"] = "Another title"  # type: ignore[index]
    with pytest.raises(ProjectConformanceFailure) as mismatch:
        validator.validate_intent(stale, load("brief.json"))
    assert mismatch.value.code == "project.contract.stale_learning_reference"


def test_non_ascii_digest_uses_direct_utf8() -> None:
    document = copy.deepcopy(load("brief.json"))
    vector = json.loads(
        (CORPUS / "vectors/non-ascii-brief-digest.json").read_text(
            encoding="utf-8"
        )
    )
    document["brief"]["title"] = vector["title"]  # type: ignore[index]
    document["brief_digest"] = vector["brief_digest"]
    ProjectContractValidator().validate_brief(document)


@pytest.mark.parametrize(
    ("title", "purpose", "milestone_count", "source_count"),
    [
        ("A", "P", 1, 1),
        ("Plain words", "A useful purpose.", 3, 2),
        ("Café review", "Compare examples from 東京.", 5, 4),
        ("Boundary review", "Use every allowed entry.", 20, 20),
    ],
)
def test_valid_briefs_do_not_depend_on_fixture_wording_or_counts(
    title: str,
    purpose: str,
    milestone_count: int,
    source_count: int,
) -> None:
    document = copy.deepcopy(load("brief.json"))
    brief = document["brief"]  # type: ignore[assignment]
    brief["title"] = title
    brief["purpose"] = purpose
    brief["milestones"] = [
        {"milestone_id": f"step-{index}", "description": f"Do step {index}."}
        for index in range(1, milestone_count + 1)
    ]
    brief["source_references"] = [
        {
            "resource_id": f"source-{index}",
            "resource_version": "1.0.0",
            "resource_digest": f"{index % 16:x}" * 64,
            "title": f"Source {index}",
        }
        for index in range(1, source_count + 1)
    ]
    document["brief_digest"] = brief_digest(document)
    ProjectContractValidator().validate_brief(document)


@pytest.mark.parametrize("private_key", ["storage_key", "provider_payload", "execution", "score", "portfolio"])
def test_public_shapes_reject_private_or_out_of_boundary_fields(
    private_key: str,
) -> None:
    document = copy.deepcopy(load("independent-shell.json"))
    document[private_key] = "not public"
    with pytest.raises(ProjectConformanceFailure) as captured:
        ProjectContractValidator().validate_shell(document)
    assert captured.value.code in {
        "project.contract.schema_invalid",
        "project.contract.private_field",
    }


def test_source_reference_overflow_fails_closed() -> None:
    document = copy.deepcopy(load("brief.json"))
    brief = document["brief"]  # type: ignore[assignment]
    brief["source_references"] = [
        {
            "resource_id": f"source-{index}",
            "resource_version": "1.0.0",
            "resource_digest": f"{index % 16:x}" * 64,
            "title": f"Source {index}",
        }
        for index in range(21)
    ]
    document["brief_digest"] = brief_digest(document)
    with pytest.raises(ProjectConformanceFailure) as captured:
        ProjectContractValidator().validate_brief(document)
    assert captured.value.code == "project.contract.schema_invalid"


@pytest.mark.parametrize(
    ("brief_id", "accepted"),
    [
        ("a", True),
        ("a" * 128, True),
        ("", False),
        ("a" * 129, False),
    ],
)
def test_identifier_length_edges(brief_id: str, accepted: bool) -> None:
    document = copy.deepcopy(load("brief.json"))
    document["brief"]["brief_id"] = brief_id  # type: ignore[index]
    document["brief_digest"] = brief_digest(document)
    if accepted:
        ProjectContractValidator().validate_brief(document)
    else:
        with pytest.raises(ProjectConformanceFailure) as captured:
            ProjectContractValidator().validate_brief(document)
        assert captured.value.code == "project.contract.schema_invalid"

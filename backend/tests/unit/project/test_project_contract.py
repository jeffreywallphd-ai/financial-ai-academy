from __future__ import annotations

import copy
from dataclasses import FrozenInstanceError, asdict, replace
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path

import pytest

from financial_ai_academy.modules.project.adapters.project_contract import (
    ContractProjectAdapter,
)
from financial_ai_academy.modules.project.domain.project import (
    IndependentProjectOrigin,
    LearningProjectBrief,
    LearningProjectOrigin,
)
from financial_ai_academy.modules.project.ports.project_contract import (
    ProjectContractFailure,
)


REPOSITORY = Path(__file__).resolve().parents[4]
SCHEMAS = REPOSITORY / "contracts/learning/project/v1"
APPROVED = REPOSITORY / "contracts/compatibility/project-workspace/v1/approved"


def adapter() -> ContractProjectAdapter:
    return ContractProjectAdapter(SCHEMAS)


def load(name: str) -> dict[str, object]:
    return json.loads((APPROVED / name).read_text(encoding="utf-8"))


def encoded(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False).encode("utf-8")


def refreshed_brief_digest(brief: LearningProjectBrief) -> str:
    value = {
        "brief_id": brief.brief_id,
        "brief_version": brief.brief_version,
        "title": brief.title,
        "purpose": brief.purpose,
        "milestones": [asdict(item) for item in brief.milestones],
        "source_references": [asdict(item) for item in brief.source_references],
    }
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()


def test_parser_returns_immutable_brief_values() -> None:
    contract = adapter()
    document = load("brief.json")
    brief = contract.parse_brief(encoded(document))
    document["brief"]["title"] = "Changed later"  # type: ignore[index]
    assert brief.title == "Review a sample portfolio"
    assert len(brief.milestones) == 2
    with pytest.raises(FrozenInstanceError):
        brief.title = "Cannot change"  # type: ignore[misc]


def test_both_origin_variants_round_trip_to_reviewed_shapes() -> None:
    contract = adapter()
    brief = contract.parse_brief((APPROVED / "brief.json").read_bytes())
    independent = contract.parse_intent(
        (APPROVED / "independent-intent.json").read_bytes()
    )
    learning = contract.parse_intent(
        (APPROVED / "learning-intent.json").read_bytes(),
        approved_brief=brief,
    )
    assert isinstance(independent.origin, IndependentProjectOrigin)
    assert isinstance(learning.origin, LearningProjectOrigin)
    assert contract.intent_document(independent) == load("independent-intent.json")
    assert contract.intent_document(learning) == load("learning-intent.json")


@pytest.mark.parametrize("name", ["independent-shell.json", "learning-shell.json"])
def test_shell_round_trip_preserves_server_owned_values(name: str) -> None:
    contract = adapter()
    shell = contract.parse_shell((APPROVED / name).read_bytes())
    assert shell.learner_id == "learner-local"
    assert shell.lifecycle == "active"
    assert shell.revision == 1
    assert contract.shell_document(shell) == load(name)


def test_learning_intent_fails_closed_without_exact_brief() -> None:
    contract = adapter()
    value = (APPROVED / "learning-intent.json").read_bytes()
    with pytest.raises(ProjectContractFailure) as missing:
        contract.parse_intent(value)
    assert missing.value.code == "project.contract.learning_brief_required"

    brief_document = copy.deepcopy(load("brief.json"))
    brief_document["brief"]["title"] = "Changed source"  # type: ignore[index]
    brief_document["brief_digest"] = "f" * 64
    with pytest.raises(ProjectContractFailure) as invalid:
        contract.parse_brief(encoded(brief_document))
    assert invalid.value.code == "project.contract.brief_digest_mismatch"


@pytest.mark.parametrize(
    ("name", "field"),
    [
        ("independent-intent.json", "learner_id"),
        ("independent-intent.json", "project_id"),
        ("independent-intent.json", "revision"),
        ("independent-shell.json", "storage_key"),
        ("independent-shell.json", "provider_payload"),
        ("independent-shell.json", "execution"),
        ("independent-shell.json", "score"),
    ],
)
def test_parser_rejects_client_authority_and_private_fields(
    name: str,
    field: str,
) -> None:
    contract = adapter()
    document = load(name)
    document[field] = "not allowed"
    operation = contract.parse_intent if name.endswith("intent.json") else contract.parse_shell
    with pytest.raises(ProjectContractFailure) as captured:
        operation(encoded(document))
    assert captured.value.code == "project.contract.schema_invalid"
    assert "not allowed" not in str(captured.value)


@pytest.mark.parametrize(
    ("title", "charter", "key"),
    [
        ("A", "One clear purpose.", "key-a"),
        ("Café study", "Compare examples in 東京.", "key-b"),
        ("A" * 120, "B" * 4000, "key-at-limits"),
    ],
)
def test_independent_intent_accepts_valid_text_without_fixture_assumptions(
    title: str,
    charter: str,
    key: str,
) -> None:
    contract = adapter()
    document = load("independent-intent.json")
    document.update(title=title, charter=charter, idempotency_key=key)
    parsed = contract.parse_intent(encoded(document))
    assert parsed.title == title
    assert parsed.charter == charter


def test_contract_adapter_is_side_effect_free() -> None:
    contract = adapter()
    first = contract.parse_shell((APPROVED / "learning-shell.json").read_bytes())
    second = contract.parse_shell((APPROVED / "learning-shell.json").read_bytes())
    assert first == second
    assert contract.shell_document(first) == contract.shell_document(second)


@pytest.mark.parametrize("reference", ["created_at", "updated_at"])
def test_shell_projection_rejects_naive_time(reference: str) -> None:
    contract = adapter()
    shell = contract.parse_shell((APPROVED / "independent-shell.json").read_bytes())
    invalid = replace(shell, **{reference: datetime(2026, 1, 1, 12, 0)})
    with pytest.raises(ProjectContractFailure) as captured:
        contract.shell_document(invalid)
    assert captured.value.code == "project.contract.invalid_shell"
    assert captured.value.reference == reference


def test_shell_projection_normalizes_aware_offset_time() -> None:
    contract = adapter()
    shell = contract.parse_shell((APPROVED / "independent-shell.json").read_bytes())
    eastern = timezone(-timedelta(hours=5))
    projected = contract.shell_document(
        replace(
            shell,
            created_at=datetime(2026, 1, 1, 12, 0, tzinfo=eastern),
            updated_at=datetime(2026, 1, 1, 12, 1, tzinfo=eastern),
        )
    )
    assert projected["created_at"] == "2026-01-01T17:00:00Z"
    assert projected["updated_at"] == "2026-01-01T17:01:00Z"


def test_shell_projection_rejects_reverse_chronology() -> None:
    contract = adapter()
    shell = contract.parse_shell((APPROVED / "independent-shell.json").read_bytes())
    invalid = replace(
        shell,
        created_at=datetime(2026, 1, 1, 12, 1, tzinfo=timezone.utc),
        updated_at=datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc),
    )
    with pytest.raises(ProjectContractFailure) as captured:
        contract.shell_document(invalid)
    assert captured.value.code == "project.contract.invalid_shell"
    assert captured.value.reference == "updated_at"


@pytest.mark.parametrize("duplicate", ["milestone", "source"])
def test_brief_projection_rejects_duplicate_identities(duplicate: str) -> None:
    contract = adapter()
    brief = contract.parse_brief((APPROVED / "brief.json").read_bytes())
    if duplicate == "milestone":
        invalid = replace(
            brief,
            milestones=(brief.milestones[0], brief.milestones[0]),
        )
    else:
        invalid = replace(
            brief,
            source_references=(
                brief.source_references[0],
                brief.source_references[0],
            ),
        )
    invalid = replace(invalid, brief_digest=refreshed_brief_digest(invalid))
    with pytest.raises(ProjectContractFailure) as captured:
        contract.brief_document(invalid)
    assert captured.value.code == "project.contract.invalid_brief"


def test_brief_projection_rejects_stale_digest() -> None:
    contract = adapter()
    brief = contract.parse_brief((APPROVED / "brief.json").read_bytes())
    with pytest.raises(ProjectContractFailure) as captured:
        contract.brief_document(replace(brief, brief_digest="f" * 64))
    assert captured.value.code == "project.contract.brief_digest_mismatch"

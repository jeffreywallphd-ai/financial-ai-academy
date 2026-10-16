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
from financial_ai_academy.modules.project.domain.workspace import (
    AddArtifactMutation,
    ArtifactKind,
    EvidenceClassification,
    InspectionMode,
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


def refresh_export_digest(document: dict[str, object]) -> None:
    document["export_digest"] = hashlib.sha256(
        json.dumps(
            document["export"],
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()


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


def test_workspace_round_trip_returns_immutable_typed_values() -> None:
    contract = adapter()
    document = load("workspace.json")
    workspace = contract.parse_workspace(encoded(document))
    document["notes"][0]["title"] = "Changed later"  # type: ignore[index]

    assert workspace.notes[0].title == "Question to test"
    assert workspace.artifacts[0].artifact_kind is ArtifactKind.DATASET
    assert workspace.artifacts[0].inspection_mode is InspectionMode.PLAIN_TEXT
    assert (
        workspace.artifacts[2].result_classification
        is EvidenceClassification.SIMULATED
    )
    assert workspace.domain_links[0].owner_module == "portfolio"
    assert contract.workspace_document(workspace) == load("workspace.json")
    with pytest.raises(FrozenInstanceError):
        workspace.workspace_revision = 5  # type: ignore[misc]


def test_workspace_mutation_snapshot_and_export_round_trip() -> None:
    contract = adapter()
    mutation = contract.parse_workspace_mutation_intent(
        (APPROVED / "workspace-mutation-intent.json").read_bytes()
    )
    close = contract.parse_snapshot_close_intent(
        (APPROVED / "snapshot-close-intent.json").read_bytes()
    )
    snapshot = contract.parse_snapshot(
        (APPROVED / "snapshot.json").read_bytes()
    )
    exported = contract.parse_evidence_export(
        (APPROVED / "evidence-export.json").read_bytes()
    )

    assert isinstance(mutation.mutation, AddArtifactMutation)
    assert mutation.expected_workspace_revision == 4
    assert close.expected_project_revision == 1
    assert snapshot.snapshot.workspace_revision == 4
    assert exported.export.snapshot_id == snapshot.snapshot_id
    assert contract.workspace_mutation_intent_document(mutation) == load(
        "workspace-mutation-intent.json"
    )
    assert contract.snapshot_close_intent_document(close) == load(
        "snapshot-close-intent.json"
    )
    assert contract.snapshot_document(snapshot) == load("snapshot.json")
    assert contract.evidence_export_document(exported) == load(
        "evidence-export.json"
    )


def test_snapshot_and_export_digest_changes_fail_closed() -> None:
    contract = adapter()
    snapshot = load("snapshot.json")
    snapshot["snapshot"]["workspace_revision"] = 5  # type: ignore[index]
    with pytest.raises(ProjectContractFailure) as stale_snapshot:
        contract.parse_snapshot(encoded(snapshot))
    assert stale_snapshot.value.code == "project.contract.snapshot_digest_mismatch"

    exported = load("evidence-export.json")
    exported["export"]["artifact_files"][0]["byte_count"] = 2049  # type: ignore[index]
    with pytest.raises(ProjectContractFailure) as stale_export:
        contract.parse_evidence_export(encoded(exported))
    assert stale_export.value.code == "project.contract.export_digest_mismatch"


@pytest.mark.parametrize(
    ("path", "value", "code"),
    [
        (["artifacts", 0, "logical_path"], "../../secret", "project.contract.noncanonical_logical_path"),
        (["artifacts", 1, "inspection_mode"], "plain_text", "project.contract.unsafe_inspection_mode"),
        (["artifacts", 2, "result_classification"], "predicted", None),
    ],
)
def test_workspace_artifact_boundaries(
    path: list[str | int],
    value: object,
    code: str | None,
) -> None:
    contract = adapter()
    document = load("workspace.json")
    current: object = document
    for part in path[:-1]:
        current = current[part]  # type: ignore[index]
    current[path[-1]] = value  # type: ignore[index]
    if code is None:
        workspace = contract.parse_workspace(encoded(document))
        assert workspace.artifacts[2].result_classification is EvidenceClassification.PREDICTED
    else:
        with pytest.raises(ProjectContractFailure) as captured:
            contract.parse_workspace(encoded(document))
        assert captured.value.code == code


@pytest.mark.parametrize(
    "logical_path",
    [
        "./data.csv",
        "data/./sample.csv",
        "data/trailing.",
        "data/trailing ",
        "data//sample.csv",
        "data/CON.csv",
        "data/Cafe\u0301.csv",
    ],
)
def test_workspace_rejects_noncanonical_logical_path(logical_path: str) -> None:
    document = load("workspace.json")
    document["artifacts"][0]["logical_path"] = logical_path  # type: ignore[index]
    with pytest.raises(ProjectContractFailure) as captured:
        adapter().parse_workspace(encoded(document))
    assert captured.value.code == "project.contract.noncanonical_logical_path"


def test_workspace_accepts_normalized_unicode_logical_path() -> None:
    document = load("workspace.json")
    document["artifacts"][0]["logical_path"] = "données/échantillon.csv"  # type: ignore[index]
    parsed = adapter().parse_workspace(encoded(document))
    assert parsed.artifacts[0].logical_path == "données/échantillon.csv"


@pytest.mark.parametrize("target", ["reference", "provenance"])
def test_workspace_rejects_credential_bearing_urls(target: str) -> None:
    document = load("workspace.json")
    if target == "reference":
        document["references"][0]["url"] = "https://user:password@example.test/source"  # type: ignore[index]
    else:
        document["artifacts"][0]["provenance"]["source_url"] = "https://token:secret@example.test/data"  # type: ignore[index]
    with pytest.raises(ProjectContractFailure) as captured:
        adapter().parse_workspace(encoded(document))
    assert captured.value.code == "project.contract.unsafe_url"


def test_export_requires_exact_snapshot_artifact_coverage() -> None:
    document = load("evidence-export.json")
    document["export"]["excluded_artifacts"] = []  # type: ignore[index]
    refresh_export_digest(document)
    with pytest.raises(ProjectContractFailure) as captured:
        adapter().parse_evidence_export(encoded(document))
    assert captured.value.code == "project.contract.incomplete_export_coverage"


def test_export_binds_workspace_record_meaning_to_snapshot() -> None:
    document = load("evidence-export.json")
    document["export"]["workspace_record"]["artifacts"][0]["provenance"]["source_title"] = "Changed source"  # type: ignore[index]
    refresh_export_digest(document)
    with pytest.raises(ProjectContractFailure) as captured:
        adapter().parse_evidence_export(encoded(document))
    assert captured.value.code == "project.contract.export_record_mismatch"


def test_export_file_metadata_matches_bound_artifact_manifest() -> None:
    document = load("evidence-export.json")
    document["export"]["artifact_files"][0]["manifest_digest"] = "f" * 64  # type: ignore[index]
    refresh_export_digest(document)
    with pytest.raises(ProjectContractFailure) as captured:
        adapter().parse_evidence_export(encoded(document))
    assert captured.value.code == "project.contract.export_artifact_mismatch"


def test_canonical_digest_preserves_direct_non_ascii_utf8() -> None:
    vector = json.loads(
        (
            REPOSITORY
            / "contracts/compatibility/project-workspace/v1/vectors/non-ascii-snapshot-digest.json"
        ).read_text(encoding="utf-8")
    )
    assert contract_digest(adapter(), vector["record"]) == vector["record_digest"]


def contract_digest(
    contract: ContractProjectAdapter,
    value: dict[str, object],
) -> str:
    return contract.canonical_digest(value)

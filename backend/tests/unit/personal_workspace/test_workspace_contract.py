from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
import json
from pathlib import Path

import pytest

from financial_ai_academy.modules.personal_workspace.adapters.workspace_contract import (
    ContractPersonalWorkspaceAdapter,
)
from financial_ai_academy.modules.personal_workspace.domain.workspace import (
    ArchiveRecordMutation,
    CreateBookmarkMutation,
    CreateCollectionMutation,
    LearningOpportunityReference,
    RefreshReferenceMutation,
    RemoveRecordMutation,
    RemoveCollectionMutation,
    RenameCollectionMutation,
    ReorderRecordsMutation,
    RestoreRecordMutation,
    SetCollectionMembersMutation,
    UpdateBookmarkMutation,
    UpdateNoteMutation,
    WorkspaceBookmark,
    WorkspaceMutationIntent,
    WorkspaceNote,
    WorkspaceQuery,
    ProjectArtifactReference,
    ProjectSnapshotReference,
    ProjectWorkspaceReference,
)
from financial_ai_academy.modules.personal_workspace.ports.workspace_contract import (
    PersonalWorkspaceContractFailure,
)


ROOT = Path(__file__).parents[4]
SCHEMA_DIR = ROOT / "contracts" / "learning" / "personal-workspace" / "v1"
FIXTURE_DIR = ROOT / "contracts" / "compatibility" / "personal-workspace" / "v1"
T1 = datetime(2026, 10, 17, 12, 5, tzinfo=timezone.utc)
T2 = datetime(2026, 10, 17, 12, 10, tzinfo=timezone.utc)
T3 = datetime(2026, 10, 17, 12, 15, tzinfo=timezone.utc)
T4 = datetime(2026, 10, 17, 12, 20, tzinfo=timezone.utc)
T5 = datetime(2026, 10, 17, 12, 25, tzinfo=timezone.utc)


@pytest.fixture
def adapter() -> ContractPersonalWorkspaceAdapter:
    return ContractPersonalWorkspaceAdapter(SCHEMA_DIR)


def _intent(revision: int, mutation: object) -> WorkspaceMutationIntent:
    return WorkspaceMutationIntent(
        schema_version="1.0.0",
        idempotency_key=f"intent.revision-{revision}",
        expected_revision=revision,
        mutation=mutation,  # type: ignore[arg-type]
    )


def _reference(adapter: ContractPersonalWorkspaceAdapter):
    intent = adapter.parse_mutation_intent(
        (FIXTURE_DIR / "valid-create-note-intent.json").read_bytes()
    )
    return intent.mutation.target  # type: ignore[union-attr]


def _project_reference(adapter: ContractPersonalWorkspaceAdapter, fixture: str):
    intent = adapter.parse_mutation_intent((FIXTURE_DIR / fixture).read_bytes())
    return intent.mutation.target  # type: ignore[union-attr]


def test_empty_workspace_has_deterministic_digest(
    adapter: ContractPersonalWorkspaceAdapter,
) -> None:
    first = adapter.empty_workspace(
        workspace_id="workspace.demo", learner_id="learner.demo", created_at=T1
    )
    second = adapter.empty_workspace(
        workspace_id="workspace.demo", learner_id="learner.demo", created_at=T1
    )
    assert first == second
    material = adapter.workspace_document(first)
    digest = material.pop("workspace_digest")
    assert digest == adapter.canonical_digest(material)


def test_create_update_archive_restore_and_remove_note(
    adapter: ContractPersonalWorkspaceAdapter,
) -> None:
    workspace = adapter.parse_workspace(
        (FIXTURE_DIR / "valid-empty-workspace.json").read_bytes()
    )
    create = adapter.parse_mutation_intent(
        (FIXTURE_DIR / "valid-create-note-intent.json").read_bytes()
    )
    workspace = adapter.apply_mutation(
        workspace, create, occurred_at=T1, issued_id="note.one"
    )
    assert isinstance(workspace.records[0], WorkspaceNote)

    workspace = adapter.apply_mutation(
        workspace,
        _intent(2, UpdateNoteMutation("note.one", "Updated", "Updated body")),
        occurred_at=T2,
    )
    assert workspace.records[0].title == "Updated"

    workspace = adapter.apply_mutation(
        workspace, _intent(3, ArchiveRecordMutation("note.one")), occurred_at=T3
    )
    assert workspace.records[0].archived is True

    workspace = adapter.apply_mutation(
        workspace,
        _intent(4, RestoreRecordMutation("note.one")),
        occurred_at=datetime(2026, 10, 17, 12, 20, tzinfo=timezone.utc),
    )
    assert workspace.records[0].archived is False

    workspace = adapter.apply_mutation(
        workspace,
        _intent(5, RemoveRecordMutation("note.one")),
        occurred_at=datetime(2026, 10, 17, 12, 25, tzinfo=timezone.utc),
    )
    assert workspace.records == ()


def test_bookmark_and_collection_mutations_preserve_order(
    adapter: ContractPersonalWorkspaceAdapter,
) -> None:
    workspace = adapter.parse_workspace(
        (FIXTURE_DIR / "valid-empty-workspace.json").read_bytes()
    )
    reference = _reference(adapter)
    workspace = adapter.apply_mutation(
        workspace,
        _intent(1, CreateBookmarkMutation(reference, "First")),
        occurred_at=T1,
        issued_id="bookmark.one",
    )
    workspace = adapter.apply_mutation(
        workspace,
        _intent(2, CreateBookmarkMutation(reference, None)),
        occurred_at=T2,
        issued_id="bookmark.two",
    )
    workspace = adapter.apply_mutation(
        workspace,
        _intent(3, UpdateBookmarkMutation("bookmark.two", "Second")),
        occurred_at=T3,
    )
    assert isinstance(workspace.records[1], WorkspaceBookmark)

    workspace = adapter.apply_mutation(
        workspace,
        _intent(4, ReorderRecordsMutation(("bookmark.two", "bookmark.one"))),
        occurred_at=datetime(2026, 10, 17, 12, 20, tzinfo=timezone.utc),
    )
    workspace = adapter.apply_mutation(
        workspace,
        _intent(5, CreateCollectionMutation("Next steps")),
        occurred_at=datetime(2026, 10, 17, 12, 25, tzinfo=timezone.utc),
        issued_id="collection.next",
    )
    workspace = adapter.apply_mutation(
        workspace,
        _intent(
            6,
            SetCollectionMembersMutation(
                "collection.next", ("bookmark.two", "bookmark.one")
            ),
        ),
        occurred_at=datetime(2026, 10, 17, 12, 30, tzinfo=timezone.utc),
    )
    assert [record.record_id for record in workspace.records] == [
        "bookmark.two",
        "bookmark.one",
    ]
    assert workspace.collections[0].member_record_ids == (
        "bookmark.two",
        "bookmark.one",
    )

    workspace = adapter.apply_mutation(
        workspace,
        _intent(7, RenameCollectionMutation("collection.next", "Later")),
        occurred_at=datetime(2026, 10, 17, 12, 35, tzinfo=timezone.utc),
    )
    assert workspace.collections[0].title == "Later"
    workspace = adapter.apply_mutation(
        workspace,
        _intent(8, RemoveCollectionMutation("collection.next")),
        occurred_at=datetime(2026, 10, 17, 12, 40, tzinfo=timezone.utc),
    )
    assert workspace.collections == ()


def test_learning_and_project_references_share_one_flexible_workspace_core(
    adapter: ContractPersonalWorkspaceAdapter,
) -> None:
    workspace = adapter.parse_workspace(
        (FIXTURE_DIR / "valid-empty-workspace.json").read_bytes()
    )
    targets = (
        _reference(adapter),
        _project_reference(adapter, "valid-project-workspace-note.json"),
        _project_reference(adapter, "valid-project-snapshot-bookmark.json"),
        _project_reference(adapter, "valid-project-artifact-bookmark.json"),
    )
    assert isinstance(targets[1], ProjectWorkspaceReference)
    assert isinstance(targets[2], ProjectSnapshotReference)
    assert isinstance(targets[3], ProjectArtifactReference)
    for index, target in enumerate(targets, start=1):
        workspace = adapter.apply_mutation(
            workspace,
            _intent(
                workspace.revision,
                CreateBookmarkMutation(target, f"Saved target {index}"),
            ),
            occurred_at=datetime(
                2026, 10, 17, 13, index, tzinfo=timezone.utc
            ),
            issued_id=f"bookmark.{index}",
        )
    workspace = adapter.apply_mutation(
        workspace,
        _intent(workspace.revision, CreateCollectionMutation("Mixed sources")),
        occurred_at=datetime(2026, 10, 17, 13, 10, tzinfo=timezone.utc),
        issued_id="collection.mixed",
    )
    workspace = adapter.apply_mutation(
        workspace,
        _intent(
            workspace.revision,
            SetCollectionMembersMutation(
                "collection.mixed",
                tuple(record.record_id for record in reversed(workspace.records)),
            ),
        ),
        occurred_at=datetime(2026, 10, 17, 13, 11, tzinfo=timezone.utc),
    )

    portable = adapter.workspace_document(workspace)
    reopened = adapter.parse_workspace(json.dumps(portable).encode("utf-8"))
    assert reopened == workspace
    assert reopened.collections[0].member_record_ids == (
        "bookmark.4",
        "bookmark.3",
        "bookmark.2",
        "bookmark.1",
    )


def test_query_normalizes_text_and_composes_safe_filters(
    adapter: ContractPersonalWorkspaceAdapter,
) -> None:
    workspace = adapter.parse_workspace(
        (FIXTURE_DIR / "valid-populated-workspace.json").read_bytes()
    )
    result = adapter.query_workspace(
        workspace,
        WorkspaceQuery(
            text="  RISK\u00a0AND   RETURN ",
            record_kinds=("bookmark",),
            owner_modules=("curriculum",),
            reference_kinds=("placed_lesson",),
            target_statuses=("available",),
            archived=False,
            collection_id="collection.foundations",
            sort="title_asc",
        ),
    )
    assert result.applied_query.text == "risk and return"
    assert [record.record_id for record in result.records] == ["bookmark.one"]
    assert result.next_cursor is None
    assert adapter.parse_workspace_query_result(
        json.dumps(adapter.workspace_query_result_document(result)).encode("utf-8")
    ) == result


def test_query_pages_are_stable_and_revision_bound(
    adapter: ContractPersonalWorkspaceAdapter,
) -> None:
    workspace = adapter.parse_workspace(
        (FIXTURE_DIR / "valid-populated-workspace.json").read_bytes()
    )
    first = adapter.query_workspace(workspace, WorkspaceQuery(limit=1))
    assert [record.record_id for record in first.records] == ["note.one"]
    assert first.next_cursor is not None

    second = adapter.query_workspace(
        workspace,
        WorkspaceQuery(limit=1, cursor=first.next_cursor),
    )
    assert [record.record_id for record in second.records] == ["bookmark.one"]
    assert second.next_cursor is None

    with pytest.raises(PersonalWorkspaceContractFailure) as tampered:
        adapter.query_workspace(
            workspace,
            WorkspaceQuery(limit=1, cursor=first.next_cursor[:-1] + "A"),
        )
    assert tampered.value.code == "personal_workspace.contract.invalid_cursor"

    newer = replace(workspace, revision=workspace.revision + 1)
    material = adapter.workspace_document(workspace)
    material["revision"] = newer.revision
    material.pop("workspace_digest")
    newer = replace(
        newer,
        workspace_digest=adapter.canonical_digest(material),
    )
    with pytest.raises(PersonalWorkspaceContractFailure) as stale:
        adapter.query_workspace(
            newer,
            WorkspaceQuery(limit=1, cursor=first.next_cursor),
        )
    assert stale.value.code == "personal_workspace.contract.invalid_cursor"


def test_query_filter_order_has_one_canonical_digest(
    adapter: ContractPersonalWorkspaceAdapter,
) -> None:
    workspace = adapter.parse_workspace(
        (FIXTURE_DIR / "valid-populated-workspace.json").read_bytes()
    )
    first = adapter.query_workspace(
        workspace,
        WorkspaceQuery(record_kinds=("note", "bookmark")),
    )
    second = adapter.query_workspace(
        workspace,
        WorkspaceQuery(record_kinds=("bookmark", "note")),
    )
    assert first.query_digest == second.query_digest
    assert first.applied_query.record_kinds == ("bookmark", "note")


@pytest.mark.parametrize(
    ("sort", "expected"),
    [
        ("workspace_order", ["note.one", "bookmark.one"]),
        ("updated_desc", ["bookmark.one", "note.one"]),
        ("updated_asc", ["note.one", "bookmark.one"]),
        ("title_asc", ["bookmark.one", "note.one"]),
        ("source_asc", ["note.one", "bookmark.one"]),
    ],
)
def test_query_sorts_are_deterministic_without_fixture_count_assumptions(
    adapter: ContractPersonalWorkspaceAdapter,
    sort: str,
    expected: list[str],
) -> None:
    workspace = adapter.parse_workspace(
        (FIXTURE_DIR / "valid-populated-workspace.json").read_bytes()
    )
    result = adapter.query_workspace(
        workspace,
        WorkspaceQuery(sort=sort),  # type: ignore[arg-type]
    )
    assert [record.record_id for record in result.records] == expected


def test_unavailable_refresh_preserves_learner_content_order_and_membership(
    adapter: ContractPersonalWorkspaceAdapter,
) -> None:
    workspace = adapter.parse_workspace(
        (FIXTURE_DIR / "valid-populated-workspace.json").read_bytes()
    )
    original = workspace.records[0]
    refreshed = adapter.apply_reference_refresh(
        workspace,
        _intent(workspace.revision, RefreshReferenceMutation("note.one")),
        occurred_at=T4,
        resolved_reference=None,
    )
    assert refreshed.records[0].target.target_status == "unavailable"
    assert refreshed.records[0].target.validated_at == T4
    assert refreshed.records[0].title == original.title
    assert refreshed.records[0].body == original.body  # type: ignore[union-attr]
    assert refreshed.collections == workspace.collections
    assert [record.record_id for record in refreshed.records] == [
        record.record_id for record in workspace.records
    ]


def test_exact_refresh_recovers_and_changed_immutable_meaning_becomes_stale(
    adapter: ContractPersonalWorkspaceAdapter,
) -> None:
    workspace = adapter.parse_workspace(
        (FIXTURE_DIR / "valid-populated-workspace.json").read_bytes()
    )
    unavailable = adapter.apply_reference_refresh(
        workspace,
        _intent(4, RefreshReferenceMutation("note.one")),
        occurred_at=T4,
        resolved_reference=None,
    )
    original = workspace.records[0].target
    assert isinstance(original, LearningOpportunityReference)
    recovered_reference = replace(
        original,
        target_status="available",
        validated_at=T5,
    )
    recovered = adapter.apply_reference_refresh(
        unavailable,
        _intent(5, RefreshReferenceMutation("note.one")),
        occurred_at=T5,
        resolved_reference=recovered_reference,
    )
    assert recovered.records[0].target.target_status == "available"

    changed = replace(
        recovered_reference,
        package_digest="f" * 64,
        validated_at=datetime(2026, 10, 17, 12, 30, tzinfo=timezone.utc),
    )
    stale = adapter.apply_reference_refresh(
        recovered,
        _intent(6, RefreshReferenceMutation("note.one")),
        occurred_at=datetime(2026, 10, 17, 12, 30, tzinfo=timezone.utc),
        resolved_reference=changed,
    )
    assert stale.records[0].target.target_status == "stale"
    assert (
        stale.records[0].target.package_digest  # type: ignore[union-attr]
        == original.package_digest
    )


def test_mutable_project_refresh_updates_safe_facts_but_snapshot_drift_is_stale(
    adapter: ContractPersonalWorkspaceAdapter,
) -> None:
    workspace = adapter.parse_workspace(
        (FIXTURE_DIR / "valid-empty-workspace.json").read_bytes()
    )
    project = _project_reference(adapter, "valid-project-workspace-note.json")
    workspace = adapter.apply_mutation(
        workspace,
        _intent(1, CreateBookmarkMutation(project, "Project")),
        occurred_at=datetime(2026, 10, 17, 13, 1, tzinfo=timezone.utc),
        issued_id="bookmark.project",
    )
    refreshed_project = replace(
        project,
        title="Updated safe title",
        project_revision=3,
        workspace_revision=5,
        validated_at=datetime(2026, 10, 17, 13, 2, tzinfo=timezone.utc),
    )
    workspace = adapter.apply_reference_refresh(
        workspace,
        _intent(2, RefreshReferenceMutation("bookmark.project")),
        occurred_at=datetime(2026, 10, 17, 13, 2, tzinfo=timezone.utc),
        resolved_reference=refreshed_project,
    )
    assert workspace.records[0].target.title == "Updated safe title"
    assert workspace.records[0].target.target_status == "available"

    snapshot = _project_reference(adapter, "valid-project-snapshot-bookmark.json")
    workspace = adapter.apply_mutation(
        workspace,
        _intent(3, CreateBookmarkMutation(snapshot, "Snapshot")),
        occurred_at=datetime(2026, 10, 17, 13, 3, tzinfo=timezone.utc),
        issued_id="bookmark.snapshot",
    )
    changed_snapshot = replace(
        snapshot,
        snapshot_digest="f" * 64,
        validated_at=datetime(2026, 10, 17, 13, 4, tzinfo=timezone.utc),
    )
    workspace = adapter.apply_reference_refresh(
        workspace,
        _intent(4, RefreshReferenceMutation("bookmark.snapshot")),
        occurred_at=datetime(2026, 10, 17, 13, 4, tzinfo=timezone.utc),
        resolved_reference=changed_snapshot,
    )
    assert workspace.records[1].target.target_status == "stale"
    assert (
        workspace.records[1].target.snapshot_digest  # type: ignore[union-attr]
        == snapshot.snapshot_digest
    )


def test_refresh_rejects_caller_only_core_path_and_mismatched_selector(
    adapter: ContractPersonalWorkspaceAdapter,
) -> None:
    workspace = adapter.parse_workspace(
        (FIXTURE_DIR / "valid-populated-workspace.json").read_bytes()
    )
    intent = _intent(4, RefreshReferenceMutation("note.one"))
    with pytest.raises(PersonalWorkspaceContractFailure) as unresolved:
        adapter.apply_mutation(workspace, intent, occurred_at=T4)
    assert unresolved.value.code == (
        "personal_workspace.contract.refresh_resolution_required"
    )

    original = workspace.records[0].target
    assert isinstance(original, LearningOpportunityReference)
    mismatched = replace(
        original,
        opportunity_id="opportunity.other",
        validated_at=T4,
    )
    with pytest.raises(PersonalWorkspaceContractFailure) as mismatch:
        adapter.apply_reference_refresh(
            workspace,
            intent,
            occurred_at=T4,
            resolved_reference=mismatched,
        )
    assert mismatch.value.code == (
        "personal_workspace.contract.invalid_refresh_result"
    )


@pytest.mark.parametrize(
    ("intent", "code"),
    [
        (
            _intent(2, CreateCollectionMutation("Stale")),
            "personal_workspace.contract.stale_revision",
        ),
        (
            _intent(1, RemoveRecordMutation("note.missing")),
            "personal_workspace.contract.record_not_found",
        ),
        (
            _intent(1, ReorderRecordsMutation(("note.missing",))),
            "personal_workspace.contract.invalid_membership",
        ),
    ],
)
def test_invalid_mutations_fail_closed(
    adapter: ContractPersonalWorkspaceAdapter,
    intent: WorkspaceMutationIntent,
    code: str,
) -> None:
    workspace = adapter.parse_workspace(
        (FIXTURE_DIR / "valid-empty-workspace.json").read_bytes()
    )
    with pytest.raises(PersonalWorkspaceContractFailure) as failure:
        adapter.apply_mutation(workspace, intent, occurred_at=T1)
    assert failure.value.code == code


def test_creation_requires_an_external_identifier(
    adapter: ContractPersonalWorkspaceAdapter,
) -> None:
    workspace = adapter.parse_workspace(
        (FIXTURE_DIR / "valid-empty-workspace.json").read_bytes()
    )
    intent = adapter.parse_mutation_intent(
        (FIXTURE_DIR / "valid-create-note-intent.json").read_bytes()
    )
    with pytest.raises(PersonalWorkspaceContractFailure) as failure:
        adapter.apply_mutation(workspace, intent, occurred_at=T1)
    assert failure.value.code == "personal_workspace.contract.issued_id_required"


@pytest.mark.parametrize(
    ("issued_id", "accepted"),
    [("a", True), ("a" * 128, True), ("a" * 129, False)],
)
def test_issued_ids_use_the_platform_identifier_profile(
    adapter: ContractPersonalWorkspaceAdapter,
    issued_id: str,
    accepted: bool,
) -> None:
    workspace = adapter.parse_workspace(
        (FIXTURE_DIR / "valid-empty-workspace.json").read_bytes()
    )
    intent = adapter.parse_mutation_intent(
        (FIXTURE_DIR / "valid-create-note-intent.json").read_bytes()
    )
    if accepted:
        result = adapter.apply_mutation(
            workspace, intent, occurred_at=T1, issued_id=issued_id
        )
        assert result.records[0].record_id == issued_id
    else:
        with pytest.raises(PersonalWorkspaceContractFailure) as failure:
            adapter.apply_mutation(
                workspace, intent, occurred_at=T1, issued_id=issued_id
            )
        assert failure.value.code == "personal_workspace.contract.invalid_shape"


def test_mutation_refuses_tampered_workspace_instead_of_resealing_it(
    adapter: ContractPersonalWorkspaceAdapter,
) -> None:
    workspace = adapter.parse_workspace(
        (FIXTURE_DIR / "valid-empty-workspace.json").read_bytes()
    )
    tampered = replace(workspace, workspace_digest="f" * 64)
    with pytest.raises(PersonalWorkspaceContractFailure) as failure:
        adapter.apply_mutation(
            tampered,
            _intent(1, CreateCollectionMutation("Collection")),
            occurred_at=T1,
            issued_id="collection.one",
        )
    assert failure.value.code == "personal_workspace.contract.digest_mismatch"


def test_mutation_refuses_invalid_direct_intent_instead_of_laundering_it(
    adapter: ContractPersonalWorkspaceAdapter,
) -> None:
    workspace = adapter.parse_workspace(
        (FIXTURE_DIR / "valid-empty-workspace.json").read_bytes()
    )
    intent = replace(
        _intent(1, CreateCollectionMutation("Collection")),
        idempotency_key="INVALID KEY",
    )
    with pytest.raises(PersonalWorkspaceContractFailure) as failure:
        adapter.apply_mutation(
            workspace,
            intent,
            occurred_at=T1,
            issued_id="collection.one",
        )
    assert failure.value.code == "personal_workspace.contract.invalid_shape"


def test_pure_core_rejects_naive_or_regressing_time(
    adapter: ContractPersonalWorkspaceAdapter,
) -> None:
    workspace = adapter.parse_workspace(
        (FIXTURE_DIR / "valid-empty-workspace.json").read_bytes()
    )
    intent = _intent(1, CreateCollectionMutation("Collection"))
    for occurred_at in (
        datetime(2026, 10, 17, 12, 5),
        datetime(2026, 10, 17, 11, 59, tzinfo=timezone.utc),
    ):
        with pytest.raises(PersonalWorkspaceContractFailure) as failure:
            adapter.apply_mutation(
                workspace,
                intent,
                occurred_at=occurred_at,
                issued_id="collection.one",
            )
        assert failure.value.code == "personal_workspace.contract.invalid_time"


def test_canonical_digest_is_key_order_independent(
    adapter: ContractPersonalWorkspaceAdapter,
) -> None:
    assert adapter.canonical_digest({"b": 2, "a": 1}) == adapter.canonical_digest(
        {"a": 1, "b": 2}
    )


def test_canonical_digest_uses_direct_utf8_for_unicode(
    adapter: ContractPersonalWorkspaceAdapter,
) -> None:
    assert adapter.canonical_digest({"text": "Café Δ"}) == (
        "63d74e3717776c4b0e26cca653e3f4075835c623436ae4c6c4be9b5882d205e6"
    )


@pytest.mark.parametrize(
    "mutation",
    [
        {"operation": "update_note", "record_id": "note.one", "title": "T", "body": "B"},
        {"operation": "create_bookmark", "target": None, "label": None},
        {"operation": "update_bookmark", "record_id": "bookmark.one", "label": None},
        {"operation": "create_collection", "title": "Collection"},
        {"operation": "rename_collection", "collection_id": "collection.one", "title": "Renamed"},
        {"operation": "remove_collection", "collection_id": "collection.one"},
        {"operation": "set_collection_members", "collection_id": "collection.one", "member_record_ids": ["note.one"]},
        {"operation": "reorder_records", "record_ids": ["note.one"]},
        {"operation": "archive_record", "record_id": "note.one"},
        {"operation": "restore_record", "record_id": "note.one"},
        {"operation": "remove_record", "record_id": "note.one"},
    ],
)
def test_every_additional_mutation_shape_is_closed_and_parseable(
    adapter: ContractPersonalWorkspaceAdapter,
    mutation: dict[str, object],
) -> None:
    if mutation["operation"] == "create_bookmark":
        mutation["target"] = adapter.reference_document(_reference(adapter))["reference"]
    document = {
        "schema_version": "1.0.0",
        "idempotency_key": "intent.table.case",
        "expected_revision": 1,
        "mutation": mutation,
    }
    parsed = adapter.parse_mutation_intent(
        json.dumps(document, ensure_ascii=False).encode("utf-8")
    )
    assert adapter.mutation_intent_document(parsed) == document


@pytest.mark.parametrize(
    "mutation",
    [
        {"operation": "create_collection", "title": "x" * 121},
        {"operation": "create_note", "target": None, "title": "T", "body": "x" * 8001},
        {"operation": "unknown_operation"},
    ],
)
def test_mutation_contract_rejects_overflow_and_unknown_operations(
    adapter: ContractPersonalWorkspaceAdapter,
    mutation: dict[str, object],
) -> None:
    if mutation["operation"] == "create_note":
        mutation["target"] = adapter.reference_document(_reference(adapter))["reference"]
    document = {
        "schema_version": "1.0.0",
        "idempotency_key": "intent.invalid.case",
        "expected_revision": 1,
        "mutation": mutation,
    }
    with pytest.raises(PersonalWorkspaceContractFailure) as failure:
        adapter.parse_mutation_intent(json.dumps(document).encode())
    assert failure.value.code == "personal_workspace.contract.invalid_shape"


def test_failure_message_does_not_echo_untrusted_content(
    adapter: ContractPersonalWorkspaceAdapter,
) -> None:
    secret = "secret-value"
    malformed = json.dumps({"secret": secret}).encode()
    with pytest.raises(PersonalWorkspaceContractFailure) as failure:
        adapter.parse_workspace(malformed)
    assert secret not in str(failure.value)

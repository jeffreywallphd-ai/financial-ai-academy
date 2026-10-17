from __future__ import annotations

import base64
from copy import deepcopy
from dataclasses import replace
from datetime import datetime, timezone
import hashlib
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
    PersonalWorkspace,
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


def _parse_workspace_document(
    adapter: ContractPersonalWorkspaceAdapter,
    document: dict[str, object],
) -> PersonalWorkspace:
    material = deepcopy(document)
    material.pop("workspace_digest", None)
    document["workspace_digest"] = adapter.canonical_digest(material)
    return adapter.parse_workspace(
        json.dumps(document, ensure_ascii=False).encode("utf-8")
    )


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


@pytest.mark.parametrize(
    "fixture_name",
    ["valid-empty-workspace.json", "valid-populated-workspace.json"],
)
def test_workspace_export_is_versioned_digest_bound_and_count_flexible(
    adapter: ContractPersonalWorkspaceAdapter,
    fixture_name: str,
) -> None:
    workspace = adapter.parse_workspace((FIXTURE_DIR / fixture_name).read_bytes())
    exported = adapter.export_workspace(workspace, generated_at=T5)
    document = adapter.workspace_export_document(exported)

    assert document["workspace_digest"] == workspace.workspace_digest
    assert document["workspace"] == adapter.workspace_document(workspace)
    assert adapter.parse_workspace_export(
        json.dumps(document, ensure_ascii=False).encode("utf-8")
    ) == exported


def test_workspace_export_rejects_time_before_current_workspace(
    adapter: ContractPersonalWorkspaceAdapter,
) -> None:
    workspace = adapter.parse_workspace(
        (FIXTURE_DIR / "valid-populated-workspace.json").read_bytes()
    )
    with pytest.raises(PersonalWorkspaceContractFailure) as failure:
        adapter.export_workspace(
            workspace,
            generated_at=datetime(2026, 10, 17, 12, 14, 59, tzinfo=timezone.utc),
        )
    assert failure.value.code == "personal_workspace.contract.invalid_time"


def test_record_capacity_accepts_200_and_rejects_201_without_mutation(
    adapter: ContractPersonalWorkspaceAdapter,
) -> None:
    document = json.loads(
        (FIXTURE_DIR / "valid-populated-workspace.json").read_text(encoding="utf-8")
    )
    template = document["records"][1]
    document["collections"] = []
    document["records"] = []
    for index in range(199):
        record = deepcopy(template)
        record["record_id"] = f"bookmark.{index:03d}"
        record["label"] = None if index % 3 == 0 else f"Saved {index}"
        document["records"].append(record)
    workspace = _parse_workspace_document(adapter, document)
    target = workspace.records[0].target

    full = adapter.apply_mutation(
        workspace,
        _intent(
            workspace.revision,
            CreateBookmarkMutation(target, "Two hundred"),
        ),
        occurred_at=T5,
        issued_id="bookmark.199",
    )
    assert len(full.records) == 200

    with pytest.raises(PersonalWorkspaceContractFailure) as failure:
        adapter.apply_mutation(
            full,
            _intent(
                full.revision,
                CreateBookmarkMutation(target, "Too many"),
            ),
            occurred_at=datetime(2026, 10, 17, 12, 30, tzinfo=timezone.utc),
            issued_id="bookmark.200",
        )
    assert failure.value.code == "personal_workspace.contract.record_limit"
    assert len(full.records) == 200


def test_collection_capacity_accepts_50_and_rejects_51_without_mutation(
    adapter: ContractPersonalWorkspaceAdapter,
) -> None:
    document = json.loads(
        (FIXTURE_DIR / "valid-populated-workspace.json").read_text(encoding="utf-8")
    )
    template = document["collections"][0]
    document["collections"] = []
    for index in range(49):
        collection = deepcopy(template)
        collection["collection_id"] = f"collection.{index:03d}"
        collection["title"] = f"Collection {index}"
        collection["member_record_ids"] = []
        document["collections"].append(collection)
    workspace = _parse_workspace_document(adapter, document)

    full = adapter.apply_mutation(
        workspace,
        _intent(workspace.revision, CreateCollectionMutation("Fiftieth")),
        occurred_at=T5,
        issued_id="collection.049",
    )
    assert len(full.collections) == 50

    with pytest.raises(PersonalWorkspaceContractFailure) as failure:
        adapter.apply_mutation(
            full,
            _intent(full.revision, CreateCollectionMutation("Too many")),
            occurred_at=datetime(2026, 10, 17, 12, 30, tzinfo=timezone.utc),
            issued_id="collection.050",
        )
    assert failure.value.code == "personal_workspace.contract.collection_limit"
    assert len(full.collections) == 50


def test_collection_membership_capacity_accepts_100_and_rejects_101(
    adapter: ContractPersonalWorkspaceAdapter,
) -> None:
    document = json.loads(
        (FIXTURE_DIR / "valid-populated-workspace.json").read_text(encoding="utf-8")
    )
    template = document["records"][1]
    document["records"] = []
    for index in range(101):
        record = deepcopy(template)
        record["record_id"] = f"bookmark.{index:03d}"
        document["records"].append(record)
    document["collections"][0]["member_record_ids"] = []
    workspace = _parse_workspace_document(adapter, document)
    first_hundred = tuple(f"bookmark.{index:03d}" for index in range(100))

    accepted = adapter.apply_mutation(
        workspace,
        _intent(
            workspace.revision,
            SetCollectionMembersMutation("collection.foundations", first_hundred),
        ),
        occurred_at=T5,
    )
    assert len(accepted.collections[0].member_record_ids) == 100

    with pytest.raises(PersonalWorkspaceContractFailure) as failure:
        adapter.apply_mutation(
            accepted,
            _intent(
                accepted.revision,
                SetCollectionMembersMutation(
                    "collection.foundations",
                    first_hundred + ("bookmark.100",),
                ),
            ),
            occurred_at=datetime(2026, 10, 17, 12, 30, tzinfo=timezone.utc),
        )
    assert failure.value.code == (
        "personal_workspace.contract.collection_member_limit"
    )
    assert accepted.collections[0].member_record_ids == first_hundred


def test_malformed_membership_shape_does_not_masquerade_as_capacity(
    adapter: ContractPersonalWorkspaceAdapter,
) -> None:
    malformed = {
        "schema_version": "1.0.0",
        "idempotency_key": "membership.malformed",
        "expected_revision": 1,
        "mutation": {
            "operation": "not_a_workspace_operation",
            "collection_id": "collection.one",
            "member_record_ids": [f"record.{index:03d}" for index in range(101)],
        },
    }
    with pytest.raises(PersonalWorkspaceContractFailure) as failure:
        adapter.parse_mutation_intent(json.dumps(malformed).encode("utf-8"))
    assert failure.value.code == "personal_workspace.contract.invalid_shape"


@pytest.mark.parametrize(
    "member_record_ids",
    [
        [f"record.{index:03d}" for index in range(100)] + ["NOT_VALID"],
        [f"record.{index:03d}" for index in range(100)] + ["record.099"],
    ],
)
def test_invalid_or_duplicate_oversized_membership_is_not_capacity(
    adapter: ContractPersonalWorkspaceAdapter,
    member_record_ids: list[str],
) -> None:
    document = {
        "schema_version": "1.0.0",
        "idempotency_key": "membership.invalid-overflow",
        "expected_revision": 1,
        "mutation": {
            "operation": "set_collection_members",
            "collection_id": "collection.one",
            "member_record_ids": member_record_ids,
        },
    }
    with pytest.raises(PersonalWorkspaceContractFailure) as failure:
        adapter.parse_mutation_intent(json.dumps(document).encode("utf-8"))
    assert failure.value.code == "personal_workspace.contract.invalid_shape"


def test_removal_cleans_only_workspace_owned_order_and_membership(
    adapter: ContractPersonalWorkspaceAdapter,
) -> None:
    document = json.loads(
        (FIXTURE_DIR / "valid-populated-workspace.json").read_text(encoding="utf-8")
    )
    second_collection = deepcopy(document["collections"][0])
    second_collection["collection_id"] = "collection.follow-up"
    second_collection["title"] = "Follow up"
    second_collection["member_record_ids"] = ["note.one"]
    document["collections"].append(second_collection)
    workspace = _parse_workspace_document(adapter, document)
    retained_record = workspace.records[1]

    removed = adapter.apply_mutation(
        workspace,
        _intent(workspace.revision, RemoveRecordMutation("note.one")),
        occurred_at=T5,
    )
    assert removed.records == (retained_record,)
    assert removed.collections[0].member_record_ids == ("bookmark.one",)
    assert removed.collections[1].member_record_ids == ()

    records_before_collection_removal = removed.records
    without_collection = adapter.apply_mutation(
        removed,
        _intent(
            removed.revision,
            RemoveCollectionMutation("collection.follow-up"),
        ),
        occurred_at=datetime(2026, 10, 17, 12, 30, tzinfo=timezone.utc),
    )
    assert without_collection.records == records_before_collection_removal
    assert tuple(
        collection.collection_id for collection in without_collection.collections
    ) == ("collection.foundations",)


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


def test_oversized_query_result_keeps_non_quota_failure(
    adapter: ContractPersonalWorkspaceAdapter,
) -> None:
    workspace = adapter.parse_workspace(
        (FIXTURE_DIR / "valid-populated-workspace.json").read_bytes()
    )
    result = adapter.query_workspace(workspace, WorkspaceQuery(limit=100))
    document = adapter.workspace_query_result_document(result)
    document["records"] = [document["records"][0]] * 101

    with pytest.raises(PersonalWorkspaceContractFailure) as failure:
        adapter.parse_workspace_query_result(json.dumps(document).encode("utf-8"))
    assert failure.value.code == "personal_workspace.contract.invalid_shape"


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


def test_query_cursor_rejects_recomputed_tampering_and_cross_workspace_replay(
    adapter: ContractPersonalWorkspaceAdapter,
) -> None:
    workspace = adapter.parse_workspace(
        (FIXTURE_DIR / "valid-populated-workspace.json").read_bytes()
    )
    first = adapter.query_workspace(workspace, WorkspaceQuery(limit=1))
    assert first.next_cursor is not None

    padded = first.next_cursor + "=" * (-len(first.next_cursor) % 4)
    cursor_document = json.loads(
        base64.urlsafe_b64decode(padded.encode("ascii")).decode("utf-8")
    )
    cursor_document["offset"] = 0
    unsigned = dict(cursor_document)
    unsigned.pop("mac")
    cursor_document["mac"] = hashlib.sha256(
        json.dumps(
            unsigned,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
    ).hexdigest()
    forged = base64.urlsafe_b64encode(
        json.dumps(
            cursor_document,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
    ).decode("ascii").rstrip("=")
    with pytest.raises(PersonalWorkspaceContractFailure) as tampered:
        adapter.query_workspace(
            workspace,
            WorkspaceQuery(limit=1, cursor=forged),
        )
    assert tampered.value.code == "personal_workspace.contract.invalid_cursor"

    other_document = adapter.workspace_document(workspace)
    other_document["workspace_id"] = "workspace.other"
    other_document["learner_id"] = "learner.other"
    other_document.pop("workspace_digest")
    other = replace(
        workspace,
        workspace_id="workspace.other",
        learner_id="learner.other",
        workspace_digest=adapter.canonical_digest(other_document),
    )
    with pytest.raises(PersonalWorkspaceContractFailure) as replayed:
        adapter.query_workspace(
            other,
            WorkspaceQuery(limit=1, cursor=first.next_cursor),
        )
    assert replayed.value.code == "personal_workspace.contract.invalid_cursor"


def test_query_result_validates_applied_cursor_and_page_progression(
    adapter: ContractPersonalWorkspaceAdapter,
) -> None:
    workspace = adapter.parse_workspace(
        (FIXTURE_DIR / "valid-populated-workspace.json").read_bytes()
    )
    first = adapter.query_workspace(workspace, WorkspaceQuery(limit=1))
    assert first.next_cursor is not None
    second = adapter.query_workspace(
        workspace,
        WorkspaceQuery(limit=1, cursor=first.next_cursor),
    )
    second_document = adapter.workspace_query_result_document(second)
    assert adapter.parse_workspace_query_result(
        json.dumps(second_document).encode("utf-8")
    ) == second

    second_document["applied_query"]["cursor"] = "A"
    with pytest.raises(PersonalWorkspaceContractFailure) as malformed:
        adapter.parse_workspace_query_result(
            json.dumps(second_document).encode("utf-8")
        )
    assert malformed.value.code == "personal_workspace.contract.invalid_cursor"

    first_document = adapter.workspace_query_result_document(first)
    first_document["records"] = []
    with pytest.raises(PersonalWorkspaceContractFailure) as stalled:
        adapter.parse_workspace_query_result(json.dumps(first_document).encode("utf-8"))
    assert stalled.value.code == "personal_workspace.contract.invalid_query_result"


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


def test_each_retained_immutable_reference_fact_marks_drift_stale(
    adapter: ContractPersonalWorkspaceAdapter,
) -> None:
    populated = adapter.parse_workspace(
        (FIXTURE_DIR / "valid-populated-workspace.json").read_bytes()
    )
    learning_opportunity = populated.records[0].target
    placed_lesson = populated.records[1].target
    snapshot = _project_reference(adapter, "valid-project-snapshot-bookmark.json")
    artifact = _project_reference(adapter, "valid-project-artifact-bookmark.json")
    assert isinstance(learning_opportunity, LearningOpportunityReference)
    assert isinstance(snapshot, ProjectSnapshotReference)
    assert isinstance(artifact, ProjectArtifactReference)

    refresh_at = datetime(2026, 10, 17, 14, 0, tzinfo=timezone.utc)
    cases = [
        (
            learning_opportunity,
            {
                "package_id": "package.changed",
                "package_version": "2.0.0",
                "package_digest": "f" * 64,
                "source_fingerprint": "e" * 64,
                "provenance": replace(
                    learning_opportunity.provenance,
                    published_by="Changed publisher",
                ),
            },
        ),
        (
            placed_lesson,
            {
                "package_id": "package.changed",
                "package_version": "2.0.0",
                "package_digest": "f" * 64,
                "provenance": replace(
                    placed_lesson.provenance,
                    content_reviewed_on="2026-10-17",
                ),
            },
        ),
        (
            snapshot,
            {
                "project_revision": snapshot.project_revision + 1,
                "workspace_revision": snapshot.workspace_revision + 1,
                "snapshot_digest": "f" * 64,
                "closed_at": snapshot.closed_at.replace(minute=31),
            },
        ),
        (
            artifact,
            {
                "artifact_kind": "notebook",
                "logical_path": "evidence/changed-inputs.csv",
                "media_type": "text/plain",
                "inspection_mode": "metadata_only",
                "byte_count": artifact.byte_count + 1,
                "content_digest": "f" * 64,
                "created_at": artifact.created_at.replace(minute=31),
            },
        ),
    ]

    for original, changes in cases:
        for field, changed_value in changes.items():
            workspace = adapter.parse_workspace(
                (FIXTURE_DIR / "valid-empty-workspace.json").read_bytes()
            )
            workspace = adapter.apply_mutation(
                workspace,
                _intent(1, CreateBookmarkMutation(original, "Saved")),
                occurred_at=datetime(2026, 10, 17, 13, 30, tzinfo=timezone.utc),
                issued_id="bookmark.immutable",
            )
            changed = replace(
                original,
                **{field: changed_value},
                target_status="available",
                validated_at=refresh_at,
            )
            refreshed = adapter.apply_reference_refresh(
                workspace,
                _intent(2, RefreshReferenceMutation("bookmark.immutable")),
                occurred_at=refresh_at,
                resolved_reference=changed,
            )
            retained = refreshed.records[0].target
            assert retained.target_status == "stale", field
            assert getattr(retained, field) == getattr(original, field), field


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

from __future__ import annotations

import json
from pathlib import Path
from copy import deepcopy

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from financial_ai_academy.modules.personal_workspace.adapters.workspace_contract import (
    ContractPersonalWorkspaceAdapter,
)
from financial_ai_academy.modules.personal_workspace.ports.workspace_contract import (
    PersonalWorkspaceContractFailure,
)
from financial_ai_academy.modules.personal_workspace.domain.workspace import (
    ProjectArtifactReference,
    ProjectSnapshotReference,
    ProjectWorkspaceReference,
)


ROOT = Path(__file__).parents[4]
SCHEMA_DIR = ROOT / "contracts" / "learning" / "personal-workspace" / "v1"
FIXTURE_DIR = ROOT / "contracts" / "compatibility" / "personal-workspace" / "v1"
EXPORT_DENIALS = json.loads(
    (FIXTURE_DIR / "workspace-export-denials.json").read_text(encoding="utf-8")
)["cases"]


@pytest.fixture
def adapter() -> ContractPersonalWorkspaceAdapter:
    return ContractPersonalWorkspaceAdapter(SCHEMA_DIR)


def _fixture(name: str) -> dict[str, object]:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def _seal(
    adapter: ContractPersonalWorkspaceAdapter,
    document: dict[str, object],
) -> bytes:
    material = deepcopy(document)
    material.pop("workspace_digest", None)
    document["workspace_digest"] = adapter.canonical_digest(material)
    return json.dumps(document, ensure_ascii=False).encode("utf-8")


def _expect_workspace_failure(
    adapter: ContractPersonalWorkspaceAdapter,
    document: dict[str, object],
    code: str,
) -> None:
    with pytest.raises(PersonalWorkspaceContractFailure) as failure:
        adapter.parse_workspace(_seal(adapter, document))
    assert failure.value.code == code


def test_all_v1_schemas_are_valid_draft_2020_12() -> None:
    names = {path.name for path in SCHEMA_DIR.glob("*.schema.json")}
    assert names == {
        "learning-reference.schema.json",
        "mutation-intent.schema.json",
        "workspace-query-result.schema.json",
        "workspace-query.schema.json",
        "workspace-export.schema.json",
        "workspace.schema.json",
    }
    for path in SCHEMA_DIR.glob("*.schema.json"):
        Draft202012Validator.check_schema(json.loads(path.read_text(encoding="utf-8")))


@pytest.mark.parametrize(
    "fixture_name",
    ["valid-empty-workspace.json", "valid-populated-workspace.json"],
)
def test_workspace_compatibility_fixtures_are_canonical(
    adapter: ContractPersonalWorkspaceAdapter,
    fixture_name: str,
) -> None:
    fixture = (FIXTURE_DIR / fixture_name).read_bytes()
    workspace = adapter.parse_workspace(fixture)
    assert adapter.workspace_document(workspace) == json.loads(fixture)


def test_workspace_export_fixture_is_canonical(
    adapter: ContractPersonalWorkspaceAdapter,
) -> None:
    fixture = (FIXTURE_DIR / "valid-workspace-export.json").read_bytes()
    exported = adapter.parse_workspace_export(fixture)
    assert adapter.workspace_export_document(exported) == json.loads(fixture)
    assert exported.workspace_digest == exported.workspace.workspace_digest


def _assign_path(document: object, path: list[object], value: object) -> None:
    target = document
    for part in path[:-1]:
        target = target[part]  # type: ignore[index]
    target[path[-1]] = value  # type: ignore[index]


@pytest.mark.parametrize("case", EXPORT_DENIALS, ids=lambda case: case["id"])
def test_workspace_export_denials_are_closed_and_bounded(
    adapter: ContractPersonalWorkspaceAdapter,
    case: dict[str, object],
) -> None:
    document = _fixture("valid-workspace-export.json")
    _assign_path(document, case["path"], case["value"])  # type: ignore[arg-type]
    with pytest.raises(PersonalWorkspaceContractFailure) as failure:
        adapter.parse_workspace_export(
            json.dumps(document, ensure_ascii=False).encode("utf-8")
        )
    assert failure.value.code == case["expected_code"]


def test_create_note_intent_is_portable(
    adapter: ContractPersonalWorkspaceAdapter,
) -> None:
    fixture = (FIXTURE_DIR / "valid-create-note-intent.json").read_bytes()
    intent = adapter.parse_mutation_intent(fixture)
    assert adapter.mutation_intent_document(intent) == json.loads(fixture)


@pytest.mark.parametrize(
    "fixture_name",
    ["valid-stale-reference.json", "valid-unavailable-reference.json"],
)
def test_non_available_reference_fixtures_are_portable(
    adapter: ContractPersonalWorkspaceAdapter,
    fixture_name: str,
) -> None:
    fixture = (FIXTURE_DIR / fixture_name).read_bytes()
    reference = adapter.parse_reference(fixture)
    assert adapter.reference_document(reference) == json.loads(fixture)


def test_query_and_result_fixtures_are_portable(
    adapter: ContractPersonalWorkspaceAdapter,
) -> None:
    query_fixture = (FIXTURE_DIR / "valid-workspace-query.json").read_bytes()
    query = adapter.parse_workspace_query(query_fixture)
    assert adapter.workspace_query_document(query) == json.loads(query_fixture)

    result_fixture = (
        FIXTURE_DIR / "valid-workspace-query-result.json"
    ).read_bytes()
    result = adapter.parse_workspace_query_result(result_fixture)
    assert adapter.workspace_query_result_document(result) == json.loads(
        result_fixture
    )


@pytest.mark.parametrize("change", ["digest", "over_limit", "duplicate_record"])
def test_query_result_semantics_fail_closed(
    adapter: ContractPersonalWorkspaceAdapter,
    change: str,
) -> None:
    document = _fixture("valid-workspace-query-result.json")
    if change == "digest":
        document["query_digest"] = "f" * 64
        expected = "personal_workspace.contract.query_digest_mismatch"
    else:
        document["records"].append(  # type: ignore[union-attr]
            deepcopy(document["records"][0])  # type: ignore[index]
        )
        if change == "duplicate_record":
            document["applied_query"]["limit"] = 2  # type: ignore[index]
            document["query_digest"] = adapter.canonical_digest(  # type: ignore[assignment]
                document["applied_query"]  # type: ignore[arg-type,index]
            )
            expected = "personal_workspace.contract.duplicate_id"
        else:
            expected = "personal_workspace.contract.invalid_query_result"
    with pytest.raises(PersonalWorkspaceContractFailure) as failure:
        adapter.parse_workspace_query_result(json.dumps(document).encode("utf-8"))
    assert failure.value.code == expected


def test_query_and_refresh_private_fields_fail_closed(
    adapter: ContractPersonalWorkspaceAdapter,
) -> None:
    with pytest.raises(PersonalWorkspaceContractFailure) as query_failure:
        adapter.parse_workspace_query(
            (FIXTURE_DIR / "invalid-workspace-query-private-field.json").read_bytes()
        )
    assert query_failure.value.code == "personal_workspace.contract.invalid_shape"

    with pytest.raises(PersonalWorkspaceContractFailure) as refresh_failure:
        adapter.parse_mutation_intent(
            (FIXTURE_DIR / "invalid-refresh-private-field.json").read_bytes()
        )
    assert refresh_failure.value.code == "personal_workspace.contract.invalid_shape"


@pytest.mark.parametrize(
    "field",
    ["text", "record_kinds", "owner_modules", "reference_kinds", "target_statuses"],
)
def test_query_contract_rejects_empty_or_unknown_values(
    adapter: ContractPersonalWorkspaceAdapter,
    field: str,
) -> None:
    document: dict[str, object] = {"schema_version": "1.0.0"}
    document[field] = "   " if field == "text" else []
    with pytest.raises(PersonalWorkspaceContractFailure):
        adapter.parse_workspace_query(json.dumps(document).encode("utf-8"))


def test_refresh_intent_contains_only_workspace_record_identity(
    adapter: ContractPersonalWorkspaceAdapter,
) -> None:
    document = {
        "schema_version": "1.0.0",
        "idempotency_key": "intent.refresh-one",
        "expected_revision": 4,
        "mutation": {"operation": "refresh_reference", "record_id": "note.one"},
    }
    intent = adapter.parse_mutation_intent(json.dumps(document).encode("utf-8"))
    assert adapter.mutation_intent_document(intent) == document


@pytest.mark.parametrize(
    ("fixture_name", "reference_type"),
    [
        ("valid-project-workspace-note.json", ProjectWorkspaceReference),
        ("valid-project-snapshot-bookmark.json", ProjectSnapshotReference),
        ("valid-project-artifact-bookmark.json", ProjectArtifactReference),
    ],
)
def test_project_reference_intents_are_closed_and_portable(
    adapter: ContractPersonalWorkspaceAdapter,
    fixture_name: str,
    reference_type: type,
) -> None:
    fixture = (FIXTURE_DIR / fixture_name).read_bytes()
    intent = adapter.parse_mutation_intent(fixture)
    assert isinstance(intent.mutation.target, reference_type)  # type: ignore[union-attr]
    assert adapter.mutation_intent_document(intent) == json.loads(fixture)
    target = json.loads(fixture)["mutation"]["target"]
    reference = adapter.parse_reference(
        json.dumps(
            {"schema_version": "1.0.0", "reference": target}
        ).encode("utf-8")
    )
    assert isinstance(reference, reference_type)


@pytest.mark.parametrize(
    ("fixture_name", "code"),
    [
        ("invalid-dangling-collection.json", "personal_workspace.contract.dangling_member"),
        ("invalid-private-field.json", "personal_workspace.contract.invalid_shape"),
    ],
)
def test_invalid_compatibility_fixtures_fail_closed(
    adapter: ContractPersonalWorkspaceAdapter,
    fixture_name: str,
    code: str,
) -> None:
    with pytest.raises(PersonalWorkspaceContractFailure) as failure:
        adapter.parse_workspace((FIXTURE_DIR / fixture_name).read_bytes())
    assert failure.value.code == code


def test_contract_has_no_private_or_authoritative_learning_fields() -> None:
    forbidden = {
        "access_token",
        "answer_key",
        "grade",
        "mastery",
        "provider_payload",
        "recommendation_score",
        "storage_path",
        "artifact_bytes",
        "download_url",
        "object_key",
        "permission",
    }
    documents = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in SCHEMA_DIR.glob("*.schema.json")
    ]
    serialized = json.dumps(documents, sort_keys=True)
    for field in forbidden:
        assert f'"{field}"' not in serialized


def test_workspace_schema_rejects_more_than_declared_record_bound() -> None:
    schema = json.loads((SCHEMA_DIR / "workspace.schema.json").read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    fixture = json.loads((FIXTURE_DIR / "valid-populated-workspace.json").read_text())
    fixture["records"] = [fixture["records"][0]] * 201
    assert any(error.validator == "maxItems" for error in validator.iter_errors(fixture))


def test_reference_matches_curriculum_route_and_title_profile(
    adapter: ContractPersonalWorkspaceAdapter,
) -> None:
    document = _fixture("valid-populated-workspace.json")
    document["records"][0]["target"]["title"] = "T" * 240  # type: ignore[index]
    adapter.parse_workspace(_seal(adapter, document))

    too_long = deepcopy(document)
    too_long["records"][0]["target"]["title"] = "T" * 241  # type: ignore[index]
    _expect_workspace_failure(
        adapter, too_long, "personal_workspace.contract.invalid_shape"
    )

    protocol_relative = deepcopy(document)
    protocol_relative["records"][0]["target"]["destination"] = (  # type: ignore[index]
        "//external.example/private"
    )
    _expect_workspace_failure(
        adapter, protocol_relative, "personal_workspace.contract.invalid_shape"
    )

    mismatched = deepcopy(document)
    mismatched["records"][0]["target"]["destination"] = (  # type: ignore[index]
        "/learn/placements/placement.other"
    )
    _expect_workspace_failure(
        adapter, mismatched, "personal_workspace.contract.invalid_reference"
    )


@pytest.mark.parametrize(
    ("fixture_name", "field", "private_value"),
    [
        ("valid-project-workspace-note.json", "charter", "private charter"),
        ("valid-project-snapshot-bookmark.json", "snapshot", {"notes": []}),
        ("valid-project-artifact-bookmark.json", "object_key", "private/key"),
        ("valid-project-artifact-bookmark.json", "content", "secret bytes"),
        ("valid-project-artifact-bookmark.json", "source_url", "https://private"),
    ],
)
def test_project_references_reject_target_content_and_private_fields(
    adapter: ContractPersonalWorkspaceAdapter,
    fixture_name: str,
    field: str,
    private_value: object,
) -> None:
    document = _fixture(fixture_name)
    document["mutation"]["target"][field] = private_value  # type: ignore[index]
    with pytest.raises(PersonalWorkspaceContractFailure) as failure:
        adapter.parse_mutation_intent(json.dumps(document).encode("utf-8"))
    assert failure.value.code == "personal_workspace.contract.invalid_shape"


@pytest.mark.parametrize(
    ("fixture_name", "destination"),
    [
        ("valid-project-workspace-note.json", "/projects/other#workspace"),
        (
            "valid-project-snapshot-bookmark.json",
            "/projects/project.research-1#snapshot-other",
        ),
        (
            "valid-project-artifact-bookmark.json",
            "/projects/project.research-1#artifact-other-v3",
        ),
    ],
)
def test_project_reference_destinations_must_match_exact_identity(
    adapter: ContractPersonalWorkspaceAdapter,
    fixture_name: str,
    destination: str,
) -> None:
    document = _fixture(fixture_name)
    document["mutation"]["target"]["destination"] = destination  # type: ignore[index]
    with pytest.raises(PersonalWorkspaceContractFailure) as failure:
        adapter.parse_mutation_intent(json.dumps(document).encode("utf-8"))
    assert failure.value.code == "personal_workspace.contract.invalid_reference"


@pytest.mark.parametrize(
    ("fixture_name", "time_field"),
    [
        ("valid-project-snapshot-bookmark.json", "closed_at"),
        ("valid-project-artifact-bookmark.json", "created_at"),
    ],
)
def test_project_reference_source_time_cannot_follow_validation(
    adapter: ContractPersonalWorkspaceAdapter,
    fixture_name: str,
    time_field: str,
) -> None:
    document = _fixture(fixture_name)
    document["mutation"]["target"][time_field] = "2026-10-17T13:00:01Z"  # type: ignore[index]
    with pytest.raises(PersonalWorkspaceContractFailure) as failure:
        adapter.parse_mutation_intent(json.dumps(document).encode("utf-8"))
    assert failure.value.code == "personal_workspace.contract.invalid_time"


@pytest.mark.parametrize(
    "logical_path",
    [
        "../private.txt",
        "evidence/../private.txt",
        "evidence/./result.csv",
        "evidence//result.csv",
        "evidence /result.csv",
        "evidence/CON.txt",
        "evidence/control\u0001.csv",
        "evidence/cafe\u0301.csv",
        "evidence/result.",
    ],
)
@pytest.mark.parametrize("surface", ["reference", "mutation", "workspace"])
def test_project_artifact_paths_preserve_project_canonical_profile(
    adapter: ContractPersonalWorkspaceAdapter,
    logical_path: str,
    surface: str,
) -> None:
    mutation_document = _fixture("valid-project-artifact-bookmark.json")
    target = deepcopy(mutation_document["mutation"]["target"])  # type: ignore[index]
    target["logical_path"] = logical_path  # type: ignore[index]

    with pytest.raises(PersonalWorkspaceContractFailure) as failure:
        if surface == "reference":
            adapter.parse_reference(
                json.dumps(
                    {"schema_version": "1.0.0", "reference": target},
                    ensure_ascii=False,
                ).encode("utf-8")
            )
        elif surface == "mutation":
            mutation_document["mutation"]["target"] = target  # type: ignore[index]
            adapter.parse_mutation_intent(
                json.dumps(mutation_document, ensure_ascii=False).encode("utf-8")
            )
        else:
            workspace_document = _fixture("valid-populated-workspace.json")
            workspace_document["records"][0]["target"] = target  # type: ignore[index]
            adapter.parse_workspace(_seal(adapter, workspace_document))

    assert failure.value.code == "personal_workspace.contract.invalid_reference"


def test_nullable_bookmark_label_has_one_canonical_representation(
    adapter: ContractPersonalWorkspaceAdapter,
) -> None:
    document = _fixture("valid-populated-workspace.json")
    document["records"][1]["label"] = None  # type: ignore[index]
    parsed_bytes = _seal(adapter, document)
    parsed = adapter.parse_workspace(parsed_bytes)
    assert adapter.workspace_document(parsed) == json.loads(parsed_bytes)

    omitted = deepcopy(document)
    omitted["records"][1].pop("label")  # type: ignore[index]
    _expect_workspace_failure(
        adapter, omitted, "personal_workspace.contract.invalid_shape"
    )


@pytest.mark.parametrize(
    "mutation_change",
    [
        "omit_create_bookmark_label",
        "unsafe_create_note_destination",
        "mismatched_create_note_destination",
    ],
)
def test_mutation_references_use_the_same_closed_profile(
    adapter: ContractPersonalWorkspaceAdapter,
    mutation_change: str,
) -> None:
    document = _fixture("valid-create-note-intent.json")
    mutation = document["mutation"]  # type: ignore[assignment]
    if mutation_change == "omit_create_bookmark_label":
        mutation["operation"] = "create_bookmark"  # type: ignore[index]
        mutation.pop("title")  # type: ignore[union-attr]
        mutation.pop("body")  # type: ignore[union-attr]
    elif mutation_change == "unsafe_create_note_destination":
        mutation["target"]["destination"] = "//external.example/private"  # type: ignore[index]
    else:
        mutation["target"]["destination"] = "/learn/placements/placement.other"  # type: ignore[index]
    with pytest.raises(PersonalWorkspaceContractFailure):
        adapter.parse_mutation_intent(json.dumps(document).encode("utf-8"))


@pytest.mark.parametrize(
    "change",
    [
        "record_before_workspace",
        "record_after_workspace",
        "collection_before_workspace",
        "collection_after_workspace",
        "publication_after_validation",
        "validation_after_record",
    ],
)
def test_complete_workspace_chronology_fails_closed(
    adapter: ContractPersonalWorkspaceAdapter,
    change: str,
) -> None:
    document = _fixture("valid-populated-workspace.json")
    if change == "record_before_workspace":
        document["records"][0]["created_at"] = "2026-10-17T11:59:59Z"  # type: ignore[index]
    elif change == "record_after_workspace":
        document["records"][0]["updated_at"] = "2026-10-17T12:15:01Z"  # type: ignore[index]
    elif change == "collection_before_workspace":
        document["collections"][0]["created_at"] = "2026-10-17T11:59:59Z"  # type: ignore[index]
    elif change == "collection_after_workspace":
        document["collections"][0]["updated_at"] = "2026-10-17T12:15:01Z"  # type: ignore[index]
    elif change == "publication_after_validation":
        document["records"][0]["target"]["provenance"]["published_at"] = (  # type: ignore[index]
            "2026-10-17T11:01:00Z"
        )
    else:
        document["records"][0]["target"]["validated_at"] = (  # type: ignore[index]
            "2026-10-17T12:05:01Z"
        )
    _expect_workspace_failure(
        adapter, document, "personal_workspace.contract.invalid_time"
    )


def test_collection_and_membership_edges_are_not_fixture_count_rigid(
    adapter: ContractPersonalWorkspaceAdapter,
) -> None:
    base = _fixture("valid-populated-workspace.json")
    template_record = base["records"][1]  # type: ignore[index]
    base["records"] = []
    for index in range(101):
        record = deepcopy(template_record)
        record["record_id"] = f"bookmark.{index:03d}"
        record["label"] = None
        base["records"].append(record)  # type: ignore[union-attr]

    template_collection = base["collections"][0]  # type: ignore[index]
    base["collections"] = []
    for index in range(50):
        collection = deepcopy(template_collection)
        collection["collection_id"] = f"collection.{index:03d}"
        collection["member_record_ids"] = []
        base["collections"].append(collection)  # type: ignore[union-attr]
    base["collections"][0]["member_record_ids"] = [  # type: ignore[index]
        f"bookmark.{index:03d}" for index in range(100)
    ]
    adapter.parse_workspace(_seal(adapter, base))

    too_many_members = deepcopy(base)
    too_many_members["collections"][0]["member_record_ids"].append(  # type: ignore[index]
        "bookmark.100"
    )
    _expect_workspace_failure(
        adapter,
        too_many_members,
        "personal_workspace.contract.collection_member_limit",
    )

    too_many_collections = deepcopy(base)
    extra = deepcopy(too_many_collections["collections"][0])  # type: ignore[index]
    extra["collection_id"] = "collection.050"
    extra["member_record_ids"] = []
    too_many_collections["collections"].append(extra)  # type: ignore[union-attr]
    _expect_workspace_failure(
        adapter,
        too_many_collections,
        "personal_workspace.contract.collection_limit",
    )


@pytest.mark.parametrize(
    ("field", "value", "accepted"),
    [
        (field, value, accepted)
        for field in ("workspace_id", "learner_id")
        for value, accepted in (("a", True), ("a" * 128, True), ("a" * 129, False))
    ],
)
def test_platform_identifier_edges_are_explicit(
    adapter: ContractPersonalWorkspaceAdapter,
    field: str,
    value: str,
    accepted: bool,
) -> None:
    document = _fixture("valid-empty-workspace.json")
    document[field] = value
    if accepted:
        adapter.parse_workspace(_seal(adapter, document))
    else:
        _expect_workspace_failure(
            adapter, document, "personal_workspace.contract.invalid_shape"
        )


@pytest.mark.parametrize(
    ("field", "value", "accepted"),
    [
        (field, value, accepted)
        for field in ("opportunity_id", "placement_id", "package_id")
        for value, accepted in (
            ("aa", False),
            ("aaa", True),
            ("a" * 64, True),
            ("a" * 65, False),
        )
    ],
)
def test_curriculum_source_identifiers_keep_the_owner_profile(
    adapter: ContractPersonalWorkspaceAdapter,
    field: str,
    value: str,
    accepted: bool,
) -> None:
    document = _fixture("valid-create-note-intent.json")
    target = document["mutation"]["target"]  # type: ignore[index]
    target[field] = value
    if field == "placement_id":
        target["destination"] = f"/learn/placements/{value}"
    encoded = json.dumps(document).encode("utf-8")
    if accepted:
        adapter.parse_mutation_intent(encoded)
    else:
        with pytest.raises(PersonalWorkspaceContractFailure) as failure:
            adapter.parse_mutation_intent(encoded)
        assert failure.value.code == "personal_workspace.contract.invalid_shape"


@pytest.mark.parametrize(
    ("field", "value", "accepted"),
    [
        (field, value, accepted)
        for field in ("idempotency_key", "record_id")
        for value, accepted in (("a", True), ("a" * 128, True), ("a" * 129, False))
    ],
)
def test_mutation_platform_identifiers_keep_the_platform_profile(
    adapter: ContractPersonalWorkspaceAdapter,
    field: str,
    value: str,
    accepted: bool,
) -> None:
    document: dict[str, object] = {
        "schema_version": "1.0.0",
        "idempotency_key": "intent.valid",
        "expected_revision": 1,
        "mutation": {"operation": "remove_record", "record_id": "record.valid"},
    }
    if field == "idempotency_key":
        document[field] = value
    else:
        document["mutation"][field] = value  # type: ignore[index]
    encoded = json.dumps(document).encode("utf-8")
    if accepted:
        adapter.parse_mutation_intent(encoded)
    else:
        with pytest.raises(PersonalWorkspaceContractFailure) as failure:
            adapter.parse_mutation_intent(encoded)
        assert failure.value.code == "personal_workspace.contract.invalid_shape"


def test_owner_allowed_review_date_does_not_gain_consumer_ordering(
    adapter: ContractPersonalWorkspaceAdapter,
) -> None:
    document = _fixture("valid-create-note-intent.json")
    document["mutation"]["target"]["provenance"]["content_reviewed_on"] = (  # type: ignore[index]
        "2026-10-17"
    )
    adapter.parse_mutation_intent(json.dumps(document).encode("utf-8"))


@pytest.mark.parametrize(
    ("field", "limit"),
    [
        ("note_title", 120),
        ("note_body", 8000),
        ("source_title", 240),
        ("published_by", 160),
        ("educational_use_notice", 500),
    ],
)
def test_text_limits_accept_the_edge_and_reject_only_overflow(
    adapter: ContractPersonalWorkspaceAdapter,
    field: str,
    limit: int,
) -> None:
    document = _fixture("valid-create-note-intent.json")
    mutation = document["mutation"]  # type: ignore[assignment]
    target = mutation["target"]  # type: ignore[index]

    def assign(value: str) -> None:
        if field == "note_title":
            mutation["title"] = value  # type: ignore[index]
        elif field == "note_body":
            mutation["body"] = value  # type: ignore[index]
        elif field == "source_title":
            target["title"] = value  # type: ignore[index]
        elif field == "published_by":
            target["provenance"]["published_by"] = value  # type: ignore[index]
        else:
            target["provenance"]["educational_use_notice"] = value  # type: ignore[index]

    assign("x" * limit)
    adapter.parse_mutation_intent(json.dumps(document).encode("utf-8"))
    assign("x" * (limit + 1))
    with pytest.raises(PersonalWorkspaceContractFailure) as failure:
        adapter.parse_mutation_intent(json.dumps(document).encode("utf-8"))
    assert failure.value.code == "personal_workspace.contract.invalid_shape"


def test_record_count_accepts_200_and_rejects_201(
    adapter: ContractPersonalWorkspaceAdapter,
) -> None:
    document = _fixture("valid-populated-workspace.json")
    template = document["records"][1]  # type: ignore[index]
    document["collections"] = []
    document["records"] = []
    for index in range(200):
        record = deepcopy(template)
        record["record_id"] = f"bookmark.{index:03d}"
        record["label"] = "x" * (index % 121) or None
        document["records"].append(record)  # type: ignore[union-attr]
    adapter.parse_workspace(_seal(adapter, document))

    overflow = deepcopy(document)
    extra = deepcopy(template)
    extra["record_id"] = "bookmark.200"
    overflow["records"].append(extra)  # type: ignore[union-attr]
    _expect_workspace_failure(
        adapter, overflow, "personal_workspace.contract.record_limit"
    )

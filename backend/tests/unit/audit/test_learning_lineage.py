from __future__ import annotations

from dataclasses import replace
from datetime import date, datetime, timezone
import json

import pytest

from financial_ai_academy.modules.audit.adapters.learning_lineage import (
    ContentLearningLineageSource,
)
from financial_ai_academy.modules.audit.application.service import AuditService
from financial_ai_academy.modules.audit.domain.models import (
    AssessmentCompletionAuditRecord,
    AuditableAssessmentEvent,
)
from financial_ai_academy.modules.audit.ports.repositories import AuditRecordConflict
from financial_ai_academy.modules.audit.public import (
    AuditError,
    AuditErrorCode,
    ReadKnowledgeCheckCompletionLineageRequest,
    ReadPublishedLessonLineageRequest,
)
from financial_ai_academy.modules.content.public import (
    EducationalSource,
    PublicationProvenance,
    PublishedLesson,
)


LEARNER_ID = "11111111-1111-4111-8111-111111111111"
NOW = datetime(2026, 8, 5, 12, tzinfo=timezone.utc)
PACKAGE_DIGEST = "7" * 64
DEFINITION_DIGEST = "9" * 64


def _event() -> AuditableAssessmentEvent:
    return AuditableAssessmentEvent(
        schema_version="1.0.0",
        event_id="aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
        event_type="assessment.knowledge-check.completed",
        event_version="1.0.0",
        owner="assessment",
        occurred_at=NOW,
        idempotency_key="cccccccc-cccc-4ccc-8ccc-cccccccccccc",
        attempt_id="bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
        evidence_id="cccccccc-cccc-4ccc-8ccc-cccccccccccc",
        learner_id=LEARNER_ID,
        placement_id="intro-risk-return",
        package_id="intro-risk-return",
        package_version="1.1.0",
        package_digest=PACKAGE_DIGEST,
        assessment_id="risk-return-check-1",
        assessment_version="1.0.0",
        definition_digest=DEFINITION_DIGEST,
        item_id="risk-return-tradeoff",
        item_version="1.0.0",
        scoring_policy_id="single-select-exact-match",
        scoring_policy_version="1.0.0",
        score=1,
        max_score=1,
        completed_at=NOW,
    )


def _lesson(*, sources: tuple[EducationalSource, ...] | None = None) -> PublishedLesson:
    return PublishedLesson(
        package_id="intro-risk-return",
        package_version="1.1.0",
        package_digest=PACKAGE_DIGEST,
        title="Risk and return",
        objectives=("Compare risk and return.",),
        body=(),
        sources=sources
        if sources is not None
        else (
            EducationalSource(
                source_id="source-zeta",
                title="Zeta source",
                publisher="University",
                locator="https://private.example/zeta",
                reviewed_on=date(2026, 8, 2),
                license_note=None,
            ),
            EducationalSource(
                source_id="source-économie",
                title="Économie source",
                publisher="Research institute",
                locator="s3://private-bucket/source",
                reviewed_on=date(2026, 8, 1),
                license_note="Educational use",
            ),
        ),
        assets=(),
        provenance=PublicationProvenance(
            published_by="content-team",
            published_at=NOW,
            content_reviewed_on=date(2026, 8, 1),
            educational_use_notice="For education.",
        ),
    )


class Content:
    def __init__(self, lesson: PublishedLesson | None = None) -> None:
        self.lesson = lesson or _lesson()

    def get_published_lesson_version(self, _request: object) -> PublishedLesson:
        return self.lesson


class Source:
    def __init__(self, events: tuple[AuditableAssessmentEvent, ...]) -> None:
        self.events = events

    def list_for_lesson(
        self, *, learner_id: str, placement_id: str
    ) -> tuple[AuditableAssessmentEvent, ...]:
        return self.events


class Repository:
    def __init__(self) -> None:
        self.records: dict[str, AssessmentCompletionAuditRecord] = {}

    def append_assessment_completion_records(
        self, records: tuple[AssessmentCompletionAuditRecord, ...]
    ) -> None:
        for record in records:
            existing = self.records.get(record.event_id)
            if existing is not None and existing.integrity_digest != record.integrity_digest:
                raise AuditRecordConflict
            if existing is None:
                self.records[record.event_id] = record

    def read_assessment_completion_record(
        self,
        *,
        actor_id: str,
        placement_id: str,
        evidence_id: str,
    ) -> AssessmentCompletionAuditRecord | None:
        return next(
            (
                record
                for record in self.records.values()
                if record.actor_id == actor_id
                and record.placement_id == placement_id
                and record.evidence_id == evidence_id
            ),
            None,
        )


class Clock:
    def now(self) -> datetime:
        return NOW


def _service(
    *,
    event: AuditableAssessmentEvent | None = None,
    lesson: PublishedLesson | None = None,
    repository: Repository | None = None,
) -> tuple[AuditService, Repository]:
    retained = repository or Repository()
    return (
        AuditService(
            Source((event or _event(),)),
            retained,
            Clock(),
            ContentLearningLineageSource(Content(lesson)),
        ),
        retained,
    )


def test_published_lesson_lineage_is_order_independent_and_omits_payloads() -> None:
    service, _repository = _service()
    view = service.read_published_lesson_lineage(
        ReadPublishedLessonLineageRequest(
            "intro-risk-return",
            "1.1.0",
            PACKAGE_DIGEST,
        )
    )
    assert [node.envelope.resource.resource_kind.value for node in view.nodes] == [
        "published_lesson",
        "educational_source",
        "educational_source",
    ]
    serialized = json.dumps(view, default=str, ensure_ascii=False)
    assert "private.example" not in serialized
    assert "private-bucket" not in serialized
    assert "Risk and return" not in serialized

    reordered = replace(_lesson(), sources=tuple(reversed(_lesson().sources)))
    reordered_service, _repository = _service(lesson=reordered)
    assert (
        reordered_service.read_published_lesson_lineage(
            ReadPublishedLessonLineageRequest(
                "intro-risk-return", "1.1.0", PACKAGE_DIGEST
            )
        ).view_digest
        == view.view_digest
    )

    changed_source = replace(
        _lesson().sources[0],
        locator="https://private.example/revised-location",
    )
    changed_lesson = replace(
        _lesson(),
        sources=(changed_source, *_lesson().sources[1:]),
    )
    changed_service, _repository = _service(lesson=changed_lesson)
    changed_view = changed_service.read_published_lesson_lineage(
        ReadPublishedLessonLineageRequest(
            "intro-risk-return", "1.1.0", PACKAGE_DIGEST
        )
    )
    changed_serialized = json.dumps(
        changed_view,
        default=str,
        ensure_ascii=False,
    )
    assert "revised-location" not in changed_serialized
    assert changed_view.view_digest != view.view_digest


@pytest.mark.parametrize("value", (None, 7, False))
@pytest.mark.parametrize(
    "field",
    ("package_id", "package_version", "package_digest"),
)
def test_published_lesson_lineage_rejects_non_string_selectors(
    field: str,
    value: object,
) -> None:
    service, _repository = _service()
    request = ReadPublishedLessonLineageRequest(
        "intro-risk-return", "1.1.0", PACKAGE_DIGEST
    )
    with pytest.raises(AuditError) as invalid:
        service.read_published_lesson_lineage(replace(request, **{field: value}))

    assert invalid.value.code is AuditErrorCode.INVALID_CONTEXT
    assert invalid.value.reference == "published_lesson"


def test_completion_lineage_reconciles_once_and_returns_stable_bounded_graph() -> None:
    service, repository = _service()
    request = ReadKnowledgeCheckCompletionLineageRequest(
        LEARNER_ID,
        "intro-risk-return",
        _event().evidence_id,
        1,
    )
    first = service.read_knowledge_check_completion_lineage(request)
    second = service.read_knowledge_check_completion_lineage(request)

    assert first == second
    assert len(repository.records) == 1
    assert [node.envelope.resource.resource_kind.value for node in first.nodes[:5]] == [
        "completion_evidence",
        "knowledge_check_event",
        "audit_reference",
        "assessment_definition",
        "published_lesson",
    ]
    serialized = json.dumps(first, default=str, ensure_ascii=False)
    assert LEARNER_ID not in serialized
    assert "selected_option" not in serialized
    assert "feedback" not in serialized
    assert "private" not in serialized


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("learner_id", None),
        ("learner_id", 7),
        ("placement_id", None),
        ("placement_id", 7),
        ("evidence_id", None),
        ("evidence_id", 7),
        ("occurrence", "1"),
        ("occurrence", None),
        ("occurrence", True),
        ("occurrence", 1.0),
    ),
)
def test_completion_lineage_rejects_malformed_selectors(
    field: str,
    value: object,
) -> None:
    service, repository = _service()
    request = ReadKnowledgeCheckCompletionLineageRequest(
        LEARNER_ID,
        "intro-risk-return",
        _event().evidence_id,
        1,
    )
    with pytest.raises(AuditError) as invalid:
        service.read_knowledge_check_completion_lineage(
            replace(request, **{field: value})
        )

    assert invalid.value.code is AuditErrorCode.INVALID_CONTEXT
    assert not repository.records


def test_zero_sources_remains_valid_without_a_fixed_fixture_count() -> None:
    service, _repository = _service(lesson=_lesson(sources=()))
    view = service.read_published_lesson_lineage(
        ReadPublishedLessonLineageRequest(
            "intro-risk-return", "1.1.0", PACKAGE_DIGEST
        )
    )
    assert len(view.nodes) == 1
    assert view.edges == ()


def test_wrong_occurrence_missing_retained_record_and_changed_owner_fact_fail_closed() -> None:
    service, repository = _service()
    with pytest.raises(AuditError) as wrong:
        service.read_knowledge_check_completion_lineage(
            ReadKnowledgeCheckCompletionLineageRequest(
                LEARNER_ID, "intro-risk-return", _event().evidence_id, 2
            )
        )
    assert wrong.value.code is AuditErrorCode.INVALID_CONTEXT

    repository.read_assessment_completion_record = lambda **_kwargs: None  # type: ignore[method-assign]
    with pytest.raises(AuditError) as missing:
        service.read_knowledge_check_completion_lineage(
            ReadKnowledgeCheckCompletionLineageRequest(
                LEARNER_ID, "intro-risk-return", _event().evidence_id, 1
            )
        )
    assert missing.value.code is AuditErrorCode.INCONSISTENT_EVIDENCE

    changed_service, _repository = _service(
        lesson=replace(_lesson(), package_digest="8" * 64)
    )
    with pytest.raises(AuditError) as changed:
        changed_service.read_published_lesson_lineage(
            ReadPublishedLessonLineageRequest(
                "intro-risk-return", "1.1.0", PACKAGE_DIGEST
            )
        )
    assert changed.value.code is AuditErrorCode.UNAVAILABLE

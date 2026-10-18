"""Owner public-operation adapters for bounded learning lineage."""

from __future__ import annotations

from datetime import datetime, time, timezone
import hashlib
import json

from financial_ai_academy.modules.content.public import (
    ContentOperations,
    EducationalSource,
    GetPublishedLessonVersionRequest,
)

from ..domain.learning_lineage import ContentLineageFragment
from ..domain.provenance import (
    OwnerModule,
    ProvenanceEnvelope,
    ProvenanceSource,
    RelationKind,
    ResourceKind,
    ResourceReference,
    ValidationStatus,
    validate_envelope,
)


class ContentLearningLineageSource:
    def __init__(self, content: ContentOperations) -> None:
        self._content = content

    def read_lesson(
        self,
        *,
        package_id: str,
        package_version: str,
        package_digest: str,
    ) -> ContentLineageFragment:
        lesson = self._content.get_published_lesson_version(
            GetPublishedLessonVersionRequest(
                package_id=package_id,
                package_version=package_version,
                package_digest=package_digest,
            )
        )
        if (
            lesson.package_id != package_id
            or lesson.package_version != package_version
            or lesson.package_digest != package_digest
        ):
            raise ValueError("Published lesson identity changed during lineage read.")
        sources = tuple(
            _source_envelope(source)
            for source in sorted(lesson.sources, key=lambda item: item.source_id)
        )
        root = validate_envelope(
            ProvenanceEnvelope(
                schema_version="1.0.0",
                resource=ResourceReference(
                    owner_module=OwnerModule.CONTENT,
                    resource_kind=ResourceKind.PUBLISHED_LESSON,
                    resource_id=lesson.package_id,
                    resource_version=lesson.package_version,
                    occurrence=None,
                    integrity_digest=lesson.package_digest,
                    recorded_at=lesson.provenance.published_at,
                    validation_status=ValidationStatus.VALIDATED,
                ),
                producer_id="content.lesson-package",
                producer_version="1.0.0",
                sources=tuple(
                    ProvenanceSource(RelationKind.PUBLISHED_FROM, item.resource)
                    for item in sources
                ),
            )
        )
        return ContentLineageFragment(root, sources)


def _source_envelope(source: EducationalSource) -> ProvenanceEnvelope:
    recorded_at = datetime.combine(
        source.reviewed_on,
        time.min,
        tzinfo=timezone.utc,
    )
    digest = hashlib.sha256(
        json.dumps(
            {
                "source_id": source.source_id,
                "title": source.title,
                "publisher": source.publisher,
                "locator": source.locator,
                "reviewed_on": source.reviewed_on.isoformat(),
                "license_note": source.license_note,
            },
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()
    return validate_envelope(
        ProvenanceEnvelope(
            schema_version="1.0.0",
            resource=ResourceReference(
                owner_module=OwnerModule.CONTENT,
                resource_kind=ResourceKind.EDUCATIONAL_SOURCE,
                resource_id=source.source_id,
                resource_version=source.reviewed_on.isoformat(),
                occurrence=None,
                integrity_digest=digest,
                recorded_at=recorded_at,
                validation_status=ValidationStatus.VALIDATED,
            ),
            producer_id="content.lesson-package",
            producer_version="1.0.0",
            sources=(),
        )
    )


__all__ = ["ContentLearningLineageSource"]

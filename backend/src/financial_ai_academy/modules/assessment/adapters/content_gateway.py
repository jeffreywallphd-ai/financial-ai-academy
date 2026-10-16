"""Assessment adapter over Content's public private-definition query."""

from __future__ import annotations

from financial_ai_academy.modules.content.public import (
    ContentOperations,
    GetPublishedAssessmentDefinitionRequest,
    GetPublishedPracticeDefinitionRequest,
    LessonErrorCode,
    LessonReadError,
)

from ..ports.gateways import (
    DefinitionDocument,
    PlacedAssessmentReference,
    PlacedPracticeReference,
    PracticeDefinitionDocument,
)
from ..public import AssessmentError, AssessmentErrorCode


class PublicContentDefinitionGateway:
    def __init__(self, content: ContentOperations) -> None:
        self._content = content

    def get_exact(
        self, reference: PlacedAssessmentReference
    ) -> DefinitionDocument:
        try:
            value = self._content.get_published_assessment_definition(
                GetPublishedAssessmentDefinitionRequest(
                    package_id=reference.package_id,
                    package_version=reference.package_version,
                    package_digest=reference.package_digest,
                    assessment_id=reference.assessment_id,
                )
            )
        except LessonReadError as error:
            code = (
                AssessmentErrorCode.NOT_FOUND
                if error.code is LessonErrorCode.NOT_FOUND
                else AssessmentErrorCode.UNAVAILABLE
            )
            raise AssessmentError(
                code,
                "The exact knowledge-check definition is unavailable.",
                reference=reference.placement_id,
            ) from error
        return DefinitionDocument(
            package_id=value.package_id,
            package_version=value.package_version,
            package_digest=value.package_digest,
            assessment_id=value.assessment_id,
            schema_version=value.schema_version,
            file_digest=value.file_digest,
            value=value.value,
        )

    def get_practice_exact(
        self, reference: PlacedPracticeReference
    ) -> PracticeDefinitionDocument:
        try:
            value = self._content.get_published_practice_definition(
                GetPublishedPracticeDefinitionRequest(
                    package_id=reference.package_id,
                    package_version=reference.package_version,
                    package_digest=reference.package_digest,
                    practice_id=reference.practice_id,
                )
            )
        except LessonReadError as error:
            code = (
                AssessmentErrorCode.NOT_FOUND
                if error.code is LessonErrorCode.NOT_FOUND
                else AssessmentErrorCode.UNAVAILABLE
            )
            raise AssessmentError(
                code,
                "The exact practice definition is unavailable.",
                reference=reference.placement_id,
            ) from error
        return PracticeDefinitionDocument(
            package_id=value.package_id,
            package_version=value.package_version,
            package_digest=value.package_digest,
            practice_id=value.practice_id,
            schema_version=value.schema_version,
            file_digest=value.file_digest,
            value=value.value,
        )


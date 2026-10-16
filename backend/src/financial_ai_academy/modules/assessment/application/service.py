"""Placed knowledge-check presentation and deterministic submission service."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from datetime import datetime, timezone
from uuid import UUID

from ..domain.models import (
    AssessmentDefinition,
    AssessmentSubmissionCandidate,
    score_single_select,
)
from ..domain.practice import PracticePresentation, PracticePresentationContext
from ..ports.definition_parser import (
    AssessmentDefinitionParserPort,
    DefinitionParsingFailure,
)
from ..ports.gateways import (
    ContentDefinitionGatewayPort,
    CurriculumAssessmentGatewayPort,
    PlacedAssessmentReference,
)
from ..ports.event_parser import (
    AssessmentEventParserPort,
    EventParsingFailure,
)
from ..ports.repositories import (
    AssessmentRepositoryPort,
    KnowledgeCheckAlreadyCompleted,
    SubmissionConflict,
)
from ..ports.practice_definition import (
    PracticeDefinitionFailure,
    PracticeDefinitionPort,
)
from ..ports.system import ClockPort, IdGeneratorPort
from ..public import (
    AssessmentError,
    AssessmentErrorCode,
    KnowledgeCheckOption,
    KnowledgeCheckCompletionEvent,
    KnowledgeCheckPresentation,
    KnowledgeCheckResult,
    OpenPlacedKnowledgeCheckRequest,
    OpenPlacedPracticeRequest,
    ReadCompletedKnowledgeChecksRequest,
    SubmitPlacedKnowledgeCheckRequest,
)


class AssessmentService:
    def __init__(
        self,
        curriculum: CurriculumAssessmentGatewayPort,
        content: ContentDefinitionGatewayPort,
        parser: AssessmentDefinitionParserPort,
        event_parser: AssessmentEventParserPort,
        repository: AssessmentRepositoryPort,
        clock: ClockPort,
        ids: IdGeneratorPort,
        practice_parser: PracticeDefinitionPort | None = None,
    ) -> None:
        self._curriculum = curriculum
        self._content = content
        self._parser = parser
        self._event_parser = event_parser
        self._repository = repository
        self._clock = clock
        self._ids = ids
        self._practice_parser = practice_parser

    def open_placed_knowledge_check(
        self, request: OpenPlacedKnowledgeCheckRequest
    ) -> KnowledgeCheckPresentation:
        reference, definition = self._resolve(request.placement_id)
        return self._presentation(reference, definition)

    def open_placed_practice(
        self, request: OpenPlacedPracticeRequest
    ) -> PracticePresentation:
        parser = self._practice_parser
        if parser is None:
            raise AssessmentError(
                AssessmentErrorCode.UNAVAILABLE,
                "Practice activities are unavailable.",
                reference=request.placement_id,
            )
        try:
            reference = self._curriculum.resolve_practice(
                request.placement_id
            )
            document = self._content.get_practice_exact(reference)
        except AssessmentError:
            raise
        except Exception as error:
            raise AssessmentError(
                AssessmentErrorCode.UNAVAILABLE,
                "The exact practice definition is unavailable.",
                reference=request.placement_id,
            ) from error
        if (
            document.package_id,
            document.package_version,
            document.package_digest,
            document.practice_id,
        ) != (
            reference.package_id,
            reference.package_version,
            reference.package_digest,
            reference.practice_id,
        ):
            raise self._stale_practice("definition")
        try:
            definition = parser.parse(document.value)
        except PracticeDefinitionFailure as error:
            public_code = (
                AssessmentErrorCode.UNSUPPORTED_VERSION
                if "unsupported" in error.code
                else AssessmentErrorCode.INVALID_DEFINITION
            )
            raise AssessmentError(
                public_code,
                "The practice definition was rejected.",
                reference=error.reference,
                diagnostic_code=error.code,
            ) from error
        if (
            definition.practice_id,
            definition.practice_version,
            definition.definition_digest,
        ) != (
            reference.practice_id,
            reference.practice_version,
            reference.definition_digest,
        ):
            raise self._stale_practice("practice")
        try:
            return parser.project(
                definition,
                PracticePresentationContext(
                    placement_id=reference.placement_id,
                    package_id=reference.package_id,
                    package_version=reference.package_version,
                    package_digest=reference.package_digest,
                ),
            )
        except PracticeDefinitionFailure as error:
            raise AssessmentError(
                AssessmentErrorCode.INVALID_DEFINITION,
                "The practice definition was rejected.",
                reference=error.reference,
                diagnostic_code=error.code,
            ) from error

    def submit_placed_knowledge_check(
        self, request: SubmitPlacedKnowledgeCheckRequest
    ) -> KnowledgeCheckResult:
        self._validate_uuid(request.learner_id, learner=True)
        self._validate_uuid(request.submission_id, learner=False)
        reference, definition = self._resolve(request.placement_id)
        presentation = self._presentation(reference, definition)
        self._validate_submission(request, presentation)
        try:
            outcome = score_single_select(
                definition, request.selected_option_id
            )
        except ValueError as error:
            raise AssessmentError(
                AssessmentErrorCode.UNKNOWN_OPTION,
                "The selected option is not available for this knowledge check.",
                reference="selected_option_id",
                diagnostic_code="assessment.unknown_option",
            ) from error

        submitted_at = self._server_time()
        result = KnowledgeCheckResult(
            attempt_id=self._ids.new(),
            evidence_id=self._ids.new(),
            learner_id=request.learner_id,
            submission_id=request.submission_id,
            placement_id=request.placement_id,
            package_id=request.package_id,
            package_version=request.package_version,
            package_digest=request.package_digest,
            assessment_id=request.assessment_id,
            assessment_version=request.assessment_version,
            definition_digest=request.definition_digest,
            item_id=request.item_id,
            item_version=request.item_version,
            scoring_policy_id=request.scoring_policy_id,
            scoring_policy_version=request.scoring_policy_version,
            selected_option_id=request.selected_option_id,
            score=outcome.score,
            max_score=outcome.max_score,
            correct=outcome.correct,
            feedback=outcome.feedback,
            submitted_at=submitted_at,
        )
        event_id = self._ids.new()
        candidate = AssessmentSubmissionCandidate(
            result=result,
            request_fingerprint=self._fingerprint(request),
            event_id=event_id,
            event=self._completion_event(event_id, result),
            occurred_at=submitted_at,
        )
        try:
            stored, _created = self._repository.record_submission(candidate)
        except SubmissionConflict as error:
            raise AssessmentError(
                AssessmentErrorCode.CONFLICT,
                "The submission identity was already used for different input.",
                reference="submission_id",
                diagnostic_code="assessment.conflicting_submission",
            ) from error
        except KnowledgeCheckAlreadyCompleted as error:
            raise AssessmentError(
                AssessmentErrorCode.ALREADY_COMPLETED,
                "This knowledge check has already been completed.",
                reference=request.placement_id,
                diagnostic_code="assessment.already_completed",
            ) from error
        except AssessmentError:
            raise
        except Exception as error:
            raise AssessmentError(
                AssessmentErrorCode.UNAVAILABLE,
                "Assessment evidence storage is unavailable.",
                reference=request.placement_id,
            ) from error
        return stored

    def read_completed_knowledge_checks(
        self, request: ReadCompletedKnowledgeChecksRequest
    ) -> tuple[KnowledgeCheckCompletionEvent, ...]:
        self._validate_uuid(request.learner_id, learner=True)
        if not self._valid_identifier(request.placement_id):
            raise AssessmentError(
                AssessmentErrorCode.INVALID_SUBMISSION,
                "The lesson placement identity is invalid.",
                reference="placement_id",
            )
        try:
            documents = self._repository.list_completion_event_documents(
                learner_id=request.learner_id,
                placement_id=request.placement_id,
            )
            events = tuple(
                self._event_parser.parse(document) for document in documents
            )
        except EventParsingFailure as error:
            raise AssessmentError(
                AssessmentErrorCode.UNAVAILABLE,
                "Assessment completion evidence is unavailable.",
                reference=error.reference,
                diagnostic_code=error.code,
            ) from error
        except AssessmentError:
            raise
        except Exception as error:
            raise AssessmentError(
                AssessmentErrorCode.UNAVAILABLE,
                "Assessment completion evidence is unavailable.",
                reference=request.placement_id,
            ) from error
        seen: set[str] = set()
        for event in events:
            if (
                event.event_id in seen
                or event.learner_id != request.learner_id
                or event.placement_id != request.placement_id
            ):
                raise AssessmentError(
                    AssessmentErrorCode.UNAVAILABLE,
                    "Assessment completion evidence is unavailable.",
                    reference="event",
                    diagnostic_code="assessment.inconsistent_event",
                )
            seen.add(event.event_id)
        return tuple(sorted(events, key=lambda event: (
            event.occurred_at, event.event_id
        )))

    def _resolve(
        self, placement_id: str
    ) -> tuple[PlacedAssessmentReference, AssessmentDefinition]:
        try:
            reference = self._curriculum.resolve(placement_id)
            document = self._content.get_exact(reference)
        except AssessmentError:
            raise
        except Exception as error:
            raise AssessmentError(
                AssessmentErrorCode.UNAVAILABLE,
                "The exact knowledge-check definition is unavailable.",
                reference=placement_id,
            ) from error
        if (
            document.package_id,
            document.package_version,
            document.package_digest,
            document.assessment_id,
        ) != (
            reference.package_id,
            reference.package_version,
            reference.package_digest,
            reference.assessment_id,
        ):
            raise self._stale("definition")
        try:
            definition = self._parser.parse(document.value)
        except DefinitionParsingFailure as error:
            public_code = (
                AssessmentErrorCode.UNSUPPORTED_VERSION
                if "unsupported" in error.code
                else AssessmentErrorCode.INVALID_DEFINITION
            )
            raise AssessmentError(
                public_code,
                "The knowledge-check definition was rejected.",
                reference=error.reference,
                diagnostic_code=error.code,
            ) from error
        expected = (
            reference.assessment_id,
            reference.assessment_version,
            reference.definition_digest,
            reference.item_id,
            reference.item_version,
            reference.scoring_policy_id,
            reference.scoring_policy_version,
        )
        actual = (
            definition.assessment_id,
            definition.assessment_version,
            definition.definition_digest,
            definition.item_id,
            definition.item_version,
            definition.scoring_policy_id,
            definition.scoring_policy_version,
        )
        if actual != expected:
            raise self._stale("assessment")
        return reference, definition

    @staticmethod
    def _presentation(
        reference: PlacedAssessmentReference,
        definition: AssessmentDefinition,
    ) -> KnowledgeCheckPresentation:
        return KnowledgeCheckPresentation(
            placement_id=reference.placement_id,
            package_id=reference.package_id,
            package_version=reference.package_version,
            package_digest=reference.package_digest,
            assessment_id=definition.assessment_id,
            assessment_version=definition.assessment_version,
            definition_digest=definition.definition_digest,
            item_type=definition.item_type,
            item_id=definition.item_id,
            item_version=definition.item_version,
            scoring_policy_id=definition.scoring_policy_id,
            scoring_policy_version=definition.scoring_policy_version,
            prompt=definition.prompt,
            options=tuple(
                KnowledgeCheckOption(option.option_id, option.label)
                for option in definition.options
            ),
        )

    @staticmethod
    def _validate_submission(
        request: SubmitPlacedKnowledgeCheckRequest,
        presentation: KnowledgeCheckPresentation,
    ) -> None:
        fields = (
            "placement_id",
            "package_id",
            "package_version",
            "package_digest",
            "assessment_id",
            "assessment_version",
            "definition_digest",
            "item_id",
            "item_version",
            "scoring_policy_id",
            "scoring_policy_version",
        )
        for field in fields:
            if getattr(request, field) != getattr(presentation, field):
                raise AssessmentService._stale(field)

    @staticmethod
    def _validate_uuid(value: str, *, learner: bool) -> None:
        try:
            UUID(value)
        except (ValueError, AttributeError) as error:
            code = (
                AssessmentErrorCode.UNAUTHORIZED_CONTEXT
                if learner
                else AssessmentErrorCode.INVALID_SUBMISSION
            )
            reference = "learner" if learner else "submission_id"
            raise AssessmentError(
                code,
                (
                    "Learner context is not authorized."
                    if learner
                    else "Submission identity is invalid."
                ),
                reference=reference,
            ) from error

    @staticmethod
    def _valid_identifier(value: str) -> bool:
        if not 3 <= len(value) <= 64 or not value[0].isalnum():
            return False
        return all(character.islower() or character.isdigit() or character in "._-" for character in value)

    def _server_time(self) -> datetime:
        value = self._clock.now()
        if value.tzinfo is None:
            raise AssessmentError(
                AssessmentErrorCode.UNAVAILABLE,
                "Assessment time authority is unavailable.",
            )
        return value.astimezone(timezone.utc)

    @staticmethod
    def _fingerprint(request: SubmitPlacedKnowledgeCheckRequest) -> str:
        value = json.dumps(
            asdict(request), sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        return hashlib.sha256(value).hexdigest()

    @staticmethod
    def _timestamp(value: datetime) -> str:
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

    @classmethod
    def _completion_event(
        cls, event_id: str, result: KnowledgeCheckResult
    ) -> dict[str, object]:
        timestamp = cls._timestamp(result.submitted_at)
        return {
            "schema_version": "1.0.0",
            "event_id": event_id,
            "event_type": "assessment.knowledge-check.completed",
            "event_version": "1.0.0",
            "owner": "assessment",
            "occurred_at": timestamp,
            "idempotency_key": result.evidence_id,
            "aggregate": {
                "aggregate_type": "knowledge_check_attempt",
                "aggregate_id": result.attempt_id,
            },
            "source": {"evidence_id": result.evidence_id},
            "payload": {
                "learner_id": result.learner_id,
                "placement_id": result.placement_id,
                "package_id": result.package_id,
                "package_version": result.package_version,
                "package_digest": result.package_digest,
                "assessment_id": result.assessment_id,
                "assessment_version": result.assessment_version,
                "definition_digest": result.definition_digest,
                "item_id": result.item_id,
                "item_version": result.item_version,
                "scoring_policy_id": result.scoring_policy_id,
                "scoring_policy_version": result.scoring_policy_version,
                "score": result.score,
                "max_score": result.max_score,
                "completed_at": timestamp,
            },
        }

    @staticmethod
    def _stale(reference: str) -> AssessmentError:
        return AssessmentError(
            AssessmentErrorCode.STALE_REFERENCE,
            "Knowledge-check version references do not match.",
            reference=reference,
            diagnostic_code="assessment.stale_reference",
        )

    @staticmethod
    def _stale_practice(reference: str) -> AssessmentError:
        return AssessmentError(
            AssessmentErrorCode.STALE_REFERENCE,
            "Practice version references do not match.",
            reference=reference,
            diagnostic_code="assessment.practice.stale_reference",
        )

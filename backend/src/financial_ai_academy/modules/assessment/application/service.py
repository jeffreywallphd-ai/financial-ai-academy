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
from ..domain.practice import (
    OrderedPracticeCompletionEvent,
    PracticeDefinition,
    PracticeDraft,
    PracticePresentation,
    PracticePresentationContext,
    PracticeResult,
    PracticeScoringError,
    PracticeRetryState,
    PracticeScope,
    score_practice,
)
from ..ports.definition_parser import (
    AssessmentDefinitionParserPort,
    DefinitionParsingFailure,
)
from ..ports.gateways import (
    ContentDefinitionGatewayPort,
    CurriculumAssessmentGatewayPort,
    PlacedAssessmentReference,
    PlacedPracticeReference,
)
from ..ports.event_parser import (
    AssessmentEventParserPort,
    EventParsingFailure,
)
from ..ports.repositories import (
    AssessmentRepositoryPort,
    KnowledgeCheckAlreadyCompleted,
    PracticeAlreadyCompleted,
    PracticeAttemptLimitReached,
    PracticeDraftConflict,
    PracticeSubmissionConflict,
    ProjectSubmissionConflict,
    ProjectSubmissionRecordCandidate,
    SubmissionConflict,
)
from ..ports.project_submission import (
    ProjectSubmissionContract,
    ProjectSubmissionContractFailure,
)
from ..ports.project_submission_gateways import (
    ProjectSubmissionSourceFailure,
    ProjectSubmissionSourcePort,
)
from ..ports.practice_definition import (
    PracticeDefinitionFailure,
    PracticeDefinitionPort,
)
from ..ports.practice_submission import (
    PracticeSubmissionFailure,
    PracticeSubmissionPort,
)
from ..ports.practice_progress import (
    PracticeProgressContractPort,
    PracticeProgressFailure,
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
    OpenProjectSubmissionCandidateRequest,
    ReadCompletedPracticesRequest,
    ReadCompletedKnowledgeChecksRequest,
    ReadPlacedPracticeProgressRequest,
    ReadProjectCompletionEvidenceRequest,
    ReadProjectCompletionHistoryRequest,
    SavePlacedPracticeDraftRequest,
    ProjectSubmissionOutcome,
    SubmitProjectSnapshotRequest,
    PracticeHistorySource,
    PracticeHistorySourceAttempt,
    PracticeHistorySourceItem,
    SubmitPlacedKnowledgeCheckRequest,
    SubmitPlacedPracticeRequest,
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
        practice_submission_parser: PracticeSubmissionPort | None = None,
        practice_progress_contract: PracticeProgressContractPort | None = None,
        project_submission_source: ProjectSubmissionSourcePort | None = None,
        project_submission_contract: ProjectSubmissionContract | None = None,
    ) -> None:
        self._curriculum = curriculum
        self._content = content
        self._parser = parser
        self._event_parser = event_parser
        self._repository = repository
        self._clock = clock
        self._ids = ids
        self._practice_parser = practice_parser
        self._practice_submission_parser = practice_submission_parser
        self._practice_progress_contract = practice_progress_contract
        self._project_submission_source = project_submission_source
        self._project_submission_contract = project_submission_contract

    def open_project_submission_candidate(
        self, request: OpenProjectSubmissionCandidateRequest
    ):
        self._validate_uuid(request.learner_id, learner=True)
        source = self._require_project_submission_source(request.project_id)
        try:
            return source.resolve(
                learner_id=request.learner_id,
                project_id=request.project_id,
                snapshot_id=request.snapshot_id,
            )
        except ProjectSubmissionSourceFailure as error:
            raise self._project_source_error(error) from error
        except AssessmentError:
            raise
        except Exception as error:
            raise AssessmentError(
                AssessmentErrorCode.UNAVAILABLE,
                "Project submission facts are unavailable.",
                reference=request.project_id,
            ) from error

    def submit_project_snapshot(
        self, request: SubmitProjectSnapshotRequest
    ) -> ProjectSubmissionOutcome:
        contract = self._require_project_submission_contract(request.project_id)
        candidate = self.open_project_submission_candidate(
            OpenProjectSubmissionCandidateRequest(
                learner_id=request.learner_id,
                project_id=request.project_id,
                snapshot_id=request.snapshot_id,
            )
        )
        try:
            submission = contract.parse_submission(request.submission)
            validation = contract.validate(candidate, submission)
        except ProjectSubmissionContractFailure as error:
            raise AssessmentError(
                AssessmentErrorCode.INVALID_SUBMISSION,
                "The Project submission was rejected.",
                reference=error.reference,
                diagnostic_code=error.code,
            ) from error
        if validation.accepted is None:
            return ProjectSubmissionOutcome(validation=validation, evidence=None)
        try:
            evidence, _created = self._repository.record_project_submission(
                ProjectSubmissionRecordCandidate(
                    accepted=validation.accepted,
                    learner_id=request.learner_id,
                    evidence_id=self._ids.new(),
                    event_id=self._ids.new(),
                    submitted_at=self._server_time(),
                )
            )
            return ProjectSubmissionOutcome(validation=validation, evidence=evidence)
        except ProjectSubmissionConflict as error:
            raise AssessmentError(
                AssessmentErrorCode.CONFLICT,
                "The submission identity was already used for different input.",
                reference="submission_id",
                diagnostic_code="assessment.project.conflicting_submission",
            ) from error
        except ProjectSubmissionContractFailure as error:
            raise AssessmentError(
                AssessmentErrorCode.UNAVAILABLE,
                "Project evidence storage is unavailable.",
                reference=error.reference,
                diagnostic_code=error.code,
            ) from error
        except AssessmentError:
            raise
        except Exception as error:
            raise AssessmentError(
                AssessmentErrorCode.UNAVAILABLE,
                "Project evidence storage is unavailable.",
                reference=request.project_id,
            ) from error

    def read_project_completion_evidence(
        self, request: ReadProjectCompletionEvidenceRequest
    ):
        history = self.read_project_completion_history(
            ReadProjectCompletionHistoryRequest(
                learner_id=request.learner_id,
                project_id=request.project_id,
            )
        )
        for evidence in history.items:
            if evidence.accepted.submission.submission_id == request.submission_id:
                return evidence
        raise AssessmentError(
            AssessmentErrorCode.NOT_FOUND,
            "Project evidence was not found.",
            reference=request.submission_id,
        )

    def read_project_completion_history(
        self, request: ReadProjectCompletionHistoryRequest
    ):
        self._validate_uuid(request.learner_id, learner=True)
        contract = self._require_project_submission_contract(request.project_id)
        try:
            evidence = self._repository.list_project_completion_evidence(
                learner_id=request.learner_id,
                project_id=request.project_id,
            )
            if not evidence:
                raise AssessmentError(
                    AssessmentErrorCode.NOT_FOUND,
                    "Project evidence was not found.",
                    reference=request.project_id,
                )
            return contract.project_history(evidence)
        except ProjectSubmissionContractFailure as error:
            raise AssessmentError(
                AssessmentErrorCode.UNAVAILABLE,
                "Project evidence history is unavailable.",
                reference=error.reference,
                diagnostic_code=error.code,
            ) from error
        except AssessmentError:
            raise
        except Exception as error:
            raise AssessmentError(
                AssessmentErrorCode.UNAVAILABLE,
                "Project evidence history is unavailable.",
                reference=request.project_id,
            ) from error

    def open_placed_knowledge_check(
        self, request: OpenPlacedKnowledgeCheckRequest
    ) -> KnowledgeCheckPresentation:
        reference, definition = self._resolve(request.placement_id)
        return self._presentation(reference, definition)

    def open_placed_practice(
        self, request: OpenPlacedPracticeRequest
    ) -> PracticePresentation:
        reference, definition = self._resolve_practice(request.placement_id)
        try:
            assert self._practice_parser is not None
            return self._practice_parser.project(
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

    def submit_placed_practice(
        self, request: SubmitPlacedPracticeRequest
    ) -> PracticeResult:
        self._validate_uuid(request.learner_id, learner=True)
        submission_parser = self._practice_submission_parser
        if submission_parser is None:
            raise AssessmentError(
                AssessmentErrorCode.UNAVAILABLE,
                "Practice submission is unavailable.",
                reference=request.placement_id,
            )
        reference, definition = self._resolve_practice(request.placement_id)
        submitted_at = self._server_time()
        try:
            candidate = submission_parser.parse_and_score(
                request.submission,
                definition,
                PracticePresentationContext(
                    placement_id=reference.placement_id,
                    package_id=reference.package_id,
                    package_version=reference.package_version,
                    package_digest=reference.package_digest,
                ),
                learner_id=request.learner_id,
                attempt_id=self._ids.new(),
                evidence_id=self._ids.new(),
                event_id=self._ids.new(),
                submitted_at=submitted_at,
            )
        except PracticeSubmissionFailure as error:
            if error.code == "assessment.practice.unsupported_version":
                code = AssessmentErrorCode.UNSUPPORTED_VERSION
            elif error.code == "assessment.practice.stale_reference":
                code = AssessmentErrorCode.STALE_REFERENCE
            elif error.code == "assessment.practice.invalid_server_metadata":
                code = AssessmentErrorCode.UNAVAILABLE
            else:
                code = AssessmentErrorCode.INVALID_SUBMISSION
            raise AssessmentError(
                code,
                "The practice submission was rejected.",
                reference=error.reference,
                diagnostic_code=error.code,
            ) from error
        try:
            stored, _created = self._repository.record_practice_submission(
                candidate,
                max_attempts=definition.attempt_policy.max_attempts,
            )
        except PracticeSubmissionConflict as error:
            raise AssessmentError(
                AssessmentErrorCode.CONFLICT,
                "The submission identity was already used for different input.",
                reference="submission_id",
                diagnostic_code="assessment.practice.conflicting_submission",
            ) from error
        except PracticeAlreadyCompleted as error:
            raise AssessmentError(
                AssessmentErrorCode.ALREADY_COMPLETED,
                "This practice activity has already been completed.",
                reference=request.placement_id,
                diagnostic_code="assessment.practice.already_completed",
            ) from error
        except PracticeAttemptLimitReached as error:
            raise AssessmentError(
                AssessmentErrorCode.ATTEMPT_LIMIT_REACHED,
                "No more attempts are available for this practice activity.",
                reference=request.placement_id,
                diagnostic_code="assessment.practice.attempt_limit_reached",
            ) from error
        except AssessmentError:
            raise
        except Exception as error:
            raise AssessmentError(
                AssessmentErrorCode.UNAVAILABLE,
                "Practice evidence storage is unavailable.",
                reference=request.placement_id,
            ) from error
        return stored

    def read_placed_practice_draft(
        self, request: ReadPlacedPracticeProgressRequest
    ) -> PracticeDraft | None:
        self._validate_uuid(request.learner_id, learner=True)
        _reference, definition, scope = self._resolve_practice_progress(
            request.placement_id
        )
        if not definition.attempt_policy.resume_allowed:
            raise AssessmentError(
                AssessmentErrorCode.UNAVAILABLE,
                "Saved progress is unavailable for this practice activity.",
                reference=request.placement_id,
            )
        try:
            return self._repository.read_practice_draft(
                learner_id=request.learner_id,
                scope=scope,
            )
        except AssessmentError:
            raise
        except Exception as error:
            raise AssessmentError(
                AssessmentErrorCode.UNAVAILABLE,
                "Saved practice progress is unavailable.",
                reference=request.placement_id,
            ) from error

    def save_placed_practice_draft(
        self, request: SavePlacedPracticeDraftRequest
    ) -> PracticeDraft:
        self._validate_uuid(request.learner_id, learner=True)
        progress = self._practice_progress_contract
        if progress is None:
            raise AssessmentError(
                AssessmentErrorCode.UNAVAILABLE,
                "Saving practice progress is unavailable.",
                reference=request.placement_id,
            )
        reference, definition, _scope = self._resolve_practice_progress(
            request.placement_id
        )
        if not definition.attempt_policy.resume_allowed:
            raise AssessmentError(
                AssessmentErrorCode.UNAVAILABLE,
                "Saving practice progress is unavailable.",
                reference=request.placement_id,
            )
        try:
            draft = progress.parse_draft_save(
                request.draft,
                definition,
                self._practice_context(reference),
            )
        except PracticeProgressFailure as error:
            code = (
                AssessmentErrorCode.UNSUPPORTED_VERSION
                if error.code == "assessment.practice.unsupported_version"
                else AssessmentErrorCode.STALE_REFERENCE
                if error.code == "assessment.practice.stale_reference"
                else AssessmentErrorCode.INVALID_SUBMISSION
            )
            raise AssessmentError(
                code,
                "Saved practice progress was rejected.",
                reference=error.reference,
                diagnostic_code=error.code,
            ) from error
        try:
            return self._repository.save_practice_draft(
                learner_id=request.learner_id,
                draft=draft,
                saved_at=self._server_time(),
            )
        except PracticeDraftConflict as error:
            raise AssessmentError(
                AssessmentErrorCode.CONFLICT,
                "Saved practice progress changed in another session.",
                reference="expected_revision",
                diagnostic_code="assessment.practice.draft_conflict",
            ) from error
        except AssessmentError:
            raise
        except Exception as error:
            raise AssessmentError(
                AssessmentErrorCode.UNAVAILABLE,
                "Saving practice progress is unavailable.",
                reference=request.placement_id,
            ) from error

    def read_placed_practice_retry_state(
        self, request: ReadPlacedPracticeProgressRequest
    ) -> PracticeRetryState:
        self._validate_uuid(request.learner_id, learner=True)
        _reference, definition, scope = self._resolve_practice_progress(
            request.placement_id
        )
        try:
            used = self._repository.count_practice_attempts(
                learner_id=request.learner_id,
                scope=scope,
            )
        except Exception as error:
            raise AssessmentError(
                AssessmentErrorCode.UNAVAILABLE,
                "Practice attempt availability is unavailable.",
                reference=request.placement_id,
            ) from error
        maximum = definition.attempt_policy.max_attempts
        if used < 0 or used > maximum:
            raise AssessmentError(
                AssessmentErrorCode.UNAVAILABLE,
                "Practice attempt availability is unavailable.",
                reference=request.placement_id,
                diagnostic_code="assessment.practice.invalid_retry_state",
            )
        remaining = maximum - used
        return PracticeRetryState(
            scope=scope,
            attempts_used=used,
            max_attempts=maximum,
            attempts_remaining=remaining,
            can_retry=remaining > 0,
            state="available" if remaining > 0 else "exhausted",
        )

    def read_completed_practices(
        self, request: ReadCompletedPracticesRequest
    ) -> tuple[OrderedPracticeCompletionEvent, ...]:
        self._validate_uuid(request.learner_id, learner=True)
        progress = self._practice_progress_contract
        if progress is None:
            raise AssessmentError(
                AssessmentErrorCode.UNAVAILABLE,
                "Practice history is unavailable.",
                reference=request.placement_id,
            )
        _reference, _definition, scope = self._resolve_practice_progress(
            request.placement_id
        )
        try:
            stored = self._repository.list_practice_completion_event_documents(
                learner_id=request.learner_id,
                scope=scope,
            )
            ordered_items: list[OrderedPracticeCompletionEvent] = []
            for item in stored:
                event = progress.parse_completion_event(item.document)
                if (
                    event.event_id != item.event_id
                    or event.attempt_id != item.attempt_id
                    or event.evidence_id != item.evidence_id
                    or event.submission_id != item.submission_id
                ):
                    raise PracticeProgressFailure(
                        "assessment.practice.inconsistent_event", "event"
                    )
                ordered_items.append(
                    OrderedPracticeCompletionEvent(
                        attempt_order=item.attempt_order,
                        event=event,
                    )
                )
            ordered = tuple(ordered_items)
        except PracticeProgressFailure as error:
            raise AssessmentError(
                AssessmentErrorCode.UNAVAILABLE,
                "Practice history is unavailable.",
                reference=error.reference,
                diagnostic_code=error.code,
            ) from error
        except AssessmentError:
            raise
        except Exception as error:
            raise AssessmentError(
                AssessmentErrorCode.UNAVAILABLE,
                "Practice history is unavailable.",
                reference=request.placement_id,
            ) from error
        seen_events: set[str] = set()
        for expected_order, item in enumerate(ordered, start=1):
            event = item.event
            if (
                item.attempt_order != expected_order
                or event.event_id in seen_events
                or event.learner_id != request.learner_id
                or event.scope != scope
            ):
                raise AssessmentError(
                    AssessmentErrorCode.UNAVAILABLE,
                    "Practice history is unavailable.",
                    reference="event",
                    diagnostic_code="assessment.practice.inconsistent_event",
                )
            seen_events.add(event.event_id)
        return ordered

    def read_practice_history_source(
        self, request: ReadCompletedPracticesRequest
    ) -> PracticeHistorySource:
        self._validate_uuid(request.learner_id, learner=True)
        progress = self._practice_progress_contract
        if progress is None:
            raise AssessmentError(
                AssessmentErrorCode.UNAVAILABLE,
                "Practice history is unavailable.",
                reference=request.placement_id,
            )
        _reference, definition, scope = self._resolve_practice_progress(
            request.placement_id
        )
        try:
            stored = self._repository.list_practice_completion_event_documents(
                learner_id=request.learner_id,
                scope=scope,
            )
            values: list[PracticeHistorySourceAttempt] = []
            seen_events: set[str] = set()
            for expected_order, item in enumerate(stored, start=1):
                event = progress.parse_completion_event(item.document)
                result = item.result
                if result is None:
                    raise PracticeProgressFailure(
                        "assessment.practice.inconsistent_event", "result"
                    )
                try:
                    rescored = score_practice(
                        definition,
                        tuple(outcome.response for outcome in result.item_results),
                    )
                except PracticeScoringError as error:
                    raise PracticeProgressFailure(
                        "assessment.practice.inconsistent_event", error.reference
                    ) from error
                if (
                    item.attempt_order != expected_order
                    or event.event_id != item.event_id
                    or not (
                        event.attempt_id == item.attempt_id == result.attempt_id
                    )
                    or not (
                        event.evidence_id == item.evidence_id == result.evidence_id
                    )
                    or not (
                        event.submission_id
                        == item.submission_id
                        == result.submission_id
                    )
                    or event.event_id in seen_events
                    or event.learner_id != request.learner_id
                    or result.learner_id != request.learner_id
                    or event.scope != scope
                    or self._result_scope(result) != scope
                    or event.score != result.score
                    or event.max_score != result.max_score
                    or event.outcome != result.outcome
                    or event.completed_at != result.submitted_at
                    or len(event.item_scores) != len(result.item_results)
                    or result.score != rescored.score
                    or result.max_score != rescored.max_score
                    or result.outcome != rescored.outcome
                    or result.review_reference_ids
                    != rescored.review_reference_ids
                    or result.item_results != rescored.item_results
                ):
                    raise PracticeProgressFailure(
                        "assessment.practice.inconsistent_event", "event"
                    )
                summaries: list[PracticeHistorySourceItem] = []
                for score, outcome in zip(
                    event.item_scores, result.item_results, strict=True
                ):
                    response = outcome.response
                    if (
                        score.item_id != response.item_id
                        or score.item_version != response.item_version
                        or score.item_type != response.item_type
                        or score.scoring_policy_id != response.scoring_policy_id
                        or score.scoring_policy_version
                        != response.scoring_policy_version
                        or score.score != outcome.score
                        or score.max_score != outcome.max_score
                        or outcome.correct
                        != (outcome.score == outcome.max_score)
                    ):
                        raise PracticeProgressFailure(
                            "assessment.practice.inconsistent_event", "item"
                        )
                    summaries.append(
                        PracticeHistorySourceItem(
                            item_id=score.item_id,
                            item_version=score.item_version,
                            item_type=score.item_type,
                            scoring_policy_id=score.scoring_policy_id,
                            scoring_policy_version=score.scoring_policy_version,
                            score=score.score,
                            max_score=score.max_score,
                            correct=outcome.correct,
                            review_reference_ids=(
                                ()
                                if outcome.correct
                                else outcome.feedback.review_reference_ids
                            ),
                        )
                    )
                seen_events.add(event.event_id)
                values.append(
                    PracticeHistorySourceAttempt(
                        attempt_order=item.attempt_order,
                        event_id=event.event_id,
                        attempt_id=event.attempt_id,
                        evidence_id=event.evidence_id,
                        learner_id=event.learner_id,
                        submission_id=event.submission_id,
                        placement_id=scope.placement_id,
                        package_id=scope.package_id,
                        package_version=scope.package_version,
                        package_digest=scope.package_digest,
                        definition_digest=scope.definition_digest,
                        practice_id=scope.practice_id,
                        practice_version=scope.practice_version,
                        attempt_policy_id=scope.attempt_policy_id,
                        attempt_policy_version=scope.attempt_policy_version,
                        score=event.score,
                        max_score=event.max_score,
                        outcome=event.outcome,
                        item_summaries=tuple(summaries),
                        completed_at=event.completed_at,
                    )
                )
            return PracticeHistorySource(
                learner_id=request.learner_id,
                placement_id=scope.placement_id,
                package_id=scope.package_id,
                package_version=scope.package_version,
                package_digest=scope.package_digest,
                definition_digest=scope.definition_digest,
                practice_id=scope.practice_id,
                practice_version=scope.practice_version,
                attempt_policy_id=scope.attempt_policy_id,
                attempt_policy_version=scope.attempt_policy_version,
                attempts=tuple(values),
            )
        except PracticeProgressFailure as error:
            raise AssessmentError(
                AssessmentErrorCode.UNAVAILABLE,
                "Practice history is unavailable.",
                reference=error.reference,
                diagnostic_code=error.code,
            ) from error
        except AssessmentError:
            raise
        except Exception as error:
            raise AssessmentError(
                AssessmentErrorCode.UNAVAILABLE,
                "Practice history is unavailable.",
                reference=request.placement_id,
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

    def _resolve_practice(
        self, placement_id: str
    ) -> tuple[PlacedPracticeReference, PracticeDefinition]:
        parser = self._practice_parser
        if parser is None:
            raise AssessmentError(
                AssessmentErrorCode.UNAVAILABLE,
                "Practice activities are unavailable.",
                reference=placement_id,
            )
        try:
            reference = self._curriculum.resolve_practice(placement_id)
            document = self._content.get_practice_exact(reference)
        except AssessmentError:
            raise
        except Exception as error:
            raise AssessmentError(
                AssessmentErrorCode.UNAVAILABLE,
                "The exact practice definition is unavailable.",
                reference=placement_id,
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
        return reference, definition

    def _resolve_practice_progress(
        self, placement_id: str
    ) -> tuple[PlacedPracticeReference, PracticeDefinition, PracticeScope]:
        reference, definition = self._resolve_practice(placement_id)
        return reference, definition, self._practice_scope(reference, definition)

    @staticmethod
    def _practice_context(
        reference: PlacedPracticeReference,
    ) -> PracticePresentationContext:
        return PracticePresentationContext(
            placement_id=reference.placement_id,
            package_id=reference.package_id,
            package_version=reference.package_version,
            package_digest=reference.package_digest,
        )

    @staticmethod
    def _practice_scope(
        reference: PlacedPracticeReference,
        definition: PracticeDefinition,
    ) -> PracticeScope:
        return PracticeScope(
            placement_id=reference.placement_id,
            package_id=reference.package_id,
            package_version=reference.package_version,
            package_digest=reference.package_digest,
            definition_digest=definition.definition_digest,
            practice_id=definition.practice_id,
            practice_version=definition.practice_version,
            attempt_policy_id=definition.attempt_policy.policy_id,
            attempt_policy_version=definition.attempt_policy.policy_version,
        )

    @staticmethod
    def _result_scope(result: PracticeResult) -> PracticeScope:
        return PracticeScope(
            placement_id=result.placement_id,
            package_id=result.package_id,
            package_version=result.package_version,
            package_digest=result.package_digest,
            definition_digest=result.definition_digest,
            practice_id=result.practice_id,
            practice_version=result.practice_version,
            attempt_policy_id=result.attempt_policy_id,
            attempt_policy_version=result.attempt_policy_version,
        )

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

    def _require_project_submission_source(
        self, reference: str
    ) -> ProjectSubmissionSourcePort:
        if self._project_submission_source is None:
            raise AssessmentError(
                AssessmentErrorCode.UNAVAILABLE,
                "Project submission facts are unavailable.",
                reference=reference,
            )
        return self._project_submission_source

    def _require_project_submission_contract(
        self, reference: str
    ) -> ProjectSubmissionContract:
        if self._project_submission_contract is None:
            raise AssessmentError(
                AssessmentErrorCode.UNAVAILABLE,
                "Project submission is unavailable.",
                reference=reference,
            )
        return self._project_submission_contract

    @staticmethod
    def _project_source_error(error: ProjectSubmissionSourceFailure) -> AssessmentError:
        if error.code == "assessment.project.not_found":
            code = AssessmentErrorCode.NOT_FOUND
        elif error.code == "assessment.project.stale_source":
            code = AssessmentErrorCode.STALE_REFERENCE
        elif error.code == "assessment.project.invalid_source":
            code = AssessmentErrorCode.INVALID_DEFINITION
        else:
            code = AssessmentErrorCode.UNAVAILABLE
        return AssessmentError(
            code,
            "Project submission facts are unavailable.",
            reference=error.reference,
            diagnostic_code=error.code,
        )

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

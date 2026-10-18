"""Rebuild and open exact lesson-completion projections."""

from __future__ import annotations

import hashlib
import json
from uuid import UUID

from ..domain.assistance_preferences import (
    AssistancePreferenceExport,
    AssistancePreferenceHistory,
    AssistancePreferenceProfile,
    InvalidAssistancePreference,
    validate_assistance_preference_history,
)
from ..domain.models import (
    InvalidCompletionEvidence,
    LessonCompletionProjection,
    PracticeHistoryProjection,
    ProjectCompletionProjection,
    derive_practice_history,
    derive_project_completion,
    derive_lesson_completion,
)
from ..domain.preferences import (
    InvalidLearnerPreference,
    LearnerPreferenceProfile,
    PreferenceExport,
    PreferenceHistory,
    validate_preference_history,
)
from ..domain.presentation_preferences import (
    InvalidPresentationPreference,
    PresentationPreferenceExport,
    PresentationPreferenceHistory,
    PresentationPreferenceProfile,
    validate_presentation_preference_history,
)
from ..ports.gateways import CompletionEvidenceSourcePort
from ..ports.assistance_preference_contract import (
    AssistancePreferenceContract,
    AssistancePreferenceContractFailure,
)
from ..ports.preference_contract import (
    LearnerPreferenceContract,
    LearnerPreferenceContractFailure,
)
from ..ports.presentation_preference_contract import (
    PresentationPreferenceContract,
    PresentationPreferenceContractFailure,
)
from ..ports.repositories import (
    AssistancePreferenceRepositoryPort,
    CompletionProjectionRepositoryPort,
    LearnerPreferenceIdempotencyConflict,
    LearnerPreferenceRepositoryPort,
    LearnerPreferenceRevisionConflict,
    PresentationPreferenceRepositoryPort,
)
from ..ports.system import (
    AssistancePreferenceSeedPort,
    ClockPort,
    IdentifierPort,
    PreferenceSeedPort,
    PresentationPreferenceSeedPort,
)
from ..public import (
    ExportAssistancePreferencesRequest,
    ExportPresentationPreferencesRequest,
    ExportLearnerPreferencesRequest,
    LearnerModelError,
    LearnerModelErrorCode,
    LessonCompletionHistoryEntry,
    LessonCompletionView,
    MutateAssistancePreferencesRequest,
    MutateLearnerPreferencesRequest,
    MutatePresentationPreferencesRequest,
    OpenAssistancePreferencesRequest,
    OpenLearnerPreferencesRequest,
    OpenPresentationPreferencesRequest,
    OpenLessonCompletionRequest,
    OpenPracticeHistoryRequest,
    OpenProjectCompletionRequest,
    PracticeHistoryAttempt,
    PracticeHistoryItemSummary,
    PracticeHistoryView,
    ProjectCompletionHistoryEntry,
    ProjectCompletionView,
    ReadAssistancePreferenceHistoryRequest,
    ReadLearnerPreferenceHistoryRequest,
    ReadPresentationPreferenceHistoryRequest,
)


class LearnerModelService:
    def __init__(
        self,
        source: CompletionEvidenceSourcePort,
        repository: CompletionProjectionRepositoryPort,
        clock: ClockPort,
        preference_repository: LearnerPreferenceRepositoryPort | None = None,
        preference_contract: LearnerPreferenceContract | None = None,
        preference_identifiers: IdentifierPort | None = None,
        preference_seeds: PreferenceSeedPort | None = None,
        presentation_preference_repository: (
            PresentationPreferenceRepositoryPort | None
        ) = None,
        presentation_preference_contract: (
            PresentationPreferenceContract | None
        ) = None,
        presentation_preference_seeds: PresentationPreferenceSeedPort | None = None,
        assistance_preference_repository: (
            AssistancePreferenceRepositoryPort | None
        ) = None,
        assistance_preference_contract: AssistancePreferenceContract | None = None,
        assistance_preference_seeds: AssistancePreferenceSeedPort | None = None,
    ) -> None:
        self._source = source
        self._repository = repository
        self._clock = clock
        self._preference_repository = preference_repository
        self._preference_contract = preference_contract
        self._preference_identifiers = preference_identifiers
        self._preference_seeds = preference_seeds
        self._presentation_preference_repository = presentation_preference_repository
        self._presentation_preference_contract = presentation_preference_contract
        self._presentation_preference_seeds = presentation_preference_seeds
        self._assistance_preference_repository = assistance_preference_repository
        self._assistance_preference_contract = assistance_preference_contract
        self._assistance_preference_seeds = assistance_preference_seeds

    def open_lesson_completion(
        self, request: OpenLessonCompletionRequest
    ) -> LessonCompletionView:
        self._validate_context(request)
        try:
            evidence = self._source.list_for_lesson(
                learner_id=request.learner_id,
                placement_id=request.placement_id,
            )
        except LearnerModelError:
            raise
        except Exception as error:
            raise LearnerModelError(
                LearnerModelErrorCode.UNAVAILABLE,
                "Completion evidence is temporarily unavailable.",
                reference=request.placement_id,
            ) from error
        try:
            projection = derive_lesson_completion(
                learner_id=request.learner_id,
                placement_id=request.placement_id,
                evidence=evidence,
                rebuilt_at=self._clock.now(),
            )
        except InvalidCompletionEvidence as error:
            raise LearnerModelError(
                LearnerModelErrorCode.INCONSISTENT_EVIDENCE,
                "Completion evidence could not be reconciled.",
                reference=error.reference,
            ) from error
        try:
            self._repository.replace(projection)
        except Exception as error:
            raise LearnerModelError(
                LearnerModelErrorCode.UNAVAILABLE,
                "The completion view is temporarily unavailable.",
                reference=request.placement_id,
            ) from error
        return self._view(projection)

    def open_practice_history(
        self, request: OpenPracticeHistoryRequest
    ) -> PracticeHistoryView:
        self._validate_practice_context(request)
        try:
            source = self._source.read_practice_history(
                learner_id=request.learner_id,
                placement_id=request.placement_id,
            )
        except LearnerModelError:
            raise
        except Exception as error:
            raise LearnerModelError(
                LearnerModelErrorCode.UNAVAILABLE,
                "Practice history is temporarily unavailable.",
                reference=request.placement_id,
            ) from error
        try:
            projection = derive_practice_history(
                source=source,
                rebuilt_at=self._clock.now(),
            )
        except InvalidCompletionEvidence as error:
            raise LearnerModelError(
                LearnerModelErrorCode.INCONSISTENT_EVIDENCE,
                "Practice evidence could not be reconciled.",
                reference=error.reference,
            ) from error
        try:
            self._repository.replace_practice_history(projection)
        except Exception as error:
            raise LearnerModelError(
                LearnerModelErrorCode.UNAVAILABLE,
                "Practice history is temporarily unavailable.",
                reference=request.placement_id,
            ) from error
        return self._practice_view(projection)

    def open_project_completion(
        self, request: OpenProjectCompletionRequest
    ) -> ProjectCompletionView:
        self._validate_project_context(request)
        try:
            evidence = self._source.list_for_project(
                learner_id=request.learner_id,
                project_id=request.project_id,
            )
        except LearnerModelError:
            raise
        except Exception as error:
            raise LearnerModelError(
                LearnerModelErrorCode.UNAVAILABLE,
                "Project completion evidence is temporarily unavailable.",
                reference=request.project_id,
            ) from error
        try:
            projection = derive_project_completion(
                learner_id=request.learner_id,
                project_id=request.project_id,
                evidence=evidence,
                rebuilt_at=self._clock.now(),
            )
        except InvalidCompletionEvidence as error:
            raise LearnerModelError(
                LearnerModelErrorCode.INCONSISTENT_EVIDENCE,
                "Project completion evidence could not be reconciled.",
                reference=error.reference,
            ) from error
        try:
            self._repository.replace_project_completion(projection)
        except Exception as error:
            raise LearnerModelError(
                LearnerModelErrorCode.UNAVAILABLE,
                "The Project completion view is temporarily unavailable.",
                reference=request.project_id,
            ) from error
        return self._project_view(projection)

    def open_preferences(
        self, request: OpenLearnerPreferencesRequest
    ) -> LearnerPreferenceProfile:
        self._validate_learner(request.learner_id)
        repository, contract, _, seeds = self._preference_dependencies()
        try:
            stored = repository.get_preferences(request.learner_id)
            return self._revalidate_preference(
                stored or self._empty_preferences(request.learner_id, contract, seeds),
                contract,
            )
        except LearnerModelError:
            raise
        except LearnerPreferenceContractFailure as error:
            raise self._preference_integrity(error.reference) from error
        except Exception as error:
            raise self._preference_unavailable() from error

    def mutate_preferences(
        self, request: MutateLearnerPreferencesRequest
    ) -> LearnerPreferenceProfile:
        self._validate_learner(request.learner_id)
        repository, contract, identifiers, seeds = self._preference_dependencies()
        intent = request.intent
        try:
            intent_document = contract.mutation_intent_document(intent)
            fingerprint = self._preference_fingerprint(intent_document)
            replay = repository.get_preference_replay(
                request.learner_id, intent.idempotency_key
            )
            if replay is not None:
                accepted_fingerprint, profile = replay
                if accepted_fingerprint != fingerprint:
                    raise LearnerModelError(
                        LearnerModelErrorCode.IMMUTABLE_CONFLICT,
                        "That request key already names a different change.",
                        reference=intent.idempotency_key,
                    )
                return self._revalidate_preference(profile, contract)
            stored = repository.get_preferences(request.learner_id)
            current = self._revalidate_preference(
                stored or self._empty_preferences(request.learner_id, contract, seeds),
                contract,
            )
            if intent.expected_revision != current.revision:
                replay = repository.get_preference_replay(
                    request.learner_id, intent.idempotency_key
                )
                if replay is not None:
                    accepted_fingerprint, profile = replay
                    if accepted_fingerprint != fingerprint:
                        raise LearnerModelError(
                            LearnerModelErrorCode.IMMUTABLE_CONFLICT,
                            "That request key already names a different change.",
                            reference=intent.idempotency_key,
                        )
                    return self._revalidate_preference(profile, contract)
                raise self._preference_stale(intent.idempotency_key)
            issued_id = self._issued_preference_id(
                intent.mutation.operation, identifiers
            )
            accepted, change = contract.apply_mutation(
                current,
                intent,
                occurred_at=self._clock.now(),
                issued_id=issued_id,
            )
            stored = repository.save_preferences_if_revision(
                idempotency_key=intent.idempotency_key,
                request_fingerprint=fingerprint,
                expected_revision=intent.expected_revision,
                profile=accepted,
                change=change,
            )
            return self._revalidate_preference(stored, contract)
        except LearnerModelError:
            raise
        except LearnerPreferenceIdempotencyConflict as error:
            raise LearnerModelError(
                LearnerModelErrorCode.IMMUTABLE_CONFLICT,
                "That request key already names a different change.",
                reference=intent.idempotency_key,
            ) from error
        except LearnerPreferenceRevisionConflict as error:
            raise self._preference_stale(intent.idempotency_key) from error
        except LearnerPreferenceContractFailure as error:
            raise self._preference_contract_error(error) from error
        except Exception as error:
            raise self._preference_unavailable(intent.idempotency_key) from error

    def read_preference_history(
        self, request: ReadLearnerPreferenceHistoryRequest
    ) -> PreferenceHistory:
        self._validate_learner(request.learner_id)
        repository, contract, _, seeds = self._preference_dependencies()
        try:
            profile = repository.get_preferences(request.learner_id)
            current = self._revalidate_preference(
                profile or self._empty_preferences(request.learner_id, contract, seeds),
                contract,
            )
            history = repository.get_preference_history(request.learner_id)
            if history is None:
                history = PreferenceHistory(
                    schema_version="1.0.0",
                    profile_id=current.profile_id,
                    current_revision=current.revision,
                    changes=(),
                )
            validate_preference_history(history, current)
            return history
        except LearnerModelError:
            raise
        except (LearnerPreferenceContractFailure, InvalidLearnerPreference) as error:
            raise self._preference_integrity(
                getattr(error, "reference", "history")
            ) from error
        except Exception as error:
            raise self._preference_unavailable("history") from error

    def export_preferences(
        self, request: ExportLearnerPreferencesRequest
    ) -> PreferenceExport:
        self._validate_learner(request.learner_id)
        _, contract, _, _ = self._preference_dependencies()
        try:
            profile = self.open_preferences(
                OpenLearnerPreferencesRequest(request.learner_id)
            )
            history = self.read_preference_history(
                ReadLearnerPreferenceHistoryRequest(request.learner_id)
            )
            exported = PreferenceExport(
                schema_version="1.0.0",
                purpose=(
                    "A portable copy of the learning goals and preferences you entered."
                ),
                limitations=(
                    "These choices are not evidence of competency or mastery.",
                    "These choices do not grant permission or change course requirements.",
                ),
                exported_at=self._clock.now(),
                profile=profile,
                history=history,
            )
            return contract.parse_export(
                self._json_bytes(contract.export_document(exported))
            )
        except LearnerModelError:
            raise
        except LearnerPreferenceContractFailure as error:
            raise self._preference_integrity(error.reference) from error
        except Exception as error:
            raise self._preference_unavailable("export") from error

    def open_presentation_preferences(
        self, request: OpenPresentationPreferencesRequest
    ) -> PresentationPreferenceProfile:
        self._validate_learner(request.learner_id)
        repository, contract, seeds = self._presentation_preference_dependencies()
        try:
            stored = repository.get_presentation_preferences(request.learner_id)
            return self._revalidate_presentation_preference(
                stored
                or self._default_presentation_preferences(
                    request.learner_id, contract, seeds
                ),
                contract,
            )
        except LearnerModelError:
            raise
        except PresentationPreferenceContractFailure as error:
            raise self._presentation_preference_integrity(error.reference) from error
        except Exception as error:
            raise self._presentation_preference_unavailable() from error

    def mutate_presentation_preferences(
        self, request: MutatePresentationPreferencesRequest
    ) -> PresentationPreferenceProfile:
        self._validate_learner(request.learner_id)
        repository, contract, seeds = self._presentation_preference_dependencies()
        intent = request.intent
        try:
            fingerprint = self._preference_fingerprint(
                contract.mutation_intent_document(intent)
            )
            replay = repository.get_presentation_preference_replay(
                request.learner_id, intent.idempotency_key
            )
            if replay is not None:
                accepted_fingerprint, profile = replay
                if accepted_fingerprint != fingerprint:
                    raise LearnerModelError(
                        LearnerModelErrorCode.IMMUTABLE_CONFLICT,
                        "That request key already names a different display change.",
                        reference=intent.idempotency_key,
                    )
                return self._revalidate_presentation_preference(profile, contract)
            current = repository.get_presentation_preferences(request.learner_id)
            current = self._revalidate_presentation_preference(
                current
                or self._default_presentation_preferences(
                    request.learner_id, contract, seeds
                ),
                contract,
            )
            if intent.expected_revision != current.revision:
                replay = repository.get_presentation_preference_replay(
                    request.learner_id, intent.idempotency_key
                )
                if replay is not None:
                    accepted_fingerprint, profile = replay
                    if accepted_fingerprint != fingerprint:
                        raise LearnerModelError(
                            LearnerModelErrorCode.IMMUTABLE_CONFLICT,
                            "That request key already names a different display change.",
                            reference=intent.idempotency_key,
                        )
                    return self._revalidate_presentation_preference(
                        profile, contract
                    )
                raise self._presentation_preference_stale(intent.idempotency_key)
            accepted, change = contract.apply_mutation(
                current, intent, occurred_at=self._clock.now()
            )
            stored = repository.save_presentation_preferences_if_revision(
                idempotency_key=intent.idempotency_key,
                request_fingerprint=fingerprint,
                expected_revision=intent.expected_revision,
                profile=accepted,
                change=change,
            )
            return self._revalidate_presentation_preference(stored, contract)
        except LearnerModelError:
            raise
        except LearnerPreferenceIdempotencyConflict as error:
            raise LearnerModelError(
                LearnerModelErrorCode.IMMUTABLE_CONFLICT,
                "That request key already names a different display change.",
                reference=intent.idempotency_key,
            ) from error
        except LearnerPreferenceRevisionConflict as error:
            raise self._presentation_preference_stale(intent.idempotency_key) from error
        except PresentationPreferenceContractFailure as error:
            raise self._presentation_preference_contract_error(error) from error
        except Exception as error:
            raise self._presentation_preference_unavailable(
                intent.idempotency_key
            ) from error

    def read_presentation_preference_history(
        self, request: ReadPresentationPreferenceHistoryRequest
    ) -> PresentationPreferenceHistory:
        self._validate_learner(request.learner_id)
        repository, contract, seeds = self._presentation_preference_dependencies()
        try:
            _, history = self._presentation_preference_snapshot(
                request.learner_id, repository, contract, seeds
            )
            return history
        except LearnerModelError:
            raise
        except (
            PresentationPreferenceContractFailure,
            InvalidPresentationPreference,
        ) as error:
            raise self._presentation_preference_integrity(
                getattr(error, "reference", "history")
            ) from error
        except Exception as error:
            raise self._presentation_preference_unavailable("history") from error

    def export_presentation_preferences(
        self, request: ExportPresentationPreferencesRequest
    ) -> PresentationPreferenceExport:
        self._validate_learner(request.learner_id)
        repository, contract, seeds = self._presentation_preference_dependencies()
        try:
            profile, history = self._presentation_preference_snapshot(
                request.learner_id, repository, contract, seeds
            )
            exported = PresentationPreferenceExport(
                schema_version="1.0.0",
                purpose="A portable copy of the display choices you selected.",
                limitations=(
                    "These choices are not a diagnosis or learning assessment.",
                    "Browser theme is stored separately and is not included.",
                ),
                exported_at=self._clock.now(),
                profile=profile,
                history=history,
            )
            return contract.parse_export(
                self._json_bytes(contract.export_document(exported))
            )
        except LearnerModelError:
            raise
        except PresentationPreferenceContractFailure as error:
            raise self._presentation_preference_integrity(error.reference) from error
        except Exception as error:
            raise self._presentation_preference_unavailable("export") from error

    def open_assistance_preferences(
        self, request: OpenAssistancePreferencesRequest
    ) -> AssistancePreferenceProfile:
        self._validate_learner(request.learner_id)
        repository, contract, seeds = self._assistance_preference_dependencies()
        try:
            stored = repository.get_assistance_preferences(request.learner_id)
            return self._revalidate_assistance_preference(
                stored
                or self._default_assistance_preferences(
                    request.learner_id, contract, seeds
                ),
                contract,
            )
        except LearnerModelError:
            raise
        except AssistancePreferenceContractFailure as error:
            raise self._assistance_preference_integrity(error.reference) from error
        except Exception as error:
            raise self._assistance_preference_unavailable() from error

    def mutate_assistance_preferences(
        self, request: MutateAssistancePreferencesRequest
    ) -> AssistancePreferenceProfile:
        self._validate_learner(request.learner_id)
        repository, contract, seeds = self._assistance_preference_dependencies()
        intent = request.intent
        try:
            fingerprint = self._preference_fingerprint(
                contract.mutation_intent_document(intent)
            )
            replay = repository.get_assistance_preference_replay(
                request.learner_id, intent.idempotency_key
            )
            if replay is not None:
                accepted_fingerprint, profile = replay
                if accepted_fingerprint != fingerprint:
                    raise LearnerModelError(
                        LearnerModelErrorCode.IMMUTABLE_CONFLICT,
                        "That request key already names a different AI-help change.",
                        reference=intent.idempotency_key,
                    )
                return self._revalidate_assistance_preference(profile, contract)
            current = repository.get_assistance_preferences(request.learner_id)
            current = self._revalidate_assistance_preference(
                current
                or self._default_assistance_preferences(
                    request.learner_id, contract, seeds
                ),
                contract,
            )
            if intent.expected_revision != current.revision:
                replay = repository.get_assistance_preference_replay(
                    request.learner_id, intent.idempotency_key
                )
                if replay is not None:
                    accepted_fingerprint, profile = replay
                    if accepted_fingerprint != fingerprint:
                        raise LearnerModelError(
                            LearnerModelErrorCode.IMMUTABLE_CONFLICT,
                            "That request key already names a different AI-help change.",
                            reference=intent.idempotency_key,
                        )
                    return self._revalidate_assistance_preference(
                        profile, contract
                    )
                raise self._assistance_preference_stale(intent.idempotency_key)
            accepted, change = contract.apply_mutation(
                current, intent, occurred_at=self._clock.now()
            )
            stored = repository.save_assistance_preferences_if_revision(
                idempotency_key=intent.idempotency_key,
                request_fingerprint=fingerprint,
                expected_revision=intent.expected_revision,
                profile=accepted,
                change=change,
            )
            return self._revalidate_assistance_preference(stored, contract)
        except LearnerModelError:
            raise
        except LearnerPreferenceIdempotencyConflict as error:
            raise LearnerModelError(
                LearnerModelErrorCode.IMMUTABLE_CONFLICT,
                "That request key already names a different AI-help change.",
                reference=intent.idempotency_key,
            ) from error
        except LearnerPreferenceRevisionConflict as error:
            raise self._assistance_preference_stale(intent.idempotency_key) from error
        except AssistancePreferenceContractFailure as error:
            raise self._assistance_preference_contract_error(error) from error
        except Exception as error:
            raise self._assistance_preference_unavailable(
                intent.idempotency_key
            ) from error

    def read_assistance_preference_history(
        self, request: ReadAssistancePreferenceHistoryRequest
    ) -> AssistancePreferenceHistory:
        self._validate_learner(request.learner_id)
        repository, contract, seeds = self._assistance_preference_dependencies()
        try:
            _, history = self._assistance_preference_snapshot(
                request.learner_id, repository, contract, seeds
            )
            return history
        except LearnerModelError:
            raise
        except (
            AssistancePreferenceContractFailure,
            InvalidAssistancePreference,
        ) as error:
            raise self._assistance_preference_integrity(
                getattr(error, "reference", "history")
            ) from error
        except Exception as error:
            raise self._assistance_preference_unavailable("history") from error

    def export_assistance_preferences(
        self, request: ExportAssistancePreferencesRequest
    ) -> AssistancePreferenceExport:
        self._validate_learner(request.learner_id)
        repository, contract, seeds = self._assistance_preference_dependencies()
        try:
            profile, history = self._assistance_preference_snapshot(
                request.learner_id, repository, contract, seeds
            )
            exported = AssistancePreferenceExport(
                schema_version="1.0.0",
                purpose="A portable copy of the AI-help choice you selected.",
                limitations=(
                    "On request records your choice only and does not enable or call an AI service.",
                    "This choice is not learning evidence or permission to share data.",
                ),
                exported_at=self._clock.now(),
                profile=profile,
                history=history,
            )
            return contract.parse_export(
                self._json_bytes(contract.export_document(exported))
            )
        except LearnerModelError:
            raise
        except AssistancePreferenceContractFailure as error:
            raise self._assistance_preference_integrity(error.reference) from error
        except Exception as error:
            raise self._assistance_preference_unavailable("export") from error

    def _assistance_preference_dependencies(self) -> tuple[
        AssistancePreferenceRepositoryPort,
        AssistancePreferenceContract,
        AssistancePreferenceSeedPort,
    ]:
        if (
            self._assistance_preference_repository is None
            or self._assistance_preference_contract is None
            or self._assistance_preference_seeds is None
        ):
            raise self._assistance_preference_unavailable()
        return (
            self._assistance_preference_repository,
            self._assistance_preference_contract,
            self._assistance_preference_seeds,
        )

    def _assistance_preference_snapshot(
        self,
        learner_id: str,
        repository: AssistancePreferenceRepositoryPort,
        contract: AssistancePreferenceContract,
        seeds: AssistancePreferenceSeedPort,
    ) -> tuple[AssistancePreferenceProfile, AssistancePreferenceHistory]:
        snapshot = repository.get_assistance_preference_snapshot(learner_id)
        if snapshot is None:
            profile = self._default_assistance_preferences(
                learner_id, contract, seeds
            )
            history = AssistancePreferenceHistory(
                schema_version="1.0.0",
                profile_id=profile.profile_id,
                current_revision=profile.revision,
                changes=(),
            )
        else:
            profile, history = snapshot
        current = self._revalidate_assistance_preference(profile, contract)
        validate_assistance_preference_history(history, current)
        return current, history

    @staticmethod
    def _default_assistance_preferences(
        learner_id: str,
        contract: AssistancePreferenceContract,
        seeds: AssistancePreferenceSeedPort,
    ) -> AssistancePreferenceProfile:
        seed = seeds.for_learner(learner_id)
        return contract.default_profile(
            profile_id=seed.profile_id,
            learner_id=learner_id,
            created_at=seed.created_at,
        )

    @classmethod
    def _revalidate_assistance_preference(
        cls,
        profile: AssistancePreferenceProfile,
        contract: AssistancePreferenceContract,
    ) -> AssistancePreferenceProfile:
        return contract.parse_profile(
            cls._json_bytes(contract.profile_document(profile))
        )

    def _presentation_preference_dependencies(self) -> tuple[
        PresentationPreferenceRepositoryPort,
        PresentationPreferenceContract,
        PresentationPreferenceSeedPort,
    ]:
        if (
            self._presentation_preference_repository is None
            or self._presentation_preference_contract is None
            or self._presentation_preference_seeds is None
        ):
            raise self._presentation_preference_unavailable()
        return (
            self._presentation_preference_repository,
            self._presentation_preference_contract,
            self._presentation_preference_seeds,
        )

    def _presentation_preference_snapshot(
        self,
        learner_id: str,
        repository: PresentationPreferenceRepositoryPort,
        contract: PresentationPreferenceContract,
        seeds: PresentationPreferenceSeedPort,
    ) -> tuple[PresentationPreferenceProfile, PresentationPreferenceHistory]:
        snapshot = repository.get_presentation_preference_snapshot(learner_id)
        if snapshot is None:
            profile = self._default_presentation_preferences(
                learner_id, contract, seeds
            )
            history = PresentationPreferenceHistory(
                schema_version="1.0.0",
                profile_id=profile.profile_id,
                current_revision=profile.revision,
                changes=(),
            )
        else:
            profile, history = snapshot
        current = self._revalidate_presentation_preference(profile, contract)
        validate_presentation_preference_history(history, current)
        return current, history

    @staticmethod
    def _default_presentation_preferences(
        learner_id: str,
        contract: PresentationPreferenceContract,
        seeds: PresentationPreferenceSeedPort,
    ) -> PresentationPreferenceProfile:
        seed = seeds.for_learner(learner_id)
        return contract.default_profile(
            profile_id=seed.profile_id,
            learner_id=learner_id,
            created_at=seed.created_at,
        )

    @classmethod
    def _revalidate_presentation_preference(
        cls,
        profile: PresentationPreferenceProfile,
        contract: PresentationPreferenceContract,
    ) -> PresentationPreferenceProfile:
        return contract.parse_profile(
            cls._json_bytes(contract.profile_document(profile))
        )

    def _preference_dependencies(self) -> tuple[
        LearnerPreferenceRepositoryPort,
        LearnerPreferenceContract,
        IdentifierPort,
        PreferenceSeedPort,
    ]:
        if (
            self._preference_repository is None
            or self._preference_contract is None
            or self._preference_identifiers is None
            or self._preference_seeds is None
        ):
            raise self._preference_unavailable()
        return (
            self._preference_repository,
            self._preference_contract,
            self._preference_identifiers,
            self._preference_seeds,
        )

    @staticmethod
    def _empty_preferences(
        learner_id: str,
        contract: LearnerPreferenceContract,
        seeds: PreferenceSeedPort,
    ) -> LearnerPreferenceProfile:
        seed = seeds.for_learner(learner_id)
        return contract.empty_profile(
            profile_id=seed.profile_id,
            learner_id=learner_id,
            created_at=seed.created_at,
        )

    @classmethod
    def _revalidate_preference(
        cls,
        profile: LearnerPreferenceProfile,
        contract: LearnerPreferenceContract,
    ) -> LearnerPreferenceProfile:
        return contract.parse_profile(
            cls._json_bytes(contract.profile_document(profile))
        )

    @staticmethod
    def _preference_fingerprint(document: dict[str, object]) -> str:
        return hashlib.sha256(
            json.dumps(
                document,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
            ).encode("utf-8")
        ).hexdigest()

    @staticmethod
    def _issued_preference_id(
        operation: str, identifiers: IdentifierPort
    ) -> str | None:
        prefixes = {
            "create_goal": "goal",
            "create_experience": "experience",
            "create_interest": "interest",
        }
        prefix = prefixes.get(operation)
        return f"{prefix}.{identifiers.new()}" if prefix else None

    @staticmethod
    def _json_bytes(value: object) -> bytes:
        return json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode("utf-8")

    @staticmethod
    def _validate_learner(learner_id: str) -> None:
        try:
            UUID(learner_id)
        except (ValueError, AttributeError) as error:
            raise LearnerModelError(
                LearnerModelErrorCode.INVALID_CONTEXT,
                "Learner context is not authorized.",
                reference="learner",
            ) from error

    @staticmethod
    def _preference_contract_error(
        error: LearnerPreferenceContractFailure,
    ) -> LearnerModelError:
        if error.code.endswith("stale_revision"):
            return LearnerModelService._preference_stale(error.reference)
        if error.code.endswith(("goal_limit", "experience_limit", "interest_limit")):
            return LearnerModelError(
                LearnerModelErrorCode.PREFERENCE_LIMIT,
                "This learning preference section is full. Remove an item before adding another.",
                reference=error.reference,
            )
        if error.code.endswith("not_found"):
            return LearnerModelError(
                LearnerModelErrorCode.NOT_FOUND,
                "That learning preference was not found.",
                reference=error.reference,
            )
        return LearnerModelError(
            LearnerModelErrorCode.INVALID_REQUEST,
            "The learning preference change is not valid.",
            reference=error.reference,
        )

    @staticmethod
    def _preference_stale(reference: str) -> LearnerModelError:
        return LearnerModelError(
            LearnerModelErrorCode.STALE_REVISION,
            "Learning preferences changed. Refresh them before trying again.",
            reference=reference,
        )

    @staticmethod
    def _preference_integrity(reference: str) -> LearnerModelError:
        return LearnerModelError(
            LearnerModelErrorCode.INTEGRITY_FAILURE,
            "Saved learning preferences could not be verified.",
            reference=reference,
        )

    @staticmethod
    def _preference_unavailable(
        reference: str = "learner-preferences",
    ) -> LearnerModelError:
        return LearnerModelError(
            LearnerModelErrorCode.UNAVAILABLE,
            "Learning preferences are temporarily unavailable.",
            reference=reference,
        )

    @staticmethod
    def _presentation_preference_contract_error(
        error: PresentationPreferenceContractFailure,
    ) -> LearnerModelError:
        if error.code.endswith("stale_revision"):
            return LearnerModelService._presentation_preference_stale(error.reference)
        return LearnerModelError(
            LearnerModelErrorCode.INVALID_REQUEST,
            "The display preference change is not valid.",
            reference=error.reference,
        )

    @staticmethod
    def _presentation_preference_stale(reference: str) -> LearnerModelError:
        return LearnerModelError(
            LearnerModelErrorCode.STALE_REVISION,
            "Display choices changed. Refresh them before trying again.",
            reference=reference,
        )

    @staticmethod
    def _presentation_preference_integrity(reference: str) -> LearnerModelError:
        return LearnerModelError(
            LearnerModelErrorCode.INTEGRITY_FAILURE,
            "Saved display choices could not be verified.",
            reference=reference,
        )

    @staticmethod
    def _presentation_preference_unavailable(
        reference: str = "learner-presentation-preferences",
    ) -> LearnerModelError:
        return LearnerModelError(
            LearnerModelErrorCode.UNAVAILABLE,
            "Display choices are temporarily unavailable.",
            reference=reference,
        )

    @staticmethod
    def _assistance_preference_contract_error(
        error: AssistancePreferenceContractFailure,
    ) -> LearnerModelError:
        if error.code.endswith("stale_revision"):
            return LearnerModelService._assistance_preference_stale(error.reference)
        return LearnerModelError(
            LearnerModelErrorCode.INVALID_REQUEST,
            "The AI-help choice is not valid.",
            reference=error.reference,
        )

    @staticmethod
    def _assistance_preference_stale(reference: str) -> LearnerModelError:
        return LearnerModelError(
            LearnerModelErrorCode.STALE_REVISION,
            "The AI-help choice changed. Refresh it before trying again.",
            reference=reference,
        )

    @staticmethod
    def _assistance_preference_integrity(reference: str) -> LearnerModelError:
        return LearnerModelError(
            LearnerModelErrorCode.INTEGRITY_FAILURE,
            "The saved AI-help choice could not be verified.",
            reference=reference,
        )

    @staticmethod
    def _assistance_preference_unavailable(
        reference: str = "learner-assistance-preferences",
    ) -> LearnerModelError:
        return LearnerModelError(
            LearnerModelErrorCode.UNAVAILABLE,
            "The AI-help choice is temporarily unavailable.",
            reference=reference,
        )

    @staticmethod
    def _validate_context(request: OpenLessonCompletionRequest) -> None:
        try:
            UUID(request.learner_id)
        except (ValueError, AttributeError) as error:
            raise LearnerModelError(
                LearnerModelErrorCode.INVALID_CONTEXT,
                "Learner context is not authorized.",
                reference="learner",
            ) from error
        value = request.placement_id
        if (
            not 3 <= len(value) <= 64
            or not value[0].isalnum()
            or not all(
                character.islower()
                or character.isdigit()
                or character in "._-"
                for character in value
            )
        ):
            raise LearnerModelError(
                LearnerModelErrorCode.INVALID_CONTEXT,
                "Lesson placement context is invalid.",
                reference="placement_id",
            )

    @staticmethod
    def _validate_practice_context(request: OpenPracticeHistoryRequest) -> None:
        try:
            UUID(request.learner_id)
        except (ValueError, AttributeError) as error:
            raise LearnerModelError(
                LearnerModelErrorCode.INVALID_CONTEXT,
                "Learner context is not authorized.",
                reference="learner",
            ) from error
        value = request.placement_id
        if (
            not 3 <= len(value) <= 64
            or not value[0].isalnum()
            or not all(
                character.islower()
                or character.isdigit()
                or character in "._-"
                for character in value
            )
        ):
            raise LearnerModelError(
                LearnerModelErrorCode.INVALID_CONTEXT,
                "Practice placement context is invalid.",
                reference="placement_id",
            )

    @staticmethod
    def _validate_project_context(request: OpenProjectCompletionRequest) -> None:
        try:
            UUID(request.learner_id)
        except (ValueError, AttributeError) as error:
            raise LearnerModelError(
                LearnerModelErrorCode.INVALID_CONTEXT,
                "Learner context is not authorized.",
                reference="learner",
            ) from error
        value = request.project_id
        if (
            not 1 <= len(value) <= 128
            or not value[0].isalnum()
            or not all(
                character.islower()
                or character.isdigit()
                or character in "._-"
                for character in value
            )
        ):
            raise LearnerModelError(
                LearnerModelErrorCode.INVALID_CONTEXT,
                "Project context is invalid.",
                reference="project_id",
            )

    @staticmethod
    def _view(projection: LessonCompletionProjection) -> LessonCompletionView:
        return LessonCompletionView(
            placement_id=projection.placement_id,
            completed=projection.completed,
            completion_meaning=(
                "bounded_knowledge_check_completed"
                if projection.completed
                else "not_completed"
            ),
            source_digest=projection.source_digest,
            rebuilt_at=projection.rebuilt_at,
            history=tuple(
                LessonCompletionHistoryEntry(
                    event_id=item.event_id,
                    attempt_id=item.attempt_id,
                    evidence_id=item.evidence_id,
                    package_id=item.package_id,
                    package_version=item.package_version,
                    package_digest=item.package_digest,
                    assessment_id=item.assessment_id,
                    assessment_version=item.assessment_version,
                    definition_digest=item.definition_digest,
                    item_id=item.item_id,
                    item_version=item.item_version,
                    scoring_policy_id=item.scoring_policy_id,
                    scoring_policy_version=item.scoring_policy_version,
                    score=item.score,
                    max_score=item.max_score,
                    completed_at=item.completed_at,
                )
                for item in projection.history
            ),
        )

    @staticmethod
    def _practice_view(
        projection: PracticeHistoryProjection,
    ) -> PracticeHistoryView:
        return PracticeHistoryView(
            schema_version="1.0.0",
            placement_id=projection.placement_id,
            package_id=projection.package_id,
            package_version=projection.package_version,
            package_digest=projection.package_digest,
            definition_digest=projection.definition_digest,
            practice_id=projection.practice_id,
            practice_version=projection.practice_version,
            attempt_policy_id=projection.attempt_policy_id,
            attempt_policy_version=projection.attempt_policy_version,
            source_digest=projection.source_digest,
            rebuilt_at=projection.rebuilt_at,
            attempts=tuple(
                PracticeHistoryAttempt(
                    attempt_order=attempt.attempt_order,
                    event_id=attempt.event_id,
                    attempt_id=attempt.attempt_id,
                    evidence_id=attempt.evidence_id,
                    submission_id=attempt.submission_id,
                    score=attempt.score,
                    max_score=attempt.max_score,
                    outcome=attempt.outcome,
                    item_summaries=tuple(
                        PracticeHistoryItemSummary(
                            item_id=item.item_id,
                            item_version=item.item_version,
                            item_type=item.item_type,
                            scoring_policy_id=item.scoring_policy_id,
                            scoring_policy_version=(
                                item.scoring_policy_version
                            ),
                            score=item.score,
                            max_score=item.max_score,
                            correct=item.correct,
                            review_reference_ids=item.review_reference_ids,
                        )
                        for item in attempt.item_summaries
                    ),
                    completed_at=attempt.completed_at,
                )
                for attempt in projection.attempts
            ),
        )

    @staticmethod
    def _project_view(
        projection: ProjectCompletionProjection,
    ) -> ProjectCompletionView:
        return ProjectCompletionView(
            project_id=projection.project_id,
            completed=projection.completed,
            completion_meaning=(
                "bounded_project_activity_completed"
                if projection.completed
                else "not_completed"
            ),
            source_digest=projection.source_digest,
            rebuilt_at=projection.rebuilt_at,
            history=tuple(
                ProjectCompletionHistoryEntry(
                    event_id=item.event_id,
                    evidence_id=item.evidence_id,
                    submission_id=item.submission_id,
                    snapshot_id=item.snapshot_id,
                    snapshot_digest=item.snapshot_digest,
                    brief_id=item.brief_id,
                    brief_version=item.brief_version,
                    brief_digest=item.brief_digest,
                    placement_id=item.placement_id,
                    placement_version=item.placement_version,
                    placement_digest=item.placement_digest,
                    policy_id=item.policy_id,
                    policy_version=item.policy_version,
                    milestone_ids=item.milestone_ids,
                    request_fingerprint=item.request_fingerprint,
                    occurrence=item.occurrence,
                    accepted_sequence=item.accepted_sequence,
                    supersedes_submission_id=(
                        item.supersedes_submission_id
                    ),
                    submitted_at=item.submitted_at,
                    occurred_at=item.occurred_at,
                )
                for item in projection.history
            ),
        )

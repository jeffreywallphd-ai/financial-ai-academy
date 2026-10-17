"""Server-authoritative Personal workspace reads and mutations."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
import hashlib
import json
import re

from ..domain.workspace import (
    CreateBookmarkMutation,
    CreateCollectionMutation,
    CreateNoteMutation,
    LearningOpportunityReference,
    PersonalWorkspace,
    PlacedLessonReference,
    ProjectArtifactReference,
    ProjectSnapshotReference,
    ProjectWorkspaceReference,
    RefreshReferenceMutation,
    WorkspaceMutationIntent,
    WorkspaceQueryResult,
)
from ..ports.learning_reference import (
    LearningReferenceGatewayPort,
    PersonalWorkspaceSourceUnavailable,
)
from ..ports.repositories import (
    PersonalWorkspaceIdempotencyConflict,
    PersonalWorkspaceRepositoryPort,
    PersonalWorkspaceRevisionConflict,
)
from ..ports.system import ClockPort, IdentifierPort, WorkspaceSeedPort
from ..ports.workspace_contract import (
    PersonalWorkspaceContractFailure,
    PersonalWorkspaceContractPort,
)
from ..public import (
    CreateBookmarkCommand,
    CreateNoteCommand,
    LearningOpportunitySelector,
    MutatePersonalWorkspaceRequest,
    OpenPersonalWorkspaceRequest,
    PersonalWorkspaceError,
    PersonalWorkspaceErrorCode,
    PersonalWorkspaceMutationCommand,
    PlacedLessonSelector,
    ProjectArtifactSelector,
    ProjectSnapshotSelector,
    ProjectWorkspaceSelector,
    QueryPersonalWorkspaceRequest,
)


_IDENTIFIER = re.compile(r"^[a-z0-9][a-z0-9._-]{0,127}$")


class PersonalWorkspaceService:
    def __init__(
        self,
        repository: PersonalWorkspaceRepositoryPort,
        contract: PersonalWorkspaceContractPort,
        references: LearningReferenceGatewayPort,
        clock: ClockPort,
        identifiers: IdentifierPort,
        seeds: WorkspaceSeedPort,
    ) -> None:
        self._repository = repository
        self._contract = contract
        self._references = references
        self._clock = clock
        self._identifiers = identifiers
        self._seeds = seeds

    def open_workspace(
        self, request: OpenPersonalWorkspaceRequest
    ) -> PersonalWorkspace:
        self._validate_learner(request.learner_id)
        try:
            workspace = self._repository.get_workspace(request.learner_id)
            return self._revalidate(workspace or self._empty(request.learner_id))
        except PersonalWorkspaceError:
            raise
        except PersonalWorkspaceContractFailure as error:
            raise self._integrity(error.reference) from error
        except Exception as error:
            raise self._unavailable() from error

    def mutate_workspace(
        self, request: MutatePersonalWorkspaceRequest
    ) -> PersonalWorkspace:
        self._validate_learner(request.learner_id)
        command = request.command
        fingerprint = self._fingerprint(command)
        try:
            replay = self._repository.get_mutation_replay(
                request.learner_id, command.idempotency_key
            )
            if replay is not None:
                accepted_fingerprint, workspace = replay
                if accepted_fingerprint != fingerprint:
                    raise PersonalWorkspaceError(
                        PersonalWorkspaceErrorCode.IMMUTABLE_CONFLICT,
                        "The request key already names different saved work.",
                        reference=command.idempotency_key,
                    )
                return self._revalidate(workspace)

            current = self._repository.get_workspace(request.learner_id)
            current = self._revalidate(current or self._empty(request.learner_id))
            if command.expected_revision != current.revision:
                raise self._stale(command.idempotency_key)

            now = self._clock.now()
            intent = self._intent(
                command,
                learner_id=request.learner_id,
                validated_at=now,
            )
            issued_id = (
                self._identifiers.new()
                if isinstance(
                    intent.mutation,
                    (CreateNoteMutation, CreateBookmarkMutation, CreateCollectionMutation),
                )
                else None
            )
            if isinstance(intent.mutation, RefreshReferenceMutation):
                accepted = self._apply_refresh(
                    current,
                    intent,
                    learner_id=request.learner_id,
                    readable_reference_kinds=request.readable_reference_kinds,
                    occurred_at=now,
                )
            else:
                accepted = self._contract.apply_mutation(
                    current,
                    intent,
                    occurred_at=now,
                    issued_id=issued_id,
                )
            stored = self._repository.save_if_revision(
                idempotency_key=command.idempotency_key,
                request_fingerprint=fingerprint,
                expected_revision=command.expected_revision,
                workspace=accepted,
            )
            return self._revalidate(stored)
        except PersonalWorkspaceError:
            raise
        except PersonalWorkspaceSourceUnavailable as error:
            raise PersonalWorkspaceError(
                PersonalWorkspaceErrorCode.SOURCE_UNAVAILABLE,
                "The learning item is not available to save.",
            ) from error
        except PersonalWorkspaceIdempotencyConflict as error:
            raise PersonalWorkspaceError(
                PersonalWorkspaceErrorCode.IMMUTABLE_CONFLICT,
                "The request key already names different saved work.",
                reference=command.idempotency_key,
            ) from error
        except PersonalWorkspaceRevisionConflict as error:
            raise self._stale(command.idempotency_key) from error
        except PersonalWorkspaceContractFailure as error:
            if error.code.endswith("stale_revision"):
                raise self._stale(command.idempotency_key) from error
            if error.code.endswith(("record_not_found", "collection_not_found")):
                raise PersonalWorkspaceError(
                    PersonalWorkspaceErrorCode.NOT_FOUND,
                    "The saved learning item was not found.",
                    reference=error.reference,
                ) from error
            raise PersonalWorkspaceError(
                PersonalWorkspaceErrorCode.INVALID_REQUEST,
                "The workspace change is not valid.",
                reference=error.reference,
            ) from error
        except Exception as error:
            raise self._unavailable(command.idempotency_key) from error

    def query_workspace(
        self, request: QueryPersonalWorkspaceRequest
    ) -> WorkspaceQueryResult:
        self._validate_learner(request.learner_id)
        try:
            workspace = self._repository.get_workspace(request.learner_id)
            current = self._revalidate(workspace or self._empty(request.learner_id))
            return self._contract.query_workspace(current, request.query)
        except PersonalWorkspaceError:
            raise
        except PersonalWorkspaceContractFailure as error:
            if error.code.endswith("collection_not_found"):
                raise PersonalWorkspaceError(
                    PersonalWorkspaceErrorCode.NOT_FOUND,
                    "The saved learning collection was not found.",
                    reference=error.reference,
                ) from error
            if error.code.endswith("invalid_cursor"):
                raise PersonalWorkspaceError(
                    PersonalWorkspaceErrorCode.IMMUTABLE_CONFLICT,
                    "Saved learning changed. Start the search again.",
                    reference="cursor",
                ) from error
            raise PersonalWorkspaceError(
                PersonalWorkspaceErrorCode.INVALID_REQUEST,
                "The saved learning search is not valid.",
                reference=error.reference,
            ) from error
        except Exception as error:
            raise self._unavailable() from error

    def _apply_refresh(
        self,
        current: PersonalWorkspace,
        intent: WorkspaceMutationIntent,
        *,
        learner_id: str,
        readable_reference_kinds: frozenset[str],
        occurred_at: datetime,
    ) -> PersonalWorkspace:
        mutation = intent.mutation
        if not isinstance(mutation, RefreshReferenceMutation):
            raise AssertionError("refresh intent required")
        record = next(
            (
                candidate
                for candidate in current.records
                if candidate.record_id == mutation.record_id
            ),
            None,
        )
        if record is None:
            raise PersonalWorkspaceError(
                PersonalWorkspaceErrorCode.NOT_FOUND,
                "The saved learning item was not found.",
                reference=mutation.record_id,
            )

        resolved = None
        target = record.target
        if target.reference_kind in readable_reference_kinds:
            try:
                resolved = self._resolve_target(
                    self._selector_for_reference(target),
                    learner_id,
                    occurred_at,
                )
            except PersonalWorkspaceSourceUnavailable:
                resolved = None
        return self._contract.apply_reference_refresh(
            current,
            intent,
            occurred_at=occurred_at,
            resolved_reference=resolved,
        )

    @staticmethod
    def _selector_for_reference(target):
        if isinstance(target, LearningOpportunityReference):
            return LearningOpportunitySelector(
                opportunity_id=target.opportunity_id,
                placement_id=target.placement_id,
            )
        if isinstance(target, PlacedLessonReference):
            return PlacedLessonSelector(placement_id=target.placement_id)
        if isinstance(target, ProjectWorkspaceReference):
            return ProjectWorkspaceSelector(project_id=target.project_id)
        if isinstance(target, ProjectSnapshotReference):
            return ProjectSnapshotSelector(
                project_id=target.project_id,
                snapshot_id=target.snapshot_id,
            )
        if isinstance(target, ProjectArtifactReference):
            return ProjectArtifactSelector(
                project_id=target.project_id,
                artifact_id=target.artifact_id,
                artifact_version=target.artifact_version,
            )
        raise PersonalWorkspaceSourceUnavailable()

    def _intent(
        self,
        command: PersonalWorkspaceMutationCommand,
        *,
        learner_id: str,
        validated_at: datetime,
    ) -> WorkspaceMutationIntent:
        mutation = command.mutation
        if isinstance(mutation, CreateNoteCommand):
            resolved = CreateNoteMutation(
                target=self._resolve_target(
                    mutation.selector, learner_id, validated_at
                ),
                title=mutation.title,
                body=mutation.body,
            )
        elif isinstance(mutation, CreateBookmarkCommand):
            resolved = CreateBookmarkMutation(
                target=self._resolve_target(
                    mutation.selector, learner_id, validated_at
                ),
                label=mutation.label,
            )
        else:
            resolved = mutation
        intent = WorkspaceMutationIntent(
            schema_version=command.schema_version,
            idempotency_key=command.idempotency_key,
            expected_revision=command.expected_revision,
            mutation=resolved,
        )
        self._contract.mutation_intent_document(intent)
        return intent

    def _resolve_target(
        self, selector, learner_id: str, validated_at: datetime
    ):
        target = self._references.resolve(
            selector,
            learner_id=learner_id,
            validated_at=validated_at,
        )
        if isinstance(selector, LearningOpportunitySelector):
            if not isinstance(target, LearningOpportunityReference) or (
                target.opportunity_id,
                target.placement_id,
            ) != (selector.opportunity_id, selector.placement_id):
                raise PersonalWorkspaceSourceUnavailable()
        elif isinstance(selector, PlacedLessonSelector):
            if not isinstance(
                target, PlacedLessonReference
            ) or target.placement_id != selector.placement_id:
                raise PersonalWorkspaceSourceUnavailable()
        elif isinstance(selector, ProjectWorkspaceSelector):
            if not isinstance(
                target, ProjectWorkspaceReference
            ) or target.project_id != selector.project_id:
                raise PersonalWorkspaceSourceUnavailable()
        elif isinstance(selector, ProjectSnapshotSelector):
            if not isinstance(target, ProjectSnapshotReference) or (
                target.project_id,
                target.snapshot_id,
            ) != (selector.project_id, selector.snapshot_id):
                raise PersonalWorkspaceSourceUnavailable()
        elif isinstance(selector, ProjectArtifactSelector):
            if not isinstance(target, ProjectArtifactReference) or (
                target.project_id,
                target.artifact_id,
                target.artifact_version,
            ) != (
                selector.project_id,
                selector.artifact_id,
                selector.artifact_version,
            ):
                raise PersonalWorkspaceSourceUnavailable()
        else:
            raise PersonalWorkspaceSourceUnavailable()
        return target

    def _empty(self, learner_id: str) -> PersonalWorkspace:
        seed = self._seeds.for_learner(learner_id)
        return self._contract.empty_workspace(
            workspace_id=seed.workspace_id,
            learner_id=learner_id,
            created_at=seed.created_at,
        )

    def _revalidate(self, workspace: PersonalWorkspace) -> PersonalWorkspace:
        document = self._contract.workspace_document(workspace)
        return self._contract.parse_workspace(
            json.dumps(
                document, sort_keys=True, separators=(",", ":"), ensure_ascii=False
            ).encode("utf-8")
        )

    @staticmethod
    def _fingerprint(command: PersonalWorkspaceMutationCommand) -> str:
        payload = json.dumps(
            asdict(command),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    @staticmethod
    def _validate_learner(learner_id: str) -> None:
        if not _IDENTIFIER.fullmatch(learner_id):
            raise PersonalWorkspaceError(
                PersonalWorkspaceErrorCode.INVALID_REQUEST,
                "The learner workspace request is not valid.",
                reference="learner",
            )

    @staticmethod
    def _stale(reference: str) -> PersonalWorkspaceError:
        return PersonalWorkspaceError(
            PersonalWorkspaceErrorCode.STALE_REVISION,
            "The saved workspace changed. Refresh it before trying again.",
            reference=reference,
        )

    @staticmethod
    def _integrity(reference: str) -> PersonalWorkspaceError:
        return PersonalWorkspaceError(
            PersonalWorkspaceErrorCode.INTEGRITY_FAILURE,
            "Saved workspace data could not be verified.",
            reference=reference,
        )

    @staticmethod
    def _unavailable(reference: str = "personal-workspace") -> PersonalWorkspaceError:
        return PersonalWorkspaceError(
            PersonalWorkspaceErrorCode.UNAVAILABLE,
            "The personal workspace is unavailable.",
            reference=reference,
        )

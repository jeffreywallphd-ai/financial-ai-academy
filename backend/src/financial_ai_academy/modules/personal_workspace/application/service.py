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
    PersonalWorkspace,
    WorkspaceMutationIntent,
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
    MutatePersonalWorkspaceRequest,
    OpenPersonalWorkspaceRequest,
    PersonalWorkspaceError,
    PersonalWorkspaceErrorCode,
    PersonalWorkspaceMutationCommand,
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
            intent = self._intent(command, validated_at=now)
            issued_id = (
                self._identifiers.new()
                if isinstance(
                    intent.mutation,
                    (CreateNoteMutation, CreateBookmarkMutation, CreateCollectionMutation),
                )
                else None
            )
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
            raise PersonalWorkspaceError(
                PersonalWorkspaceErrorCode.INVALID_REQUEST,
                "The workspace change is not valid.",
                reference=error.reference,
            ) from error
        except Exception as error:
            raise self._unavailable(command.idempotency_key) from error

    def _intent(
        self,
        command: PersonalWorkspaceMutationCommand,
        *,
        validated_at: datetime,
    ) -> WorkspaceMutationIntent:
        mutation = command.mutation
        if isinstance(mutation, CreateNoteCommand):
            resolved = CreateNoteMutation(
                target=self._references.resolve(
                    mutation.selector, validated_at=validated_at
                ),
                title=mutation.title,
                body=mutation.body,
            )
        elif isinstance(mutation, CreateBookmarkCommand):
            resolved = CreateBookmarkMutation(
                target=self._references.resolve(
                    mutation.selector, validated_at=validated_at
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

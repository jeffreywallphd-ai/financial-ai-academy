"""Server-authoritative creation and reading of Project shells."""

from __future__ import annotations

import hashlib
import json
import re

from financial_ai_academy.modules.content.public import (
    LessonErrorCode,
    LessonReadError,
)
from financial_ai_academy.modules.curriculum.public import ProjectBriefPlacement

from ..domain.project import (
    LearningProjectBrief,
    LearningProjectOrigin,
    ProjectCreateIntent,
    ProjectShell,
)
from ..ports.learning_origin import (
    ProjectBriefGatewayPort,
    ProjectPlacementGatewayPort,
)
from ..ports.project_contract import ProjectContractFailure, ProjectContractPort
from ..ports.repositories import ProjectIdempotencyConflict, ProjectRepositoryPort
from ..ports.system import ClockPort, IdentifierPort
from ..public import (
    CreateProjectRequest,
    ListProjectsRequest,
    OpenProjectRequest,
    ProjectError,
    ProjectErrorCode,
)


_IDENTIFIER = re.compile(r"^[a-z0-9][a-z0-9._-]{0,127}$")


class ProjectService:
    def __init__(
        self,
        repository: ProjectRepositoryPort,
        contract: ProjectContractPort,
        briefs: ProjectBriefGatewayPort,
        placements: ProjectPlacementGatewayPort,
        clock: ClockPort,
        identifiers: IdentifierPort,
    ) -> None:
        self._repository = repository
        self._contract = contract
        self._briefs = briefs
        self._placements = placements
        self._clock = clock
        self._identifiers = identifiers

    def create_project(self, request: CreateProjectRequest) -> ProjectShell:
        if not _IDENTIFIER.fullmatch(request.learner_id):
            raise self._invalid("learner")
        try:
            fingerprint = self._fingerprint(request.intent)
            replay = self._repository.get_by_idempotency(
                request.learner_id,
                request.intent.idempotency_key,
            )
            if replay is not None:
                accepted_fingerprint, shell = replay
                if accepted_fingerprint != fingerprint:
                    raise ProjectError(
                        ProjectErrorCode.IMMUTABLE_CONFLICT,
                        "The idempotency key already names a different Project request.",
                        reference=request.intent.idempotency_key,
                    )
                return self._revalidate_shell(shell)
        except ProjectError:
            raise
        except ProjectContractFailure as error:
            raise self._invalid(error.reference) from error
        except Exception as error:
            raise ProjectError(
                ProjectErrorCode.UNAVAILABLE,
                "Project storage is unavailable.",
                reference=request.intent.idempotency_key,
            ) from error
        approved_brief = None
        origin = request.intent.origin
        if isinstance(origin, LearningProjectOrigin):
            try:
                placement = self._placements.resolve(origin.placement_id)
                self._match_placement(origin, placement)
                approved_brief = self._briefs.resolve(origin)
            except ProjectError:
                raise
            except LessonReadError as error:
                code = (
                    ProjectErrorCode.UNAVAILABLE
                    if error.code
                    in {
                        LessonErrorCode.UNAVAILABLE,
                        LessonErrorCode.INTEGRITY_FAILURE,
                    }
                    else ProjectErrorCode.INVALID_REQUEST
                )
                raise ProjectError(
                    code,
                    "The exact learning Project source is unavailable."
                    if code is ProjectErrorCode.UNAVAILABLE
                    else "The learning Project source is not current.",
                    reference=origin.placement_id,
                ) from error
            except ProjectContractFailure as error:
                raise self._invalid(error.reference) from error
            except Exception as error:
                raise ProjectError(
                    ProjectErrorCode.UNAVAILABLE,
                    "The learning Project source is unavailable.",
                    reference=origin.placement_id,
                ) from error
        try:
            intent = self._revalidate_intent(request.intent, approved_brief)
            fingerprint = self._fingerprint(intent)
            now = self._clock.now()
            project_id = self._identifiers.new()
            shell = ProjectShell(
                schema_version="1.0.0",
                project_id=project_id,
                learner_id=request.learner_id,
                title=intent.title,
                charter=intent.charter,
                origin=intent.origin,
                lifecycle="active",
                revision=1,
                created_at=now,
                updated_at=now,
            )
            self._contract.shell_document(shell)
            stored, _created = self._repository.create_if_absent(
                idempotency_key=intent.idempotency_key,
                request_fingerprint=fingerprint,
                shell=shell,
            )
            return self._revalidate_shell(stored)
        except ProjectIdempotencyConflict as error:
            raise ProjectError(
                ProjectErrorCode.IMMUTABLE_CONFLICT,
                "The idempotency key already names a different Project request.",
                reference=request.intent.idempotency_key,
            ) from error
        except ProjectError:
            raise
        except ProjectContractFailure as error:
            raise self._invalid(error.reference) from error
        except Exception as error:
            raise ProjectError(
                ProjectErrorCode.UNAVAILABLE,
                "Project storage is unavailable.",
                reference=request.intent.idempotency_key,
            ) from error

    def list_projects(
        self, request: ListProjectsRequest
    ) -> tuple[ProjectShell, ...]:
        if not _IDENTIFIER.fullmatch(request.learner_id):
            raise self._invalid("learner")
        try:
            return tuple(
                self._revalidate_shell(shell)
                for shell in self._repository.list_for_learner(request.learner_id)
            )
        except ProjectError:
            raise
        except Exception as error:
            raise ProjectError(
                ProjectErrorCode.UNAVAILABLE,
                "Project storage is unavailable.",
            ) from error

    def open_project(self, request: OpenProjectRequest) -> ProjectShell:
        if not _IDENTIFIER.fullmatch(request.learner_id) or not _IDENTIFIER.fullmatch(
            request.project_id
        ):
            raise ProjectError(
                ProjectErrorCode.NOT_FOUND,
                "Project was not found.",
                reference=request.project_id,
            )
        try:
            shell = self._repository.get_for_learner(
                request.learner_id, request.project_id
            )
            if shell is None:
                raise ProjectError(
                    ProjectErrorCode.NOT_FOUND,
                    "Project was not found.",
                    reference=request.project_id,
                )
            return self._revalidate_shell(shell)
        except ProjectError:
            raise
        except Exception as error:
            raise ProjectError(
                ProjectErrorCode.UNAVAILABLE,
                "Project storage is unavailable.",
                reference=request.project_id,
            ) from error

    def _revalidate_intent(
        self,
        intent: ProjectCreateIntent,
        approved_brief: LearningProjectBrief | None,
    ) -> ProjectCreateIntent:
        document = self._contract.intent_document(intent)
        return self._contract.parse_intent(
            self._canonical(document),
            approved_brief=approved_brief,
        )

    def _revalidate_shell(self, shell: ProjectShell) -> ProjectShell:
        document = self._contract.shell_document(shell)
        return self._contract.parse_shell(self._canonical(document))

    def _fingerprint(self, intent: ProjectCreateIntent) -> str:
        return hashlib.sha256(
            self._canonical(self._contract.intent_document(intent))
        ).hexdigest()

    @staticmethod
    def _canonical(value: dict[str, object]) -> bytes:
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")

    @staticmethod
    def _match_placement(
        origin: LearningProjectOrigin,
        placement: ProjectBriefPlacement,
    ) -> None:
        actual = (
            placement.project_brief_schema_version,
            placement.package_id,
            placement.package_version,
            placement.package_digest,
            placement.brief_id,
            placement.brief_version,
            placement.brief_digest,
            placement.curriculum_id,
            placement.curriculum_version,
            placement.curriculum_digest,
            placement.placement_id,
            placement.placement_version,
            placement.placement_digest,
        )
        expected = (
            origin.project_brief_schema_version,
            origin.package_id,
            origin.package_version,
            origin.package_digest,
            origin.brief_id,
            origin.brief_version,
            origin.brief_digest,
            origin.curriculum_id,
            origin.curriculum_version,
            origin.curriculum_digest,
            origin.placement_id,
            origin.placement_version,
            origin.placement_digest,
        )
        if actual != expected:
            raise ProjectError(
                ProjectErrorCode.INVALID_REQUEST,
                "The learning Project source is not current.",
                reference=origin.placement_id,
            )

    @staticmethod
    def _invalid(reference: str) -> ProjectError:
        return ProjectError(
            ProjectErrorCode.INVALID_REQUEST,
            "Project input is invalid.",
            reference=reference,
        )

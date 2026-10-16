"""Server-authoritative creation and reading of Project shells."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import replace
from datetime import datetime, timezone

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
from ..domain.workspace import (
    AddArtifactMutation,
    AddDomainLinkMutation,
    AddNoteMutation,
    AddReferenceMutation,
    EvidenceArtifactFile,
    ExcludedEvidenceArtifact,
    ProjectArtifact,
    ProjectArtifactReference,
    ProjectDomainLinkReference,
    ProjectEvidenceExport,
    ProjectEvidenceExportMaterial,
    ProjectNote,
    ProjectReference,
    ProjectSnapshot,
    ProjectSnapshotCloseIntent,
    ProjectSnapshotMaterial,
    ProjectVersionReference,
    ProjectWorkspace,
    RemoveDomainLinkMutation,
    ReplaceNoteMutation,
    ReplaceReferenceMutation,
    WorkspaceMutationIntent,
)
from ..ports.object_storage import ProjectObjectStoragePort
from ..ports.learning_origin import (
    ProjectBriefGatewayPort,
    ProjectPlacementGatewayPort,
)
from ..ports.project_contract import ProjectContractFailure, ProjectContractPort
from ..ports.repositories import (
    ProjectIdempotencyConflict,
    ProjectRepositoryPort,
    ProjectRevisionConflict,
    StoredProjectArtifact,
)
from ..ports.system import ClockPort, IdentifierPort
from ..public import (
    CloseProjectSnapshotRequest,
    CreateProjectRequest,
    DownloadProjectArtifactRequest,
    ExportProjectSnapshotRequest,
    LearningProjectStartOption,
    ListLearningProjectStartOptionsRequest,
    ListProjectSnapshotsRequest,
    ListProjectsRequest,
    MutateProjectWorkspaceRequest,
    OpenProjectRequest,
    OpenProjectSnapshotRequest,
    OpenProjectWorkspaceRequest,
    ProjectArtifactDownload,
    ProjectEvidenceExportBundle,
    ProjectEvidenceFileContent,
    ProjectError,
    ProjectErrorCode,
    ResolveLearningProjectStartOptionRequest,
    UploadProjectArtifactRequest,
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
        object_storage: ProjectObjectStoragePort | None = None,
    ) -> None:
        self._repository = repository
        self._contract = contract
        self._briefs = briefs
        self._placements = placements
        self._clock = clock
        self._identifiers = identifiers
        self._object_storage = object_storage

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
            option, approved_brief = self._resolve_learning_option(
                origin.placement_id
            )
            if option.origin != origin:
                raise ProjectError(
                    ProjectErrorCode.INVALID_REQUEST,
                    "The learning Project source is not current.",
                    reference=origin.placement_id,
                )
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

    def open_workspace(
        self, request: OpenProjectWorkspaceRequest
    ) -> ProjectWorkspace:
        shell = self._owned_shell(request.learner_id, request.project_id)
        try:
            current = self._repository.get_workspace(
                request.learner_id, request.project_id
            )
            if current is None:
                now = self._clock.now()
                current = self._repository.get_or_create_workspace(
                    ProjectWorkspace(
                        schema_version="1.0.0",
                        project_id=shell.project_id,
                        learner_id=shell.learner_id,
                        workspace_revision=1,
                        notes=(),
                        references=(),
                        artifacts=(),
                        domain_links=(),
                        created_at=now,
                        updated_at=now,
                    )
                )
            return self._revalidate_workspace(current)
        except ProjectError:
            raise
        except ProjectContractFailure as error:
            raise self._integrity(error.reference) from error
        except Exception as error:
            raise self._unavailable(request.project_id) from error

    def mutate_workspace(
        self, request: MutateProjectWorkspaceRequest
    ) -> ProjectWorkspace:
        if isinstance(request.intent.mutation, AddArtifactMutation):
            raise self._invalid("mutation.operation")
        return self._mutate_workspace(
            request.learner_id,
            request.project_id,
            request.intent,
            content=None,
        )

    def upload_artifact(
        self, request: UploadProjectArtifactRequest
    ) -> ProjectWorkspace:
        if not isinstance(request.intent.mutation, AddArtifactMutation):
            raise self._invalid("mutation.operation")
        return self._mutate_workspace(
            request.learner_id,
            request.project_id,
            request.intent,
            content=request.content,
        )

    def download_artifact(
        self, request: DownloadProjectArtifactRequest
    ) -> ProjectArtifactDownload:
        workspace = self.open_workspace(
            OpenProjectWorkspaceRequest(request.learner_id, request.project_id)
        )
        artifact = next(
            (
                item
                for item in workspace.artifacts
                if item.artifact_id == request.artifact_id
                and item.artifact_version == request.artifact_version
            ),
            None,
        )
        if artifact is None or self._object_storage is None:
            raise self._not_found(request.artifact_id)
        try:
            stored = self._repository.get_artifact(
                request.learner_id,
                request.project_id,
                request.artifact_id,
                request.artifact_version,
            )
            if stored is None:
                raise self._not_found(request.artifact_id)
            content = self._object_storage.read(stored.object_key)
            if (
                len(content) != artifact.byte_count
                or hashlib.sha256(content).hexdigest()
                != artifact.content_digest
                or stored.byte_count != artifact.byte_count
                or stored.content_digest != artifact.content_digest
            ):
                raise self._integrity(request.artifact_id)
            return ProjectArtifactDownload(artifact, content)
        except ProjectError:
            raise
        except Exception as error:
            raise self._unavailable(request.artifact_id) from error

    def close_snapshot(
        self, request: CloseProjectSnapshotRequest
    ) -> ProjectSnapshot:
        shell = self._owned_shell(request.learner_id, request.project_id)
        intent = self._revalidate_snapshot_intent(request.intent)
        fingerprint = self._fingerprint_document(
            self._contract.snapshot_close_intent_document(intent)
        )
        try:
            replay = self._repository.get_snapshot_by_idempotency(
                request.learner_id,
                request.project_id,
                intent.idempotency_key,
            )
            if replay is not None:
                accepted_fingerprint, stored = replay
                if accepted_fingerprint != fingerprint:
                    raise self._immutable_conflict(intent.idempotency_key)
                return self._revalidate_snapshot(stored.snapshot)
            workspace = self.open_workspace(
                OpenProjectWorkspaceRequest(
                    request.learner_id, request.project_id
                )
            )
            if shell.revision != intent.expected_project_revision:
                raise self._stale(request.project_id)
            if workspace.workspace_revision != intent.expected_workspace_revision:
                raise self._stale(request.project_id)
            material, material_document = self._snapshot_material(shell, workspace)
            closed_at = self._clock.now()
            snapshot = ProjectSnapshot(
                schema_version="1.0.0",
                snapshot_id=self._identifiers.new(),
                snapshot_digest=self._contract.canonical_digest(
                    material_document
                ),
                snapshot=material,
                closed_at=closed_at,
            )
            snapshot = self._revalidate_snapshot(snapshot)
            stored = self._repository.create_snapshot_if_absent(
                idempotency_key=intent.idempotency_key,
                request_fingerprint=fingerprint,
                expected_workspace_revision=intent.expected_workspace_revision,
                snapshot=snapshot,
                workspace=workspace,
            )
            return self._revalidate_snapshot(stored.snapshot)
        except (ProjectIdempotencyConflict,) as error:
            raise self._immutable_conflict(intent.idempotency_key) from error
        except ProjectRevisionConflict as error:
            raise self._stale(request.project_id) from error
        except ProjectError:
            raise
        except ProjectContractFailure as error:
            raise self._integrity(error.reference) from error
        except Exception as error:
            raise self._unavailable(request.project_id) from error

    def list_snapshots(
        self, request: ListProjectSnapshotsRequest
    ) -> tuple[ProjectSnapshot, ...]:
        self._owned_shell(request.learner_id, request.project_id)
        try:
            return tuple(
                self._revalidate_snapshot(snapshot)
                for snapshot in self._repository.list_snapshots(
                    request.learner_id, request.project_id
                )
            )
        except ProjectError:
            raise
        except Exception as error:
            raise self._unavailable(request.project_id) from error

    def open_snapshot(
        self, request: OpenProjectSnapshotRequest
    ) -> ProjectSnapshot:
        self._owned_shell(request.learner_id, request.project_id)
        try:
            stored = self._repository.get_snapshot(
                request.learner_id, request.project_id, request.snapshot_id
            )
            if stored is None:
                raise self._not_found(request.snapshot_id)
            return self._revalidate_snapshot(stored.snapshot)
        except ProjectError:
            raise
        except Exception as error:
            raise self._unavailable(request.snapshot_id) from error

    def export_snapshot(
        self, request: ExportProjectSnapshotRequest
    ) -> ProjectEvidenceExportBundle:
        self._owned_shell(request.learner_id, request.project_id)
        if self._object_storage is None:
            raise self._unavailable(request.snapshot_id)
        try:
            stored_snapshot = self._repository.get_snapshot(
                request.learner_id, request.project_id, request.snapshot_id
            )
            if stored_snapshot is None:
                raise self._not_found(request.snapshot_id)
            snapshot = self._revalidate_snapshot(stored_snapshot.snapshot)
            workspace = self._revalidate_workspace(stored_snapshot.workspace)
            artifact_files: list[EvidenceArtifactFile] = []
            excluded: list[ExcludedEvidenceArtifact] = []
            files: list[ProjectEvidenceFileContent] = []
            workspace_document = self._contract.workspace_document(workspace)
            artifact_documents = {
                str(item["artifact_id"]): item
                for item in workspace_document["artifacts"]  # type: ignore[index]
            }
            for reference in snapshot.snapshot.artifacts:
                artifact = next(
                    item
                    for item in workspace.artifacts
                    if item.artifact_id == reference.artifact_id
                    and item.artifact_version == reference.artifact_version
                )
                if (
                    artifact.provenance.source_type.value != "learner_created"
                    and artifact.provenance.use_constraints is not None
                ):
                    excluded.append(
                        ExcludedEvidenceArtifact(
                            artifact.artifact_id,
                            artifact.artifact_version,
                            "source_use_restricted",
                        )
                    )
                    continue
                stored = self._repository.get_artifact(
                    request.learner_id,
                    request.project_id,
                    artifact.artifact_id,
                    artifact.artifact_version,
                )
                if stored is None:
                    excluded.append(
                        ExcludedEvidenceArtifact(
                            artifact.artifact_id,
                            artifact.artifact_version,
                            "content_unavailable",
                        )
                    )
                    continue
                try:
                    content = self._object_storage.read(stored.object_key)
                except (OSError, RuntimeError, ValueError):
                    excluded.append(
                        ExcludedEvidenceArtifact(
                            artifact.artifact_id,
                            artifact.artifact_version,
                            "content_unavailable",
                        )
                    )
                    continue
                if (
                    len(content) != artifact.byte_count
                    or hashlib.sha256(content).hexdigest()
                    != artifact.content_digest
                ):
                    raise self._integrity(artifact.artifact_id)
                manifest_digest = self._contract.canonical_digest(
                    artifact_documents[artifact.artifact_id]  # type: ignore[arg-type]
                )
                artifact_files.append(
                    EvidenceArtifactFile(
                        artifact.artifact_id,
                        artifact.artifact_version,
                        manifest_digest,
                        artifact.logical_path,
                        artifact.media_type,
                        artifact.byte_count,
                        artifact.content_digest,
                    )
                )
                files.append(
                    ProjectEvidenceFileContent(
                        artifact.artifact_id,
                        artifact.artifact_version,
                        artifact.logical_path,
                        content,
                    )
                )
            material = ProjectEvidenceExportMaterial(
                project_id=request.project_id,
                snapshot_id=snapshot.snapshot_id,
                snapshot_digest=snapshot.snapshot_digest,
                snapshot_record=snapshot,
                workspace_record=workspace,
                artifact_files=tuple(artifact_files),
                excluded_artifacts=tuple(excluded),
            )
            material_document = {
                "format": material.format,
                "project_id": material.project_id,
                "snapshot_id": material.snapshot_id,
                "snapshot_digest": material.snapshot_digest,
                "snapshot_record": self._contract.snapshot_document(snapshot),
                "workspace_record": workspace_document,
                "artifact_files": [
                    {
                        "artifact_id": item.artifact_id,
                        "artifact_version": item.artifact_version,
                        "manifest_digest": item.manifest_digest,
                        "logical_path": item.logical_path,
                        "media_type": item.media_type,
                        "byte_count": item.byte_count,
                        "content_digest": item.content_digest,
                    }
                    for item in artifact_files
                ],
                "excluded_artifacts": [
                    {
                        "artifact_id": item.artifact_id,
                        "artifact_version": item.artifact_version,
                        "reason": item.reason,
                    }
                    for item in excluded
                ],
            }
            manifest = ProjectEvidenceExport(
                schema_version="1.0.0",
                export_id=self._identifiers.new(),
                export_digest=self._contract.canonical_digest(material_document),
                export=material,
                generated_at=self._clock.now(),
            )
            manifest = self._revalidate_export(manifest)
            return ProjectEvidenceExportBundle(manifest, tuple(files))
        except ProjectError:
            raise
        except ProjectContractFailure as error:
            raise self._integrity(error.reference) from error
        except (StopIteration, KeyError, TypeError) as error:
            raise self._integrity(request.snapshot_id) from error
        except Exception as error:
            raise self._unavailable(request.snapshot_id) from error

    def resolve_learning_project_start_option(
        self, request: ResolveLearningProjectStartOptionRequest
    ) -> LearningProjectStartOption:
        if not _IDENTIFIER.fullmatch(request.placement_id):
            raise self._invalid("placement")
        option, _brief = self._resolve_learning_option(request.placement_id)
        return option

    def list_learning_project_start_options(
        self, _request: ListLearningProjectStartOptionsRequest
    ) -> tuple[LearningProjectStartOption, ...]:
        try:
            placements = self._placements.list()
        except LessonReadError as error:
            raise ProjectError(
                ProjectErrorCode.UNAVAILABLE,
                "Learning Project choices are unavailable.",
                reference="project-start-options",
            ) from error
        except Exception as error:
            raise ProjectError(
                ProjectErrorCode.UNAVAILABLE,
                "Learning Project choices are unavailable.",
                reference="project-start-options",
            ) from error
        return tuple(
            self._resolve_learning_option(placement.placement_id)[0]
            for placement in placements
        )

    def _resolve_learning_option(
        self, placement_id: str
    ) -> tuple[LearningProjectStartOption, LearningProjectBrief]:
        try:
            placement = self._placements.resolve(placement_id)
            source = LearningProjectOrigin(
                project_brief_schema_version=(
                    placement.project_brief_schema_version
                ),
                package_id=placement.package_id,
                package_version=placement.package_version,
                package_digest=placement.package_digest,
                brief_id=placement.brief_id,
                brief_version=placement.brief_version,
                brief_digest=placement.brief_digest,
                curriculum_id=placement.curriculum_id,
                curriculum_version=placement.curriculum_version,
                curriculum_digest=placement.curriculum_digest,
                placement_id=placement.placement_id,
                placement_version=placement.placement_version,
                placement_digest=placement.placement_digest,
                brief_title="pending exact brief validation",
                brief_purpose="pending exact brief validation",
            )
            approved_brief = self._briefs.resolve(source)
            origin = LearningProjectOrigin(
                project_brief_schema_version=approved_brief.schema_version,
                package_id=placement.package_id,
                package_version=placement.package_version,
                package_digest=placement.package_digest,
                brief_id=approved_brief.brief_id,
                brief_version=approved_brief.brief_version,
                brief_digest=approved_brief.brief_digest,
                curriculum_id=placement.curriculum_id,
                curriculum_version=placement.curriculum_version,
                curriculum_digest=placement.curriculum_digest,
                placement_id=placement.placement_id,
                placement_version=placement.placement_version,
                placement_digest=placement.placement_digest,
                brief_title=approved_brief.title,
                brief_purpose=approved_brief.purpose,
            )
            self._match_placement(origin, placement)
            return (
                LearningProjectStartOption(
                    title=approved_brief.title,
                    purpose=approved_brief.purpose,
                    origin=origin,
                ),
                approved_brief,
            )
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
                reference=placement_id,
            ) from error
        except ProjectContractFailure as error:
            raise self._invalid(error.reference) from error
        except Exception as error:
            raise ProjectError(
                ProjectErrorCode.UNAVAILABLE,
                "The learning Project source is unavailable.",
                reference=placement_id,
            ) from error

    def _mutate_workspace(
        self,
        learner_id: str,
        project_id: str,
        supplied_intent: WorkspaceMutationIntent,
        *,
        content: bytes | None,
    ) -> ProjectWorkspace:
        self._owned_shell(learner_id, project_id)
        intent = self._revalidate_workspace_intent(supplied_intent)
        fingerprint = self._fingerprint_document(
            self._contract.workspace_mutation_intent_document(intent)
        )
        try:
            replay = self._repository.get_workspace_mutation_replay(
                learner_id, project_id, intent.idempotency_key
            )
            if replay is not None:
                accepted_fingerprint, workspace = replay
                if accepted_fingerprint != fingerprint:
                    raise self._immutable_conflict(intent.idempotency_key)
                return self._revalidate_workspace(workspace)
            current = self.open_workspace(
                OpenProjectWorkspaceRequest(learner_id, project_id)
            )
            if current.workspace_revision != intent.expected_workspace_revision:
                raise self._stale(project_id)
            now = self._clock.now()
            candidate, artifact = self._apply_mutation(
                current, intent, now, content=content
            )
            stored_artifact = None
            staged = None
            if artifact is not None:
                if self._object_storage is None or content is None:
                    raise self._unavailable(artifact.artifact_id)
                if (
                    len(content) != artifact.byte_count
                    or hashlib.sha256(content).hexdigest()
                    != artifact.content_digest
                ):
                    raise self._integrity(artifact.artifact_id)
                storage_digest = hashlib.sha256(
                    b"project-artifact-v1\0" + content
                ).hexdigest()
                object_key = f"{storage_digest[:2]}/{storage_digest}"
                try:
                    staged = self._object_storage.stage(object_key, content)
                    self._object_storage.finalize(staged)
                except (OSError, RuntimeError, ValueError) as error:
                    if staged is not None:
                        try:
                            self._object_storage.discard_stage(staged)
                        except (OSError, RuntimeError, ValueError):
                            pass
                    raise self._unavailable(artifact.artifact_id) from error
                stored_artifact = StoredProjectArtifact(
                    learner_id,
                    project_id,
                    artifact.artifact_id,
                    artifact.artifact_version,
                    object_key,
                    artifact.content_digest,
                    artifact.byte_count,
                )
            accepted = self._repository.save_workspace_if_revision(
                idempotency_key=intent.idempotency_key,
                request_fingerprint=fingerprint,
                expected_revision=intent.expected_workspace_revision,
                workspace=candidate,
                artifact=stored_artifact,
            )
            return self._revalidate_workspace(accepted)
        except ProjectIdempotencyConflict as error:
            raise self._immutable_conflict(intent.idempotency_key) from error
        except ProjectRevisionConflict as error:
            raise self._stale(project_id) from error
        except ProjectError:
            raise
        except ProjectContractFailure as error:
            raise self._invalid(error.reference) from error
        except Exception as error:
            raise self._unavailable(project_id) from error

    def _apply_mutation(
        self,
        workspace: ProjectWorkspace,
        intent: WorkspaceMutationIntent,
        now: datetime,
        *,
        content: bytes | None,
    ) -> tuple[ProjectWorkspace, ProjectArtifact | None]:
        if now.tzinfo is None or now.utcoffset() is None:
            raise ValueError("Project clock returned an invalid timestamp.")
        mutation = intent.mutation
        notes = workspace.notes
        references = workspace.references
        artifacts = workspace.artifacts
        domain_links = workspace.domain_links
        accepted_artifact = None
        if isinstance(mutation, AddNoteMutation):
            notes = notes + (
                ProjectNote(
                    self._identifiers.new(),
                    1,
                    mutation.title,
                    mutation.body,
                    now,
                    now,
                ),
            )
        elif isinstance(mutation, ReplaceNoteMutation):
            found = False
            updated: list[ProjectNote] = []
            for note in notes:
                if note.note_id != mutation.note_id:
                    updated.append(note)
                    continue
                found = True
                if note.note_version != mutation.expected_note_version:
                    raise self._stale(mutation.note_id)
                updated.append(
                    replace(
                        note,
                        note_version=note.note_version + 1,
                        title=mutation.title,
                        body=mutation.body,
                        updated_at=now,
                    )
                )
            if not found:
                raise self._not_found(mutation.note_id)
            notes = tuple(updated)
        elif isinstance(mutation, AddReferenceMutation):
            references = references + (
                ProjectReference(
                    self._identifiers.new(),
                    1,
                    mutation.title,
                    mutation.url,
                    mutation.source_name,
                    mutation.source_version,
                    mutation.source_digest,
                    mutation.license,
                    mutation.use_constraints,
                    now,
                    now,
                ),
            )
        elif isinstance(mutation, ReplaceReferenceMutation):
            found = False
            updated_references: list[ProjectReference] = []
            for reference in references:
                if reference.reference_id != mutation.reference_id:
                    updated_references.append(reference)
                    continue
                found = True
                if reference.reference_version != mutation.expected_reference_version:
                    raise self._stale(mutation.reference_id)
                updated_references.append(
                    replace(
                        reference,
                        reference_version=reference.reference_version + 1,
                        title=mutation.title,
                        url=mutation.url,
                        source_name=mutation.source_name,
                        source_version=mutation.source_version,
                        source_digest=mutation.source_digest,
                        license=mutation.license,
                        use_constraints=mutation.use_constraints,
                        updated_at=now,
                    )
                )
            if not found:
                raise self._not_found(mutation.reference_id)
            references = tuple(updated_references)
        elif isinstance(mutation, AddArtifactMutation):
            if content is None:
                raise self._invalid("mutation.operation")
            accepted_artifact = ProjectArtifact(
                **{
                    field: getattr(mutation.artifact, field)
                    for field in (
                        "artifact_kind",
                        "logical_path",
                        "media_type",
                        "inspection_mode",
                        "byte_count",
                        "content_digest",
                        "result_classification",
                        "provenance",
                        "environment",
                        "assumptions",
                    )
                },
                artifact_id=self._identifiers.new(),
                artifact_version=1,
                created_at=now,
            )
            artifacts = artifacts + (accepted_artifact,)
        elif isinstance(mutation, AddDomainLinkMutation):
            raise ProjectError(
                ProjectErrorCode.UNAVAILABLE,
                "The referenced Project resource is not available.",
                reference=mutation.link.owner_module,
            )
        elif isinstance(mutation, RemoveDomainLinkMutation):
            retained = tuple(
                link for link in domain_links if link.link_id != mutation.link_id
            )
            if len(retained) == len(domain_links):
                raise self._not_found(mutation.link_id)
            domain_links = retained
        else:
            raise self._invalid("mutation.operation")
        candidate = ProjectWorkspace(
            schema_version="1.0.0",
            project_id=workspace.project_id,
            learner_id=workspace.learner_id,
            workspace_revision=workspace.workspace_revision + 1,
            notes=notes,
            references=references,
            artifacts=artifacts,
            domain_links=domain_links,
            created_at=workspace.created_at,
            updated_at=now,
        )
        return self._revalidate_workspace(candidate), accepted_artifact

    def _snapshot_material(
        self, shell: ProjectShell, workspace: ProjectWorkspace
    ) -> tuple[ProjectSnapshotMaterial, dict[str, object]]:
        shell_document = self._contract.shell_document(shell)
        workspace_document = self._contract.workspace_document(workspace)
        notes = tuple(
            ProjectVersionReference(
                str(item["note_id"]),
                int(item["note_version"]),
                self._contract.canonical_digest(item),
            )
            for item in workspace_document["notes"]  # type: ignore[index]
        )
        references = tuple(
            ProjectVersionReference(
                str(item["reference_id"]),
                int(item["reference_version"]),
                self._contract.canonical_digest(item),
            )
            for item in workspace_document["references"]  # type: ignore[index]
        )
        artifacts = tuple(
            ProjectArtifactReference(
                str(item["artifact_id"]),
                int(item["artifact_version"]),
                self._contract.canonical_digest(item),
                str(item["content_digest"]),
                int(item["byte_count"]),
            )
            for item in workspace_document["artifacts"]  # type: ignore[index]
        )
        domain_links = tuple(
            ProjectDomainLinkReference(
                str(item["link_id"]),
                self._contract.canonical_digest(item),
                str(item["owner_reference_digest"]),
            )
            for item in workspace_document["domain_links"]  # type: ignore[index]
        )
        material = ProjectSnapshotMaterial(
            project_id=shell.project_id,
            learner_id=shell.learner_id,
            project_revision=shell.revision,
            project_shell_digest=self._contract.canonical_digest(shell_document),
            workspace_revision=workspace.workspace_revision,
            workspace_created_at=workspace.created_at,
            workspace_updated_at=workspace.updated_at,
            notes=notes,
            references=references,
            artifacts=artifacts,
            domain_links=domain_links,
        )
        document: dict[str, object] = {
            "project_id": material.project_id,
            "learner_id": material.learner_id,
            "project_revision": material.project_revision,
            "project_shell_digest": material.project_shell_digest,
            "workspace_revision": material.workspace_revision,
            "workspace_created_at": self._timestamp(material.workspace_created_at),
            "workspace_updated_at": self._timestamp(material.workspace_updated_at),
            "notes": [
                {
                    "record_id": item.record_id,
                    "record_version": item.record_version,
                    "record_digest": item.record_digest,
                }
                for item in notes
            ],
            "references": [
                {
                    "record_id": item.record_id,
                    "record_version": item.record_version,
                    "record_digest": item.record_digest,
                }
                for item in references
            ],
            "artifacts": [
                {
                    "artifact_id": item.artifact_id,
                    "artifact_version": item.artifact_version,
                    "manifest_digest": item.manifest_digest,
                    "content_digest": item.content_digest,
                    "byte_count": item.byte_count,
                }
                for item in artifacts
            ],
            "domain_links": [
                {
                    "link_id": item.link_id,
                    "record_digest": item.record_digest,
                    "owner_reference_digest": item.owner_reference_digest,
                }
                for item in domain_links
            ],
        }
        return material, document

    def _owned_shell(self, learner_id: str, project_id: str) -> ProjectShell:
        return self.open_project(OpenProjectRequest(learner_id, project_id))

    def _revalidate_workspace_intent(
        self, intent: WorkspaceMutationIntent
    ) -> WorkspaceMutationIntent:
        document = self._contract.workspace_mutation_intent_document(intent)
        return self._contract.parse_workspace_mutation_intent(
            self._canonical(document)
        )

    def _revalidate_snapshot_intent(
        self, intent: ProjectSnapshotCloseIntent
    ) -> ProjectSnapshotCloseIntent:
        document = self._contract.snapshot_close_intent_document(intent)
        return self._contract.parse_snapshot_close_intent(
            self._canonical(document)
        )

    def _revalidate_workspace(
        self, workspace: ProjectWorkspace
    ) -> ProjectWorkspace:
        return self._contract.parse_workspace(
            self._canonical(self._contract.workspace_document(workspace))
        )

    def _revalidate_snapshot(self, snapshot: ProjectSnapshot) -> ProjectSnapshot:
        return self._contract.parse_snapshot(
            self._canonical(self._contract.snapshot_document(snapshot))
        )

    def _revalidate_export(
        self, exported: ProjectEvidenceExport
    ) -> ProjectEvidenceExport:
        return self._contract.parse_evidence_export(
            self._canonical(self._contract.evidence_export_document(exported))
        )

    @classmethod
    def _fingerprint_document(cls, document: dict[str, object]) -> str:
        return hashlib.sha256(cls._canonical(document)).hexdigest()

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
    def _timestamp(value: datetime) -> str:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Project timestamp must include an offset.")
        rendered = (
            value.astimezone(timezone.utc)
            .isoformat(timespec="microseconds")
            .replace("+00:00", "Z")
        )
        return rendered.replace(".000000Z", "Z")

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

    @staticmethod
    def _not_found(reference: str) -> ProjectError:
        return ProjectError(
            ProjectErrorCode.NOT_FOUND,
            "Project resource was not found.",
            reference=reference,
        )

    @staticmethod
    def _stale(reference: str) -> ProjectError:
        return ProjectError(
            ProjectErrorCode.STALE_REVISION,
            "Project work changed before this request was accepted.",
            reference=reference,
        )

    @staticmethod
    def _immutable_conflict(reference: str) -> ProjectError:
        return ProjectError(
            ProjectErrorCode.IMMUTABLE_CONFLICT,
            "The idempotency key already names different Project work.",
            reference=reference,
        )

    @staticmethod
    def _integrity(reference: str) -> ProjectError:
        return ProjectError(
            ProjectErrorCode.INTEGRITY_FAILURE,
            "Project evidence did not pass integrity checks.",
            reference=reference,
        )

    @staticmethod
    def _unavailable(reference: str) -> ProjectError:
        return ProjectError(
            ProjectErrorCode.UNAVAILABLE,
            "Project storage is unavailable.",
            reference=reference,
        )

"""Resolve safe Project references only through Project public reads."""

from __future__ import annotations

from datetime import datetime

from financial_ai_academy.modules.project.public import (
    OpenProjectRequest,
    OpenProjectSnapshotRequest,
    OpenProjectWorkspaceRequest,
    ProjectOperations,
)

from ..domain.workspace import (
    LearningReference,
    ProjectArtifactReference,
    ProjectSnapshotReference,
    ProjectWorkspaceReference,
    is_canonical_project_logical_path,
)
from ..ports.learning_reference import PersonalWorkspaceSourceUnavailable
from ..public import (
    LearningReferenceSelector,
    ProjectArtifactSelector,
    ProjectSnapshotSelector,
    ProjectWorkspaceSelector,
)


class PublicProjectLearningReferenceGateway:
    """Map learner-bound Project public values to inert saved references."""

    def __init__(self, projects: ProjectOperations) -> None:
        self._projects = projects

    def resolve(
        self,
        selector: LearningReferenceSelector,
        *,
        validated_at: datetime,
        learner_id: str,
    ) -> LearningReference:
        if not isinstance(
            selector,
            (
                ProjectWorkspaceSelector,
                ProjectSnapshotSelector,
                ProjectArtifactSelector,
            ),
        ):
            raise PersonalWorkspaceSourceUnavailable()
        try:
            shell = self._projects.open_project(
                OpenProjectRequest(learner_id, selector.project_id)
            )
            if (
                shell.learner_id != learner_id
                or shell.project_id != selector.project_id
                or shell.lifecycle != "active"
            ):
                raise PersonalWorkspaceSourceUnavailable()
            if isinstance(selector, ProjectWorkspaceSelector):
                workspace = self._projects.open_workspace(
                    OpenProjectWorkspaceRequest(learner_id, selector.project_id)
                )
                self._workspace_matches(workspace, learner_id, selector.project_id)
                return ProjectWorkspaceReference(
                    project_id=shell.project_id,
                    title=shell.title,
                    lifecycle=shell.lifecycle,
                    project_revision=shell.revision,
                    workspace_revision=workspace.workspace_revision,
                    destination=f"/projects/{shell.project_id}#workspace",
                    target_status="available",
                    validated_at=validated_at,
                )
            if isinstance(selector, ProjectSnapshotSelector):
                snapshot = self._projects.open_snapshot(
                    OpenProjectSnapshotRequest(
                        learner_id, selector.project_id, selector.snapshot_id
                    )
                )
                material = snapshot.snapshot
                if (
                    snapshot.snapshot_id != selector.snapshot_id
                    or material.project_id != shell.project_id
                    or material.learner_id != learner_id
                    or material.project_revision > shell.revision
                    or snapshot.closed_at > validated_at
                ):
                    raise PersonalWorkspaceSourceUnavailable()
                return ProjectSnapshotReference(
                    project_id=shell.project_id,
                    snapshot_id=snapshot.snapshot_id,
                    title=shell.title,
                    lifecycle=shell.lifecycle,
                    project_revision=material.project_revision,
                    workspace_revision=material.workspace_revision,
                    snapshot_digest=snapshot.snapshot_digest,
                    closed_at=snapshot.closed_at,
                    destination=(
                        f"/projects/{shell.project_id}#snapshot-{snapshot.snapshot_id}"
                    ),
                    target_status="available",
                    validated_at=validated_at,
                )
            if not isinstance(selector, ProjectArtifactSelector):
                raise PersonalWorkspaceSourceUnavailable()
            workspace = self._projects.open_workspace(
                OpenProjectWorkspaceRequest(learner_id, selector.project_id)
            )
            self._workspace_matches(workspace, learner_id, selector.project_id)
            artifact = next(
                (
                    item
                    for item in workspace.artifacts
                    if item.artifact_id == selector.artifact_id
                    and item.artifact_version == selector.artifact_version
                ),
                None,
            )
            if artifact is None:
                raise PersonalWorkspaceSourceUnavailable()
            if (
                artifact.created_at > validated_at
                or not is_canonical_project_logical_path(artifact.logical_path)
            ):
                raise PersonalWorkspaceSourceUnavailable()
            return ProjectArtifactReference(
                project_id=shell.project_id,
                artifact_id=artifact.artifact_id,
                artifact_version=artifact.artifact_version,
                title=shell.title,
                lifecycle=shell.lifecycle,
                project_revision=shell.revision,
                workspace_revision=workspace.workspace_revision,
                artifact_kind=artifact.artifact_kind.value,
                logical_path=artifact.logical_path,
                media_type=artifact.media_type,
                inspection_mode=artifact.inspection_mode.value,
                byte_count=artifact.byte_count,
                content_digest=artifact.content_digest,
                created_at=artifact.created_at,
                destination=(
                    f"/projects/{shell.project_id}#artifact-"
                    f"{artifact.artifact_id}-v{artifact.artifact_version}"
                ),
                target_status="available",
                validated_at=validated_at,
            )
        except PersonalWorkspaceSourceUnavailable:
            raise
        except Exception as error:
            raise PersonalWorkspaceSourceUnavailable() from error

    @staticmethod
    def _workspace_matches(workspace, learner_id: str, project_id: str) -> None:
        if workspace.learner_id != learner_id or workspace.project_id != project_id:
            raise PersonalWorkspaceSourceUnavailable()

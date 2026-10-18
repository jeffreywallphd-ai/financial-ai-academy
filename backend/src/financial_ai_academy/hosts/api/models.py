"""Validated HTTP models generated into the reviewed OpenAPI snapshot."""

from __future__ import annotations

from dataclasses import asdict
import base64
import binascii
from datetime import date, datetime, timezone
import re
from typing import Annotated, Literal, Union
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    GetJsonSchemaHandler,
    field_serializer,
    field_validator,
    model_serializer,
)
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import CoreSchema

from financial_ai_academy.modules.adaptation.public import (
    ActivityLaunchResolution,
    NavigationStateProjection,
    activity_launch_payload,
    navigation_state_payload,
)
from financial_ai_academy.modules.assessment.public import (
    KnowledgeCheckPresentation,
    KnowledgeCheckResult,
    PracticeDraft,
    PracticePresentation,
    PracticeRetryState,
    ProjectCompletionEvidence,
    ProjectHistory,
    ProjectSnapshotCandidate,
    ProjectSubmissionOutcome,
)
from financial_ai_academy.modules.assessment.domain.project_submission import (
    ProjectValidationResult,
    SnapshotResource,
)
from financial_ai_academy.modules.content import public as content_public
from financial_ai_academy.modules.curriculum.public import (
    AppliedLearningOpportunityQuery,
    CurriculumGraph,
    LearningOpportunityBrowse,
    LearningOpportunityQueryPage,
    LearningOpportunityRecord,
    LessonReadingResult,
    PracticeReviewTarget,
    curriculum_graph_payload,
)
from financial_ai_academy.modules.learner_model.public import (
    AssistancePreferenceExport,
    AssistancePreferenceHistory,
    AssistancePreferenceMutationIntent,
    AssistancePreferenceProfile,
    LearnerPreferenceProfile,
    LessonCompletionView,
    PreferenceExport,
    PreferenceHistory,
    PreferenceMutationIntent,
    PresentationPreferenceExport,
    PresentationPreferenceHistory,
    PresentationPreferenceMutationIntent,
    PresentationPreferenceProfile,
    PracticeHistoryView,
    ProjectCompletionView,
)
from financial_ai_academy.modules.learner_model.domain.assistance_preferences import (
    AssistancePreferenceMutation,
)
from financial_ai_academy.modules.learner_model.domain.preferences import (
    PreferenceMutation,
)
from financial_ai_academy.modules.learner_model.domain.presentation_preferences import (
    PresentationPreferenceMutation,
)
from financial_ai_academy.modules.project.public import (
    IndependentProjectOrigin,
    LearningProjectOrigin,
    LearningProjectStartOption,
    ProjectCreateIntent,
    ProjectShell,
    ProjectEvidenceExportBundle,
)
from financial_ai_academy.modules.project.domain.workspace import (
    AddArtifactMutation,
    AddDomainLinkMutation,
    AddNoteMutation,
    AddReferenceMutation,
    ArtifactKind,
    ArtifactProvenance,
    DomainLinkType,
    EvidenceClassification,
    InspectionMode,
    ProjectArtifactInput,
    ProjectDomainLinkInput,
    ProjectEnvironment,
    ProjectEvidenceExport,
    ProjectSnapshot,
    ProjectSnapshotCloseIntent,
    ProjectWorkspace,
    ProvenanceSourceType,
    RemoveDomainLinkMutation,
    ReplaceNoteMutation,
    ReplaceReferenceMutation,
    WorkspaceMutationIntent,
)
from financial_ai_academy.modules.personal_workspace.domain.workspace import (
    ArchiveRecordMutation as PersonalArchiveRecordMutation,
    CreateCollectionMutation as PersonalCreateCollectionMutation,
    RemoveCollectionMutation as PersonalRemoveCollectionMutation,
    RemoveRecordMutation as PersonalRemoveRecordMutation,
    RefreshReferenceMutation as PersonalRefreshReferenceMutation,
    RenameCollectionMutation as PersonalRenameCollectionMutation,
    ReorderRecordsMutation as PersonalReorderRecordsMutation,
    RestoreRecordMutation as PersonalRestoreRecordMutation,
    SetCollectionMembersMutation as PersonalSetCollectionMembersMutation,
    UpdateBookmarkMutation as PersonalUpdateBookmarkMutation,
    UpdateNoteMutation as PersonalUpdateNoteMutation,
    is_canonical_project_logical_path,
)
from financial_ai_academy.modules.personal_workspace.public import (
    CreateBookmarkCommand as PersonalCreateBookmarkCommand,
    CreateNoteCommand as PersonalCreateNoteCommand,
    LearningOpportunitySelector as PersonalLearningOpportunitySelector,
    PersonalWorkspace,
    PersonalWorkspaceMutationCommand,
    WorkspaceExportView as PersonalWorkspaceExportView,
    PlacedLessonSelector as PersonalPlacedLessonSelector,
    ProjectArtifactSelector as PersonalProjectArtifactSelector,
    ProjectSnapshotSelector as PersonalProjectSnapshotSelector,
    ProjectWorkspaceSelector as PersonalProjectWorkspaceSelector,
    WorkspaceQuery as PersonalWorkspaceQuery,
    WorkspaceQueryResult as PersonalWorkspaceQueryResult,
)


class ApiModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


def _project_timestamp_json(value: datetime) -> str:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("Project timestamps must include an offset.")
    normalized = value.astimezone(timezone.utc)
    if normalized.microsecond:
        rendered = normalized.strftime("%Y-%m-%dT%H:%M:%S.%f").rstrip("0")
    else:
        rendered = normalized.strftime("%Y-%m-%dT%H:%M:%S")
    return f"{rendered}Z"


class ProjectTimestampModel(ApiModel):
    """Keep Project JSON timestamps aligned with its canonical contracts."""

    @field_serializer("*", check_fields=False, when_used="json")
    def _serialize_project_timestamp_fields(self, value: object):
        # Omitting the return annotation preserves the OpenAPI date-time schema.
        if isinstance(value, datetime):
            return _project_timestamp_json(value)
        return value


def _learner_preference_timestamp_json(value: datetime) -> str:
    """Preserve the exact timestamp text covered by preference digests."""

    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("Learner preference timestamps must include an offset.")
    normalized = value.astimezone(timezone.utc)
    if normalized.microsecond:
        rendered = normalized.strftime("%Y-%m-%dT%H:%M:%S.%f")
    else:
        rendered = normalized.strftime("%Y-%m-%dT%H:%M:%S")
    return f"{rendered}Z"


class LearnerPreferenceTimestampModel(ApiModel):
    """Keep preference response timestamps aligned with canonical digests."""

    @field_serializer("*", check_fields=False, when_used="json")
    def _serialize_learner_preference_timestamp_fields(self, value: object):
        # Omitting the return annotation preserves the OpenAPI date-time schema.
        if isinstance(value, datetime):
            return _learner_preference_timestamp_json(value)
        return value


class ApiErrorEnvelope(ApiModel):
    error_version: Literal["1.0"] = "1.0"
    code: str = Field(min_length=1, max_length=80)
    message: str = Field(min_length=1, max_length=240)
    correlation_id: str = Field(min_length=36, max_length=36)


class SessionBootstrapRequestModel(ApiModel):
    limitation_acknowledged: Literal[True]


class SessionBootstrapResponseModel(ApiModel):
    status: Literal["ready"] = "ready"
    authentication_method: Literal["single_profile"] = "single_profile"
    expires_at: datetime


class IndependentProjectOriginModel(ApiModel):
    origin_type: Literal["independent"] = "independent"


class LearningProjectOriginModel(ApiModel):
    origin_type: Literal["learning"] = "learning"
    project_brief_schema_version: Literal["1.0.0"]
    package_id: str = Field(min_length=1, max_length=128, pattern=r"^[a-z0-9][a-z0-9._-]*$")
    package_version: str = Field(pattern=r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
    package_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    brief_id: str = Field(min_length=1, max_length=128, pattern=r"^[a-z0-9][a-z0-9._-]*$")
    brief_version: str = Field(pattern=r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
    brief_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    curriculum_id: str = Field(min_length=1, max_length=128, pattern=r"^[a-z0-9][a-z0-9._-]*$")
    curriculum_version: str = Field(pattern=r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
    curriculum_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    placement_id: str = Field(min_length=1, max_length=128, pattern=r"^[a-z0-9][a-z0-9._-]*$")
    placement_version: str = Field(pattern=r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
    placement_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    brief_title: str = Field(min_length=1, max_length=120)
    brief_purpose: str = Field(min_length=1, max_length=2000)


ProjectOriginModel = Annotated[
    Union[IndependentProjectOriginModel, LearningProjectOriginModel],
    Field(discriminator="origin_type"),
]


class ProjectCreateRequestModel(ApiModel):
    schema_version: Literal["1.0.0"]
    idempotency_key: str = Field(min_length=1, max_length=128, pattern=r"^[a-z0-9][a-z0-9._-]*$")
    title: str = Field(min_length=1, max_length=120)
    charter: str = Field(min_length=1, max_length=4000)
    origin: ProjectOriginModel


class ProjectShellResponseModel(ProjectTimestampModel):
    schema_version: Literal["1.0.0"]
    project_id: str
    learner_id: str
    title: str
    charter: str
    origin: ProjectOriginModel
    lifecycle: Literal["active"]
    revision: int = Field(ge=1)
    created_at: datetime
    updated_at: datetime


class ProjectListResponseModel(ApiModel):
    records: list[ProjectShellResponseModel]


class LearningProjectStartOptionResponseModel(ApiModel):
    title: str = Field(min_length=1, max_length=120)
    purpose: str = Field(min_length=1, max_length=2000)
    origin: LearningProjectOriginModel


class LearningProjectStartOptionListResponseModel(ApiModel):
    records: list[LearningProjectStartOptionResponseModel] = Field(
        max_length=500
    )


Identifier = Annotated[
    str,
    Field(min_length=1, max_length=128, pattern=r"^[a-z0-9][a-z0-9._-]*$"),
]
Digest = Annotated[str, Field(pattern=r"^[a-f0-9]{64}$")]


class ProjectNoteResponseModel(ProjectTimestampModel):
    note_id: Identifier
    note_version: int = Field(ge=1)
    title: str = Field(min_length=1, max_length=120)
    body: str = Field(min_length=1, max_length=20000)
    created_at: datetime
    updated_at: datetime


class ProjectReferenceResponseModel(ProjectTimestampModel):
    reference_id: Identifier
    reference_version: int = Field(ge=1)
    title: str = Field(min_length=1, max_length=160)
    url: str = Field(max_length=2048, pattern=r"^https://")
    source_name: str = Field(min_length=1, max_length=160)
    source_version: str | None = Field(default=None, max_length=128)
    source_digest: Digest | None = None
    license: str | None = Field(default=None, max_length=160)
    use_constraints: str | None = Field(default=None, max_length=1000)
    created_at: datetime
    updated_at: datetime


class ArtifactProvenanceModel(ApiModel):
    source_type: Literal["learner_created", "supplied", "external"]
    source_title: str = Field(min_length=1, max_length=160)
    source_version: str | None = Field(default=None, max_length=128)
    source_url: str | None = Field(default=None, max_length=2048, pattern=r"^https://")
    source_digest: Digest | None = None
    license: str | None = Field(default=None, max_length=160)
    use_constraints: str | None = Field(default=None, max_length=1000)


class ProjectEnvironmentModel(ApiModel):
    name: str = Field(min_length=1, max_length=120)
    version: str = Field(min_length=1, max_length=120)
    dependency_digest: Digest | None = None


class ProjectArtifactInputModel(ProjectTimestampModel):
    artifact_kind: Literal[
        "dataset", "notebook", "code", "environment", "result",
        "reflection", "supporting_file",
    ]
    logical_path: str = Field(min_length=1, max_length=240)
    media_type: Literal[
        "application/octet-stream", "application/json", "application/pdf",
        "application/x-ipynb+json", "text/csv", "text/markdown",
        "text/plain", "text/x-python",
    ]
    inspection_mode: Literal["metadata_only", "plain_text"]
    byte_count: int = Field(ge=0, le=10485760)
    content_digest: Digest
    result_classification: Literal[
        "observed", "calculated", "simulated", "predicted", "generated",
        "narrative",
    ] | None = None
    provenance: ArtifactProvenanceModel
    environment: ProjectEnvironmentModel | None = None
    assumptions: list[str] = Field(max_length=20)


class ProjectArtifactResponseModel(ProjectArtifactInputModel):
    artifact_id: Identifier
    artifact_version: int = Field(ge=1)
    created_at: datetime


class ProjectDomainLinkInputModel(ProjectTimestampModel):
    link_type: Literal["context", "input", "comparison", "output"]
    owner_module: Identifier
    resource_type: Identifier
    resource_id: Identifier
    resource_version: str | None = Field(default=None, max_length=128)
    resource_as_of: datetime | None = None
    provenance: str = Field(min_length=1, max_length=1000)


class ProjectDomainLinkResponseModel(ProjectDomainLinkInputModel):
    link_id: Identifier
    owner_reference_digest: Digest
    target_status: Literal["available"]
    validated_at: datetime
    created_at: datetime


class AddProjectNoteModel(ApiModel):
    operation: Literal["add_note"]
    title: str = Field(min_length=1, max_length=120)
    body: str = Field(min_length=1, max_length=20000)


class ReplaceProjectNoteModel(ApiModel):
    operation: Literal["replace_note"]
    note_id: Identifier
    expected_note_version: int = Field(ge=1)
    title: str = Field(min_length=1, max_length=120)
    body: str = Field(min_length=1, max_length=20000)


class AddProjectReferenceModel(ApiModel):
    operation: Literal["add_reference"]
    title: str = Field(min_length=1, max_length=160)
    url: str = Field(max_length=2048, pattern=r"^https://")
    source_name: str = Field(min_length=1, max_length=160)
    source_version: str | None = Field(default=None, max_length=128)
    source_digest: Digest | None = None
    license: str | None = Field(default=None, max_length=160)
    use_constraints: str | None = Field(default=None, max_length=1000)


class ReplaceProjectReferenceModel(AddProjectReferenceModel):
    operation: Literal["replace_reference"]
    reference_id: Identifier
    expected_reference_version: int = Field(ge=1)


class AddProjectArtifactModel(ApiModel):
    operation: Literal["add_artifact"]
    artifact: ProjectArtifactInputModel


class AddProjectDomainLinkModel(ApiModel):
    operation: Literal["add_domain_link"]
    link: ProjectDomainLinkInputModel


class RemoveProjectDomainLinkModel(ApiModel):
    operation: Literal["remove_domain_link"]
    link_id: Identifier


ProjectWorkspaceMutationModel = Annotated[
    Union[
        AddProjectNoteModel,
        ReplaceProjectNoteModel,
        AddProjectReferenceModel,
        ReplaceProjectReferenceModel,
        AddProjectDomainLinkModel,
        RemoveProjectDomainLinkModel,
    ],
    Field(discriminator="operation"),
]


class ProjectWorkspaceMutationRequestModel(ApiModel):
    schema_version: Literal["1.0.0"]
    idempotency_key: Identifier
    expected_workspace_revision: int = Field(ge=1)
    mutation: ProjectWorkspaceMutationModel


class ProjectArtifactMutationRequestModel(ApiModel):
    schema_version: Literal["1.0.0"]
    idempotency_key: Identifier
    expected_workspace_revision: int = Field(ge=1)
    mutation: AddProjectArtifactModel


class ProjectArtifactUploadRequestModel(ApiModel):
    intent: ProjectArtifactMutationRequestModel
    content_base64: str = Field(max_length=13981016)

    @field_validator("content_base64")
    @classmethod
    def bounded_base64(cls, value: str) -> str:
        try:
            decoded = base64.b64decode(value, validate=True)
        except (binascii.Error, ValueError) as error:
            raise ValueError("Artifact content must use canonical base64.") from error
        if len(decoded) > 10485760:
            raise ValueError("Artifact content exceeds the size limit.")
        if base64.b64encode(decoded).decode("ascii") != value:
            raise ValueError("Artifact content must use canonical base64.")
        return value


class ProjectWorkspaceResponseModel(ProjectTimestampModel):
    schema_version: Literal["1.0.0"]
    project_id: Identifier
    learner_id: Identifier
    workspace_revision: int = Field(ge=1)
    notes: list[ProjectNoteResponseModel] = Field(max_length=50)
    references: list[ProjectReferenceResponseModel] = Field(max_length=50)
    artifacts: list[ProjectArtifactResponseModel] = Field(max_length=100)
    domain_links: list[ProjectDomainLinkResponseModel] = Field(max_length=50)
    created_at: datetime
    updated_at: datetime


CurriculumIdentifier = Annotated[
    str,
    Field(
        min_length=3,
        max_length=64,
        pattern=r"^[a-z0-9][a-z0-9._-]{2,63}$",
    ),
]


class PersonalWorkspaceProvenanceModel(ProjectTimestampModel):
    published_by: str = Field(min_length=1, max_length=160)
    published_at: datetime
    content_reviewed_on: date
    educational_use_notice: str = Field(min_length=1, max_length=500)


class PersonalLearningOpportunityReferenceModel(ProjectTimestampModel):
    reference_kind: Literal["learning_opportunity"]
    owner_module: Literal["curriculum"]
    opportunity_id: CurriculumIdentifier
    placement_id: CurriculumIdentifier
    package_id: CurriculumIdentifier
    package_version: str
    package_digest: Digest
    source_fingerprint: Digest
    title: str = Field(min_length=1, max_length=240)
    destination: str = Field(
        pattern=r"^/learn/placements/[a-z0-9][a-z0-9._-]{2,63}$"
    )
    target_status: Literal["available", "stale", "unavailable"]
    provenance: PersonalWorkspaceProvenanceModel
    validated_at: datetime


class PersonalPlacedLessonReferenceModel(ProjectTimestampModel):
    reference_kind: Literal["placed_lesson"]
    owner_module: Literal["curriculum"]
    placement_id: CurriculumIdentifier
    package_id: CurriculumIdentifier
    package_version: str
    package_digest: Digest
    title: str = Field(min_length=1, max_length=240)
    destination: str = Field(
        pattern=r"^/learn/placements/[a-z0-9][a-z0-9._-]{2,63}$"
    )
    target_status: Literal["available", "stale", "unavailable"]
    provenance: PersonalWorkspaceProvenanceModel
    validated_at: datetime


class PersonalProjectWorkspaceReferenceModel(ProjectTimestampModel):
    reference_kind: Literal["project_workspace"]
    owner_module: Literal["project"]
    project_id: Identifier
    title: str = Field(min_length=1, max_length=240)
    lifecycle: Literal["active"]
    project_revision: int = Field(ge=1)
    workspace_revision: int = Field(ge=1)
    destination: str = Field(
        pattern=r"^/projects/[a-z0-9][a-z0-9._-]{0,127}#workspace$"
    )
    target_status: Literal["available", "stale", "unavailable"]
    validated_at: datetime


class PersonalProjectSnapshotReferenceModel(ProjectTimestampModel):
    reference_kind: Literal["project_snapshot"]
    owner_module: Literal["project"]
    project_id: Identifier
    snapshot_id: Identifier
    title: str = Field(min_length=1, max_length=240)
    lifecycle: Literal["active"]
    project_revision: int = Field(ge=1)
    workspace_revision: int = Field(ge=1)
    snapshot_digest: Digest
    closed_at: datetime
    destination: str = Field(
        pattern=(
            r"^/projects/[a-z0-9][a-z0-9._-]{0,127}"
            r"#snapshot-[a-z0-9][a-z0-9._-]{0,127}$"
        )
    )
    target_status: Literal["available", "stale", "unavailable"]
    validated_at: datetime


class PersonalProjectArtifactReferenceModel(ProjectTimestampModel):
    reference_kind: Literal["project_artifact"]
    owner_module: Literal["project"]
    project_id: Identifier
    artifact_id: Identifier
    artifact_version: int = Field(ge=1)
    title: str = Field(min_length=1, max_length=240)
    lifecycle: Literal["active"]
    project_revision: int = Field(ge=1)
    workspace_revision: int = Field(ge=1)
    artifact_kind: Literal[
        "dataset",
        "notebook",
        "code",
        "environment",
        "result",
        "reflection",
        "supporting_file",
    ]
    logical_path: str = Field(min_length=1, max_length=240)
    media_type: Literal[
        "application/octet-stream",
        "application/json",
        "application/pdf",
        "application/x-ipynb+json",
        "text/csv",
        "text/markdown",
        "text/plain",
        "text/x-python",
    ]
    inspection_mode: Literal["metadata_only", "plain_text"]
    byte_count: int = Field(ge=0, le=10485760)
    content_digest: Digest
    created_at: datetime
    destination: str = Field(
        pattern=(
            r"^/projects/[a-z0-9][a-z0-9._-]{0,127}"
            r"#artifact-[a-z0-9][a-z0-9._-]{0,127}-v[1-9][0-9]*$"
        )
    )
    target_status: Literal["available", "stale", "unavailable"]
    validated_at: datetime

    @field_validator("logical_path")
    @classmethod
    def validate_logical_path(cls, value: str) -> str:
        if not is_canonical_project_logical_path(value):
            raise ValueError("logical_path must be a canonical relative path")
        return value


PersonalLearningReferenceModel = Annotated[
    Union[
        PersonalLearningOpportunityReferenceModel,
        PersonalPlacedLessonReferenceModel,
        PersonalProjectWorkspaceReferenceModel,
        PersonalProjectSnapshotReferenceModel,
        PersonalProjectArtifactReferenceModel,
    ],
    Field(discriminator="reference_kind"),
]


class PersonalWorkspaceNoteModel(ProjectTimestampModel):
    record_kind: Literal["note"]
    record_id: Identifier
    title: str = Field(min_length=1, max_length=120)
    body: str = Field(min_length=1, max_length=8000)
    target: PersonalLearningReferenceModel
    archived: bool
    created_at: datetime
    updated_at: datetime


class PersonalWorkspaceBookmarkModel(ProjectTimestampModel):
    record_kind: Literal["bookmark"]
    record_id: Identifier
    target: PersonalLearningReferenceModel
    label: str | None = Field(max_length=120)
    archived: bool
    created_at: datetime
    updated_at: datetime


PersonalWorkspaceRecordModel = Annotated[
    Union[PersonalWorkspaceNoteModel, PersonalWorkspaceBookmarkModel],
    Field(discriminator="record_kind"),
]


class PersonalWorkspaceCollectionModel(ProjectTimestampModel):
    collection_id: Identifier
    title: str = Field(min_length=1, max_length=120)
    member_record_ids: list[Identifier] = Field(max_length=100)
    created_at: datetime
    updated_at: datetime


class PersonalWorkspaceResponseModel(ProjectTimestampModel):
    schema_version: Literal["1.0.0"]
    workspace_id: Identifier
    learner_id: Identifier
    revision: int = Field(ge=1)
    records: list[PersonalWorkspaceRecordModel] = Field(max_length=200)
    collections: list[PersonalWorkspaceCollectionModel] = Field(max_length=50)
    created_at: datetime
    updated_at: datetime
    workspace_digest: Digest


class PersonalWorkspaceExportResponseModel(ProjectTimestampModel):
    schema_version: Literal["1.0.0"]
    workspace_digest: Digest
    generated_at: datetime
    workspace: PersonalWorkspaceResponseModel


class PersonalWorkspaceQueryRequestModel(ApiModel):
    schema_version: Literal["1.0.0"]
    text: str = Field(
        default_factory=lambda: None,
        min_length=1,
        max_length=240,
    )
    record_kinds: tuple[Literal["note", "bookmark"], ...] = Field(
        default_factory=tuple, min_length=1, max_length=2
    )
    owner_modules: tuple[Literal["curriculum", "project"], ...] = Field(
        default_factory=tuple, min_length=1, max_length=2
    )
    reference_kinds: tuple[
        Literal[
            "learning_opportunity",
            "placed_lesson",
            "project_workspace",
            "project_snapshot",
            "project_artifact",
        ],
        ...,
    ] = Field(default_factory=tuple, min_length=1, max_length=5)
    target_statuses: tuple[
        Literal["available", "stale", "unavailable"], ...
    ] = Field(default_factory=tuple, min_length=1, max_length=3)
    archived: bool = Field(default_factory=lambda: None)
    collection_id: Identifier = Field(default_factory=lambda: None)
    sort: Literal[
        "workspace_order",
        "updated_desc",
        "updated_asc",
        "title_asc",
        "source_asc",
    ] = "workspace_order"
    limit: int = Field(default=50, ge=1, le=100)
    cursor: str = Field(
        default_factory=lambda: None,
        min_length=1,
        max_length=512,
        pattern=r"^[A-Za-z0-9_-]+$",
    )

    @model_serializer(mode="wrap")
    def omit_absent_query_fields(self, handler):
        serialized = handler(self)
        return {
            key: value
            for key, value in serialized.items()
            if value is not None and value != []
        }

    @field_validator(
        "record_kinds",
        "owner_modules",
        "reference_kinds",
        "target_statuses",
    )
    @classmethod
    def require_unique_query_values(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if len(value) != len(set(value)):
            raise ValueError("query filters must contain unique values")
        return value


class PersonalWorkspaceQueryResponseModel(ProjectTimestampModel):
    schema_version: Literal["1.0.0"]
    workspace_revision: int = Field(ge=1)
    query_digest: Digest
    applied_query: PersonalWorkspaceQueryRequestModel
    records: list[PersonalWorkspaceRecordModel] = Field(max_length=100)
    next_cursor: str | None = Field(
        min_length=1,
        max_length=512,
        pattern=r"^[A-Za-z0-9_-]+$",
    )


class PersonalLearningOpportunitySelectorModel(ApiModel):
    reference_kind: Literal["learning_opportunity"]
    opportunity_id: CurriculumIdentifier
    placement_id: CurriculumIdentifier


class PersonalPlacedLessonSelectorModel(ApiModel):
    reference_kind: Literal["placed_lesson"]
    placement_id: CurriculumIdentifier


class PersonalProjectWorkspaceSelectorModel(ApiModel):
    reference_kind: Literal["project_workspace"]
    project_id: Identifier


class PersonalProjectSnapshotSelectorModel(ApiModel):
    reference_kind: Literal["project_snapshot"]
    project_id: Identifier
    snapshot_id: Identifier


class PersonalProjectArtifactSelectorModel(ApiModel):
    reference_kind: Literal["project_artifact"]
    project_id: Identifier
    artifact_id: Identifier
    artifact_version: int = Field(ge=1)


PersonalLearningReferenceSelectorModel = Annotated[
    Union[
        PersonalLearningOpportunitySelectorModel,
        PersonalPlacedLessonSelectorModel,
        PersonalProjectWorkspaceSelectorModel,
        PersonalProjectSnapshotSelectorModel,
        PersonalProjectArtifactSelectorModel,
    ],
    Field(discriminator="reference_kind"),
]


class PersonalCreateNoteModel(ApiModel):
    operation: Literal["create_note"]
    selector: PersonalLearningReferenceSelectorModel
    title: str = Field(min_length=1, max_length=120)
    body: str = Field(min_length=1, max_length=8000)


class PersonalUpdateNoteModel(ApiModel):
    operation: Literal["update_note"]
    record_id: Identifier
    title: str = Field(min_length=1, max_length=120)
    body: str = Field(min_length=1, max_length=8000)


class PersonalCreateBookmarkModel(ApiModel):
    operation: Literal["create_bookmark"]
    selector: PersonalLearningReferenceSelectorModel
    label: str | None = Field(max_length=120)


class PersonalUpdateBookmarkModel(ApiModel):
    operation: Literal["update_bookmark"]
    record_id: Identifier
    label: str | None = Field(max_length=120)


class PersonalCreateCollectionModel(ApiModel):
    operation: Literal["create_collection"]
    title: str = Field(min_length=1, max_length=120)


class PersonalRenameCollectionModel(ApiModel):
    operation: Literal["rename_collection"]
    collection_id: Identifier
    title: str = Field(min_length=1, max_length=120)


class PersonalRemoveCollectionModel(ApiModel):
    operation: Literal["remove_collection"]
    collection_id: Identifier


class PersonalSetCollectionMembersModel(ApiModel):
    operation: Literal["set_collection_members"]
    collection_id: Identifier
    # Admit the bounded next-item attempt so the application can return the
    # specific collection capacity outcome instead of a generic shape error.
    member_record_ids: list[Identifier] = Field(max_length=200)


class PersonalReorderRecordsModel(ApiModel):
    operation: Literal["reorder_records"]
    record_ids: list[Identifier] = Field(max_length=200)


class PersonalArchiveRecordModel(ApiModel):
    operation: Literal["archive_record"]
    record_id: Identifier


class PersonalRestoreRecordModel(ApiModel):
    operation: Literal["restore_record"]
    record_id: Identifier


class PersonalRemoveRecordModel(ApiModel):
    operation: Literal["remove_record"]
    record_id: Identifier


class PersonalRefreshReferenceModel(ApiModel):
    operation: Literal["refresh_reference"]
    record_id: Identifier


PersonalWorkspaceMutationModel = Annotated[
    Union[
        PersonalCreateNoteModel,
        PersonalUpdateNoteModel,
        PersonalCreateBookmarkModel,
        PersonalUpdateBookmarkModel,
        PersonalCreateCollectionModel,
        PersonalRenameCollectionModel,
        PersonalRemoveCollectionModel,
        PersonalSetCollectionMembersModel,
        PersonalReorderRecordsModel,
        PersonalArchiveRecordModel,
        PersonalRestoreRecordModel,
        PersonalRemoveRecordModel,
        PersonalRefreshReferenceModel,
    ],
    Field(discriminator="operation"),
]


class PersonalWorkspaceMutationRequestModel(ApiModel):
    schema_version: Literal["1.0.0"]
    idempotency_key: Identifier
    expected_revision: int = Field(ge=1)
    mutation: PersonalWorkspaceMutationModel


def personal_workspace_source_permission(
    model: PersonalWorkspaceMutationRequestModel,
) -> str | None:
    mutation = model.mutation
    if not isinstance(
        mutation, (PersonalCreateNoteModel, PersonalCreateBookmarkModel)
    ):
        return None
    if isinstance(mutation.selector, PersonalLearningOpportunitySelectorModel):
        return "curriculum.discovery.read"
    if isinstance(mutation.selector, PersonalPlacedLessonSelectorModel):
        return "curriculum.lesson.read"
    return "project.read"


class ProjectSnapshotCloseRequestModel(ApiModel):
    schema_version: Literal["1.0.0"]
    idempotency_key: Identifier
    expected_project_revision: int = Field(ge=1)
    expected_workspace_revision: int = Field(ge=1)


class ProjectVersionReferenceModel(ApiModel):
    record_id: Identifier
    record_version: int = Field(ge=1)
    record_digest: Digest


class ProjectArtifactReferenceModel(ApiModel):
    artifact_id: Identifier
    artifact_version: int = Field(ge=1)
    manifest_digest: Digest
    content_digest: Digest
    byte_count: int = Field(ge=0, le=10485760)


class ProjectDomainLinkReferenceModel(ApiModel):
    link_id: Identifier
    record_digest: Digest
    owner_reference_digest: Digest


class ProjectSnapshotMaterialModel(ProjectTimestampModel):
    project_id: Identifier
    learner_id: Identifier
    project_revision: int = Field(ge=1)
    project_shell_digest: Digest
    workspace_revision: int = Field(ge=1)
    workspace_created_at: datetime
    workspace_updated_at: datetime
    notes: list[ProjectVersionReferenceModel] = Field(max_length=50)
    references: list[ProjectVersionReferenceModel] = Field(max_length=50)
    artifacts: list[ProjectArtifactReferenceModel] = Field(max_length=100)
    domain_links: list[ProjectDomainLinkReferenceModel] = Field(max_length=50)


class ProjectSnapshotResponseModel(ProjectTimestampModel):
    schema_version: Literal["1.0.0"]
    snapshot_id: Identifier
    snapshot_digest: Digest
    snapshot: ProjectSnapshotMaterialModel
    closed_at: datetime


class ProjectSnapshotListResponseModel(ApiModel):
    records: list[ProjectSnapshotResponseModel]


class EvidenceArtifactFileModel(ApiModel):
    artifact_id: Identifier
    artifact_version: int = Field(ge=1)
    manifest_digest: Digest
    logical_path: str = Field(min_length=1, max_length=240)
    media_type: str
    byte_count: int = Field(ge=0, le=10485760)
    content_digest: Digest


class ExcludedEvidenceArtifactModel(ApiModel):
    artifact_id: Identifier
    artifact_version: int = Field(ge=1)
    reason: Literal[
        "source_use_restricted", "not_authorized", "content_unavailable"
    ]


class ProjectEvidenceExportMaterialModel(ApiModel):
    format: Literal["project-evidence-manifest-v1"]
    project_id: Identifier
    snapshot_id: Identifier
    snapshot_digest: Digest
    snapshot_record: ProjectSnapshotResponseModel
    workspace_record: ProjectWorkspaceResponseModel
    artifact_files: list[EvidenceArtifactFileModel] = Field(max_length=100)
    excluded_artifacts: list[ExcludedEvidenceArtifactModel] = Field(max_length=100)


class ProjectEvidenceExportResponseModel(ProjectTimestampModel):
    schema_version: Literal["1.0.0"]
    export_id: Identifier
    export_digest: Digest
    export: ProjectEvidenceExportMaterialModel
    generated_at: datetime


class ProjectEvidenceFileContentModel(ApiModel):
    artifact_id: Identifier
    artifact_version: int = Field(ge=1)
    logical_path: str = Field(min_length=1, max_length=240)
    content_base64: str


class ProjectEvidenceExportBundleResponseModel(ApiModel):
    manifest: ProjectEvidenceExportResponseModel
    files: list[ProjectEvidenceFileContentModel] = Field(max_length=100)


ProjectSubmissionVersion = Annotated[
    str,
    Field(
        min_length=1,
        max_length=64,
        pattern=r"^[0-9]+\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?$",
    ),
]


class ProjectSubmissionProjectResponseModel(ProjectTimestampModel):
    project_id: Identifier
    project_revision: int = Field(ge=1)
    project_shell_digest: Digest
    snapshot_id: Identifier
    snapshot_digest: Digest
    workspace_revision: int = Field(ge=1)
    closed_at: datetime


class ProjectSubmissionOriginResponseModel(ApiModel):
    package_id: Identifier
    package_version: ProjectSubmissionVersion
    package_digest: Digest
    brief_id: Identifier
    brief_version: ProjectSubmissionVersion
    brief_digest: Digest
    curriculum_id: Identifier
    curriculum_version: ProjectSubmissionVersion
    curriculum_digest: Digest
    placement_id: Identifier
    placement_version: ProjectSubmissionVersion
    placement_digest: Digest


class ProjectSubmissionMilestoneResponseModel(ApiModel):
    milestone_id: Identifier
    milestone_version: ProjectSubmissionVersion
    sequence: int = Field(ge=1, le=20)
    title: str = Field(min_length=1, max_length=160, pattern=r"^[^<>\u0000]*$")


class ProjectSubmissionVersionedResourceModel(ApiModel):
    resource_kind: Literal["note", "source"]
    resource_id: Identifier
    resource_version: int = Field(ge=1)
    record_digest: Digest


class ProjectSubmissionArtifactResourceModel(ApiModel):
    resource_kind: Literal["artifact"]
    resource_id: Identifier
    resource_version: int = Field(ge=1)
    record_digest: Digest
    content_digest: Digest
    byte_count: int = Field(ge=0, le=10485760)


PROJECT_SUBMISSION_UTC_TIME_PATTERN = (
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:"
    r"[0-9]{2}(?:\.[0-9]{1,6})?Z$"
)


class ProjectSubmissionDomainResourceBaseModel(ProjectTimestampModel):
    resource_kind: Literal["domain_resource"]
    resource_id: Identifier
    record_digest: Digest
    owner_reference_digest: Digest


class ProjectSubmissionDomainResourceVersionModel(
    ProjectSubmissionDomainResourceBaseModel
):
    resource_version: str = Field(
        min_length=1,
        max_length=128,
        pattern=r"^[^<>\u0000]*$",
    )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        schema = handler(core_schema)
        schema.setdefault("properties", {})["resource_as_of"] = False
        return schema


class ProjectSubmissionDomainResourceAsOfModel(
    ProjectSubmissionDomainResourceBaseModel
):
    resource_as_of: datetime = Field(
        json_schema_extra={
            "minLength": 20,
            "maxLength": 27,
            "pattern": PROJECT_SUBMISSION_UTC_TIME_PATTERN,
        },
    )

    @field_validator("resource_as_of", mode="before")
    @classmethod
    def domain_resource_has_canonical_utc_time(cls, value: object) -> object:
        if isinstance(value, str) and re.fullmatch(
            PROJECT_SUBMISSION_UTC_TIME_PATTERN, value
        ) is None:
            raise ValueError(
                "domain resource as-of time must use canonical UTC JSON"
            )
        return value

    @field_validator("resource_as_of")
    @classmethod
    def domain_resource_time_has_offset(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("domain resource as-of time must include an offset")
        return value

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        schema = handler(core_schema)
        schema.setdefault("properties", {})["resource_version"] = False
        return schema


ProjectSubmissionResourceModel = Union[
    ProjectSubmissionVersionedResourceModel,
    ProjectSubmissionArtifactResourceModel,
    ProjectSubmissionDomainResourceVersionModel,
    ProjectSubmissionDomainResourceAsOfModel,
]


class ProjectSubmissionCandidateResponseModel(ApiModel):
    schema_version: Literal["1.0.0"]
    project: ProjectSubmissionProjectResponseModel
    origin: ProjectSubmissionOriginResponseModel
    policy_id: Literal["assessment-project-closure"]
    policy_version: Literal["1.0.0"]
    milestones: list[ProjectSubmissionMilestoneResponseModel] = Field(
        min_length=1, max_length=20
    )
    resources: list[ProjectSubmissionResourceModel] = Field(
        min_length=1, max_length=200
    )


class ProjectSubmissionSourceRequestModel(ApiModel):
    project_id: Identifier
    snapshot_id: Identifier
    snapshot_digest: Digest
    brief_id: Identifier
    brief_version: ProjectSubmissionVersion
    brief_digest: Digest
    placement_id: Identifier
    placement_version: ProjectSubmissionVersion
    placement_digest: Digest


class ProjectMilestoneEvidenceRequestModel(ApiModel):
    milestone_id: Identifier
    resources: list[ProjectSubmissionResourceModel] = Field(
        min_length=1, max_length=50
    )


class ProjectSubmissionRequestModel(ApiModel):
    schema_version: Literal["1.0.0"]
    submission_id: Identifier
    source: ProjectSubmissionSourceRequestModel
    policy_id: Literal["assessment-project-closure"]
    policy_version: Literal["1.0.0"]
    milestone_evidence: list[ProjectMilestoneEvidenceRequestModel] = Field(
        min_length=1, max_length=20
    )


class ProjectValidationIssueResponseModel(ApiModel):
    code: str = Field(
        min_length=1,
        max_length=96,
        pattern=r"^assessment\.project\.[a-z0-9_]+$",
    )
    reference: str = Field(min_length=1, max_length=120)
    message: str = Field(min_length=1, max_length=160)


class ProjectAcceptedValidationResponseModel(ApiModel):
    schema_version: Literal["1.0.0"]
    status: Literal["accepted"]
    request_fingerprint: Digest
    issues: list[ProjectValidationIssueResponseModel] = Field(max_length=0)


class ProjectRefusedValidationResponseModel(ApiModel):
    schema_version: Literal["1.0.0"]
    status: Literal["refused"]
    issues: list[ProjectValidationIssueResponseModel] = Field(
        min_length=1, max_length=100
    )


ProjectValidationResponseModel = Annotated[
    Union[
        ProjectAcceptedValidationResponseModel,
        ProjectRefusedValidationResponseModel,
    ],
    Field(discriminator="status"),
]


class ProjectCompletionEvidenceResponseModel(ProjectTimestampModel):
    schema_version: Literal["1.0.0"]
    evidence_id: Identifier
    learner_id: Identifier
    submission_id: Identifier
    project_id: Identifier
    snapshot_id: Identifier
    snapshot_digest: Digest
    brief_id: Identifier
    brief_version: ProjectSubmissionVersion
    brief_digest: Digest
    placement_id: Identifier
    placement_version: ProjectSubmissionVersion
    placement_digest: Digest
    policy_id: Literal["assessment-project-closure"]
    policy_version: Literal["1.0.0"]
    milestone_evidence: list[ProjectMilestoneEvidenceRequestModel] = Field(
        min_length=1, max_length=20
    )
    milestone_ids: list[Identifier] = Field(min_length=1, max_length=20)
    request_fingerprint: Digest
    occurrence: int = Field(ge=1)
    accepted_sequence: int = Field(ge=1)
    submitted_at: datetime
    supersedes_submission_id: Identifier | None = Field(
        default=None, exclude_if=lambda value: value is None
    )


class ProjectSubmissionOutcomeResponseModel(ApiModel):
    validation: ProjectValidationResponseModel
    evidence: ProjectCompletionEvidenceResponseModel | None


class ProjectCompletionHistoryItemResponseModel(ProjectTimestampModel):
    evidence_id: Identifier
    submission_id: Identifier
    snapshot_id: Identifier
    snapshot_digest: Digest
    request_fingerprint: Digest
    occurrence: int = Field(ge=1)
    submitted_at: datetime
    supersedes_submission_id: Identifier | None = Field(
        default=None, exclude_if=lambda value: value is None
    )


class ProjectCompletionHistoryResponseModel(ApiModel):
    schema_version: Literal["1.0.0"]
    project_id: Identifier
    items: list[ProjectCompletionHistoryItemResponseModel] = Field(
        min_length=1, max_length=100
    )


class InlineTextModel(ApiModel):
    kind: Literal["text"] = "text"
    value: str


class InlineCodeModel(ApiModel):
    kind: Literal["code"] = "code"
    value: str


class SoftBreakModel(ApiModel):
    kind: Literal["soft_break"] = "soft_break"


class HardBreakModel(ApiModel):
    kind: Literal["hard_break"] = "hard_break"


class EmphasisModel(ApiModel):
    kind: Literal["emphasis"] = "emphasis"
    children: list["InlineNodeModel"]


class StrongModel(ApiModel):
    kind: Literal["strong"] = "strong"
    children: list["InlineNodeModel"]


class SourceLinkModel(ApiModel):
    kind: Literal["source_link"] = "source_link"
    children: list["InlineNodeModel"]
    href: str
    source_id: str


class AssetImageModel(ApiModel):
    kind: Literal["asset_image"] = "asset_image"
    asset_id: str
    alt_text: str


InlineNodeModel = Annotated[
    Union[
        InlineTextModel,
        InlineCodeModel,
        SoftBreakModel,
        HardBreakModel,
        EmphasisModel,
        StrongModel,
        SourceLinkModel,
        AssetImageModel,
    ],
    Field(discriminator="kind"),
]


class HeadingModel(ApiModel):
    kind: Literal["heading"] = "heading"
    level: int = Field(ge=1, le=6)
    children: list[InlineNodeModel]


class ParagraphModel(ApiModel):
    kind: Literal["paragraph"] = "paragraph"
    children: list[InlineNodeModel]


class CodeBlockModel(ApiModel):
    kind: Literal["code_block"] = "code_block"
    code: str
    language: str | None


class ThematicBreakModel(ApiModel):
    kind: Literal["thematic_break"] = "thematic_break"


class ListItemModel(ApiModel):
    blocks: list["BodyNodeModel"]


class BulletListModel(ApiModel):
    kind: Literal["bullet_list"] = "bullet_list"
    items: list[ListItemModel]


class OrderedListModel(ApiModel):
    kind: Literal["ordered_list"] = "ordered_list"
    start: int = Field(ge=1)
    items: list[ListItemModel]


BodyNodeModel = Annotated[
    Union[
        HeadingModel,
        ParagraphModel,
        CodeBlockModel,
        ThematicBreakModel,
        BulletListModel,
        OrderedListModel,
    ],
    Field(discriminator="kind"),
]


class EducationalSourceModel(ApiModel):
    source_id: str
    title: str
    publisher: str
    locator: str
    reviewed_on: date
    license_note: str | None


class PassiveAssetModel(ApiModel):
    asset_id: str
    media_type: Literal["image/png", "image/jpeg", "image/webp"]
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    alt_text: str
    locator: str


class PublicationProvenanceModel(ApiModel):
    published_by: str
    published_at: datetime
    content_reviewed_on: date
    educational_use_notice: str


class LessonReadingResponseModel(ApiModel):
    placement_id: str
    package_id: str
    package_version: str
    package_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    title: str
    objectives: list[str]
    body: list[BodyNodeModel]
    sources: list[EducationalSourceModel]
    assets: list[PassiveAssetModel]
    provenance: PublicationProvenanceModel


GraphIdentifier = Annotated[
    str,
    Field(
        min_length=3,
        max_length=64,
        pattern=r"^[a-z0-9][a-z0-9._-]{2,63}$",
    ),
]
GraphVersion = Annotated[
    str,
    Field(
        pattern=(
            r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\."
            r"(0|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?$"
        )
    ),
]
GraphDigest = Annotated[str, Field(pattern=r"^[a-f0-9]{64}$")]
NavigationIdentifier = Annotated[
    str,
    Field(pattern=r"^[a-z0-9][a-z0-9._:-]{0,127}$"),
]
NavigationVersion = Annotated[
    str,
    Field(
        pattern=(
            r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\."
            r"(0|[1-9][0-9]*)$"
        )
    ),
]
NAVIGATION_TIMESTAMP_PATTERN = (
    r"^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])"
    r"T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]"
    r"(\.[0-9]{1,6})?(Z|[+-]([01][0-9]|2[0-3]):[0-5][0-9])$"
)


class CurriculumObjectiveResponseModel(ApiModel):
    objective_id: GraphIdentifier
    title: str = Field(min_length=1, max_length=240)
    description: str = Field(min_length=1, max_length=1000)


class CurriculumCompetencyResponseModel(ApiModel):
    competency_id: GraphIdentifier
    title: str = Field(min_length=1, max_length=240)
    description: str = Field(min_length=1, max_length=1000)


class LessonActivityReferenceResponseModel(ApiModel):
    reference_kind: Literal["lesson_placement"]
    placement_id: GraphIdentifier
    package_id: GraphIdentifier
    package_version: GraphVersion
    package_digest: GraphDigest


class AssessmentActivityReferenceResponseModel(ApiModel):
    reference_kind: Literal["assessment_placement"]
    placement_id: GraphIdentifier
    assessment_id: GraphIdentifier
    assessment_version: GraphVersion
    definition_digest: GraphDigest


CurriculumActivityReferenceResponseModel = Annotated[
    Union[
        LessonActivityReferenceResponseModel,
        AssessmentActivityReferenceResponseModel,
    ],
    Field(discriminator="reference_kind"),
]


class CurriculumActivityResponseModel(ApiModel):
    activity_id: GraphIdentifier
    title: str = Field(min_length=1, max_length=240)
    kind: Literal["lesson", "assessment"]
    reference: CurriculumActivityReferenceResponseModel


class CurriculumBranchResponseModel(ApiModel):
    branch_id: GraphIdentifier
    title: str = Field(min_length=1, max_length=240)
    kind: Literal["required", "optional"]
    activity_ids: list[GraphIdentifier] = Field(
        min_length=1,
        max_length=500,
        json_schema_extra={"uniqueItems": True},
    )


class CurriculumRelationshipResponseModel(ApiModel):
    relationship_id: GraphIdentifier
    kind: Literal[
        "objective_competency",
        "activity_develops_competency",
        "activity_assesses_competency",
        "competency_prerequisite",
        "activity_prerequisite",
    ]
    source_id: GraphIdentifier
    target_id: GraphIdentifier


class CurriculumPresentationOrderResponseModel(ApiModel):
    objective_ids: list[GraphIdentifier] = Field(
        default_factory=list,
        max_length=100,
        json_schema_extra={"uniqueItems": True},
    )
    competency_ids: list[GraphIdentifier] = Field(
        default_factory=list,
        max_length=200,
        json_schema_extra={"uniqueItems": True},
    )
    activity_ids: list[GraphIdentifier] = Field(
        default_factory=list,
        max_length=500,
        json_schema_extra={"uniqueItems": True},
    )
    branch_ids: list[GraphIdentifier] = Field(
        default_factory=list,
        max_length=100,
        json_schema_extra={"uniqueItems": True},
    )


class CurriculumGraphResponseModel(ApiModel):
    schema_version: Literal["1.0.0"]
    curriculum_id: GraphIdentifier
    curriculum_version: GraphVersion
    title: str = Field(min_length=1, max_length=240)
    summary: str = Field(min_length=20, max_length=500)
    publication_state: Literal["approved"]
    published_at: datetime
    source_references: list[str] = Field(
        min_length=1,
        max_length=20,
        json_schema_extra={"uniqueItems": True},
    )
    presentation_order: CurriculumPresentationOrderResponseModel | None = None
    objectives: list[CurriculumObjectiveResponseModel] = Field(
        min_length=1,
        max_length=100,
    )
    competencies: list[CurriculumCompetencyResponseModel] = Field(
        min_length=1,
        max_length=200,
    )
    activities: list[CurriculumActivityResponseModel] = Field(
        min_length=1,
        max_length=500,
    )
    branches: list[CurriculumBranchResponseModel] = Field(max_length=100)
    relationships: list[CurriculumRelationshipResponseModel] = Field(
        max_length=2000
    )
    graph_digest: GraphDigest


class NavigationReasonResponseModel(ApiModel):
    code: Literal[
        "activity_completed",
        "required_activity",
        "optional_activity",
        "unassigned_activity",
        "activity_source_unavailable",
        "completion_source_unavailable",
        "entry_activity",
        "prerequisite_incomplete",
        "prerequisite_unavailable",
        "prerequisite_satisfied",
    ]
    explanation: str = Field(min_length=1, max_length=240)
    references: list[NavigationIdentifier] = Field(
        min_length=1,
        max_length=10,
        json_schema_extra={"uniqueItems": True},
    )

    @field_validator("references")
    @classmethod
    def references_are_unique(cls, value: list[str]) -> list[str]:
        if len(value) != len(set(value)):
            raise ValueError("Navigation reason references must be unique.")
        return value


class ActivityNavigationStateResponseModel(ApiModel):
    activity_id: NavigationIdentifier
    completion: Literal["completed", "incomplete", "unavailable"]
    eligibility: Literal["eligible", "locked", "unavailable"]
    requirement: Literal["required", "optional", "unassigned"]
    availability: Literal["available", "unavailable"]
    reasons: list[NavigationReasonResponseModel] = Field(
        min_length=2,
        max_length=2002,
    )


class NavigationStateResponseModel(ApiModel):
    schema_version: Literal["1.0.0"]
    curriculum_id: NavigationIdentifier
    curriculum_version: NavigationVersion
    graph_digest: GraphDigest
    policy_id: NavigationIdentifier
    policy_version: NavigationVersion
    evaluated_at: datetime = Field(
        json_schema_extra={"pattern": NAVIGATION_TIMESTAMP_PATTERN}
    )
    source_set_digest: GraphDigest
    activity_states: list[ActivityNavigationStateResponseModel] = Field(
        min_length=1,
        max_length=500,
        json_schema_extra={"uniqueItems": True},
    )
    projection_digest: GraphDigest

    @field_validator("evaluated_at")
    @classmethod
    def evaluated_at_has_offset(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Navigation evaluation time requires an offset.")
        return value

    @field_validator("activity_states")
    @classmethod
    def activity_states_are_unique(
        cls, value: list[ActivityNavigationStateResponseModel]
    ) -> list[ActivityNavigationStateResponseModel]:
        activity_ids = [item.activity_id for item in value]
        if len(activity_ids) != len(set(activity_ids)):
            raise ValueError("Navigation activity states must be unique.")
        return value


class ActivityLaunchResponseModel(ApiModel):
    schema_version: Literal["1.0.0"]
    curriculum_id: NavigationIdentifier
    curriculum_version: NavigationVersion
    graph_digest: GraphDigest
    activity_id: NavigationIdentifier
    navigation_projection_digest: GraphDigest
    evaluated_at: datetime = Field(
        json_schema_extra={"pattern": NAVIGATION_TIMESTAMP_PATTERN}
    )
    placement_id: NavigationIdentifier
    package_id: NavigationIdentifier
    package_version: GraphVersion
    package_digest: GraphDigest
    destination: str = Field(
        pattern=r"^/learn/placements/[a-z0-9][a-z0-9._:-]{0,127}$",
        max_length=146,
    )

    @field_validator("evaluated_at")
    @classmethod
    def evaluated_at_has_offset(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Activity launch evaluation time requires an offset.")
        return value

class DiscoveryProvenanceResponseModel(ApiModel):
    published_by: str = Field(min_length=1, max_length=160)
    published_at: datetime
    content_reviewed_on: date
    educational_use_notice: str = Field(min_length=1, max_length=500)


DiscoveryObjective = Annotated[str, Field(min_length=1, max_length=500)]
DiscoveryTopic = Annotated[
    str,
    Field(pattern=r"^[a-z0-9][a-z0-9-]{1,49}$"),
]


class LearningOpportunityResponseModel(ApiModel):
    schema_version: Literal["1.0.0"]
    opportunity_id: str = Field(
        min_length=3,
        max_length=64,
        pattern=r"^[a-z0-9][a-z0-9._-]{2,63}$",
    )
    placement_id: str = Field(
        min_length=3,
        max_length=64,
        pattern=r"^[a-z0-9][a-z0-9._-]{2,63}$",
    )
    destination: str = Field(
        pattern=r"^/learn/placements/[a-z0-9][a-z0-9._-]{2,63}$",
    )
    kind: Literal["course", "lesson", "lab", "project"]
    title: str = Field(min_length=1, max_length=240)
    summary: str = Field(min_length=20, max_length=500)
    objectives: list[DiscoveryObjective] = Field(
        min_length=1,
        max_length=20,
        json_schema_extra={"uniqueItems": True},
    )
    topics: list[DiscoveryTopic] = Field(
        min_length=1,
        max_length=8,
        json_schema_extra={"uniqueItems": True},
    )
    level: Literal["introductory", "intermediate", "advanced"]
    estimated_minutes: int = Field(ge=1, le=1440)
    prerequisite_summary: str = Field(min_length=2, max_length=500)
    availability: Literal["available", "unavailable", "planned"]
    availability_reason: str = Field(min_length=10, max_length=500)
    package_id: str = Field(
        min_length=3,
        max_length=64,
        pattern=r"^[a-z0-9][a-z0-9._-]{2,63}$",
    )
    package_version: str = Field(
        pattern=(
            r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\."
            r"(0|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?$"
        )
    )
    package_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    provenance: DiscoveryProvenanceResponseModel
    source_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    projected_at: datetime

    @field_validator("objectives", "topics")
    @classmethod
    def require_unique_values(cls, values: list[str]) -> list[str]:
        if len(values) != len(set(values)):
            raise ValueError("Discovery list values must be unique.")
        return values


class LearningOpportunityBrowseResponseModel(ApiModel):
    schema_version: Literal["1.0.0"]
    projection_generation: str = Field(pattern=r"^[a-f0-9]{64}$")
    projected_at: datetime
    records: list[LearningOpportunityResponseModel] = Field(max_length=500)


class AppliedLearningOpportunityQueryResponseModel(ApiModel):
    query: str | None = Field(min_length=1, max_length=100)
    prerequisite_query: str | None = Field(
        min_length=1,
        max_length=100,
    )
    topics: list[DiscoveryTopic] = Field(
        max_length=8,
        json_schema_extra={"uniqueItems": True},
    )
    levels: list[
        Literal["introductory", "intermediate", "advanced"]
    ] = Field(max_length=8, json_schema_extra={"uniqueItems": True})
    kinds: list[Literal["course", "lesson", "lab", "project"]] = Field(
        max_length=8,
        json_schema_extra={"uniqueItems": True},
    )
    availabilities: list[
        Literal["available", "unavailable", "planned"]
    ] = Field(max_length=8, json_schema_extra={"uniqueItems": True})
    minimum_minutes: int | None = Field(ge=1, le=1440)
    maximum_minutes: int | None = Field(ge=1, le=1440)
    sort: Literal[
        "catalog",
        "title",
        "duration_ascending",
        "duration_descending",
    ]
    page_size: int = Field(ge=1, le=50)

    @field_validator("topics", "levels", "kinds", "availabilities")
    @classmethod
    def require_unique_filters(cls, values: list[str]) -> list[str]:
        if len(values) != len(set(values)):
            raise ValueError("Discovery query filters must be unique.")
        return values


class LearningOpportunityQueryPageResponseModel(ApiModel):
    schema_version: Literal["1.0.0"]
    projection_generation: str = Field(pattern=r"^[a-f0-9]{64}$")
    projected_at: datetime
    applied_query: AppliedLearningOpportunityQueryResponseModel
    total_matches: int = Field(ge=0, le=500)
    records: list[LearningOpportunityResponseModel] = Field(max_length=50)
    next_cursor: str | None = Field(
        min_length=1,
        max_length=1024,
        pattern=r"^[A-Za-z0-9_-]+\.[a-f0-9]{64}$",
    )


class KnowledgeCheckOptionModel(ApiModel):
    option_id: str = Field(
        min_length=3,
        max_length=64,
        pattern=r"^[a-z0-9][a-z0-9._-]{2,63}$",
    )
    label: str = Field(min_length=1, max_length=160)


class KnowledgeCheckPresentationResponseModel(ApiModel):
    schema_version: Literal["1.0.0"] = "1.0.0"
    placement_id: str
    package_id: str
    package_version: Literal["1.1.0"]
    package_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    assessment_id: str
    assessment_version: Literal["1.0.0"]
    definition_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    item_type: Literal["single_select"]
    item_id: str
    item_version: Literal["1.0.0"]
    scoring_policy_id: Literal["single-select-exact-match"]
    scoring_policy_version: Literal["1.0.0"]
    prompt: str = Field(min_length=1, max_length=400)
    options: list[KnowledgeCheckOptionModel] = Field(
        min_length=2, max_length=6
    )


PracticeIdentifier = Annotated[
    str,
    Field(
        min_length=3,
        max_length=64,
        pattern=r"^[a-z0-9][a-z0-9._-]{2,63}$",
    ),
]


class PracticeResourceReferenceModel(ApiModel):
    resource_id: str = Field(
        min_length=3,
        max_length=64,
        pattern=r"^[a-z0-9][a-z0-9._-]{2,63}$",
    )
    resource_version: str = Field(
        pattern=(
            r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\."
            r"(0|[1-9][0-9]*)$"
        )
    )
    resource_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    title: str = Field(
        min_length=1,
        max_length=160,
        pattern=r"^[^<>&\u0000-\u001f\u007f]+$",
    )


class PracticeAttemptPolicyModel(ApiModel):
    policy_id: Literal["formative-retry"]
    policy_version: Literal["1.0.0"]
    max_attempts: int = Field(ge=1, le=10)
    resume_allowed: Literal[True]
    history_visible: Literal[True]


class PracticeOptionModel(ApiModel):
    option_id: str = Field(
        min_length=3,
        max_length=64,
        pattern=r"^[a-z0-9][a-z0-9._-]{2,63}$",
    )
    label: str = Field(
        min_length=1,
        max_length=160,
        pattern=r"^[^<>&\u0000-\u001f\u007f]+$",
    )


class SingleSelectPracticeItemModel(ApiModel):
    item_id: str = Field(
        min_length=3,
        max_length=64,
        pattern=r"^[a-z0-9][a-z0-9._-]{2,63}$",
    )
    item_version: Literal["1.0.0"]
    item_type: Literal["single_select"]
    prompt: str = Field(
        min_length=1,
        max_length=600,
        pattern=r"^[^<>&\u0000-\u001f\u007f]+$",
    )
    scoring_policy_id: Literal["single-select-exact-match"]
    scoring_policy_version: Literal["1.0.0"]
    max_score: Literal[1]
    options: list[PracticeOptionModel] = Field(min_length=2, max_length=8)


class MultipleSelectPracticeItemModel(ApiModel):
    item_id: str = Field(
        min_length=3,
        max_length=64,
        pattern=r"^[a-z0-9][a-z0-9._-]{2,63}$",
    )
    item_version: Literal["1.0.0"]
    item_type: Literal["multiple_select"]
    prompt: str = Field(
        min_length=1,
        max_length=600,
        pattern=r"^[^<>&\u0000-\u001f\u007f]+$",
    )
    scoring_policy_id: Literal["multiple-select-exact-set"]
    scoring_policy_version: Literal["1.0.0"]
    max_score: Literal[1]
    options: list[PracticeOptionModel] = Field(min_length=3, max_length=12)


class NumericPracticeItemModel(ApiModel):
    item_id: str = Field(
        min_length=3,
        max_length=64,
        pattern=r"^[a-z0-9][a-z0-9._-]{2,63}$",
    )
    item_version: Literal["1.0.0"]
    item_type: Literal["numeric_entry"]
    prompt: str = Field(
        min_length=1,
        max_length=600,
        pattern=r"^[^<>&\u0000-\u001f\u007f]+$",
    )
    scoring_policy_id: Literal["numeric-exact-or-inclusive-range"]
    scoring_policy_version: Literal["1.0.0"]
    max_score: Literal[1]
    scale: int = Field(ge=0, le=6)
    unit_label: str = Field(
        min_length=1,
        max_length=160,
        pattern=r"^[^<>&\u0000-\u001f\u007f]+$",
    )
    allow_negative: bool


PracticePresentationItemModel = Annotated[
    Union[
        SingleSelectPracticeItemModel,
        MultipleSelectPracticeItemModel,
        NumericPracticeItemModel,
    ],
    Field(discriminator="item_type"),
]


class PracticePresentationResponseModel(ApiModel):
    schema_version: Literal["1.0.0"]
    placement_id: str = Field(
        min_length=3,
        max_length=64,
        pattern=r"^[a-z0-9][a-z0-9._-]{2,63}$",
    )
    package_id: str = Field(
        min_length=3,
        max_length=64,
        pattern=r"^[a-z0-9][a-z0-9._-]{2,63}$",
    )
    package_version: str = Field(
        pattern=(
            r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\."
            r"(0|[1-9][0-9]*)$"
        )
    )
    package_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    definition_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    practice_id: str = Field(
        min_length=3,
        max_length=64,
        pattern=r"^[a-z0-9][a-z0-9._-]{2,63}$",
    )
    practice_version: Literal["1.0.0"]
    title: str = Field(
        min_length=1,
        max_length=160,
        pattern=r"^[^<>&\u0000-\u001f\u007f]+$",
    )
    purpose: str = Field(
        min_length=1,
        max_length=600,
        pattern=r"^[^<>&\u0000-\u001f\u007f]+$",
    )
    instructions: str = Field(
        min_length=1,
        max_length=600,
        pattern=r"^[^<>&\u0000-\u001f\u007f]+$",
    )
    attempt_policy: PracticeAttemptPolicyModel
    source_references: list[PracticeResourceReferenceModel] = Field(
        min_length=1, max_length=8
    )
    review_references: list[PracticeResourceReferenceModel] = Field(
        min_length=1, max_length=8
    )
    items: list[PracticePresentationItemModel] = Field(
        min_length=1, max_length=20
    )


class SingleSelectPracticeResponseModel(ApiModel):
    item_id: str = Field(
        min_length=3,
        max_length=64,
        pattern=r"^[a-z0-9][a-z0-9._-]{2,63}$",
    )
    item_version: Literal["1.0.0"]
    item_type: Literal["single_select"]
    scoring_policy_id: Literal["single-select-exact-match"]
    scoring_policy_version: Literal["1.0.0"]
    selected_option_id: str = Field(
        min_length=3,
        max_length=64,
        pattern=r"^[a-z0-9][a-z0-9._-]{2,63}$",
    )


class MultipleSelectPracticeResponseModel(ApiModel):
    item_id: str = Field(
        min_length=3,
        max_length=64,
        pattern=r"^[a-z0-9][a-z0-9._-]{2,63}$",
    )
    item_version: Literal["1.0.0"]
    item_type: Literal["multiple_select"]
    scoring_policy_id: Literal["multiple-select-exact-set"]
    scoring_policy_version: Literal["1.0.0"]
    selected_option_ids: list[PracticeIdentifier] = Field(
        min_length=1,
        max_length=12,
        json_schema_extra={"uniqueItems": True},
    )

    @field_validator("selected_option_ids")
    @classmethod
    def selected_options_are_unique(cls, value: list[str]) -> list[str]:
        if len(value) != len(set(value)):
            raise ValueError("selected option identifiers must be unique")
        return value


class NumericEntryPracticeResponseModel(ApiModel):
    item_id: str = Field(
        min_length=3,
        max_length=64,
        pattern=r"^[a-z0-9][a-z0-9._-]{2,63}$",
    )
    item_version: Literal["1.0.0"]
    item_type: Literal["numeric_entry"]
    scoring_policy_id: Literal["numeric-exact-or-inclusive-range"]
    scoring_policy_version: Literal["1.0.0"]
    entered_value: str = Field(
        max_length=40,
        pattern=r"^-?(0|[1-9][0-9]*)(\.[0-9]{1,6})?$",
    )


PracticeSubmissionItemModel = Annotated[
    Union[
        SingleSelectPracticeResponseModel,
        MultipleSelectPracticeResponseModel,
        NumericEntryPracticeResponseModel,
    ],
    Field(discriminator="item_type"),
]


class PracticeSubmissionRequestModel(ApiModel):
    schema_version: Literal["1.0.0"]
    submission_id: UUID
    placement_id: str = Field(
        min_length=3,
        max_length=64,
        pattern=r"^[a-z0-9][a-z0-9._-]{2,63}$",
    )
    package_id: str = Field(
        min_length=3,
        max_length=64,
        pattern=r"^[a-z0-9][a-z0-9._-]{2,63}$",
    )
    package_version: str = Field(
        pattern=(
            r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\."
            r"(0|[1-9][0-9]*)$"
        )
    )
    package_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    definition_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    practice_id: str = Field(
        min_length=3,
        max_length=64,
        pattern=r"^[a-z0-9][a-z0-9._-]{2,63}$",
    )
    practice_version: Literal["1.0.0"]
    attempt_policy_id: Literal["formative-retry"]
    attempt_policy_version: Literal["1.0.0"]
    responses: list[PracticeSubmissionItemModel] = Field(
        min_length=1, max_length=20
    )


class PracticeFeedbackResultModel(ApiModel):
    feedback_id: str = Field(
        min_length=3,
        max_length=64,
        pattern=r"^[a-z0-9][a-z0-9._-]{2,63}$",
    )
    text: str = Field(
        min_length=1,
        max_length=600,
        pattern=r"^[^<>&\u0000-\u001f\u007f]+$",
    )
    review_reference_ids: list[PracticeIdentifier] = Field(
        min_length=1,
        max_length=8,
        json_schema_extra={"uniqueItems": True},
    )

    @field_validator("review_reference_ids")
    @classmethod
    def review_references_are_unique(cls, value: list[str]) -> list[str]:
        if len(value) != len(set(value)):
            raise ValueError("review reference identifiers must be unique")
        return value


class SingleSelectPracticeResultModel(SingleSelectPracticeResponseModel):
    score: int = Field(ge=0, le=1)
    max_score: Literal[1]
    correct: bool
    feedback: PracticeFeedbackResultModel


class MultipleSelectPracticeResultModel(MultipleSelectPracticeResponseModel):
    score: int = Field(ge=0, le=1)
    max_score: Literal[1]
    correct: bool
    feedback: PracticeFeedbackResultModel


class NumericEntryPracticeResultModel(NumericEntryPracticeResponseModel):
    score: int = Field(ge=0, le=1)
    max_score: Literal[1]
    correct: bool
    feedback: PracticeFeedbackResultModel


PracticeSubmissionItemResultModel = Annotated[
    Union[
        SingleSelectPracticeResultModel,
        MultipleSelectPracticeResultModel,
        NumericEntryPracticeResultModel,
    ],
    Field(discriminator="item_type"),
]


class PracticeSubmissionResultResponseModel(ApiModel):
    schema_version: Literal["1.0.0"]
    attempt_id: UUID
    evidence_id: UUID
    submission_id: UUID
    placement_id: str = Field(
        min_length=3,
        max_length=64,
        pattern=r"^[a-z0-9][a-z0-9._-]{2,63}$",
    )
    package_id: str = Field(
        min_length=3,
        max_length=64,
        pattern=r"^[a-z0-9][a-z0-9._-]{2,63}$",
    )
    package_version: str = Field(
        pattern=(
            r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\."
            r"(0|[1-9][0-9]*)$"
        )
    )
    package_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    definition_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    practice_id: str = Field(
        min_length=3,
        max_length=64,
        pattern=r"^[a-z0-9][a-z0-9._-]{2,63}$",
    )
    practice_version: Literal["1.0.0"]
    attempt_policy_id: Literal["formative-retry"]
    attempt_policy_version: Literal["1.0.0"]
    score: int = Field(ge=0, le=20)
    max_score: int = Field(ge=1, le=20)
    outcome: Literal["all_correct", "review_needed"]
    review_reference_ids: list[PracticeIdentifier] = Field(
        min_length=1,
        max_length=8,
        json_schema_extra={"uniqueItems": True},
    )
    item_results: list[PracticeSubmissionItemResultModel] = Field(
        min_length=1, max_length=20
    )
    submitted_at: datetime

    @field_validator("review_reference_ids")
    @classmethod
    def result_review_references_are_unique(
        cls, value: list[str]
    ) -> list[str]:
        if len(value) != len(set(value)):
            raise ValueError("review reference identifiers must be unique")
        return value


class PracticeProgressScopeModel(ApiModel):
    schema_version: Literal["1.0.0"]
    placement_id: PracticeIdentifier
    package_id: PracticeIdentifier
    package_version: str = Field(
        pattern=(
            r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\."
            r"(0|[1-9][0-9]*)$"
        )
    )
    package_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    definition_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    practice_id: PracticeIdentifier
    practice_version: Literal["1.0.0"]
    attempt_policy_id: Literal["formative-retry"]
    attempt_policy_version: Literal["1.0.0"]


class PracticeDraftSaveRequestModel(PracticeProgressScopeModel):
    expected_revision: int = Field(ge=0)
    responses: list[PracticeSubmissionItemModel] = Field(max_length=20)


class PracticeDraftResponseModel(PracticeProgressScopeModel):
    responses: list[PracticeSubmissionItemModel] = Field(max_length=20)
    revision: int = Field(ge=1)
    saved_at: datetime
    response_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")


class PracticeRetryStateResponseModel(PracticeProgressScopeModel):
    attempts_used: int = Field(ge=0, le=10)
    max_attempts: int = Field(ge=1, le=10)
    attempts_remaining: int = Field(ge=0, le=10)
    can_retry: bool
    state: Literal["available", "exhausted"]


class PracticeHistoryItemSummaryBaseModel(ApiModel):
    item_id: PracticeIdentifier
    item_version: Literal["1.0.0"]
    scoring_policy_version: Literal["1.0.0"]
    score: int = Field(ge=0, le=1)
    max_score: Literal[1]
    correct: bool
    review_reference_ids: list[PracticeIdentifier] = Field(
        max_length=8,
        json_schema_extra={"uniqueItems": True},
    )

    @field_validator("review_reference_ids")
    @classmethod
    def history_review_references_are_unique(
        cls, value: list[str]
    ) -> list[str]:
        if len(value) != len(set(value)):
            raise ValueError("review reference identifiers must be unique")
        return value


class SingleSelectPracticeHistoryItemModel(
    PracticeHistoryItemSummaryBaseModel
):
    item_type: Literal["single_select"]
    scoring_policy_id: Literal["single-select-exact-match"]


class MultipleSelectPracticeHistoryItemModel(
    PracticeHistoryItemSummaryBaseModel
):
    item_type: Literal["multiple_select"]
    scoring_policy_id: Literal["multiple-select-exact-set"]


class NumericEntryPracticeHistoryItemModel(
    PracticeHistoryItemSummaryBaseModel
):
    item_type: Literal["numeric_entry"]
    scoring_policy_id: Literal["numeric-exact-or-inclusive-range"]


PracticeHistoryItemSummaryModel = Annotated[
    Union[
        SingleSelectPracticeHistoryItemModel,
        MultipleSelectPracticeHistoryItemModel,
        NumericEntryPracticeHistoryItemModel,
    ],
    Field(discriminator="item_type"),
]


class PracticeHistoryAttemptModel(ApiModel):
    attempt_order: int = Field(ge=1, le=10)
    event_id: UUID
    attempt_id: UUID
    evidence_id: UUID
    submission_id: UUID
    score: int = Field(ge=0, le=20)
    max_score: int = Field(ge=1, le=20)
    outcome: Literal["all_correct", "review_needed"]
    item_summaries: list[PracticeHistoryItemSummaryModel] = Field(
        min_length=1,
        max_length=20,
    )
    completed_at: datetime


class PracticeHistoryResponseModel(PracticeProgressScopeModel):
    source_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    attempts: list[PracticeHistoryAttemptModel] = Field(max_length=10)


class PracticeReviewDestinationModel(ApiModel):
    placement_id: PracticeIdentifier
    package_id: PracticeIdentifier
    package_version: str = Field(
        pattern=(
            r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\."
            r"(0|[1-9][0-9]*)$"
        )
    )
    package_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    section_id: PracticeIdentifier | None = Field(
        default=None,
        exclude_if=lambda value: value is None,
    )


class PracticeReviewTargetBaseModel(ApiModel):
    schema_version: Literal["1.0.0"]
    practice_placement_id: PracticeIdentifier
    resource_id: PracticeIdentifier
    resource_version: str = Field(
        pattern=(
            r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\."
            r"(0|[1-9][0-9]*)$"
        )
    )
    resource_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    resource_title: str = Field(
        min_length=1,
        max_length=240,
        pattern=r"^[^<>&\u0000-\u001f\u007f]+$",
    )


class AvailablePracticeReviewTargetModel(PracticeReviewTargetBaseModel):
    state: Literal["available"]
    destination: PracticeReviewDestinationModel


class UnavailablePracticeReviewTargetModel(PracticeReviewTargetBaseModel):
    state: Literal["unavailable"]
    unavailable_reason: Literal[
        "mapping_not_found",
        "destination_not_available",
        "version_mismatch",
    ]


PracticeReviewTargetModel = Annotated[
    Union[
        AvailablePracticeReviewTargetModel,
        UnavailablePracticeReviewTargetModel,
    ],
    Field(discriminator="state"),
]


class PracticeProgressResponseModel(ApiModel):
    schema_version: Literal["1.0.0"] = "1.0.0"
    placement_id: PracticeIdentifier
    draft: PracticeDraftResponseModel | None
    retry_state: PracticeRetryStateResponseModel
    history: PracticeHistoryResponseModel
    review_targets: list[PracticeReviewTargetModel] = Field(max_length=8)


class KnowledgeCheckSubmissionRequestModel(ApiModel):
    schema_version: Literal["1.0.0"]
    submission_id: UUID
    placement_id: str = Field(
        min_length=3,
        max_length=64,
        pattern=r"^[a-z0-9][a-z0-9._-]{2,63}$",
    )
    package_id: str = Field(
        min_length=3,
        max_length=64,
        pattern=r"^[a-z0-9][a-z0-9._-]{2,63}$",
    )
    package_version: Literal["1.1.0"]
    package_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    assessment_id: str = Field(
        min_length=3,
        max_length=64,
        pattern=r"^[a-z0-9][a-z0-9._-]{2,63}$",
    )
    assessment_version: Literal["1.0.0"]
    definition_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    item_id: str = Field(
        min_length=3,
        max_length=64,
        pattern=r"^[a-z0-9][a-z0-9._-]{2,63}$",
    )
    item_version: Literal["1.0.0"]
    scoring_policy_id: Literal["single-select-exact-match"]
    scoring_policy_version: Literal["1.0.0"]
    selected_option_id: str = Field(
        min_length=3,
        max_length=64,
        pattern=r"^[a-z0-9][a-z0-9._-]{2,63}$",
    )


class KnowledgeCheckFeedbackModel(ApiModel):
    feedback_id: str
    text: str = Field(min_length=1, max_length=400)


class KnowledgeCheckResultResponseModel(ApiModel):
    schema_version: Literal["1.0.0"] = "1.0.0"
    attempt_id: UUID
    evidence_id: UUID
    submission_id: UUID
    placement_id: str
    package_id: str
    package_version: Literal["1.1.0"]
    package_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    assessment_id: str
    assessment_version: Literal["1.0.0"]
    definition_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    item_id: str
    item_version: Literal["1.0.0"]
    scoring_policy_id: Literal["single-select-exact-match"]
    scoring_policy_version: Literal["1.0.0"]
    score: int = Field(ge=0, le=1)
    max_score: Literal[1]
    correct: bool
    feedback: KnowledgeCheckFeedbackModel
    submitted_at: datetime


class LessonCompletionHistoryEntryModel(ApiModel):
    event_id: UUID
    attempt_id: UUID
    evidence_id: UUID
    package_id: str
    package_version: Literal["1.1.0"]
    package_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    assessment_id: str
    assessment_version: Literal["1.0.0"]
    definition_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    item_id: str
    item_version: Literal["1.0.0"]
    scoring_policy_id: Literal["single-select-exact-match"]
    scoring_policy_version: Literal["1.0.0"]
    score: int = Field(ge=0, le=1)
    max_score: Literal[1]
    completed_at: datetime


class LessonCompletionResponseModel(ApiModel):
    projection_version: Literal["1.0.0"] = "1.0.0"
    placement_id: str
    completed: bool
    completion_meaning: Literal[
        "not_completed", "bounded_knowledge_check_completed"
    ]
    source_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    rebuilt_at: datetime
    history: list[LessonCompletionHistoryEntryModel]


class ProjectActivityCompletionHistoryEntryModel(ApiModel):
    event_id: Identifier
    evidence_id: Identifier
    submission_id: Identifier
    snapshot_id: Identifier
    snapshot_digest: Digest
    brief_id: Identifier
    brief_version: ProjectSubmissionVersion
    brief_digest: Digest
    placement_id: Identifier
    placement_version: ProjectSubmissionVersion
    placement_digest: Digest
    policy_id: Literal["assessment-project-closure"]
    policy_version: Literal["1.0.0"]
    milestone_ids: list[Identifier] = Field(min_length=1, max_length=20)
    request_fingerprint: Digest
    occurrence: int = Field(ge=1, le=100)
    accepted_sequence: int = Field(ge=1)
    supersedes_submission_id: Identifier | None = Field(
        default=None, exclude_if=lambda value: value is None
    )
    submitted_at: datetime
    occurred_at: datetime


class ProjectActivityCompletionResponseModel(ApiModel):
    projection_version: Literal["1.0.0"]
    project_id: Identifier
    completed: bool
    completion_meaning: Literal[
        "not_completed", "bounded_project_activity_completed"
    ]
    source_digest: Digest
    rebuilt_at: datetime
    history: list[ProjectActivityCompletionHistoryEntryModel] = Field(
        max_length=100
    )


LearnerPreferenceIdentifier = Annotated[
    str,
    Field(
        min_length=3,
        max_length=64,
        pattern=r"^[a-z0-9][a-z0-9._-]{2,63}$",
    ),
]
LearnerPreferenceDigest = Annotated[
    str,
    Field(pattern=r"^[a-f0-9]{64}$"),
]
LearnerPreferenceDetail2000 = Annotated[
    str,
    Field(min_length=1, max_length=2_000),
] | None
LearnerPreferenceDetail1000 = Annotated[
    str,
    Field(min_length=1, max_length=1_000),
] | None
LearnerPreferenceLimitation = Annotated[
    str,
    Field(min_length=1, max_length=320),
]
LearnerPreferenceOperation = Literal[
    "create_goal",
    "update_goal",
    "archive_goal",
    "restore_goal",
    "remove_goal",
    "reorder_goals",
    "create_experience",
    "update_experience",
    "remove_experience",
    "reorder_experience",
    "create_interest",
    "rename_interest",
    "remove_interest",
    "reorder_interests",
    "reset_profile",
]


class LearnerPreferenceGoalModel(LearnerPreferenceTimestampModel):
    goal_id: LearnerPreferenceIdentifier
    title: str = Field(min_length=1, max_length=160)
    detail: LearnerPreferenceDetail2000
    archived: bool
    created_at: datetime
    updated_at: datetime


class LearnerPreferenceExperienceModel(LearnerPreferenceTimestampModel):
    experience_id: LearnerPreferenceIdentifier
    subject: str = Field(min_length=1, max_length=120)
    level: Literal["new", "some_experience", "experienced"]
    detail: LearnerPreferenceDetail1000
    created_at: datetime
    updated_at: datetime


class LearnerPreferenceInterestModel(LearnerPreferenceTimestampModel):
    interest_id: LearnerPreferenceIdentifier
    label: str = Field(min_length=1, max_length=120)
    created_at: datetime
    updated_at: datetime


class LearnerPreferenceProfileResponseModel(LearnerPreferenceTimestampModel):
    schema_version: Literal["1.0.0"]
    profile_id: LearnerPreferenceIdentifier
    learner_id: UUID
    revision: int = Field(ge=1)
    goals: list[LearnerPreferenceGoalModel] = Field(max_length=20)
    experience: list[LearnerPreferenceExperienceModel] = Field(max_length=20)
    interests: list[LearnerPreferenceInterestModel] = Field(max_length=50)
    created_at: datetime
    updated_at: datetime
    profile_digest: LearnerPreferenceDigest


class CreateLearnerGoalMutationModel(ApiModel):
    operation: Literal["create_goal"]
    title: str = Field(min_length=1, max_length=160)
    detail: LearnerPreferenceDetail2000


class UpdateLearnerGoalMutationModel(CreateLearnerGoalMutationModel):
    operation: Literal["update_goal"]
    entry_id: LearnerPreferenceIdentifier


class SelectLearnerGoalMutationModel(ApiModel):
    operation: Literal["archive_goal", "restore_goal", "remove_goal"]
    entry_id: LearnerPreferenceIdentifier


class ReorderLearnerGoalsMutationModel(ApiModel):
    operation: Literal["reorder_goals"]
    ordered_ids: list[LearnerPreferenceIdentifier] = Field(
        max_length=20,
        json_schema_extra={"uniqueItems": True},
    )


class CreateLearnerExperienceMutationModel(ApiModel):
    operation: Literal["create_experience"]
    subject: str = Field(min_length=1, max_length=120)
    level: Literal["new", "some_experience", "experienced"]
    detail: LearnerPreferenceDetail1000


class UpdateLearnerExperienceMutationModel(
    CreateLearnerExperienceMutationModel
):
    operation: Literal["update_experience"]
    entry_id: LearnerPreferenceIdentifier


class RemoveLearnerExperienceMutationModel(ApiModel):
    operation: Literal["remove_experience"]
    entry_id: LearnerPreferenceIdentifier


class ReorderLearnerExperienceMutationModel(ApiModel):
    operation: Literal["reorder_experience"]
    ordered_ids: list[LearnerPreferenceIdentifier] = Field(
        max_length=20,
        json_schema_extra={"uniqueItems": True},
    )


class CreateLearnerInterestMutationModel(ApiModel):
    operation: Literal["create_interest"]
    label: str = Field(min_length=1, max_length=120)


class RenameLearnerInterestMutationModel(CreateLearnerInterestMutationModel):
    operation: Literal["rename_interest"]
    entry_id: LearnerPreferenceIdentifier


class RemoveLearnerInterestMutationModel(ApiModel):
    operation: Literal["remove_interest"]
    entry_id: LearnerPreferenceIdentifier


class ReorderLearnerInterestsMutationModel(ApiModel):
    operation: Literal["reorder_interests"]
    ordered_ids: list[LearnerPreferenceIdentifier] = Field(
        max_length=50,
        json_schema_extra={"uniqueItems": True},
    )


class ResetLearnerPreferenceProfileMutationModel(ApiModel):
    operation: Literal["reset_profile"]


LearnerPreferenceMutationModel = Annotated[
    Union[
        CreateLearnerGoalMutationModel,
        UpdateLearnerGoalMutationModel,
        SelectLearnerGoalMutationModel,
        ReorderLearnerGoalsMutationModel,
        CreateLearnerExperienceMutationModel,
        UpdateLearnerExperienceMutationModel,
        RemoveLearnerExperienceMutationModel,
        ReorderLearnerExperienceMutationModel,
        CreateLearnerInterestMutationModel,
        RenameLearnerInterestMutationModel,
        RemoveLearnerInterestMutationModel,
        ReorderLearnerInterestsMutationModel,
        ResetLearnerPreferenceProfileMutationModel,
    ],
    Field(discriminator="operation"),
]


class LearnerPreferenceMutationRequestModel(ApiModel):
    schema_version: Literal["1.0.0"]
    idempotency_key: LearnerPreferenceIdentifier
    expected_revision: int = Field(ge=1)
    mutation: LearnerPreferenceMutationModel


class LearnerPreferenceChangeModel(LearnerPreferenceTimestampModel):
    schema_version: Literal["1.0.0"]
    revision: int = Field(ge=1)
    operation: LearnerPreferenceOperation
    object_kind: Literal["goal", "experience", "interest", "profile"]
    object_id: LearnerPreferenceIdentifier | None
    occurred_at: datetime
    resulting_profile_digest: LearnerPreferenceDigest


class LearnerPreferenceHistoryResponseModel(LearnerPreferenceTimestampModel):
    schema_version: Literal["1.0.0"]
    profile_id: LearnerPreferenceIdentifier
    current_revision: int = Field(ge=1)
    changes: list[LearnerPreferenceChangeModel] = Field(max_length=100)


class LearnerPreferenceExportResponseModel(LearnerPreferenceTimestampModel):
    schema_version: Literal["1.0.0"]
    purpose: str = Field(min_length=1, max_length=240)
    limitations: list[LearnerPreferenceLimitation] = Field(
        min_length=1,
        max_length=8,
    )
    exported_at: datetime
    profile: LearnerPreferenceProfileResponseModel
    history: LearnerPreferenceHistoryResponseModel


class PresentationPreferenceProfileResponseModel(LearnerPreferenceTimestampModel):
    schema_version: Literal["1.0.0"]
    profile_id: LearnerPreferenceIdentifier
    learner_id: UUID
    revision: int = Field(ge=1)
    text_size: Literal["default", "larger"]
    text_spacing: Literal["default", "increased"]
    reading_width: Literal["standard", "focused"]
    motion: Literal["system", "reduce"]
    created_at: datetime
    updated_at: datetime
    profile_digest: LearnerPreferenceDigest


class ReplacePresentationPreferencesMutationModel(ApiModel):
    operation: Literal["replace_preferences"]
    text_size: Literal["default", "larger"]
    text_spacing: Literal["default", "increased"]
    reading_width: Literal["standard", "focused"]
    motion: Literal["system", "reduce"]


class ResetPresentationPreferencesMutationModel(ApiModel):
    operation: Literal["reset_profile"]


PresentationPreferenceMutationModel = Annotated[
    Union[
        ReplacePresentationPreferencesMutationModel,
        ResetPresentationPreferencesMutationModel,
    ],
    Field(discriminator="operation"),
]


class PresentationPreferenceMutationRequestModel(ApiModel):
    schema_version: Literal["1.0.0"]
    idempotency_key: LearnerPreferenceIdentifier
    expected_revision: int = Field(ge=1)
    mutation: PresentationPreferenceMutationModel


class PresentationPreferenceChangeModel(LearnerPreferenceTimestampModel):
    schema_version: Literal["1.0.0"]
    revision: int = Field(ge=1)
    operation: Literal["replace_preferences", "reset_profile"]
    object_kind: Literal["profile"]
    object_id: None
    occurred_at: datetime
    resulting_profile_digest: LearnerPreferenceDigest


class PresentationPreferenceHistoryResponseModel(LearnerPreferenceTimestampModel):
    schema_version: Literal["1.0.0"]
    profile_id: LearnerPreferenceIdentifier
    current_revision: int = Field(ge=1)
    changes: list[PresentationPreferenceChangeModel] = Field(max_length=100)


class PresentationPreferenceExportResponseModel(LearnerPreferenceTimestampModel):
    schema_version: Literal["1.0.0"]
    purpose: str = Field(min_length=1, max_length=240)
    limitations: list[LearnerPreferenceLimitation] = Field(
        min_length=1,
        max_length=8,
    )
    exported_at: datetime
    profile: PresentationPreferenceProfileResponseModel
    history: PresentationPreferenceHistoryResponseModel


class AssistancePreferenceProfileResponseModel(LearnerPreferenceTimestampModel):
    schema_version: Literal["1.0.0"]
    profile_id: LearnerPreferenceIdentifier
    learner_id: UUID
    revision: int = Field(ge=1)
    assistance_mode: Literal["off", "on_request"]
    created_at: datetime
    updated_at: datetime
    profile_digest: LearnerPreferenceDigest


class ReplaceAssistancePreferencesMutationModel(ApiModel):
    operation: Literal["replace_preferences"]
    assistance_mode: Literal["off", "on_request"]


class ResetAssistancePreferencesMutationModel(ApiModel):
    operation: Literal["reset_profile"]


AssistancePreferenceMutationModel = Annotated[
    Union[
        ReplaceAssistancePreferencesMutationModel,
        ResetAssistancePreferencesMutationModel,
    ],
    Field(discriminator="operation"),
]


class AssistancePreferenceMutationRequestModel(ApiModel):
    schema_version: Literal["1.0.0"]
    idempotency_key: LearnerPreferenceIdentifier
    expected_revision: int = Field(ge=1)
    mutation: AssistancePreferenceMutationModel


class AssistancePreferenceChangeModel(LearnerPreferenceTimestampModel):
    schema_version: Literal["1.0.0"]
    revision: int = Field(ge=1)
    operation: Literal["replace_preferences", "reset_profile"]
    object_kind: Literal["profile"]
    object_id: None
    occurred_at: datetime
    resulting_profile_digest: LearnerPreferenceDigest


class AssistancePreferenceHistoryResponseModel(LearnerPreferenceTimestampModel):
    schema_version: Literal["1.0.0"]
    profile_id: LearnerPreferenceIdentifier
    current_revision: int = Field(ge=1)
    changes: list[AssistancePreferenceChangeModel] = Field(max_length=100)


class AssistancePreferenceExportResponseModel(LearnerPreferenceTimestampModel):
    schema_version: Literal["1.0.0"]
    purpose: str = Field(min_length=1, max_length=240)
    limitations: list[LearnerPreferenceLimitation] = Field(
        min_length=1,
        max_length=8,
    )
    exported_at: datetime
    profile: AssistancePreferenceProfileResponseModel
    history: AssistancePreferenceHistoryResponseModel


class HealthResponseModel(ApiModel):
    status: Literal["ok", "ready", "not_ready"]


_MODEL_NAMESPACE = {
    "InlineNodeModel": InlineNodeModel,
    "BodyNodeModel": BodyNodeModel,
}
for _model in (
    EmphasisModel,
    StrongModel,
    SourceLinkModel,
    ListItemModel,
    BulletListModel,
    OrderedListModel,
    LessonReadingResponseModel,
):
    _model.model_rebuild(_types_namespace=_MODEL_NAMESPACE)


def lesson_response(
    reading: LessonReadingResult,
) -> LessonReadingResponseModel:
    return LessonReadingResponseModel(
        placement_id=reading.placement_id,
        package_id=reading.package_id,
        package_version=reading.package_version,
        package_digest=reading.package_digest,
        title=reading.title,
        objectives=list(reading.objectives),
        body=[_body_node(node) for node in reading.body],
        sources=[
            EducationalSourceModel(
                source_id=source.source_id,
                title=source.title,
                publisher=source.publisher,
                locator=source.locator,
                reviewed_on=source.reviewed_on,
                license_note=source.license_note,
            )
            for source in reading.sources
        ],
        assets=[
            PassiveAssetModel(
                asset_id=asset.asset_id,
                media_type=asset.media_type,
                sha256=asset.sha256,
                alt_text=asset.alt_text,
                locator=f"/api/v1/content/assets/{asset.asset_id}",
            )
            for asset in reading.assets
        ],
        provenance=PublicationProvenanceModel(
            published_by=reading.provenance.published_by,
            published_at=reading.provenance.published_at,
            content_reviewed_on=reading.provenance.content_reviewed_on,
            educational_use_notice=(
                reading.provenance.educational_use_notice
            ),
        ),
    )


def curriculum_graph_response(
    graph: CurriculumGraph,
) -> CurriculumGraphResponseModel:
    return CurriculumGraphResponseModel.model_validate(
        curriculum_graph_payload(graph)
    )


def navigation_state_response(
    projection: NavigationStateProjection,
) -> NavigationStateResponseModel:
    return NavigationStateResponseModel.model_validate(
        navigation_state_payload(projection)
    )


def activity_launch_response(
    resolution: ActivityLaunchResolution,
) -> ActivityLaunchResponseModel:
    return ActivityLaunchResponseModel.model_validate(
        activity_launch_payload(resolution)
    )


def learning_opportunity_browse_response(
    browse: LearningOpportunityBrowse,
) -> LearningOpportunityBrowseResponseModel:
    return LearningOpportunityBrowseResponseModel(
        schema_version=browse.schema_version,  # type: ignore[arg-type]
        projection_generation=browse.projection_generation,
        projected_at=browse.projected_at,
        records=[
            learning_opportunity_response(record)
            for record in browse.records
        ],
    )


def learning_opportunity_query_page_response(
    page: LearningOpportunityQueryPage,
) -> LearningOpportunityQueryPageResponseModel:
    return LearningOpportunityQueryPageResponseModel(
        schema_version=page.schema_version,  # type: ignore[arg-type]
        projection_generation=page.projection_generation,
        projected_at=page.projected_at,
        applied_query=applied_learning_opportunity_query_response(
            page.applied_query
        ),
        total_matches=page.total_matches,
        records=[
            learning_opportunity_response(record)
            for record in page.records
        ],
        next_cursor=page.next_cursor,
    )


def applied_learning_opportunity_query_response(
    query: AppliedLearningOpportunityQuery,
) -> AppliedLearningOpportunityQueryResponseModel:
    return AppliedLearningOpportunityQueryResponseModel(
        query=query.query,
        prerequisite_query=query.prerequisite_query,
        topics=list(query.topics),
        levels=[level.value for level in query.levels],  # type: ignore[list-item]
        kinds=[kind.value for kind in query.kinds],  # type: ignore[list-item]
        availabilities=[
            availability.value for availability in query.availabilities
        ],  # type: ignore[list-item]
        minimum_minutes=query.minimum_minutes,
        maximum_minutes=query.maximum_minutes,
        sort=query.sort.value,  # type: ignore[arg-type]
        page_size=query.page_size,
    )


def learning_opportunity_response(
    record: LearningOpportunityRecord,
) -> LearningOpportunityResponseModel:
    return LearningOpportunityResponseModel(
        schema_version=record.schema_version,  # type: ignore[arg-type]
        opportunity_id=record.opportunity_id,
        placement_id=record.placement_id,
        destination=record.destination,
        kind=record.kind.value,  # type: ignore[arg-type]
        title=record.title,
        summary=record.summary,
        objectives=list(record.objectives),
        topics=list(record.topics),
        level=record.level.value,  # type: ignore[arg-type]
        estimated_minutes=record.estimated_minutes,
        prerequisite_summary=record.prerequisite_summary,
        availability=record.availability.value,  # type: ignore[arg-type]
        availability_reason=record.availability_reason,
        package_id=record.package_id,
        package_version=record.package_version,
        package_digest=record.package_digest,
        provenance=DiscoveryProvenanceResponseModel(
            published_by=record.provenance.published_by,
            published_at=record.provenance.published_at,
            content_reviewed_on=record.provenance.content_reviewed_on,
            educational_use_notice=(
                record.provenance.educational_use_notice
            ),
        ),
        source_fingerprint=record.source_fingerprint,
        projected_at=record.projected_at,
    )


def knowledge_check_presentation_response(
    presentation: KnowledgeCheckPresentation,
) -> KnowledgeCheckPresentationResponseModel:
    return KnowledgeCheckPresentationResponseModel(
        placement_id=presentation.placement_id,
        package_id=presentation.package_id,
        package_version=presentation.package_version,  # type: ignore[arg-type]
        package_digest=presentation.package_digest,
        assessment_id=presentation.assessment_id,
        assessment_version=presentation.assessment_version,  # type: ignore[arg-type]
        definition_digest=presentation.definition_digest,
        item_type=presentation.item_type,  # type: ignore[arg-type]
        item_id=presentation.item_id,
        item_version=presentation.item_version,  # type: ignore[arg-type]
        scoring_policy_id=presentation.scoring_policy_id,  # type: ignore[arg-type]
        scoring_policy_version=presentation.scoring_policy_version,  # type: ignore[arg-type]
        prompt=presentation.prompt,
        options=[
            KnowledgeCheckOptionModel(
                option_id=option.option_id,
                label=option.label,
            )
            for option in presentation.options
        ],
    )


def knowledge_check_result_response(
    result: KnowledgeCheckResult,
) -> KnowledgeCheckResultResponseModel:
    return KnowledgeCheckResultResponseModel(
        attempt_id=result.attempt_id,
        evidence_id=result.evidence_id,
        submission_id=result.submission_id,
        placement_id=result.placement_id,
        package_id=result.package_id,
        package_version=result.package_version,  # type: ignore[arg-type]
        package_digest=result.package_digest,
        assessment_id=result.assessment_id,
        assessment_version=result.assessment_version,  # type: ignore[arg-type]
        definition_digest=result.definition_digest,
        item_id=result.item_id,
        item_version=result.item_version,  # type: ignore[arg-type]
        scoring_policy_id=result.scoring_policy_id,  # type: ignore[arg-type]
        scoring_policy_version=result.scoring_policy_version,  # type: ignore[arg-type]
        score=result.score,
        max_score=result.max_score,  # type: ignore[arg-type]
        correct=result.correct,
        feedback=KnowledgeCheckFeedbackModel(
            feedback_id=result.feedback.feedback_id,
            text=result.feedback.text,
        ),
        submitted_at=result.submitted_at,
    )


def practice_presentation_response(
    presentation: PracticePresentation,
) -> PracticePresentationResponseModel:
    return PracticePresentationResponseModel.model_validate(
        asdict(presentation)
    )


def practice_submission_result_response(
    result: PracticeResult,
) -> PracticeSubmissionResultResponseModel:
    item_results: list[dict[str, object]] = []
    for item in result.item_results:
        value = asdict(item)
        response = value.pop("response")
        if not isinstance(response, dict):
            raise ValueError("Practice response projection is invalid.")
        item_results.append({**response, **value})
    return PracticeSubmissionResultResponseModel.model_validate(
        {
            "schema_version": result.schema_version,
            "attempt_id": result.attempt_id,
            "evidence_id": result.evidence_id,
            "submission_id": result.submission_id,
            "placement_id": result.placement_id,
            "package_id": result.package_id,
            "package_version": result.package_version,
            "package_digest": result.package_digest,
            "definition_digest": result.definition_digest,
            "practice_id": result.practice_id,
            "practice_version": result.practice_version,
            "attempt_policy_id": result.attempt_policy_id,
            "attempt_policy_version": result.attempt_policy_version,
            "score": result.score,
            "max_score": result.max_score,
            "outcome": result.outcome,
            "review_reference_ids": list(result.review_reference_ids),
            "item_results": item_results,
            "submitted_at": result.submitted_at,
        }
    )


def practice_draft_response(
    draft: PracticeDraft,
) -> PracticeDraftResponseModel:
    value = asdict(draft)
    scope = value.pop("scope")
    if not isinstance(scope, dict):
        raise ValueError("Practice draft scope is invalid.")
    return PracticeDraftResponseModel.model_validate(
        {"schema_version": "1.0.0", **scope, **value}
    )


def practice_progress_response(
    *,
    placement_id: str,
    draft: PracticeDraft | None,
    retry_state: PracticeRetryState,
    history: PracticeHistoryView,
    review_targets: tuple[PracticeReviewTarget, ...],
) -> PracticeProgressResponseModel:
    retry_value = asdict(retry_state)
    retry_scope = retry_value.pop("scope")
    if not isinstance(retry_scope, dict):
        raise ValueError("Practice retry scope is invalid.")
    history_value = asdict(history)
    history_value.pop("rebuilt_at", None)
    target_values: list[dict[str, object]] = []
    for target in review_targets:
        target_value = asdict(target)
        if target.state == "available":
            target_value.pop("unavailable_reason", None)
        else:
            target_value.pop("destination", None)
        target_values.append(target_value)
    return PracticeProgressResponseModel.model_validate(
        {
            "schema_version": "1.0.0",
            "placement_id": placement_id,
            "draft": (
                practice_draft_response(draft).model_dump(mode="json")
                if draft is not None
                else None
            ),
            "retry_state": {
                "schema_version": "1.0.0",
                **retry_scope,
                **retry_value,
            },
            "history": history_value,
            "review_targets": target_values,
        }
    )


def lesson_completion_response(
    view: LessonCompletionView,
) -> LessonCompletionResponseModel:
    return LessonCompletionResponseModel(
        placement_id=view.placement_id,
        completed=view.completed,
        completion_meaning=view.completion_meaning,  # type: ignore[arg-type]
        source_digest=view.source_digest,
        rebuilt_at=view.rebuilt_at,
        history=[
            LessonCompletionHistoryEntryModel(
                event_id=entry.event_id,
                attempt_id=entry.attempt_id,
                evidence_id=entry.evidence_id,
                package_id=entry.package_id,
                package_version=entry.package_version,  # type: ignore[arg-type]
                package_digest=entry.package_digest,
                assessment_id=entry.assessment_id,
                assessment_version=entry.assessment_version,  # type: ignore[arg-type]
                definition_digest=entry.definition_digest,
                item_id=entry.item_id,
                item_version=entry.item_version,  # type: ignore[arg-type]
                scoring_policy_id=entry.scoring_policy_id,  # type: ignore[arg-type]
                scoring_policy_version=entry.scoring_policy_version,  # type: ignore[arg-type]
                score=entry.score,
                max_score=entry.max_score,  # type: ignore[arg-type]
                completed_at=entry.completed_at,
            )
            for entry in view.history
        ],
    )


def project_activity_completion_response(
    view: ProjectCompletionView,
) -> ProjectActivityCompletionResponseModel:
    return ProjectActivityCompletionResponseModel(
        projection_version="1.0.0",
        project_id=view.project_id,
        completed=view.completed,
        completion_meaning=view.completion_meaning,  # type: ignore[arg-type]
        source_digest=view.source_digest,
        rebuilt_at=view.rebuilt_at,
        history=[
            ProjectActivityCompletionHistoryEntryModel(
                event_id=entry.event_id,
                evidence_id=entry.evidence_id,
                submission_id=entry.submission_id,
                snapshot_id=entry.snapshot_id,
                snapshot_digest=entry.snapshot_digest,
                brief_id=entry.brief_id,
                brief_version=entry.brief_version,
                brief_digest=entry.brief_digest,
                placement_id=entry.placement_id,
                placement_version=entry.placement_version,
                placement_digest=entry.placement_digest,
                policy_id=entry.policy_id,  # type: ignore[arg-type]
                policy_version=entry.policy_version,  # type: ignore[arg-type]
                milestone_ids=list(entry.milestone_ids),
                request_fingerprint=entry.request_fingerprint,
                occurrence=entry.occurrence,
                accepted_sequence=entry.accepted_sequence,
                supersedes_submission_id=entry.supersedes_submission_id,
                submitted_at=entry.submitted_at,
                occurred_at=entry.occurred_at,
            )
            for entry in view.history
        ],
    )


def learner_preference_mutation_intent(
    model: LearnerPreferenceMutationRequestModel,
) -> PreferenceMutationIntent:
    values = model.mutation.model_dump()
    return PreferenceMutationIntent(
        schema_version=model.schema_version,
        idempotency_key=model.idempotency_key,
        expected_revision=model.expected_revision,
        mutation=PreferenceMutation(
            operation=str(values["operation"]),
            entry_id=values.get("entry_id"),
            title=values.get("title"),
            detail=values.get("detail"),
            subject=values.get("subject"),
            level=values.get("level"),
            label=values.get("label"),
            ordered_ids=tuple(values.get("ordered_ids", ())),
        ),
    )


def learner_preference_profile_response(
    profile: LearnerPreferenceProfile,
) -> LearnerPreferenceProfileResponseModel:
    return LearnerPreferenceProfileResponseModel.model_validate(
        asdict(profile)
    )


def learner_preference_history_response(
    history: PreferenceHistory,
) -> LearnerPreferenceHistoryResponseModel:
    return LearnerPreferenceHistoryResponseModel.model_validate(
        asdict(history)
    )


def learner_preference_export_response(
    export: PreferenceExport,
) -> LearnerPreferenceExportResponseModel:
    return LearnerPreferenceExportResponseModel.model_validate(asdict(export))


def presentation_preference_mutation_intent(
    model: PresentationPreferenceMutationRequestModel,
) -> PresentationPreferenceMutationIntent:
    values = model.mutation.model_dump()
    return PresentationPreferenceMutationIntent(
        schema_version=model.schema_version,
        idempotency_key=model.idempotency_key,
        expected_revision=model.expected_revision,
        mutation=PresentationPreferenceMutation(
            operation=values["operation"],
            text_size=values.get("text_size"),
            text_spacing=values.get("text_spacing"),
            reading_width=values.get("reading_width"),
            motion=values.get("motion"),
        ),
    )


def presentation_preference_profile_response(
    profile: PresentationPreferenceProfile,
) -> PresentationPreferenceProfileResponseModel:
    return PresentationPreferenceProfileResponseModel.model_validate(
        asdict(profile)
    )


def presentation_preference_history_response(
    history: PresentationPreferenceHistory,
) -> PresentationPreferenceHistoryResponseModel:
    return PresentationPreferenceHistoryResponseModel.model_validate(
        asdict(history)
    )


def presentation_preference_export_response(
    export: PresentationPreferenceExport,
) -> PresentationPreferenceExportResponseModel:
    return PresentationPreferenceExportResponseModel.model_validate(asdict(export))


def assistance_preference_mutation_intent(
    model: AssistancePreferenceMutationRequestModel,
) -> AssistancePreferenceMutationIntent:
    values = model.mutation.model_dump()
    return AssistancePreferenceMutationIntent(
        schema_version=model.schema_version,
        idempotency_key=model.idempotency_key,
        expected_revision=model.expected_revision,
        mutation=AssistancePreferenceMutation(
            operation=values["operation"],
            assistance_mode=values.get("assistance_mode"),
        ),
    )


def assistance_preference_profile_response(
    profile: AssistancePreferenceProfile,
) -> AssistancePreferenceProfileResponseModel:
    return AssistancePreferenceProfileResponseModel.model_validate(
        asdict(profile)
    )


def assistance_preference_history_response(
    history: AssistancePreferenceHistory,
) -> AssistancePreferenceHistoryResponseModel:
    return AssistancePreferenceHistoryResponseModel.model_validate(
        asdict(history)
    )


def assistance_preference_export_response(
    export: AssistancePreferenceExport,
) -> AssistancePreferenceExportResponseModel:
    return AssistancePreferenceExportResponseModel.model_validate(asdict(export))


def _inline_node(node: content_public.InlineNode) -> InlineNodeModel:
    if isinstance(node, content_public.InlineText):
        return InlineTextModel(value=node.value)
    if isinstance(node, content_public.InlineCode):
        return InlineCodeModel(value=node.value)
    if isinstance(node, content_public.SoftBreak):
        return SoftBreakModel()
    if isinstance(node, content_public.HardBreak):
        return HardBreakModel()
    if isinstance(node, content_public.Emphasis):
        return EmphasisModel(
            children=[_inline_node(child) for child in node.children]
        )
    if isinstance(node, content_public.Strong):
        return StrongModel(
            children=[_inline_node(child) for child in node.children]
        )
    if isinstance(node, content_public.SourceLink):
        return SourceLinkModel(
            children=[_inline_node(child) for child in node.children],
            href=node.href,
            source_id=node.source_id,
        )
    if isinstance(node, content_public.AssetImage):
        return AssetImageModel(
            asset_id=node.asset_id, alt_text=node.alt_text
        )
    raise TypeError("Unsupported public inline node.")


def project_create_intent(
    request: ProjectCreateRequestModel,
) -> ProjectCreateIntent:
    origin = request.origin
    if isinstance(origin, IndependentProjectOriginModel):
        domain_origin = IndependentProjectOrigin()
    else:
        domain_origin = LearningProjectOrigin(**origin.model_dump())
    return ProjectCreateIntent(
        schema_version=request.schema_version,
        idempotency_key=request.idempotency_key,
        title=request.title,
        charter=request.charter,
        origin=domain_origin,
    )


def project_shell_response(shell: ProjectShell) -> ProjectShellResponseModel:
    return ProjectShellResponseModel.model_validate(asdict(shell))


def project_list_response(
    shells: tuple[ProjectShell, ...],
) -> ProjectListResponseModel:
    return ProjectListResponseModel(
        records=[project_shell_response(shell) for shell in shells]
    )


def project_workspace_mutation_intent(
    value: ProjectWorkspaceMutationRequestModel
    | ProjectArtifactMutationRequestModel,
) -> WorkspaceMutationIntent:
    mutation = value.mutation
    if isinstance(mutation, AddProjectNoteModel):
        parsed = AddNoteMutation(mutation.title, mutation.body)
    elif isinstance(mutation, ReplaceProjectNoteModel):
        parsed = ReplaceNoteMutation(
            mutation.note_id,
            mutation.expected_note_version,
            mutation.title,
            mutation.body,
        )
    elif isinstance(mutation, ReplaceProjectReferenceModel):
        parsed = ReplaceReferenceMutation(
            mutation.reference_id,
            mutation.expected_reference_version,
            mutation.title,
            mutation.url,
            mutation.source_name,
            mutation.source_version,
            mutation.source_digest,
            mutation.license,
            mutation.use_constraints,
        )
    elif isinstance(mutation, AddProjectReferenceModel):
        parsed = AddReferenceMutation(
            mutation.title,
            mutation.url,
            mutation.source_name,
            mutation.source_version,
            mutation.source_digest,
            mutation.license,
            mutation.use_constraints,
        )
    elif isinstance(mutation, AddProjectArtifactModel):
        artifact = mutation.artifact
        parsed = AddArtifactMutation(
            ProjectArtifactInput(
                ArtifactKind(artifact.artifact_kind),
                artifact.logical_path,
                artifact.media_type,
                InspectionMode(artifact.inspection_mode),
                artifact.byte_count,
                artifact.content_digest,
                EvidenceClassification(artifact.result_classification)
                if artifact.result_classification is not None
                else None,
                ArtifactProvenance(
                    ProvenanceSourceType(artifact.provenance.source_type),
                    artifact.provenance.source_title,
                    artifact.provenance.source_version,
                    artifact.provenance.source_url,
                    artifact.provenance.source_digest,
                    artifact.provenance.license,
                    artifact.provenance.use_constraints,
                ),
                ProjectEnvironment(
                    artifact.environment.name,
                    artifact.environment.version,
                    artifact.environment.dependency_digest,
                )
                if artifact.environment is not None
                else None,
                tuple(artifact.assumptions),
            )
        )
    elif isinstance(mutation, AddProjectDomainLinkModel):
        link = mutation.link
        parsed = AddDomainLinkMutation(
            ProjectDomainLinkInput(
                DomainLinkType(link.link_type),
                link.owner_module,
                link.resource_type,
                link.resource_id,
                link.resource_version,
                link.resource_as_of,
                link.provenance,
            )
        )
    elif isinstance(mutation, RemoveProjectDomainLinkModel):
        parsed = RemoveDomainLinkMutation(mutation.link_id)
    else:
        raise TypeError("Unsupported Project workspace mutation.")
    return WorkspaceMutationIntent(
        value.schema_version,
        value.idempotency_key,
        value.expected_workspace_revision,
        parsed,
    )


def project_artifact_content(value: ProjectArtifactUploadRequestModel) -> bytes:
    return base64.b64decode(value.content_base64, validate=True)


def project_snapshot_close_intent(
    value: ProjectSnapshotCloseRequestModel,
) -> ProjectSnapshotCloseIntent:
    return ProjectSnapshotCloseIntent(
        value.schema_version,
        value.idempotency_key,
        value.expected_project_revision,
        value.expected_workspace_revision,
    )


def project_workspace_response(
    workspace: ProjectWorkspace,
) -> ProjectWorkspaceResponseModel:
    return ProjectWorkspaceResponseModel.model_validate(asdict(workspace))


def project_snapshot_response(
    snapshot: ProjectSnapshot,
) -> ProjectSnapshotResponseModel:
    return ProjectSnapshotResponseModel.model_validate(asdict(snapshot))


def project_snapshot_list_response(
    snapshots: tuple[ProjectSnapshot, ...],
) -> ProjectSnapshotListResponseModel:
    return ProjectSnapshotListResponseModel(
        records=[project_snapshot_response(snapshot) for snapshot in snapshots]
    )


def project_evidence_export_response(
    bundle: ProjectEvidenceExportBundle,
) -> ProjectEvidenceExportBundleResponseModel:
    return ProjectEvidenceExportBundleResponseModel(
        manifest=ProjectEvidenceExportResponseModel.model_validate(
            asdict(bundle.manifest)
        ),
        files=[
            ProjectEvidenceFileContentModel(
                artifact_id=item.artifact_id,
                artifact_version=item.artifact_version,
                logical_path=item.logical_path,
                content_base64=base64.b64encode(item.content).decode("ascii"),
            )
            for item in bundle.files
        ],
    )


def _project_submission_resource_response(
    resource: SnapshotResource,
) -> ProjectSubmissionResourceModel:
    shared = {
        "resource_kind": resource.resource_kind,
        "resource_id": resource.resource_id,
        "record_digest": resource.record_digest,
    }
    if resource.resource_kind in {"note", "source"}:
        return ProjectSubmissionVersionedResourceModel(
            **shared,
            resource_version=resource.resource_version,
        )
    if resource.resource_kind == "artifact":
        return ProjectSubmissionArtifactResourceModel(
            **shared,
            resource_version=resource.resource_version,
            content_digest=resource.content_digest,
            byte_count=resource.byte_count,
        )
    domain_shared = {
        **shared,
        "owner_reference_digest": resource.owner_reference_digest,
    }
    if resource.resource_version is not None:
        return ProjectSubmissionDomainResourceVersionModel(
            **domain_shared,
            resource_version=resource.resource_version,
        )
    return ProjectSubmissionDomainResourceAsOfModel(
        **domain_shared,
        resource_as_of=resource.resource_as_of,
    )


def project_submission_candidate_response(
    candidate: ProjectSnapshotCandidate,
) -> ProjectSubmissionCandidateResponseModel:
    return ProjectSubmissionCandidateResponseModel(
        schema_version="1.0.0",
        project=ProjectSubmissionProjectResponseModel.model_validate(
            asdict(candidate.project)
        ),
        origin=ProjectSubmissionOriginResponseModel.model_validate(
            asdict(candidate.origin)
        ),
        policy_id="assessment-project-closure",
        policy_version="1.0.0",
        milestones=[
            ProjectSubmissionMilestoneResponseModel.model_validate(asdict(item))
            for item in candidate.milestones
        ],
        resources=[
            _project_submission_resource_response(item)
            for item in candidate.resources
        ],
    )


def _project_milestone_evidence_response(
    evidence,
) -> ProjectMilestoneEvidenceRequestModel:
    return ProjectMilestoneEvidenceRequestModel(
        milestone_id=evidence.milestone_id,
        resources=[
            _project_submission_resource_response(item)
            for item in evidence.resources
        ],
    )


def project_completion_evidence_response(
    evidence: ProjectCompletionEvidence,
) -> ProjectCompletionEvidenceResponseModel:
    accepted = evidence.accepted
    submission = accepted.submission
    return ProjectCompletionEvidenceResponseModel(
        schema_version="1.0.0",
        evidence_id=evidence.evidence_id,
        learner_id=evidence.learner_id,
        submission_id=submission.submission_id,
        project_id=submission.project_id,
        snapshot_id=submission.snapshot_id,
        snapshot_digest=submission.snapshot_digest,
        brief_id=submission.brief_id,
        brief_version=submission.brief_version,
        brief_digest=submission.brief_digest,
        placement_id=submission.placement_id,
        placement_version=submission.placement_version,
        placement_digest=submission.placement_digest,
        policy_id="assessment-project-closure",
        policy_version="1.0.0",
        milestone_evidence=[
            _project_milestone_evidence_response(item)
            for item in submission.milestone_evidence
        ],
        milestone_ids=[item.milestone_id for item in accepted.candidate.milestones],
        request_fingerprint=accepted.request_fingerprint,
        occurrence=evidence.occurrence,
        accepted_sequence=evidence.accepted_sequence,
        submitted_at=evidence.submitted_at,
        supersedes_submission_id=evidence.supersedes_submission_id,
    )


def _project_validation_response(
    validation: ProjectValidationResult,
) -> ProjectValidationResponseModel:
    issues = [
        ProjectValidationIssueResponseModel.model_validate(asdict(item))
        for item in validation.issues
    ]
    if validation.status == "accepted":
        return ProjectAcceptedValidationResponseModel(
            schema_version="1.0.0",
            status="accepted",
            request_fingerprint=validation.request_fingerprint,
            issues=issues,
        )
    return ProjectRefusedValidationResponseModel(
        schema_version="1.0.0",
        status="refused",
        issues=issues,
    )


def project_submission_outcome_response(
    outcome: ProjectSubmissionOutcome,
) -> ProjectSubmissionOutcomeResponseModel:
    return ProjectSubmissionOutcomeResponseModel(
        validation=_project_validation_response(outcome.validation),
        evidence=(
            project_completion_evidence_response(outcome.evidence)
            if outcome.evidence is not None
            else None
        ),
    )


def project_completion_history_response(
    history: ProjectHistory,
) -> ProjectCompletionHistoryResponseModel:
    return ProjectCompletionHistoryResponseModel(
        schema_version="1.0.0",
        project_id=history.project_id,
        items=[
            ProjectCompletionHistoryItemResponseModel(
                evidence_id=item.evidence_id,
                submission_id=item.accepted.submission.submission_id,
                snapshot_id=item.accepted.submission.snapshot_id,
                snapshot_digest=item.accepted.submission.snapshot_digest,
                request_fingerprint=item.accepted.request_fingerprint,
                occurrence=item.occurrence,
                submitted_at=item.submitted_at,
                supersedes_submission_id=item.supersedes_submission_id,
            )
            for item in history.items
        ],
    )


def learning_project_start_option_response(
    option: LearningProjectStartOption,
) -> LearningProjectStartOptionResponseModel:
    return LearningProjectStartOptionResponseModel.model_validate(
        asdict(option)
    )


def learning_project_start_option_list_response(
    options: tuple[LearningProjectStartOption, ...],
) -> LearningProjectStartOptionListResponseModel:
    return LearningProjectStartOptionListResponseModel(
        records=[
            learning_project_start_option_response(option)
            for option in options
        ]
    )


def _personal_reference_selector(
    selector: PersonalLearningReferenceSelectorModel,
):
    if isinstance(selector, PersonalLearningOpportunitySelectorModel):
        return PersonalLearningOpportunitySelector(
            opportunity_id=selector.opportunity_id,
            placement_id=selector.placement_id,
        )
    if isinstance(selector, PersonalPlacedLessonSelectorModel):
        return PersonalPlacedLessonSelector(placement_id=selector.placement_id)
    if isinstance(selector, PersonalProjectWorkspaceSelectorModel):
        return PersonalProjectWorkspaceSelector(project_id=selector.project_id)
    if isinstance(selector, PersonalProjectSnapshotSelectorModel):
        return PersonalProjectSnapshotSelector(
            project_id=selector.project_id,
            snapshot_id=selector.snapshot_id,
        )
    return PersonalProjectArtifactSelector(
        project_id=selector.project_id,
        artifact_id=selector.artifact_id,
        artifact_version=selector.artifact_version,
    )


def personal_workspace_mutation_command(
    model: PersonalWorkspaceMutationRequestModel,
) -> PersonalWorkspaceMutationCommand:
    mutation = model.mutation
    if isinstance(mutation, PersonalCreateNoteModel):
        value = PersonalCreateNoteCommand(
            selector=_personal_reference_selector(mutation.selector),
            title=mutation.title,
            body=mutation.body,
        )
    elif isinstance(mutation, PersonalUpdateNoteModel):
        value = PersonalUpdateNoteMutation(
            record_id=mutation.record_id,
            title=mutation.title,
            body=mutation.body,
        )
    elif isinstance(mutation, PersonalCreateBookmarkModel):
        value = PersonalCreateBookmarkCommand(
            selector=_personal_reference_selector(mutation.selector),
            label=mutation.label,
        )
    elif isinstance(mutation, PersonalUpdateBookmarkModel):
        value = PersonalUpdateBookmarkMutation(
            record_id=mutation.record_id,
            label=mutation.label,
        )
    elif isinstance(mutation, PersonalCreateCollectionModel):
        value = PersonalCreateCollectionMutation(title=mutation.title)
    elif isinstance(mutation, PersonalRenameCollectionModel):
        value = PersonalRenameCollectionMutation(
            collection_id=mutation.collection_id,
            title=mutation.title,
        )
    elif isinstance(mutation, PersonalRemoveCollectionModel):
        value = PersonalRemoveCollectionMutation(
            collection_id=mutation.collection_id
        )
    elif isinstance(mutation, PersonalSetCollectionMembersModel):
        value = PersonalSetCollectionMembersMutation(
            collection_id=mutation.collection_id,
            member_record_ids=tuple(mutation.member_record_ids),
        )
    elif isinstance(mutation, PersonalReorderRecordsModel):
        value = PersonalReorderRecordsMutation(
            record_ids=tuple(mutation.record_ids)
        )
    elif isinstance(mutation, PersonalArchiveRecordModel):
        value = PersonalArchiveRecordMutation(record_id=mutation.record_id)
    elif isinstance(mutation, PersonalRestoreRecordModel):
        value = PersonalRestoreRecordMutation(record_id=mutation.record_id)
    elif isinstance(mutation, PersonalRefreshReferenceModel):
        value = PersonalRefreshReferenceMutation(record_id=mutation.record_id)
    else:
        value = PersonalRemoveRecordMutation(record_id=mutation.record_id)
    return PersonalWorkspaceMutationCommand(
        schema_version=model.schema_version,
        idempotency_key=model.idempotency_key,
        expected_revision=model.expected_revision,
        mutation=value,
    )


def personal_workspace_response(
    workspace: PersonalWorkspace,
) -> PersonalWorkspaceResponseModel:
    return PersonalWorkspaceResponseModel.model_validate(asdict(workspace))


def personal_workspace_export_response(
    export: PersonalWorkspaceExportView,
) -> PersonalWorkspaceExportResponseModel:
    return PersonalWorkspaceExportResponseModel.model_validate(asdict(export))


def personal_workspace_query(
    model: PersonalWorkspaceQueryRequestModel,
) -> PersonalWorkspaceQuery:
    return PersonalWorkspaceQuery(
        schema_version=model.schema_version,
        text=model.text,
        record_kinds=model.record_kinds,
        owner_modules=model.owner_modules,
        reference_kinds=model.reference_kinds,
        target_statuses=model.target_statuses,
        archived=model.archived,
        collection_id=model.collection_id,
        sort=model.sort,
        limit=model.limit,
        cursor=model.cursor,
    )


def personal_workspace_query_response(
    result: PersonalWorkspaceQueryResult,
) -> PersonalWorkspaceQueryResponseModel:
    query = asdict(result.applied_query)
    normalized_query = {
        key: value
        for key, value in query.items()
        if value is not None and value != ()
    }
    return PersonalWorkspaceQueryResponseModel.model_validate(
        {
            "schema_version": result.schema_version,
            "workspace_revision": result.workspace_revision,
            "query_digest": result.query_digest,
            "applied_query": normalized_query,
            "records": [asdict(record) for record in result.records],
            "next_cursor": result.next_cursor,
        }
    )


def _body_node(node: content_public.BodyNode) -> BodyNodeModel:
    if isinstance(node, content_public.Heading):
        return HeadingModel(
            level=node.level,
            children=[_inline_node(child) for child in node.children],
        )
    if isinstance(node, content_public.Paragraph):
        return ParagraphModel(
            children=[_inline_node(child) for child in node.children]
        )
    if isinstance(node, content_public.CodeBlock):
        return CodeBlockModel(code=node.code, language=node.language)
    if isinstance(node, content_public.ThematicBreak):
        return ThematicBreakModel()
    if isinstance(node, content_public.BulletList):
        return BulletListModel(
            items=[
                ListItemModel(
                    blocks=[_body_node(block) for block in item.blocks]
                )
                for item in node.items
            ]
        )
    if isinstance(node, content_public.OrderedList):
        return OrderedListModel(
            start=node.start,
            items=[
                ListItemModel(
                    blocks=[_body_node(block) for block in item.blocks]
                )
                for item in node.items
            ],
        )
    raise TypeError("Unsupported public body node.")

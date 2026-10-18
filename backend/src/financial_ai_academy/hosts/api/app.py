"""Thin FastAPI transport over Identity and Curriculum public operations."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
import json
from uuid import uuid4

from fastapi import (
    Depends,
    FastAPI,
    Path,
    Query,
    Request,
    Response,
    Security,
    status,
)
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyCookie

from financial_ai_academy.modules.adaptation.public import (
    ActivityLaunchError,
    ActivityLaunchErrorCode,
    AdaptationOperations,
    NavigationStateOperationError,
    NavigationStateOperationErrorCode,
    OpenActivityLaunchRequest,
    OpenNavigationStateRequest,
)
from financial_ai_academy.modules.assessment.public import (
    AssessmentError,
    AssessmentErrorCode,
    AssessmentOperations,
    OpenPlacedKnowledgeCheckRequest,
    OpenPlacedPracticeRequest,
    OpenProjectSubmissionCandidateRequest,
    PracticePresentation,
    ReadPlacedPracticeProgressRequest,
    SavePlacedPracticeDraftRequest,
    ReadProjectCompletionEvidenceRequest,
    ReadProjectCompletionHistoryRequest,
    SubmitPlacedKnowledgeCheckRequest,
    SubmitPlacedPracticeRequest,
    SubmitProjectSnapshotRequest,
)
from financial_ai_academy.modules.audit.public import (
    AuditError,
    AuditErrorCode,
    AuditOperations,
    ReconcileLessonCompletionAuditRequest,
    ReconcileProjectCompletionAuditRequest,
)
from financial_ai_academy.modules.content.public import (
    LessonErrorCode,
    LessonReadError,
)
from financial_ai_academy.modules.curriculum.public import (
    BrowseLearningOpportunitiesRequest,
    CurriculumGraphError,
    CurriculumGraphErrorCode,
    CurriculumOperations,
    DiscoveryError,
    DiscoveryErrorCode,
    OpenPlacedLessonRequest,
    OpenCurriculumGraphRequest,
    OpportunityAvailability,
    OpportunityKind,
    OpportunityLevel,
    OpportunityQuerySort,
    PracticeReviewError,
    PracticeReviewErrorCode,
    PracticeReviewResource,
    QueryLearningOpportunitiesRequest,
    ResolvePracticeReviewTargetsRequest,
)
from financial_ai_academy.modules.identity.public import (
    IdentityError,
    IdentityErrorCode,
    IdentityOperations,
    LearnerContext,
    SingleProfileBootstrapRequest,
)
from financial_ai_academy.modules.guidance.public import (
    GuidanceError,
    GuidanceErrorCode,
    GuidanceOperations,
    OpenContextualHelpRequest,
    OpenPlatformHelpTopicRequest,
    ResolveFeatureGuidanceRequest,
    SearchRequest as PlatformHelpSearchRequest,
    TopicKind as PlatformHelpTopicKind,
)
from financial_ai_academy.modules.learner_model.public import (
    ExportAssistancePreferencesRequest,
    ExportLearnerPreferencesRequest,
    ExportPresentationPreferencesRequest,
    LearnerModelError,
    LearnerModelErrorCode,
    LearnerModelOperations,
    MutateAssistancePreferencesRequest,
    MutateLearnerPreferencesRequest,
    MutatePresentationPreferencesRequest,
    OpenAssistancePreferencesRequest,
    OpenLearnerPreferencesRequest,
    OpenPresentationPreferencesRequest,
    OpenLessonCompletionRequest,
    OpenProjectCompletionRequest,
    OpenPracticeHistoryRequest,
    PracticeHistoryView,
    ReadAssistancePreferenceHistoryRequest,
    ReadLearnerPreferenceHistoryRequest,
    ReadPresentationPreferenceHistoryRequest,
)
from financial_ai_academy.modules.project.public import (
    CloseProjectSnapshotRequest,
    CreateProjectRequest,
    DownloadProjectArtifactRequest,
    ExportProjectSnapshotRequest,
    ListLearningProjectStartOptionsRequest,
    ListProjectSnapshotsRequest,
    ListProjectsRequest,
    MutateProjectWorkspaceRequest,
    OpenProjectRequest,
    OpenProjectSnapshotRequest,
    OpenProjectWorkspaceRequest,
    ProjectError,
    ProjectErrorCode,
    ProjectOperations,
    ResolveLearningProjectStartOptionRequest,
    UploadProjectArtifactRequest,
)
from financial_ai_academy.modules.personal_workspace.public import (
    ExportPersonalWorkspaceRequest,
    MutatePersonalWorkspaceRequest,
    OpenPersonalWorkspaceRequest,
    PersonalWorkspaceError,
    PersonalWorkspaceErrorCode,
    PersonalWorkspaceOperations,
    QueryPersonalWorkspaceRequest,
    ReadableReferenceKind,
)
from financial_ai_academy.platform.security.single_profile_policy import (
    RequestPolicyViolation,
    SingleProfileRequestPolicy,
)

from .models import (
    ActivityLaunchResponseModel,
    AssistancePreferenceExportResponseModel,
    AssistancePreferenceHistoryResponseModel,
    AssistancePreferenceMutationRequestModel,
    AssistancePreferenceProfileResponseModel,
    ApiErrorEnvelope,
    CurriculumGraphResponseModel,
    DiscoveryTopic,
    HealthResponseModel,
    KnowledgeCheckPresentationResponseModel,
    KnowledgeCheckResultResponseModel,
    KnowledgeCheckSubmissionRequestModel,
    LearningOpportunityBrowseResponseModel,
    LearningOpportunityQueryPageResponseModel,
    LearningProjectStartOptionResponseModel,
    LearningProjectStartOptionListResponseModel,
    LearnerPreferenceExportResponseModel,
    LearnerPreferenceHistoryResponseModel,
    LearnerPreferenceMutationRequestModel,
    LearnerPreferenceProfileResponseModel,
    PresentationPreferenceExportResponseModel,
    PresentationPreferenceHistoryResponseModel,
    PresentationPreferenceMutationRequestModel,
    PresentationPreferenceProfileResponseModel,
    LessonCompletionResponseModel,
    LessonReadingResponseModel,
    NavigationStateResponseModel,
    PracticePresentationResponseModel,
    PracticeDraftResponseModel,
    PracticeDraftSaveRequestModel,
    PracticeProgressResponseModel,
    PracticeSubmissionRequestModel,
    PracticeSubmissionResultResponseModel,
    ProjectCreateRequestModel,
    ProjectArtifactUploadRequestModel,
    ProjectEvidenceExportBundleResponseModel,
    ProjectCompletionEvidenceResponseModel,
    ProjectCompletionHistoryResponseModel,
    ProjectActivityCompletionResponseModel,
    ProjectListResponseModel,
    ProjectSnapshotCloseRequestModel,
    ProjectSnapshotListResponseModel,
    ProjectSnapshotResponseModel,
    ProjectSubmissionCandidateResponseModel,
    ProjectSubmissionOutcomeResponseModel,
    ProjectSubmissionRequestModel,
    ProjectShellResponseModel,
    ProjectWorkspaceMutationRequestModel,
    ProjectWorkspaceResponseModel,
    PersonalWorkspaceMutationRequestModel,
    PersonalWorkspaceExportResponseModel,
    PersonalWorkspaceQueryRequestModel,
    PersonalWorkspaceQueryResponseModel,
    PersonalWorkspaceResponseModel,
    ContextualHelpResponseModel,
    FeatureGuidanceResponseModel,
    PlatformHelpSearchPageResponseModel,
    PlatformHelpTopicResponseModel,
    SessionBootstrapRequestModel,
    SessionBootstrapResponseModel,
    assistance_preference_export_response,
    assistance_preference_history_response,
    assistance_preference_mutation_intent,
    assistance_preference_profile_response,
    activity_launch_response,
    curriculum_graph_response,
    knowledge_check_presentation_response,
    knowledge_check_result_response,
    learning_opportunity_browse_response,
    learning_opportunity_query_page_response,
    lesson_completion_response,
    lesson_response,
    learning_project_start_option_response,
    learning_project_start_option_list_response,
    learner_preference_export_response,
    learner_preference_history_response,
    learner_preference_mutation_intent,
    learner_preference_profile_response,
    presentation_preference_export_response,
    presentation_preference_history_response,
    presentation_preference_mutation_intent,
    presentation_preference_profile_response,
    navigation_state_response,
    practice_presentation_response,
    practice_draft_response,
    practice_progress_response,
    practice_submission_result_response,
    project_create_intent,
    project_artifact_content,
    project_evidence_export_response,
    project_completion_evidence_response,
    project_completion_history_response,
    project_activity_completion_response,
    project_list_response,
    project_snapshot_close_intent,
    project_snapshot_list_response,
    project_snapshot_response,
    project_submission_candidate_response,
    project_submission_outcome_response,
    project_shell_response,
    project_workspace_mutation_intent,
    project_workspace_response,
    personal_workspace_mutation_command,
    personal_workspace_export_response,
    personal_workspace_query,
    personal_workspace_query_response,
    personal_workspace_response,
    personal_workspace_source_permission,
    contextual_help_response,
    feature_guidance_response,
    platform_help_search_page_response,
    platform_help_topic_response,
)


@dataclass(frozen=True, slots=True)
class ApiServices:
    identity: IdentityOperations
    curriculum: CurriculumOperations
    request_policy: SingleProfileRequestPolicy
    assessment: AssessmentOperations | None = None
    learner_model: LearnerModelOperations | None = None
    adaptation: AdaptationOperations | None = None
    audit: AuditOperations | None = None
    project: ProjectOperations | None = None
    personal_workspace: PersonalWorkspaceOperations | None = None
    guidance: GuidanceOperations | None = None


_ERROR_RESPONSES = {
    400: {"model": ApiErrorEnvelope, "description": "Invalid request"},
    401: {"model": ApiErrorEnvelope, "description": "Unauthorized"},
    403: {"model": ApiErrorEnvelope, "description": "Forbidden"},
    404: {"model": ApiErrorEnvelope, "description": "Not found"},
    409: {"model": ApiErrorEnvelope, "description": "Conflict"},
    503: {"model": ApiErrorEnvelope, "description": "Unavailable"},
}


def _readable_reference_kinds(
    permissions: tuple[str, ...],
) -> frozenset[ReadableReferenceKind]:
    readable: set[ReadableReferenceKind] = set()
    if "curriculum.discovery.read" in permissions:
        readable.add("learning_opportunity")
    if "curriculum.lesson.read" in permissions:
        readable.add("placed_lesson")
    if "project.read" in permissions:
        readable.update(
            {"project_workspace", "project_snapshot", "project_artifact"}
        )
    return frozenset(readable)


def create_app(services: ApiServices) -> FastAPI:
    app = FastAPI(
        title="Financial AI Academy API",
        version="1.0.0",
        openapi_version="3.1.0",
        docs_url=None,
        redoc_url=None,
    )
    cookie_name = services.request_policy.settings.cookie_name
    session_cookie = APIKeyCookie(
        name=cookie_name,
        scheme_name="OpaqueSessionCookie",
        description=(
            "Opaque server-side session cookie. The value is never an "
            "identity selector and is not readable by browser scripts."
        ),
        auto_error=False,
    )

    @app.middleware("http")
    async def enforce_local_boundary(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        correlation_id = str(uuid4())
        request.state.correlation_id = correlation_id
        try:
            services.request_policy.verify(
                request.headers,
                state_changing=request.method
                not in {"GET", "HEAD", "OPTIONS"},
            )
        except RequestPolicyViolation:
            response = _error_response(
                status.HTTP_403_FORBIDDEN,
                "forbidden",
                "The request is not allowed by the local security boundary.",
                correlation_id,
            )
        else:
            try:
                response = await call_next(request)
            except Exception:
                response = _error_response(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "internal_error",
                    "The request could not be completed.",
                    correlation_id,
                )
        response.headers["X-Correlation-ID"] = correlation_id
        response.headers["Cache-Control"] = "no-store"
        return response

    @app.exception_handler(IdentityError)
    async def identity_error_handler(
        request: Request, error: IdentityError
    ) -> JSONResponse:
        http_status = {
            IdentityErrorCode.UNAUTHORIZED: status.HTTP_401_UNAUTHORIZED,
            IdentityErrorCode.FORBIDDEN: status.HTTP_403_FORBIDDEN,
            IdentityErrorCode.UNSAFE_CONFIGURATION: (
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            IdentityErrorCode.MODE_MISMATCH: (
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            IdentityErrorCode.UNAVAILABLE: status.HTTP_503_SERVICE_UNAVAILABLE,
        }[error.code]
        return _error_response(
            http_status,
            error.code.value,
            error.safe_message,
            request.state.correlation_id,
        )

    @app.exception_handler(GuidanceError)
    async def guidance_error_handler(
        request: Request, error: GuidanceError
    ) -> JSONResponse:
        http_status = {
            GuidanceErrorCode.INVALID_RECORD: status.HTTP_400_BAD_REQUEST,
            GuidanceErrorCode.UNSUPPORTED_VERSION: status.HTTP_409_CONFLICT,
            GuidanceErrorCode.DIGEST_MISMATCH: (
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            GuidanceErrorCode.DUPLICATE_IDENTITY: (
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            GuidanceErrorCode.DANGLING_REFERENCE: (
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            GuidanceErrorCode.NOT_FOUND: status.HTTP_404_NOT_FOUND,
            GuidanceErrorCode.INVALID_CURSOR: status.HTTP_409_CONFLICT,
            GuidanceErrorCode.UNAVAILABLE: status.HTTP_503_SERVICE_UNAVAILABLE,
        }[error.code]
        return _error_response(
            http_status,
            error.code.value,
            error.message,
            request.state.correlation_id,
        )

    @app.exception_handler(LessonReadError)
    async def lesson_error_handler(
        request: Request, error: LessonReadError
    ) -> JSONResponse:
        http_status = {
            LessonErrorCode.INVALID_PACKAGE: status.HTTP_400_BAD_REQUEST,
            LessonErrorCode.UNSUPPORTED_VERSION: status.HTTP_409_CONFLICT,
            LessonErrorCode.IMMUTABLE_CONFLICT: status.HTTP_409_CONFLICT,
            LessonErrorCode.INTEGRITY_FAILURE: (
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            LessonErrorCode.NOT_FOUND: status.HTTP_404_NOT_FOUND,
            LessonErrorCode.UNAVAILABLE: status.HTTP_503_SERVICE_UNAVAILABLE,
        }[error.code]
        return _error_response(
            http_status,
            error.code.value,
            error.message,
            request.state.correlation_id,
        )

    @app.exception_handler(DiscoveryError)
    async def discovery_error_handler(
        request: Request, error: DiscoveryError
    ) -> JSONResponse:
        http_status = {
            DiscoveryErrorCode.INVALID_RECORD: (
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            DiscoveryErrorCode.INVALID_QUERY: status.HTTP_400_BAD_REQUEST,
            DiscoveryErrorCode.IMMUTABLE_CONFLICT: status.HTTP_409_CONFLICT,
            DiscoveryErrorCode.STALE_CURSOR: status.HTTP_409_CONFLICT,
            DiscoveryErrorCode.STALE_SOURCE: (
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            DiscoveryErrorCode.UNAVAILABLE: (
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
        }[error.code]
        return _error_response(
            http_status,
            error.code.value,
            error.message,
            request.state.correlation_id,
        )

    @app.exception_handler(ProjectError)
    async def project_error_handler(
        request: Request, error: ProjectError
    ) -> JSONResponse:
        http_status = {
            ProjectErrorCode.INVALID_REQUEST: status.HTTP_400_BAD_REQUEST,
            ProjectErrorCode.IMMUTABLE_CONFLICT: status.HTTP_409_CONFLICT,
            ProjectErrorCode.STALE_REVISION: status.HTTP_409_CONFLICT,
            ProjectErrorCode.INTEGRITY_FAILURE: (
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            ProjectErrorCode.NOT_FOUND: status.HTTP_404_NOT_FOUND,
            ProjectErrorCode.UNAVAILABLE: status.HTTP_503_SERVICE_UNAVAILABLE,
        }[error.code]
        return _error_response(
            http_status,
            error.code.value,
            error.message,
            request.state.correlation_id,
        )

    @app.exception_handler(PersonalWorkspaceError)
    async def personal_workspace_error_handler(
        request: Request, error: PersonalWorkspaceError
    ) -> JSONResponse:
        http_status = {
            PersonalWorkspaceErrorCode.INVALID_REQUEST: status.HTTP_400_BAD_REQUEST,
            PersonalWorkspaceErrorCode.IMMUTABLE_CONFLICT: status.HTTP_409_CONFLICT,
            PersonalWorkspaceErrorCode.STALE_REVISION: status.HTTP_409_CONFLICT,
            PersonalWorkspaceErrorCode.SOURCE_UNAVAILABLE: status.HTTP_409_CONFLICT,
            PersonalWorkspaceErrorCode.NOT_FOUND: status.HTTP_404_NOT_FOUND,
            PersonalWorkspaceErrorCode.RECORD_LIMIT: status.HTTP_409_CONFLICT,
            PersonalWorkspaceErrorCode.COLLECTION_LIMIT: status.HTTP_409_CONFLICT,
            PersonalWorkspaceErrorCode.COLLECTION_MEMBER_LIMIT: (
                status.HTTP_409_CONFLICT
            ),
            PersonalWorkspaceErrorCode.INTEGRITY_FAILURE: (
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            PersonalWorkspaceErrorCode.UNAVAILABLE: (
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
        }[error.code]
        return _error_response(
            http_status,
            error.code.value,
            error.message,
            request.state.correlation_id,
        )

    @app.exception_handler(CurriculumGraphError)
    async def curriculum_graph_error_handler(
        request: Request, error: CurriculumGraphError
    ) -> JSONResponse:
        http_status = {
            CurriculumGraphErrorCode.INVALID_RECORD: (
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            CurriculumGraphErrorCode.UNSUPPORTED_VERSION: (
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            CurriculumGraphErrorCode.IMMUTABLE_CONFLICT: (
                status.HTTP_409_CONFLICT
            ),
            CurriculumGraphErrorCode.NOT_FOUND: status.HTTP_404_NOT_FOUND,
            CurriculumGraphErrorCode.STALE_REFERENCE: (
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            CurriculumGraphErrorCode.UNAVAILABLE: (
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            CurriculumGraphErrorCode.DUPLICATE_IDENTITY: (
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            CurriculumGraphErrorCode.DANGLING_REFERENCE: (
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            CurriculumGraphErrorCode.INVALID_RELATIONSHIP: (
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            CurriculumGraphErrorCode.DUPLICATE_BRANCH_MEMBERSHIP: (
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            CurriculumGraphErrorCode.AMBIGUOUS_BRANCH_MEMBERSHIP: (
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            CurriculumGraphErrorCode.PREREQUISITE_CYCLE: (
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            CurriculumGraphErrorCode.REFERENCE_KIND_MISMATCH: (
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            CurriculumGraphErrorCode.GRAPH_DIGEST_MISMATCH: (
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
        }[error.code]
        return _error_response(
            http_status,
            error.code.value,
            error.message,
            request.state.correlation_id,
        )

    @app.exception_handler(PracticeReviewError)
    async def practice_review_error_handler(
        request: Request, error: PracticeReviewError
    ) -> JSONResponse:
        http_status = {
            PracticeReviewErrorCode.INVALID_RECORD: (
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            PracticeReviewErrorCode.IMMUTABLE_CONFLICT: (
                status.HTTP_409_CONFLICT
            ),
            PracticeReviewErrorCode.UNAVAILABLE: (
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
        }[error.code]
        return _error_response(
            http_status,
            error.code.value,
            error.message,
            request.state.correlation_id,
        )

    @app.exception_handler(AssessmentError)
    async def assessment_error_handler(
        request: Request, error: AssessmentError
    ) -> JSONResponse:
        http_status = {
            AssessmentErrorCode.INVALID_DEFINITION: (
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            AssessmentErrorCode.INVALID_SUBMISSION: (
                status.HTTP_400_BAD_REQUEST
            ),
            AssessmentErrorCode.UNSUPPORTED_VERSION: (
                status.HTTP_409_CONFLICT
            ),
            AssessmentErrorCode.NOT_FOUND: status.HTTP_404_NOT_FOUND,
            AssessmentErrorCode.STALE_REFERENCE: status.HTTP_409_CONFLICT,
            AssessmentErrorCode.UNKNOWN_OPTION: status.HTTP_400_BAD_REQUEST,
            AssessmentErrorCode.CONFLICT: status.HTTP_409_CONFLICT,
            AssessmentErrorCode.ALREADY_COMPLETED: (
                status.HTTP_409_CONFLICT
            ),
            AssessmentErrorCode.ATTEMPT_LIMIT_REACHED: (
                status.HTTP_409_CONFLICT
            ),
            AssessmentErrorCode.UNAUTHORIZED_CONTEXT: (
                status.HTTP_401_UNAUTHORIZED
            ),
            AssessmentErrorCode.UNAVAILABLE: (
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
        }[error.code]
        return _error_response(
            http_status,
            error.code.value,
            error.safe_message,
            request.state.correlation_id,
        )

    @app.exception_handler(AuditError)
    async def audit_error_handler(
        request: Request, error: AuditError
    ) -> JSONResponse:
        http_status = {
            AuditErrorCode.INVALID_CONTEXT: status.HTTP_401_UNAUTHORIZED,
            AuditErrorCode.INCONSISTENT_EVIDENCE: (
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            AuditErrorCode.CONFLICT: status.HTTP_409_CONFLICT,
            AuditErrorCode.UNAVAILABLE: status.HTTP_503_SERVICE_UNAVAILABLE,
        }[error.code]
        return _error_response(
            http_status,
            error.code.value,
            error.safe_message,
            request.state.correlation_id,
        )

    @app.exception_handler(LearnerModelError)
    async def learner_model_error_handler(
        request: Request, error: LearnerModelError
    ) -> JSONResponse:
        http_status = {
            LearnerModelErrorCode.INVALID_REQUEST: (
                status.HTTP_400_BAD_REQUEST
            ),
            LearnerModelErrorCode.INVALID_CONTEXT: (
                status.HTTP_401_UNAUTHORIZED
            ),
            LearnerModelErrorCode.INCONSISTENT_EVIDENCE: (
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            LearnerModelErrorCode.IMMUTABLE_CONFLICT: (
                status.HTTP_409_CONFLICT
            ),
            LearnerModelErrorCode.STALE_REVISION: (
                status.HTTP_409_CONFLICT
            ),
            LearnerModelErrorCode.NOT_FOUND: status.HTTP_404_NOT_FOUND,
            LearnerModelErrorCode.PREFERENCE_LIMIT: (
                status.HTTP_409_CONFLICT
            ),
            LearnerModelErrorCode.INTEGRITY_FAILURE: (
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            LearnerModelErrorCode.UNAVAILABLE: (
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
        }[error.code]
        return _error_response(
            http_status,
            error.code.value,
            error.safe_message,
            request.state.correlation_id,
        )

    @app.exception_handler(NavigationStateOperationError)
    async def navigation_state_operation_error_handler(
        request: Request, error: NavigationStateOperationError
    ) -> JSONResponse:
        http_status = {
            NavigationStateOperationErrorCode.INVALID_CONTEXT: (
                status.HTTP_401_UNAUTHORIZED
            ),
            NavigationStateOperationErrorCode.NOT_FOUND: (
                status.HTTP_404_NOT_FOUND
            ),
            NavigationStateOperationErrorCode.UNAVAILABLE: (
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
        }[error.code]
        return _error_response(
            http_status,
            error.code.value,
            error.safe_message,
            request.state.correlation_id,
        )

    @app.exception_handler(ActivityLaunchError)
    async def activity_launch_error_handler(
        request: Request, error: ActivityLaunchError
    ) -> JSONResponse:
        http_status = {
            ActivityLaunchErrorCode.INVALID_CONTEXT: (
                status.HTTP_400_BAD_REQUEST
            ),
            ActivityLaunchErrorCode.ACTIVITY_NOT_FOUND: (
                status.HTTP_404_NOT_FOUND
            ),
            ActivityLaunchErrorCode.ACTIVITY_LOCKED: status.HTTP_409_CONFLICT,
            ActivityLaunchErrorCode.ACTIVITY_UNAVAILABLE: (
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            ActivityLaunchErrorCode.UNSUPPORTED_ACTIVITY: (
                status.HTTP_409_CONFLICT
            ),
        }[error.code]
        return _error_response(
            http_status,
            error.code.value,
            error.message,
            request.state.correlation_id,
        )

    @app.exception_handler(RequestValidationError)
    async def request_validation_handler(
        request: Request, _error: RequestValidationError
    ) -> JSONResponse:
        return _error_response(
            status.HTTP_400_BAD_REQUEST,
            "invalid_request",
            "The request does not satisfy the API contract.",
            request.state.correlation_id,
        )

    def resolved_context(
        cookie_value: str | None = Security(session_cookie),
    ) -> LearnerContext:
        return services.identity.resolve_session(cookie_value)

    def lesson_context(
        context: LearnerContext = Depends(resolved_context),
    ) -> LearnerContext:
        if "curriculum.lesson.read" not in context.permissions:
            raise IdentityError(
                IdentityErrorCode.FORBIDDEN,
                "The learner session cannot read lessons.",
            )
        return context

    def discovery_context(
        context: LearnerContext = Depends(resolved_context),
    ) -> LearnerContext:
        if "curriculum.discovery.read" not in context.permissions:
            raise IdentityError(
                IdentityErrorCode.FORBIDDEN,
                "The learner session cannot browse learning opportunities.",
            )
        return context

    def curriculum_graph_context(
        context: LearnerContext = Depends(resolved_context),
    ) -> LearnerContext:
        if "curriculum.graph.read" not in context.permissions:
            raise IdentityError(
                IdentityErrorCode.FORBIDDEN,
                "The learner session cannot read curriculum graphs.",
            )
        return context

    def guidance_context(
        context: LearnerContext = Depends(resolved_context),
    ) -> LearnerContext:
        if "guidance.platform_help.read" not in context.permissions:
            raise IdentityError(
                IdentityErrorCode.FORBIDDEN,
                "The learner session cannot read platform help.",
            )
        return context

    def guidance_operations() -> GuidanceOperations:
        if services.guidance is None:
            raise GuidanceError(
                GuidanceErrorCode.UNAVAILABLE,
                "Platform help is unavailable.",
            )
        return services.guidance

    def adaptation_context(
        context: LearnerContext = Depends(resolved_context),
    ) -> LearnerContext:
        if "adaptation.navigation.read" not in context.permissions:
            raise IdentityError(
                IdentityErrorCode.FORBIDDEN,
                "The learner session cannot read navigation state.",
            )
        return context

    def activity_launch_context(
        context: LearnerContext = Depends(resolved_context),
    ) -> LearnerContext:
        if not {
            "adaptation.navigation.read",
            "curriculum.lesson.read",
        }.issubset(context.permissions):
            raise IdentityError(
                IdentityErrorCode.FORBIDDEN,
                "The learner session cannot open this activity.",
            )
        return context

    def project_create_context(
        context: LearnerContext = Depends(resolved_context),
    ) -> LearnerContext:
        if "project.create" not in context.permissions:
            raise IdentityError(
                IdentityErrorCode.FORBIDDEN,
                "The learner session cannot create Projects.",
            )
        return context

    def project_read_context(
        context: LearnerContext = Depends(resolved_context),
    ) -> LearnerContext:
        if "project.read" not in context.permissions:
            raise IdentityError(
                IdentityErrorCode.FORBIDDEN,
                "The learner session cannot read Projects.",
            )
        return context

    def project_write_context(
        context: LearnerContext = Depends(resolved_context),
    ) -> LearnerContext:
        if "project.write" not in context.permissions:
            raise IdentityError(
                IdentityErrorCode.FORBIDDEN,
                "The learner session cannot change Project work.",
            )
        return context

    def project_operations() -> ProjectOperations:
        if services.project is None:
            raise ProjectError(
                ProjectErrorCode.UNAVAILABLE,
                "Project operations are unavailable.",
            )
        return services.project

    def personal_workspace_read_context(
        context: LearnerContext = Depends(resolved_context),
    ) -> LearnerContext:
        if "personal_workspace.read" not in context.permissions:
            raise IdentityError(
                IdentityErrorCode.FORBIDDEN,
                "The learner session cannot read saved learning.",
            )
        return context

    def personal_workspace_write_context(
        context: LearnerContext = Depends(resolved_context),
    ) -> LearnerContext:
        if "personal_workspace.write" not in context.permissions:
            raise IdentityError(
                IdentityErrorCode.FORBIDDEN,
                "The learner session cannot change saved learning.",
            )
        return context

    def personal_workspace_operations() -> PersonalWorkspaceOperations:
        if services.personal_workspace is None:
            raise PersonalWorkspaceError(
                PersonalWorkspaceErrorCode.UNAVAILABLE,
                "The personal workspace is unavailable.",
            )
        return services.personal_workspace

    def learner_preferences_read_context(
        context: LearnerContext = Depends(resolved_context),
    ) -> LearnerContext:
        if "learner_preferences.read" not in context.permissions:
            raise IdentityError(
                IdentityErrorCode.FORBIDDEN,
                "The learner session cannot read learning preferences.",
            )
        return context

    def learner_preferences_write_context(
        context: LearnerContext = Depends(resolved_context),
    ) -> LearnerContext:
        if "learner_preferences.write" not in context.permissions:
            raise IdentityError(
                IdentityErrorCode.FORBIDDEN,
                "The learner session cannot change learning preferences.",
            )
        return context

    def presentation_preferences_read_context(
        context: LearnerContext = Depends(resolved_context),
    ) -> LearnerContext:
        if "learner_presentation_preferences.read" not in context.permissions:
            raise IdentityError(
                IdentityErrorCode.FORBIDDEN,
                "The learner session cannot read display choices.",
            )
        return context

    def presentation_preferences_write_context(
        context: LearnerContext = Depends(resolved_context),
    ) -> LearnerContext:
        if "learner_presentation_preferences.write" not in context.permissions:
            raise IdentityError(
                IdentityErrorCode.FORBIDDEN,
                "The learner session cannot change display choices.",
            )
        return context

    def assistance_preferences_read_context(
        context: LearnerContext = Depends(resolved_context),
    ) -> LearnerContext:
        if "learner_assistance_preferences.read" not in context.permissions:
            raise IdentityError(
                IdentityErrorCode.FORBIDDEN,
                "The learner session cannot read the AI-help choice.",
            )
        return context

    def assistance_preferences_write_context(
        context: LearnerContext = Depends(resolved_context),
    ) -> LearnerContext:
        if "learner_assistance_preferences.write" not in context.permissions:
            raise IdentityError(
                IdentityErrorCode.FORBIDDEN,
                "The learner session cannot change the AI-help choice.",
            )
        return context

    @app.get(
        "/health",
        response_model=HealthResponseModel,
        operation_id="getHealth",
        tags=["operations"],
    )
    def health() -> HealthResponseModel:
        return HealthResponseModel(status="ok")

    @app.get(
        "/ready",
        response_model=HealthResponseModel,
        operation_id="getReadiness",
        responses={503: _ERROR_RESPONSES[503]},
        tags=["operations"],
    )
    def readiness(request: Request) -> HealthResponseModel | JSONResponse:
        if services.identity.health():
            return HealthResponseModel(status="ready")
        return _error_response(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "not_ready",
            "The application is not ready.",
            request.state.correlation_id,
        )

    @app.post(
        "/api/v1/session/single-profile",
        response_model=SessionBootstrapResponseModel,
        status_code=status.HTTP_201_CREATED,
        operation_id="bootstrapSingleProfileSession",
        responses=_ERROR_RESPONSES,
        tags=["session"],
    )
    def bootstrap_single_profile_session(
        request_model: SessionBootstrapRequestModel,
        response: Response,
    ) -> SessionBootstrapResponseModel:
        issued = services.identity.bootstrap_single_profile(
            SingleProfileBootstrapRequest(
                limitation_acknowledged=(
                    request_model.limitation_acknowledged
                )
            )
        )
        settings = services.request_policy.settings
        response.set_cookie(
            key=settings.cookie_name,
            value=issued.cookie_value,
            max_age=settings.absolute_session_seconds,
            httponly=True,
            secure=settings.secure_cookie,
            samesite="strict",
            path="/",
        )
        return SessionBootstrapResponseModel(
            expires_at=issued.context.expires_at
        )

    @app.post(
        "/api/v1/projects",
        response_model=ProjectShellResponseModel,
        operation_id="createProject",
        responses=_ERROR_RESPONSES,
        tags=["projects"],
    )
    def create_project(
        request_model: ProjectCreateRequestModel,
        context: LearnerContext = Depends(project_create_context),
    ) -> ProjectShellResponseModel:
        shell = project_operations().create_project(
            CreateProjectRequest(
                learner_id=context.learner_id,
                intent=project_create_intent(request_model),
            )
        )
        return project_shell_response(shell)

    @app.get(
        "/api/v1/personal-workspace",
        response_model=PersonalWorkspaceResponseModel,
        operation_id="getPersonalWorkspace",
        responses=_ERROR_RESPONSES,
        tags=["personal-workspace"],
    )
    def get_personal_workspace(
        request: Request,
        context: LearnerContext = Depends(personal_workspace_read_context),
    ) -> PersonalWorkspaceResponseModel:
        if request.query_params:
            raise PersonalWorkspaceError(
                PersonalWorkspaceErrorCode.INVALID_REQUEST,
                "Saved learning does not accept query selectors.",
            )
        workspace = personal_workspace_operations().open_workspace(
            OpenPersonalWorkspaceRequest(learner_id=context.learner_id)
        )
        return personal_workspace_response(workspace)

    @app.get(
        "/api/v1/personal-workspace/export",
        response_model=PersonalWorkspaceExportResponseModel,
        operation_id="exportPersonalWorkspace",
        responses=_ERROR_RESPONSES,
        tags=["personal-workspace"],
    )
    async def export_personal_workspace(
        request: Request,
        context: LearnerContext = Depends(personal_workspace_read_context),
    ) -> PersonalWorkspaceExportResponseModel:
        if request.query_params or await request.body():
            raise PersonalWorkspaceError(
                PersonalWorkspaceErrorCode.INVALID_REQUEST,
                "Saved learning export does not accept request input.",
            )
        exported = personal_workspace_operations().export_workspace(
            ExportPersonalWorkspaceRequest(learner_id=context.learner_id)
        )
        return personal_workspace_export_response(exported)

    @app.post(
        "/api/v1/personal-workspace/query",
        response_model=PersonalWorkspaceQueryResponseModel,
        operation_id="queryPersonalWorkspace",
        responses=_ERROR_RESPONSES,
        tags=["personal-workspace"],
    )
    def query_personal_workspace(
        request_model: PersonalWorkspaceQueryRequestModel,
        request: Request,
        context: LearnerContext = Depends(personal_workspace_read_context),
    ) -> PersonalWorkspaceQueryResponseModel:
        if request.query_params:
            raise PersonalWorkspaceError(
                PersonalWorkspaceErrorCode.INVALID_REQUEST,
                "Saved learning search does not accept URL query selectors.",
            )
        result = personal_workspace_operations().query_workspace(
            QueryPersonalWorkspaceRequest(
                learner_id=context.learner_id,
                query=personal_workspace_query(request_model),
            )
        )
        return personal_workspace_query_response(result)

    @app.post(
        "/api/v1/personal-workspace/mutations",
        response_model=PersonalWorkspaceResponseModel,
        operation_id="mutatePersonalWorkspace",
        responses=_ERROR_RESPONSES,
        tags=["personal-workspace"],
    )
    def mutate_personal_workspace(
        request_model: PersonalWorkspaceMutationRequestModel,
        request: Request,
        context: LearnerContext = Depends(personal_workspace_write_context),
    ) -> PersonalWorkspaceResponseModel:
        if request.query_params:
            raise PersonalWorkspaceError(
                PersonalWorkspaceErrorCode.INVALID_REQUEST,
                "Saved learning does not accept query selectors.",
            )
        source_permission = personal_workspace_source_permission(request_model)
        if (
            source_permission is not None
            and source_permission not in context.permissions
        ):
            raise IdentityError(
                IdentityErrorCode.FORBIDDEN,
                "The learner session cannot read the learning item being saved.",
            )
        workspace = personal_workspace_operations().mutate_workspace(
            MutatePersonalWorkspaceRequest(
                learner_id=context.learner_id,
                command=personal_workspace_mutation_command(request_model),
                readable_reference_kinds=_readable_reference_kinds(
                    context.permissions
                ),
            )
        )
        return personal_workspace_response(workspace)

    @app.get(
        "/api/v1/projects",
        response_model=ProjectListResponseModel,
        operation_id="listProjects",
        responses=_ERROR_RESPONSES,
        tags=["projects"],
    )
    def list_projects(
        context: LearnerContext = Depends(project_read_context),
    ) -> ProjectListResponseModel:
        shells = project_operations().list_projects(
            ListProjectsRequest(learner_id=context.learner_id)
        )
        return project_list_response(shells)

    @app.get(
        "/api/v1/projects/start-options",
        response_model=LearningProjectStartOptionListResponseModel,
        operation_id="listLearningProjectStartOptions",
        responses=_ERROR_RESPONSES,
        tags=["projects"],
    )
    def list_learning_project_start_options(
        _context: LearnerContext = Depends(project_create_context),
    ) -> LearningProjectStartOptionListResponseModel:
        options = project_operations().list_learning_project_start_options(
            ListLearningProjectStartOptionsRequest()
        )
        return learning_project_start_option_list_response(options)

    @app.get(
        "/api/v1/projects/start-options/{placement_id}",
        response_model=LearningProjectStartOptionResponseModel,
        operation_id="getLearningProjectStartOption",
        responses=_ERROR_RESPONSES,
        tags=["projects"],
    )
    def get_learning_project_start_option(
        placement_id: str = Path(
            min_length=1,
            max_length=128,
            pattern=r"^[a-z0-9][a-z0-9._-]*$",
        ),
        _context: LearnerContext = Depends(project_create_context),
    ) -> LearningProjectStartOptionResponseModel:
        option = project_operations().resolve_learning_project_start_option(
            ResolveLearningProjectStartOptionRequest(
                placement_id=placement_id
            )
        )
        return learning_project_start_option_response(option)

    @app.get(
        "/api/v1/projects/{project_id}",
        response_model=ProjectShellResponseModel,
        operation_id="getProject",
        responses=_ERROR_RESPONSES,
        tags=["projects"],
    )
    def get_project(
        project_id: str = Path(
            min_length=1,
            max_length=128,
            pattern=r"^[a-z0-9][a-z0-9._-]*$",
        ),
        context: LearnerContext = Depends(project_read_context),
    ) -> ProjectShellResponseModel:
        shell = project_operations().open_project(
            OpenProjectRequest(
                learner_id=context.learner_id,
                project_id=project_id,
            )
        )
        return project_shell_response(shell)

    @app.get(
        "/api/v1/projects/{project_id}/workspace",
        response_model=ProjectWorkspaceResponseModel,
        operation_id="getProjectWorkspace",
        responses=_ERROR_RESPONSES,
        tags=["projects"],
    )
    def get_project_workspace(
        project_id: str = Path(
            min_length=1,
            max_length=128,
            pattern=r"^[a-z0-9][a-z0-9._-]*$",
        ),
        context: LearnerContext = Depends(project_read_context),
    ) -> ProjectWorkspaceResponseModel:
        workspace = project_operations().open_workspace(
            OpenProjectWorkspaceRequest(context.learner_id, project_id)
        )
        return project_workspace_response(workspace)

    @app.post(
        "/api/v1/projects/{project_id}/workspace/mutations",
        response_model=ProjectWorkspaceResponseModel,
        operation_id="mutateProjectWorkspace",
        responses=_ERROR_RESPONSES,
        tags=["projects"],
    )
    def mutate_project_workspace(
        request_model: ProjectWorkspaceMutationRequestModel,
        project_id: str = Path(
            min_length=1,
            max_length=128,
            pattern=r"^[a-z0-9][a-z0-9._-]*$",
        ),
        context: LearnerContext = Depends(project_write_context),
    ) -> ProjectWorkspaceResponseModel:
        workspace = project_operations().mutate_workspace(
            MutateProjectWorkspaceRequest(
                context.learner_id,
                project_id,
                project_workspace_mutation_intent(request_model),
            )
        )
        return project_workspace_response(workspace)

    @app.post(
        "/api/v1/projects/{project_id}/artifacts",
        response_model=ProjectWorkspaceResponseModel,
        operation_id="uploadProjectArtifact",
        responses=_ERROR_RESPONSES,
        tags=["projects"],
    )
    def upload_project_artifact(
        request_model: ProjectArtifactUploadRequestModel,
        project_id: str = Path(
            min_length=1,
            max_length=128,
            pattern=r"^[a-z0-9][a-z0-9._-]*$",
        ),
        context: LearnerContext = Depends(project_write_context),
    ) -> ProjectWorkspaceResponseModel:
        workspace = project_operations().upload_artifact(
            UploadProjectArtifactRequest(
                context.learner_id,
                project_id,
                project_workspace_mutation_intent(request_model.intent),
                project_artifact_content(request_model),
            )
        )
        return project_workspace_response(workspace)

    @app.get(
        "/api/v1/projects/{project_id}/artifacts/{artifact_id}/versions/{artifact_version}",
        operation_id="downloadProjectArtifact",
        responses={
            **_ERROR_RESPONSES,
            200: {
                "description": "Exact inert Project artifact bytes",
                "content": {
                    "application/octet-stream": {
                        "schema": {"type": "string", "format": "binary"}
                    }
                },
            },
        },
        tags=["projects"],
    )
    def download_project_artifact(
        project_id: str = Path(min_length=1, max_length=128),
        artifact_id: str = Path(min_length=1, max_length=128),
        artifact_version: int = Path(ge=1),
        context: LearnerContext = Depends(project_read_context),
    ) -> Response:
        downloaded = project_operations().download_artifact(
            DownloadProjectArtifactRequest(
                context.learner_id,
                project_id,
                artifact_id,
                artifact_version,
            )
        )
        return Response(
            content=downloaded.content,
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": "attachment; filename=project-artifact",
                "X-Content-Type-Options": "nosniff",
                "X-Content-SHA256": downloaded.artifact.content_digest,
                "X-Artifact-Media-Type": downloaded.artifact.media_type,
            },
        )

    @app.post(
        "/api/v1/projects/{project_id}/snapshots",
        response_model=ProjectSnapshotResponseModel,
        operation_id="closeProjectSnapshot",
        responses=_ERROR_RESPONSES,
        tags=["projects"],
    )
    def close_project_snapshot(
        request_model: ProjectSnapshotCloseRequestModel,
        project_id: str = Path(min_length=1, max_length=128),
        context: LearnerContext = Depends(project_write_context),
    ) -> ProjectSnapshotResponseModel:
        snapshot = project_operations().close_snapshot(
            CloseProjectSnapshotRequest(
                context.learner_id,
                project_id,
                project_snapshot_close_intent(request_model),
            )
        )
        return project_snapshot_response(snapshot)

    @app.get(
        "/api/v1/projects/{project_id}/snapshots",
        response_model=ProjectSnapshotListResponseModel,
        operation_id="listProjectSnapshots",
        responses=_ERROR_RESPONSES,
        tags=["projects"],
    )
    def list_project_snapshots(
        project_id: str = Path(min_length=1, max_length=128),
        context: LearnerContext = Depends(project_read_context),
    ) -> ProjectSnapshotListResponseModel:
        snapshots = project_operations().list_snapshots(
            ListProjectSnapshotsRequest(context.learner_id, project_id)
        )
        return project_snapshot_list_response(snapshots)

    @app.get(
        "/api/v1/projects/{project_id}/snapshots/{snapshot_id}",
        response_model=ProjectSnapshotResponseModel,
        operation_id="getProjectSnapshot",
        responses=_ERROR_RESPONSES,
        tags=["projects"],
    )
    def get_project_snapshot(
        project_id: str = Path(min_length=1, max_length=128),
        snapshot_id: str = Path(min_length=1, max_length=128),
        context: LearnerContext = Depends(project_read_context),
    ) -> ProjectSnapshotResponseModel:
        snapshot = project_operations().open_snapshot(
            OpenProjectSnapshotRequest(
                context.learner_id, project_id, snapshot_id
            )
        )
        return project_snapshot_response(snapshot)

    @app.get(
        "/api/v1/projects/{project_id}/snapshots/{snapshot_id}/export",
        response_model=ProjectEvidenceExportBundleResponseModel,
        operation_id="exportProjectSnapshot",
        responses=_ERROR_RESPONSES,
        tags=["projects"],
    )
    def export_project_snapshot(
        project_id: str = Path(min_length=1, max_length=128),
        snapshot_id: str = Path(min_length=1, max_length=128),
        context: LearnerContext = Depends(project_read_context),
    ) -> ProjectEvidenceExportBundleResponseModel:
        exported = project_operations().export_snapshot(
            ExportProjectSnapshotRequest(
                context.learner_id, project_id, snapshot_id
            )
        )
        return project_evidence_export_response(exported)

    @app.get(
        "/api/v1/projects/{project_id}/snapshots/{snapshot_id}/submission-candidate",
        response_model=ProjectSubmissionCandidateResponseModel,
        response_model_exclude_none=True,
        operation_id="getProjectSubmissionCandidate",
        responses=_ERROR_RESPONSES,
        tags=["projects", "assessment"],
    )
    def get_project_submission_candidate(
        request: Request,
        project_id: str = Path(min_length=1, max_length=128),
        snapshot_id: str = Path(min_length=1, max_length=128),
        context: LearnerContext = Depends(project_read_context),
    ) -> ProjectSubmissionCandidateResponseModel:
        if request.query_params:
            raise AssessmentError(
                AssessmentErrorCode.INVALID_SUBMISSION,
                "Project submission opening does not accept query input.",
                reference="query",
            )
        candidate = _assessment_service(
            services.assessment
        ).open_project_submission_candidate(
            OpenProjectSubmissionCandidateRequest(
                learner_id=context.learner_id,
                project_id=project_id,
                snapshot_id=snapshot_id,
            )
        )
        return project_submission_candidate_response(candidate)

    @app.post(
        "/api/v1/projects/{project_id}/snapshots/{snapshot_id}/submissions",
        response_model=ProjectSubmissionOutcomeResponseModel,
        operation_id="submitProjectSnapshot",
        responses=_ERROR_RESPONSES,
        tags=["projects", "assessment"],
    )
    def submit_project_snapshot(
        request: Request,
        request_model: ProjectSubmissionRequestModel,
        project_id: str = Path(min_length=1, max_length=128),
        snapshot_id: str = Path(min_length=1, max_length=128),
        context: LearnerContext = Depends(project_write_context),
    ) -> ProjectSubmissionOutcomeResponseModel:
        if request.query_params:
            raise AssessmentError(
                AssessmentErrorCode.INVALID_SUBMISSION,
                "Project submission does not accept query input.",
                reference="query",
            )
        if (
            request_model.source.project_id != project_id
            or request_model.source.snapshot_id != snapshot_id
        ):
            raise AssessmentError(
                AssessmentErrorCode.STALE_REFERENCE,
                "Project submission source references do not match.",
                reference="source",
            )
        document = json.dumps(
            request_model.model_dump(mode="json", exclude_none=True),
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        outcome = _assessment_service(services.assessment).submit_project_snapshot(
            SubmitProjectSnapshotRequest(
                learner_id=context.learner_id,
                project_id=project_id,
                snapshot_id=snapshot_id,
                submission=document,
            )
        )
        return project_submission_outcome_response(outcome)

    @app.get(
        "/api/v1/projects/{project_id}/submissions",
        response_model=ProjectCompletionHistoryResponseModel,
        response_model_exclude_none=True,
        operation_id="getProjectSubmissionHistory",
        responses=_ERROR_RESPONSES,
        tags=["projects", "assessment"],
    )
    def get_project_submission_history(
        request: Request,
        project_id: str = Path(min_length=1, max_length=128),
        context: LearnerContext = Depends(project_read_context),
    ) -> ProjectCompletionHistoryResponseModel:
        if request.query_params:
            raise AssessmentError(
                AssessmentErrorCode.INVALID_SUBMISSION,
                "Project submission history does not accept query input.",
                reference="query",
            )
        history = _assessment_service(
            services.assessment
        ).read_project_completion_history(
            ReadProjectCompletionHistoryRequest(
                learner_id=context.learner_id,
                project_id=project_id,
            )
        )
        return project_completion_history_response(history)

    @app.get(
        "/api/v1/projects/{project_id}/submissions/{submission_id}",
        response_model=ProjectCompletionEvidenceResponseModel,
        response_model_exclude_none=True,
        operation_id="getProjectSubmissionEvidence",
        responses=_ERROR_RESPONSES,
        tags=["projects", "assessment"],
    )
    def get_project_submission_evidence(
        request: Request,
        project_id: str = Path(min_length=1, max_length=128),
        submission_id: str = Path(min_length=1, max_length=128),
        context: LearnerContext = Depends(project_read_context),
    ) -> ProjectCompletionEvidenceResponseModel:
        if request.query_params:
            raise AssessmentError(
                AssessmentErrorCode.INVALID_SUBMISSION,
                "Project submission evidence does not accept query input.",
                reference="query",
            )
        evidence = _assessment_service(
            services.assessment
        ).read_project_completion_evidence(
            ReadProjectCompletionEvidenceRequest(
                learner_id=context.learner_id,
                project_id=project_id,
                submission_id=submission_id,
            )
        )
        return project_completion_evidence_response(evidence)

    @app.get(
        "/api/v1/projects/{project_id}/completion",
        response_model=ProjectActivityCompletionResponseModel,
        response_model_exclude_none=True,
        operation_id="getProjectCompletion",
        responses=_ERROR_RESPONSES,
        tags=["projects", "learner-model"],
    )
    def get_project_completion(
        request: Request,
        project_id: str = Path(min_length=1, max_length=128),
        context: LearnerContext = Depends(project_read_context),
    ) -> ProjectActivityCompletionResponseModel:
        if request.query_params:
            raise AssessmentError(
                AssessmentErrorCode.INVALID_SUBMISSION,
                "Project completion does not accept query input.",
                reference="query",
            )
        project_operations().open_project(
            OpenProjectRequest(
                learner_id=context.learner_id,
                project_id=project_id,
            )
        )
        _audit_service(services.audit).reconcile_project_completion(
            ReconcileProjectCompletionAuditRequest(
                learner_id=context.learner_id,
                project_id=project_id,
            )
        )
        view = _learner_model_service(
            services.learner_model
        ).open_project_completion(
            OpenProjectCompletionRequest(
                learner_id=context.learner_id,
                project_id=project_id,
            )
        )
        return project_activity_completion_response(view)

    @app.get(
        "/api/v1/guidance/platform-help",
        response_model=PlatformHelpSearchPageResponseModel,
        response_model_exclude_none=True,
        operation_id="searchPlatformHelp",
        responses=_ERROR_RESPONSES,
        tags=["guidance"],
    )
    async def search_platform_help(
        request: Request,
        query: str = Query(default="", max_length=200),
        topic_kind: PlatformHelpTopicKind | None = Query(default=None),
        page_size: int = Query(default=20, ge=1, le=50),
        cursor: str | None = Query(default=None, min_length=1, max_length=4096),
        _context: LearnerContext = Depends(guidance_context),
    ) -> JSONResponse:
        if not set(request.query_params).issubset(
            {"query", "topic_kind", "page_size", "cursor"}
        ) or await request.body():
            raise RequestValidationError([])
        page = guidance_operations().search_platform_help(
            PlatformHelpSearchRequest(
                query=query,
                topic_kind=topic_kind,
                page_size=page_size,
                cursor=cursor,
            )
        )
        response = platform_help_search_page_response(page)
        payload = response.model_dump(mode="json", exclude_none=True)
        payload["next_cursor"] = response.next_cursor
        return JSONResponse(content=payload)

    @app.get(
        "/api/v1/guidance/platform-help/{topic_id}/versions/{topic_version}",
        response_model=PlatformHelpTopicResponseModel,
        response_model_exclude_none=True,
        operation_id="getPlatformHelpTopicVersion",
        responses=_ERROR_RESPONSES,
        tags=["guidance"],
    )
    async def get_platform_help_topic_version(
        request: Request,
        topic_id: str = Path(
            min_length=3,
            max_length=64,
            pattern=r"^[a-z0-9][a-z0-9._-]{2,63}$",
        ),
        topic_version: str = Path(
            pattern=(
                r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\."
                r"(0|[1-9][0-9]*)$"
            ),
        ),
        _context: LearnerContext = Depends(guidance_context),
    ) -> PlatformHelpTopicResponseModel:
        if request.query_params or await request.body():
            raise RequestValidationError([])
        topic = guidance_operations().open_platform_help_topic(
            OpenPlatformHelpTopicRequest(topic_id, topic_version)
        )
        return platform_help_topic_response(topic)

    @app.get(
        "/api/v1/guidance/contextual-help/{context_key}/versions/{context_version}",
        response_model=ContextualHelpResponseModel,
        operation_id="getContextualHelpVersion",
        responses=_ERROR_RESPONSES,
        tags=["guidance"],
    )
    async def get_contextual_help_version(
        request: Request,
        context_key: str = Path(
            min_length=3,
            max_length=64,
            pattern=r"^[a-z0-9][a-z0-9._-]{2,63}$",
        ),
        context_version: str = Path(
            pattern=(
                r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\."
                r"(0|[1-9][0-9]*)$"
            ),
        ),
        _context: LearnerContext = Depends(guidance_context),
    ) -> ContextualHelpResponseModel:
        if request.query_params or await request.body():
            raise RequestValidationError([])
        context = guidance_operations().open_contextual_help(
            OpenContextualHelpRequest(context_key, context_version)
        )
        return contextual_help_response(context)

    @app.get(
        "/api/v1/guidance/feature-guidance/{surface_key}/conditions/{condition_key}/versions/{mapping_version}",
        response_model=FeatureGuidanceResponseModel,
        operation_id="getFeatureGuidanceVersion",
        responses=_ERROR_RESPONSES,
        tags=["guidance"],
    )
    async def get_feature_guidance_version(
        request: Request,
        surface_key: str = Path(
            min_length=3,
            max_length=64,
            pattern=r"^[a-z0-9][a-z0-9._-]{2,63}$",
        ),
        condition_key: str = Path(
            min_length=3,
            max_length=64,
            pattern=r"^[a-z0-9][a-z0-9._-]{2,63}$",
        ),
        mapping_version: str = Path(
            pattern=(
                r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\."
                r"(0|[1-9][0-9]*)$"
            ),
        ),
        _context: LearnerContext = Depends(guidance_context),
    ) -> FeatureGuidanceResponseModel:
        if request.query_params or await request.body():
            raise RequestValidationError([])
        resolution = guidance_operations().resolve_feature_guidance(
            ResolveFeatureGuidanceRequest(
                surface_key=surface_key,
                condition_key=condition_key,
                mapping_version=mapping_version,
            )
        )
        return feature_guidance_response(resolution)

    @app.get(
        "/api/v1/curriculum/graphs/{curriculum_id}/versions/{curriculum_version}",
        response_model=CurriculumGraphResponseModel,
        operation_id="getCurriculumGraphVersion",
        responses=_ERROR_RESPONSES,
        tags=["curriculum"],
    )
    def get_curriculum_graph_version(
        curriculum_id: str = Path(
            min_length=3,
            max_length=64,
            pattern=r"^[a-z0-9][a-z0-9._-]{2,63}$",
        ),
        curriculum_version: str = Path(
            pattern=(
                r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\."
                r"(0|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?$"
            ),
        ),
        _context: LearnerContext = Depends(curriculum_graph_context),
    ) -> CurriculumGraphResponseModel:
        graph = services.curriculum.open_curriculum_graph(
            OpenCurriculumGraphRequest(
                curriculum_id=curriculum_id,
                curriculum_version=curriculum_version,
            )
        )
        return curriculum_graph_response(graph)

    @app.get(
        "/api/v1/adaptation/curricula/{curriculum_id}/versions/{curriculum_version}/navigation-state",
        response_model=NavigationStateResponseModel,
        operation_id="getCurriculumNavigationState",
        responses=_ERROR_RESPONSES,
        tags=["adaptation"],
    )
    def get_curriculum_navigation_state(
        request: Request,
        curriculum_id: str = Path(
            min_length=3,
            max_length=64,
            pattern=r"^[a-z0-9][a-z0-9._-]{2,63}$",
        ),
        curriculum_version: str = Path(
            pattern=(
                r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\."
                r"(0|[1-9][0-9]*)$"
            ),
        ),
        context: LearnerContext = Depends(adaptation_context),
    ) -> NavigationStateResponseModel:
        if request.query_params:
            raise RequestValidationError([])
        adaptation = _adaptation_service(services.adaptation)
        projection = adaptation.open_navigation_state(
            OpenNavigationStateRequest(
                learner_id=context.learner_id,
                curriculum_id=curriculum_id,
                curriculum_version=curriculum_version,
            )
        )
        return navigation_state_response(projection)

    @app.get(
        "/api/v1/adaptation/curricula/{curriculum_id}/versions/{curriculum_version}/activities/{activity_id}/launch",
        response_model=ActivityLaunchResponseModel,
        operation_id="getCurriculumActivityLaunch",
        responses=_ERROR_RESPONSES,
        tags=["adaptation"],
    )
    async def get_curriculum_activity_launch(
        request: Request,
        curriculum_id: str = Path(
            min_length=3,
            max_length=64,
            pattern=r"^[a-z0-9][a-z0-9._-]{2,63}$",
        ),
        curriculum_version: str = Path(
            pattern=(
                r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\."
                r"(0|[1-9][0-9]*)$"
            ),
        ),
        activity_id: str = Path(
            min_length=1,
            max_length=128,
            pattern=r"^[a-z0-9][a-z0-9._:-]{0,127}$",
        ),
        context: LearnerContext = Depends(activity_launch_context),
    ) -> ActivityLaunchResponseModel:
        if request.query_params or await request.body():
            raise RequestValidationError([])
        adaptation = _adaptation_service(services.adaptation)
        resolution = adaptation.open_activity_launch(
            OpenActivityLaunchRequest(
                learner_id=context.learner_id,
                curriculum_id=curriculum_id,
                curriculum_version=curriculum_version,
                activity_id=activity_id,
            )
        )
        return activity_launch_response(resolution)

    @app.get(
        "/api/v1/curriculum/opportunities",
        response_model=LearningOpportunityBrowseResponseModel,
        operation_id="browseLearningOpportunities",
        responses=_ERROR_RESPONSES,
        tags=["curriculum"],
    )
    def browse_learning_opportunities(
        _context: LearnerContext = Depends(discovery_context),
    ) -> LearningOpportunityBrowseResponseModel:
        browse = services.curriculum.browse_learning_opportunities(
            BrowseLearningOpportunitiesRequest()
        )
        return learning_opportunity_browse_response(browse)

    @app.get(
        "/api/v1/curriculum/opportunities/query",
        response_model=LearningOpportunityQueryPageResponseModel,
        operation_id="queryLearningOpportunities",
        responses=_ERROR_RESPONSES,
        tags=["curriculum"],
    )
    def query_learning_opportunities(
        query: str | None = Query(
            default=None,
            min_length=1,
            max_length=100,
        ),
        prerequisite_query: str | None = Query(
            default=None,
            min_length=1,
            max_length=100,
        ),
        topic: tuple[DiscoveryTopic, ...] = Query(
            default=(),
            max_length=8,
        ),
        level: tuple[OpportunityLevel, ...] = Query(
            default=(),
            max_length=8,
        ),
        kind: tuple[OpportunityKind, ...] = Query(
            default=(),
            max_length=8,
        ),
        availability: tuple[OpportunityAvailability, ...] = Query(
            default=(),
            max_length=8,
        ),
        minimum_minutes: int | None = Query(default=None, ge=1, le=1440),
        maximum_minutes: int | None = Query(default=None, ge=1, le=1440),
        sort: OpportunityQuerySort = Query(
            default=OpportunityQuerySort.CATALOG
        ),
        page_size: int = Query(default=20, ge=1, le=50),
        cursor: str | None = Query(
            default=None,
            min_length=1,
            max_length=1024,
            pattern=r"^[A-Za-z0-9_-]+\.[a-f0-9]{64}$",
        ),
        _context: LearnerContext = Depends(discovery_context),
    ) -> LearningOpportunityQueryPageResponseModel:
        page = services.curriculum.query_learning_opportunities(
            QueryLearningOpportunitiesRequest(
                query=query,
                prerequisite_query=prerequisite_query,
                topics=topic,
                levels=level,
                kinds=kind,
                availabilities=availability,
                minimum_minutes=minimum_minutes,
                maximum_minutes=maximum_minutes,
                sort=sort,
                page_size=page_size,
                cursor=cursor,
            )
        )
        return learning_opportunity_query_page_response(page)

    @app.get(
        "/api/v1/curriculum/placements/{placement_id}/lesson",
        response_model=LessonReadingResponseModel,
        operation_id="getPlacedLesson",
        responses=_ERROR_RESPONSES,
        tags=["curriculum"],
    )
    def get_placed_lesson(
        placement_id: str = Path(
            min_length=3,
            max_length=64,
            pattern=r"^[a-z0-9][a-z0-9._-]{2,63}$",
        ),
        _context: LearnerContext = Depends(lesson_context),
    ) -> LessonReadingResponseModel:
        reading = services.curriculum.open_placed_lesson(
            OpenPlacedLessonRequest(placement_id)
        )
        return lesson_response(reading)

    @app.get(
        "/api/v1/curriculum/placements/{placement_id}/knowledge-check",
        response_model=KnowledgeCheckPresentationResponseModel,
        operation_id="getPlacedKnowledgeCheck",
        responses=_ERROR_RESPONSES,
        tags=["assessment"],
    )
    def get_placed_knowledge_check(
        placement_id: str = Path(
            min_length=3,
            max_length=64,
            pattern=r"^[a-z0-9][a-z0-9._-]{2,63}$",
        ),
        _context: LearnerContext = Depends(lesson_context),
    ) -> KnowledgeCheckPresentationResponseModel:
        assessment = _assessment_service(services.assessment)
        presentation = assessment.open_placed_knowledge_check(
            OpenPlacedKnowledgeCheckRequest(placement_id)
        )
        return knowledge_check_presentation_response(presentation)

    @app.get(
        "/api/v1/curriculum/placements/{placement_id}/practice",
        response_model=PracticePresentationResponseModel,
        operation_id="getPlacedPractice",
        responses=_ERROR_RESPONSES,
        tags=["assessment"],
    )
    def get_placed_practice(
        request: Request,
        placement_id: str = Path(
            min_length=3,
            max_length=64,
            pattern=r"^[a-z0-9][a-z0-9._-]{2,63}$",
        ),
        _context: LearnerContext = Depends(lesson_context),
    ) -> PracticePresentationResponseModel:
        if request.query_params:
            raise AssessmentError(
                AssessmentErrorCode.INVALID_SUBMISSION,
                "Practice opening does not accept query input.",
                reference="query",
            )
        assessment = _assessment_service(services.assessment)
        presentation = assessment.open_placed_practice(
            OpenPlacedPracticeRequest(placement_id)
        )
        return practice_presentation_response(presentation)

    @app.post(
        "/api/v1/curriculum/placements/{placement_id}/practice/submissions",
        response_model=PracticeSubmissionResultResponseModel,
        operation_id="submitPlacedPractice",
        responses=_ERROR_RESPONSES,
        tags=["assessment"],
    )
    def submit_placed_practice(
        request: Request,
        request_model: PracticeSubmissionRequestModel,
        placement_id: str = Path(
            min_length=3,
            max_length=64,
            pattern=r"^[a-z0-9][a-z0-9._-]{2,63}$",
        ),
        context: LearnerContext = Depends(lesson_context),
    ) -> PracticeSubmissionResultResponseModel:
        if request.query_params:
            raise AssessmentError(
                AssessmentErrorCode.INVALID_SUBMISSION,
                "Practice submission does not accept query input.",
                reference="query",
            )
        if request_model.placement_id != placement_id:
            raise AssessmentError(
                AssessmentErrorCode.STALE_REFERENCE,
                "Practice version references do not match.",
                reference="placement_id",
            )
        document = json.dumps(
            request_model.model_dump(mode="json"),
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        assessment = _assessment_service(services.assessment)
        result = assessment.submit_placed_practice(
            SubmitPlacedPracticeRequest(
                learner_id=context.learner_id,
                placement_id=placement_id,
                submission=document,
            )
        )
        return practice_submission_result_response(result)

    @app.get(
        "/api/v1/curriculum/placements/{placement_id}/practice/progress",
        response_model=PracticeProgressResponseModel,
        operation_id="getPlacedPracticeProgress",
        responses=_ERROR_RESPONSES,
        tags=["assessment", "learner-model"],
    )
    def get_placed_practice_progress(
        request: Request,
        placement_id: str = Path(
            min_length=3,
            max_length=64,
            pattern=r"^[a-z0-9][a-z0-9._-]{2,63}$",
        ),
        context: LearnerContext = Depends(lesson_context),
    ) -> PracticeProgressResponseModel:
        if request.query_params:
            raise AssessmentError(
                AssessmentErrorCode.INVALID_SUBMISSION,
                "Practice progress does not accept query input.",
                reference="query",
            )
        assessment = _assessment_service(services.assessment)
        learner_model = _learner_model_service(services.learner_model)
        presentation = assessment.open_placed_practice(
            OpenPlacedPracticeRequest(placement_id)
        )
        progress_request = ReadPlacedPracticeProgressRequest(
            learner_id=context.learner_id,
            placement_id=placement_id,
        )
        draft = assessment.read_placed_practice_draft(progress_request)
        retry_state = assessment.read_placed_practice_retry_state(
            progress_request
        )
        history = learner_model.open_practice_history(
            OpenPracticeHistoryRequest(
                learner_id=context.learner_id,
                placement_id=placement_id,
            )
        )
        resources = _latest_practice_review_resources(
            presentation,
            history,
        )
        review_targets = (
            services.curriculum.resolve_practice_review_targets(
                ResolvePracticeReviewTargetsRequest(
                    practice_placement_id=placement_id,
                    resources=resources,
                )
            )
            if resources
            else ()
        )
        return practice_progress_response(
            placement_id=placement_id,
            draft=draft,
            retry_state=retry_state,
            history=history,
            review_targets=review_targets,
        )

    @app.put(
        "/api/v1/curriculum/placements/{placement_id}/practice/draft",
        response_model=PracticeDraftResponseModel,
        operation_id="savePlacedPracticeDraft",
        responses=_ERROR_RESPONSES,
        tags=["assessment"],
    )
    def save_placed_practice_draft(
        request: Request,
        request_model: PracticeDraftSaveRequestModel,
        placement_id: str = Path(
            min_length=3,
            max_length=64,
            pattern=r"^[a-z0-9][a-z0-9._-]{2,63}$",
        ),
        context: LearnerContext = Depends(lesson_context),
    ) -> PracticeDraftResponseModel:
        if request.query_params:
            raise AssessmentError(
                AssessmentErrorCode.INVALID_SUBMISSION,
                "Saving practice progress does not accept query input.",
                reference="query",
            )
        if request_model.placement_id != placement_id:
            raise AssessmentError(
                AssessmentErrorCode.STALE_REFERENCE,
                "Practice version references do not match.",
                reference="placement_id",
            )
        document = json.dumps(
            request_model.model_dump(mode="json"),
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        draft = _assessment_service(
            services.assessment
        ).save_placed_practice_draft(
            SavePlacedPracticeDraftRequest(
                learner_id=context.learner_id,
                placement_id=placement_id,
                draft=document,
            )
        )
        return practice_draft_response(draft)

    @app.post(
        "/api/v1/curriculum/placements/{placement_id}/knowledge-check/submissions",
        response_model=KnowledgeCheckResultResponseModel,
        operation_id="submitPlacedKnowledgeCheck",
        responses=_ERROR_RESPONSES,
        tags=["assessment"],
    )
    def submit_placed_knowledge_check(
        request_model: KnowledgeCheckSubmissionRequestModel,
        placement_id: str = Path(
            min_length=3,
            max_length=64,
            pattern=r"^[a-z0-9][a-z0-9._-]{2,63}$",
        ),
        context: LearnerContext = Depends(lesson_context),
    ) -> KnowledgeCheckResultResponseModel:
        if request_model.placement_id != placement_id:
            raise AssessmentError(
                AssessmentErrorCode.STALE_REFERENCE,
                "Knowledge-check version references do not match.",
                reference="placement_id",
            )
        assessment = _assessment_service(services.assessment)
        result = assessment.submit_placed_knowledge_check(
            SubmitPlacedKnowledgeCheckRequest(
                learner_id=context.learner_id,
                submission_id=str(request_model.submission_id),
                placement_id=placement_id,
                package_id=request_model.package_id,
                package_version=request_model.package_version,
                package_digest=request_model.package_digest,
                assessment_id=request_model.assessment_id,
                assessment_version=request_model.assessment_version,
                definition_digest=request_model.definition_digest,
                item_id=request_model.item_id,
                item_version=request_model.item_version,
                scoring_policy_id=request_model.scoring_policy_id,
                scoring_policy_version=(
                    request_model.scoring_policy_version
                ),
                selected_option_id=request_model.selected_option_id,
            )
        )
        return knowledge_check_result_response(result)

    @app.get(
        "/api/v1/curriculum/placements/{placement_id}/completion",
        response_model=LessonCompletionResponseModel,
        operation_id="getLessonCompletion",
        responses=_ERROR_RESPONSES,
        tags=["learner-model"],
    )
    def get_lesson_completion(
        placement_id: str = Path(
            min_length=3,
            max_length=64,
            pattern=r"^[a-z0-9][a-z0-9._-]{2,63}$",
        ),
        context: LearnerContext = Depends(lesson_context),
    ) -> LessonCompletionResponseModel:
        audit = _audit_service(services.audit)
        learner_model = _learner_model_service(services.learner_model)
        audit.reconcile_lesson_completion(
            ReconcileLessonCompletionAuditRequest(
                learner_id=context.learner_id,
                placement_id=placement_id,
            )
        )
        view = learner_model.open_lesson_completion(
            OpenLessonCompletionRequest(
                learner_id=context.learner_id,
                placement_id=placement_id,
            )
        )
        return lesson_completion_response(view)

    @app.get(
        "/api/v1/learner-preferences",
        response_model=LearnerPreferenceProfileResponseModel,
        operation_id="getLearnerPreferences",
        responses=_ERROR_RESPONSES,
        tags=["learner-model"],
    )
    def get_learner_preferences(
        request: Request,
        context: LearnerContext = Depends(learner_preferences_read_context),
    ) -> LearnerPreferenceProfileResponseModel:
        if request.query_params:
            raise LearnerModelError(
                LearnerModelErrorCode.INVALID_REQUEST,
                "Learning preferences do not accept query input.",
                reference="query",
            )
        profile = _learner_model_service(
            services.learner_model
        ).open_preferences(
            OpenLearnerPreferencesRequest(learner_id=context.learner_id)
        )
        return learner_preference_profile_response(profile)

    @app.post(
        "/api/v1/learner-preferences/mutations",
        response_model=LearnerPreferenceProfileResponseModel,
        operation_id="mutateLearnerPreferences",
        responses=_ERROR_RESPONSES,
        tags=["learner-model"],
    )
    def mutate_learner_preferences(
        request: Request,
        request_model: LearnerPreferenceMutationRequestModel,
        context: LearnerContext = Depends(learner_preferences_write_context),
    ) -> LearnerPreferenceProfileResponseModel:
        if request.query_params:
            raise LearnerModelError(
                LearnerModelErrorCode.INVALID_REQUEST,
                "Learning preference changes do not accept query input.",
                reference="query",
            )
        profile = _learner_model_service(
            services.learner_model
        ).mutate_preferences(
            MutateLearnerPreferencesRequest(
                learner_id=context.learner_id,
                intent=learner_preference_mutation_intent(request_model),
            )
        )
        return learner_preference_profile_response(profile)

    @app.get(
        "/api/v1/learner-preferences/history",
        response_model=LearnerPreferenceHistoryResponseModel,
        operation_id="getLearnerPreferenceHistory",
        responses=_ERROR_RESPONSES,
        tags=["learner-model"],
    )
    def get_learner_preference_history(
        request: Request,
        context: LearnerContext = Depends(learner_preferences_read_context),
    ) -> LearnerPreferenceHistoryResponseModel:
        if request.query_params:
            raise LearnerModelError(
                LearnerModelErrorCode.INVALID_REQUEST,
                "Learning preference history does not accept query input.",
                reference="query",
            )
        history = _learner_model_service(
            services.learner_model
        ).read_preference_history(
            ReadLearnerPreferenceHistoryRequest(
                learner_id=context.learner_id
            )
        )
        return learner_preference_history_response(history)

    @app.get(
        "/api/v1/learner-preferences/export",
        response_model=LearnerPreferenceExportResponseModel,
        operation_id="exportLearnerPreferences",
        responses=_ERROR_RESPONSES,
        tags=["learner-model"],
    )
    def export_learner_preferences(
        request: Request,
        context: LearnerContext = Depends(learner_preferences_read_context),
    ) -> LearnerPreferenceExportResponseModel:
        if request.query_params:
            raise LearnerModelError(
                LearnerModelErrorCode.INVALID_REQUEST,
                "Learning preference export does not accept query input.",
                reference="query",
            )
        export = _learner_model_service(
            services.learner_model
        ).export_preferences(
            ExportLearnerPreferencesRequest(
                learner_id=context.learner_id
            )
        )
        return learner_preference_export_response(export)

    @app.get(
        "/api/v1/learner-presentation-preferences",
        response_model=PresentationPreferenceProfileResponseModel,
        operation_id="getLearnerPresentationPreferences",
        responses=_ERROR_RESPONSES,
        tags=["learner-model"],
    )
    def get_learner_presentation_preferences(
        request: Request,
        context: LearnerContext = Depends(presentation_preferences_read_context),
    ) -> PresentationPreferenceProfileResponseModel:
        if request.query_params:
            raise LearnerModelError(
                LearnerModelErrorCode.INVALID_REQUEST,
                "Display choices do not accept query input.",
                reference="query",
            )
        profile = _learner_model_service(
            services.learner_model
        ).open_presentation_preferences(
            OpenPresentationPreferencesRequest(learner_id=context.learner_id)
        )
        return presentation_preference_profile_response(profile)

    @app.post(
        "/api/v1/learner-presentation-preferences/mutations",
        response_model=PresentationPreferenceProfileResponseModel,
        operation_id="mutateLearnerPresentationPreferences",
        responses=_ERROR_RESPONSES,
        tags=["learner-model"],
    )
    def mutate_learner_presentation_preferences(
        request: Request,
        request_model: PresentationPreferenceMutationRequestModel,
        context: LearnerContext = Depends(presentation_preferences_write_context),
    ) -> PresentationPreferenceProfileResponseModel:
        if request.query_params:
            raise LearnerModelError(
                LearnerModelErrorCode.INVALID_REQUEST,
                "Display choice changes do not accept query input.",
                reference="query",
            )
        profile = _learner_model_service(
            services.learner_model
        ).mutate_presentation_preferences(
            MutatePresentationPreferencesRequest(
                learner_id=context.learner_id,
                intent=presentation_preference_mutation_intent(request_model),
            )
        )
        return presentation_preference_profile_response(profile)

    @app.get(
        "/api/v1/learner-presentation-preferences/history",
        response_model=PresentationPreferenceHistoryResponseModel,
        operation_id="getLearnerPresentationPreferenceHistory",
        responses=_ERROR_RESPONSES,
        tags=["learner-model"],
    )
    def get_learner_presentation_preference_history(
        request: Request,
        context: LearnerContext = Depends(presentation_preferences_read_context),
    ) -> PresentationPreferenceHistoryResponseModel:
        if request.query_params:
            raise LearnerModelError(
                LearnerModelErrorCode.INVALID_REQUEST,
                "Display choice history does not accept query input.",
                reference="query",
            )
        history = _learner_model_service(
            services.learner_model
        ).read_presentation_preference_history(
            ReadPresentationPreferenceHistoryRequest(
                learner_id=context.learner_id
            )
        )
        return presentation_preference_history_response(history)

    @app.get(
        "/api/v1/learner-presentation-preferences/export",
        response_model=PresentationPreferenceExportResponseModel,
        operation_id="exportLearnerPresentationPreferences",
        responses=_ERROR_RESPONSES,
        tags=["learner-model"],
    )
    def export_learner_presentation_preferences(
        request: Request,
        context: LearnerContext = Depends(presentation_preferences_read_context),
    ) -> PresentationPreferenceExportResponseModel:
        if request.query_params:
            raise LearnerModelError(
                LearnerModelErrorCode.INVALID_REQUEST,
                "Display choice export does not accept query input.",
                reference="query",
            )
        exported = _learner_model_service(
            services.learner_model
        ).export_presentation_preferences(
            ExportPresentationPreferencesRequest(
                learner_id=context.learner_id
            )
        )
        return presentation_preference_export_response(exported)

    @app.get(
        "/api/v1/learner-assistance-preferences",
        response_model=AssistancePreferenceProfileResponseModel,
        operation_id="getLearnerAssistancePreferences",
        responses=_ERROR_RESPONSES,
        tags=["learner-model"],
    )
    def get_learner_assistance_preferences(
        request: Request,
        context: LearnerContext = Depends(assistance_preferences_read_context),
    ) -> AssistancePreferenceProfileResponseModel:
        if request.query_params:
            raise LearnerModelError(
                LearnerModelErrorCode.INVALID_REQUEST,
                "The AI-help choice does not accept query input.",
                reference="query",
            )
        profile = _learner_model_service(
            services.learner_model
        ).open_assistance_preferences(
            OpenAssistancePreferencesRequest(learner_id=context.learner_id)
        )
        return assistance_preference_profile_response(profile)

    @app.post(
        "/api/v1/learner-assistance-preferences/mutations",
        response_model=AssistancePreferenceProfileResponseModel,
        operation_id="mutateLearnerAssistancePreferences",
        responses=_ERROR_RESPONSES,
        tags=["learner-model"],
    )
    def mutate_learner_assistance_preferences(
        request: Request,
        request_model: AssistancePreferenceMutationRequestModel,
        context: LearnerContext = Depends(assistance_preferences_write_context),
    ) -> AssistancePreferenceProfileResponseModel:
        if request.query_params:
            raise LearnerModelError(
                LearnerModelErrorCode.INVALID_REQUEST,
                "AI-help choice changes do not accept query input.",
                reference="query",
            )
        profile = _learner_model_service(
            services.learner_model
        ).mutate_assistance_preferences(
            MutateAssistancePreferencesRequest(
                learner_id=context.learner_id,
                intent=assistance_preference_mutation_intent(request_model),
            )
        )
        return assistance_preference_profile_response(profile)

    @app.get(
        "/api/v1/learner-assistance-preferences/history",
        response_model=AssistancePreferenceHistoryResponseModel,
        operation_id="getLearnerAssistancePreferenceHistory",
        responses=_ERROR_RESPONSES,
        tags=["learner-model"],
    )
    def get_learner_assistance_preference_history(
        request: Request,
        context: LearnerContext = Depends(assistance_preferences_read_context),
    ) -> AssistancePreferenceHistoryResponseModel:
        if request.query_params:
            raise LearnerModelError(
                LearnerModelErrorCode.INVALID_REQUEST,
                "AI-help choice history does not accept query input.",
                reference="query",
            )
        history = _learner_model_service(
            services.learner_model
        ).read_assistance_preference_history(
            ReadAssistancePreferenceHistoryRequest(
                learner_id=context.learner_id
            )
        )
        return assistance_preference_history_response(history)

    @app.get(
        "/api/v1/learner-assistance-preferences/export",
        response_model=AssistancePreferenceExportResponseModel,
        operation_id="exportLearnerAssistancePreferences",
        responses=_ERROR_RESPONSES,
        tags=["learner-model"],
    )
    def export_learner_assistance_preferences(
        request: Request,
        context: LearnerContext = Depends(assistance_preferences_read_context),
    ) -> AssistancePreferenceExportResponseModel:
        if request.query_params:
            raise LearnerModelError(
                LearnerModelErrorCode.INVALID_REQUEST,
                "The AI-help choice export does not accept query input.",
                reference="query",
            )
        exported = _learner_model_service(
            services.learner_model
        ).export_assistance_preferences(
            ExportAssistancePreferencesRequest(
                learner_id=context.learner_id
            )
        )
        return assistance_preference_export_response(exported)

    def reviewed_openapi() -> dict[str, object]:
        if app.openapi_schema is None:
            schema = get_openapi(
                title=app.title,
                version=app.version,
                openapi_version=app.openapi_version,
                routes=app.routes,
            )
            schema["x-contract-version"] = "1.0"
            schema["x-generated-by"] = (
                "python -m financial_ai_academy.hosts.api.generate_openapi"
            )
            query_operation = schema["paths"][
                "/api/v1/curriculum/opportunities/query"
            ]["get"]
            query_operation["responses"].pop("422", None)
            graph_operation = schema["paths"][
                "/api/v1/curriculum/graphs/{curriculum_id}/versions/{curriculum_version}"
            ]["get"]
            graph_operation["responses"].pop("422", None)
            guidance_search_operation = schema["paths"][
                "/api/v1/guidance/platform-help"
            ]["get"]
            guidance_search_operation["responses"].pop("422", None)
            guidance_topic_operation = schema["paths"][
                "/api/v1/guidance/platform-help/{topic_id}/versions/{topic_version}"
            ]["get"]
            guidance_topic_operation["responses"].pop("422", None)
            contextual_help_operation = schema["paths"][
                "/api/v1/guidance/contextual-help/{context_key}/versions/{context_version}"
            ]["get"]
            contextual_help_operation["responses"].pop("422", None)
            feature_guidance_operation = schema["paths"][
                "/api/v1/guidance/feature-guidance/{surface_key}/conditions/{condition_key}/versions/{mapping_version}"
            ]["get"]
            feature_guidance_operation["responses"].pop("422", None)
            navigation_operation = schema["paths"][
                "/api/v1/adaptation/curricula/{curriculum_id}/versions/{curriculum_version}/navigation-state"
            ]["get"]
            navigation_operation["responses"].pop("422", None)
            launch_operation = schema["paths"][
                "/api/v1/adaptation/curricula/{curriculum_id}/versions/{curriculum_version}/activities/{activity_id}/launch"
            ]["get"]
            launch_operation["responses"].pop("422", None)
            practice_submission_operation = schema["paths"][
                "/api/v1/curriculum/placements/{placement_id}/practice/submissions"
            ]["post"]
            practice_submission_operation["responses"].pop("422", None)
            practice_progress_operation = schema["paths"][
                "/api/v1/curriculum/placements/{placement_id}/practice/progress"
            ]["get"]
            practice_progress_operation["responses"].pop("422", None)
            practice_draft_operation = schema["paths"][
                "/api/v1/curriculum/placements/{placement_id}/practice/draft"
            ]["put"]
            practice_draft_operation["responses"].pop("422", None)
            preference_mutation_operation = schema["paths"][
                "/api/v1/learner-preferences/mutations"
            ]["post"]
            preference_mutation_operation["responses"].pop("422", None)
            presentation_preference_mutation_operation = schema["paths"][
                "/api/v1/learner-presentation-preferences/mutations"
            ]["post"]
            presentation_preference_mutation_operation["responses"].pop(
                "422", None
            )
            assistance_preference_mutation_operation = schema["paths"][
                "/api/v1/learner-assistance-preferences/mutations"
            ]["post"]
            assistance_preference_mutation_operation["responses"].pop(
                "422", None
            )
            app.openapi_schema = schema
        return app.openapi_schema

    app.openapi = reviewed_openapi  # type: ignore[method-assign]
    return app


def _error_response(
    http_status: int,
    code: str,
    message: str,
    correlation_id: str,
) -> JSONResponse:
    envelope = ApiErrorEnvelope(
        code=code,
        message=message,
        correlation_id=correlation_id,
    )
    return JSONResponse(
        status_code=http_status,
        content=envelope.model_dump(mode="json"),
    )


def _assessment_service(
    assessment: AssessmentOperations | None,
) -> AssessmentOperations:
    if assessment is None:
        raise AssessmentError(
            AssessmentErrorCode.UNAVAILABLE,
            "The knowledge-check service is unavailable.",
        )
    return assessment


def _audit_service(audit: AuditOperations | None) -> AuditOperations:
    if audit is None:
        raise AuditError(
            AuditErrorCode.UNAVAILABLE,
            "Audit reconciliation is unavailable.",
        )
    return audit


def _learner_model_service(
    learner_model: LearnerModelOperations | None,
) -> LearnerModelOperations:
    if learner_model is None:
        raise LearnerModelError(
            LearnerModelErrorCode.UNAVAILABLE,
            "The completion view is unavailable.",
        )
    return learner_model


def _latest_practice_review_resources(
    presentation: PracticePresentation,
    history: PracticeHistoryView,
) -> tuple[PracticeReviewResource, ...]:
    if not history.attempts:
        return ()
    references = {
        reference.resource_id: reference
        for reference in presentation.review_references
    }
    selected: list[PracticeReviewResource] = []
    seen: set[str] = set()
    for item in history.attempts[-1].item_summaries:
        if item.correct:
            continue
        for resource_id in item.review_reference_ids:
            if resource_id in seen:
                continue
            reference = references.get(resource_id)
            if reference is None:
                raise AssessmentError(
                    AssessmentErrorCode.UNAVAILABLE,
                    "Practice review information is unavailable.",
                    reference=resource_id,
                )
            seen.add(resource_id)
            selected.append(
                PracticeReviewResource(
                    resource_id=reference.resource_id,
                    resource_version=reference.resource_version,
                    resource_digest=reference.resource_digest,
                    resource_title=reference.title,
                )
            )
    return tuple(selected)


def _adaptation_service(
    adaptation: AdaptationOperations | None,
) -> AdaptationOperations:
    if adaptation is None:
        raise NavigationStateOperationError(
            NavigationStateOperationErrorCode.UNAVAILABLE,
            "Navigation state is currently unavailable.",
        )
    return adaptation

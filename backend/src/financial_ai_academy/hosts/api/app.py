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
    PracticePresentation,
    ReadPlacedPracticeProgressRequest,
    SavePlacedPracticeDraftRequest,
    SubmitPlacedKnowledgeCheckRequest,
    SubmitPlacedPracticeRequest,
)
from financial_ai_academy.modules.audit.public import (
    AuditError,
    AuditErrorCode,
    AuditOperations,
    ReconcileLessonCompletionAuditRequest,
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
from financial_ai_academy.modules.learner_model.public import (
    LearnerModelError,
    LearnerModelErrorCode,
    LearnerModelOperations,
    OpenLessonCompletionRequest,
    OpenPracticeHistoryRequest,
    PracticeHistoryView,
)
from financial_ai_academy.platform.security.single_profile_policy import (
    RequestPolicyViolation,
    SingleProfileRequestPolicy,
)

from .models import (
    ActivityLaunchResponseModel,
    ApiErrorEnvelope,
    CurriculumGraphResponseModel,
    DiscoveryTopic,
    HealthResponseModel,
    KnowledgeCheckPresentationResponseModel,
    KnowledgeCheckResultResponseModel,
    KnowledgeCheckSubmissionRequestModel,
    LearningOpportunityBrowseResponseModel,
    LearningOpportunityQueryPageResponseModel,
    LessonCompletionResponseModel,
    LessonReadingResponseModel,
    NavigationStateResponseModel,
    PracticePresentationResponseModel,
    PracticeDraftResponseModel,
    PracticeDraftSaveRequestModel,
    PracticeProgressResponseModel,
    PracticeSubmissionRequestModel,
    PracticeSubmissionResultResponseModel,
    SessionBootstrapRequestModel,
    SessionBootstrapResponseModel,
    activity_launch_response,
    curriculum_graph_response,
    knowledge_check_presentation_response,
    knowledge_check_result_response,
    learning_opportunity_browse_response,
    learning_opportunity_query_page_response,
    lesson_completion_response,
    lesson_response,
    navigation_state_response,
    practice_presentation_response,
    practice_draft_response,
    practice_progress_response,
    practice_submission_result_response,
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


_ERROR_RESPONSES = {
    400: {"model": ApiErrorEnvelope, "description": "Invalid request"},
    401: {"model": ApiErrorEnvelope, "description": "Unauthorized"},
    403: {"model": ApiErrorEnvelope, "description": "Forbidden"},
    404: {"model": ApiErrorEnvelope, "description": "Not found"},
    409: {"model": ApiErrorEnvelope, "description": "Conflict"},
    503: {"model": ApiErrorEnvelope, "description": "Unavailable"},
}


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
            LearnerModelErrorCode.INVALID_CONTEXT: (
                status.HTTP_401_UNAUTHORIZED
            ),
            LearnerModelErrorCode.INCONSISTENT_EVIDENCE: (
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

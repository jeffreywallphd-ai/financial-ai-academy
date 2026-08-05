"""Thin FastAPI transport over Identity and Curriculum public operations."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from uuid import uuid4

from fastapi import (
    Depends,
    FastAPI,
    Path,
    Request,
    Response,
    Security,
    status,
)
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyCookie

from financial_ai_academy.modules.content.public import (
    LessonErrorCode,
    LessonReadError,
)
from financial_ai_academy.modules.curriculum.public import (
    CurriculumOperations,
    OpenPlacedLessonRequest,
)
from financial_ai_academy.modules.identity.public import (
    IdentityError,
    IdentityErrorCode,
    IdentityOperations,
    LearnerContext,
    SingleProfileBootstrapRequest,
)
from financial_ai_academy.platform.security.single_profile_policy import (
    RequestPolicyViolation,
    SingleProfileRequestPolicy,
)

from .models import (
    ApiErrorEnvelope,
    HealthResponseModel,
    LessonReadingResponseModel,
    SessionBootstrapRequestModel,
    SessionBootstrapResponseModel,
    lesson_response,
)


@dataclass(frozen=True, slots=True)
class ApiServices:
    identity: IdentityOperations
    curriculum: CurriculumOperations
    request_policy: SingleProfileRequestPolicy


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

    def learner_context(
        cookie_value: str | None = Security(session_cookie),
    ) -> LearnerContext:
        context = services.identity.resolve_session(cookie_value)
        if "curriculum.lesson.read" not in context.permissions:
            raise IdentityError(
                IdentityErrorCode.FORBIDDEN,
                "The learner session cannot read lessons.",
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
        _context: LearnerContext = Depends(learner_context),
    ) -> LessonReadingResponseModel:
        reading = services.curriculum.open_placed_lesson(
            OpenPlacedLessonRequest(placement_id)
        )
        return lesson_response(reading)

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

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
import json
from pathlib import Path

from fastapi.testclient import TestClient

from financial_ai_academy.hosts.api.app import ApiServices, create_app
from financial_ai_academy.hosts.api.generate_openapi import generate_bytes
from financial_ai_academy.modules.assessment.adapters.practice_contract import (
    ContractPracticeDefinitionAdapter,
)
from financial_ai_academy.modules.assessment.adapters.practice_progress_contract import (
    ContractPracticeProgressAdapter,
)
from financial_ai_academy.modules.assessment.domain.practice import (
    PracticeDraft,
    PracticePresentation,
    PracticePresentationContext,
    PracticeRetryState,
)
from financial_ai_academy.modules.assessment.public import (
    AssessmentError,
    OpenPlacedPracticeRequest,
    ReadPlacedPracticeProgressRequest,
    SavePlacedPracticeDraftRequest,
)
from financial_ai_academy.modules.curriculum.public import (
    PracticeReviewDestination,
    PracticeReviewState,
    PracticeReviewTarget,
    PracticeReviewUnavailableReason,
    ResolvePracticeReviewTargetsRequest,
)
from financial_ai_academy.modules.identity.public import (
    IdentityError,
    IdentityErrorCode,
    LearnerContext,
)
from financial_ai_academy.modules.learner_model.public import (
    OpenPracticeHistoryRequest,
    PracticeHistoryAttempt,
    PracticeHistoryItemSummary,
    PracticeHistoryView,
)
from financial_ai_academy.platform.security.single_profile_policy import (
    SingleProfileRequestPolicy,
    SingleProfileSecuritySettings,
)


REPOSITORY = Path(__file__).resolve().parents[4]
SCHEMAS = REPOSITORY / "contracts/learning/assessment/practice/v1"
DEFINITION = (
    REPOSITORY
    / "contracts/compatibility/assessment-practice/v1/approved/definition.json"
)
DRAFT_SAVE = (
    REPOSITORY
    / "contracts/compatibility/assessment-practice/v1/approved/draft-save.json"
)
OPENAPI_PATH = REPOSITORY / "contracts/api/openapi.json"
ORIGIN = "http://127.0.0.1:8000"
COOKIE = "a" * 43
LEARNER_ID = "11111111-1111-4111-8111-111111111111"
PLACEMENT_ID = "risk-return-practice-placement"
DEFINITION_DIGEST = (
    "82cdc82c402aacdb0070fb19671d896ae22a4c16d338ccbf27f02a51a396d527"
)


class Identity:
    def __init__(
        self, permissions: tuple[str, ...] = ("curriculum.lesson.read",)
    ) -> None:
        self.permissions = permissions

    def resolve_session(self, cookie_value: str | None) -> LearnerContext:
        if cookie_value != COOKIE:
            raise IdentityError(
                IdentityErrorCode.UNAUTHORIZED,
                "A valid learner session is required.",
            )
        return LearnerContext(
            actor_id="33333333-3333-4333-8333-333333333333",
            learner_id=LEARNER_ID,
            session_id="44444444-4444-4444-8444-444444444444",
            authenticated_at=datetime(2026, 10, 15, tzinfo=timezone.utc),
            expires_at=datetime(2026, 10, 17, tzinfo=timezone.utc),
            authentication_method="single_profile",
            permissions=self.permissions,
        )

    def bootstrap_single_profile(self, request: object) -> object:
        raise NotImplementedError

    def revoke_session(self, cookie_value: str | None) -> None:
        return None

    def health(self) -> bool:
        return True


def presentation_and_draft() -> tuple[PracticePresentation, PracticeDraft]:
    practice = ContractPracticeDefinitionAdapter(SCHEMAS)
    definition = practice.parse(DEFINITION.read_bytes())
    context = PracticePresentationContext(
        placement_id=PLACEMENT_ID,
        package_id="intro-risk-return",
        package_version="2.0.0",
        package_digest="a" * 64,
    )
    presentation = practice.project(definition, context)
    parsed = ContractPracticeProgressAdapter(SCHEMAS).parse_draft_save(
        DRAFT_SAVE.read_bytes(), definition, context
    )
    draft = PracticeDraft(
        scope=parsed.scope,
        responses=parsed.responses,
        revision=1,
        saved_at=datetime(2026, 10, 16, 15, 1, tzinfo=timezone.utc),
        response_fingerprint=parsed.response_fingerprint,
    )
    return presentation, draft


def item(
    item_id: str,
    item_type: str,
    policy: str,
    *,
    correct: bool,
    references: tuple[str, ...] = (),
) -> PracticeHistoryItemSummary:
    return PracticeHistoryItemSummary(
        item_id=item_id,
        item_version="1.0.0",
        item_type=item_type,
        scoring_policy_id=policy,
        scoring_policy_version="1.0.0",
        score=1 if correct else 0,
        max_score=1,
        correct=correct,
        review_reference_ids=references,
    )


def history(
    *,
    attempts: tuple[PracticeHistoryAttempt, ...] | None = None,
) -> PracticeHistoryView:
    if attempts is None:
        attempts = (
            PracticeHistoryAttempt(
                attempt_order=1,
                event_id="55555555-5555-4555-8555-555555555555",
                attempt_id="33333333-3333-4333-8333-333333333333",
                evidence_id="44444444-4444-4444-8444-444444444444",
                submission_id="22222222-2222-4222-8222-222222222222",
                score=1,
                max_score=3,
                outcome="review_needed",
                item_summaries=(
                    item(
                        "risk-meaning",
                        "single_select",
                        "single-select-exact-match",
                        correct=False,
                        references=("risk-return-review",),
                    ),
                    item(
                        "diversification-actions",
                        "multiple_select",
                        "multiple-select-exact-set",
                        correct=False,
                        references=("risk-return-review",),
                    ),
                    item(
                        "simple-growth",
                        "numeric_entry",
                        "numeric-exact-or-inclusive-range",
                        correct=True,
                    ),
                ),
                completed_at=datetime(
                    2026, 10, 16, 15, 0, tzinfo=timezone.utc
                ),
            ),
        )
    return PracticeHistoryView(
        schema_version="1.0.0",
        placement_id=PLACEMENT_ID,
        package_id="intro-risk-return",
        package_version="2.0.0",
        package_digest="a" * 64,
        definition_digest=DEFINITION_DIGEST,
        practice_id="risk-return-practice",
        practice_version="1.0.0",
        attempt_policy_id="formative-retry",
        attempt_policy_version="1.0.0",
        source_digest="e" * 64,
        rebuilt_at=datetime(2026, 10, 16, 16, 0, tzinfo=timezone.utc),
        attempts=attempts,
    )


class Assessment:
    def __init__(self) -> None:
        self.presentation, self.draft = presentation_and_draft()
        self.retry = PracticeRetryState(
            scope=self.draft.scope,
            attempts_used=1,
            max_attempts=3,
            attempts_remaining=2,
            can_retry=True,
            state="available",
        )
        self.saved_request: SavePlacedPracticeDraftRequest | None = None
        self.save_error: AssessmentError | None = None

    def open_placed_practice(
        self, request: OpenPlacedPracticeRequest
    ) -> PracticePresentation:
        assert request.placement_id == PLACEMENT_ID
        return self.presentation

    def read_placed_practice_draft(
        self, request: ReadPlacedPracticeProgressRequest
    ) -> PracticeDraft | None:
        assert request.learner_id == LEARNER_ID
        assert request.placement_id == PLACEMENT_ID
        return self.draft

    def read_placed_practice_retry_state(
        self, request: ReadPlacedPracticeProgressRequest
    ) -> PracticeRetryState:
        assert request.learner_id == LEARNER_ID
        assert request.placement_id == PLACEMENT_ID
        return self.retry

    def save_placed_practice_draft(
        self, request: SavePlacedPracticeDraftRequest
    ) -> PracticeDraft:
        self.saved_request = request
        if self.save_error is not None:
            raise self.save_error
        return self.draft


class LearnerModel:
    def __init__(self, value: PracticeHistoryView) -> None:
        self.value = value
        self.request: OpenPracticeHistoryRequest | None = None

    def open_practice_history(
        self, request: OpenPracticeHistoryRequest
    ) -> PracticeHistoryView:
        self.request = request
        return self.value


class Curriculum:
    def __init__(self) -> None:
        self.request: ResolvePracticeReviewTargetsRequest | None = None
        self.calls = 0
        self.available = True

    def resolve_practice_review_targets(
        self, request: ResolvePracticeReviewTargetsRequest
    ) -> tuple[PracticeReviewTarget, ...]:
        self.calls += 1
        self.request = request
        resource = request.resources[0]
        if not self.available:
            return (
                PracticeReviewTarget(
                    schema_version="1.0.0",
                    practice_placement_id=request.practice_placement_id,
                    resource_id=resource.resource_id,
                    resource_version=resource.resource_version,
                    resource_digest=resource.resource_digest,
                    resource_title=resource.resource_title,
                    state=PracticeReviewState.UNAVAILABLE,
                    unavailable_reason=(
                        PracticeReviewUnavailableReason.MAPPING_NOT_FOUND
                    ),
                ),
            )
        return (
            PracticeReviewTarget(
                schema_version="1.0.0",
                practice_placement_id=request.practice_placement_id,
                resource_id=resource.resource_id,
                resource_version=resource.resource_version,
                resource_digest=resource.resource_digest,
                resource_title=resource.resource_title,
                state=PracticeReviewState.AVAILABLE,
                destination=PracticeReviewDestination(
                    placement_id="risk-return-reading-placement",
                    package_id="intro-risk-return",
                    package_version="2.0.0",
                    package_digest="a" * 64,
                    section_id="risk-return-review-section",
                ),
            ),
        )


def client(
    *,
    history_value: PracticeHistoryView | None = None,
    permissions: tuple[str, ...] = ("curriculum.lesson.read",),
) -> tuple[TestClient, Assessment, Curriculum, LearnerModel]:
    assessment = Assessment()
    curriculum = Curriculum()
    learner_model = LearnerModel(history_value or history())
    policy = SingleProfileRequestPolicy(
        SingleProfileSecuritySettings(
            identity_mode="single_profile",
            bind_host="127.0.0.1",
            public_origin=ORIGIN,
            allowed_hosts=("127.0.0.1:8000",),
            secure_cookie=False,
        )
    )
    result = TestClient(
        create_app(
            ApiServices(
                identity=Identity(permissions),  # type: ignore[arg-type]
                curriculum=curriculum,  # type: ignore[arg-type]
                request_policy=policy,
                assessment=assessment,  # type: ignore[arg-type]
                learner_model=learner_model,  # type: ignore[arg-type]
            )
        ),
        base_url=ORIGIN,
    )
    result.cookies.set("financial_ai_academy_session", COOKIE)
    return result, assessment, curriculum, learner_model


def test_headless_progress_read_composes_safe_exact_state() -> None:
    api, _assessment, curriculum, learner_model = client()

    response = api.get(
        f"/api/v1/curriculum/placements/{PLACEMENT_ID}/practice/progress"
    )

    assert response.status_code == 200
    body = response.json()
    assert body["placement_id"] == PLACEMENT_ID
    assert body["draft"]["revision"] == 1
    assert len(body["draft"]["responses"]) == 2
    assert body["retry_state"] == {
        "schema_version": "1.0.0",
        "placement_id": PLACEMENT_ID,
        "package_id": "intro-risk-return",
        "package_version": "2.0.0",
        "package_digest": "a" * 64,
        "definition_digest": DEFINITION_DIGEST,
        "practice_id": "risk-return-practice",
        "practice_version": "1.0.0",
        "attempt_policy_id": "formative-retry",
        "attempt_policy_version": "1.0.0",
        "attempts_used": 1,
        "max_attempts": 3,
        "attempts_remaining": 2,
        "can_retry": True,
        "state": "available",
    }
    assert len(body["history"]["attempts"]) == 1
    assert "rebuilt_at" not in body["history"]
    assert [target["resource_id"] for target in body["review_targets"]] == [
        "risk-return-review"
    ]
    assert curriculum.request is not None
    assert len(curriculum.request.resources) == 1
    assert curriculum.request.resources[0].resource_title == (
        "Review risk and return"
    )
    assert learner_model.request == OpenPracticeHistoryRequest(
        learner_id=LEARNER_ID,
        placement_id=PLACEMENT_ID,
    )
    for private_name in (
        "learner_id",
        "correct_answer",
        "evaluator",
        "request_fingerprint",
    ):
        assert private_name not in response.text


def test_empty_or_all_correct_latest_history_has_no_review_targets() -> None:
    empty_api, _assessment, empty_curriculum, _learner = client(
        history_value=history(attempts=())
    )
    empty_response = empty_api.get(
        f"/api/v1/curriculum/placements/{PLACEMENT_ID}/practice/progress"
    )

    original = history().attempts[0]
    correct_attempt = replace(
        original,
        score=3,
        outcome="all_correct",
        item_summaries=tuple(
            replace(summary, score=1, correct=True)
            for summary in original.item_summaries
        ),
    )
    correct_api, _assessment, correct_curriculum, _learner = client(
        history_value=history(attempts=(correct_attempt,))
    )
    correct_response = correct_api.get(
        f"/api/v1/curriculum/placements/{PLACEMENT_ID}/practice/progress"
    )

    assert empty_response.status_code == 200
    assert empty_response.json()["review_targets"] == []
    assert empty_curriculum.calls == 0
    assert correct_response.status_code == 200
    assert correct_response.json()["review_targets"] == []
    assert correct_curriculum.calls == 0


def test_missing_exact_review_mapping_remains_explicitly_unavailable() -> None:
    api, _assessment, curriculum, _learner = client()
    curriculum.available = False

    response = api.get(
        f"/api/v1/curriculum/placements/{PLACEMENT_ID}/practice/progress"
    )

    assert response.status_code == 200
    assert response.json()["review_targets"] == [
        {
            "schema_version": "1.0.0",
            "practice_placement_id": PLACEMENT_ID,
            "resource_id": "risk-return-review",
            "resource_version": "1.0.0",
            "resource_digest": "c" * 64,
            "resource_title": "Review risk and return",
            "state": "unavailable",
            "unavailable_reason": "mapping_not_found",
        }
    ]


def test_draft_save_uses_server_learner_and_rejects_scope_escape() -> None:
    api, assessment, _curriculum, _learner = client()
    body = json.loads(DRAFT_SAVE.read_text(encoding="utf-8"))

    response = api.put(
        f"/api/v1/curriculum/placements/{PLACEMENT_ID}/practice/draft",
        headers={"Origin": ORIGIN, "Sec-Fetch-Site": "same-origin"},
        json=body,
    )

    assert response.status_code == 200
    assert assessment.saved_request is not None
    assert assessment.saved_request.learner_id == LEARNER_ID
    assert json.loads(assessment.saved_request.draft) == body
    assert "learner_id" not in response.text

    mismatch = {**body, "placement_id": "another-practice-placement"}
    refused = api.put(
        f"/api/v1/curriculum/placements/{PLACEMENT_ID}/practice/draft",
        headers={"Origin": ORIGIN, "Sec-Fetch-Site": "same-origin"},
        json=mismatch,
    )
    assert refused.status_code == 409

    authority = {**body, "learner_id": LEARNER_ID}
    refused = api.put(
        f"/api/v1/curriculum/placements/{PLACEMENT_ID}/practice/draft",
        headers={"Origin": ORIGIN, "Sec-Fetch-Site": "same-origin"},
        json=authority,
    )
    assert refused.status_code == 400


def test_progress_and_save_enforce_session_permission_and_same_origin() -> None:
    forbidden_api, _assessment, _curriculum, _learner = client(
        permissions=()
    )
    denied_read = forbidden_api.get(
        f"/api/v1/curriculum/placements/{PLACEMENT_ID}/practice/progress"
    )
    assert denied_read.status_code == 403

    api, _assessment, _curriculum, _learner = client()
    api.cookies.clear()
    unauthorized = api.get(
        f"/api/v1/curriculum/placements/{PLACEMENT_ID}/practice/progress"
    )
    assert unauthorized.status_code == 401

    body = json.loads(DRAFT_SAVE.read_text(encoding="utf-8"))
    unsafe = api.put(
        f"/api/v1/curriculum/placements/{PLACEMENT_ID}/practice/draft",
        json=body,
    )
    assert unsafe.status_code in {401, 403}


def test_openapi_exposes_headless_progress_and_draft_operations() -> None:
    generated = generate_bytes()
    assert generated == OPENAPI_PATH.read_bytes()
    schema = json.loads(generated)
    progress = schema["paths"][
        "/api/v1/curriculum/placements/{placement_id}/practice/progress"
    ]["get"]
    draft = schema["paths"][
        "/api/v1/curriculum/placements/{placement_id}/practice/draft"
    ]["put"]

    assert progress["operationId"] == "getPlacedPracticeProgress"
    assert draft["operationId"] == "savePlacedPracticeDraft"
    assert progress["security"] == [{"OpaqueSessionCookie": []}]
    assert draft["security"] == [{"OpaqueSessionCookie": []}]
    assert "422" not in progress["responses"]
    assert "422" not in draft["responses"]
    assert draft["requestBody"]["content"]["application/json"]["schema"] == {
        "$ref": "#/components/schemas/PracticeDraftSaveRequestModel"
    }
    serialized = json.dumps(
        {
            "progress": progress,
            "draft": draft,
            "response": schema["components"]["schemas"][
                "PracticeProgressResponseModel"
            ],
        },
        sort_keys=True,
    )
    assert "learner_id" not in serialized
    assert "request_fingerprint" not in serialized


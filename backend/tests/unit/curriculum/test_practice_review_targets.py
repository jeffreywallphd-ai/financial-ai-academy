from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone

import pytest

from financial_ai_academy.modules.curriculum.application.service import (
    CurriculumService,
)
from financial_ai_academy.modules.curriculum.ports.repositories import (
    PracticeReviewConflict,
)
from financial_ai_academy.modules.curriculum.public import (
    LessonPlacement,
    PracticePlacement,
    PracticeReviewDestination,
    PracticeReviewError,
    PracticeReviewErrorCode,
    PracticeReviewResource,
    PracticeReviewState,
    PracticeReviewTarget,
    PracticeReviewUnavailableReason,
    RegisterPracticeReviewTargetRequest,
    ResolvePracticeReviewTargetsRequest,
)


PRACTICE_PLACEMENT = "risk-return-practice-placement"


class Repository:
    def __init__(self) -> None:
        created = datetime(2026, 10, 16, 15, 0, tzinfo=timezone.utc)
        self.practice = PracticePlacement(
            placement_id=PRACTICE_PLACEMENT,
            package_id="intro-risk-return",
            package_version="2.0.0",
            package_digest="a" * 64,
            practice_id="risk-return-practice",
            practice_version="1.0.0",
            definition_digest="b" * 64,
            created_at=created,
        )
        self.lesson = LessonPlacement(
            placement_id="risk-return-reading-placement",
            package_id="intro-risk-return",
            package_version="2.0.0",
            package_digest="a" * 64,
            created_at=created,
        )
        self.targets: dict[tuple[str, str, str, str], PracticeReviewTarget] = {}

    def get_practice(self, placement_id: str) -> PracticePlacement | None:
        return self.practice if placement_id == self.practice.placement_id else None

    def get(self, placement_id: str) -> LessonPlacement | None:
        return self.lesson if placement_id == self.lesson.placement_id else None

    def get_practice_review_target(
        self,
        practice_placement_id: str,
        resource_id: str,
        resource_version: str,
        resource_digest: str,
    ) -> PracticeReviewTarget | None:
        return self.targets.get(
            (
                practice_placement_id,
                resource_id,
                resource_version,
                resource_digest,
            )
        )

    def save_practice_review_target_if_absent(
        self, target: PracticeReviewTarget
    ) -> tuple[PracticeReviewTarget, bool]:
        key = (
            target.practice_placement_id,
            target.resource_id,
            target.resource_version,
            target.resource_digest,
        )
        existing = self.targets.get(key)
        if existing is None:
            self.targets[key] = target
            return target, True
        if existing != target:
            raise PracticeReviewConflict
        return existing, False


def available_target(*, title: str = "Review risk and return") -> PracticeReviewTarget:
    return PracticeReviewTarget(
        schema_version="1.0.0",
        practice_placement_id=PRACTICE_PLACEMENT,
        resource_id="risk-return-review",
        resource_version="1.0.0",
        resource_digest="c" * 64,
        resource_title=title,
        state=PracticeReviewState.AVAILABLE,
        destination=PracticeReviewDestination(
            placement_id="risk-return-reading-placement",
            package_id="intro-risk-return",
            package_version="2.0.0",
            package_digest="a" * 64,
            section_id="risk-return-review-section",
        ),
    )


def test_exact_mapping_is_idempotent_and_resolution_preserves_declared_order() -> None:
    repository = Repository()
    service = CurriculumService(repository, object())  # type: ignore[arg-type]
    created = service.register_practice_review_target(
        RegisterPracticeReviewTargetRequest(available_target())
    )
    replayed = service.register_practice_review_target(
        RegisterPracticeReviewTargetRequest(available_target())
    )

    targets = service.resolve_practice_review_targets(
        ResolvePracticeReviewTargetsRequest(
            practice_placement_id=PRACTICE_PLACEMENT,
            resources=(
                PracticeReviewResource(
                    resource_id="additional-review",
                    resource_version="1.1.0",
                    resource_digest="d" * 64,
                    resource_title="Additional review",
                ),
                PracticeReviewResource(
                    resource_id="risk-return-review",
                    resource_version="1.0.0",
                    resource_digest="c" * 64,
                    resource_title="Review risk and return",
                ),
                PracticeReviewResource(
                    resource_id="additional-review",
                    resource_version="1.1.0",
                    resource_digest="d" * 64,
                    resource_title="Additional review",
                ),
            ),
        )
    )

    assert created == replayed
    assert [target.resource_id for target in targets] == [
        "additional-review",
        "risk-return-review",
    ]
    assert targets[0].state is PracticeReviewState.UNAVAILABLE
    assert (
        targets[0].unavailable_reason
        is PracticeReviewUnavailableReason.MAPPING_NOT_FOUND
    )
    assert targets[1] == created


def test_exact_identity_conflict_and_unsafe_title_fail_closed() -> None:
    repository = Repository()
    service = CurriculumService(repository, object())  # type: ignore[arg-type]
    service.register_practice_review_target(
        RegisterPracticeReviewTargetRequest(available_target())
    )

    with pytest.raises(PracticeReviewError) as conflict:
        service.register_practice_review_target(
            RegisterPracticeReviewTargetRequest(
                available_target(title="Different meaning")
            )
        )
    assert conflict.value.code is PracticeReviewErrorCode.IMMUTABLE_CONFLICT

    with pytest.raises(PracticeReviewError) as unsafe:
        service.register_practice_review_target(
            RegisterPracticeReviewTargetRequest(
                available_target(title="<script>private</script>")
            )
        )
    assert unsafe.value.code is PracticeReviewErrorCode.INVALID_RECORD
    assert "private" not in str(unsafe.value.as_dict())


@pytest.mark.parametrize(
    "target",
    (
        replace(available_target(), state="bogus"),  # type: ignore[arg-type]
        replace(
            available_target(),
            state=PracticeReviewState.UNAVAILABLE,
            destination=None,
            unavailable_reason="bogus",  # type: ignore[arg-type]
        ),
    ),
)
def test_forged_review_state_or_reason_fails_closed(
    target: PracticeReviewTarget,
) -> None:
    service = CurriculumService(Repository(), object())  # type: ignore[arg-type]

    with pytest.raises(PracticeReviewError) as invalid:
        service.register_practice_review_target(
            RegisterPracticeReviewTargetRequest(target)
        )

    assert invalid.value.code is PracticeReviewErrorCode.INVALID_RECORD

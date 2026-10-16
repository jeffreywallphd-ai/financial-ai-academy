from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone

import pytest

from financial_ai_academy.modules.learner_model.application.service import (
    LearnerModelService,
)
from financial_ai_academy.modules.learner_model.domain.models import (
    PracticeHistoryProjection,
    SourcePracticeAttempt,
    SourcePracticeHistory,
    SourcePracticeItemSummary,
)
from financial_ai_academy.modules.learner_model.public import (
    LearnerModelError,
    LearnerModelErrorCode,
    OpenPracticeHistoryRequest,
)


LEARNER_ID = "11111111-1111-4111-8111-111111111111"
PLACEMENT_ID = "risk-return-practice-placement"
COMPLETED_AT = datetime(2026, 10, 16, 15, 0, tzinfo=timezone.utc)


def item(
    item_id: str,
    item_type: str,
    policy: str,
    *,
    score: int,
    references: tuple[str, ...] = (),
) -> SourcePracticeItemSummary:
    return SourcePracticeItemSummary(
        item_id=item_id,
        item_version="1.0.0",
        item_type=item_type,
        scoring_policy_id=policy,
        scoring_policy_version="1.0.0",
        score=score,
        max_score=1,
        correct=score == 1,
        review_reference_ids=references,
    )


def source(*, attempts: tuple[SourcePracticeAttempt, ...] | None = None) -> SourcePracticeHistory:
    if attempts is None:
        attempts = (
            SourcePracticeAttempt(
                attempt_order=1,
                event_id="55555555-5555-4555-8555-555555555555",
                attempt_id="33333333-3333-4333-8333-333333333333",
                evidence_id="44444444-4444-4444-8444-444444444444",
                learner_id=LEARNER_ID,
                submission_id="22222222-2222-4222-8222-222222222222",
                placement_id=PLACEMENT_ID,
                package_id="intro-risk-return",
                package_version="2.0.0",
                package_digest="a" * 64,
                definition_digest=(
                    "82cdc82c402aacdb0070fb19671d896ae22a4c16d338ccbf27f02a51a396d527"
                ),
                practice_id="risk-return-practice",
                practice_version="1.0.0",
                attempt_policy_id="formative-retry",
                attempt_policy_version="1.0.0",
                score=2,
                max_score=3,
                outcome="review_needed",
                item_summaries=(
                    item(
                        "risk-meaning",
                        "single_select",
                        "single-select-exact-match",
                        score=1,
                    ),
                    item(
                        "diversification-actions",
                        "multiple_select",
                        "multiple-select-exact-set",
                        score=0,
                        references=("risk-return-review",),
                    ),
                    item(
                        "simple-growth",
                        "numeric_entry",
                        "numeric-exact-or-inclusive-range",
                        score=1,
                    ),
                ),
                completed_at=COMPLETED_AT,
            ),
        )
    return SourcePracticeHistory(
        learner_id=LEARNER_ID,
        placement_id=PLACEMENT_ID,
        package_id="intro-risk-return",
        package_version="2.0.0",
        package_digest="a" * 64,
        definition_digest=(
            "82cdc82c402aacdb0070fb19671d896ae22a4c16d338ccbf27f02a51a396d527"
        ),
        practice_id="risk-return-practice",
        practice_version="1.0.0",
        attempt_policy_id="formative-retry",
        attempt_policy_version="1.0.0",
        attempts=attempts,
    )


class Source:
    def __init__(self, value: SourcePracticeHistory) -> None:
        self.value = value

    def read_practice_history(
        self, *, learner_id: str, placement_id: str
    ) -> SourcePracticeHistory:
        assert learner_id == LEARNER_ID
        assert placement_id == PLACEMENT_ID
        return self.value


class Repository:
    def __init__(self) -> None:
        self.projection: PracticeHistoryProjection | None = None

    def replace_practice_history(
        self, projection: PracticeHistoryProjection
    ) -> None:
        self.projection = projection


class Clock:
    def now(self) -> datetime:
        return datetime(2026, 10, 16, 16, 0, tzinfo=timezone.utc)


def service(value: SourcePracticeHistory) -> tuple[LearnerModelService, Repository]:
    repository = Repository()
    return (
        LearnerModelService(
            Source(value),  # type: ignore[arg-type]
            repository,  # type: ignore[arg-type]
            Clock(),
        ),
        repository,
    )


def request() -> OpenPracticeHistoryRequest:
    return OpenPracticeHistoryRequest(
        learner_id=LEARNER_ID,
        placement_id=PLACEMENT_ID,
    )


def test_rebuild_matches_canonical_contract_digest_and_exact_replay_is_idempotent() -> None:
    value = source()
    replayed = replace(value, attempts=(value.attempts[0], value.attempts[0]))
    operations, repository = service(replayed)

    view = operations.open_practice_history(request())

    assert view.source_digest == (
        "e21a237b2d331992d342b8f6ab3f7a57ed37b0c4accb1929d5ef016309680669"
    )
    assert len(view.attempts) == 1
    assert repository.projection is not None
    assert repository.projection.source_digest == view.source_digest


def test_zero_attempt_history_is_closed_and_rebuildable() -> None:
    operations, repository = service(source(attempts=()))

    view = operations.open_practice_history(request())

    assert view.attempts == ()
    assert view.source_digest == (
        "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945"
    )
    assert repository.projection is not None


def test_changed_item_signature_and_incorrect_item_without_review_fail_closed() -> None:
    first = source().attempts[0]
    bad_items = list(first.item_summaries)
    bad_items[1] = replace(bad_items[1], review_reference_ids=())
    operations, repository = service(
        source(attempts=(replace(first, item_summaries=tuple(bad_items)),))
    )

    with pytest.raises(LearnerModelError) as captured:
        operations.open_practice_history(request())

    assert captured.value.code is LearnerModelErrorCode.INCONSISTENT_EVIDENCE
    assert repository.projection is None

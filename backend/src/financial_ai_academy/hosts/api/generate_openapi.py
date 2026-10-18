"""Generate or verify the reviewed OpenAPI snapshot."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from financial_ai_academy.modules.assessment.public import (
    KnowledgeCheckPresentation,
    KnowledgeCheckResult,
    OpenPlacedKnowledgeCheckRequest,
    OpenPlacedPracticeRequest,
    OpenProjectSubmissionCandidateRequest,
    PracticeDraft,
    PracticePresentation,
    PracticeResult,
    PracticeRetryState,
    ReadPlacedPracticeProgressRequest,
    ReadProjectCompletionEvidenceRequest,
    ReadProjectCompletionHistoryRequest,
    SavePlacedPracticeDraftRequest,
    SubmitPlacedKnowledgeCheckRequest,
    SubmitPlacedPracticeRequest,
    SubmitProjectSnapshotRequest,
    ProjectCompletionEvidence,
    ProjectHistory,
    ProjectSnapshotCandidate,
    ProjectSubmissionOutcome,
)
from financial_ai_academy.modules.identity.public import (
    IdentityError,
    IdentityErrorCode,
    LearnerContext,
)
from financial_ai_academy.modules.audit.public import (
    AuditReconciliationReceipt,
    ProjectAuditReconciliationReceipt,
    ReconcileLessonCompletionAuditRequest,
    ReconcileProjectCompletionAuditRequest,
)
from financial_ai_academy.modules.learner_model.public import (
    AssistancePreferenceExport,
    AssistancePreferenceHistory,
    AssistancePreferenceProfile,
    ExportAssistancePreferencesRequest,
    ExportPresentationPreferencesRequest,
    ExportLearnerPreferencesRequest,
    LearnerPreferenceProfile,
    LessonCompletionView,
    MutateLearnerPreferencesRequest,
    MutateAssistancePreferencesRequest,
    MutatePresentationPreferencesRequest,
    OpenLearnerPreferencesRequest,
    OpenAssistancePreferencesRequest,
    OpenPresentationPreferencesRequest,
    OpenLessonCompletionRequest,
    OpenPracticeHistoryRequest,
    OpenProjectCompletionRequest,
    PreferenceExport,
    PreferenceHistory,
    PresentationPreferenceExport,
    PresentationPreferenceHistory,
    PresentationPreferenceProfile,
    PracticeHistoryView,
    ProjectCompletionView,
    ReadLearnerPreferenceHistoryRequest,
    ReadAssistancePreferenceHistoryRequest,
    ReadPresentationPreferenceHistoryRequest,
)
from financial_ai_academy.modules.curriculum.public import (
    BrowseLearningOpportunitiesRequest,
    CurriculumGraph,
    LearningOpportunityBrowse,
    LearningOpportunityQueryPage,
    OpenCurriculumGraphRequest,
    PracticeReviewTarget,
    QueryLearningOpportunitiesRequest,
    ResolvePracticeReviewTargetsRequest,
)
from financial_ai_academy.modules.guidance.public import (
    OpenPlatformHelpTopicRequest,
    PlatformHelpTopic,
    SearchPage as PlatformHelpSearchPage,
    SearchRequest as PlatformHelpSearchRequest,
)
from financial_ai_academy.platform.security.single_profile_policy import (
    SingleProfileRequestPolicy,
    SingleProfileSecuritySettings,
)

from .app import ApiServices, create_app


class _SchemaIdentity:
    def bootstrap_single_profile(self, request: object) -> object:
        raise NotImplementedError

    def resolve_session(self, cookie_value: str | None) -> LearnerContext:
        raise IdentityError(
            IdentityErrorCode.UNAUTHORIZED,
            "A valid learner session is required.",
        )

    def revoke_session(self, cookie_value: str | None) -> None:
        raise NotImplementedError

    def health(self) -> bool:
        return True


class _SchemaCurriculum:
    def create_lesson_placement(self, request: object) -> object:
        raise NotImplementedError

    def open_placed_lesson(self, request: object) -> object:
        raise NotImplementedError

    def open_curriculum_graph(
        self, request: OpenCurriculumGraphRequest
    ) -> CurriculumGraph:
        raise NotImplementedError

    def browse_learning_opportunities(
        self, request: BrowseLearningOpportunitiesRequest
    ) -> LearningOpportunityBrowse:
        raise NotImplementedError

    def query_learning_opportunities(
        self, request: QueryLearningOpportunitiesRequest
    ) -> LearningOpportunityQueryPage:
        raise NotImplementedError

    def resolve_practice_review_targets(
        self, request: ResolvePracticeReviewTargetsRequest
    ) -> tuple[PracticeReviewTarget, ...]:
        raise NotImplementedError


class _SchemaAssessment:
    def open_project_submission_candidate(
        self, request: OpenProjectSubmissionCandidateRequest
    ) -> ProjectSnapshotCandidate:
        raise NotImplementedError

    def submit_project_snapshot(
        self, request: SubmitProjectSnapshotRequest
    ) -> ProjectSubmissionOutcome:
        raise NotImplementedError

    def read_project_completion_evidence(
        self, request: ReadProjectCompletionEvidenceRequest
    ) -> ProjectCompletionEvidence:
        raise NotImplementedError

    def read_project_completion_history(
        self, request: ReadProjectCompletionHistoryRequest
    ) -> ProjectHistory:
        raise NotImplementedError

    def open_placed_knowledge_check(
        self, request: OpenPlacedKnowledgeCheckRequest
    ) -> KnowledgeCheckPresentation:
        raise NotImplementedError

    def open_placed_practice(
        self, request: OpenPlacedPracticeRequest
    ) -> PracticePresentation:
        raise NotImplementedError

    def submit_placed_practice(
        self, request: SubmitPlacedPracticeRequest
    ) -> PracticeResult:
        raise NotImplementedError

    def read_placed_practice_draft(
        self, request: ReadPlacedPracticeProgressRequest
    ) -> PracticeDraft | None:
        raise NotImplementedError

    def save_placed_practice_draft(
        self, request: SavePlacedPracticeDraftRequest
    ) -> PracticeDraft:
        raise NotImplementedError

    def read_placed_practice_retry_state(
        self, request: ReadPlacedPracticeProgressRequest
    ) -> PracticeRetryState:
        raise NotImplementedError

    def submit_placed_knowledge_check(
        self, request: SubmitPlacedKnowledgeCheckRequest
    ) -> KnowledgeCheckResult:
        raise NotImplementedError


class _SchemaGuidance:
    def search_platform_help(
        self, request: PlatformHelpSearchRequest
    ) -> PlatformHelpSearchPage:
        raise NotImplementedError

    def open_platform_help_topic(
        self, request: OpenPlatformHelpTopicRequest
    ) -> PlatformHelpTopic:
        raise NotImplementedError


class _SchemaAudit:
    def reconcile_lesson_completion(
        self, request: ReconcileLessonCompletionAuditRequest
    ) -> AuditReconciliationReceipt:
        raise NotImplementedError

    def reconcile_project_completion(
        self, request: ReconcileProjectCompletionAuditRequest
    ) -> ProjectAuditReconciliationReceipt:
        raise NotImplementedError


class _SchemaLearnerModel:
    def open_lesson_completion(
        self, request: OpenLessonCompletionRequest
    ) -> LessonCompletionView:
        raise NotImplementedError

    def open_practice_history(
        self, request: OpenPracticeHistoryRequest
    ) -> PracticeHistoryView:
        raise NotImplementedError

    def open_project_completion(
        self, request: OpenProjectCompletionRequest
    ) -> ProjectCompletionView:
        raise NotImplementedError

    def open_preferences(
        self, request: OpenLearnerPreferencesRequest
    ) -> LearnerPreferenceProfile:
        raise NotImplementedError

    def mutate_preferences(
        self, request: MutateLearnerPreferencesRequest
    ) -> LearnerPreferenceProfile:
        raise NotImplementedError

    def read_preference_history(
        self, request: ReadLearnerPreferenceHistoryRequest
    ) -> PreferenceHistory:
        raise NotImplementedError

    def export_preferences(
        self, request: ExportLearnerPreferencesRequest
    ) -> PreferenceExport:
        raise NotImplementedError

    def open_presentation_preferences(
        self, request: OpenPresentationPreferencesRequest
    ) -> PresentationPreferenceProfile:
        raise NotImplementedError

    def mutate_presentation_preferences(
        self, request: MutatePresentationPreferencesRequest
    ) -> PresentationPreferenceProfile:
        raise NotImplementedError

    def read_presentation_preference_history(
        self, request: ReadPresentationPreferenceHistoryRequest
    ) -> PresentationPreferenceHistory:
        raise NotImplementedError

    def export_presentation_preferences(
        self, request: ExportPresentationPreferencesRequest
    ) -> PresentationPreferenceExport:
        raise NotImplementedError

    def open_assistance_preferences(
        self, request: OpenAssistancePreferencesRequest
    ) -> AssistancePreferenceProfile:
        raise NotImplementedError

    def mutate_assistance_preferences(
        self, request: MutateAssistancePreferencesRequest
    ) -> AssistancePreferenceProfile:
        raise NotImplementedError

    def read_assistance_preference_history(
        self, request: ReadAssistancePreferenceHistoryRequest
    ) -> AssistancePreferenceHistory:
        raise NotImplementedError

    def export_assistance_preferences(
        self, request: ExportAssistancePreferencesRequest
    ) -> AssistancePreferenceExport:
        raise NotImplementedError


def repository_root() -> Path:
    return Path(__file__).resolve().parents[5]


def snapshot_path() -> Path:
    return repository_root() / "contracts/api/openapi.json"


def generate_bytes() -> bytes:
    policy = SingleProfileRequestPolicy(
        SingleProfileSecuritySettings(
            identity_mode="single_profile",
            bind_host="127.0.0.1",
            public_origin="http://127.0.0.1:8000",
            allowed_hosts=("127.0.0.1:8000", "testserver"),
            secure_cookie=False,
        )
    )
    app = create_app(
        ApiServices(
            identity=_SchemaIdentity(),  # type: ignore[arg-type]
            curriculum=_SchemaCurriculum(),  # type: ignore[arg-type]
            request_policy=policy,
            assessment=_SchemaAssessment(),
            learner_model=_SchemaLearnerModel(),
            audit=_SchemaAudit(),
            guidance=_SchemaGuidance(),
        )
    )
    return (
        json.dumps(
            app.openapi(),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + chr(10)
    ).encode("utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args(argv)
    expected = generate_bytes()
    target = snapshot_path()
    if arguments.check:
        if not target.is_file() or target.read_bytes() != expected:
            print(
                "OpenAPI snapshot is stale; run "
                "python -m financial_ai_academy.hosts.api.generate_openapi"
            )
            return 1
        print("OpenAPI snapshot is current.")
        return 0
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(expected)
    print(f"Wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

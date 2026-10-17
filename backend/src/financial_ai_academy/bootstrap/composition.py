"""Composition root; hosts receive public operations, never repositories."""

from __future__ import annotations

from dataclasses import dataclass

from financial_ai_academy.modules.adaptation.adapters.curriculum_gateway import (
    PublicCurriculumNavigationGateway,
)
from financial_ai_academy.modules.adaptation.adapters.learner_model_gateway import (
    PublicLearnerModelCompletionGateway,
)
from financial_ai_academy.modules.adaptation.adapters.system import (
    UtcClock as AdaptationUtcClock,
)
from financial_ai_academy.modules.adaptation.application.service import (
    AdaptationService,
)
from financial_ai_academy.modules.assessment.adapters.content_gateway import (
    PublicContentDefinitionGateway,
)
from financial_ai_academy.modules.assessment.adapters.contract import (
    ContractAssessmentDefinitionParser,
)
from financial_ai_academy.modules.assessment.adapters.curriculum_gateway import (
    PublicCurriculumAssessmentGateway,
)
from financial_ai_academy.modules.assessment.adapters.event_contract import (
    ContractAssessmentEventParser,
)
from financial_ai_academy.modules.assessment.adapters.postgres_repository import (
    PostgresAssessmentRepository,
)
from financial_ai_academy.modules.assessment.adapters.project_submission_contract import (
    ContractProjectSubmissionAdapter,
)
from financial_ai_academy.modules.assessment.adapters.project_submission_gateways import (
    PublicProjectSubmissionSource,
)
from financial_ai_academy.modules.assessment.adapters.practice_contract import (
    ContractPracticeDefinitionAdapter,
)
from financial_ai_academy.modules.assessment.adapters.practice_progress_contract import (
    ContractPracticeProgressAdapter,
)
from financial_ai_academy.modules.assessment.adapters import (
    practice_submission_contract,
)
from financial_ai_academy.modules.assessment.adapters.system import (
    UtcClock,
    UuidGenerator,
)
from financial_ai_academy.modules.assessment.application.service import (
    AssessmentService,
)
from financial_ai_academy.modules.audit.adapters.assessment_gateway import (
    AssessmentAuditEventSource,
)
from financial_ai_academy.modules.audit.adapters.postgres_repository import (
    PostgresAuditRepository,
)
from financial_ai_academy.modules.audit.adapters.system import (
    UtcClock as AuditUtcClock,
)
from financial_ai_academy.modules.audit.application.service import AuditService
from financial_ai_academy.modules.content.adapters.lesson_package import (
    ContractLessonPackageValidator,
)
from financial_ai_academy.modules.content.adapters.postgres_repository import (
    PostgresContentRepository,
)
from financial_ai_academy.modules.content.application.service import ContentService
from financial_ai_academy.modules.curriculum.adapters.content_gateway import (
    PublicContentGateway,
)
from financial_ai_academy.modules.curriculum.adapters.postgres_repository import (
    PostgresCurriculumRepository,
)
from financial_ai_academy.modules.curriculum.application.service import (
    CurriculumService,
)
from financial_ai_academy.modules.identity.adapters.postgres_repository import (
    PostgresIdentityRepository,
)
from financial_ai_academy.modules.identity.application.service import IdentityService
from financial_ai_academy.modules.learner_model.adapters.assessment_gateway import (
    AssessmentCompletionEvidenceSource,
)
from financial_ai_academy.modules.learner_model.adapters.postgres_repository import (
    PostgresCompletionProjectionRepository,
)
from financial_ai_academy.modules.learner_model.adapters.preference_contract import (
    ContractLearnerPreferenceAdapter,
)
from financial_ai_academy.modules.learner_model.adapters.presentation_preference_contract import (
    ContractPresentationPreferenceAdapter,
)
from financial_ai_academy.modules.learner_model.adapters.system import (
    StablePreferenceSeed,
    StablePresentationPreferenceSeed,
    UtcClock as LearnerModelUtcClock,
    UuidGenerator as LearnerModelUuidGenerator,
)
from financial_ai_academy.modules.learner_model.application.service import (
    LearnerModelService,
)
from financial_ai_academy.modules.project.adapters.learning_origin import (
    PublicContentProjectBriefGateway,
    PublicCurriculumProjectPlacementGateway,
)
from financial_ai_academy.modules.project.adapters.postgres_repository import (
    PostgresProjectRepository,
)
from financial_ai_academy.modules.project.adapters.object_storage import (
    ProjectFilesystemObjectStorage,
)
from financial_ai_academy.modules.project.adapters.project_contract import (
    ContractProjectAdapter,
)
from financial_ai_academy.modules.project.adapters.system import (
    UtcClock as ProjectUtcClock,
    UuidGenerator as ProjectUuidGenerator,
)
from financial_ai_academy.modules.project.application.service import ProjectService
from financial_ai_academy.modules.personal_workspace.adapters.learning_reference import (
    PublicCurriculumLearningReferenceGateway,
    PublicLearningReferenceGateway,
)
from financial_ai_academy.modules.personal_workspace.adapters.project_reference import (
    PublicProjectLearningReferenceGateway,
)
from financial_ai_academy.modules.personal_workspace.adapters.postgres_repository import (
    PostgresPersonalWorkspaceRepository,
)
from financial_ai_academy.modules.personal_workspace.adapters.system import (
    StableWorkspaceSeed,
    UtcClock as PersonalWorkspaceUtcClock,
    UuidGenerator as PersonalWorkspaceUuidGenerator,
)
from financial_ai_academy.modules.personal_workspace.adapters.workspace_contract import (
    ContractPersonalWorkspaceAdapter,
)
from financial_ai_academy.modules.personal_workspace.application.service import (
    PersonalWorkspaceService,
)
from financial_ai_academy.platform.database.migrations import (
    PostgresMigrationRunner,
)
from financial_ai_academy.platform.object_storage.filesystem import (
    FilesystemObjectStorage,
)
from financial_ai_academy.platform.security.single_profile_policy import (
    SingleProfileRequestPolicy,
)

from .settings import SingleProfileApplicationSettings


@dataclass(frozen=True, slots=True)
class ApplicationServices:
    content: ContentService
    curriculum: CurriculumService
    assessment: AssessmentService
    learner_model: LearnerModelService
    adaptation: AdaptationService
    audit: AuditService
    identity: IdentityService
    project: ProjectService
    personal_workspace: PersonalWorkspaceService
    request_policy: SingleProfileRequestPolicy


def build_application_services(
    settings: SingleProfileApplicationSettings,
    *,
    apply_migrations: bool = False,
) -> ApplicationServices:
    request_policy = settings.validate()
    if apply_migrations:
        PostgresMigrationRunner(
            settings.postgres_dsn, settings.migrations_dir
        ).apply_all()
        PostgresMigrationRunner(
            settings.postgres_dsn, settings.migrations_dir / "curriculum"
        ).apply_all()
        PostgresMigrationRunner(
            settings.postgres_dsn, settings.migrations_dir / "assessment"
        ).apply_all()
        PostgresMigrationRunner(
            settings.postgres_dsn, settings.migrations_dir / "learner_model"
        ).apply_all()
        PostgresMigrationRunner(
            settings.postgres_dsn, settings.migrations_dir / "audit"
        ).apply_all()
        PostgresMigrationRunner(
            settings.postgres_dsn, settings.migrations_dir / "identity"
        ).apply_all()
        PostgresMigrationRunner(
            settings.postgres_dsn, settings.migrations_dir / "project"
        ).apply_all()
        PostgresMigrationRunner(
            settings.postgres_dsn,
            settings.migrations_dir / "personal_workspace",
        ).apply_all()
    project_contract = ContractProjectAdapter(settings.project_schema_dir)
    object_storage = FilesystemObjectStorage(settings.object_storage_root)
    content = ContentService(
        PostgresContentRepository(settings.postgres_dsn),
        object_storage,
        ContractLessonPackageValidator(
            settings.lesson_schema_dir,
            project_schema_dir=settings.project_schema_dir,
        ),
    )
    curriculum = CurriculumService(
        PostgresCurriculumRepository(settings.postgres_dsn),
        PublicContentGateway(content),
    )
    project = ProjectService(
        PostgresProjectRepository(settings.postgres_dsn, project_contract),
        project_contract,
        PublicContentProjectBriefGateway(content, project_contract),
        PublicCurriculumProjectPlacementGateway(curriculum),
        ProjectUtcClock(),
        ProjectUuidGenerator(),
        ProjectFilesystemObjectStorage(object_storage),
    )
    personal_workspace_contract = ContractPersonalWorkspaceAdapter(
        settings.personal_workspace_schema_dir
    )
    personal_workspace = PersonalWorkspaceService(
        PostgresPersonalWorkspaceRepository(
            settings.postgres_dsn, personal_workspace_contract
        ),
        personal_workspace_contract,
        PublicLearningReferenceGateway(
            PublicCurriculumLearningReferenceGateway(curriculum),
            PublicProjectLearningReferenceGateway(project),
        ),
        PersonalWorkspaceUtcClock(),
        PersonalWorkspaceUuidGenerator(),
        StableWorkspaceSeed(),
    )
    project_submission_contract = ContractProjectSubmissionAdapter(
        settings.assessment_project_schema_dir
    )
    assessment = AssessmentService(
        PublicCurriculumAssessmentGateway(curriculum),
        PublicContentDefinitionGateway(content),
        ContractAssessmentDefinitionParser(settings.assessment_schema_dir),
        ContractAssessmentEventParser(settings.assessment_event_schema_dir),
        PostgresAssessmentRepository(
            settings.postgres_dsn,
            project_submission_contract=project_submission_contract,
        ),
        UtcClock(),
        UuidGenerator(),
        ContractPracticeDefinitionAdapter(settings.practice_schema_dir),
        practice_submission_contract.ContractPracticeSubmissionAdapter(
            settings.practice_schema_dir
        ),
        ContractPracticeProgressAdapter(settings.practice_schema_dir),
        PublicProjectSubmissionSource(
            project,
            content,
            curriculum,
            project_submission_contract,
            settings.project_schema_dir,
        ),
        project_submission_contract,
    )
    learner_preference_contract = ContractLearnerPreferenceAdapter(
        settings.learner_preference_schema_dir
    )
    learner_presentation_preference_contract = ContractPresentationPreferenceAdapter(
        settings.learner_presentation_preference_schema_dir
    )
    learner_model_repository = PostgresCompletionProjectionRepository(
        settings.postgres_dsn,
        preference_contract=learner_preference_contract,
        presentation_preference_contract=learner_presentation_preference_contract,
    )
    learner_model = LearnerModelService(
        AssessmentCompletionEvidenceSource(assessment),
        learner_model_repository,
        LearnerModelUtcClock(),
        learner_model_repository,
        learner_preference_contract,
        LearnerModelUuidGenerator(),
        StablePreferenceSeed(),
        learner_model_repository,
        learner_presentation_preference_contract,
        StablePresentationPreferenceSeed(),
    )
    adaptation = AdaptationService(
        PublicCurriculumNavigationGateway(curriculum),
        PublicLearnerModelCompletionGateway(learner_model),
        AdaptationUtcClock(),
    )
    audit = AuditService(
        AssessmentAuditEventSource(assessment),
        PostgresAuditRepository(settings.postgres_dsn),
        AuditUtcClock(),
    )
    identity = IdentityService(
        PostgresIdentityRepository(settings.postgres_dsn),
        configured_mode=settings.security.identity_mode,
    )
    return ApplicationServices(
        content=content,
        curriculum=curriculum,
        assessment=assessment,
        learner_model=learner_model,
        adaptation=adaptation,
        audit=audit,
        identity=identity,
        project=project,
        personal_workspace=personal_workspace,
        request_policy=request_policy,
    )

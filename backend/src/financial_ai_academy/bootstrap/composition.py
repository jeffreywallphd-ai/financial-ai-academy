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
from financial_ai_academy.modules.learner_model.adapters.system import (
    UtcClock as LearnerModelUtcClock,
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
    assessment = AssessmentService(
        PublicCurriculumAssessmentGateway(curriculum),
        PublicContentDefinitionGateway(content),
        ContractAssessmentDefinitionParser(settings.assessment_schema_dir),
        ContractAssessmentEventParser(settings.assessment_event_schema_dir),
        PostgresAssessmentRepository(settings.postgres_dsn),
        UtcClock(),
        UuidGenerator(),
        ContractPracticeDefinitionAdapter(settings.practice_schema_dir),
        practice_submission_contract.ContractPracticeSubmissionAdapter(
            settings.practice_schema_dir
        ),
        ContractPracticeProgressAdapter(settings.practice_schema_dir),
    )
    learner_model = LearnerModelService(
        AssessmentCompletionEvidenceSource(assessment),
        PostgresCompletionProjectionRepository(settings.postgres_dsn),
        LearnerModelUtcClock(),
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
    project = ProjectService(
        PostgresProjectRepository(settings.postgres_dsn, project_contract),
        project_contract,
        PublicContentProjectBriefGateway(content, project_contract),
        PublicCurriculumProjectPlacementGateway(curriculum),
        ProjectUtcClock(),
        ProjectUuidGenerator(),
        ProjectFilesystemObjectStorage(object_storage),
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
        request_policy=request_policy,
    )

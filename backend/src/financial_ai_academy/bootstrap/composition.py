"""Composition root; hosts receive public operations, never repositories."""

from __future__ import annotations

from dataclasses import dataclass

from financial_ai_academy.modules.assessment.adapters.content_gateway import (
    PublicContentDefinitionGateway,
)
from financial_ai_academy.modules.assessment.adapters.contract import (
    ContractAssessmentDefinitionParser,
)
from financial_ai_academy.modules.assessment.adapters.curriculum_gateway import (
    PublicCurriculumAssessmentGateway,
)
from financial_ai_academy.modules.assessment.adapters.postgres_repository import (
    PostgresAssessmentRepository,
)
from financial_ai_academy.modules.assessment.adapters.system import (
    UtcClock,
    UuidGenerator,
)
from financial_ai_academy.modules.assessment.application.service import (
    AssessmentService,
)
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
    identity: IdentityService
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
            settings.postgres_dsn, settings.migrations_dir / "identity"
        ).apply_all()
    content = ContentService(
        PostgresContentRepository(settings.postgres_dsn),
        FilesystemObjectStorage(settings.object_storage_root),
        ContractLessonPackageValidator(settings.lesson_schema_dir),
    )
    curriculum = CurriculumService(
        PostgresCurriculumRepository(settings.postgres_dsn),
        PublicContentGateway(content),
    )
    assessment = AssessmentService(
        PublicCurriculumAssessmentGateway(curriculum),
        PublicContentDefinitionGateway(content),
        ContractAssessmentDefinitionParser(settings.assessment_schema_dir),
        PostgresAssessmentRepository(settings.postgres_dsn),
        UtcClock(),
        UuidGenerator(),
    )
    identity = IdentityService(
        PostgresIdentityRepository(settings.postgres_dsn),
        configured_mode=settings.security.identity_mode,
    )
    return ApplicationServices(
        content=content,
        curriculum=curriculum,
        assessment=assessment,
        identity=identity,
        request_policy=request_policy,
    )

"""Composition root; hosts receive public operations, never repositories."""

from __future__ import annotations

from dataclasses import dataclass

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
    identity = IdentityService(
        PostgresIdentityRepository(settings.postgres_dsn),
        configured_mode=settings.security.identity_mode,
    )
    return ApplicationServices(
        content=content,
        curriculum=curriculum,
        identity=identity,
        request_policy=request_policy,
    )

from pathlib import Path

from financial_ai_academy.bootstrap.settings import (
    SingleProfileApplicationSettings,
)
from financial_ai_academy.platform.security.single_profile_policy import (
    SingleProfileRequestPolicy,
    SingleProfileSecuritySettings,
)


def test_contract_schema_directories_resolve_from_the_shared_contract_root(
    tmp_path: Path,
) -> None:
    contracts = tmp_path / "contracts"
    lesson = contracts / "learning" / "lesson-package" / "v1"
    assessment = contracts / "learning" / "assessment" / "v1"
    practice = contracts / "learning" / "assessment" / "practice" / "v1"
    assessment_project = (
        contracts / "learning" / "assessment" / "project" / "v1"
    )
    events = contracts / "events" / "assessment" / "v1"
    project = contracts / "learning" / "project" / "v1"
    personal_workspace = contracts / "learning" / "personal-workspace" / "v1"
    learner_preferences = contracts / "learning" / "learner-preferences" / "v1"
    learner_presentation_preferences = (
        contracts / "learning" / "learner-presentation-preferences" / "v1"
    )
    migrations = tmp_path / "migrations"
    for directory in (
        lesson,
        assessment,
        practice,
        assessment_project,
        events,
        project,
        personal_workspace,
        learner_preferences,
        learner_presentation_preferences,
        migrations,
    ):
        directory.mkdir(parents=True, exist_ok=True)

    settings = SingleProfileApplicationSettings(
        postgres_dsn="postgresql://qualification-only",
        object_storage_root=tmp_path / "objects",
        lesson_schema_dir=lesson,
        migrations_dir=migrations,
        security=SingleProfileSecuritySettings(
            identity_mode="single_profile",
            bind_host="127.0.0.1",
            public_origin="http://127.0.0.1:8000",
            allowed_hosts=("127.0.0.1:8000",),
            secure_cookie=False,
        ),
    )

    assert settings.assessment_schema_dir == assessment
    assert settings.practice_schema_dir == practice
    assert settings.assessment_event_schema_dir == events
    assert settings.project_schema_dir == project
    assert settings.assessment_project_schema_dir == assessment_project
    assert settings.personal_workspace_schema_dir == personal_workspace
    assert settings.learner_preference_schema_dir == learner_preferences
    assert (
        settings.learner_presentation_preference_schema_dir
        == learner_presentation_preferences
    )
    assert isinstance(settings.validate(), SingleProfileRequestPolicy)

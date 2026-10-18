from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from financial_ai_academy.modules.audit.adapters import (
    ProjectSnapshotReferenceAdapter,
)
from financial_ai_academy.modules.audit.application import (
    CrossDomainConformanceCode,
    evaluate_cross_domain_reference,
    run_cross_domain_conformance,
)
from financial_ai_academy.modules.audit.domain import CrossDomainProfile
from financial_ai_academy.modules.project.domain.workspace import (
    ProjectSnapshotMaterial,
)
from financial_ai_academy.modules.project.public import (
    OpenProjectSnapshotRequest,
    ProjectError,
    ProjectErrorCode,
    ProjectSnapshot,
)

from .synthetic_adapters import synthetic_reference_adapters


NOW = datetime(2026, 10, 18, 9, 48, tzinfo=timezone.utc)
ALL_PROFILES = frozenset(CrossDomainProfile)


def _snapshot() -> ProjectSnapshot:
    return ProjectSnapshot(
        schema_version="project-workspace-v1",
        snapshot_id="snapshot-mixed-suite-001",
        snapshot_digest="d" * 64,
        snapshot=ProjectSnapshotMaterial(
            project_id="project-mixed-suite-001",
            learner_id="learner-private-mixed-suite",
            project_revision=4,
            project_shell_digest="e" * 64,
            workspace_revision=9,
            workspace_created_at=NOW,
            workspace_updated_at=NOW,
            notes=(),
            references=(),
            artifacts=(),
            domain_links=(),
        ),
        closed_at=NOW,
    )


@dataclass
class ProjectSnapshotOperations:
    result: ProjectSnapshot
    failure: Exception | None = None

    def open_snapshot(
        self, request: OpenProjectSnapshotRequest
    ) -> ProjectSnapshot:
        if self.failure is not None:
            raise self.failure
        assert request == OpenProjectSnapshotRequest(
            learner_id="learner-private-mixed-suite",
            project_id="project-mixed-suite-001",
            snapshot_id="snapshot-mixed-suite-001",
        )
        return self.result


def _project_adapter(
    operations: ProjectSnapshotOperations | None = None,
) -> ProjectSnapshotReferenceAdapter:
    project_operations = operations or ProjectSnapshotOperations(_snapshot())
    return ProjectSnapshotReferenceAdapter(
        operations=project_operations,  # type: ignore[arg-type]
        learner_id="learner-private-mixed-suite",
        project_id="project-mixed-suite-001",
        snapshot_id="snapshot-mixed-suite-001",
    )


def _mixed_adapters() -> tuple[object, ...]:
    return tuple(
        _project_adapter()
        if adapter.profile is CrossDomainProfile.PROJECT_SNAPSHOT
        else adapter
        for adapter in synthetic_reference_adapters()
    )


def test_real_project_adapter_replaces_only_its_synthetic_profile() -> None:
    adapters = _mixed_adapters()
    report = run_cross_domain_conformance(adapters)  # type: ignore[arg-type]
    project = evaluate_cross_domain_reference(_project_adapter())

    assert report.complete is True
    assert report.missing_profiles == ()
    assert {case.profile for case in report.cases} == ALL_PROFILES
    assert all(
        case.code is CrossDomainConformanceCode.VALID for case in report.cases
    )
    assert next(
        case.envelope_digest
        for case in report.cases
        if case.profile is CrossDomainProfile.PROJECT_SNAPSHOT
    ) == project.envelope_digest


def test_mixed_suite_supports_varied_partial_adoption_and_input_order() -> None:
    adapters = _mixed_adapters()
    selections = (
        (),
        adapters[:1],
        adapters[1:4],
        adapters[::2],
        tuple(reversed(adapters[2:7])),
    )

    for selected in selections:
        forward = run_cross_domain_conformance(selected)  # type: ignore[arg-type]
        reversed_report = run_cross_domain_conformance(  # type: ignore[arg-type]
            tuple(reversed(selected))
        )
        declared = {adapter.profile for adapter in selected}
        expected_missing = tuple(
            sorted(ALL_PROFILES - declared, key=lambda profile: profile.value)
        )

        assert forward.cases == reversed_report.cases
        assert forward.missing_profiles == expected_missing
        assert len(forward.cases) == len(selected)
        assert forward.complete is (declared == ALL_PROFILES)


def test_real_project_failure_does_not_disable_unrelated_profiles() -> None:
    secret = "https://private.example/project?token=secret"
    failure = ProjectError(
        ProjectErrorCode.UNAVAILABLE,
        f"private Project failure at {secret}",
        reference=secret,
    )
    project = _project_adapter(ProjectSnapshotOperations(_snapshot(), failure))
    unrelated = tuple(
        adapter
        for adapter in synthetic_reference_adapters()
        if adapter.profile
        in {
            CrossDomainProfile.DATASET_SNAPSHOT,
            CrossDomainProfile.MARKET_OBSERVATION,
        }
    )

    report = run_cross_domain_conformance((project, *unrelated))
    cases = {case.profile: case for case in report.cases}

    assert cases[CrossDomainProfile.PROJECT_SNAPSHOT].code is (
        CrossDomainConformanceCode.ADAPTER_FAILURE
    )
    assert (
        cases[CrossDomainProfile.PROJECT_SNAPSHOT].reference
        == "adapter.reference"
    )
    assert cases[CrossDomainProfile.DATASET_SNAPSHOT].valid is True
    assert cases[CrossDomainProfile.MARKET_OBSERVATION].valid is True
    assert CrossDomainProfile.PROJECT_SNAPSHOT not in report.missing_profiles
    assert secret not in repr(report)
    assert "private Project failure" not in repr(report)

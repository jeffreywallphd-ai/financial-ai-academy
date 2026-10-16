from __future__ import annotations

import copy
from datetime import datetime
import json
import subprocess
import sys
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from financial_ai_academy.modules.adaptation.public import (
    ActivityNavigationState,
    ActivitySourceState,
    CompletionState,
    EligibilityState,
    NavigationReason,
    NavigationReasonCode,
    NavigationStateProjection,
    RequirementState,
    ResolveActivityLaunchRequest,
    activity_launch_payload,
    resolve_activity_launch,
)
from financial_ai_academy.modules.curriculum.public import curriculum_graph_from_mapping

from .runner import (
    ActivityLaunchContractValidator,
    ConformanceFailure,
    approved_launch,
    default_corpus_dir,
    default_graph_path,
    default_navigation_path,
    default_schema_path,
    load_json,
    projection_digest,
)


REPOSITORY = Path(__file__).resolve().parents[4]


def _domain_projection(value: dict) -> NavigationStateProjection:
    return NavigationStateProjection(
        schema_version=value["schema_version"],
        curriculum_id=value["curriculum_id"],
        curriculum_version=value["curriculum_version"],
        graph_digest=value["graph_digest"],
        policy_id=value["policy_id"],
        policy_version=value["policy_version"],
        evaluated_at=datetime.fromisoformat(value["evaluated_at"].replace("Z", "+00:00")),
        source_set_digest=value["source_set_digest"],
        activity_states=tuple(
            ActivityNavigationState(
                activity_id=item["activity_id"],
                completion=CompletionState(item["completion"]),
                eligibility=EligibilityState(item["eligibility"]),
                requirement=RequirementState(item["requirement"]),
                availability=ActivitySourceState(item["availability"]),
                reasons=tuple(
                    NavigationReason(
                        code=NavigationReasonCode(reason["code"]),
                        explanation=reason["explanation"],
                        references=tuple(reason["references"]),
                    )
                    for reason in item["reasons"]
                ),
            )
            for item in value["activity_states"]
        ),
        projection_digest=value["projection_digest"],
    )


def test_schema_is_closed_valid_draft_2020_12() -> None:
    schema = load_json(default_schema_path())
    Draft202012Validator.check_schema(schema)
    approved = approved_launch()
    assert list(Draft202012Validator(schema).iter_errors(approved)) == []
    extended = {**approved, "learner_id": "private"}
    assert list(Draft202012Validator(schema).iter_errors(extended))


def test_approved_launch_matches_graph_navigation_and_public_policy() -> None:
    launch = approved_launch()
    graph = load_json(default_graph_path())
    navigation = load_json(default_navigation_path())
    ActivityLaunchContractValidator().validate(launch, graph, navigation)
    result = resolve_activity_launch(
        ResolveActivityLaunchRequest(
            graph=curriculum_graph_from_mapping(graph),
            navigation_state=_domain_projection(navigation),
            activity_id=launch["activity_id"],
        )
    )
    assert activity_launch_payload(result) == launch


def test_denial_corpus_names_all_required_bounded_refusals() -> None:
    corpus = load_json(default_corpus_dir() / "cases/denials.json")
    assert corpus["schema_version"] == "1.0.0"
    assert {item["case_id"] for item in corpus["cases"]} == {
        "unknown-activity",
        "locked-activity",
        "unavailable-activity",
        "unsupported-assessment",
        "mismatched-navigation-context",
        "tampered-projection-digest",
        "unsafe-activity-identity",
    }
    assert all(item["expected_destination"] is False for item in corpus["cases"])


@pytest.mark.parametrize(
    "mutation,expected_code",
    [
        ("unknown", "adaptation_activity_launch.activity_not_found"),
        ("locked", "adaptation_activity_launch.activity_locked"),
        ("unavailable", "adaptation_activity_launch.activity_unavailable"),
        ("assessment", "adaptation_activity_launch.unsupported_activity"),
        ("context", "adaptation_activity_launch.context_mismatch"),
        ("digest", "adaptation_activity_launch.navigation_mismatch"),
    ],
)
def test_denials_are_deterministic_and_sanitized(mutation: str, expected_code: str) -> None:
    launch = copy.deepcopy(approved_launch())
    graph = load_json(default_graph_path())
    navigation = load_json(default_navigation_path())
    if mutation == "unknown":
        launch["activity_id"] = "activity-unknown"
    elif mutation in {"locked", "unavailable"}:
        navigation["activity_states"][0]["eligibility"] = mutation
        navigation["projection_digest"] = projection_digest(navigation)
        launch["navigation_projection_digest"] = navigation["projection_digest"]
    elif mutation == "assessment":
        launch["activity_id"] = "activity-risk-return-check"
    elif mutation == "context":
        launch["curriculum_version"] = "2.0.0"
    else:
        navigation["projection_digest"] = "f" * 64
    with pytest.raises(ConformanceFailure) as captured:
        ActivityLaunchContractValidator().validate(launch, graph, navigation)
    assert captured.value.diagnostic.code == expected_code
    assert len(captured.value.diagnostic.reference) <= 120
    assert "\n" not in captured.value.diagnostic.reference
    assert "destination" not in captured.value.diagnostic.as_dict()


def test_cli_emits_bounded_success_without_private_or_filesystem_data() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "tests.contract.adaptation_activity_launch.runner"],
        cwd=REPOSITORY / "backend",
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert completed.returncode == 0, completed.stderr
    assert json.loads(completed.stdout) == {
        "activity_id": "activity-risk-return-lesson",
        "curriculum_id": "investing-foundations",
        "curriculum_version": "1.0.0",
        "destination": "/learn/placements/intro-risk-return-primary",
        "valid": True,
    }
    combined = completed.stdout + completed.stderr
    assert str(REPOSITORY) not in combined
    assert "learner_id" not in combined
    assert "Traceback" not in combined

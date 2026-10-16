"""Dependency-light conformance runner for Assessment practice v1."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Mapping, Sequence

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource


VERSION = "1.0.0"
POLICIES = {
    "single_select": "single-select-exact-match",
    "multiple_select": "multiple-select-exact-set",
    "numeric_entry": "numeric-exact-or-inclusive-range",
}
DECIMAL_RE = re.compile(r"^-?(0|[1-9][0-9]*)(?:\.([0-9]{1,6}))?$")
PRIVATE_NAMES = {
    "answer",
    "correct_option_id",
    "correct_option_ids",
    "feedback",
}


class PracticeConformanceFailure(ValueError):
    def __init__(self, code: str, reference: str, message: str) -> None:
        self.code = code
        self.reference = safe_reference(reference)
        self.message = message
        super().__init__(message)

    def as_dict(self) -> dict[str, str]:
        return {
            "code": self.code,
            "reference": self.reference,
            "message": self.message,
        }


def safe_reference(value: object) -> str:
    return (
        str(value)
        .replace(chr(0), "")
        .replace("\r", " ")
        .replace("\n", " ")[:120]
    )


def reject(code: str, reference: str, message: str) -> None:
    raise PracticeConformanceFailure(code, reference, message)


def repository_root() -> Path:
    return Path(__file__).resolve().parents[4]


def schema_dir() -> Path:
    return repository_root() / "contracts/learning/assessment/practice/v1"


def corpus_dir() -> Path:
    return repository_root() / "contracts/compatibility/assessment-practice/v1"


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        reject(
            "assessment.practice.schema_invalid",
            path.name,
            "Practice record must be an object.",
        )
    return value


def canonical_practice_bytes(practice: Mapping[str, Any]) -> bytes:
    return json.dumps(
        practice,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def definition_digest(definition: Mapping[str, Any]) -> str:
    practice = definition.get("practice")
    if not isinstance(practice, Mapping):
        reject(
            "assessment.practice.schema_invalid",
            "practice",
            "Practice definition is malformed.",
        )
    return hashlib.sha256(canonical_practice_bytes(practice)).hexdigest()


def approved_pair(
    corpus: Path | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    approved = (corpus or corpus_dir()) / "approved"
    return load_json(approved / "definition.json"), load_json(
        approved / "presentation.json"
    )


def approved_chain(
    corpus: Path | None = None,
) -> tuple[
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
]:
    approved = (corpus or corpus_dir()) / "approved"
    definition, presentation = approved_pair(corpus)
    return (
        definition,
        presentation,
        load_json(approved / "submission.json"),
        load_json(approved / "result.json"),
        load_json(approved / "completion-event.json"),
    )


def approved_progress(
    corpus: Path | None = None,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    approved = (corpus or corpus_dir()) / "approved"
    return (
        load_json(approved / "draft-save.json"),
        load_json(approved / "draft.json"),
        load_json(approved / "retry-state.json"),
    )


def canonical_draft_responses_bytes(responses: Sequence[Mapping[str, Any]]) -> bytes:
    canonical = copy.deepcopy(list(responses))
    for response in canonical:
        if isinstance(response.get("selected_option_ids"), list):
            response["selected_option_ids"] = sorted(response["selected_option_ids"])
    canonical.sort(key=lambda response: str(response.get("item_id", "")))
    return json.dumps(
        canonical,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def draft_response_fingerprint(responses: Sequence[Mapping[str, Any]]) -> str:
    return hashlib.sha256(canonical_draft_responses_bytes(responses)).hexdigest()


def classify_draft_save(
    current_draft: Mapping[str, Any] | None,
    draft_save: Mapping[str, Any],
) -> str:
    """Classify conditional-save behavior without assigning server authority."""
    expected_revision = int(draft_save["expected_revision"])
    if current_draft is None:
        return "create" if expected_revision == 0 else "conflict"
    fingerprint = draft_response_fingerprint(draft_save["responses"])
    if fingerprint == current_draft["response_fingerprint"]:
        return "replay"
    if expected_revision != current_draft["revision"]:
        return "conflict"
    return "replace"


def canonical_submission_bytes(submission: Mapping[str, Any]) -> bytes:
    canonical = copy.deepcopy(dict(submission))
    responses = canonical.get("responses")
    if not isinstance(responses, list):
        reject(
            "assessment.practice.schema_invalid",
            "responses",
            "Practice responses must be an array.",
        )
    for response in responses:
        if isinstance(response, dict) and isinstance(
            response.get("selected_option_ids"), list
        ):
            response["selected_option_ids"] = sorted(
                response["selected_option_ids"]
            )
    canonical["responses"] = sorted(
        responses,
        key=lambda response: (
            str(response.get("item_id", ""))
            if isinstance(response, Mapping)
            else ""
        ),
    )
    return json.dumps(
        canonical,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def submission_fingerprint(submission: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_submission_bytes(submission)).hexdigest()


def _private_name(value: object) -> str | None:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            if key in PRIVATE_NAMES:
                return str(key)
            found = _private_name(nested)
            if found:
                return found
    elif isinstance(value, list):
        for nested in value:
            found = _private_name(nested)
            if found:
                return found
    return None


class PracticeContractValidator:
    def __init__(self, schemas: Path | None = None) -> None:
        root = schemas or schema_dir()
        self._schemas = {
            name: load_json(root / f"{name}.schema.json")
            for name in (
                "definition",
                "presentation",
                "submission",
                "result",
                "completion-event",
                "draft-save",
                "draft",
                "retry-state",
            )
        }
        registry = Registry().with_resources(
            (
                schema["$id"],
                Resource.from_contents(schema),
            )
            for schema in self._schemas.values()
        )
        self._validators: dict[str, Draft202012Validator] = {}
        for schema in self._schemas.values():
            Draft202012Validator.check_schema(schema)
        for name, schema in self._schemas.items():
            self._validators[name] = Draft202012Validator(
                schema,
                registry=registry,
                format_checker=FormatChecker(),
            )

    def _versions(self, definition: Mapping[str, Any]) -> None:
        if definition.get("schema_version") != VERSION:
            reject(
                "assessment.practice.unsupported_version",
                "schema_version",
                "Practice contract version is unsupported.",
            )
        practice = definition.get("practice")
        if not isinstance(practice, Mapping):
            return
        if practice.get("practice_version") != VERSION:
            reject(
                "assessment.practice.unsupported_version",
                "practice_version",
                "Practice version is unsupported.",
            )
        for index, item in enumerate(practice.get("items", ())):
            if not isinstance(item, Mapping):
                continue
            item_type = item.get("item_type")
            if not isinstance(item_type, str):
                continue
            if item_type not in POLICIES:
                reject(
                    "assessment.practice.unsupported_item_type",
                    f"items.{index}.item_type",
                    "Practice item type is unsupported.",
                )
            if item.get("item_version") != VERSION:
                reject(
                    "assessment.practice.unsupported_version",
                    f"items.{index}.item_version",
                    "Practice item version is unsupported.",
                )
            policy = item.get("scoring_policy")
            if isinstance(policy, Mapping) and (
                policy.get("policy_id") != POLICIES[item_type]
                or policy.get("policy_version") != VERSION
            ):
                reject(
                    "assessment.practice.unsupported_policy",
                    f"items.{index}.scoring_policy",
                    "Practice scoring policy is unsupported.",
                )

    def _shape(self, kind: str, value: Mapping[str, Any]) -> None:
        error = next(
            iter(
                self._validators[kind].iter_errors(value)
            ),
            None,
        )
        if error is not None:
            reference = ".".join(str(part) for part in error.absolute_path)
            reject(
                "assessment.practice.schema_invalid",
                reference or kind,
                f"Practice {kind} is malformed.",
            )

    def validate_definition(self, definition: Mapping[str, Any]) -> None:
        self._versions(definition)
        self._shape("definition", definition)
        if definition_digest(definition) != definition["definition_digest"]:
            reject(
                "assessment.practice.definition_digest_mismatch",
                "definition_digest",
                "Practice definition digest does not match its meaning.",
            )
        practice = definition["practice"]
        self._unique(
            [item["item_id"] for item in practice["items"]],
            "items",
        )
        self._unique(
            [item["resource_id"] for item in practice["source_references"]],
            "source_references",
        )
        review_ids = [
            item["resource_id"] for item in practice["review_references"]
        ]
        self._unique(review_ids, "review_references")
        declared_review = set(review_ids)
        for index, item in enumerate(practice["items"]):
            self._validate_item(item, index, declared_review)

    def _validate_item(
        self, item: Mapping[str, Any], index: int, review_ids: set[str]
    ) -> None:
        item_type = item["item_type"]
        for feedback in item["feedback"].values():
            if not set(feedback["review_reference_ids"]).issubset(review_ids):
                reject(
                    "assessment.practice.invalid_definition",
                    f"items.{index}.feedback",
                    "Feedback must reference declared review resources.",
                )
        if item_type in {"single_select", "multiple_select"}:
            option_ids = [option["option_id"] for option in item["options"]]
            self._unique(option_ids, f"items.{index}.options")
            declared = set(option_ids)
            correct = (
                {item["correct_option_id"]}
                if item_type == "single_select"
                else set(item["correct_option_ids"])
            )
            if not correct.issubset(declared):
                reject(
                    "assessment.practice.invalid_definition",
                    f"items.{index}.options",
                    "Correct options must be declared by the item.",
                )
            return
        response = item["response"]
        answer = item["answer"]
        values = (
            [answer["value"]]
            if answer["mode"] == "exact"
            else [answer["lower"], answer["upper"]]
        )
        decimals = [
            self._decimal(value, response["scale"], index) for value in values
        ]
        if not response["allow_negative"] and any(value < 0 for value in decimals):
            reject(
                "assessment.practice.invalid_decimal",
                f"items.{index}.answer",
                "Negative answers are not allowed by this item.",
            )
        if answer["mode"] == "inclusive_range" and decimals[0] > decimals[1]:
            reject(
                "assessment.practice.invalid_decimal",
                f"items.{index}.answer",
                "Numeric range bounds are inverted.",
            )

    @staticmethod
    def _unique(values: list[str], reference: str) -> None:
        if len(values) != len(set(values)):
            reject(
                "assessment.practice.invalid_definition",
                reference,
                "Practice identities must be unique.",
            )

    @staticmethod
    def _decimal(value: str, scale: int, item_index: int) -> Decimal:
        match = DECIMAL_RE.fullmatch(value)
        fraction = match.group(2) if match else None
        if match is None or len(fraction or "") != scale:
            reject(
                "assessment.practice.invalid_decimal",
                f"items.{item_index}.answer",
                "Numeric answer does not match the declared fixed scale.",
            )
        if value.startswith("-0") and Decimal(value) == 0:
            reject(
                "assessment.practice.invalid_decimal",
                f"items.{item_index}.answer",
                "Negative zero is not a canonical numeric answer.",
            )
        try:
            return Decimal(value)
        except InvalidOperation as error:
            raise PracticeConformanceFailure(
                "assessment.practice.invalid_decimal",
                f"items.{item_index}.answer",
                "Numeric answer is invalid.",
            ) from error

    def project(
        self,
        definition: Mapping[str, Any],
        *,
        placement_id: str,
        package_id: str,
        package_version: str,
        package_digest: str,
    ) -> dict[str, Any]:
        self.validate_definition(definition)
        practice = definition["practice"]
        items: list[dict[str, Any]] = []
        for item in practice["items"]:
            projected = {
                "item_id": item["item_id"],
                "item_version": item["item_version"],
                "item_type": item["item_type"],
                "prompt": item["prompt"],
                "scoring_policy_id": item["scoring_policy"]["policy_id"],
                "scoring_policy_version": item["scoring_policy"]["policy_version"],
                "max_score": item["scoring_policy"]["max_score"],
            }
            if item["item_type"] in {"single_select", "multiple_select"}:
                projected["options"] = copy.deepcopy(item["options"])
            else:
                projected.update(copy.deepcopy(item["response"]))
            items.append(projected)
        return {
            "schema_version": VERSION,
            "placement_id": placement_id,
            "package_id": package_id,
            "package_version": package_version,
            "package_digest": package_digest,
            "definition_digest": definition["definition_digest"],
            "practice_id": practice["practice_id"],
            "practice_version": practice["practice_version"],
            "title": practice["title"],
            "purpose": practice["purpose"],
            "instructions": practice["instructions"],
            "attempt_policy": copy.deepcopy(practice["attempt_policy"]),
            "source_references": copy.deepcopy(practice["source_references"]),
            "review_references": copy.deepcopy(practice["review_references"]),
            "items": items,
        }

    def validate_presentation(
        self,
        definition: Mapping[str, Any],
        presentation: Mapping[str, Any],
    ) -> None:
        leaked = _private_name(presentation)
        if leaked:
            reject(
                "assessment.practice.presentation_leak",
                leaked,
                "Practice presentation contains private Assessment fields.",
            )
        self._shape("presentation", presentation)
        expected = self.project(
            definition,
            placement_id=str(presentation["placement_id"]),
            package_id=str(presentation["package_id"]),
            package_version=str(presentation["package_version"]),
            package_digest=str(presentation["package_digest"]),
        )
        if presentation != expected:
            reject(
                "assessment.practice.stale_reference",
                "presentation",
                "Practice presentation does not match the exact definition.",
            )

    def validate_submission_chain(
        self,
        definition: Mapping[str, Any],
        presentation: Mapping[str, Any],
        submission: Mapping[str, Any],
        result: Mapping[str, Any],
        event: Mapping[str, Any],
    ) -> None:
        self.validate_presentation(definition, presentation)
        if submission.get("schema_version") != VERSION:
            reject(
                "assessment.practice.unsupported_version",
                "schema_version",
                "Practice submission version is unsupported.",
            )
        for kind, value in (
            ("submission", submission),
            ("result", result),
            ("completion-event", event),
        ):
            self._shape(kind, value)
        practice = definition["practice"]
        correlation = {
            "placement_id": presentation["placement_id"],
            "package_id": presentation["package_id"],
            "package_version": presentation["package_version"],
            "package_digest": presentation["package_digest"],
            "definition_digest": definition["definition_digest"],
            "practice_id": practice["practice_id"],
            "practice_version": practice["practice_version"],
            "attempt_policy_id": practice["attempt_policy"]["policy_id"],
            "attempt_policy_version": practice["attempt_policy"]["policy_version"],
        }
        for name, expected in correlation.items():
            if submission.get(name) != expected:
                reject(
                    "assessment.practice.stale_reference",
                    name,
                    "Practice submission does not match the exact definition.",
                )
        responses = submission["responses"]
        by_id = {response["item_id"]: response for response in responses}
        if len(by_id) != len(responses) or set(by_id) != {
            item["item_id"] for item in practice["items"]
        }:
            reject(
                "assessment.practice.invalid_response",
                "responses",
                "Practice responses must cover every item exactly once.",
            )
        expected_items: list[dict[str, Any]] = []
        review_ids: list[str] = []
        for index, item in enumerate(practice["items"]):
            response = by_id[item["item_id"]]
            expected_items.append(
                self._score_response(item, response, index, review_ids)
            )
        score = sum(item["score"] for item in expected_items)
        maximum = sum(item["max_score"] for item in expected_items)
        expected_result = {
            "schema_version": VERSION,
            "attempt_id": result["attempt_id"],
            "evidence_id": result["evidence_id"],
            "learner_id": result["learner_id"],
            "submission_id": submission["submission_id"],
            "request_fingerprint": submission_fingerprint(submission),
            **correlation,
            "score": score,
            "max_score": maximum,
            "outcome": "all_correct" if score == maximum else "review_needed",
            "review_reference_ids": review_ids,
            "item_results": expected_items,
            "submitted_at": result["submitted_at"],
        }
        if result != expected_result:
            reject(
                "assessment.practice.stale_reference",
                "result",
                "Practice result does not match deterministic scoring.",
            )
        leaked = _output_private_name(result)
        if leaked:
            reject(
                "assessment.practice.result_leak",
                leaked,
                "Practice result contains private Assessment fields.",
            )
        expected_event = {
            "schema_version": VERSION,
            "event_type": "assessment.practice.completed",
            "event_version": VERSION,
            "event_id": event["event_id"],
            "owner": "assessment",
            "occurred_at": result["submitted_at"],
            "idempotency_key": result["evidence_id"],
            "aggregate": {
                "aggregate_type": "practice_attempt",
                "aggregate_id": result["attempt_id"],
            },
            "source": {"evidence_id": result["evidence_id"]},
            "payload": {
                "learner_id": result["learner_id"],
                "submission_id": result["submission_id"],
                "placement_id": result["placement_id"],
                "package_id": result["package_id"],
                "package_version": result["package_version"],
                "package_digest": result["package_digest"],
                "definition_digest": result["definition_digest"],
                "practice_id": result["practice_id"],
                "practice_version": result["practice_version"],
                "attempt_policy_id": result["attempt_policy_id"],
                "attempt_policy_version": result["attempt_policy_version"],
                "score": result["score"],
                "max_score": result["max_score"],
                "outcome": result["outcome"],
                "item_scores": [
                    {
                        key: item[key]
                        for key in (
                            "item_id",
                            "item_version",
                            "item_type",
                            "scoring_policy_id",
                            "scoring_policy_version",
                            "score",
                            "max_score",
                        )
                    }
                    for item in result["item_results"]
                ],
                "completed_at": result["submitted_at"],
            },
        }
        if event != expected_event:
            reject(
                "assessment.practice.stale_reference",
                "event",
                "Practice completion event does not match its exact result.",
            )

    @staticmethod
    def _practice_correlation(
        definition: Mapping[str, Any], presentation: Mapping[str, Any]
    ) -> dict[str, Any]:
        practice = definition["practice"]
        return {
            "placement_id": presentation["placement_id"],
            "package_id": presentation["package_id"],
            "package_version": presentation["package_version"],
            "package_digest": presentation["package_digest"],
            "definition_digest": definition["definition_digest"],
            "practice_id": practice["practice_id"],
            "practice_version": practice["practice_version"],
            "attempt_policy_id": practice["attempt_policy"]["policy_id"],
            "attempt_policy_version": practice["attempt_policy"]["policy_version"],
        }

    def _validate_draft_responses(
        self,
        definition: Mapping[str, Any],
        responses: Sequence[Mapping[str, Any]],
    ) -> None:
        practice = definition["practice"]
        items = {item["item_id"]: item for item in practice["items"]}
        response_ids = [str(response.get("item_id", "")) for response in responses]
        if len(response_ids) != len(set(response_ids)):
            reject(
                "assessment.practice.invalid_draft",
                "responses",
                "A draft can contain each practice item at most once.",
            )
        for index, response in enumerate(responses):
            item = items.get(response.get("item_id"))
            if item is None:
                reject(
                    "assessment.practice.invalid_draft",
                    f"responses.{index}.item_id",
                    "A draft response must reference an item in the exact definition.",
                )
            self._score_response(item, response, index, [])

    def validate_draft_save(
        self,
        definition: Mapping[str, Any],
        presentation: Mapping[str, Any],
        draft_save: Mapping[str, Any],
    ) -> None:
        self.validate_presentation(definition, presentation)
        self._shape("draft-save", draft_save)
        for name, expected in self._practice_correlation(
            definition, presentation
        ).items():
            if draft_save.get(name) != expected:
                reject(
                    "assessment.practice.stale_reference",
                    name,
                    "Practice draft does not match the exact definition.",
                )
        self._validate_draft_responses(definition, draft_save["responses"])

    def validate_draft(
        self,
        definition: Mapping[str, Any],
        presentation: Mapping[str, Any],
        draft: Mapping[str, Any],
    ) -> None:
        self.validate_presentation(definition, presentation)
        self._shape("draft", draft)
        for name, expected in self._practice_correlation(
            definition, presentation
        ).items():
            if draft.get(name) != expected:
                reject(
                    "assessment.practice.stale_reference",
                    name,
                    "Practice draft does not match the exact definition.",
                )
        self._validate_draft_responses(definition, draft["responses"])
        if draft_response_fingerprint(draft["responses"]) != draft.get(
            "response_fingerprint"
        ):
            reject(
                "assessment.practice.invalid_draft",
                "response_fingerprint",
                "Practice draft fingerprint does not match its response snapshot.",
            )

    def validate_retry_state(
        self,
        definition: Mapping[str, Any],
        presentation: Mapping[str, Any],
        retry_state: Mapping[str, Any],
    ) -> None:
        self.validate_presentation(definition, presentation)
        self._shape("retry-state", retry_state)
        for name, expected in self._practice_correlation(
            definition, presentation
        ).items():
            if retry_state.get(name) != expected:
                reject(
                    "assessment.practice.stale_reference",
                    name,
                    "Practice retry state does not match the exact definition.",
                )
        declared_maximum = definition["practice"]["attempt_policy"]["max_attempts"]
        used = retry_state["attempts_used"]
        remaining = declared_maximum - used
        expected_can_retry = remaining > 0
        if (
            retry_state["max_attempts"] != declared_maximum
            or used > declared_maximum
            or retry_state["attempts_remaining"] != max(remaining, 0)
            or retry_state["can_retry"] is not expected_can_retry
            or retry_state["state"]
            != ("available" if expected_can_retry else "exhausted")
        ):
            reject(
                "assessment.practice.invalid_retry_state",
                "retry_state",
                "Practice retry state contradicts the exact attempt policy.",
            )

    def _score_response(
        self,
        item: Mapping[str, Any],
        response: Mapping[str, Any],
        index: int,
        review_ids: list[str],
    ) -> dict[str, Any]:
        policy = item["scoring_policy"]
        expected = {
            "item_version": item["item_version"],
            "item_type": item["item_type"],
            "scoring_policy_id": policy["policy_id"],
            "scoring_policy_version": policy["policy_version"],
        }
        if any(response.get(name) != value for name, value in expected.items()):
            reject(
                "assessment.practice.invalid_response",
                f"responses.{index}",
                "Practice response type or version does not match its item.",
            )
        item_type = item["item_type"]
        if item_type == "single_select":
            selected = response["selected_option_id"]
            declared = {option["option_id"] for option in item["options"]}
            if selected not in declared:
                reject(
                    "assessment.practice.invalid_response",
                    f"responses.{index}",
                    "Selected option is not declared by the item.",
                )
            correct = selected == item["correct_option_id"]
            submitted = {"selected_option_id": selected}
        elif item_type == "multiple_select":
            selected_values = response["selected_option_ids"]
            declared = {option["option_id"] for option in item["options"]}
            if not set(selected_values).issubset(declared):
                reject(
                    "assessment.practice.invalid_response",
                    f"responses.{index}",
                    "Selected options are not declared by the item.",
                )
            correct = set(selected_values) == set(item["correct_option_ids"])
            submitted = {"selected_option_ids": copy.deepcopy(selected_values)}
        else:
            entered = response["entered_value"]
            parsed = self._response_decimal(
                entered,
                item["response"]["scale"],
                item["response"]["allow_negative"],
                index,
            )
            answer = item["answer"]
            if answer["mode"] == "exact":
                correct = parsed == Decimal(answer["value"])
            else:
                correct = Decimal(answer["lower"]) <= parsed <= Decimal(
                    answer["upper"]
                )
            submitted = {"entered_value": entered}
        feedback = copy.deepcopy(item["feedback"]["correct" if correct else "incorrect"])
        for reference_id in feedback["review_reference_ids"]:
            if reference_id not in review_ids:
                review_ids.append(reference_id)
        return {
            "item_id": item["item_id"],
            **expected,
            **submitted,
            "score": 1 if correct else 0,
            "max_score": policy["max_score"],
            "correct": correct,
            "feedback": feedback,
        }

    @staticmethod
    def _response_decimal(
        value: str, scale: int, allow_negative: bool, index: int
    ) -> Decimal:
        match = DECIMAL_RE.fullmatch(value)
        if match is None or len(match.group(2) or "") != scale:
            reject(
                "assessment.practice.invalid_response",
                f"responses.{index}",
                "Numeric response does not match the declared fixed scale.",
            )
        parsed = Decimal(value)
        if value.startswith("-0") and parsed == 0:
            reject(
                "assessment.practice.invalid_response",
                f"responses.{index}",
                "Numeric response is not canonical.",
            )
        if not allow_negative and parsed < 0:
            reject(
                "assessment.practice.invalid_response",
                f"responses.{index}",
                "Negative response is not allowed.",
            )
        return parsed


def _output_private_name(value: object) -> str | None:
    private_names = {"answer", "correct_option_id", "correct_option_ids"}
    if isinstance(value, Mapping):
        for key, nested in value.items():
            if key in private_names:
                return str(key)
            found = _output_private_name(nested)
            if found:
                return found
    elif isinstance(value, list):
        for nested in value:
            found = _output_private_name(nested)
            if found:
                return found
    return None


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=corpus_dir())
    arguments = parser.parse_args(argv)
    try:
        chain = approved_chain(arguments.corpus)
        definition = chain[0]
        PracticeContractValidator().validate_submission_chain(*chain)
    except (PracticeConformanceFailure, OSError, ValueError) as error:
        diagnostic = (
            error.as_dict()
            if isinstance(error, PracticeConformanceFailure)
            else PracticeConformanceFailure(
                "assessment.practice.internal_error",
                "practice",
                "Practice conformance could not complete.",
            ).as_dict()
        )
        print(json.dumps({"valid": False, "diagnostic": diagnostic}, sort_keys=True))
        return 1
    print(
        json.dumps(
            {
                "valid": True,
                "practice_id": definition["practice"]["practice_id"],
                "definition_digest": definition["definition_digest"],
                "item_types": [
                    item["item_type"] for item in definition["practice"]["items"]
                ],
                "submission_fingerprint": chain[3]["request_fingerprint"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

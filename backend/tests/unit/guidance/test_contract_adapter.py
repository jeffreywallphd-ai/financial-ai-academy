from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from financial_ai_academy.modules.guidance.adapters import (
    search_page_payload,
    search_request_from_mapping,
    search_request_payload,
    topic_from_mapping,
)
from financial_ai_academy.modules.guidance.domain import (
    GuidanceError,
    PlatformHelpCorpus,
    topic_payload,
)


CORPUS = (
    Path(__file__).resolve().parents[4]
    / "contracts/compatibility/platform-help/v1/approved"
)


def approved_records():
    return tuple(
        json.loads((CORPUS / name).read_text(encoding="utf-8"))
        for name in ("topic.json", "search-request.json", "search-page.json")
    )


def test_contract_adapter_round_trips_exact_topic_and_search_records() -> None:
    topic_value, request_value, page_value = approved_records()
    topic = topic_from_mapping(topic_value)
    request = search_request_from_mapping(request_value)
    page = PlatformHelpCorpus((topic,)).search(request)
    assert topic_payload(topic) == topic_value
    assert search_request_payload(request) == request_value
    assert search_page_payload(page) == page_value


@pytest.mark.parametrize(
    "path, value",
    [
        (("repository_path",), "private/path.md"),
        (("source_references", 0, "approval"), "approved-by-someone"),
        (("body", 0, "html"), "<script>active()</script>"),
    ],
)
def test_contract_adapter_rejects_unknown_private_or_active_fields(
    path: tuple[object, ...],
    value: object,
) -> None:
    topic_value, _, _ = approved_records()
    target = copy.deepcopy(topic_value)
    current = target
    for part in path[:-1]:
        current = current[part]
    current[path[-1]] = value
    with pytest.raises(GuidanceError) as captured:
        topic_from_mapping(target)
    assert value not in str(captured.value)


def test_adapter_failures_do_not_echo_source_payload() -> None:
    topic_value, _, _ = approved_records()
    target = copy.deepcopy(topic_value)
    target["publication"]["updated_at"] = "private-invalid-time"
    with pytest.raises(GuidanceError) as captured:
        topic_from_mapping(target)
    assert "private-invalid-time" not in str(captured.value)
    assert "C:/" not in str(captured.value)


def test_contract_shapes_contain_no_forbidden_field_names() -> None:
    topic, request, page = approved_records()
    text = json.dumps([topic, request, page], sort_keys=True).casefold()
    for forbidden in (
        "repository_path",
        "absolute_path",
        "reviewer",
        "approval",
        "prompt",
        "learner_id",
        "provider_payload",
        "raw_html",
        "external_url",
    ):
        assert forbidden not in text

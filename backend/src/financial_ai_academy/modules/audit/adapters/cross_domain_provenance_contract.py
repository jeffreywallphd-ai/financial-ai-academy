"""Closed mapping boundary for cross-domain provenance v2 references."""

from __future__ import annotations

from datetime import datetime
import re
from typing import Mapping, Sequence

from ..domain.cross_domain_provenance import (
    AdministrativeActionIdentity,
    CrossDomainIdentity,
    CrossDomainOwnerModule,
    CrossDomainProducer,
    CrossDomainProfile,
    CrossDomainProvenanceEnvelope,
    CrossDomainProvenanceLabel,
    CrossDomainRelation,
    CrossDomainResourceKind,
    CrossDomainResourceReference,
    CrossDomainSource,
    CrossDomainValidationStatus,
    DatasetSnapshotIdentity,
    FinancialAccountIdentity,
    FinancialAnalysisIdentity,
    InvalidCrossDomainProvenance,
    MarketObservationIdentity,
    ModelExecutionIdentity,
    ModelVersionIdentity,
    ProjectSnapshotIdentity,
    RecommendationRecordIdentity,
    SimulationResultIdentity,
    cross_domain_envelope_payload,
    validate_cross_domain_envelope,
)


_TIMESTAMP = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-]\d{2}:\d{2})$"
)
_RESOURCE_FIELDS = {
    "profile",
    "owner_module",
    "resource_kind",
    "resource_id",
    "identity",
    "integrity_digest",
    "recorded_at",
    "provenance_label",
    "validation_status",
}


def cross_domain_envelope_from_mapping(
    value: Mapping[str, object],
) -> CrossDomainProvenanceEnvelope:
    item = _mapping(value, "envelope")
    _exact_keys(item, {"schema_version", "resource", "producer", "sources"}, "envelope")
    producer_value = _mapping(item["producer"], "producer")
    _exact_keys(producer_value, {"producer_id", "producer_version"}, "producer")
    sources: list[CrossDomainSource] = []
    for index, source_value in enumerate(_sequence(item["sources"], "sources")):
        source = _mapping(source_value, f"sources.{index}")
        _exact_keys(source, {"relation", "reference"}, f"sources.{index}")
        sources.append(
            CrossDomainSource(
                _relation(source["relation"], f"sources.{index}.relation"),
                _resource(
                    source["reference"], f"sources.{index}.reference"
                ),
            )
        )
    envelope = CrossDomainProvenanceEnvelope(
        schema_version=_string(item["schema_version"], "schema_version"),
        resource=_resource(item["resource"], "resource"),
        producer=CrossDomainProducer(
            _string(producer_value["producer_id"], "producer.producer_id"),
            _string(
                producer_value["producer_version"], "producer.producer_version"
            ),
        ),
        sources=tuple(sources),
    )
    return validate_cross_domain_envelope(envelope)


def cross_domain_envelope_to_mapping(
    value: CrossDomainProvenanceEnvelope,
) -> dict[str, object]:
    return cross_domain_envelope_payload(value)


def _resource(value: object, reference: str) -> CrossDomainResourceReference:
    item = _mapping(value, reference)
    _exact_keys(item, _RESOURCE_FIELDS, reference)
    profile = _profile(item["profile"], f"{reference}.profile")
    return CrossDomainResourceReference(
        profile=profile,
        owner_module=_owner(item["owner_module"], f"{reference}.owner_module"),
        resource_kind=_kind(item["resource_kind"], f"{reference}.resource_kind"),
        resource_id=_string(item["resource_id"], f"{reference}.resource_id"),
        identity=_identity(profile, item["identity"], f"{reference}.identity"),
        integrity_digest=_string(
            item["integrity_digest"], f"{reference}.integrity_digest"
        ),
        recorded_at=_datetime(item["recorded_at"], f"{reference}.recorded_at"),
        provenance_label=_label(
            item["provenance_label"], f"{reference}.provenance_label"
        ),
        validation_status=_status(
            item["validation_status"], f"{reference}.validation_status"
        ),
    )


def _identity(
    profile: CrossDomainProfile, value: object, reference: str
) -> CrossDomainIdentity:
    item = _mapping(value, reference)
    if profile is CrossDomainProfile.ADMINISTRATIVE_ACTION:
        _exact_keys(
            item,
            {"action_id", "policy_id", "policy_version", "action_at", "occurrence"},
            reference,
        )
        return AdministrativeActionIdentity(
            _string(item["action_id"], f"{reference}.action_id"),
            _string(item["policy_id"], f"{reference}.policy_id"),
            _string(item["policy_version"], f"{reference}.policy_version"),
            _datetime(item["action_at"], f"{reference}.action_at"),
            _integer(item["occurrence"], f"{reference}.occurrence"),
        )
    if profile is CrossDomainProfile.DATASET_SNAPSHOT:
        _exact_keys(item, {"dataset_id", "dataset_version"}, reference)
        return DatasetSnapshotIdentity(
            _string(item["dataset_id"], f"{reference}.dataset_id"),
            _string(item["dataset_version"], f"{reference}.dataset_version"),
        )
    if profile is CrossDomainProfile.FINANCIAL_RESULT:
        subject_kind = _string(item.get("subject_kind"), f"{reference}.subject_kind")
        common = {
            "subject_kind",
            "as_of",
            "method_id",
            "method_version",
            "source_set_digest",
        }
        if subject_kind == "analysis":
            _exact_keys(item, common | {"analysis_id"}, reference)
            return FinancialAnalysisIdentity(
                analysis_id=_string(item["analysis_id"], f"{reference}.analysis_id"),
                as_of=_datetime(item["as_of"], f"{reference}.as_of"),
                method_id=_string(item["method_id"], f"{reference}.method_id"),
                method_version=_string(
                    item["method_version"], f"{reference}.method_version"
                ),
                source_set_digest=_string(
                    item["source_set_digest"], f"{reference}.source_set_digest"
                ),
            )
        if subject_kind == "account":
            _exact_keys(item, common | {"account_id"}, reference)
            return FinancialAccountIdentity(
                account_id=_string(item["account_id"], f"{reference}.account_id"),
                as_of=_datetime(item["as_of"], f"{reference}.as_of"),
                method_id=_string(item["method_id"], f"{reference}.method_id"),
                method_version=_string(
                    item["method_version"], f"{reference}.method_version"
                ),
                source_set_digest=_string(
                    item["source_set_digest"], f"{reference}.source_set_digest"
                ),
            )
        raise InvalidCrossDomainProvenance(f"{reference}.subject_kind")
    if profile is CrossDomainProfile.MARKET_OBSERVATION:
        _exact_keys(
            item,
            {
                "instrument_id",
                "observed_at",
                "method_id",
                "method_version",
                "source_set_digest",
            },
            reference,
        )
        return MarketObservationIdentity(
            _string(item["instrument_id"], f"{reference}.instrument_id"),
            _datetime(item["observed_at"], f"{reference}.observed_at"),
            _string(item["method_id"], f"{reference}.method_id"),
            _string(item["method_version"], f"{reference}.method_version"),
            _string(
                item["source_set_digest"], f"{reference}.source_set_digest"
            ),
        )
    if profile is CrossDomainProfile.MODEL_EXECUTION:
        _exact_keys(
            item,
            {"execution_id", "model_id", "model_version", "occurrence"},
            reference,
        )
        return ModelExecutionIdentity(
            _string(item["execution_id"], f"{reference}.execution_id"),
            _string(item["model_id"], f"{reference}.model_id"),
            _string(item["model_version"], f"{reference}.model_version"),
            _integer(item["occurrence"], f"{reference}.occurrence"),
        )
    if profile is CrossDomainProfile.MODEL_VERSION:
        _exact_keys(item, {"model_id", "model_version"}, reference)
        return ModelVersionIdentity(
            _string(item["model_id"], f"{reference}.model_id"),
            _string(item["model_version"], f"{reference}.model_version"),
        )
    if profile is CrossDomainProfile.PROJECT_SNAPSHOT:
        _exact_keys(
            item,
            {"project_id", "snapshot_id", "project_revision", "workspace_revision"},
            reference,
        )
        return ProjectSnapshotIdentity(
            _string(item["project_id"], f"{reference}.project_id"),
            _string(item["snapshot_id"], f"{reference}.snapshot_id"),
            _integer(item["project_revision"], f"{reference}.project_revision"),
            _integer(
                item["workspace_revision"], f"{reference}.workspace_revision"
            ),
        )
    if profile is CrossDomainProfile.RECOMMENDATION_RECORD:
        _exact_keys(
            item,
            {
                "recommendation_id",
                "policy_id",
                "policy_version",
                "decision_at",
                "occurrence",
            },
            reference,
        )
        return RecommendationRecordIdentity(
            _string(
                item["recommendation_id"], f"{reference}.recommendation_id"
            ),
            _string(item["policy_id"], f"{reference}.policy_id"),
            _string(item["policy_version"], f"{reference}.policy_version"),
            _datetime(item["decision_at"], f"{reference}.decision_at"),
            _integer(item["occurrence"], f"{reference}.occurrence"),
        )
    if profile is CrossDomainProfile.SIMULATION_RESULT:
        _exact_keys(
            item,
            {"simulation_id", "method_id", "method_version", "as_of", "occurrence"},
            reference,
        )
        return SimulationResultIdentity(
            _string(item["simulation_id"], f"{reference}.simulation_id"),
            _string(item["method_id"], f"{reference}.method_id"),
            _string(item["method_version"], f"{reference}.method_version"),
            _datetime(item["as_of"], f"{reference}.as_of"),
            _integer(item["occurrence"], f"{reference}.occurrence"),
        )
    raise InvalidCrossDomainProvenance(f"{reference}.profile")


def _mapping(value: object, reference: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping) or not all(
        isinstance(key, str) for key in value
    ):
        raise InvalidCrossDomainProvenance(reference)
    return value


def _sequence(value: object, reference: str) -> Sequence[object]:
    if not isinstance(value, (list, tuple)):
        raise InvalidCrossDomainProvenance(reference)
    return value


def _exact_keys(
    value: Mapping[str, object], expected: set[str], reference: str
) -> None:
    if set(value) != expected:
        raise InvalidCrossDomainProvenance(reference)


def _string(value: object, reference: str) -> str:
    if not isinstance(value, str):
        raise InvalidCrossDomainProvenance(reference)
    return value


def _integer(value: object, reference: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise InvalidCrossDomainProvenance(reference)
    return value


def _datetime(value: object, reference: str) -> datetime:
    if not isinstance(value, str) or _TIMESTAMP.fullmatch(value) is None:
        raise InvalidCrossDomainProvenance(reference)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise InvalidCrossDomainProvenance(reference) from error
    if parsed.tzinfo is None:
        raise InvalidCrossDomainProvenance(reference)
    return parsed


def _profile(value: object, reference: str) -> CrossDomainProfile:
    try:
        return CrossDomainProfile(_string(value, reference))
    except ValueError as error:
        raise InvalidCrossDomainProvenance(reference) from error


def _owner(value: object, reference: str) -> CrossDomainOwnerModule:
    try:
        return CrossDomainOwnerModule(_string(value, reference))
    except ValueError as error:
        raise InvalidCrossDomainProvenance(reference) from error


def _kind(value: object, reference: str) -> CrossDomainResourceKind:
    try:
        return CrossDomainResourceKind(_string(value, reference))
    except ValueError as error:
        raise InvalidCrossDomainProvenance(reference) from error


def _label(value: object, reference: str) -> CrossDomainProvenanceLabel:
    try:
        return CrossDomainProvenanceLabel(_string(value, reference))
    except ValueError as error:
        raise InvalidCrossDomainProvenance(reference) from error


def _relation(value: object, reference: str) -> CrossDomainRelation:
    try:
        return CrossDomainRelation(_string(value, reference))
    except ValueError as error:
        raise InvalidCrossDomainProvenance(reference) from error


def _status(value: object, reference: str) -> CrossDomainValidationStatus:
    try:
        return CrossDomainValidationStatus(_string(value, reference))
    except ValueError as error:
        raise InvalidCrossDomainProvenance(reference) from error


__all__ = [
    "cross_domain_envelope_from_mapping",
    "cross_domain_envelope_to_mapping",
]

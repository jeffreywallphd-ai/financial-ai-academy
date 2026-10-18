"""Pure values for closed cross-domain provenance owner references."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from enum import StrEnum
from hashlib import sha256
import json
import re
from typing import TypeAlias
import unicodedata


_VERSION = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._+-]{0,79}$")
_DIGEST = re.compile(r"^[a-f0-9]{64}$")


class InvalidCrossDomainProvenance(ValueError):
    """Bounded failure for inconsistent v2 owner-reference meaning."""

    def __init__(self, reference: str) -> None:
        super().__init__("Cross-domain provenance record is inconsistent.")
        self.reference = str(reference).replace("\r", " ").replace("\n", " ")[:120]


class CrossDomainOwnerModule(StrEnum):
    ADAPTATION = "adaptation"
    AI_ORCHESTRATION = "ai_orchestration"
    AUDIT = "audit"
    MARKET_DATA = "market_data"
    PORTFOLIO = "portfolio"
    PROJECT = "project"


class CrossDomainProfile(StrEnum):
    ADMINISTRATIVE_ACTION = "administrative_action"
    DATASET_SNAPSHOT = "dataset_snapshot"
    FINANCIAL_RESULT = "financial_result"
    MARKET_OBSERVATION = "market_observation"
    MODEL_EXECUTION = "model_execution"
    MODEL_VERSION = "model_version"
    PROJECT_SNAPSHOT = "project_snapshot"
    RECOMMENDATION_RECORD = "recommendation_record"
    SIMULATION_RESULT = "simulation_result"


class CrossDomainResourceKind(StrEnum):
    ADMINISTRATIVE_ACTION = "administrative_action"
    DATASET_SNAPSHOT = "dataset_snapshot"
    FINANCIAL_RESULT = "financial_result"
    MARKET_OBSERVATION = "market_observation"
    MODEL_EXECUTION = "model_execution"
    MODEL_VERSION = "model_version"
    PROJECT_SNAPSHOT = "project_snapshot"
    RECOMMENDATION_RECORD = "recommendation_record"
    SIMULATION_RESULT = "simulation_result"


class CrossDomainProvenanceLabel(StrEnum):
    OBSERVED = "observed"
    CALCULATED = "calculated"
    SIMULATED = "simulated"
    PREDICTED = "predicted"
    GENERATED = "generated"
    ADMINISTRATIVE = "administrative"


class CrossDomainRelation(StrEnum):
    DERIVED_FROM = "derived_from"
    CALCULATED_FROM = "calculated_from"
    USED_DATASET = "used_dataset"
    USED_MODEL = "used_model"
    EXECUTED_AS = "executed_as"
    SIMULATED_FROM = "simulated_from"
    RECOMMENDED_FROM = "recommended_from"
    GOVERNED_BY = "governed_by"
    RECORDED_AS = "recorded_as"


class CrossDomainValidationStatus(StrEnum):
    VALIDATED = "validated"
    INCOMPLETE = "incomplete"


@dataclass(frozen=True, slots=True)
class AdministrativeActionIdentity:
    action_id: str
    policy_id: str
    policy_version: str
    action_at: datetime
    occurrence: int


@dataclass(frozen=True, slots=True)
class DatasetSnapshotIdentity:
    dataset_id: str
    dataset_version: str


@dataclass(frozen=True, slots=True)
class FinancialAnalysisIdentity:
    analysis_id: str
    as_of: datetime
    method_id: str
    method_version: str
    source_set_digest: str
    subject_kind: str = "analysis"


@dataclass(frozen=True, slots=True)
class FinancialAccountIdentity:
    account_id: str
    as_of: datetime
    method_id: str
    method_version: str
    source_set_digest: str
    subject_kind: str = "account"


@dataclass(frozen=True, slots=True)
class MarketObservationIdentity:
    instrument_id: str
    observed_at: datetime
    method_id: str
    method_version: str
    source_set_digest: str


@dataclass(frozen=True, slots=True)
class ModelExecutionIdentity:
    execution_id: str
    model_id: str
    model_version: str
    occurrence: int


@dataclass(frozen=True, slots=True)
class ModelVersionIdentity:
    model_id: str
    model_version: str


@dataclass(frozen=True, slots=True)
class ProjectSnapshotIdentity:
    project_id: str
    snapshot_id: str
    project_revision: int
    workspace_revision: int


@dataclass(frozen=True, slots=True)
class RecommendationRecordIdentity:
    recommendation_id: str
    policy_id: str
    policy_version: str
    decision_at: datetime
    occurrence: int


@dataclass(frozen=True, slots=True)
class SimulationResultIdentity:
    simulation_id: str
    method_id: str
    method_version: str
    as_of: datetime
    occurrence: int


CrossDomainIdentity: TypeAlias = (
    AdministrativeActionIdentity
    | DatasetSnapshotIdentity
    | FinancialAnalysisIdentity
    | FinancialAccountIdentity
    | MarketObservationIdentity
    | ModelExecutionIdentity
    | ModelVersionIdentity
    | ProjectSnapshotIdentity
    | RecommendationRecordIdentity
    | SimulationResultIdentity
)


@dataclass(frozen=True, slots=True)
class CrossDomainResourceReference:
    profile: CrossDomainProfile
    owner_module: CrossDomainOwnerModule
    resource_kind: CrossDomainResourceKind
    resource_id: str
    identity: CrossDomainIdentity
    integrity_digest: str
    recorded_at: datetime
    provenance_label: CrossDomainProvenanceLabel
    validation_status: CrossDomainValidationStatus


@dataclass(frozen=True, slots=True)
class CrossDomainProducer:
    producer_id: str
    producer_version: str


@dataclass(frozen=True, slots=True)
class CrossDomainSource:
    relation: CrossDomainRelation
    reference: CrossDomainResourceReference


@dataclass(frozen=True, slots=True)
class CrossDomainProvenanceEnvelope:
    schema_version: str
    resource: CrossDomainResourceReference
    producer: CrossDomainProducer
    sources: tuple[CrossDomainSource, ...]


@dataclass(frozen=True, slots=True)
class _ProfileRule:
    owner: CrossDomainOwnerModule
    kind: CrossDomainResourceKind
    identity_types: tuple[type[object], ...]
    labels: frozenset[CrossDomainProvenanceLabel]
    relations: frozenset[CrossDomainRelation]


_PROFILE_RULES = {
    CrossDomainProfile.ADMINISTRATIVE_ACTION: _ProfileRule(
        CrossDomainOwnerModule.AUDIT,
        CrossDomainResourceKind.ADMINISTRATIVE_ACTION,
        (AdministrativeActionIdentity,),
        frozenset({CrossDomainProvenanceLabel.ADMINISTRATIVE}),
        frozenset(
            {
                CrossDomainRelation.DERIVED_FROM,
                CrossDomainRelation.GOVERNED_BY,
                CrossDomainRelation.RECORDED_AS,
            }
        ),
    ),
    CrossDomainProfile.DATASET_SNAPSHOT: _ProfileRule(
        CrossDomainOwnerModule.AI_ORCHESTRATION,
        CrossDomainResourceKind.DATASET_SNAPSHOT,
        (DatasetSnapshotIdentity,),
        frozenset(
            {
                CrossDomainProvenanceLabel.OBSERVED,
                CrossDomainProvenanceLabel.GENERATED,
            }
        ),
        frozenset(
            {
                CrossDomainRelation.DERIVED_FROM,
                CrossDomainRelation.GOVERNED_BY,
                CrossDomainRelation.RECORDED_AS,
            }
        ),
    ),
    CrossDomainProfile.FINANCIAL_RESULT: _ProfileRule(
        CrossDomainOwnerModule.PORTFOLIO,
        CrossDomainResourceKind.FINANCIAL_RESULT,
        (FinancialAnalysisIdentity, FinancialAccountIdentity),
        frozenset({CrossDomainProvenanceLabel.CALCULATED}),
        frozenset(
            {
                CrossDomainRelation.CALCULATED_FROM,
                CrossDomainRelation.GOVERNED_BY,
                CrossDomainRelation.RECORDED_AS,
            }
        ),
    ),
    CrossDomainProfile.MARKET_OBSERVATION: _ProfileRule(
        CrossDomainOwnerModule.MARKET_DATA,
        CrossDomainResourceKind.MARKET_OBSERVATION,
        (MarketObservationIdentity,),
        frozenset({CrossDomainProvenanceLabel.OBSERVED}),
        frozenset(
            {
                CrossDomainRelation.DERIVED_FROM,
                CrossDomainRelation.GOVERNED_BY,
                CrossDomainRelation.RECORDED_AS,
            }
        ),
    ),
    CrossDomainProfile.MODEL_EXECUTION: _ProfileRule(
        CrossDomainOwnerModule.AI_ORCHESTRATION,
        CrossDomainResourceKind.MODEL_EXECUTION,
        (ModelExecutionIdentity,),
        frozenset(
            {
                CrossDomainProvenanceLabel.PREDICTED,
                CrossDomainProvenanceLabel.GENERATED,
            }
        ),
        frozenset(
            {
                CrossDomainRelation.EXECUTED_AS,
                CrossDomainRelation.GOVERNED_BY,
                CrossDomainRelation.USED_DATASET,
                CrossDomainRelation.USED_MODEL,
            }
        ),
    ),
    CrossDomainProfile.MODEL_VERSION: _ProfileRule(
        CrossDomainOwnerModule.AI_ORCHESTRATION,
        CrossDomainResourceKind.MODEL_VERSION,
        (ModelVersionIdentity,),
        frozenset({CrossDomainProvenanceLabel.GENERATED}),
        frozenset(
            {
                CrossDomainRelation.DERIVED_FROM,
                CrossDomainRelation.GOVERNED_BY,
                CrossDomainRelation.USED_DATASET,
            }
        ),
    ),
    CrossDomainProfile.PROJECT_SNAPSHOT: _ProfileRule(
        CrossDomainOwnerModule.PROJECT,
        CrossDomainResourceKind.PROJECT_SNAPSHOT,
        (ProjectSnapshotIdentity,),
        frozenset({CrossDomainProvenanceLabel.OBSERVED}),
        frozenset(
            {
                CrossDomainRelation.DERIVED_FROM,
                CrossDomainRelation.GOVERNED_BY,
                CrossDomainRelation.RECORDED_AS,
            }
        ),
    ),
    CrossDomainProfile.RECOMMENDATION_RECORD: _ProfileRule(
        CrossDomainOwnerModule.ADAPTATION,
        CrossDomainResourceKind.RECOMMENDATION_RECORD,
        (RecommendationRecordIdentity,),
        frozenset(
            {
                CrossDomainProvenanceLabel.CALCULATED,
                CrossDomainProvenanceLabel.PREDICTED,
                CrossDomainProvenanceLabel.GENERATED,
            }
        ),
        frozenset(
            {
                CrossDomainRelation.GOVERNED_BY,
                CrossDomainRelation.RECOMMENDED_FROM,
                CrossDomainRelation.USED_MODEL,
            }
        ),
    ),
    CrossDomainProfile.SIMULATION_RESULT: _ProfileRule(
        CrossDomainOwnerModule.PORTFOLIO,
        CrossDomainResourceKind.SIMULATION_RESULT,
        (SimulationResultIdentity,),
        frozenset({CrossDomainProvenanceLabel.SIMULATED}),
        frozenset(
            {
                CrossDomainRelation.CALCULATED_FROM,
                CrossDomainRelation.GOVERNED_BY,
                CrossDomainRelation.SIMULATED_FROM,
                CrossDomainRelation.USED_DATASET,
            }
        ),
    ),
}


def validate_cross_domain_envelope(
    value: CrossDomainProvenanceEnvelope,
) -> CrossDomainProvenanceEnvelope:
    if not isinstance(value, CrossDomainProvenanceEnvelope):
        raise InvalidCrossDomainProvenance("envelope")
    if value.schema_version != "2.0.0":
        raise InvalidCrossDomainProvenance("schema_version")
    resource = _validate_resource(value.resource, "resource")
    producer = _validate_producer(value.producer)
    if not isinstance(value.sources, tuple) or len(value.sources) > 20:
        raise InvalidCrossDomainProvenance("sources")
    rule = _PROFILE_RULES[resource.profile]
    seen: dict[bytes, bytes] = {
        _identity_key(resource): _canonical_bytes(_resource_payload(resource))
    }
    sources: list[CrossDomainSource] = []
    for index, source in enumerate(value.sources):
        if not isinstance(source, CrossDomainSource):
            raise InvalidCrossDomainProvenance(f"sources.{index}")
        if not isinstance(source.relation, CrossDomainRelation):
            raise InvalidCrossDomainProvenance(f"sources.{index}.relation")
        if source.relation not in rule.relations:
            raise InvalidCrossDomainProvenance(f"sources.{index}.relation")
        reference = _validate_resource(
            source.reference, f"sources.{index}.reference"
        )
        identity_key = _identity_key(reference)
        meaning = _canonical_bytes(_resource_payload(reference))
        if identity_key in seen:
            suffix = "identity_conflict" if seen[identity_key] != meaning else "duplicate"
            raise InvalidCrossDomainProvenance(f"sources.{index}.{suffix}")
        seen[identity_key] = meaning
        sources.append(CrossDomainSource(source.relation, reference))
    normalized = replace(
        value,
        resource=resource,
        producer=producer,
        sources=tuple(
            sorted(
                sources,
                key=lambda item: _canonical_bytes(_source_payload(item)),
            )
        ),
    )
    return normalized


def cross_domain_envelope_payload(
    value: CrossDomainProvenanceEnvelope,
) -> dict[str, object]:
    admitted = validate_cross_domain_envelope(value)
    return {
        "schema_version": admitted.schema_version,
        "resource": _resource_payload(admitted.resource),
        "producer": {
            "producer_id": admitted.producer.producer_id,
            "producer_version": admitted.producer.producer_version,
        },
        "sources": [_source_payload(source) for source in admitted.sources],
    }


def cross_domain_envelope_digest(value: CrossDomainProvenanceEnvelope) -> str:
    return sha256(_canonical_bytes(cross_domain_envelope_payload(value))).hexdigest()


def market_observation_resource_id(identity: MarketObservationIdentity) -> str:
    normalized = _validate_identity(identity, "identity")
    return sha256(_canonical_bytes(_identity_payload(normalized))).hexdigest()


def _validate_producer(value: CrossDomainProducer) -> CrossDomainProducer:
    if not isinstance(value, CrossDomainProducer):
        raise InvalidCrossDomainProvenance("producer")
    _identifier(value.producer_id, "producer.producer_id")
    _version(value.producer_version, "producer.producer_version")
    return value


def _validate_resource(
    value: CrossDomainResourceReference, reference: str
) -> CrossDomainResourceReference:
    if not isinstance(value, CrossDomainResourceReference):
        raise InvalidCrossDomainProvenance(reference)
    if not isinstance(value.profile, CrossDomainProfile):
        raise InvalidCrossDomainProvenance(f"{reference}.profile")
    rule = _PROFILE_RULES[value.profile]
    if value.owner_module is not rule.owner or value.resource_kind is not rule.kind:
        raise InvalidCrossDomainProvenance(f"{reference}.owner_kind")
    if not isinstance(value.identity, rule.identity_types):
        raise InvalidCrossDomainProvenance(f"{reference}.identity")
    identity = _validate_identity(value.identity, f"{reference}.identity")
    expected_id = _identity_resource_id(identity)
    _identifier(value.resource_id, f"{reference}.resource_id")
    if value.resource_id != expected_id:
        raise InvalidCrossDomainProvenance(f"{reference}.resource_id")
    _digest(value.integrity_digest, f"{reference}.integrity_digest")
    recorded_at = _aware_time(value.recorded_at, f"{reference}.recorded_at")
    if (
        not isinstance(value.provenance_label, CrossDomainProvenanceLabel)
        or value.provenance_label not in rule.labels
    ):
        raise InvalidCrossDomainProvenance(f"{reference}.provenance_label")
    if not isinstance(value.validation_status, CrossDomainValidationStatus):
        raise InvalidCrossDomainProvenance(f"{reference}.validation_status")
    return replace(value, identity=identity, recorded_at=recorded_at)


def _validate_identity(
    value: CrossDomainIdentity, reference: str
) -> CrossDomainIdentity:
    if isinstance(value, AdministrativeActionIdentity):
        _identifier(value.action_id, f"{reference}.action_id")
        _identifier(value.policy_id, f"{reference}.policy_id")
        _version(value.policy_version, f"{reference}.policy_version")
        _positive(value.occurrence, f"{reference}.occurrence")
        return replace(
            value, action_at=_aware_time(value.action_at, f"{reference}.action_at")
        )
    if isinstance(value, DatasetSnapshotIdentity):
        _identifier(value.dataset_id, f"{reference}.dataset_id")
        _version(value.dataset_version, f"{reference}.dataset_version")
        return value
    if isinstance(value, (FinancialAnalysisIdentity, FinancialAccountIdentity)):
        expected_kind = "analysis" if isinstance(value, FinancialAnalysisIdentity) else "account"
        if value.subject_kind != expected_kind:
            raise InvalidCrossDomainProvenance(f"{reference}.subject_kind")
        identifier = value.analysis_id if isinstance(value, FinancialAnalysisIdentity) else value.account_id
        _identifier(identifier, f"{reference}.{expected_kind}_id")
        _identifier(value.method_id, f"{reference}.method_id")
        _version(value.method_version, f"{reference}.method_version")
        _digest(value.source_set_digest, f"{reference}.source_set_digest")
        return replace(value, as_of=_aware_time(value.as_of, f"{reference}.as_of"))
    if isinstance(value, MarketObservationIdentity):
        _identifier(value.instrument_id, f"{reference}.instrument_id")
        _identifier(value.method_id, f"{reference}.method_id")
        _version(value.method_version, f"{reference}.method_version")
        _digest(value.source_set_digest, f"{reference}.source_set_digest")
        return replace(
            value,
            observed_at=_aware_time(value.observed_at, f"{reference}.observed_at"),
        )
    if isinstance(value, ModelExecutionIdentity):
        _identifier(value.execution_id, f"{reference}.execution_id")
        _identifier(value.model_id, f"{reference}.model_id")
        _version(value.model_version, f"{reference}.model_version")
        _positive(value.occurrence, f"{reference}.occurrence")
        return value
    if isinstance(value, ModelVersionIdentity):
        _identifier(value.model_id, f"{reference}.model_id")
        _version(value.model_version, f"{reference}.model_version")
        return value
    if isinstance(value, ProjectSnapshotIdentity):
        _identifier(value.project_id, f"{reference}.project_id")
        _identifier(value.snapshot_id, f"{reference}.snapshot_id")
        _positive(value.project_revision, f"{reference}.project_revision")
        _positive(value.workspace_revision, f"{reference}.workspace_revision")
        return value
    if isinstance(value, RecommendationRecordIdentity):
        _identifier(value.recommendation_id, f"{reference}.recommendation_id")
        _identifier(value.policy_id, f"{reference}.policy_id")
        _version(value.policy_version, f"{reference}.policy_version")
        _positive(value.occurrence, f"{reference}.occurrence")
        return replace(
            value,
            decision_at=_aware_time(value.decision_at, f"{reference}.decision_at"),
        )
    if isinstance(value, SimulationResultIdentity):
        _identifier(value.simulation_id, f"{reference}.simulation_id")
        _identifier(value.method_id, f"{reference}.method_id")
        _version(value.method_version, f"{reference}.method_version")
        _positive(value.occurrence, f"{reference}.occurrence")
        return replace(value, as_of=_aware_time(value.as_of, f"{reference}.as_of"))
    raise InvalidCrossDomainProvenance(reference)


def _identity_resource_id(value: CrossDomainIdentity) -> str:
    if isinstance(value, AdministrativeActionIdentity):
        return value.action_id
    if isinstance(value, DatasetSnapshotIdentity):
        return value.dataset_id
    if isinstance(value, FinancialAnalysisIdentity):
        return value.analysis_id
    if isinstance(value, FinancialAccountIdentity):
        return value.account_id
    if isinstance(value, MarketObservationIdentity):
        return sha256(_canonical_bytes(_identity_payload(value))).hexdigest()
    if isinstance(value, ModelExecutionIdentity):
        return value.execution_id
    if isinstance(value, ModelVersionIdentity):
        return value.model_id
    if isinstance(value, ProjectSnapshotIdentity):
        return value.snapshot_id
    if isinstance(value, RecommendationRecordIdentity):
        return value.recommendation_id
    if isinstance(value, SimulationResultIdentity):
        return value.simulation_id
    raise InvalidCrossDomainProvenance("identity")


def _identity_payload(value: CrossDomainIdentity) -> dict[str, object]:
    if isinstance(value, AdministrativeActionIdentity):
        return {
            "action_id": value.action_id,
            "policy_id": value.policy_id,
            "policy_version": value.policy_version,
            "action_at": _timestamp(value.action_at),
            "occurrence": value.occurrence,
        }
    if isinstance(value, DatasetSnapshotIdentity):
        return {"dataset_id": value.dataset_id, "dataset_version": value.dataset_version}
    if isinstance(value, FinancialAnalysisIdentity):
        return {
            "subject_kind": value.subject_kind,
            "analysis_id": value.analysis_id,
            "as_of": _timestamp(value.as_of),
            "method_id": value.method_id,
            "method_version": value.method_version,
            "source_set_digest": value.source_set_digest,
        }
    if isinstance(value, FinancialAccountIdentity):
        return {
            "subject_kind": value.subject_kind,
            "account_id": value.account_id,
            "as_of": _timestamp(value.as_of),
            "method_id": value.method_id,
            "method_version": value.method_version,
            "source_set_digest": value.source_set_digest,
        }
    if isinstance(value, MarketObservationIdentity):
        return {
            "instrument_id": value.instrument_id,
            "observed_at": _timestamp(value.observed_at),
            "method_id": value.method_id,
            "method_version": value.method_version,
            "source_set_digest": value.source_set_digest,
        }
    if isinstance(value, ModelExecutionIdentity):
        return {
            "execution_id": value.execution_id,
            "model_id": value.model_id,
            "model_version": value.model_version,
            "occurrence": value.occurrence,
        }
    if isinstance(value, ModelVersionIdentity):
        return {"model_id": value.model_id, "model_version": value.model_version}
    if isinstance(value, ProjectSnapshotIdentity):
        return {
            "project_id": value.project_id,
            "snapshot_id": value.snapshot_id,
            "project_revision": value.project_revision,
            "workspace_revision": value.workspace_revision,
        }
    if isinstance(value, RecommendationRecordIdentity):
        return {
            "recommendation_id": value.recommendation_id,
            "policy_id": value.policy_id,
            "policy_version": value.policy_version,
            "decision_at": _timestamp(value.decision_at),
            "occurrence": value.occurrence,
        }
    if isinstance(value, SimulationResultIdentity):
        return {
            "simulation_id": value.simulation_id,
            "method_id": value.method_id,
            "method_version": value.method_version,
            "as_of": _timestamp(value.as_of),
            "occurrence": value.occurrence,
        }
    raise InvalidCrossDomainProvenance("identity")


def _resource_payload(value: CrossDomainResourceReference) -> dict[str, object]:
    return {
        "profile": value.profile.value,
        "owner_module": value.owner_module.value,
        "resource_kind": value.resource_kind.value,
        "resource_id": value.resource_id,
        "identity": _identity_payload(value.identity),
        "integrity_digest": value.integrity_digest,
        "recorded_at": _timestamp(value.recorded_at),
        "provenance_label": value.provenance_label.value,
        "validation_status": value.validation_status.value,
    }


def _source_payload(value: CrossDomainSource) -> dict[str, object]:
    return {
        "relation": value.relation.value,
        "reference": _resource_payload(value.reference),
    }


def _identity_key(value: CrossDomainResourceReference) -> bytes:
    return _canonical_bytes(
        {"profile": value.profile.value, "identity": _identity_payload(value.identity)}
    )


def _identifier(value: object, reference: str) -> str:
    if (
        not isinstance(value, str)
        or not value
        or len(value) > 128
        or not value[0].isalnum()
        or any(
            character.isspace()
            or unicodedata.category(character).startswith("C")
            or character in "/\\?#"
            for character in value
        )
    ):
        raise InvalidCrossDomainProvenance(reference)
    return value


def _version(value: object, reference: str) -> str:
    if not isinstance(value, str) or _VERSION.fullmatch(value) is None:
        raise InvalidCrossDomainProvenance(reference)
    return value


def _digest(value: object, reference: str) -> str:
    if not isinstance(value, str) or _DIGEST.fullmatch(value) is None:
        raise InvalidCrossDomainProvenance(reference)
    return value


def _positive(value: object, reference: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise InvalidCrossDomainProvenance(reference)
    return value


def _aware_time(value: object, reference: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise InvalidCrossDomainProvenance(reference)
    return value.astimezone(timezone.utc)


def _timestamp(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


__all__ = [
    "AdministrativeActionIdentity",
    "CrossDomainIdentity",
    "CrossDomainOwnerModule",
    "CrossDomainProducer",
    "CrossDomainProfile",
    "CrossDomainProvenanceEnvelope",
    "CrossDomainProvenanceLabel",
    "CrossDomainRelation",
    "CrossDomainResourceKind",
    "CrossDomainResourceReference",
    "CrossDomainSource",
    "CrossDomainValidationStatus",
    "DatasetSnapshotIdentity",
    "FinancialAccountIdentity",
    "FinancialAnalysisIdentity",
    "InvalidCrossDomainProvenance",
    "MarketObservationIdentity",
    "ModelExecutionIdentity",
    "ModelVersionIdentity",
    "ProjectSnapshotIdentity",
    "RecommendationRecordIdentity",
    "SimulationResultIdentity",
    "cross_domain_envelope_digest",
    "cross_domain_envelope_payload",
    "market_observation_resource_id",
    "validate_cross_domain_envelope",
]

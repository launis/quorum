"""Unit tests verifying all Polyfactory model factories build valid models."""

from __future__ import annotations

import re

import pytest
from pydantic import ValidationError

from backend_v2.models.core_base import OPAQUE_STRIPE_ID_REGEX
from backend_v2.models.domain.report_artifact import ReportArtifact
from backend_v2.models.domain.scoring import StepPanelDTO
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.causal_discovery import CausalEdgeDTO, CausalGraphPayloadDTO
from backend_v2.tests.factories.model_factories import (
    CausalGraphPayloadDTOFactory,
    CausalNodeDTOFactory,
    ExecutionRecordFactory,
    ExecutionStepFactory,
    GlobalContextVarsDTOFactory,
    I18nTextFactory,
    MatrixPromptBlockFactory,
    OutputProfileFactory,
    ReportArtifactFactory,
    StepPanelDTOFactory,
    SystemRulePromptBlockFactory,
    WorkflowFactory,
)

__all__ = [
    "ALL_FACTORIES",
    "RegisteredFactoryType",
    "test_polyfactory_build_succeeds",
    "test_polyfactory_causal_graph_referential_integrity_error",
    "test_polyfactory_invalid_extra_field_error",
    "test_polyfactory_invalid_id_error",
    "test_polyfactory_step_panel_empty_payload_error",
]

type RegisteredFactoryType = (
    type[I18nTextFactory]
    | type[WorkflowFactory]
    | type[SystemRulePromptBlockFactory]
    | type[OutputProfileFactory]
    | type[MatrixPromptBlockFactory]
    | type[ExecutionStepFactory]
    | type[ExecutionRecordFactory]
    | type[ReportArtifactFactory]
    | type[StepPanelDTOFactory]
    | type[GlobalContextVarsDTOFactory]
    | type[CausalNodeDTOFactory]
    | type[CausalGraphPayloadDTOFactory]
)

ALL_FACTORIES: tuple[RegisteredFactoryType, ...] = (
    I18nTextFactory,
    WorkflowFactory,
    SystemRulePromptBlockFactory,
    OutputProfileFactory,
    MatrixPromptBlockFactory,
    ExecutionStepFactory,
    ExecutionRecordFactory,
    ReportArtifactFactory,
    StepPanelDTOFactory,
    GlobalContextVarsDTOFactory,
    CausalNodeDTOFactory,
    CausalGraphPayloadDTOFactory,
)


@pytest.mark.parametrize("factory_cls", ALL_FACTORIES)
def test_polyfactory_build_succeeds(factory_cls: RegisteredFactoryType) -> None:
    """Assert that each registered Polyfactory model factory builds valid instances.

    Args:
        factory_cls: Polyfactory model factory class under test.
    """
    instance = factory_cls.build()
    model_cls = factory_cls.__model__
    assert isinstance(instance, model_cls)
    # Verify strict re-validation roundtrip
    validated = model_cls.model_validate(instance)
    dumped = validated.model_dump()
    assert dumped is not None
    if "id" in dumped and isinstance(dumped["id"], str):
        assert re.match(OPAQUE_STRIPE_ID_REGEX, dumped["id"]) is not None
    if "organization_id" in dumped and isinstance(dumped["organization_id"], str):
        assert re.match(OPAQUE_STRIPE_ID_REGEX, dumped["organization_id"]) is not None
    if "node_id" in dumped and isinstance(dumped["node_id"], str):
        assert re.match(OPAQUE_STRIPE_ID_REGEX, dumped["node_id"]) is not None


def test_polyfactory_invalid_id_error() -> None:
    """Verify non-hexadecimal entity IDs trigger ValidationError."""
    valid_payload = ReportArtifactFactory.build().model_dump()
    valid_payload["id"] = "rep_non_hex_invalid_id_1234"
    with pytest.raises(ValidationError):
        ReportArtifact.model_validate(valid_payload)


def test_polyfactory_invalid_extra_field_error() -> None:
    """Verify extra fields trigger ValidationError under extra='forbid'."""
    valid_payload = WorkflowFactory.build().model_dump()
    valid_payload["unexpected_extra_field"] = "forbidden"
    with pytest.raises(ValidationError):
        Workflow.model_validate(valid_payload)


def test_polyfactory_step_panel_empty_payload_error() -> None:
    """Verify StepPanelDTO rejects all-None payloads when falsifier_data is cleared."""
    with pytest.raises(ValidationError, match="StepPanelDTO requires at least one analysis payload"):
        StepPanelDTOFactory.build(falsifier_data=None)


def test_polyfactory_causal_graph_referential_integrity_error() -> None:
    """Verify CausalGraphPayloadDTO rejects dangling edge target_id references."""
    with pytest.raises(ValidationError, match="does not exist in graph nodes"):
        CausalGraphPayloadDTOFactory.build(
            edges=[
                CausalEdgeDTO(
                    source_id="tda_0195f3a0000070008000000000000001",
                    target_id="tda_0195f3a0000070008000ffffffffffff",
                    reasoning="Dangling target reference.",
                )
            ]
        )
    assert isinstance(CausalGraphPayloadDTOFactory.build(), CausalGraphPayloadDTO)
    assert isinstance(StepPanelDTOFactory.build(), StepPanelDTO)

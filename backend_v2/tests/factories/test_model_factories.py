"""Unit tests verifying all Polyfactory model factories build valid models."""

from __future__ import annotations

import re
from typing import Any

import pytest
from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import ValidationError

from backend_v2.models.core_base import OPAQUE_STRIPE_ID_REGEX
from backend_v2.models.domain.report_artifact import ReportArtifact
from backend_v2.models.domain.workflow import Workflow
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

ALL_FACTORIES: list[type[ModelFactory[Any]]] = [
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
]


@pytest.mark.parametrize("factory_cls", ALL_FACTORIES)
def test_polyfactory_build_succeeds(factory_cls: type[ModelFactory[Any]]) -> None:
    """Asserts that each registered Polyfactory model factory builds valid instances."""
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


def test_polyfactory_invalid_id_error() -> None:
    """Phase 5, Step 5: ISTQB negative test verifying non-hexadecimal entity IDs trigger ValidationError."""
    valid_payload = ReportArtifactFactory.build().model_dump()
    valid_payload["id"] = "rep_non_hex_invalid_id_1234"
    with pytest.raises(ValidationError):
        ReportArtifact.model_validate(valid_payload)


def test_polyfactory_invalid_extra_field_error() -> None:
    """Phase 5, Step 5: ISTQB negative test verifying extra fields trigger ValidationError under extra='forbid'."""
    valid_payload = WorkflowFactory.build().model_dump()
    valid_payload["unexpected_extra_field"] = "forbidden"
    with pytest.raises(ValidationError):
        Workflow.model_validate(valid_payload)

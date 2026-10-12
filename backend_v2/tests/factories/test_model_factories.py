"""Unit tests verifying all Polyfactory model factories build valid models."""

from __future__ import annotations

from typing import Any

import pytest
from polyfactory.factories.pydantic_factory import ModelFactory

from backend_v2.tests.factories.model_factories import (
    CausalGraphPayloadDTOFactory,
    CausalNodeDTOFactory,
    ExecutionRecordFactory,
    ExecutionStepFactory,
    GlobalContextVarsDTOFactory,
    I18nTextFactory,
    MatrixPromptBlockFactory,
    OutputProfileFactory,
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
    assert model_cls.model_validate(instance).model_dump() is not None

"""Unit tests verifying all Polyfactory model factories build valid models."""

from __future__ import annotations

import pytest

from backend_v2.tests.factories.model_factories import (
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

ALL_FACTORIES = [
    I18nTextFactory,
    WorkflowFactory,
    SystemRulePromptBlockFactory,
    OutputProfileFactory,
    MatrixPromptBlockFactory,
    ExecutionStepFactory,
    ExecutionRecordFactory,
    StepPanelDTOFactory,
    GlobalContextVarsDTOFactory,
]


@pytest.mark.parametrize("factory_cls", ALL_FACTORIES)
def test_polyfactory_build_succeeds(factory_cls: type) -> None:
    """Asserts that each registered Polyfactory model factory builds valid instances."""
    instance = factory_cls.build()
    assert isinstance(instance, factory_cls.__model__)
    # Verify strict re-validation roundtrip
    assert factory_cls.__model__.model_validate(instance).model_dump() is not None

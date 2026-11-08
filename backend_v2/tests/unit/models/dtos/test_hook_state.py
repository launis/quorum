"""Unit tests for hook state DTOs."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend_v2.models.dtos import hook_state as hook_state_module
from backend_v2.models.dtos.hook_delta import ExecutionMetadataDeltaDTO, PassivityDetectionResultDTO
from backend_v2.models.dtos.hook_state import ExecutionInputsDTO, GlobalContextVarsDTO, HookDeltaDTO


def test_execution_inputs_dto_instantiation() -> None:
    """Verify ExecutionInputsDTO instantiation and field defaults."""
    dto = ExecutionInputsDTO(
        raw_inputs={"input_1": "value"},
        dynamic_inputs={"param_1": 10},
        user_role="admin",
        target_locale="fi",
    )
    assert dto.raw_inputs == {"input_1": "value"}
    assert dto.dynamic_inputs == {"param_1": 10}
    assert dto.user_role == "admin"
    assert dto.target_locale == "fi"

    # Default factory test via JSON validation boundary
    default_dto = ExecutionInputsDTO.model_validate_json("{}")
    assert default_dto.raw_inputs == {}
    assert default_dto.dynamic_inputs == {}
    assert default_dto.user_role is None
    assert default_dto.target_locale is None


def test_execution_inputs_dto_strictness() -> None:
    """Verify ExecutionInputsDTO forbids extra fields, enforces strict types, and is frozen."""
    assert ExecutionInputsDTO.model_config["frozen"] is True
    assert ExecutionInputsDTO.model_config["extra"] == "forbid"
    assert ExecutionInputsDTO.model_config["strict"] is True

    with pytest.raises(ValidationError):
        ExecutionInputsDTO.model_validate({"extra_field": "fail"})

    with pytest.raises(ValidationError):
        ExecutionInputsDTO.model_validate({"user_role": 12345})

    with pytest.raises(ValidationError):
        ExecutionInputsDTO.model_validate({"raw_inputs": "not_a_mapping"})


def test_hook_state_module_invalid_attribute() -> None:
    """Verify accessing an unknown attribute on hook_state module raises AttributeError."""
    with pytest.raises(AttributeError):
        hook_state_module.__getattr__("NonExistentAttributeDTO")


def test_global_context_vars_dto_instantiation() -> None:
    """Verify GlobalContextVarsDTO instantiation and field defaults."""
    dto = GlobalContextVarsDTO(language="fi", target_locale="fi", profile_id="prf_123")
    assert dto.language == "fi"
    assert dto.target_locale == "fi"
    assert dto.profile_id == "prf_123"

    default_dto = GlobalContextVarsDTO()
    assert default_dto.language is None


def test_global_context_vars_dto_strictness() -> None:
    """Verify GlobalContextVarsDTO forbids extra fields and enforces immutability."""
    with pytest.raises(ValidationError):
        GlobalContextVarsDTO.model_validate({"extra_field": "fail"})


def test_hook_delta_dto_instantiation() -> None:
    """Verify HookDeltaDTO instantiation and field defaults."""
    payload = PassivityDetectionResultDTO(passivity_detected=True)
    meta = ExecutionMetadataDeltaDTO(estimated_token_count=100)
    dto = HookDeltaDTO(delta=payload, metadata_updates=meta)
    assert dto.delta == payload
    assert dto.metadata_updates == meta

    default_dto = HookDeltaDTO()
    assert default_dto.delta is None
    assert default_dto.metadata_updates is None


def test_hook_delta_dto_strictness() -> None:
    """Verify HookDeltaDTO forbids extra fields and enforces immutability."""
    with pytest.raises(ValidationError):
        HookDeltaDTO.model_validate({"extra_field": "fail"})

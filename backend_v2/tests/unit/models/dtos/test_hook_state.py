import pytest
from pydantic import ValidationError

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

    # Default factory test
    default_dto = ExecutionInputsDTO()
    assert default_dto.raw_inputs == {}
    assert default_dto.dynamic_inputs == {}
    assert default_dto.user_role is None
    assert default_dto.target_locale is None


def test_execution_inputs_dto_strictness() -> None:
    """Verify ExecutionInputsDTO forbids extra fields and enforces immutability."""
    with pytest.raises(ValidationError):
        ExecutionInputsDTO(extra_field="fail")  # type: ignore[call-arg]

    dto = ExecutionInputsDTO()
    with pytest.raises(ValidationError):
        dto.user_role = "mutated"  # type: ignore[misc]


def test_global_context_vars_dto_instantiation() -> None:
    """Verify GlobalContextVarsDTO instantiation and field defaults."""
    dto = GlobalContextVarsDTO(vars={"key": "val"})
    assert dto.vars == {"key": "val"}

    default_dto = GlobalContextVarsDTO()
    assert default_dto.vars == {}


def test_global_context_vars_dto_strictness() -> None:
    """Verify GlobalContextVarsDTO forbids extra fields and enforces immutability."""
    with pytest.raises(ValidationError):
        GlobalContextVarsDTO(extra_field="fail")  # type: ignore[call-arg]


def test_hook_delta_dto_instantiation() -> None:
    """Verify HookDeltaDTO instantiation and field defaults."""
    dto = HookDeltaDTO(delta={"result": "ok"}, metadata_updates={"tokens": 100})
    assert dto.delta == {"result": "ok"}
    assert dto.metadata_updates == {"tokens": 100}

    default_dto = HookDeltaDTO()
    assert default_dto.delta == {}
    assert default_dto.metadata_updates is None


def test_hook_delta_dto_strictness() -> None:
    """Verify HookDeltaDTO forbids extra fields and enforces immutability."""
    with pytest.raises(ValidationError):
        HookDeltaDTO(extra_field="fail")  # type: ignore[call-arg]

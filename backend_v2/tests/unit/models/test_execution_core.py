from unittest.mock import AsyncMock
"""Unit tests for ExecutionCoreFields SSOT leaf module.

Tests verify the structural contract, inheritance chain,
field definitions, and Pydantic V2 strict mode enforcement.
"""

import pytest
from pydantic import ValidationError

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.enums import ExecutionStatus
from backend_v2.models.execution_core import ExecutionCoreFields
from backend_v2.models.state import ErrorTraceEvent, TombstoneEvent, TraceEvent


class TestExecutionCoreFieldsStructure:
    """Verify the SSOT structural contract of ExecutionCoreFields."""

    def test_inherits_v2_core_base(self) -> None:
        """ExecutionCoreFields must inherit V2CoreBase for strict Pydantic config."""
        assert issubclass(ExecutionCoreFields, V2CoreBase)

    def test_model_config_frozen_strict_forbid(self) -> None:
        """ExecutionCoreFields must enforce frozen, strict, and extra=forbid."""
        config = ExecutionCoreFields.model_config
        assert config.get("frozen") is True
        assert config.get("strict") is True
        assert config.get("extra") == "forbid"

    def test_defines_exactly_five_ssot_fields(self) -> None:
        """ExecutionCoreFields must define exactly the 5 shared SSOT fields."""
        expected = {
            "status",
            "execution_trace",
            "execution_trace_storage_path",
            "context_variables",
            "context_variables_storage_path",
        }
        actual = set(ExecutionCoreFields.model_fields.keys())
        assert actual == expected, f"Expected {expected}, got {actual}"


class TestExecutionCoreFieldsDefaults:
    """Verify default values match the domain contract."""

    def test_default_status_is_pending(self) -> None:
        """Status must default to ExecutionStatus.PENDING."""
        instance = ExecutionCoreFields.model_validate({})
        assert instance.status == ExecutionStatus.PENDING

    def test_default_execution_trace_is_empty_list(self) -> None:
        """Execution trace must default to an empty list."""
        instance = ExecutionCoreFields.model_validate({})
        assert instance.execution_trace == []

    def test_default_execution_trace_storage_path_is_none(self) -> None:
        """Execution trace storage path must default to None."""
        instance = ExecutionCoreFields.model_validate({})
        assert instance.execution_trace_storage_path is None

    def test_default_context_variables_is_empty_dict(self) -> None:
        """Context variables must default to an empty dict."""
        instance = ExecutionCoreFields.model_validate({})
        assert instance.context_variables == {}

    def test_default_context_variables_storage_path_is_none(self) -> None:
        """Context variables storage path must default to None."""
        instance = ExecutionCoreFields.model_validate({})
        assert instance.context_variables_storage_path is None


class TestExecutionCoreFieldsValidation:
    """Verify Pydantic V2 fail-fast validation on ExecutionCoreFields."""

    def test_fail_fast_on_invalid_status(self) -> None:
        """Invalid status must crash immediately via Pydantic validation."""
        with pytest.raises(ValidationError):
            ExecutionCoreFields.model_validate({"status": "INVALID"})

    def test_fail_fast_on_extra_fields(self) -> None:
        """Extra fields must crash immediately (extra=forbid)."""
        with pytest.raises(ValidationError):
            ExecutionCoreFields.model_validate({"rogue_field": "should_crash"})

    def test_accepts_valid_trace_event_union(self) -> None:
        """Execution trace must accept all union members."""
        trace_event = TraceEvent(step_name="test", event_type="output")
        error_event = ErrorTraceEvent(step_name="test", error_code="ERR_TEST", error_message="fail")
        tombstone_event = TombstoneEvent(step_name="test", redacted_hash="abc123")

        instance = ExecutionCoreFields.model_validate({"execution_trace": [trace_event, error_event, tombstone_event]})
        assert len(instance.execution_trace) == 3

    def test_frozen_immutability(self) -> None:
        """Frozen model must reject in-place mutation."""
        instance = ExecutionCoreFields.model_validate({})
        with pytest.raises(ValidationError):
            instance.status = ExecutionStatus.PENDING  # type: ignore[misc]

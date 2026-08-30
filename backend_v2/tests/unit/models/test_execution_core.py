"""Unit tests for ExecutionCoreFields SSOT leaf module.

Tests verify the structural contract, inheritance chain,
field definitions, and Pydantic V2 strict mode enforcement.
"""

import pytest
from pydantic import ValidationError

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.enums import ExecutionStatus
from backend_v2.models.execution_core import ExecutionCoreFields, ExecutionMetadata
from backend_v2.models.state import ErrorTraceEvent, TombstoneEvent, TraceEvent


class TestExecutionCoreFieldsStructure:
    """Verify the SSOT structural contract of ExecutionCoreFields."""

    def test_inherits_v2_core_base(self) -> None:
        """ExecutionCoreFields must inherit V2CoreBase for strict Pydantic config."""
        assert issubclass(ExecutionCoreFields, V2CoreBase)

    def test_model_config_strict_forbid(self) -> None:
        """ExecutionCoreFields must enforce strict and extra=forbid."""
        config = ExecutionCoreFields.model_config
        assert config.get("strict") is True
        assert config.get("extra") == "forbid"

    def test_defines_ssot_fields(self) -> None:
        """ExecutionCoreFields must define the shared SSOT fields."""
        expected = {
            "status",
            "target_locale",
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

    def test_default_target_locale_is_en(self) -> None:
        """Target locale must default to 'en'."""
        instance = ExecutionCoreFields.model_validate({})
        assert instance.target_locale == "en"

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


class TestExecutionMetadata:
    """Verify the SSOT structural contract and defaults of ExecutionMetadata."""

    def test_inherits_v2_core_base(self) -> None:
        """ExecutionMetadata must inherit V2CoreBase."""
        assert issubclass(ExecutionMetadata, V2CoreBase)

    def test_model_config_strict_forbid(self) -> None:
        """ExecutionMetadata must enforce strict and extra=forbid."""
        config = ExecutionMetadata.model_config
        assert config.get("strict") is True
        assert config.get("extra") == "forbid"

    def test_defaults(self) -> None:
        """Verify default values on ExecutionMetadata when target_locale is provided."""
        meta = ExecutionMetadata(target_locale="en")
        assert meta.target_locale == "en"
        assert meta.profile_id is None
        assert meta.matrix_sampling_strategy == 10
        assert meta.workflow_version == 1
        assert meta.user_id is None
        assert meta.organization_id is None

    def test_fail_fast_on_missing_target_locale(self) -> None:
        """Missing mandatory target_locale must fail fast."""
        with pytest.raises(ValidationError):
            ExecutionMetadata.model_validate({})

    def test_custom_values(self) -> None:
        """Verify custom values initialization."""
        meta = ExecutionMetadata(
            target_locale="fi",
            profile_id="prof-1",
            matrix_sampling_strategy=20,
            workflow_version=2,
            user_id="usr-1",
            organization_id="org-1",
        )
        assert meta.target_locale == "fi"
        assert meta.profile_id == "prof-1"
        assert meta.matrix_sampling_strategy == 20
        assert meta.workflow_version == 2
        assert meta.user_id == "usr-1"
        assert meta.organization_id == "org-1"

    def test_fail_fast_on_extra_fields(self) -> None:
        """Extra fields must crash immediately (extra=forbid)."""
        with pytest.raises(ValidationError):
            ExecutionMetadata.model_validate({"rogue_field": "crash"})

    def test_execution_metadata_accepts_telemetry_and_context_fields(self) -> None:
        """Verify ExecutionMetadata accepts proven runtime telemetry and context fields written by worker."""
        payload = {
            "target_locale": "fi",
            "global_context_vars": {"language": "fi"},
            "execution_summary": {"strictness_level": 85},
            "step_metrics": {"sr_1": {"cost_usd": 0.05}},
            "dag_cost_usd": 0.414,
            "prompt_tokens": 1000,
            "completion_tokens": 200,
            "cached_tokens": 300,
            "reasoning_tokens": 50,
        }
        meta = ExecutionMetadata.model_validate(payload)
        assert meta.global_context_vars == {"language": "fi"}
        assert meta.execution_summary == {"strictness_level": 85}
        assert meta.step_metrics == {"sr_1": {"cost_usd": 0.05}}
        assert meta.dag_cost_usd == 0.414
        assert meta.prompt_tokens == 1000
        assert meta.completion_tokens == 200
        assert meta.cached_tokens == 300
        assert meta.reasoning_tokens == 50

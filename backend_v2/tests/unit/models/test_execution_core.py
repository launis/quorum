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
        instance = ExecutionCoreFields.model_validate({"target_locale": "en"})
        assert instance.status == ExecutionStatus.PENDING

    def test_fail_fast_on_missing_target_locale(self) -> None:
        """Missing mandatory target_locale must fail fast."""
        with pytest.raises(ValidationError):
            ExecutionCoreFields.model_validate({})

    def test_default_execution_trace_is_empty_list(self) -> None:
        """Execution trace must default to an empty list."""
        instance = ExecutionCoreFields.model_validate({"target_locale": "en"})
        assert instance.execution_trace == []

    def test_default_execution_trace_storage_path_is_none(self) -> None:
        """Execution trace storage path must default to None."""
        instance = ExecutionCoreFields.model_validate({"target_locale": "en"})
        assert instance.execution_trace_storage_path is None

    def test_default_context_variables_is_empty_dict(self) -> None:
        """Context variables must default to an empty dict."""
        instance = ExecutionCoreFields.model_validate({"target_locale": "en"})
        assert instance.context_variables == {}

    def test_default_context_variables_storage_path_is_none(self) -> None:
        """Context variables storage path must default to None."""
        instance = ExecutionCoreFields.model_validate({"target_locale": "en"})
        assert instance.context_variables_storage_path is None


class TestExecutionCoreFieldsValidation:
    """Verify Pydantic V2 fail-fast validation on ExecutionCoreFields."""

    def test_fail_fast_on_invalid_status(self) -> None:
        """Invalid status must crash immediately via Pydantic validation."""
        with pytest.raises(ValidationError):
            ExecutionCoreFields.model_validate({"target_locale": "en", "status": "INVALID"})

    def test_fail_fast_on_extra_fields(self) -> None:
        """Extra fields must crash immediately (extra=forbid)."""
        with pytest.raises(ValidationError):
            ExecutionCoreFields.model_validate({"target_locale": "en", "rogue_field": "should_crash"})

    def test_accepts_valid_trace_event_union(self) -> None:
        """Execution trace must accept all union members."""
        trace_event = TraceEvent(step_name="test", event_type="output")
        error_event = ErrorTraceEvent(step_name="test", error_code="ERR_TEST", error_message="fail")
        tombstone_event = TombstoneEvent(step_name="test", redacted_hash="abc123")

        instance = ExecutionCoreFields.model_validate(
            {"target_locale": "en", "execution_trace": [trace_event, error_event, tombstone_event]}
        )
        assert len(instance.execution_trace) == 3

    def test_execution_record_missing_target_locale_raises_validation_error(self) -> None:
        """Contract: Verify ExecutionRecord missing target_locale raises ValidationError (Fail-Fast)."""
        from backend_v2.models.v2_core import ExecutionRecord

        payload = {
            "id": "exe_1234567890abcdef",
            "workflow_id": "wor_1234567890abcdef",
            "metadata": {},
        }
        with pytest.raises(ValidationError):
            ExecutionRecord.model_validate(payload)

    def test_execution_record_accepts_null_frozen_context_when_offloaded(self) -> None:
        """Contract: Verify ExecutionRecord accepts null frozen_context when offloaded to storage."""
        from backend_v2.models.v2_core import ExecutionRecord

        payload = {
            "id": "exe_1234567890abcdef",
            "workflow_id": "wor_1234567890abcdef",
            "output_profile_id": "prof_1234567890abcdef",
            "target_locale": "en",
            "status": "PASSED",
            "metadata": {"workflow_version": 1},
            "frozen_context": None,
            "frozen_context_storage_path": "executions/exe_1234567890abcdef/frozen_context.json",
        }
        record = ExecutionRecord.model_validate(payload)
        assert record.id == "exe_1234567890abcdef"
        assert record.frozen_context is None
        assert record.frozen_context_storage_path == "executions/exe_1234567890abcdef/frozen_context.json"


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
        """Verify default values on ExecutionMetadata."""
        meta = ExecutionMetadata()
        assert meta.matrix_sampling_strategy == 10
        assert meta.workflow_version == 1
        assert meta.global_context_vars is None

    def test_custom_values(self) -> None:
        """Verify custom values initialization."""
        meta = ExecutionMetadata(
            matrix_sampling_strategy=20,
            workflow_version=2,
            global_context_vars={"language": "fi"},
        )
        assert meta.matrix_sampling_strategy == 20
        assert meta.workflow_version == 2
        assert meta.global_context_vars == {"language": "fi"}

    def test_fail_fast_on_extra_fields(self) -> None:
        """Extra fields must crash immediately (extra=forbid)."""
        with pytest.raises(ValidationError):
            ExecutionMetadata.model_validate({"rogue_field": "crash"})

    def test_deprecated_finops_and_duplication_fields_rejected(self) -> None:
        """Verify ExecutionMetadata rejects deprecated fields (target_locale, prompt_tokens, dag_cost_usd)."""
        with pytest.raises(ValidationError):
            ExecutionMetadata.model_validate({"target_locale": "fi"})

        with pytest.raises(ValidationError):
            ExecutionMetadata.model_validate({"dag_cost_usd": 0.414})

        with pytest.raises(ValidationError):
            ExecutionMetadata.model_validate({"prompt_tokens": 1000})

        with pytest.raises(ValidationError):
            ExecutionMetadata.model_validate({"step_metrics": {}})

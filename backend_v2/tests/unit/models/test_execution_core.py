"""Unit tests for ExecutionCoreFields SSOT leaf module.

Tests verify the structural contract, inheritance chain,
field definitions, and Pydantic V2 strict mode enforcement.
"""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from backend_v2.models.core_base import V2CoreBase, generate_uuid7
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.dtos.context_variables import ContextVariablesDTO
from backend_v2.models.dtos.trace import TraceEventMetadataDTO
from backend_v2.models.enums import ExecutionStatus
from backend_v2.models.execution_core import ExecutionCoreFields, ExecutionMetadata
from backend_v2.models.state import ErrorTraceEvent, TombstoneEvent, TraceEvent
from backend_v2.tests.factories.model_factories import ExecutionRecordFactory, GlobalContextVarsDTOFactory


class TestExecutionCoreFieldsStructure:
    """Verify the SSOT structural contract of ExecutionCoreFields."""

    def test_inherits_v2_core_base(self) -> None:
        """ExecutionCoreFields must inherit V2CoreBase for strict Pydantic config."""
        assert issubclass(ExecutionCoreFields, V2CoreBase)

    def test_model_config_strict_forbid(self) -> None:
        """ExecutionCoreFields must enforce strict and extra=forbid."""
        config = ExecutionCoreFields.model_config
        assert config["strict"] is True
        assert config["extra"] == "forbid"

    def test_defines_ssot_fields(self) -> None:
        """ExecutionCoreFields must define the shared SSOT fields."""
        expected = {
            "status",
            "target_locale",
            "execution_trace",
            "context_variables",
            "progress",
            "status_message",
        }
        actual = set(ExecutionCoreFields.model_fields.keys())
        assert actual == expected, f"Expected {expected}, got {actual}"


class TestExecutionCoreFieldsDefaults:
    """Verify default values match the domain contract."""

    def test_default_status_is_pending(self) -> None:
        """Status must default to ExecutionStatus.PENDING."""
        instance = ExecutionCoreFields(
            target_locale="en",
            execution_trace=[],
            context_variables=ContextVariablesDTO.empty(),
        )
        assert instance.status == ExecutionStatus.PENDING

    def test_fail_fast_on_missing_target_locale(self) -> None:
        """Missing mandatory target_locale must fail fast."""
        with pytest.raises(ValidationError):
            ExecutionCoreFields.model_validate({})

    def test_default_execution_trace_is_empty_list(self) -> None:
        """Execution trace must default to an empty list."""
        instance = ExecutionRecordFactory.build(target_locale="en")
        assert instance.execution_trace == []

    def test_default_context_variables_is_empty_dto(self) -> None:
        """Context variables must default to an empty ContextVariablesDTO."""
        instance = ExecutionRecordFactory.build(target_locale="en")
        assert isinstance(instance.context_variables, ContextVariablesDTO)
        assert len(instance.context_variables) == 0
        assert instance.context_variables.variables == {}

    def test_default_progress_is_none(self) -> None:
        """Progress must default to None."""
        instance = ExecutionCoreFields(
            target_locale="en",
            execution_trace=[],
            context_variables=ContextVariablesDTO.empty(),
        )
        assert instance.progress is None

    def test_default_status_message_is_none(self) -> None:
        """Status message must default to None."""
        instance = ExecutionCoreFields(
            target_locale="en",
            execution_trace=[],
            context_variables=ContextVariablesDTO.empty(),
        )
        assert instance.status_message is None

    def test_progress_bounds_validation(self) -> None:
        """Progress must enforce 0 <= progress <= 100 per ISTQB boundaries."""
        valid_0 = ExecutionCoreFields(
            target_locale="en",
            execution_trace=[],
            context_variables=ContextVariablesDTO.empty(),
            progress=0,
        )
        assert valid_0.progress == 0

        valid_100 = ExecutionCoreFields(
            target_locale="en",
            execution_trace=[],
            context_variables=ContextVariablesDTO.empty(),
            progress=100,
        )
        assert valid_100.progress == 100

        with pytest.raises(ValidationError):
            ExecutionCoreFields.model_validate({"target_locale": "en", "progress": -1})

        with pytest.raises(ValidationError):
            ExecutionCoreFields.model_validate({"target_locale": "en", "progress": 101})

    def test_status_message_validation(self) -> None:
        """Status message must accept strings and reject non-string types."""
        valid = ExecutionCoreFields(
            target_locale="en",
            execution_trace=[],
            context_variables=ContextVariablesDTO.empty(),
            status_message="Executing Step 1",
        )
        assert valid.status_message == "Executing Step 1"

        with pytest.raises(ValidationError):
            ExecutionCoreFields.model_validate({"target_locale": "en", "status_message": 12345})


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
        now = datetime.now(UTC)
        meta = TraceEventMetadataDTO(mcp_audit_traces=[])
        trace_event = TraceEvent(
            event_id=generate_uuid7(),
            timestamp=now,
            step_name="test",
            event_type="output",
            metadata=meta,
            mcp_audit_traces=[],
        )
        error_event = ErrorTraceEvent(
            event_id=generate_uuid7(),
            timestamp=now,
            step_name="test",
            error_code="ERR_TEST",
            error_message="fail",
            metadata=meta,
            mcp_audit_traces=[],
        )
        tombstone_event = TombstoneEvent(
            event_id=generate_uuid7(),
            timestamp=now,
            step_name="test",
            redacted_hash="abc123",
            metadata=meta,
            mcp_audit_traces=[],
        )

        instance = ExecutionCoreFields(
            target_locale="en",
            execution_trace=[trace_event, error_event, tombstone_event],
            context_variables=ContextVariablesDTO.empty(),
        )
        assert len(instance.execution_trace) == 3

    def test_execution_record_missing_target_locale_raises_validation_error(self) -> None:
        """Contract: Verify ExecutionRecord missing target_locale raises ValidationError (Fail-Fast)."""
        payload = {
            "id": "exe_0195f3a0000070018234567890abcdef",
            "workflow_id": "wor_0195f3a0000070018234567890abcdef",
            "metadata": {},
        }
        with pytest.raises(ValidationError):
            ExecutionRecord.model_validate(payload)

    def test_execution_record_accepts_null_frozen_context_on_summary_row(self) -> None:
        """Contract: Verify ExecutionRecord accepts null frozen_context on summary hydration."""
        record = ExecutionRecordFactory.build(
            id="exe_0195f3a0000070018234567890abcdef",
            workflow_id="wor_0195f3a0000070018234567890abcdef",
            output_profile_id="prof_0195f3a0000070018234567890abcdef",
            target_locale="en",
            status=ExecutionStatus.PASSED,
            frozen_context=None,
        )
        assert record.id == "exe_0195f3a0000070018234567890abcdef"
        assert record.frozen_context is None


class TestExecutionMetadata:
    """Verify the SSOT structural contract and defaults of ExecutionMetadata."""

    def test_inherits_v2_core_base(self) -> None:
        """ExecutionMetadata must inherit V2CoreBase."""
        assert issubclass(ExecutionMetadata, V2CoreBase)

    def test_model_config_strict_forbid(self) -> None:
        """ExecutionMetadata must enforce strict and extra=forbid."""
        config = ExecutionMetadata.model_config
        assert config["strict"] is True
        assert config["extra"] == "forbid"

    def test_defaults(self) -> None:
        """Verify default values on ExecutionMetadata."""
        meta = ExecutionMetadata()
        assert meta.matrix_sampling_strategy == 10
        assert meta.workflow_version == 1
        assert meta.global_context_vars is None

    def test_custom_values(self) -> None:
        """Verify custom values initialization."""
        global_vars = GlobalContextVarsDTOFactory.build(language="fi")
        meta = ExecutionMetadata(
            matrix_sampling_strategy=20,
            workflow_version=2,
            global_context_vars=global_vars,
        )
        assert meta.matrix_sampling_strategy == 20
        assert meta.workflow_version == 2
        assert meta.global_context_vars == global_vars
        assert meta.global_context_vars is not None
        assert meta.global_context_vars.language == "fi"

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

    def test_bounds_validation(self) -> None:
        """Verify ISTQB boundary value analysis on matrix_sampling_strategy and workflow_version."""
        valid_min = ExecutionMetadata(matrix_sampling_strategy=0, workflow_version=1)
        assert valid_min.matrix_sampling_strategy == 0
        assert valid_min.workflow_version == 1

        with pytest.raises(ValidationError):
            ExecutionMetadata.model_validate({"matrix_sampling_strategy": -1})

        with pytest.raises(ValidationError):
            ExecutionMetadata.model_validate({"workflow_version": 0})

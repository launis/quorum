import pytest
from pydantic import ValidationError

from backend_v2.models.domain.prompt_blocks import SystemRulePromptBlock
from backend_v2.models.enums import DisplayScale
from backend_v2.models.state import WorkflowState  # noqa: F401 (Ensures ExecutionRecord is rebuilt)
from backend_v2.models.v2_core import ExecutionRecord, MCPAuditTrace, OutputProfile


def test_prompt_block_fail_fast_on_corrupt_type() -> None:
    data = {
        "id": "blk_1111111111111111",
        "slug": "pb_1",
        "label": {"translations": {"en": "T", "fi": "T"}},
        "description": {"translations": {"en": "D", "fi": "D"}},
        "category_id": "system_rule",
        "type": "INVALID_TYPE",
    }
    with pytest.raises(ValidationError) as exc_info:
        SystemRulePromptBlock.model_validate(data)
    assert "INVALID_TYPE" in str(exc_info.value)


def test_mcp_audit_trace_fail_fast_on_corrupt_timestamp() -> None:
    data = {"tool_id": "t1", "step_name": "s1", "query": "q", "timestamp": "not-a-date"}
    with pytest.raises(ValidationError) as exc_info:
        MCPAuditTrace.model_validate(data)
    assert "valid datetime" in str(exc_info.value)


def test_execution_record_fail_fast_on_corrupt_status() -> None:
    data = {"id": "exe_eeeeeeeeeeeeeeee", "workflow_id": "wf_1", "status": "INVALID_STATUS", "raw_inputs": {}}
    with pytest.raises(ValidationError) as exc_info:
        ExecutionRecord.model_validate(data)
    # Phase 1: status is now LaxExecutionStatus (enum) inherited from ExecutionCoreFields
    assert "INVALID_STATUS" in str(exc_info.value)


from typing import Any


def test_embedded_output_profile_description_parsing() -> None:
    # 1. Success case with valid I18nText
    valid_data: dict[str, Any] = {
        "id": "prf_1234567890123456",
        "slug": "test-profile",
        "workflow_id": "wf_9d68c573802341db",
        "name": {"translations": {"en": "My Profile", "fi": "My Profile"}},
        "description": {
            "translations": {"en": "A valid description", "fi": "A valid description"},
        },
        "display_scale": DisplayScale.ORIGINAL,
        "layouts": [],
    }
    profile_success = OutputProfile.model_validate(valid_data)
    assert profile_success.description is not None
    assert profile_success.description.get("en") == "A valid description"

    # 2. Fail-fast case with invalid description
    invalid_data: dict[str, Any] = {
        "id": "prf_1234567890123456",
        "slug": "test-profile",
        "workflow_id": "wf_9d68c573802341db",
        "name": {"translations": {"en": "My Profile", "fi": "My Profile"}},
        "description": "This is a simple string instead of I18nText dict",
        "display_scale": DisplayScale.ORIGINAL,
    }
    with pytest.raises(ValidationError) as exc_info:
        OutputProfile.model_validate(invalid_data)
    assert "Input should be a valid dictionary" in str(exc_info.value)


def test_execution_record_has_context_variables() -> None:
    data = {
        "id": "exe_1234567890123456",
        "workflow_id": "wf_1234567890",
        "status": "PENDING",
        "raw_inputs": {},
        "context_variables": {"report_context": {"output_extensions": []}},
    }

    record = ExecutionRecord.model_validate(data, strict=False)
    assert record.context_variables == {"report_context": {"output_extensions": []}}


def test_execution_core_fields_inheritance_on_execution_record() -> None:
    """Phase 1: Verify ExecutionRecord correctly inherits ExecutionCoreFields SSOT."""
    from backend_v2.models.execution_core import ExecutionCoreFields

    # 1. Verify inheritance chain
    assert issubclass(ExecutionRecord, ExecutionCoreFields), "ExecutionRecord must inherit from ExecutionCoreFields"

    # 2. Verify ExecutionCoreFields enforces V2CoreBase config
    config = ExecutionCoreFields.model_config
    assert config.get("frozen") is True, "ExecutionCoreFields must be frozen"
    assert config.get("strict") is True, "ExecutionCoreFields must be strict"
    assert config.get("extra") == "forbid", "ExecutionCoreFields must forbid extra fields"

    # 3. Verify all 5 core fields are accessible on ExecutionRecord instances
    core_field_names = {
        "status",
        "execution_trace",
        "execution_trace_storage_path",
        "context_variables",
        "context_variables_storage_path",
    }
    record_fields = set(ExecutionRecord.model_fields.keys())
    missing = core_field_names - record_fields
    assert not missing, f"ExecutionRecord missing inherited core fields: {missing}"

    # 4. Verify core fields on ExecutionCoreFields itself
    ecf_fields = set(ExecutionCoreFields.model_fields.keys())
    assert core_field_names == ecf_fields, (
        f"ExecutionCoreFields must define exactly the 5 SSOT fields. Expected: {core_field_names}, Got: {ecf_fields}"
    )


def test_strict_schema_parity_for_core_execution_fields() -> None:
    """Meta-test: Enforce that child classes inherit and do NOT redefine core fields.

    Uses __annotations__ (not model_fields) because model_fields includes
    BOTH inherited AND own fields, making it impossible to detect redefinitions.
    __annotations__ contains ONLY the fields explicitly defined at that class level.

    The 'status' field is whitelisted as a legitimate override because
    ExecutionRecord uses LaxExecutionStatus (broader type) while
    ExecutionCoreFields uses Literal (strict domain type).
    """
    from backend_v2.models.execution_core import ExecutionCoreFields
    from backend_v2.models.v2_core import ExecutionRecord

    core_field_names = set(ExecutionCoreFields.model_fields.keys())
    assert len(core_field_names) >= 5, "ExecutionCoreFields must define at least 5 shared fields"

    # Fields that child classes are explicitly allowed to override
    # (e.g., ExecutionRecord overrides 'status' with LaxExecutionStatus)
    allowed_overrides = {"status"}

    for child_cls in [WorkflowState, ExecutionRecord]:
        # 1. Verify inheritance
        assert issubclass(child_cls, ExecutionCoreFields), f"{child_cls.__name__} must inherit from ExecutionCoreFields"

        # 2. Verify NO redefinition of core fields using __annotations__
        own_annotations = child_cls.__annotations__  # Only THIS class level
        redefined = (core_field_names - allowed_overrides) & set(own_annotations.keys())
        assert not redefined, (
            f"{child_cls.__name__} illegally redefines inherited core fields: {redefined}. "
            f"These must be defined ONLY in ExecutionCoreFields."
        )

        # 3. Verify all core fields are accessible on the child
        child_all_fields = set(child_cls.model_fields.keys())
        missing = core_field_names - child_all_fields
        assert not missing, f"{child_cls.__name__} is missing inherited core fields: {missing}"


@pytest.mark.parametrize(
    "dead_weight_field",
    [
        "model_strategy",
        "historical_context_mode",
        "enable_pii_masking",
        "allowed_exports",
        "omit_empty_sections",
        "allowed_mcp_tools",
    ],
)
def test_synthesis_config_dto_rejects_purged_dead_weight_fields(dead_weight_field: str) -> None:
    """Negative test: SynthesisConfigDTO rejects purged fields with ValidationError under extra='forbid'."""
    from backend_v2.models.v2_core import SynthesisConfigDTO

    payload = {
        "synthesis_block_id": "blk_synthesis123",
        dead_weight_field: "unexpected_value",
    }
    with pytest.raises(ValidationError) as exc_info:
        SynthesisConfigDTO.model_validate(payload)
    assert "Extra inputs are not permitted" in str(exc_info.value)

import pytest
from pydantic import ValidationError

from backend_v2.models.v2_core import EmbeddedOutputProfile, ExecutionRecord, MCPAuditTrace, PromptBlock


def test_prompt_block_fail_fast_on_corrupt_type() -> None:
    data = {
        "id": "blk_testblock123",
        "slug": "pb_1",
        "label": {"default_locale": "en", "translations": {"en": "T"}},
        "description": {"default_locale": "en", "translations": {"en": "D"}},
        "category_id": "c1",
        "type": "INVALID_TYPE",
    }
    with pytest.raises(ValidationError) as exc_info:
        PromptBlock.model_validate(data)
    assert "Input should be 'float'" in str(exc_info.value)


def test_mcp_audit_trace_fail_fast_on_corrupt_timestamp() -> None:
    data = {"tool_id": "t1", "step_name": "s1", "query": "q", "timestamp": "not-a-date"}
    with pytest.raises(ValidationError) as exc_info:
        MCPAuditTrace.model_validate(data)
    assert "valid datetime" in str(exc_info.value)


def test_execution_record_fail_fast_on_corrupt_status() -> None:
    data = {"id": "exe_eeeeeeeeeeeeeeee", "workflow_id": "wf_1", "status": "INVALID_STATUS", "raw_inputs": {}}
    with pytest.raises(ValidationError) as exc_info:
        ExecutionRecord.model_validate(data)
    assert "Input should be 'pending'" in str(exc_info.value)


from typing import Any


def test_embedded_output_profile_description_parsing() -> None:
    # 1. Success case with valid I18nText
    valid_data: dict[str, Any] = {
        "name": {"default_locale": "en", "translations": {"en": "My Profile"}},
        "description": {"default_locale": "en", "translations": {"en": "A valid description"}},
        "display_scale": "original",
        "synthesis": None,
        "layouts": [],
    }
    profile_success = EmbeddedOutputProfile.model_validate(valid_data)
    assert profile_success.description is not None
    assert profile_success.description.get("en") == "A valid description"

    # 2. Fail-fast case with invalid description
    invalid_data: dict[str, Any] = {
        "name": {"default_locale": "en", "translations": {"en": "My Profile"}},
        "description": "This is a simple string instead of I18nText dict",
        "display_scale": "original",
    }
    with pytest.raises(ValidationError) as exc_info:
        EmbeddedOutputProfile.model_validate(invalid_data)
    assert "Input should be a valid dictionary" in str(exc_info.value)

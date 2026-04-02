import pytest
from pydantic import ValidationError

from backend_v2.models.v2_core import ExecutionRecord, MCPAuditTrace, PromptBlock


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
    data = {"id": "exe_testexec123", "workflow_id": "wf_1", "status": "INVALID_STATUS", "raw_inputs": {}}
    with pytest.raises(ValidationError) as exc_info:
        ExecutionRecord.model_validate(data)
    assert "Input should be 'pending'" in str(exc_info.value)

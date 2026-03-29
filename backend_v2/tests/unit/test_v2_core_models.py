from typing import Any
import pytest

from backend_v2.exceptions import AppException
from backend_v2.models.v2_core import ExecutionRecord, MCPAuditTrace, PromptBlock


def test_prompt_block_fail_fast_on_corrupt_type() -> None:
    data = {
        "id": "pb_1",
        "slug": "pb_1",
        "label": {"default_locale": "en", "translations": {"en": "T"}},
        "description": {"default_locale": "en", "translations": {"en": "D"}},
        "category_id": "c1",
        "type": "INVALID_TYPE",
    }
    with pytest.raises(AppException) as exc_info:
        PromptBlock.model_validate(data)
    assert "Invalid BlockDataType" in exc_info.value.message


def test_mcp_audit_trace_fail_fast_on_corrupt_timestamp() -> None:
    data = {"tool_id": "t1", "step_name": "s1", "query": "q", "timestamp": "not-a-date"}
    with pytest.raises(AppException) as exc_info:
        MCPAuditTrace.model_validate(data)
    assert "Invalid timestamp" in exc_info.value.message


def test_execution_record_fail_fast_on_corrupt_status() -> None:
    data = {"id": "exec_1", "workflow_id": "wf_1", "status": "INVALID_STATUS", "raw_inputs": {}}
    with pytest.raises(AppException) as exc_info:
        ExecutionRecord.model_validate(data)
    assert "Invalid status" in exc_info.value.message

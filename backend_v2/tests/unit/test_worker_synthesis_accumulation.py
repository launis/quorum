"""Unit tests for worker background synthesis FinOps and token accumulation.

Verifies that consecutive synthesis runs accumulate costs and tokens monotonically
without losing DAG execution costs or token figures.
"""

from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from backend_v2.models.dtos.trace import ExecutionUpdateDTO
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.state import TraceEvent
from backend_v2.models.v2_core import ExecutionRecord, ExecutionStatus
from backend_v2.settings import get_settings
from backend_v2.worker import generate_profile_synthesis_and_pdf_task


def _setup_mock_repo(mock_repo: AsyncMock, execution: ExecutionRecord) -> None:
    """Helper to populate repository mock data matching test_worker_synthesis conventions."""
    mock_repo.get_execution.return_value = execution
    mock_repo.get_workflow_by_id.return_value = {
        "id": "wf_1234567812345678",
        "slug": "test_workflow",
        "name": {"translations": {"en": "Test", "fi": "Test"}},
        "description": {"translations": {"en": "Desc", "fi": "Desc"}},
        "status": "draft",
        "allowed_exports": ["pdf"],
        "historical_context_mode": "DISABLED",
        "version": 1,
        "default_profile_id": "prof_1111111111111111",
        "expected_inputs": [],
        "steps": [{"id": "sr_1234567812345678", "task_blueprint": "sp_1234567812345678"}],
    }

    async def mock_get_step_by_id(b_id: str) -> dict[str, Any] | None:
        if b_id == "sp_1234567812345678":
            return {"id": "sp_1234567812345678", "model_strategy": "synthesis", "type": "logic"}
        return None

    mock_repo.get_step_by_id.side_effect = mock_get_step_by_id
    mock_repo.get_all_steps.return_value = [
        {
            "id": "sp_1234567812345678",
            "slug": "synthesis_step",
            "name": {"translations": {"en": "Synth"}},
            "model_strategy": "synthesis",
            "type": "logic",
            "hook": "text_consolidation_hook",
        }
    ]
    mock_repo.get_model_registry.return_value = {
        "id": "cfg_1111111111111111",
        "type": "model_registry",
        "slug": "model_registry",
        "models": {
            "synthesis": {
                "provider": "mock_llm_99",
                "model_name": "gemini-2.5-pro",
                "temperature": 0.0,
                "max_tokens": 1024,
                "is_active": True,
                "tpm_limit": 100000,
                "rpm_limit": 1000,
            }
        },
    }
    mock_repo.get_all_prompt_blocks.return_value = [
        {
            "id": "pb_1111111111111111",
            "slug": "system_prompt",
            "type": "instruction",
            "label": {"translations": {"en": "System"}},
            "description": {"translations": {"en": "System prompt"}},
            "category_id": "system_rule",
        }
    ]
    mock_repo.get_prompt_block.return_value = {
        "id": "pb_2222222222222222",
        "slug": "synthesis_prompt",
        "type": "instruction",
        "label": {"translations": {"en": "Synth System"}},
        "description": {"translations": {"en": "System prompt for synthesis"}},
        "ai_description": "You are an AI.",
        "category_id": "system_rule",
    }
    mock_repo.get_output_profile_by_id.return_value = {
        "slug": "test_slug",
        "workflow_id": "wf_123",
        "name": {"translations": {"en": "Test", "fi": "Test"}},
        "id": "prof_1111111111111111",
        "strictness_level": 85,
        "scoring_strategy": "AVERAGE",
        "max_extension_items": 3,
        "synthesis_length_constraint": 1000,
        "tone_instruction": "Professional",
        "matrix_1d_synthesis_directive": "1D directive",
        "matrix_synthesis_groups": [
            {
                "id": "grp_1111111111111111",
                "title": {"translations": {"en": "Group 1", "fi": "Ryhmä 1"}},
                "target_blocks": ["blk_1"],
            }
        ],
        "target_block_order": ["matrix_graphs_block"],
        "display_scale": "original",
    }


@pytest.mark.asyncio
@patch("backend_v2.worker.UnifiedWorkflowRepository")
@patch("backend_v2.worker.get_driver", new_callable=AsyncMock)
async def test_worker_synthesis_accumulates_costs_monotonically(
    _mock_driver: AsyncMock, mock_repo_class: AsyncMock
) -> None:
    """Test that consecutive synthesis runs accumulate costs and tokens monotonically without losing DAG costs."""
    get_settings().use_mock_llm = True

    mock_repo = AsyncMock()
    mock_repo_class.return_value = mock_repo

    mock_record_initial = ExecutionRecord(
        id="exe_1234567812345678",
        workflow_id="wf_1234567812345678",
        output_profile_id="prof_1111111111111111",
        status=ExecutionStatus.PASSED,
        target_locale="fi",
        metadata=ExecutionMetadata(),
        dag_cost_usd=1.85,
        cost_estimate=1.85,
        prompt_tokens=10000,
        completion_tokens=2000,
        cumulative_synthesis_tokens=0,
        cumulative_synthesis_cost=0.0,
        execution_trace=[
            TraceEvent(
                v=1,
                timestamp=datetime.now(timezone.utc),
                event_type="output",
                step_name="sr_1234567812345678",
                content={"blk_synth12345678": {"synthesized_markdown": "Test MD"}},
            )
        ],
    )

    _setup_mock_repo(mock_repo, mock_record_initial)

    # --- Run 1: First Synthesis Execution ---
    await generate_profile_synthesis_and_pdf_task(
        execution_id="exe_1234567812345678",
        accept_language="fi",
        profile_id="prof_1111111111111111",
        redis=None,
    )

    def _find_synthesis_update(calls: list[Any]) -> ExecutionUpdateDTO:
        for call in reversed(calls):
            args, _kwargs = call
            if len(args) >= 2 and isinstance(args[1], ExecutionUpdateDTO):
                if args[1].cumulative_synthesis_tokens is not None:
                    return args[1]
        raise AssertionError("No ExecutionUpdateDTO with cumulative_synthesis_tokens found")

    update_dto1 = _find_synthesis_update(mock_repo.update_execution.call_args_list)

    run1_tokens = update_dto1.cumulative_synthesis_tokens
    run1_cost = update_dto1.cumulative_synthesis_cost
    run1_estimate = update_dto1.cost_estimate

    assert run1_tokens is not None and run1_tokens >= 0
    assert run1_cost is not None and run1_cost >= 0.0
    # Total cost estimate must incorporate the DAG cost plus synthesis cost
    assert run1_estimate == pytest.approx(1.85 + run1_cost)

    # --- Run 2: Second Synthesis Execution (Accumulation) ---
    # Simulate database state after Run 1
    mock_record_after_run1 = mock_record_initial.model_copy(
        update={
            "cumulative_synthesis_tokens": run1_tokens,
            "cumulative_synthesis_cost": run1_cost,
            "cost_estimate": run1_estimate,
        }
    )
    mock_repo.get_execution.return_value = mock_record_after_run1
    mock_repo.update_execution.reset_mock()

    await generate_profile_synthesis_and_pdf_task(
        execution_id="exe_1234567812345678",
        accept_language="fi",
        profile_id="prof_1111111111111111",
        redis=None,
    )

    update_dto2 = _find_synthesis_update(mock_repo.update_execution.call_args_list)

    run2_tokens = update_dto2.cumulative_synthesis_tokens
    run2_cost = update_dto2.cumulative_synthesis_cost
    run2_estimate = update_dto2.cost_estimate

    assert run2_tokens is not None and run2_tokens >= run1_tokens
    assert run2_cost is not None and run2_cost >= run1_cost
    assert run2_estimate == pytest.approx(1.85 + run2_cost)

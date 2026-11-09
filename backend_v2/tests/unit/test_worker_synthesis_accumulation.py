"""Unit tests for worker background synthesis FinOps and token accumulation.

Verifies that consecutive synthesis runs accumulate costs and tokens monotonically
without losing DAG execution costs or token figures.
"""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch

import pytest

import backend_v2.workers.synthesis_worker as synthesis_worker_mod
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.system_config import SystemConfigModelRegistry
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.enums import ExecutionStatus
from backend_v2.settings import get_settings
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository
from backend_v2.workers import generate_profile_synthesis_and_pdf_task


async def _setup_mock_repo(fake_repo: InMemoryUnifiedWorkflowRepository, execution: ExecutionRecord) -> None:
    """Helper to populate repository mock data matching test_worker_synthesis conventions."""
    await fake_repo.save_execution(execution)

    wf_dict = {
        "id": "wf_0195f3a0000070018234567812345678",
        "slug": "test_workflow",
        "name": {"translations": {"en": "Test", "fi": "Test"}},
        "description": {"translations": {"en": "Desc", "fi": "Desc"}},
        "status": "draft",
        "historical_context_mode": "DISABLED",
        "version": 1,
        "default_profile_id": "prof_0195f3a0000070018111111111111111",
        "model_registry_id": "sys_0195f3a0000070018111222233334444",
        "expected_inputs": [],
        "steps": [
            {"id": "sr_0195f3a0000070018234567812345678", "task_blueprint": "sp_0195f3a0000070018234567812345678"}
        ],
    }
    await fake_repo.save_workflow(Workflow.model_validate(wf_dict, strict=False))

    fake_repo.seed_raw_step(
        "sp_0195f3a0000070018234567812345678",
        {
            "id": "sp_0195f3a0000070018234567812345678",
            "slug": "synthesis_step",
            "name": {"translations": {"en": "Synth"}},
            "type": "logic",
            "hook": "text_consolidation_hook",
        },
    )

    profile = {
        "provider": "mock_llm_99",
        "model_name": "gemini-2.5-pro",
        "temperature": 0.0,
        "max_tokens": 1024,
        "is_active": True,
        "tpm_limit": 100000,
        "rpm_limit": 1000,
    }
    model_reg = {
        "id": "sys_0195f3a0000070018111222233334444",
        "name": "Default Test Registry",
        "type": "model_registry",
        "slug": "model_registry",
        "default_provider": "vertex_ai",
        "tier_definitions": {
            "fast": profile,
            "balanced": profile,
            "deep": profile,
            "reasoning": profile,
        },
    }
    fake_repo.set_model_registry(
        SystemConfigModelRegistry.model_validate(model_reg), "sys_0195f3a0000070018111222233334444"
    )

    pb_1 = {
        "id": "pb_0195f3a0000070018111111111111111",
        "slug": "system_prompt",
        "type": "instruction",
        "label": {"translations": {"en": "System"}},
        "description": {"translations": {"en": "System prompt"}},
        "category_id": "system_rule",
    }
    pb_2 = {
        "id": "pb_0195f3a0000070028222222222222222",
        "slug": "synthesis_prompt",
        "type": "instruction",
        "label": {"translations": {"en": "Synth System"}},
        "description": {"translations": {"en": "System prompt for synthesis"}},
        "instruction_text": "You are an AI.",
        "category_id": "system_rule",
    }
    fake_repo.set_prompt_blocks([pb_1, pb_2])

    output_prof = {
        "slug": "test_slug",
        "workflow_id": "wf_0195f3a0000070018234567812345678",
        "name": {"translations": {"en": "Test", "fi": "Test"}},
        "id": "prof_0195f3a0000070018111111111111111",
        "max_extension_items": 3,
        "synthesis_length_constraint": 1000,
        "tone_instruction": "Professional",
        "matrix_1d_synthesis_directive": "1D directive",
        "matrix_synthesis_groups": [
            {
                "id": "grp_0195f3a0000070018111111111111111",
                "title": {"translations": {"en": "Group 1", "fi": "Ryhmä 1"}},
                "target_blocks": ["blk_1"],
            }
        ],
        "target_block_order": ["matrix_graphs_block"],
        "display_scale": "original",
    }
    fake_repo.set_output_profiles([output_prof])


@pytest.mark.asyncio
@patch("backend_v2.workers.synthesis_worker.get_driver", new_callable=AsyncMock)
async def test_worker_synthesis_accumulates_costs_monotonically(
    _mock_driver: AsyncMock,
) -> None:
    """Test that consecutive synthesis runs accumulate costs and tokens monotonically without losing DAG costs."""
    get_settings().use_mock_llm = True

    fake_repo = InMemoryUnifiedWorkflowRepository()

    mock_record_initial = ExecutionRecord.model_validate(
        {
            "id": "exe_0195f3a0000070018234567812345678",
            "workflow_id": "wf_0195f3a0000070018234567812345678",
            "output_profile_id": "prof_0195f3a0000070018111111111111111",
            "status": ExecutionStatus.PASSED,
            "target_locale": "fi",
            "metadata": {},
            "dag_cost_usd": 1.85,
            "cost_estimate": 1.85,
            "prompt_tokens": 10000,
            "completion_tokens": 2000,
            "cumulative_synthesis_tokens": 0,
            "cumulative_synthesis_cost": 0.0,
            "execution_trace": [
                {
                    "v": 1,
                    "timestamp": datetime.now(UTC),
                    "event_type": "output",
                    "step_name": "sr_0195f3a0000070018234567812345678",
                    "content": {"blk_synth12345678": {"synthesized_markdown": "Test MD"}},
                }
            ],
        },
        strict=False,
    )

    await _setup_mock_repo(fake_repo, mock_record_initial)

    with patch.object(synthesis_worker_mod, "UnifiedWorkflowRepository", return_value=fake_repo):
        # --- Run 1: First Synthesis Execution ---
        await generate_profile_synthesis_and_pdf_task(
            execution_id="exe_0195f3a0000070018234567812345678",
            accept_language="fi",
            profile_id="prof_0195f3a0000070018111111111111111",
            redis=None,
        )

        rec1 = await fake_repo.get_execution("exe_0195f3a0000070018234567812345678")
        assert rec1 is not None
        run1_tokens = rec1.cumulative_synthesis_tokens
        run1_cost = rec1.cumulative_synthesis_cost
        run1_estimate = rec1.cost_estimate

        assert run1_tokens is not None and run1_tokens >= 0
        assert run1_cost is not None and run1_cost >= 0.0
        # Total cost estimate must incorporate the DAG cost plus synthesis cost
        assert run1_estimate == pytest.approx(1.85 + run1_cost)

        # --- Run 2: Second Synthesis Execution (Accumulation) ---
        await generate_profile_synthesis_and_pdf_task(
            execution_id="exe_0195f3a0000070018234567812345678",
            accept_language="fi",
            profile_id="prof_0195f3a0000070018111111111111111",
            redis=None,
        )

        rec2 = await fake_repo.get_execution("exe_0195f3a0000070018234567812345678")
        assert rec2 is not None
        run2_tokens = rec2.cumulative_synthesis_tokens
        run2_cost = rec2.cumulative_synthesis_cost
        run2_estimate = rec2.cost_estimate

        assert run2_tokens is not None and run2_tokens >= run1_tokens
        assert run2_cost is not None and run2_cost >= run1_cost
        assert run2_estimate == pytest.approx(1.85 + run2_cost)


@pytest.mark.asyncio
@patch("backend_v2.workers.synthesis_worker.get_driver", new_callable=AsyncMock)
async def test_worker_synthesis_accumulation_preserves_multi_profile_caches(
    _mock_driver: AsyncMock,
) -> None:
    """Phase 6, Step 6.1: Verify synthesis accumulation across 2 distinct OutputProfile IDs preserves both caches."""
    get_settings().use_mock_llm = True
    fake_repo = InMemoryUnifiedWorkflowRepository()

    mock_record_initial = ExecutionRecord.model_validate(
        {
            "id": "exe_0195f3a0000070018234567812345678",
            "workflow_id": "wf_0195f3a0000070018234567812345678",
            "output_profile_id": "prof_0195f3a0000070018111111111111111",
            "status": ExecutionStatus.PASSED,
            "target_locale": "fi",
            "metadata": {},
            "dag_cost_usd": 1.85,
            "cost_estimate": 1.85,
            "prompt_tokens": 10000,
            "completion_tokens": 2000,
            "cumulative_synthesis_tokens": 0,
            "cumulative_synthesis_cost": 0.0,
            "execution_trace": [
                {
                    "v": 1,
                    "timestamp": datetime.now(UTC),
                    "event_type": "output",
                    "step_name": "sr_0195f3a0000070018234567812345678",
                    "content": {"blk_synth12345678": {"synthesized_markdown": "Test MD"}},
                }
            ],
        },
        strict=False,
    )

    await _setup_mock_repo(fake_repo, mock_record_initial)
    profile_1_id = "prof_0195f3a0000070018111111111111111"
    profile_2_id = "prof_0195f3a0000070018222222222222222"
    existing_profile = await fake_repo.get_output_profile(profile_1_id)
    assert existing_profile is not None
    second_profile = existing_profile.model_copy(
        update={
            "id": profile_2_id,
            "slug": "test_slug_second",
        }
    )
    fake_repo.set_output_profiles([existing_profile, second_profile])

    with patch.object(synthesis_worker_mod, "UnifiedWorkflowRepository", return_value=fake_repo):
        await generate_profile_synthesis_and_pdf_task(
            execution_id="exe_0195f3a0000070018234567812345678",
            accept_language="fi",
            profile_id=profile_1_id,
            redis=None,
        )
        await generate_profile_synthesis_and_pdf_task(
            execution_id="exe_0195f3a0000070018234567812345678",
            accept_language="fi",
            profile_id=profile_2_id,
            redis=None,
        )

    final_rec = await fake_repo.get_execution("exe_0195f3a0000070018234567812345678")
    assert final_rec is not None
    validated = ExecutionRecord.model_validate_json(final_rec.model_dump_json())
    assert validated.profile_syntheses is not None
    assert profile_1_id in validated.profile_syntheses
    assert profile_2_id in validated.profile_syntheses

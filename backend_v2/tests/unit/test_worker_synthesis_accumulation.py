"""Unit tests for worker background synthesis FinOps and token accumulation.

Verifies that consecutive synthesis runs accumulate costs and tokens monotonically
without losing DAG execution costs or token figures.
"""

from __future__ import annotations

from collections.abc import Generator
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from polyfactory.factories.pydantic_factory import ModelFactory

import backend_v2.workers.synthesis_worker as synthesis_worker_mod
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.step import StepRule
from backend_v2.models.domain.synthesis import MatrixSynthesisGroup
from backend_v2.models.domain.system_config import ModelProfile, SystemConfigModelRegistry
from backend_v2.models.enums import (
    BlockDataType,
    CognitiveTier,
    DisplayScale,
    ExecutionStatus,
    HistoricalContextMode,
    LLMProvider,
    PromptBlockCategory,
    TargetBlockType,
)
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.settings import get_settings
from backend_v2.tests.factories.model_factories import (
    ExecutionRecordFactory,
    OutputProfileFactory,
    SystemRulePromptBlockFactory,
    WorkflowFactory,
)
from backend_v2.tests.factories.model_factories import (
    TraceEventFactory as _TraceEventFactory,
)
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository
from backend_v2.workers import generate_profile_synthesis_and_pdf_task


class _ModelProfileFactory(ModelFactory[ModelProfile]):
    """Polyfactory model factory for ModelProfile configurations."""

    __model__ = ModelProfile
    __use_defaults__ = True


class _ModelRegistryFactory(ModelFactory[SystemConfigModelRegistry]):
    """Polyfactory model factory for SystemConfigModelRegistry instances."""

    __model__ = SystemConfigModelRegistry
    __use_defaults__ = True


@pytest.fixture(autouse=True)
def mock_worker_report_service() -> Generator[MagicMock]:
    """Mock ReportService for background worker synthesis accumulation tests.

    Yields:
        Mocked ReportService instance.
    """
    mock_artifact = MagicMock()
    mock_artifact.id = "rep_0195f3a0000070018234567890123456"
    mock_svc = MagicMock()
    mock_svc.get_or_create_default_artifact = AsyncMock(return_value=mock_artifact)
    mock_svc.compile_and_persist_artifact = AsyncMock()
    with (
        patch("backend_v2.workers.synthesis_worker.ReportService", return_value=mock_svc),
        patch("backend_v2.workers.synthesis_reducers.ReportService", return_value=mock_svc),
    ):
        yield mock_svc


def _build_initial_record() -> ExecutionRecord:
    """Build an initial ExecutionRecord with baseline DAG cost and output trace event.

    Returns:
        Configured ExecutionRecord instance.
    """
    trace_event = _TraceEventFactory.build(
        v=1,
        timestamp=datetime.now(UTC),
        event_type="output",
        step_name="sr_0195f3a0000070018234567812345678",
        content={"blk_synth12345678": {"synthesized_markdown": "Test MD"}},
    )
    return ExecutionRecordFactory.build(
        id="exe_0195f3a0000070018234567812345678",
        workflow_id="wf_0195f3a0000070018234567812345678",
        output_profile_id="prof_0195f3a0000070018111111111111111",
        status=ExecutionStatus.PASSED,
        target_locale="fi",
        metadata=ExecutionMetadata(),
        dag_cost_usd=1.85,
        cost_estimate=1.85,
        prompt_tokens=10000,
        completion_tokens=2000,
        cumulative_synthesis_tokens=0,
        cumulative_synthesis_cost=0.0,
        execution_trace=[trace_event],
    )


async def _setup_mock_repo(fake_repo: InMemoryUnifiedWorkflowRepository, execution: ExecutionRecord) -> None:
    """Populate in-memory repository fixtures for synthesis accumulation tests.

    Args:
        fake_repo: Target InMemoryUnifiedWorkflowRepository instance.
        execution: Initial ExecutionRecord to persist.
    """
    await fake_repo.save_execution(execution)

    workflow = WorkflowFactory.build(
        id="wf_0195f3a0000070018234567812345678",
        slug="test_workflow",
        name=I18nText(translations={"en": "Test", "fi": "Test"}),
        description=I18nText(translations={"en": "Desc", "fi": "Desc"}),
        status="draft",
        historical_context_mode=HistoricalContextMode.DISABLED,
        version=1,
        default_profile_id="prof_0195f3a0000070018111111111111111",
        model_registry_id="mrg_0195f3a0000070018111222233334444",
        expected_inputs=[],
        steps=[
            StepRule(
                id="sr_0195f3a0000070018234567812345678",
                task_blueprint="sp_0195f3a0000070018234567812345678",
                depends_on=[],
                input_mappings={},
            )
        ],
    )
    await fake_repo.save_workflow(workflow)

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

    tier_profile = _ModelProfileFactory.build(
        provider="mock_llm_99",
        model_name="gemini-2.5-pro",
        temperature=0.0,
        max_tokens=1024,
        is_active=True,
        tpm_limit=100000,
        rpm_limit=1000,
        allowed_tools=[],
        additional_params={},
    )
    model_reg = _ModelRegistryFactory.build(
        id="mrg_0195f3a0000070018111222233334444",
        name="Default Test Registry",
        slug="model_registry",
        default_provider=LLMProvider.VERTEX_AI,
        tier_definitions={
            CognitiveTier.FAST: tier_profile,
            CognitiveTier.BALANCED: tier_profile,
            CognitiveTier.DEEP: tier_profile,
            CognitiveTier.REASONING: tier_profile,
        },
    )
    fake_repo.set_model_registry(model_reg, "mrg_0195f3a0000070018111222233334444")

    pb_1 = SystemRulePromptBlockFactory.build(
        id="pb_0195f3a0000070018111111111111111",
        slug="system_prompt",
        type=BlockDataType.INSTRUCTION,
        label=I18nText(translations={"en": "System"}),
        description=I18nText(translations={"en": "System prompt"}),
        category_id=PromptBlockCategory.SYSTEM_RULE,
    )
    pb_2 = SystemRulePromptBlockFactory.build(
        id="pb_0195f3a0000070028222222222222222",
        slug="synthesis_prompt",
        type=BlockDataType.INSTRUCTION,
        label=I18nText(translations={"en": "Synth System"}),
        description=I18nText(translations={"en": "System prompt for synthesis"}),
        instruction_text="You are an AI.",
        category_id=PromptBlockCategory.SYSTEM_RULE,
    )
    fake_repo.set_prompt_blocks([pb_1, pb_2])

    output_prof = OutputProfileFactory.build(
        id="prof_0195f3a0000070018111111111111111",
        slug="test_slug",
        workflow_id="wf_0195f3a0000070018234567812345678",
        name=I18nText(translations={"en": "Test", "fi": "Test"}),
        max_extension_items=3,
        synthesis_length_constraint=1000,
        tone_instruction="Professional",
        matrix_1d_synthesis_directive="1D directive",
        matrix_synthesis_groups=[
            MatrixSynthesisGroup(
                id="grp_0195f3a0000070018111111111111111",
                title=I18nText(translations={"en": "Group 1", "fi": "Ryhmä 1"}),
                target_blocks=["blk_1"],
            )
        ],
        target_block_order=[TargetBlockType.MATRIX_GRAPHS_BLOCK],
        display_scale=DisplayScale.ORIGINAL,
    )
    fake_repo.set_output_profiles([output_prof])


@pytest.mark.asyncio
async def test_worker_synthesis_accumulates_costs_monotonically() -> None:
    """Verify consecutive synthesis runs accumulate costs and tokens monotonically without losing DAG costs."""
    get_settings().use_mock_llm = True

    fake_repo = InMemoryUnifiedWorkflowRepository()
    mock_record_initial = _build_initial_record()
    await _setup_mock_repo(fake_repo, mock_record_initial)

    with patch.object(synthesis_worker_mod, "UnifiedWorkflowRepository", return_value=fake_repo):
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
        assert run1_estimate == pytest.approx(1.85 + run1_cost)

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
async def test_worker_synthesis_accumulation_preserves_multi_profile_caches() -> None:
    """Verify synthesis accumulation across two distinct OutputProfile IDs preserves both caches."""
    get_settings().use_mock_llm = True
    fake_repo = InMemoryUnifiedWorkflowRepository()

    mock_record_initial = _build_initial_record()
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


@pytest.mark.asyncio
async def test_worker_synthesis_accumulation_missing_language_raises_error() -> None:
    """Verify synthesis accumulation rejects missing accept_language with Fail-Fast AppException."""
    with pytest.raises(AppException) as exc_info:
        await generate_profile_synthesis_and_pdf_task(
            execution_id="exe_0195f3a0000070018234567812345678",
            accept_language=None,
            profile_id="prof_0195f3a0000070018111111111111111",
            redis=None,
        )

    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

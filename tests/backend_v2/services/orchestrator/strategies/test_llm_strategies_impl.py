import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Any

from backend_v2.models.enums import SystemConcurrency
from backend_v2.services.orchestrator.strategies.llm import LLMNodeStrategy
from backend_v2.models.state import StateProjector
from backend_v2.models.v2_core import StepRule
from backend_v2.services.orchestrator.strategies.base import StrategyContext


@pytest.mark.asyncio
async def test_llm_strategy_concurrent_chunks_semaphore() -> None:
    """Epic 23/27: Test that LLM execution limits concurrency via Semaphore."""
    strategy = LLMNodeStrategy(repository=AsyncMock(), prompt_compiler=MagicMock())
    
    # 1. Setup minimal inputs
    step_rule = MagicMock(spec=StepRule)
    step_rule.id = "step_concurrent_test"
    step_rule.task_blueprint = "bp_123"
    step_rule.input_mappings = {}
    step_rule.allowed_mcp_tools = []
    
    projector = MagicMock(spec=StateProjector)
    projector.snapshot = {"shuffled_atoms": [{"atom_id": str(i), "boolean": True} for i in range(5)]}
    
    context = MagicMock(spec=StrategyContext)
    context.execution_id = "exec_1"
    context.workflow_id = "wf_1"
    context.model_strategy = "test_mock_strategy"
    context.metadata = {"profile_id": "prof_1", "target_locale": "en"}
    context.expected_inputs = None
    
    mock_step_def = {"id": "step_1111222233334444", "slug": "test", "name": "test", "type": "llm", "model_strategy": "test_mock", "prompt_blocks": ["block_123"]}
    strategy.repository.get_step_by_id = AsyncMock(return_value=mock_step_def)
    strategy.repository.get_all_prompt_blocks = AsyncMock(return_value=[{"id": "block_123"}])
    
    strategy.run_pre_hooks = AsyncMock(return_value=MagicMock(inputs=projector.snapshot))
    strategy.run_post_hooks = AsyncMock(return_value={"final": "output"})
    
    # 2. Track concurrency
    concurrent_executions = 0
    max_concurrent_executions = 0
    
    async def fake_run_structured_task(*args: Any, **kwargs: Any) -> tuple[Any, dict[str, int]]:
        nonlocal concurrent_executions, max_concurrent_executions
        concurrent_executions += 1
        max_concurrent_executions = max(max_concurrent_executions, concurrent_executions)
        await asyncio.sleep(0.05)  # Slight delay to ensure tasks overlap
        concurrent_executions -= 1
        mock_result = MagicMock()
        mock_result.model_dump.return_value = {"evaluations": []}
        return mock_result, {"total_tokens": 10}

    mock_client = MagicMock()
    mock_client.run_structured_task = AsyncMock(side_effect=fake_run_structured_task)
    
    # We must patch ChunkingService.chunk_payload to return more chunks than the semaphore limit.
    # MAX_CONCURRENT_LLM_STEPS is 3. We return 5 chunks so 5 parallel tasks are created.
    fake_chunks = [MagicMock(items=[{"atom_id": f"atom{i}"}]) for i in range(5)]
    
    mock_from_strategy = AsyncMock(return_value=mock_client)
    with patch("backend_v2.services.orchestrator.strategies.llm.LLMClient.from_strategy", new=mock_from_strategy), \
         patch("backend_v2.services.orchestrator.chunking_service.ChunkingService.chunk_payload", return_value=fake_chunks):
        
        await strategy.execute(step_rule, projector, context, None, None)
        
    # 3. Assertions
    assert mock_client.run_structured_task.call_count == 5
    # The max concurrent executions MUST exactly match the limit.
    assert max_concurrent_executions == SystemConcurrency.MAX_CONCURRENT_LLM_STEPS.value


@pytest.mark.asyncio
async def test_llm_strategy_context_pruning() -> None:
    """Epic 27 Phase 1: Test that input context mapping pruning successfully strips heavy keys."""
    strategy = LLMNodeStrategy(repository=AsyncMock(), prompt_compiler=MagicMock())
    
    step_rule = MagicMock(spec=StepRule)
    step_rule.id = "step_prune_test"
    step_rule.task_blueprint = "bp_123"
    step_rule.input_mappings = {"test_ctx": "$inputs.good_data"}
    step_rule.allowed_mcp_tools = []
    
    projector = MagicMock(spec=StateProjector)
    projector.snapshot = {
        "shuffled_atoms": [{"atom_id": "1", "quote": "heavy", "reasoning": "heavy", "boolean": True}],
        "inputs": {"good_data": "keep", "heavy_data": "should_be_ignored"}
    }
    
    context = MagicMock(spec=StrategyContext)
    context.execution_id = "exec_1"
    context.workflow_id = "wf_1"
    context.model_strategy = "test_strategy"
    context.metadata = {"profile_id": "prof_1", "target_locale": "en"}
    context.expected_inputs = None
    
    mock_step_def = {"id": "step_1111222233334444", "slug": "test", "name": "test", "type": "llm", "model_strategy": "test_mock", "prompt_blocks": ["block_123"]}
    strategy.repository.get_step_by_id = AsyncMock(return_value=mock_step_def)
    strategy.repository.get_all_prompt_blocks = AsyncMock(return_value=[{"id": "block_123"}])
    
    strategy.run_pre_hooks = AsyncMock(return_value=MagicMock(inputs=projector.snapshot))
    strategy.run_post_hooks = AsyncMock(return_value={"final": "output"})
    
    mock_client = MagicMock()
    mock_result = MagicMock()
    mock_result.model_dump.return_value = {"evaluations": []}
    mock_client.run_structured_task = AsyncMock(return_value=(mock_result, {}))
    
    mock_from_strategy = AsyncMock(return_value=mock_client)
    with patch("backend_v2.services.orchestrator.strategies.llm.LLMClient.from_strategy", new=mock_from_strategy), \
         patch("backend_v2.services.orchestrator.chunking_service.ChunkingService.chunk_payload", return_value=[MagicMock(items=[{"atom_id": "1"}])]):
        
        await strategy.execute(step_rule, projector, context, None, None)
        
    call_args = strategy.compiler.build_xml_context.call_args
    assert call_args is not None
    state_data = call_args.kwargs.get("state_data")
    assert state_data is not None
    
    # Verify strict stripping occurred
    assert "shuffled_atoms" not in state_data
    assert "heavy_data" not in state_data.get("inputs", {})
    assert state_data.get("inputs", {}).get("good_data") == "keep"

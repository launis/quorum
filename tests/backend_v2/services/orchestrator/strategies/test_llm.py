import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Any

from backend_v2.models.enums import SystemConcurrency
from backend_v2.services.orchestrator.strategies.llm import LLMNodeStrategy
from backend_v2.models.state import StateProjector
from backend_v2.models.v2_core import StepRule
from backend_v2.services.orchestrator.strategies.base import StrategyContext

MOCK_MATRIX_BLOCK = {
    "id": "comp_1234567890abcdef1234567890abcdef",
    "slug": "block-slug",
    "label": {"default_locale": "en", "translations": {"en": "Block Label"}},
    "description": {"default_locale": "en", "translations": {"en": "Block Description"}},
    "category_id": "matrix",
    "type": "string",
    "is_evaluative": True,
    "scale_min": 1,
    "scale_max": 5,
    "scales": [
        {
            "score": 1,
            "ai_label": "FAIL",
            "claims": [
                {
                    "label": {"default_locale": "en", "translations": {"en": "Claim 1"}},
                    "ai_description": "Claim 1 desc",
                    "tda_assertions": [
                        {
                            "tda_id": "tda_1234567890abcdef",
                            "ai_rule_description": "Rule 1",
                            "inverse_evidence": False,
                            "aggregation_mode": "EXISTS",
                        }
                    ]
                }
            ]
        },
        {
            "score": 5,
            "ai_label": "EXCELLENT",
            "claims": [
                {
                    "label": {"default_locale": "en", "translations": {"en": "Claim 5"}},
                    "ai_description": "Claim 5 desc",
                    "tda_assertions": [
                        {
                            "tda_id": "tda_abcdef1234567890",
                            "ai_rule_description": "Rule 5",
                            "inverse_evidence": False,
                            "aggregation_mode": "EXISTS",
                        }
                    ]
                }
            ]
        }
    ]
}

MOCK_INSTRUCTION_BLOCK = {
    "id": "comp_1234567890abcdef1234567890abcdef",
    "slug": "block-slug",
    "label": {"default_locale": "en", "translations": {"en": "Block Label"}},
    "description": {"default_locale": "en", "translations": {"en": "Block Description"}},
    "category_id": "instruction",
    "type": "string",
    "is_evaluative": True,
}


@pytest.mark.asyncio
async def test_llm_strategy_concurrent_chunks_semaphore() -> None:
    """Epic 23/27: Test that LLM execution limits concurrency via Semaphore."""
    exec_repo = AsyncMock()
    workflow_repo = AsyncMock()
    comp_repo = AsyncMock()
    identity_repo = AsyncMock()
    audit_repo = AsyncMock()
    system_repo = AsyncMock()
    prompt_compiler = MagicMock()
    
    strategy = LLMNodeStrategy(
        exec_repo=exec_repo,
        workflow_repo=workflow_repo,
        comp_repo=comp_repo,
        identity_repo=identity_repo,
        audit_repo=audit_repo,
        system_repo=system_repo,
        prompt_compiler=prompt_compiler,
    )
    
    # 1. Setup minimal inputs
    step_rule = MagicMock(spec=StepRule)
    step_rule.id = "step_concurrent_test"
    step_rule.task_blueprint = "bp_123"
    step_rule.input_mappings = {}
    step_rule.allowed_mcp_tools = []
    
    projector = MagicMock(spec=StateProjector)
    projector.snapshot = []
    
    context = StrategyContext(
        execution_id="exec_1",
        workflow_id="wf_1",
        model_strategy="test_mock_strategy",
        metadata={"profile_id": "prof_1", "target_locale": "en"},
        expected_inputs=None,
    )
    
    mock_step_def = {
        "id": "step_11112222333344445555666677778888",
        "slug": "test",
        "name": {"default_locale": "en", "translations": {"en": "test"}},
        "type": "llm",
        "model_strategy": "test_mock",
        "prompt_blocks": ["comp_1234567890abcdef1234567890abcdef"]
    }
    workflow_repo.get_step_by_id = AsyncMock(return_value=mock_step_def)
    workflow_repo.get_workflow = AsyncMock(return_value=None)
    comp_repo.get_all_prompt_blocks = AsyncMock(return_value=[MOCK_MATRIX_BLOCK])
    
    pre_hook_inputs = {"shuffled_atoms": [{"atom_id": str(i), "boolean": True} for i in range(5)]}
    strategy.run_pre_hooks = AsyncMock(return_value=MagicMock(inputs=pre_hook_inputs))
    strategy.run_post_hooks = AsyncMock(return_value=MagicMock(inputs={"final": "output"}))
    
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
    exec_repo = AsyncMock()
    workflow_repo = AsyncMock()
    comp_repo = AsyncMock()
    identity_repo = AsyncMock()
    audit_repo = AsyncMock()
    system_repo = AsyncMock()
    prompt_compiler = MagicMock()
    
    strategy = LLMNodeStrategy(
        exec_repo=exec_repo,
        workflow_repo=workflow_repo,
        comp_repo=comp_repo,
        identity_repo=identity_repo,
        audit_repo=audit_repo,
        system_repo=system_repo,
        prompt_compiler=prompt_compiler,
    )
    
    step_rule = MagicMock(spec=StepRule)
    step_rule.id = "step_prune_test"
    step_rule.task_blueprint = "bp_123"
    step_rule.input_mappings = {"test_ctx": "$inputs.good_data"}
    step_rule.allowed_mcp_tools = []
    
    projector = MagicMock(spec=StateProjector)
    projector.snapshot = []
    
    context = StrategyContext(
        execution_id="exec_1",
        workflow_id="wf_1",
        model_strategy="test_strategy",
        metadata={"profile_id": "prof_1", "target_locale": "en"},
        expected_inputs=None,
    )
    
    mock_step_def = {
        "id": "step_11112222333344445555666677778888",
        "slug": "test",
        "name": {"default_locale": "en", "translations": {"en": "test"}},
        "type": "llm",
        "model_strategy": "test_mock",
        "prompt_blocks": ["comp_1234567890abcdef1234567890abcdef"]
    }
    workflow_repo.get_step_by_id = AsyncMock(return_value=mock_step_def)
    workflow_repo.get_workflow = AsyncMock(return_value=None)
    comp_repo.get_all_prompt_blocks = AsyncMock(return_value=[MOCK_MATRIX_BLOCK])
    
    pre_hook_inputs = {
        "shuffled_atoms": [{"atom_id": "1", "quote": "heavy", "reasoning": "heavy", "boolean": True}],
        "heavy_root_field": "should_be_pruned",
        "inputs": {"good_data": "keep"}
    }
    strategy.run_pre_hooks = AsyncMock(return_value=MagicMock(inputs=pre_hook_inputs))
    strategy.run_post_hooks = AsyncMock(return_value=MagicMock(inputs={"final": "output"}))
    
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
    assert "heavy_root_field" not in state_data
    assert state_data.get("inputs", {}).get("good_data") == "keep"


from backend_v2.exceptions import TokenLimitExceededError

@pytest.mark.asyncio
async def test_llm_strategy_token_limit_breach() -> None:
    """Epic 35 Phase 3: Test that token max breach raises TokenLimitExceededError."""
    exec_repo = AsyncMock()
    workflow_repo = AsyncMock()
    comp_repo = AsyncMock()
    identity_repo = AsyncMock()
    audit_repo = AsyncMock()
    system_repo = AsyncMock()
    prompt_compiler = MagicMock()
    
    strategy = LLMNodeStrategy(
        exec_repo=exec_repo,
        workflow_repo=workflow_repo,
        comp_repo=comp_repo,
        identity_repo=identity_repo,
        audit_repo=audit_repo,
        system_repo=system_repo,
        prompt_compiler=prompt_compiler,
    )
    
    step_rule = MagicMock(spec=StepRule)
    step_rule.id = "step_token_limit"
    step_rule.task_blueprint = "bp_123"
    step_rule.input_mappings = {"massive_doc": "$inputs.huge_data"}
    step_rule.allowed_mcp_tools = []
    
    projector = MagicMock(spec=StateProjector)
    projector.snapshot = []
    
    context = StrategyContext(
        execution_id="exec_1",
        workflow_id="wf_1",
        model_strategy="test_strategy",
        metadata={"profile_id": "prof_1", "target_locale": "en"},
        expected_inputs=None,
    )
    
    workflow_repo.get_step_by_id = AsyncMock(return_value={"id": "step_11112222333344445555666677778888", "slug": "test", "name": {"default_locale": "en", "translations": {"en": "test"}}, "type": "llm", "model_strategy": "test_mock", "prompt_blocks": ["comp_1234567890abcdef1234567890abcdef"]})
    workflow_repo.get_workflow = AsyncMock(return_value=None)
    comp_repo.get_all_prompt_blocks = AsyncMock(return_value=[MOCK_MATRIX_BLOCK])
    
    pre_hook_inputs = {
        "inputs": {"huge_data": "A" * 500000}
    }
    strategy.run_pre_hooks = AsyncMock(return_value=MagicMock(inputs=pre_hook_inputs))
    
    with patch("litellm.token_counter", return_value=1000001):
        with pytest.raises(TokenLimitExceededError):
            await strategy.execute(step_rule, projector, context, None, None)


@pytest.mark.asyncio
async def test_llm_strategy_synthesis_output_profile() -> None:
    """Epic 35 Phase 3: Test that Synthesis tasks use SduiResponseList schema and map chunks."""
    exec_repo = AsyncMock()
    workflow_repo = AsyncMock()
    comp_repo = AsyncMock()
    identity_repo = AsyncMock()
    audit_repo = AsyncMock()
    system_repo = AsyncMock()
    prompt_compiler = MagicMock()
    
    strategy = LLMNodeStrategy(
        exec_repo=exec_repo,
        workflow_repo=workflow_repo,
        comp_repo=comp_repo,
        identity_repo=identity_repo,
        audit_repo=audit_repo,
        system_repo=system_repo,
        prompt_compiler=prompt_compiler,
    )
    
    step_rule = MagicMock(spec=StepRule)
    step_rule.id = "step_synthesis"
    step_rule.task_blueprint = "bp_123"
    step_rule.input_mappings = {}
    step_rule.allowed_mcp_tools = []
    
    projector = MagicMock(spec=StateProjector)
    projector.snapshot = []
    
    context = StrategyContext(
        execution_id="exec_1",
        workflow_id="wf_1",
        model_strategy="test_strategy",
        metadata={"profile_id": "prof_1", "target_locale": "en"},
        expected_inputs=None,
    )
    
    workflow_repo.get_step_by_id = AsyncMock(return_value={"id": "step_11112222333344445555666677778888", "slug": "test", "name": {"default_locale": "en", "translations": {"en": "test"}}, "type": "llm", "model_strategy": "test_mock", "prompt_blocks": ["comp_1234567890abcdef1234567890abcdef"]})
    
    mock_workflow_def = {
        "id": "wf_1234567890abcdef1234567890abcdef",
        "slug": "test-workflow",
        "name": "Test Workflow",
        "description": "Test description",
        "status": "active",
        "version": 1,
        "default_profile_id": "prof_1",
        "output_profiles": {
            "prof_1": {
                "name": {"default_locale": "en", "translations": {"en": "Management Summary"}},
                "description": {"default_locale": "en", "translations": {"en": "Summary desc"}},
                "layouts": []
            }
        },
        "steps": []
    }
    workflow_repo.get_workflow = AsyncMock(return_value=mock_workflow_def)
    comp_repo.get_all_prompt_blocks = AsyncMock(return_value=[MOCK_MATRIX_BLOCK])
    
    pre_hook_inputs = {}
    strategy.run_pre_hooks = AsyncMock(return_value=MagicMock(inputs=pre_hook_inputs))
    strategy.run_post_hooks = AsyncMock(return_value=MagicMock(inputs={"final": "output"}))
    
    mock_client = MagicMock()
    mock_result = MagicMock()
    mock_result.model_dump.return_value = {"blocks": [{"block_type": "hero_insight"}]}
    mock_client.run_structured_task = AsyncMock(return_value=(mock_result, {}))
    
    mock_from_strategy = AsyncMock(return_value=mock_client)
    with patch("backend_v2.services.orchestrator.strategies.llm.LLMClient.from_strategy", new=mock_from_strategy):
        with patch("backend_v2.services.orchestrator.chunking_service.ChunkingService.chunk_payload", return_value=[None]):
            res = await strategy.execute(step_rule, projector, context, None, None)
            
    assert len(res) == 1
    call_args = mock_client.run_structured_task.call_args
    assert call_args is not None
    assert call_args.kwargs["max_retries"] == 3
    assert call_args.kwargs["response_model"].__name__ == "SduiResponseList"


@pytest.mark.asyncio
async def test_llm_strategy_state_leakage_prevention() -> None:
    """Epic 32: Test that State Leakage (Zombie Map-Reduce) is prevented if step has no matrices."""
    exec_repo = AsyncMock()
    workflow_repo = AsyncMock()
    comp_repo = AsyncMock()
    identity_repo = AsyncMock()
    audit_repo = AsyncMock()
    system_repo = AsyncMock()
    prompt_compiler = MagicMock()
    
    strategy = LLMNodeStrategy(
        exec_repo=exec_repo,
        workflow_repo=workflow_repo,
        comp_repo=comp_repo,
        identity_repo=identity_repo,
        audit_repo=audit_repo,
        system_repo=system_repo,
        prompt_compiler=prompt_compiler,
    )
    
    step_rule = MagicMock(spec=StepRule)
    step_rule.id = "step_leakage"
    step_rule.task_blueprint = "bp_123"
    step_rule.input_mappings = {}
    step_rule.allowed_mcp_tools = []
    
    projector = MagicMock(spec=StateProjector)
    projector.snapshot = []
    
    context = StrategyContext(
        execution_id="exec_1",
        workflow_id="wf_1",
        model_strategy="test_strategy",
        metadata={"profile_id": "prof_1", "target_locale": "en"},
        expected_inputs=None,
    )
    
    # Mock block without 'category_id' == 'matrix'
    mock_step_def = {
        "id": "step_11112222333344445555666677778888", 
        "slug": "t", 
        "name": {"default_locale": "en", "translations": {"en": "Test Step"}}, 
        "type": "llm", 
        "model_strategy": "test_mock", 
        "prompt_blocks": ["comp_1234567890abcdef1234567890abcdef"]
    }
    workflow_repo.get_step_by_id = AsyncMock(return_value=mock_step_def)
    workflow_repo.get_workflow = AsyncMock(return_value=None)
    comp_repo.get_all_prompt_blocks = AsyncMock(return_value=[MOCK_INSTRUCTION_BLOCK])
    
    pre_hook_inputs = {
        "shuffled_atoms": [{"atom_id": "1", "boolean": True}]
    }
    strategy.run_pre_hooks = AsyncMock(return_value=MagicMock(inputs=pre_hook_inputs))
    strategy.run_post_hooks = AsyncMock(return_value=MagicMock(inputs={"final": "output"}))
    
    mock_client = MagicMock()
    mock_result = MagicMock()
    mock_result.model_dump.return_value = {"evaluations": []}
    mock_client.run_structured_task = AsyncMock(return_value=(mock_result, {}))
    
    mock_from_strategy = AsyncMock(return_value=mock_client)
    with patch("backend_v2.services.orchestrator.strategies.llm.LLMClient.from_strategy", new=mock_from_strategy):
        with patch("backend_v2.services.orchestrator.chunking_service.ChunkingService.chunk_payload") as mock_chunk:
            # Should not call chunking service because is_matrix_step is False!
            await strategy.execute(step_rule, projector, context, None, None)
            
    # Verification: Chunking payload should NEVER be called!
    mock_chunk.assert_not_called()

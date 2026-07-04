import asyncio
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend_v2.models.v2_core import PromptBlock
from backend_v2.services.orchestrator.strategies.llm_execution.chunk_worker import (
    ChunkWorker,
    resolve_majority_vote,
)


@pytest.fixture
def base_votes() -> list[dict[str, Any]]:
    return [
        {
            "exact_quotes": ["q1"],
            "contextual_override": False,
            "semantic_reasoning": "reason 1",
        },
        {
            "exact_quotes": ["q1"],
            "contextual_override": False,
            "semantic_reasoning": "reason 2",
        },
        {
            "exact_quotes": ["q2"],
            "contextual_override": False,
            "semantic_reasoning": "reason 3",
        },
    ]


def test_resolve_majority_vote_pure_majority() -> None:
    """End-to-end test of resolve_majority_vote with pure majority consensus."""
    criteria_blocks = [
        PromptBlock.model_validate(
            {
                "id": "blk_12345678901234567890123456789012",
                "slug": "test_slug",
                "label": {"default_locale": "en", "translations": {"en": "Label", "fi": "Testi"}},
                "description": {"default_locale": "en", "translations": {"en": "Desc", "fi": "Testi"}},
                "type": "string",
                "category_id": "matrix",
                "scale_min": 1,
                "scale_max": 5,
                "scales": [
                    {
                        "score": 1,
                        "ai_label": "Scale 1",
                        "claims": [
                            {
                                "label": {"default_locale": "en", "translations": {"en": "Claim 1", "fi": "Väite 1"}},
                                "ai_description": "Claim 1 Desc",
                                "tda_assertions": [
                                    {
                                        "tda_id": "tda_11111111111111111111111111111111",
                                        "concept_description": "Atom 1",
                                        "inverse_evidence": True,
                                        "aggregation_mode": "EXISTS",
                                    },
                                    {
                                        "tda_id": "tda_22222222222222222222222222222222",
                                        "concept_description": "Atom 2",
                                        "inverse_evidence": False,
                                        "aggregation_mode": "EXISTS",
                                    },
                                ],
                            },
                        ],
                    }
                ],
            }
        )
    ]

    res_list = [
        {"evaluations": [{"atom_id": "tda_11111111111111111111111111111111", "exact_quotes": [{"text": "q"}]}]},
        {"evaluations": [{"atom_id": "tda_11111111111111111111111111111111", "exact_quotes": [{"text": "q"}]}]},
        {"evaluations": [{"atom_id": "tda_11111111111111111111111111111111", "exact_quotes": [{"text": "q"}]}]},
    ]

    with patch(
        "backend_v2.services.orchestrator.strategies.llm_execution.chunk_worker.evaluate_extraction"
    ) as mock_eval:
        # Simulate pure majority FAIL
        mock_eval.side_effect = ["PASS", "FAIL", "FAIL"]

        merged = resolve_majority_vote(
            results=res_list,
            has_shuffled_atoms=True,
            chunk_criteria=criteria_blocks,
            user_payload="source",
            global_source_text="source",
            strictness_level=50,
        )

        evals = merged["evaluations"]
        assert len(evals) == 1
        assert evals[0]["status"] == "CONTESTED"
        assert evals[0]["confidence"] == 2 / 3  # 2 FAILs, 1 PASS (confidence <= 0.67 causes override to CONTESTED)
        assert evals[0]["exact_quotes"] == [{"text": "q"}]


@pytest.mark.asyncio
async def test_llm_count_is_standard_when_lightweight() -> None:
    """Test that llm_count=1 when is_lightweight is True."""
    mock_compiler = MagicMock()
    mock_client = AsyncMock()

    with patch(
        "backend_v2.services.orchestrator.strategies.llm_execution.chunk_worker.LLMTaskExecutor"
    ) as MockExecutor:
        mock_executor_instance = MockExecutor.return_value
        # Mock executor to return a valid result to avoid "All LLM calls failed" error
        mock_executor_instance.execute_structured_task = AsyncMock(return_value=(MagicMock(), None))

        mock_compiled_prompt = MagicMock()
        mock_compiled_prompt.static_messages = []
        mock_compiled_prompt.dynamic_messages = []
        mock_compiled_prompt.metadata = {}
        mock_compiler.compile_chunk_prompt.return_value = mock_compiled_prompt

        sem = asyncio.Semaphore(1)
        step_metadata = {"is_lightweight_extraction": True}

        # We patch LLMTaskExecutor to intercept the arguments run_llm_calls passes to it
        # However, run_llm_calls evaluates count internally, so we patch asyncio.TaskGroup to count tasks
        # Simpler approach: we will patch the run_llm_calls inside process_chunk if we could,
        # but since it's nested, we will patch the executor and verify it was called 3 times.

        # Simpler approach: we will patch the run_llm_calls inside process_chunk if we could,
        # but since it's nested, we will patch the executor and verify it was called 3 times.
        await ChunkWorker.process_chunk(
            chunk=None,
            sem=sem,
            compiler=mock_compiler,
            criteria_blocks=[],
            user_payload="<payload>",
            global_source_text="<payload>",
            base_system_prompt="Base prompt",
            has_search=False,
            has_shuffled_atoms=False,
            atom_to_block_ids={},
            effective_mcp_tools=[],
            bound_client=mock_client,
            step_id="step1",
            target_locale="en",
            synthesis_instructions=None,
            output_profile=None,
            step_metadata=step_metadata,
        )

        assert mock_executor_instance.execute_structured_task.call_count == 1


@pytest.mark.asyncio
async def test_llm_count_is_ensemble_when_not_lightweight() -> None:
    """Test that llm_count=3 when is_lightweight is False."""
    mock_compiler = MagicMock()
    mock_client = AsyncMock()

    with patch(
        "backend_v2.services.orchestrator.strategies.llm_execution.chunk_worker.LLMTaskExecutor"
    ) as MockExecutor:
        mock_executor_instance = MockExecutor.return_value
        mock_executor_instance.execute_structured_task = AsyncMock(return_value=(MagicMock(), None))

        mock_compiled_prompt = MagicMock()
        mock_compiled_prompt.static_messages = []
        mock_compiled_prompt.dynamic_messages = []
        mock_compiled_prompt.metadata = {}
        mock_compiler.compile_chunk_prompt.return_value = mock_compiled_prompt

        sem = asyncio.Semaphore(1)
        step_metadata = {"is_lightweight_extraction": False}

        try:
            await ChunkWorker.process_chunk(
                chunk=None,
                sem=sem,
                compiler=mock_compiler,
                criteria_blocks=[],
                user_payload="<payload>",
                global_source_text="<payload>",
                base_system_prompt="Base prompt",
                has_search=False,
                has_shuffled_atoms=False,
                atom_to_block_ids={},
                effective_mcp_tools=[],
                bound_client=mock_client,
                step_id="step1",
                target_locale="en",
                synthesis_instructions=None,
                output_profile=None,
                step_metadata=step_metadata,
            )
        except Exception:
            pass

        assert mock_executor_instance.execute_structured_task.call_count == 3

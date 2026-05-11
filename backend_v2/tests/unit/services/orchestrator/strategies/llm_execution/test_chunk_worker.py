import asyncio
from collections.abc import Generator
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend_v2.exceptions import AppException
from backend_v2.models.chunking import Chunk
from backend_v2.models.v2_core import PromptBlock
from backend_v2.services.orchestrator.strategies.llm_execution.chunk_worker import ChunkWorker


@pytest.fixture
def mock_executor_class() -> Generator[Any]:
    with patch("backend_v2.services.orchestrator.strategies.llm_execution.chunk_worker.LLMTaskExecutor") as mock_cls:
        yield mock_cls


@pytest.mark.asyncio
async def test_chunk_worker_process_chunk_success(mock_executor_class: Any) -> None:
    """Test successful execution of a chunk through structured LLM task."""
    mock_compiler = MagicMock()
    mock_compiler.compile_xml_rubrics.return_value = "<xml>rubrics</xml>"
    mock_schema = MagicMock()
    mock_compiler.build_dynamic_schema.return_value = mock_schema

    mock_client = AsyncMock()
    mock_result = MagicMock()
    mock_result.model_dump.return_value = {"answer": "42"}

    mock_executor_instance = mock_executor_class.return_value
    from backend_v2.models.domain.usage import TokenUsage

    mock_executor_instance.execute_structured_task = AsyncMock(
        return_value=(mock_result, TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15))
    )

    sem = asyncio.Semaphore(1)
    chunk = Chunk(parent_id="wf1", index=0, items=[{"atom_id": "a1", "text": "hello"}])

    criteria_blocks = [
        PromptBlock.model_validate(
            {
                "id": "blk_12345678901234567890123456789012",
                "slug": "test_slug",
                "label": {"default_locale": "en", "translations": {"en": "Test Label", "fi": "Testi"}},
                "description": {"default_locale": "en", "translations": {"en": "Test Desc", "fi": "Testi"}},
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
                                        "tda_id": "atom_1",
                                        "ai_rule_description": "Atom 1",
                                        "inverse_evidence": False,
                                        "aggregation_mode": "EXISTS",
                                    },
                                    {
                                        "tda_id": "atom_2",
                                        "ai_rule_description": "Atom 2",
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
    atom_to_block_ids = {"a1": {"blk_12345678901234567890123456789012"}}

    final, usage, traces = await ChunkWorker.process_chunk(
        chunk=chunk,
        sem=sem,
        compiler=mock_compiler,
        criteria_blocks=criteria_blocks,
        user_payload="<payload>",
        base_system_prompt="Base prompt",
        has_search=False,
        has_shuffled_atoms=True,
        atom_to_block_ids=atom_to_block_ids,
        effective_mcp_tools=[],
        bound_client=mock_client,
        step_id="step1",
        target_locale="en",
        synthesis_instructions=None,
        output_profile=None,
    )

    assert final == {"answer": "42"}
    assert usage is not None
    assert usage.prompt_tokens == 10
    assert usage.completion_tokens == 5
    assert traces == []

    # Check compiler was called correctly
    mock_compiler.compile_xml_rubrics.assert_called_once()
    mock_compiler.build_dynamic_schema.assert_called_once()

    # Check that client was called with correct arguments
    mock_executor_instance.execute_structured_task.assert_called_once()
    kwargs = mock_executor_instance.execute_structured_task.call_args.kwargs
    assert kwargs["response_model"] == mock_schema
    assert kwargs["mock_identity"] == "step1"


@pytest.mark.asyncio
async def test_chunk_worker_process_chunk_failure(mock_executor_class: Any) -> None:
    """Test that execution failure correctly raises AppException."""
    mock_compiler = MagicMock()
    mock_client = AsyncMock()

    mock_executor_instance = mock_executor_class.return_value
    mock_executor_instance.execute_structured_task.side_effect = Exception("LLM connection error")

    sem = asyncio.Semaphore(1)

    with pytest.raises(AppException) as exc_info:
        await ChunkWorker.process_chunk(
            chunk=None,
            sem=sem,
            compiler=mock_compiler,
            criteria_blocks=[],
            user_payload="<payload>",
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
        )

    assert exc_info.value.status_code == 500
    assert "LLM connection error" in str(exc_info.value.message)

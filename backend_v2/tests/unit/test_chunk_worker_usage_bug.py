import asyncio
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import BaseModel

from backend_v2.models.domain.usage import TokenUsage
from backend_v2.services.orchestrator.strategies.llm_execution.chunk_worker import ChunkWorker


class MockResult(BaseModel):
    evaluations: list[Any] = []


@pytest.mark.asyncio
async def test_chunk_worker_usage_name_error() -> None:
    """Test ChunkWorker.process_chunk does not raise NameError due to usage/chunk_usage discrepancy."""
    sem = asyncio.Semaphore(1)

    # Mock compiler
    compiler = MagicMock()
    compiler.compile_xml_rubrics.return_value = "<rubrics></rubrics>"
    # This test mocks compiler, so it doesn't need modification
    compiler.calibrate_strictness.return_value = "Balanced"
    compiler.get_critical_language_mandate.return_value = "Use English"

    # Mock schema return to avoid magicmock on model_dump
    mock_schema = MagicMock()
    mock_schema.model_validate.return_value.model_dump.return_value = {"evaluations": []}
    compiler.build_dynamic_schema.return_value = mock_schema

    # Mock executor & run_structured_task via bound_client
    mock_client = AsyncMock()
    mock_client.run_structured_task.return_value = (
        MockResult(evaluations=[]),
        TokenUsage(total_tokens=100, prompt_tokens=50, completion_tokens=50),
    )

    # Calls ChunkWorker.process_chunk
    # This should complete without raising NameError: name 'usage' is not defined
    res, usage, traces, pctx = await ChunkWorker.process_chunk(
        chunk=None,
        sem=sem,
        compiler=compiler,
        criteria_blocks=[],
        user_payload="test payload",
        global_source_text="test payload",
        base_system_prompt="base system prompt",
        has_search=False,
        has_shuffled_atoms=False,
        atom_to_block_ids={},
        effective_mcp_tools=[],
        bound_client=mock_client,
        step_id="step_test",
        target_locale="fi",
        synthesis_instructions=None,
        output_profile=None,
        strictness_level=85,
    )

    assert res == {"evaluations": []}
    assert usage is not None
    assert usage.total_tokens == 100
    assert traces == []

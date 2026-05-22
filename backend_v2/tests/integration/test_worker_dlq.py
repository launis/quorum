import asyncio
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import BaseModel, Field

from backend_v2.exceptions import LLMSchemaValidationError
from backend_v2.services.orchestrator.strategies.llm_execution.chunk_worker import ChunkWorker


class MockSchema(BaseModel):
    exact_quote: str = Field(max_length=1500)


@pytest.mark.asyncio
async def test_pydantic_max_length_fail_fast_and_dlq_routing() -> None:
    # Create the mock chunk and tools
    class DummyChunk:
        def __init__(self, items: list[Any]) -> None:
            self.items = items

    chunk_obj = DummyChunk([])
    sem = asyncio.Semaphore(1)

    # Mock prompt compiler
    compiler = MagicMock()
    compiler.compile_xml_rubrics.return_value = ""
    compiler.build_dynamic_schema.return_value = MockSchema
    compiler.calibrate_strictness.return_value = ""

    # Mock LLMTaskExecutor to raise LLMSchemaValidationError due to max_length
    with patch(
        "backend_v2.services.orchestrator.strategies.llm_execution.chunk_worker.LLMTaskExecutor"
    ) as mock_executor:
        mock_instance = mock_executor.return_value
        error = LLMSchemaValidationError(
            validation_error_msg="exact_quote max_length exceeded",
            raw_llm_payload="{}",
            token_usage=None,
            is_eof=False,
        )
        mock_instance.execute_structured_task = AsyncMock(side_effect=error)

        # Execute process_chunk
        chunk_final, chunk_usage, chunk_traces = await ChunkWorker.process_chunk(
            chunk=chunk_obj,
            sem=sem,
            compiler=compiler,
            criteria_blocks=[],
            user_payload="",
            base_system_prompt="",
            has_search=False,
            has_shuffled_atoms=False,
            atom_to_block_ids={},
            effective_mcp_tools=[],
            bound_client=MagicMock(),
            step_id="step_1",
            target_locale="en",
            synthesis_instructions=None,
            output_profile=None,
            strictness_level=50,
        )

        # Assert returned DLQ status
        assert chunk_final.get("_dlq_status") == "FAILED/DLQ"
        assert "exact_quote max_length exceeded" in str(chunk_final.get("reason"))

        # Assert execute_structured_task was called exactly once (no retries because max_schema_retries=1)
        # Wait, since max_schema_retries=1, LLMTaskExecutor handles it and raises the error on the first failure.
        # It's called once.
        mock_instance.execute_structured_task.assert_called_once()


@pytest.mark.asyncio
async def test_programmatic_errors_bubble_up_and_crash_fail_fast() -> None:
    # Create the mock chunk and tools
    class DummyChunk:
        def __init__(self, items: list[Any]) -> None:
            self.items = items

    chunk_obj = DummyChunk([])
    sem = asyncio.Semaphore(1)

    # Mock prompt compiler
    compiler = MagicMock()
    compiler.compile_xml_rubrics.return_value = ""
    compiler.build_dynamic_schema.return_value = MockSchema
    compiler.calibrate_strictness.return_value = ""

    # Mock LLMTaskExecutor to raise standard TypeError
    with patch(
        "backend_v2.services.orchestrator.strategies.llm_execution.chunk_worker.LLMTaskExecutor"
    ) as mock_executor:
        mock_instance = mock_executor.return_value
        mock_instance.execute_structured_task = AsyncMock(side_effect=TypeError("string indices must be integers"))

        # Execute process_chunk and assert TypeError bubbles up
        with pytest.raises(TypeError) as exc_info:
            await ChunkWorker.process_chunk(
                chunk=chunk_obj,
                sem=sem,
                compiler=compiler,
                criteria_blocks=[],
                user_payload="",
                base_system_prompt="",
                has_search=False,
                has_shuffled_atoms=False,
                atom_to_block_ids={},
                effective_mcp_tools=[],
                bound_client=MagicMock(),
                step_id="step_1",
                target_locale="en",
                synthesis_instructions=None,
                output_profile=None,
                strictness_level=50,
            )
        assert "string indices must be integers" in str(exc_info.value)


@pytest.mark.asyncio
async def test_worker_evaluate_chunk_job_aborts_on_dlq_status() -> None:
    from backend_v2.exceptions import AppException
    from backend_v2.worker import evaluate_chunk_job

    # Mock ChunkWorker.process_chunk to return a DLQ status dict
    with patch("backend_v2.worker.ChunkWorker.process_chunk") as mock_process_chunk:
        mock_process_chunk.return_value = (
            {"_dlq_status": "FAILED/DLQ", "reason": "Test DLQ Trigger"},
            None,
            [],
        )

        ctx = {"redis": MagicMock()}  # Redis client

        with pytest.raises(AppException) as exc_info:
            await evaluate_chunk_job(
                ctx=ctx,
                execution_id="exec_123",
                step_id="step_1",
                chunk_index=0,
                total_chunks=1,
                file_path=None,
                chunk_items=[],
                criteria_blocks_dump=[],
                base_system_prompt="",
                has_search=False,
                has_shuffled_atoms=False,
                atom_to_block_ids={},
                effective_mcp_tools=[],
                target_locale="en",
                synthesis_instructions=None,
                strictness_level=50,
            )

        assert exc_info.value.status_code == 500
        assert "Chunk execution failed and routed to DLQ" in exc_info.value.message

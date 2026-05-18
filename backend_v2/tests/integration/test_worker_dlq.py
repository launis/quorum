import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from backend_v2.services.orchestrator.strategies.llm_execution.chunk_worker import ChunkWorker
from backend_v2.exceptions import LLMSchemaValidationError
import asyncio
from pydantic import BaseModel, Field

class MockSchema(BaseModel):
    exact_quote: str = Field(max_length=1500)

@pytest.mark.asyncio
async def test_pydantic_max_length_fail_fast_and_dlq_routing():
    # Mock LLM response with an exact_quote of 1501 chars
    long_quote = "a" * 1501
    
    # Create the mock chunk and tools
    class DummyChunk:
        def __init__(self, items):
            self.items = items
            
    chunk_obj = DummyChunk([])
    sem = asyncio.Semaphore(1)
    
    # Mock prompt compiler
    compiler = MagicMock()
    compiler.compile_xml_rubrics.return_value = ""
    compiler.build_dynamic_schema.return_value = MockSchema
    compiler.calibrate_strictness.return_value = ""
    
    # Mock LLMTaskExecutor to raise LLMSchemaValidationError due to max_length
    with patch("backend_v2.services.orchestrator.strategies.llm_execution.chunk_worker.LLMTaskExecutor") as mock_executor:
        mock_instance = mock_executor.return_value
        error = LLMSchemaValidationError(validation_error_msg="exact_quote max_length exceeded", raw_llm_payload="{}", token_usage=None, is_eof=False)
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
        assert "exact_quote max_length exceeded" in chunk_final.get("reason")
        
        # Assert execute_structured_task was called exactly once (no retries because max_schema_retries=1)
        # Wait, since max_schema_retries=1, LLMTaskExecutor handles it and raises the error on the first failure.
        # It's called once.
        mock_instance.execute_structured_task.assert_called_once()

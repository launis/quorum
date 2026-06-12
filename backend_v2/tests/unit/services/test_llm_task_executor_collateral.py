from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import BaseModel

from backend_v2.exceptions import SemanticEvidenceError
from backend_v2.services.llm_task_executor import LLMTaskExecutor


class AtomResponse(BaseModel):
    atom_id: str
    exact_quote: str | None = None
    contextual_override: bool = False
    semantic_reasoning: str = ""

class ChunkResponseSchema(BaseModel):
    reasoning_trace: str
    evaluation_notes: str
    evaluations: list[AtomResponse]

@pytest.mark.asyncio
async def test_collateral_damage_prevention():
    """Test that a single hallucinated quote in a chunk doesn't nuke the valid ones during fallback."""
    mock_compiler = MagicMock()
    mock_compiler.get_schema_healing_prompt.return_value = "fix it"
    executor = LLMTaskExecutor(prompt_compiler=mock_compiler)
    mock_client = AsyncMock()

    # The LLM returns a chunk with 1 valid quote and 1 hallucinated quote.
    expected_model = ChunkResponseSchema(
        reasoning_trace="trace",
        evaluation_notes="notes",
        evaluations=[
            AtomResponse(atom_id="valid_atom", exact_quote="real text", semantic_reasoning="good reasoning"),
            AtomResponse(atom_id="hallucinated_atom", exact_quote="fake text", semantic_reasoning="bad reasoning")
        ]
    )

    # We mock LLM returning this same invalid chunk twice (it fails to heal)
    mock_client.run_structured_task.side_effect = [
        (expected_model, {"total_tokens": 10, "prompt_tokens": 5, "completion_tokens": 5}),
        (expected_model, {"total_tokens": 10, "prompt_tokens": 5, "completion_tokens": 5}),
    ]

    # We mock validate_evidence to pass for "real text" and fail for "fake text"
    def mock_validate(pdf_text, exact_quote, **kwargs):
        if exact_quote == "fake text":
            raise SemanticEvidenceError(message="fail")
        return exact_quote

    with patch("backend_v2.services.llm_task_executor.AnchorValidationService.validate_evidence", side_effect=mock_validate):
        res_model, _ = await executor.execute_structured_task(
            client=mock_client,
            messages=[{"role": "user", "content": "hello world this is a test payload"}],
            response_model=ChunkResponseSchema,
            max_logical_retries=1,
            validation_context={"source_text": "this has real text"}
        )

        assert len(res_model.evaluations) == 2

        # Valid atom should be preserved
        assert res_model.evaluations[0].atom_id == "valid_atom"
        assert res_model.evaluations[0].exact_quote == "real text"
        assert res_model.evaluations[0].semantic_reasoning == "good reasoning"

        # Hallucinated atom should be fallen back
        assert res_model.evaluations[1].atom_id == "hallucinated_atom"
        assert res_model.evaluations[1].exact_quote is None
        assert res_model.evaluations[1].semantic_reasoning == "[SYSTEM ERROR: LLM Unable to verify.]"

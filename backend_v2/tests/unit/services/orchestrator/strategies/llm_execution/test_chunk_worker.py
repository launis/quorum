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
    mock_validated = MagicMock()
    mock_validated.model_dump.return_value = {
        "evaluations": [
            {
                "atom_id": "a1",
                "exact_quotes": ["yes"],
                "contextual_override": False,
                "semantic_reasoning": "Because...\n\n[5. VALIDATION DECISION: PASS]",
                "status": "PASS",
            }
        ]
    }

    mock_atom = MagicMock()
    mock_atom.atom_id = "a1"
    mock_atom.exact_quotes = "yes"
    mock_atom.contextual_override = False
    mock_atom.semantic_reasoning = "Because..."
    mock_atom.model_copy.return_value = mock_atom
    mock_validated.evaluations = [mock_atom]

    mock_validated.model_copy.return_value = mock_validated
    mock_schema.model_validate.return_value = mock_validated
    mock_compiler.build_dynamic_schema.return_value = mock_schema

    mock_client = AsyncMock()
    mock_result = MagicMock()
    mock_result.model_dump.return_value = {
        "evaluations": [
            {
                "atom_id": "a1",
                "exact_quotes": ["yes"],
                "contextual_override": False,
                "semantic_reasoning": "Because...",
            }
        ]
    }

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
                                        "tda_id": "tda_11111111111111111111111111111111",
                                        "concept_description": "Atom 1",
                                        "inverse_evidence": False,
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
    atom_to_block_ids = {"a1": {"blk_12345678901234567890123456789012"}}

    final, usage, traces, pctx = await ChunkWorker.process_chunk(
        chunk=chunk,
        sem=sem,
        compiler=mock_compiler,
        criteria_blocks=criteria_blocks,
        user_payload="<payload>",
        global_source_text="<payload>",
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

    assert "evaluations" in final
    assert final["evaluations"][0]["status"] in ["PASS", "FAIL", "DLQ"]
    assert "VALIDATION DECISION:" in final["evaluations"][0]["semantic_reasoning"]
    assert usage is not None
    assert usage.prompt_tokens == 10
    assert usage.completion_tokens == 5
    assert traces == []

    # V3: ChunkWorker delegates to compile_chunk_prompt (which internally calls compile_xml_rubrics)
    mock_compiler.compile_chunk_prompt.assert_called_once()
    mock_compiler.build_dynamic_schema.assert_called_once()

    # Check that client was called with correct arguments
    mock_executor_instance.execute_structured_task.assert_called_once()
    kwargs = mock_executor_instance.execute_structured_task.call_args.kwargs
    assert kwargs["response_model"] == mock_schema
    assert kwargs["mock_identity"] == "step1"


@pytest.mark.asyncio
async def test_chunk_worker_process_chunk_failure(mock_executor_class: Any) -> None:
    """Test that execution failure correctly routes to DLQ."""
    mock_compiler = MagicMock()
    mock_client = AsyncMock()

    mock_executor_instance = mock_executor_class.return_value
    mock_executor_instance.execute_structured_task.side_effect = AppException("LLM connection error", status_code=500)

    sem = asyncio.Semaphore(1)

    crit_std = PromptBlock.model_validate(
        {
            "id": "crit_12345678901234567890123456789012",
            "slug": "criteria_slug",
            "label": {"default_locale": "en", "translations": {"en": "Criteria Label", "fi": "Kriteeri"}},
            "description": {"default_locale": "en", "translations": {"en": "Criteria Desc", "fi": "Kriteeri"}},
            "type": "string",
            "category_id": "system_rule",
            "scales": None,
        }
    )

    final, usage, traces, pctx = await ChunkWorker.process_chunk(
        chunk=None,
        sem=sem,
        compiler=mock_compiler,
        criteria_blocks=[crit_std],
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
    )

    assert final["crit_12345678901234567890123456789012"]["status"] == "DLQ"
    assert "LLM connection error" in final["crit_12345678901234567890123456789012"]["semantic_reasoning"]
    assert usage is None
    assert traces == []


def test_deterministic_extraction_scoring() -> None:
    """Test the evaluate_extraction pure function."""
    from unittest.mock import patch

    from pydantic import BaseModel

    from backend_v2.exceptions import SemanticEvidenceError
    from backend_v2.services.orchestrator.strategies.llm_execution.chunk_worker import evaluate_extraction

    class MockExtraction(BaseModel):
        exact_quotes: list[str] | None = None
        contextual_override: bool = False
        semantic_reasoning: str | None = ""
        premise_1_quote: str | None = None

    # Track B (Semantic Override = False, No quote) -> FAIL
    ext1 = MockExtraction(exact_quotes=[], contextual_override=False)
    assert evaluate_extraction(ext1, "test text", False) == "FAIL"

    # Track B (Semantic Override = True, No exact_quote, but has premise) -> PASS
    ext2 = MockExtraction(
        exact_quotes=[], contextual_override=True, semantic_reasoning="Model reasoning", premise_1_quote="test text"
    )
    with patch(
        "backend_v2.services.orchestrator.anchor_validation_service.AnchorValidationService.validate_evidence"
    ) as mock_val:
        assert evaluate_extraction(ext2, "test text", False) == "PASS"

    # Track A (Physical Match) -> PASS
    ext3 = MockExtraction(exact_quotes=["matched quote"], contextual_override=False)
    with patch(
        "backend_v2.services.orchestrator.anchor_validation_service.AnchorValidationService.validate_evidence"
    ) as mock_val:
        assert evaluate_extraction(ext3, "test text", False) == "PASS"

    # Track A (Physical Match - but fails lexical verification) -> FAIL
    with patch(
        "backend_v2.services.orchestrator.anchor_validation_service.AnchorValidationService.validate_evidence"
    ) as mock_val:
        mock_val.side_effect = SemanticEvidenceError(message="Not found")
        assert evaluate_extraction(ext3, "test text", False) == "FAIL"

    # Trace Contradiction test: [5. VALIDATION DECISION: FAIL] in semantic_reasoning -> FAIL
    ext_contradiction = MockExtraction(
        exact_quotes=["matched quote"],
        contextual_override=False,
        semantic_reasoning="Some reasoning... [5. VALIDATION DECISION: FAIL]",
    )
    assert evaluate_extraction(ext_contradiction, "matched quote", False) == "FAIL"

    # Negative condition
    # Track B -> FAIL becomes PASS
    assert evaluate_extraction(ext1, "test text", True) == "PASS"
    # Track B -> PASS becomes FAIL for negative rules
    assert evaluate_extraction(ext2, "test text", True) == "FAIL"


@pytest.mark.asyncio
async def test_chunk_worker_process_chunk_with_instruction_block(mock_executor_class: Any) -> None:
    """Test standard block evaluation skips instruction blocks which are raw strings."""
    mock_compiler = MagicMock()
    mock_compiler.compile_xml_rubrics.return_value = "<xml>rubrics</xml>"
    mock_schema = MagicMock()

    mock_validated = MagicMock()
    mock_validated.model_dump.return_value = {
        "inst_12345678901234567890123456789012": "This is raw instruction text",
        "crit_12345678901234567890123456789012": {
            "exact_quotes": ["yes"],
            "contextual_override": False,
            "semantic_reasoning": "Standard justification",
            "status": "PASS",
        },
    }
    mock_crit = MagicMock()
    mock_crit.exact_quotes = "yes"
    mock_crit.contextual_override = False
    mock_crit.semantic_reasoning = "Standard justification"
    mock_crit.model_copy.return_value = mock_crit
    mock_validated.crit_12345678901234567890123456789012 = mock_crit
    mock_validated.inst_12345678901234567890123456789012 = "This is raw instruction text"

    mock_validated.model_copy.return_value = mock_validated
    mock_schema.model_validate.return_value = mock_validated
    mock_compiler.build_dynamic_schema.return_value = mock_schema

    mock_client = AsyncMock()
    mock_result = MagicMock()

    mock_executor_instance = mock_executor_class.return_value
    from backend_v2.models.domain.usage import TokenUsage

    mock_executor_instance.execute_structured_task = AsyncMock(
        return_value=(mock_result, TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15))
    )

    sem = asyncio.Semaphore(1)

    crit_inst = PromptBlock.model_validate(
        {
            "id": "inst_12345678901234567890123456789012",
            "slug": "instruction_slug",
            "label": {"default_locale": "en", "translations": {"en": "Instruction Label", "fi": "Ohje"}},
            "description": {"default_locale": "en", "translations": {"en": "Instruction Desc", "fi": "Ohje"}},
            "type": "instruction",
            "category_id": "system_rule",
            "scales": None,
        }
    )
    crit_std = PromptBlock.model_validate(
        {
            "id": "crit_12345678901234567890123456789012",
            "slug": "criteria_slug",
            "label": {"default_locale": "en", "translations": {"en": "Criteria Label", "fi": "Kriteeri"}},
            "description": {"default_locale": "en", "translations": {"en": "Criteria Desc", "fi": "Kriteeri"}},
            "type": "string",
            "category_id": "system_rule",
            "scales": None,
        }
    )

    criteria_blocks = [crit_inst, crit_std]

    # Map the model dump keys to match the criteria IDs
    mock_result.model_dump.return_value = {
        "inst_12345678901234567890123456789012": "This is raw instruction text",
        "crit_12345678901234567890123456789012": {
            "exact_quotes": ["yes"],
            "contextual_override": False,
            "semantic_reasoning": "Standard justification",
        },
    }

    final, usage, traces, pctx = await ChunkWorker.process_chunk(
        chunk=None,
        sem=sem,
        compiler=mock_compiler,
        criteria_blocks=criteria_blocks,
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
    )

    assert final["inst_12345678901234567890123456789012"] == "This is raw instruction text"
    assert final["crit_12345678901234567890123456789012"]["status"] in ["PASS", "FAIL", "DLQ"]


@pytest.mark.asyncio
async def test_chunk_worker_exception_group_dlq_masking(mock_executor_class: Any) -> None:
    """Test that ExceptionGroup correctly unwraps AppException for DLQ reason."""
    mock_compiler = MagicMock()
    mock_client = AsyncMock()

    mock_executor_instance = mock_executor_class.return_value

    # We simulate a TaskGroup raising an ExceptionGroup containing an AppException
    def raise_exception_group(*args: Any, **kwargs: Any) -> None:
        raise ExceptionGroup(
            "unhandled errors in a TaskGroup", [AppException("Upstream LLM service timed out", status_code=500)]
        )

    mock_executor_instance.execute_structured_task.side_effect = raise_exception_group

    sem = asyncio.Semaphore(1)

    crit_std = PromptBlock.model_validate(
        {
            "id": "crit_12345678901234567890123456789012",
            "slug": "criteria_slug",
            "label": {"default_locale": "en", "translations": {"en": "Criteria Label", "fi": "Kriteeri"}},
            "description": {"default_locale": "en", "translations": {"en": "Criteria Desc", "fi": "Kriteeri"}},
            "type": "string",
            "category_id": "system_rule",
            "scales": None,
        }
    )

    final, usage, traces, pctx = await ChunkWorker.process_chunk(
        chunk=None,
        sem=sem,
        compiler=mock_compiler,
        criteria_blocks=[crit_std],
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
    )

    assert final["crit_12345678901234567890123456789012"]["status"] == "DLQ"
    # This assertion verifies that the DLQ reason extracts the actual inner exception's message
    # rather than just printing the generic TaskGroup wrapper message.
    assert "Upstream LLM service timed out" in final["crit_12345678901234567890123456789012"]["semantic_reasoning"]
    assert "unhandled errors in a TaskGroup" not in final["crit_12345678901234567890123456789012"]["semantic_reasoning"]

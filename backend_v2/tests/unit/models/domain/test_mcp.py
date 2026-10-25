"""Unit tests for MCP domain models and citation extraction DTOs."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from backend_v2.models.domain.mcp import (
    CitationCorrectionResult,
    CitationExtractionFailure,
    CitationExtractionItemDTO,
    CitationExtractionResult,
    MCPRetrievalResultDTO,
    MCPSynthesisInstructionsDTO,
    MCPToolLoopResult,
    OpenAIFunctionCallDTO,
    OpenAIProbeResponseDTO,
    OpenAIToolCallDTO,
)
from backend_v2.models.domain.system_config import MCPAuditTrace


def test_openai_function_call_dto_valid() -> None:
    """Verify OpenAIFunctionCallDTO validates both string and typed argument dictionaries."""
    data = {"name": "mcp_tavily_search", "arguments": '{"query": "test"}'}
    model = OpenAIFunctionCallDTO.model_validate(data)
    assert model.name == "mcp_tavily_search"
    assert model.arguments == '{"query": "test"}'

    typed_model = OpenAIFunctionCallDTO(
        name="mcp_tavily_search",
        arguments={"query": "test", "max_results": 5, "include_raw": False},
    )
    assert typed_model.arguments == {"query": "test", "max_results": 5, "include_raw": False}


def test_openai_function_call_dto_forbids_extra_and_invalid_types() -> None:
    """Verify OpenAIFunctionCallDTO rejects extra fields and invalid argument types."""
    data = {"name": "mcp_tavily_search", "arguments": '{"query": "test"}', "extra_field": "not allowed"}
    with pytest.raises(ValidationError):
        OpenAIFunctionCallDTO.model_validate(data)

    with pytest.raises(ValidationError):
        OpenAIFunctionCallDTO.model_validate({"name": 123, "arguments": "{}"})


def test_openai_tool_call_dto_valid() -> None:
    """Verify OpenAIToolCallDTO validates tool call payloads with default type."""
    data = {
        "id": "call_123",
        "type": "function",
        "function": {"name": "mcp_tavily_search", "arguments": '{"query": "test"}'},
    }
    model = OpenAIToolCallDTO.model_validate(data)
    assert model.id == "call_123"
    assert model.type == "function"
    assert model.function.name == "mcp_tavily_search"


def test_openai_tool_call_dto_accepts_provider_specific_fields_and_rejects_extra() -> None:
    """Verify OpenAIToolCallDTO accepts provider_specific_fields and forbids unknown fields."""
    data = {
        "id": "call_123",
        "type": "function",
        "function": {"name": "mcp_tavily_search", "arguments": '{"query": "test"}'},
        "provider_specific_fields": {"thought_signature": "Cu...7yJQl4aGsEaLDmOw1eSQ=="},
    }
    model = OpenAIToolCallDTO.model_validate(data)
    assert model.id == "call_123"

    with pytest.raises(ValidationError):
        OpenAIToolCallDTO.model_validate({**data, "unknown_key": "forbidden"})

    with pytest.raises(ValidationError):
        OpenAIToolCallDTO.model_validate({"type": "function"})


def test_openai_probe_response_dto_valid() -> None:
    """Verify OpenAIProbeResponseDTO validates tool_calls and conversational content."""
    data = {
        "tool_calls": [
            {
                "id": "call_123",
                "type": "function",
                "function": {"name": "mcp_tavily_search", "arguments": '{"query": "test"}'},
            }
        ],
        "content": "thinking...",
    }
    model = OpenAIProbeResponseDTO.model_validate(data)
    assert model.content == "thinking..."
    assert model.tool_calls is not None
    assert len(model.tool_calls) == 1
    assert model.tool_calls[0].id == "call_123"


def test_openai_probe_response_dto_forbids_extra() -> None:
    """Verify OpenAIProbeResponseDTO rejects unexpected extra fields and non-string content."""
    data = {
        "tool_calls": [],
        "content": "hello",
        "usage": {},
    }
    with pytest.raises(ValidationError):
        OpenAIProbeResponseDTO.model_validate(data)

    with pytest.raises(ValidationError):
        OpenAIProbeResponseDTO.model_validate({"content": 999})


def test_mcp_tool_loop_result_valid() -> None:
    """Verify MCPToolLoopResult validates structured output, audit traces, and token usage."""
    audit = MCPAuditTrace(
        tool_id="mcp_tavily_search",
        step_name="test_step",
        query="test query",
        response_summary="summary",
        source_urls=["https://example.com"],
        timestamp=datetime.now(UTC),
        duration_ms=100,
    )
    data = {
        "result_data": {"key": "value"},
        "audit_traces": [audit.model_dump()],
        "usage": {"prompt_tokens": 100, "completion_tokens": 0, "total_tokens": 100},
    }
    model = MCPToolLoopResult.model_validate(data)
    assert model.result_data["key"] == "value"
    assert len(model.audit_traces) == 1
    assert model.audit_traces[0].query == "test query"
    assert model.usage.total_tokens == 100


def test_mcp_tool_loop_result_defaults_and_negative_validation() -> None:
    """Verify MCPToolLoopResult default factories and fail-fast validation on missing or extra fields."""
    data = {"result_data": {"key": "value"}}
    model = MCPToolLoopResult.model_validate(data)
    assert model.audit_traces == []
    assert model.usage.total_tokens == 0

    with pytest.raises(ValidationError):
        MCPToolLoopResult.model_validate({})

    with pytest.raises(ValidationError):
        MCPToolLoopResult.model_validate({"result_data": {"key": "value"}, "extra": True})


def test_mcp_synthesis_instructions_dto() -> None:
    """Verify MCPSynthesisInstructionsDTO valid instantiation and negative validation."""
    model = MCPSynthesisInstructionsDTO(synthesis_preamble="Intro", synthesis_length_limit=500)
    assert model.synthesis_preamble == "Intro"
    assert model.synthesis_length_limit == 500

    with pytest.raises(ValidationError):
        MCPSynthesisInstructionsDTO.model_validate({"synthesis_length_limit": "not_an_int"})

    with pytest.raises(ValidationError):
        MCPSynthesisInstructionsDTO.model_validate({"unknown_field": "rejected"})


def test_citation_extraction_item_dto_and_truncation() -> None:
    """Verify CitationExtractionItemDTO sentence-boundary truncation and strict validation."""
    short_reason = "Short reasoning for test."
    item = CitationExtractionItemDTO(
        claim_text="Claim",
        search_query="Query",
        knowledge_gap="Gap",
        search_rationale="Rationale",
        reasoning=short_reason,
    )
    assert item.reasoning == short_reason

    # Test truncation at boundary 400 (no truncation needed)
    exact_400 = "A" * 400
    item_400 = CitationExtractionItemDTO(
        claim_text="Claim",
        search_query="Query",
        reasoning=exact_400,
    )
    assert len(item_400.reasoning) == 400

    # Test truncation with long reasoning (401+ chars) containing a period after index 50
    long_reason = "A" * 60 + ". " + "B" * 350
    item_long = CitationExtractionItemDTO(
        claim_text="Claim",
        search_query="Query",
        reasoning=long_reason,
    )
    assert len(item_long.reasoning) == 61
    assert item_long.reasoning.endswith(".")

    # Test truncation when period is at or before index 50 (falls back to ellipsis)
    early_period_reason = "A" * 10 + "." + "C" * 400
    item_early_period = CitationExtractionItemDTO(
        claim_text="Claim",
        search_query="Query",
        reasoning=early_period_reason,
    )
    assert len(item_early_period.reasoning) == 400
    assert item_early_period.reasoning.endswith("...")

    # Negative: non-string reasoning fails strict validation
    with pytest.raises(ValidationError):
        CitationExtractionItemDTO.model_validate(
            {
                "claim_text": "Claim",
                "search_query": "Query",
                "reasoning": 12345,
            }
        )

    # Negative: extra fields forbidden
    with pytest.raises(ValidationError):
        CitationExtractionItemDTO.model_validate(
            {
                "claim_text": "Claim",
                "search_query": "Query",
                "reasoning": "Valid.",
                "extra": "forbidden",
            }
        )


def test_citation_extraction_correction_and_failure_results() -> None:
    """Verify CitationExtractionResult, CitationCorrectionResult, and CitationExtractionFailure."""
    extraction = CitationExtractionResult(
        citations=[
            CitationExtractionItemDTO(
                claim_text="Claim",
                search_query="Query",
                reasoning="Reasoning.",
            )
        ]
    )
    assert len(extraction.citations) == 1

    correction = CitationCorrectionResult(corrected_claim="Corrected text.")
    assert correction.corrected_claim == "Corrected text."

    failure = CitationExtractionFailure(error_message="Worker timeout")
    assert failure.error_message == "Worker timeout"

    # Negative cases for all three result models
    with pytest.raises(ValidationError):
        CitationExtractionResult.model_validate({"citations": "not_a_list"})

    with pytest.raises(ValidationError):
        CitationCorrectionResult.model_validate({"corrected_claim": 42})

    with pytest.raises(ValidationError):
        CitationExtractionFailure.model_validate({"error_message": None})

    with pytest.raises(ValidationError):
        CitationExtractionFailure.model_validate({"error_message": "err", "extra": 1})


def test_mcp_retrieval_result_dto_valid_and_defaults() -> None:
    """Verify MCPRetrievalResultDTO default factories and explicit value hydration."""
    result = MCPRetrievalResultDTO()
    assert result.audit_traces == []
    assert result.usage.total_tokens == 0
    assert result.evidence_payload == ""

    audit = MCPAuditTrace(
        tool_id="mcp_wikipedia_search",
        step_name="archivist_step",
        query="Kahneman bias",
        response_summary="Found article on cognitive biases",
        source_urls=["https://fi.wikipedia.org/wiki/Kognitiivinen_vinouma"],
        timestamp=datetime.now(UTC),
        duration_ms=45,
    )
    populated = MCPRetrievalResultDTO(
        audit_traces=[audit],
        usage={"prompt_tokens": 150, "completion_tokens": 30, "total_tokens": 180},
        evidence_payload="<external_evidence>evidence text</external_evidence>",
    )
    assert len(populated.audit_traces) == 1
    assert populated.audit_traces[0].tool_id == "mcp_wikipedia_search"
    assert populated.usage.total_tokens == 180
    assert populated.evidence_payload == "<external_evidence>evidence text</external_evidence>"


def test_mcp_retrieval_result_dto_forbids_extra_and_frozen_invalid() -> None:
    """Verify MCPRetrievalResultDTO rejects extra keys and enforces frozen immutability."""
    with pytest.raises(ValidationError):
        invalid_payload = {"extra_key": "forbidden"}
        MCPRetrievalResultDTO.model_validate(invalid_payload)

    result = MCPRetrievalResultDTO()
    with pytest.raises(ValidationError):
        result.evidence_payload = "new text"

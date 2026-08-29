from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from backend_v2.models.domain.mcp import (
    CitationCorrectionResult,
    CitationExtractionItemDTO,
    CitationExtractionResult,
    MCPSynthesisInstructionsDTO,
    MCPToolLoopResult,
    OpenAIFunctionCallDTO,
    OpenAIProbeResponseDTO,
    OpenAIToolCallDTO,
    TavilyApiResponseDTO,
    TavilyApiResultItemDTO,
    TavilySearchResult,
    TavilyToolArgsDTO,
)
from backend_v2.models.v2_core import MCPAuditTrace


def test_openai_function_call_dto_valid() -> None:
    data = {"name": "mcp_tavily_search", "arguments": '{"query": "test"}'}
    model = OpenAIFunctionCallDTO.model_validate(data)
    assert model.name == "mcp_tavily_search"
    assert model.arguments == '{"query": "test"}'


def test_openai_function_call_dto_forbids_extra() -> None:
    data = {"name": "mcp_tavily_search", "arguments": '{"query": "test"}', "extra_field": "not allowed"}
    with pytest.raises(ValidationError):
        OpenAIFunctionCallDTO.model_validate(data)


def test_openai_tool_call_dto_valid() -> None:
    data = {
        "id": "call_123",
        "type": "function",
        "function": {"name": "mcp_tavily_search", "arguments": '{"query": "test"}'},
    }
    model = OpenAIToolCallDTO.model_validate(data)
    assert model.id == "call_123"
    assert model.type == "function"
    assert model.function.name == "mcp_tavily_search"


def test_openai_tool_call_dto_accepts_provider_specific_fields() -> None:
    data = {
        "id": "call_123",
        "type": "function",
        "function": {"name": "mcp_tavily_search", "arguments": '{"query": "test"}'},
        "provider_specific_fields": {"thought_signature": "Cu...7yJQl4aGsEaLDmOw1eSQ=="},
    }
    model = OpenAIToolCallDTO.model_validate(data)
    assert model.id == "call_123"


def test_openai_probe_response_dto_valid() -> None:
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
    data = {
        "tool_calls": [],
        "content": "hello",
        "usage": {},  # not allowed
    }
    with pytest.raises(ValidationError):
        OpenAIProbeResponseDTO.model_validate(data)


def test_tavily_tool_args_dto_valid() -> None:
    data = {"query": "test query"}
    model = TavilyToolArgsDTO.model_validate(data)
    assert model.query == "test query"


def test_mcp_tool_loop_result_valid() -> None:
    audit = MCPAuditTrace(
        tool_id="mcp_tavily_search",
        step_name="test_step",
        query="test query",
        response_summary="summary",
        source_urls=["http://example.com"],
        timestamp=datetime.now(timezone.utc),
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


def test_mcp_tool_loop_result_defaults() -> None:
    data = {"result_data": {"key": "value"}}
    model = MCPToolLoopResult.model_validate(data)
    assert model.audit_traces == []
    assert model.usage.total_tokens == 0


def test_tavily_api_result_item_dto() -> None:
    data = {
        "id": "7df8ff-00",
        "title": "Example Result",
        "url": "https://example.com",
        "content": "Example content",
        "score": 0.95,
        "published_date": "2026-08-28",
    }
    model = TavilyApiResultItemDTO.model_validate(data)
    assert model.id == "7df8ff-00"
    assert model.title == "Example Result"
    assert model.url == "https://example.com"


def test_tavily_api_response_dto() -> None:
    data = {
        "query": "test",
        "answer": "answer",
        "response_time": 0.5,
        "images": [],
        "results": [
            {
                "id": "res_1",
                "title": "Title",
                "url": "https://example.com",
                "content": "Content",
            }
        ],
    }
    model = TavilyApiResponseDTO.model_validate(data)
    assert model.query == "test"
    assert len(model.results) == 1
    assert model.results[0].id == "res_1"


def test_tavily_search_result_dto() -> None:
    model = TavilySearchResult(
        query="test query",
        answer="test answer",
        source_urls=["https://example.com"],
        raw_content="raw content",
        duration_ms=150,
    )
    assert model.query == "test query"
    assert model.source_urls == ["https://example.com"]


def test_mcp_synthesis_instructions_dto() -> None:
    model = MCPSynthesisInstructionsDTO(synthesis_preamble="Intro", synthesis_length_limit=500)
    assert model.synthesis_preamble == "Intro"
    assert model.synthesis_length_limit == 500


def test_citation_extraction_item_dto_and_truncation() -> None:
    short_reason = "Short reasoning for test."
    item = CitationExtractionItemDTO(
        claim_text="Claim",
        search_query="Query",
        knowledge_gap="Gap",
        search_rationale="Rationale",
        reasoning=short_reason,
    )
    assert item.reasoning == short_reason

    # Test truncation with long reasoning ending with period
    long_reason = "A" * 60 + ". " + "B" * 350
    item_long = CitationExtractionItemDTO(
        claim_text="Claim",
        search_query="Query",
        reasoning=long_reason,
    )
    assert len(item_long.reasoning) <= 400

    # Test truncation without periods
    long_reason_no_period = "C" * 450
    item_long_no_period = CitationExtractionItemDTO(
        claim_text="Claim",
        search_query="Query",
        reasoning=long_reason_no_period,
    )
    assert len(item_long_no_period.reasoning) <= 400
    assert item_long_no_period.reasoning.endswith("...")


def test_citation_extraction_and_correction_results() -> None:
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

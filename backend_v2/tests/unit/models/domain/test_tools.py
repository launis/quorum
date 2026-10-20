"""Unit tests for tool domain contracts and input DTOs in tools.py."""

from __future__ import annotations

from typing import Any

import pytest
from pydantic import ValidationError

from backend_v2.models.domain.system_config import MCPAuditTrace
from backend_v2.models.domain.tools import BaseSearchTool, BaseTool, StandardSearchInputDTO
from backend_v2.models.dtos.mcp import MCPFunctionDefinitionDTO, MCPToolDeclarationDTO
from backend_v2.models.enums import ToolCapability


class ConcreteTestSearchTool(BaseSearchTool):
    """Concrete implementation of BaseSearchTool for test verification."""

    @property
    def tool_id(self) -> str:
        return "test_search_tool"

    @property
    def declaration(self) -> MCPToolDeclarationDTO:
        return MCPToolDeclarationDTO(
            type="function",
            function=MCPFunctionDefinitionDTO(
                name="test_search_tool",
                description="Test tool declaration",
                parameters={"type": "object", "properties": {}},
            ),
        )

    async def execute(self, **kwargs: Any) -> MCPAuditTrace:
        dto = StandardSearchInputDTO.model_validate(kwargs)
        return MCPAuditTrace(
            tool_id=self.tool_id,
            step_name=dto.step_name,
            query=dto.query,
            response_summary="search results",
            source_urls=["https://example.com/source"],
        )


def test_tool_capability_enum_members_and_l10n() -> None:
    """Verify ToolCapability enum values and localization keys."""
    assert ToolCapability.SEARCH == "search"
    assert ToolCapability.DOCUMENT_READER == "document_reader"
    assert ToolCapability.ACTION == "action"

    assert ToolCapability.SEARCH.l10n_key == "mcp_capability_search"
    assert ToolCapability.DOCUMENT_READER.l10n_key == "mcp_capability_document_reader"
    assert ToolCapability.ACTION.l10n_key == "mcp_capability_action"


def test_standard_search_input_dto_valid() -> None:
    """Verify StandardSearchInputDTO initializes with valid arguments and defaults."""
    dto = StandardSearchInputDTO(query="quantum computing")
    assert dto.query == "quantum computing"
    assert dto.step_name == "unknown_step"
    assert dto.target_language == "en"
    assert dto.reasoning == ""
    assert dto.claim_text is None
    assert dto.llm_client is None


def test_standard_search_input_dto_full_payload() -> None:
    """Verify StandardSearchInputDTO initializes with all fields populated."""
    dummy_client = object()
    dto = StandardSearchInputDTO(
        query="artificial intelligence",
        step_name="step_01",
        target_language="fi",
        reasoning="Need latest AI trends",
        claim_text="AI is advancing rapidly",
        llm_client=dummy_client,
    )
    assert dto.query == "artificial intelligence"
    assert dto.step_name == "step_01"
    assert dto.target_language == "fi"
    assert dto.reasoning == "Need latest AI trends"
    assert dto.claim_text == "AI is advancing rapidly"
    assert dto.llm_client is dummy_client


def test_standard_search_input_dto_empty_query_raises() -> None:
    """Verify empty query triggers ValidationError (min_length=1)."""
    with pytest.raises(ValidationError):
        StandardSearchInputDTO(query="")


def test_standard_search_input_dto_extra_fields_forbidden() -> None:
    """Verify extra fields trigger ValidationError under extra='forbid'."""
    with pytest.raises(ValidationError):
        StandardSearchInputDTO.model_validate({"query": "test", "extra_param": 123})


def test_base_tool_abstract_instantiation_raises() -> None:
    """Verify BaseTool cannot be instantiated directly without implementations."""

    class IncompleteTool(BaseTool):
        pass

    with pytest.raises(TypeError):
        IncompleteTool()


def test_base_search_tool_capability_and_execution() -> None:
    """Verify BaseSearchTool provides ToolCapability.SEARCH and executes correctly."""
    tool = ConcreteTestSearchTool()
    assert tool.capability == ToolCapability.SEARCH
    assert tool.tool_id == "test_search_tool"
    assert tool.declaration.function.name == "test_search_tool"


@pytest.mark.asyncio
async def test_concrete_search_tool_execute() -> None:
    """Verify asynchronous execution of concrete search tool with StandardSearchInputDTO."""
    tool = ConcreteTestSearchTool()
    trace = await tool.execute(query="machine learning", step_name="step_ml")
    assert trace.tool_id == "test_search_tool"
    assert trace.step_name == "step_ml"
    assert trace.query == "machine learning"
    assert trace.response_summary == "search results"
    assert trace.source_urls == ["https://example.com/source"]


@pytest.mark.asyncio
async def test_base_tool_abstract_super_calls() -> None:
    """Verify BaseTool default method passes for coverage completeness."""

    class DelegatingTool(BaseTool):
        @property
        def tool_id(self) -> str:
            super().tool_id
            return "delegating_tool"

        @property
        def capability(self) -> ToolCapability:
            super().capability
            return ToolCapability.ACTION

        @property
        def declaration(self) -> MCPToolDeclarationDTO:
            super().declaration
            return MCPToolDeclarationDTO(
                type="function",
                function=MCPFunctionDefinitionDTO(
                    name="delegating_tool",
                    description="Test",
                    parameters={"type": "object", "properties": {}},
                ),
            )

        async def execute(self, **kwargs: Any) -> MCPAuditTrace:
            await super().execute(**kwargs)
            return MCPAuditTrace(
                tool_id=self.tool_id,
                step_name="step_del",
                query="query",
                response_summary="summary",
            )

    tool = DelegatingTool()
    assert tool.tool_id == "delegating_tool"
    assert tool.capability == ToolCapability.ACTION
    assert tool.declaration.function.name == "delegating_tool"
    trace = await tool.execute()
    assert trace.tool_id == "delegating_tool"


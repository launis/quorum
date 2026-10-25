import pytest
from pydantic import ValidationError

from backend_v2.exceptions import AppException
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.prompt_blocks import SystemRulePromptBlock
from backend_v2.models.domain.system_config import AllowedMCPTool
from backend_v2.models.dtos.mcp import (
    MCPToolInputSchemaDTO,
    MCPToolSchemaPropertyDTO,
)
from backend_v2.models.enums import BlockDataType, JSONSchemaPropertyType, PromptBlockCategory, ToolCapability
from backend_v2.services.orchestrator.schema_factory import SchemaFactory


def test_mcp_source_id_literal_validation() -> None:
    """Verify that a dynamically generated MCP tool result ID is accepted by the SchemaFactory union schema."""
    factory = SchemaFactory(resolve_i18n_fn=lambda t, locale: str(t) if t else "")

    block = SystemRulePromptBlock(
        id="blk_0123456789abcdef0123456789abcdef",
        slug="test",
        description=I18nText(translations={"en": "test"}),
        category_id=PromptBlockCategory.SYSTEM_RULE,
        type=BlockDataType.STRING,
        label=I18nText(translations={"en": "test"}),
    )

    Schema = factory.build_dynamic_schema(
        schema_name="TestSchema",
        criteria=[block],
        strictness_level=1,
        source_document_ids=["doc0"],
        allowed_atom_ids=["a0"],
        allowed_dynamic_keys=["chat_log", "mcp0"],
    )

    # 3. Simulate the LLM returning a dynamic MCP tool ID
    payload = {
        "blk_0123456789abcdef0123456789abcdef": {
            "source_document_aliases": ["doc0"],
            "exact_quotes": [{"source_id": "mcp0", "text": "This is a fact checked from tavily."}],
            "semantic_reasoning": "Reasoning",
            "rule_internalization": "Understood",
            "reasoning_steps": "Step 1",
            "decision": True,
        },
        "evaluation_notes": "",
        "reasoning_trace": "",
    }

    # 4. This should pass because the schema should allow mcp0 for tool results
    validated = Schema.model_validate(payload)
    assert validated.model_dump()["blk_0123456789abcdef0123456789abcdef"]["exact_quotes"][0]["source_id"] == "mcp0"


def test_mcp_source_id_literal_validation_invalid_source_rejected() -> None:
    """Negative: Verify that an unauthorized source_id is rejected by SchemaFactory union schema."""
    factory = SchemaFactory(resolve_i18n_fn=lambda t, locale: str(t) if t else "")

    block = SystemRulePromptBlock(
        id="blk_0123456789abcdef0123456789abcdef",
        slug="test",
        description=I18nText(translations={"en": "test"}),
        category_id=PromptBlockCategory.SYSTEM_RULE,
        type=BlockDataType.STRING,
        label=I18nText(translations={"en": "test"}),
    )

    Schema = factory.build_dynamic_schema(
        schema_name="TestSchema",
        criteria=[block],
        strictness_level=1,
        source_document_ids=["doc0"],
        allowed_atom_ids=["a0"],
        allowed_dynamic_keys=["chat_log"],
    )

    invalid_payload = {
        "blk_0123456789abcdef0123456789abcdef": {
            "source_document_aliases": ["doc0"],
            "exact_quotes": [{"source_id": "mcp_unauthorized", "text": "Unverified fact."}],
            "semantic_reasoning": "Reasoning",
            "rule_internalization": "Understood",
            "reasoning_steps": "Step 1",
            "decision": True,
        },
        "evaluation_notes": "",
        "reasoning_trace": "",
    }

    with pytest.raises(ValidationError):
        Schema.model_validate(invalid_payload)


def test_mcp_dynamic_tool_argument_schema_compilation_and_declaration() -> None:
    """Positive & Negative: Verify dynamic MCP tool argument model creation and declaration synthesis."""
    schema = MCPToolInputSchemaDTO(
        properties={
            "query": MCPToolSchemaPropertyDTO(type=JSONSchemaPropertyType.STRING, description="Search query"),
            "search_depth": MCPToolSchemaPropertyDTO(
                type=JSONSchemaPropertyType.STRING,
                enum_values=["basic", "advanced"],
            ),
        },
        required=["query"],
        additional_properties=False,
    )
    ArgModel = SchemaFactory.create_mcp_tool_argument_model(
        "default_mcp_gateway__mcp_tavily_search",
        schema,
    )
    instance = ArgModel.model_validate({"query": "Quorum architecture"})
    assert instance.model_dump() == {"query": "Quorum architecture", "search_depth": None}

    with pytest.raises(ValidationError):
        ArgModel.model_validate({"query": "Quorum", "extra_field": "forbidden"})

    with pytest.raises(ValidationError):
        ArgModel.model_validate({"query": "Quorum", "search_depth": "invalid_depth"})

    with pytest.raises(AppException):
        SchemaFactory.create_mcp_tool_argument_model("", schema)

    tool = AllowedMCPTool(
        tool_id="mcp_tavily_search",
        capability=ToolCapability.SEARCH,
        name=I18nText(translations={"en": "Search"}),
        description="Execute web search.",
        input_schema=schema,
        enabled=True,
    )
    declaration = SchemaFactory.build_mcp_tool_declaration("default_mcp_gateway__mcp_tavily_search", tool)
    assert declaration.function.name == "default_mcp_gateway__mcp_tavily_search"
    assert declaration.function.parameters.required == ["query"]

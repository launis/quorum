"""Unit tests for SchemaFactory dynamic Pydantic schema generation."""

import pydantic
import pytest
from pydantic import BaseModel, ValidationError

from backend_v2.exceptions import AppException
from backend_v2.llm.schema_builder import SchemaCompilerService
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.prompt_blocks import AnyPromptBlock, SystemRulePromptBlock
from backend_v2.models.domain.system_config import AllowedMCPTool
from backend_v2.models.dtos.mcp import (
    MCPToolDescriptorDTO,
    MCPToolInputSchemaDTO,
    MCPToolSchemaPropertyDTO,
)
from backend_v2.models.enums import (
    BlockDataType,
    JSONSchemaPropertyType,
    PromptBlockCategory,
    ToolCapability,
)
from backend_v2.services.orchestrator.schema_factory import (
    SchemaFactory,
    StrippedBaseTDAExtraction,
)


def dummy_resolve_i18n(text: str, locale: str) -> str:
    """No-op I18n resolver returning the input text unchanged."""
    return text


@pytest.fixture
def schema_factory() -> SchemaFactory:
    return SchemaFactory(resolve_i18n_fn=dummy_resolve_i18n)


def test_build_chunk_response_schema(schema_factory: SchemaFactory) -> None:
    """Verify chunk response schema nests records and chunk_id fields."""

    class DummyPayload(BaseModel):
        test_field: str

    model = schema_factory.build_chunk_response_schema("ChunkSchema", DummyPayload)
    assert issubclass(model, BaseModel)
    assert "records" in model.model_fields
    assert "chunk_id" in model.model_fields


def test_build_dynamic_schema_empty(schema_factory: SchemaFactory) -> None:
    """Verify empty criteria produces fallback reasoning and evaluation fields."""
    model = schema_factory.build_dynamic_schema("EmptySchema", [], strictness_level=50)
    assert issubclass(model, BaseModel)
    assert "reasoning_trace" in model.model_fields
    assert "evaluation_notes" in model.model_fields


def test_dunder_hallucination_rejected_by_extra_forbid() -> None:
    """Verify that LLM dunder-key hallucinations (e.g. __rule_satisfied__) are REJECTED.

    This ensures we enforce Fail-Fast validation instead of silently allowing hallucinations.
    """
    # Simulate LLM output with hallucinated __rule_satisfied__ field
    data = {
        "exact_quotes": ["test quote"],
        "contextual_override": False,
        "semantic_reasoning": "Test reasoning",
        "__rule_satisfied__": True,  # <-- LLM hallucination
    }

    # Strict validation MUST reject this to fail-fast and route to DLQ
    with pytest.raises(pydantic.ValidationError) as exc:
        StrippedBaseTDAExtraction.model_validate(data)

    assert "extra_forbidden" in str(exc.value)


def test_normal_typo_still_rejected_by_extra_forbid() -> None:
    """Verify that non-dunder typos still trigger extra_forbidden.

    The before-validator MUST only strip __dunder__ keys, not normal field typos.
    """
    data = {
        "exact_quotes": ["test quote"],
        "contextual_override": False,
        "semnatic_reasoning": "Typo field name",  # <-- typo, NOT a dunder
    }

    with pytest.raises(pydantic.ValidationError) as exc:
        StrippedBaseTDAExtraction.model_validate(data)

    assert "extra_forbidden" in str(exc.value)


def test_build_dynamic_schema_with_source_document_ids(schema_factory: SchemaFactory) -> None:
    """Verify that build_dynamic_schema enforces dynamic Literal validation on source_document_ids."""
    criteria: list[AnyPromptBlock] = [
        SystemRulePromptBlock(
            id="blk_1234567890abcdef1234567890abcdef",
            slug="test-slug-1",
            label=I18nText(translations={"en": "Test Label"}),
            description=I18nText(translations={"en": "Test Desc"}),
            instruction_text="Test AI instruction",
            category_id=PromptBlockCategory.SYSTEM_RULE,
            type=BlockDataType.COMPLIANCE,
            output_extensions=[],
        )
    ]

    allowed_docs = ["doc_a", "doc_b"]
    DynamicModel = schema_factory.build_dynamic_schema(
        "DynamicTestSchema",
        criteria,
        strictness_level=100,
        source_document_ids=allowed_docs,
    )

    assert "blk_1234567890abcdef1234567890abcdef" in DynamicModel.model_fields
    inner_model = DynamicModel.model_fields["blk_1234567890abcdef1234567890abcdef"].annotation
    assert inner_model is not None

    valid_data = {
        "rule_internalization": "Criteria require checking X.",
        "used_source_aliases": [],
        "source_document_aliases": ["doc_a"],
        "exact_quotes": [{"text": "quote", "source_id": "N/A"}],
        "reasoning_steps": "1) R requires X. 2) T has Y. 3) F.",
        "falsification_argument": "No falsification possible.",
        "decision": True,
        "semantic_reasoning": "Pass",
    }

    obj = inner_model.model_validate(valid_data, context={"alias_map": {"doc_a": "opa_1", "doc_b": "opa_2"}})
    assert obj.source_document_aliases == ["doc_a"]

    invalid_data = valid_data.copy()
    invalid_data["source_document_aliases"] = ["doc_invalid"]
    obj_invalid = inner_model.model_validate(invalid_data, context={"alias_map": {"doc_a": "opa_1", "doc_b": "opa_2"}})
    assert obj_invalid.source_document_aliases == ["N/A"]


def test_create_mcp_tool_argument_model_all_json_schema_types_positive() -> None:
    """Positive: Verify create_mcp_tool_argument_model compiles recursive JSON Schema types into strict Pydantic V2."""
    input_schema = MCPToolInputSchemaDTO(
        properties={
            "query": MCPToolSchemaPropertyDTO(
                type=JSONSchemaPropertyType.STRING,
                description="Search query string",
            ),
            "max_results": MCPToolSchemaPropertyDTO(
                type=JSONSchemaPropertyType.INTEGER,
                description="Maximum number of results",
            ),
            "threshold": MCPToolSchemaPropertyDTO(
                type=JSONSchemaPropertyType.NUMBER,
                description="Relevance score threshold",
            ),
            "include_raw": MCPToolSchemaPropertyDTO(
                type=JSONSchemaPropertyType.BOOLEAN,
                description="Include raw page content",
            ),
            "search_depth": MCPToolSchemaPropertyDTO(
                type=JSONSchemaPropertyType.STRING,
                description="Depth mode",
                enum_values=["basic", "advanced"],
            ),
            "tags": MCPToolSchemaPropertyDTO(
                type=JSONSchemaPropertyType.ARRAY,
                description="Filter tags",
                items=MCPToolSchemaPropertyDTO(type=JSONSchemaPropertyType.STRING),
            ),
            "untyped_array": MCPToolSchemaPropertyDTO(
                type=JSONSchemaPropertyType.ARRAY,
                description="Fallback string array when items is omitted",
            ),
            "filter_obj": MCPToolSchemaPropertyDTO(
                type=JSONSchemaPropertyType.OBJECT,
                description="Nested filter object",
                properties={
                    "domain": MCPToolSchemaPropertyDTO(
                        type=JSONSchemaPropertyType.STRING,
                        description="Target domain",
                    ),
                },
                required=["domain"],
            ),
        },
        required=["query", "search_depth", "filter_obj"],
        additional_properties=False,
    )

    ArgModel = SchemaCompilerService.create_mcp_tool_argument_model(
        "default_mcp_gateway__mcp_tavily_search",
        input_schema,
    )
    validated = ArgModel.model_validate(
        {
            "query": "ISO 9001 quality management",
            "max_results": 5,
            "threshold": 0.75,
            "include_raw": False,
            "search_depth": "advanced",
            "tags": ["iso", "quality"],
            "untyped_array": ["item1"],
            "filter_obj": {"domain": "iso.org"},
        }
    )
    dumped = validated.model_dump(exclude_none=True)
    assert dumped["query"] == "ISO 9001 quality management"
    assert dumped["max_results"] == 5
    assert dumped["search_depth"] == "advanced"
    assert dumped["filter_obj"] == {"domain": "iso.org"}


def test_create_mcp_tool_argument_model_rejects_extra_and_invalid_types_negative() -> None:
    """Negative 1: Verify compiled runtime argument model rejects extra fields, invalid enum literals, and wrong types."""
    input_schema = MCPToolInputSchemaDTO(
        properties={
            "query": MCPToolSchemaPropertyDTO(type=JSONSchemaPropertyType.STRING),
            "mode": MCPToolSchemaPropertyDTO(
                type=JSONSchemaPropertyType.STRING,
                enum_values=["fast", "deep"],
            ),
        },
        required=["query", "mode"],
    )

    ArgModel = SchemaFactory.create_mcp_tool_argument_model("gw__search", input_schema)

    # Extra field rejected
    with pytest.raises(ValidationError):
        ArgModel.model_validate({"query": "hello", "mode": "fast", "unexpected": 123})

    # Invalid Literal value rejected
    with pytest.raises(ValidationError):
        ArgModel.model_validate({"query": "hello", "mode": "invalid_mode"})

    # Missing required field rejected
    with pytest.raises(ValidationError):
        ArgModel.model_validate({"mode": "fast"})


def test_create_mcp_tool_argument_model_invalid_definition_negative() -> None:
    """Negative 2: Verify empty namespaced_alias or missing required property key raises AppException."""
    valid_schema = MCPToolInputSchemaDTO(
        properties={"query": MCPToolSchemaPropertyDTO(type=JSONSchemaPropertyType.STRING)},
        required=["query"],
    )

    with pytest.raises(AppException):
        SchemaFactory.create_mcp_tool_argument_model("   ", valid_schema)

    inconsistent_schema = MCPToolInputSchemaDTO(
        properties={"query": MCPToolSchemaPropertyDTO(type=JSONSchemaPropertyType.STRING)},
        required=["query", "non_existent_required_key"],
    )
    with pytest.raises(AppException):
        SchemaFactory.create_mcp_tool_argument_model("gw__search", inconsistent_schema)

    missing_obj_props_schema = MCPToolInputSchemaDTO(
        properties={
            "nested": MCPToolSchemaPropertyDTO(
                type=JSONSchemaPropertyType.OBJECT,
                properties=None,
            )
        },
        required=["nested"],
    )
    with pytest.raises(AppException):
        SchemaFactory.create_mcp_tool_argument_model("gw__search", missing_obj_props_schema)


def test_build_mcp_tool_declaration_positive_and_negative() -> None:
    """Positive & Negative: Verify build_mcp_tool_declaration constructs strict declaration and rejects blank alias."""
    schema = MCPToolInputSchemaDTO(
        properties={"query": MCPToolSchemaPropertyDTO(type=JSONSchemaPropertyType.STRING)},
        required=["query"],
    )
    tool = AllowedMCPTool(
        tool_id="mcp_tavily_search",
        capability=ToolCapability.SEARCH,
        name=I18nText(translations={"en": "Search", "fi": "Haku"}),
        description="Search the web for factual verification.",
        input_schema=schema,
        enabled=True,
    )
    decl = SchemaCompilerService.build_mcp_tool_declaration(
        "default_mcp_gateway__mcp_tavily_search",
        tool,
    )
    assert decl.type == "function"
    assert decl.function.name == "default_mcp_gateway__mcp_tavily_search"
    assert decl.function.description == "Search the web for factual verification."
    assert decl.function.parameters == schema
    assert decl.function.strict is True

    descriptor = MCPToolDescriptorDTO(
        gateway_id="mcp_0195f3a00000700080008172bda70c86",
        gateway_slug="default_mcp_gateway",
        namespaced_alias="default_mcp_gateway__mcp_tavily_search",
        tool_id="mcp_tavily_search",
        description="Search the web.",
        capability=ToolCapability.SEARCH,
        input_schema=schema,
        enabled=True,
    )
    decl_from_desc = SchemaFactory.build_mcp_tool_declaration(descriptor.namespaced_alias, descriptor)
    assert decl_from_desc.function.name == "default_mcp_gateway__mcp_tavily_search"

    with pytest.raises(AppException):
        SchemaFactory.build_mcp_tool_declaration("", tool)


def test_create_mcp_tool_argument_model_with_const_and_array_bounds_positive_and_negative() -> None:
    """Positive & Negative: Verify SchemaFactory compiles const into Literal and enforces strict validation."""
    input_schema = MCPToolInputSchemaDTO(
        properties={
            "encoding": MCPToolSchemaPropertyDTO(
                type=JSONSchemaPropertyType.STRING,
                const="base64",
                description="Attachment encoding format",
            ),
            "files": MCPToolSchemaPropertyDTO(
                type=JSONSchemaPropertyType.ARRAY,
                min_items=1,
                max_items=5,
                items=MCPToolSchemaPropertyDTO(type=JSONSchemaPropertyType.STRING),
                description="Attached file names",
            ),
        },
        required=["encoding"],
    )

    ArgModel = SchemaFactory.create_mcp_tool_argument_model(
        "default_mcp_gateway__tavily_research",
        input_schema,
    )

    # Positive: exact const literal and valid string array accepted
    valid_instance = ArgModel.model_validate({"encoding": "base64", "files": ["report.md"]})
    dumped = valid_instance.model_dump(exclude_none=True)
    assert dumped["encoding"] == "base64"
    assert dumped["files"] == ["report.md"]

    # Negative 1: non-matching string for const Literal raises ValidationError
    with pytest.raises(ValidationError):
        ArgModel.model_validate({"encoding": "utf8"})

    # Negative 2: wrong scalar type (int) for const Literal raises ValidationError
    with pytest.raises(ValidationError):
        ArgModel.model_validate({"encoding": 12345})

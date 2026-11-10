"""Unit tests for SchemaCompilerService dynamic Pydantic schema and MCP tool compilation."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.llm.schema_builder import SchemaCompilerService
from backend_v2.models.domain.prompt_blocks import PromptBlock
from backend_v2.models.dtos.mcp import (
    MCPToolDescriptorDTO,
    MCPToolInputSchemaDTO,
    MCPToolSchemaPropertyDTO,
)
from backend_v2.models.enums import (
    BlockDataType,
    JSONSchemaPropertyType,
    XaiExtensionType,
)
from backend_v2.models.prompts.common import (
    XAI_DESC_EMOTIONAL_SENTIMENT,
    XAI_DESC_MISSING_CONTEXT,
    XAI_DESC_REMEDIATION_STEPS,
    XAI_DESC_RISK_FLAG,
    XAI_DESC_THEORY_LINK,
)
from backend_v2.tests.factories.model_factories import (
    MatrixPromptBlockFactory,
    SystemRulePromptBlockFactory,
)

_TEST_BLOCK_ID = "blk_1234567890abcdef1234567890abcdef"


def create_mock_block(slug: str, btype: BlockDataType, extensions: list[str]) -> PromptBlock:
    """Create a valid V2 PromptBlock for schema testing using Polyfactory.

    Args:
        slug: Informational block slug.
        btype: Block data type enum.
        extensions: List of requested XAI output extensions.

    Returns:
        Instantiated MatrixPromptBlock or SystemRulePromptBlock.
    """
    if btype in (BlockDataType.FLOAT, BlockDataType.INT):
        return MatrixPromptBlockFactory.build(
            id=_TEST_BLOCK_ID,
            slug=slug,
            type=btype,
            output_extensions=extensions,
        )
    return SystemRulePromptBlockFactory.build(
        id=_TEST_BLOCK_ID,
        slug=slug,
        type=BlockDataType.STRING,
        output_extensions=extensions,
    )


def test_schema_compiler_basic_compile() -> None:
    """Test that a PromptBlock successfully compiles into a strict Pydantic model."""
    block = create_mock_block("test_metric", BlockDataType.FLOAT, [])

    DynamicModel = SchemaCompilerService.compile([block])

    # Should validate correct data using the alias
    instance = DynamicModel.model_validate_json('{"eval_1": 3.5}')
    assert instance.model_dump()[_TEST_BLOCK_ID] == 3.5

    # Should forbid extra fields due to strict=True, extra='forbid'
    with pytest.raises(ValidationError):
        DynamicModel.model_validate({"eval_1": 3.5, "extra_field": "bad"})


def test_schema_compiler_xai_extensions() -> None:
    """Test that Anti-Sycophancy XAI Extensions are correctly injected."""
    block = create_mock_block(
        "obs_1",
        BlockDataType.STRING,
        [XaiExtensionType.COACHING.value, XaiExtensionType.FALSIFICATION.value],
    )

    DynamicModel = SchemaCompilerService.compile([block])
    schema = DynamicModel.model_json_schema()

    properties = schema["properties"]
    assert "eval_1" in properties

    coaching_key = f"eval_1_{XaiExtensionType.COACHING.value}"
    falsification_key = f"eval_1_{XaiExtensionType.FALSIFICATION.value}"

    assert coaching_key in properties
    assert falsification_key in properties


def test_schema_compiler_all_xai_extensions_descriptions() -> None:
    """Test that all 5 advanced XAI Extensions are injected with SSOT descriptions."""
    block = create_mock_block(
        "obs_2",
        BlockDataType.STRING,
        [
            XaiExtensionType.MISSING_CONTEXT.value,
            XaiExtensionType.RISK_FLAG.value,
            XaiExtensionType.REMEDIATION_STEPS.value,
            XaiExtensionType.EMOTIONAL_SENTIMENT.value,
            XaiExtensionType.THEORY_LINK.value,
        ],
    )

    DynamicModel = SchemaCompilerService.compile([block])
    schema = DynamicModel.model_json_schema()
    props = schema["properties"]

    assert props[f"eval_1_{XaiExtensionType.MISSING_CONTEXT.value}"]["description"] == XAI_DESC_MISSING_CONTEXT
    assert props[f"eval_1_{XaiExtensionType.RISK_FLAG.value}"]["description"] == XAI_DESC_RISK_FLAG
    assert props[f"eval_1_{XaiExtensionType.REMEDIATION_STEPS.value}"]["description"] == XAI_DESC_REMEDIATION_STEPS
    assert props[f"eval_1_{XaiExtensionType.EMOTIONAL_SENTIMENT.value}"]["description"] == XAI_DESC_EMOTIONAL_SENTIMENT
    assert props[f"eval_1_{XaiExtensionType.THEORY_LINK.value}"]["description"] == XAI_DESC_THEORY_LINK


def test_schema_compiler_int_and_remaining_extensions() -> None:
    """Test compiling integer blocks and remaining extensions (justification, citation, confidence)."""
    block = create_mock_block(
        "int_metric",
        BlockDataType.INT,
        [
            XaiExtensionType.JUSTIFICATION.value,
            XaiExtensionType.CITATION.value,
            XaiExtensionType.CONFIDENCE.value,
        ],
    )

    DynamicModel = SchemaCompilerService.compile([block])
    schema = DynamicModel.model_json_schema()
    props = schema["properties"]

    assert "eval_1" in props
    assert props["eval_1"]["type"] == "integer"
    assert f"eval_1_{XaiExtensionType.JUSTIFICATION.value}" in props
    assert f"eval_1_{XaiExtensionType.CITATION.value}" in props
    assert f"eval_1_{XaiExtensionType.CONFIDENCE.value}" in props

    # Valid validation
    instance = DynamicModel.model_validate_json(
        '{"eval_1": 4, "eval_1_justification": "Justification text", '
        '"eval_1_citation": "Citation text", "eval_1_confidence": 0.9}'
    )
    assert instance.model_dump()[_TEST_BLOCK_ID] == 4

    # Negative test: invalid int type raises ValidationError
    with pytest.raises(ValidationError):
        DynamicModel.model_validate(
            {
                "eval_1": "not_an_int",
                f"eval_1_{XaiExtensionType.JUSTIFICATION.value}": "Justification",
                f"eval_1_{XaiExtensionType.CITATION.value}": "Citation",
                f"eval_1_{XaiExtensionType.CONFIDENCE.value}": 0.9,
            }
        )

    # Negative test: missing required field raises ValidationError
    with pytest.raises(ValidationError):
        DynamicModel.model_validate({"eval_1": 4})


def test_schema_compiler_mcp_tool_delegation_and_negative_boundaries() -> None:
    """Test MCP tool argument model and declaration delegation plus negative AppException boundaries."""
    input_schema = MCPToolInputSchemaDTO(
        properties={
            "query": MCPToolSchemaPropertyDTO(
                type=JSONSchemaPropertyType.STRING,
                description="Search query string.",
            )
        },
        required=["query"],
    )

    arg_model = SchemaCompilerService.create_mcp_tool_argument_model("gw_search__web", input_schema)
    validated_args = arg_model.model_validate_json('{"query": "quorum architecture"}')
    assert validated_args.model_dump() == {"query": "quorum architecture"}

    descriptor = MCPToolDescriptorDTO(
        gateway_id="sys_1234567890abcdef1234567890abcdef",
        gateway_slug="gw_search",
        namespaced_alias="gw_search__web",
        tool_id="web",
        description="Execute web search.",
        input_schema=input_schema,
    )
    declaration = SchemaCompilerService.build_mcp_tool_declaration("gw_search__web", descriptor)
    assert declaration.function.name == "gw_search__web"
    assert declaration.function.description == "Execute web search."

    # Negative test 1: blank namespaced_alias in create_mcp_tool_argument_model raises AppException
    with pytest.raises(AppException) as exc_arg:
        SchemaCompilerService.create_mcp_tool_argument_model("   ", input_schema)
    assert exc_arg.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED

    # Negative test 2: blank namespaced_alias in build_mcp_tool_declaration raises AppException
    with pytest.raises(AppException) as exc_decl:
        SchemaCompilerService.build_mcp_tool_declaration("", descriptor)
    assert exc_decl.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED

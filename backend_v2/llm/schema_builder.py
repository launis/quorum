"""Schema Compiler Service for compiling PromptBlocks into dynamic Pydantic models."""

from __future__ import annotations

import functools
import hashlib
import json
from enum import Enum
from typing import Annotated, Any, cast

from pydantic import BaseModel, ConfigDict, Field, create_model

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.prompt_blocks import PromptBlock
from backend_v2.models.domain.system_config import AllowedMCPTool
from backend_v2.models.dtos.mcp import (
    MCPToolDeclarationDTO,
    MCPToolDescriptorDTO,
    MCPToolInputSchemaDTO,
)
from backend_v2.models.enums import BlockDataType, XaiExtensionType
from backend_v2.models.prompts.common import (
    XAI_DESC_CITATION,
    XAI_DESC_COACHING,
    XAI_DESC_CONFIDENCE,
    XAI_DESC_EMOTIONAL_SENTIMENT,
    XAI_DESC_FALSIFICATION,
    XAI_DESC_JUSTIFICATION,
    XAI_DESC_MISSING_CONTEXT,
    XAI_DESC_REMEDIATION_STEPS,
    XAI_DESC_RISK_FLAG,
    XAI_DESC_THEORY_LINK,
)
from backend_v2.services.orchestrator.schema_factory import SchemaFactory

__all__ = ["BlockSchemaConfigDTO", "DynamicFieldDefinition", "DynamicFieldSpecDTO", "SchemaCompilerService"]

type DynamicFieldDefinition = tuple[Any, Any]


class BlockSchemaConfigDTO(BaseModel):
    """Configuration signature of a prompt block for schema compilation.

    Attributes:
        id: Prompt block identifier.
        type: Block data type string representation.
        output_extensions: List of supported output extension keys.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    id: Annotated[str, Field(description="Prompt block identifier.")]
    type: Annotated[str, Field(description="Block data type string representation.")]
    output_extensions: Annotated[
        list[str], Field(default_factory=list, description="List of supported output extension keys.")
    ]


class DynamicFieldSpecDTO(V2CoreBase):
    """Specification of a dynamically generated schema field.

    Attributes:
        name: Internal field name on the generated model.
        type_hint: Python type annotation for the generated field.
        description: Schema description instruction for the LLM.
        alias: Deterministic evaluation alias exposed to the LLM.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True, arbitrary_types_allowed=True)

    name: str
    type_hint: Any
    description: str
    alias: str

    def to_field_definition(self) -> DynamicFieldDefinition:
        """Convert specification into a Pydantic create_model field definition tuple.

        Returns:
            Tuple of (type_hint, FieldInfo) representing the field definition.
        """
        return (self.type_hint, Field(..., description=self.description, alias=self.alias))


class SchemaCompilerService:
    """Compiles PromptBlocks and MCP Tool schemas into dynamic Pydantic Models."""

    @staticmethod
    def _generate_hash(blocks_config: list[BlockSchemaConfigDTO]) -> str:
        """Generate a stable SHA-256 hash for a given schema configuration.

        Args:
            blocks_config: List of block configuration DTOs.

        Returns:
            SHA-256 hash string.
        """
        # Ensure we sort the config so identical schemas get the same hash
        config_list = [b.model_dump(mode="json") for b in blocks_config]
        config_str = json.dumps(config_list, sort_keys=True)
        return hashlib.sha256(config_str.encode()).hexdigest()

    @staticmethod
    @functools.lru_cache(maxsize=1024)
    def _get_or_create_model(schema_hash: str, fields_tuple: tuple[DynamicFieldSpecDTO, ...]) -> type[BaseModel]:
        """Retrieve or create a Pydantic Model based on the fields tuple.

        LRU Cache strictly prevents Python `type` memory leaks (OOM) during dynamic creation.

        Args:
            schema_hash: The unique hash of the schema.
            fields_tuple: Tuple of field definitions.

        Returns:
            The dynamically generated Pydantic model class.
        """
        fields: dict[str, DynamicFieldDefinition] = {spec.name: spec.to_field_definition() for spec in fields_tuple}
        model = create_model(
            f"DynamicSchema_{schema_hash[:8]}",
            __config__=ConfigDict(extra="forbid", strict=True, frozen=True, populate_by_name=True),
            **cast(dict[str, Any], fields),
        )
        return cast(type[BaseModel], model)

    @staticmethod
    def _resolve_primary_field_spec(block_id: str, alias_name: str, b_type: str) -> DynamicFieldSpecDTO:
        """Build the primary evaluation DynamicFieldSpecDTO for a prompt block.

        Args:
            block_id: Canonical prompt block identifier.
            alias_name: Deterministic evaluation alias (e.g., 'eval_1').
            b_type: Serialized BlockDataType value.

        Returns:
            Configured DynamicFieldSpecDTO for the primary block output.
        """
        if b_type == BlockDataType.FLOAT.value:
            type_hint: Any = float
            desc = f"Float numerical value for {block_id}"
        elif b_type == BlockDataType.INT.value:
            type_hint = int
            desc = f"Integer numerical value for {block_id}"
        else:
            type_hint = str
            desc = f"Extracted text content for {block_id}"

        return DynamicFieldSpecDTO(
            name=block_id,
            type_hint=type_hint,
            description=desc,
            alias=alias_name,
        )

    @staticmethod
    def _make_extension_spec(
        block_id: str,
        alias_name: str,
        ext_type: XaiExtensionType,
        type_hint: Any,
        description: str,
    ) -> DynamicFieldSpecDTO:
        """Create a DynamicFieldSpecDTO for a single XAI output extension.

        Args:
            block_id: Canonical prompt block identifier.
            alias_name: Deterministic evaluation alias (e.g., 'eval_1').
            ext_type: XAI extension enum variant.
            type_hint: Python type annotation for the extension field.
            description: Formatted schema description instruction.

        Returns:
            Configured DynamicFieldSpecDTO for the extension field.
        """
        return DynamicFieldSpecDTO(
            name=f"{block_id}_{ext_type.value}",
            type_hint=type_hint,
            description=description,
            alias=f"{alias_name}_{ext_type.value}",
        )

    @classmethod
    def _build_xai_extension_specs(
        cls,
        block_id: str,
        alias_name: str,
        extensions: list[str],
    ) -> list[DynamicFieldSpecDTO]:
        """Build XAI extension field specifications for a prompt block.

        Args:
            block_id: Canonical prompt block identifier.
            alias_name: Deterministic evaluation alias (e.g., 'eval_1').
            extensions: Requested XAI output extension identifiers.

        Returns:
            Ordered list of DynamicFieldSpecDTO instances for active extensions.
        """
        extension_set = set(extensions)
        specs: list[DynamicFieldSpecDTO] = []
        if XaiExtensionType.JUSTIFICATION.value in extension_set:
            specs.append(
                cls._make_extension_spec(
                    block_id,
                    alias_name,
                    XaiExtensionType.JUSTIFICATION,
                    str,
                    XAI_DESC_JUSTIFICATION.format(block_id=block_id),
                )
            )
        if XaiExtensionType.CITATION.value in extension_set:
            specs.append(
                cls._make_extension_spec(
                    block_id, alias_name, XaiExtensionType.CITATION, str, XAI_DESC_CITATION.format(block_id=block_id)
                )
            )
        if XaiExtensionType.COACHING.value in extension_set:
            specs.append(
                cls._make_extension_spec(block_id, alias_name, XaiExtensionType.COACHING, str, XAI_DESC_COACHING)
            )
        if XaiExtensionType.CONFIDENCE.value in extension_set:
            specs.append(
                cls._make_extension_spec(block_id, alias_name, XaiExtensionType.CONFIDENCE, float, XAI_DESC_CONFIDENCE)
            )
        if XaiExtensionType.FALSIFICATION.value in extension_set:
            specs.append(
                cls._make_extension_spec(
                    block_id,
                    alias_name,
                    XaiExtensionType.FALSIFICATION,
                    str,
                    XAI_DESC_FALSIFICATION.format(block_id=block_id),
                )
            )
        if XaiExtensionType.MISSING_CONTEXT.value in extension_set:
            specs.append(
                cls._make_extension_spec(
                    block_id, alias_name, XaiExtensionType.MISSING_CONTEXT, str, XAI_DESC_MISSING_CONTEXT
                )
            )
        if XaiExtensionType.RISK_FLAG.value in extension_set:
            specs.append(
                cls._make_extension_spec(block_id, alias_name, XaiExtensionType.RISK_FLAG, bool, XAI_DESC_RISK_FLAG)
            )
        if XaiExtensionType.REMEDIATION_STEPS.value in extension_set:
            specs.append(
                cls._make_extension_spec(
                    block_id, alias_name, XaiExtensionType.REMEDIATION_STEPS, list[str], XAI_DESC_REMEDIATION_STEPS
                )
            )
        if XaiExtensionType.EMOTIONAL_SENTIMENT.value in extension_set:
            specs.append(
                cls._make_extension_spec(
                    block_id, alias_name, XaiExtensionType.EMOTIONAL_SENTIMENT, str, XAI_DESC_EMOTIONAL_SENTIMENT
                )
            )
        if XaiExtensionType.THEORY_LINK.value in extension_set:
            specs.append(
                cls._make_extension_spec(block_id, alias_name, XaiExtensionType.THEORY_LINK, str, XAI_DESC_THEORY_LINK)
            )
        return specs

    @classmethod
    def compile(cls, prompt_blocks: list[PromptBlock]) -> type[BaseModel]:
        """Compile a list of PromptBlocks into a rigid Pydantic model.

        Args:
            prompt_blocks: List of PromptBlock configuration blocks.

        Returns:
            Compiled Pydantic Model.
        """
        blocks_config: list[BlockSchemaConfigDTO] = [
            BlockSchemaConfigDTO(
                id=block.id,
                type=block.type.value if isinstance(block.type, Enum) else str(block.type),
                output_extensions=block.output_extensions,
            )
            for block in prompt_blocks
        ]

        blocks_config.sort(key=lambda x: x.id)
        schema_hash = cls._generate_hash(blocks_config)

        fields_list: list[DynamicFieldSpecDTO] = []
        for index, cfg in enumerate(blocks_config):
            alias_name = f"eval_{index + 1}"
            fields_list.append(cls._resolve_primary_field_spec(cfg.id, alias_name, cfg.type))
            fields_list.extend(cls._build_xai_extension_specs(cfg.id, alias_name, cfg.output_extensions))

        return cls._get_or_create_model(schema_hash, tuple(fields_list))

    @classmethod
    def create_mcp_tool_argument_model(
        cls,
        namespaced_alias: str,
        input_schema: MCPToolInputSchemaDTO,
    ) -> type[BaseModel]:
        """Delegate runtime MCP tool argument model compilation to SchemaFactory.

        Args:
            namespaced_alias: Full namespaced tool alias ('{gateway_slug}__{tool_id}').
            input_schema: Strict recursive JSON Schema DTO for the tool's input parameters.

        Returns:
            Dynamically generated Pydantic V2 BaseModel enforcing strict=True, extra='forbid', frozen=True.

        Raises:
            AppException: With VALIDATION_FAILED if namespaced_alias is empty or input_schema has invalid required keys.
        """
        return SchemaFactory.create_mcp_tool_argument_model(namespaced_alias, input_schema)

    @classmethod
    def build_mcp_tool_declaration(
        cls,
        namespaced_alias: str,
        tool: AllowedMCPTool | MCPToolDescriptorDTO,
    ) -> MCPToolDeclarationDTO:
        """Delegate MCPToolDeclarationDTO construction to SchemaFactory.

        Args:
            namespaced_alias: Full namespaced tool alias ('{gateway_slug}__{tool_id}').
            tool: AllowedMCPTool domain configuration or hydrated MCPToolDescriptorDTO.

        Returns:
            Strongly typed MCPToolDeclarationDTO ready for LLM provider serialization.

        Raises:
            AppException: With VALIDATION_FAILED if namespaced_alias is empty.
        """
        return SchemaFactory.build_mcp_tool_declaration(namespaced_alias, tool)

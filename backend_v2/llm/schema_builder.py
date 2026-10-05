"""Schema Compiler Service for compiling PromptBlocks into dynamic Pydantic models."""

import functools
import hashlib
import json
from enum import Enum
from typing import Annotated, Any, cast

from pydantic import BaseModel, ConfigDict, Field, create_model

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.prompt_blocks import PromptBlock
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
    """Specification of a dynamically generated schema field."""

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
    """Compiles PromptBlocks into dynamic Pydantic Models for LLM structured outputs."""

    @staticmethod
    def _generate_hash(blocks_config: list[BlockSchemaConfigDTO]) -> str:
        """Generates a stable SHA-256 hash for a given schema configuration.

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
        """Retrieves or creates a Pydantic Model based on the fields tuple.
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

    @classmethod
    def compile(cls, prompt_blocks: list[PromptBlock]) -> type[BaseModel]:
        """Compiles a list of PromptBlocks into a rigid Pydantic model.

        Args:
            prompt_blocks: List of PromptBlock configuration blocks.

        Returns:
            Compiled Pydantic Model.
        """
        # 1. Create a hashable representation of the schema requirements
        blocks_config: list[BlockSchemaConfigDTO] = []
        for block in prompt_blocks:
            blocks_config.append(
                BlockSchemaConfigDTO(
                    id=block.id,
                    type=block.type.value if isinstance(block.type, Enum) else str(block.type),
                    output_extensions=block.output_extensions,
                )
            )

        # Sort blocks_config by id to ensure deterministic hashing regardless of input order
        blocks_config.sort(key=lambda x: x.id)
        schema_hash = cls._generate_hash(blocks_config)

        # 2. Build the fields tuple for Pydantic (must be hashable for lru_cache)
        fields_list: list[DynamicFieldSpecDTO] = []
        for index, cfg in enumerate(blocks_config):
            block_id = cfg.id
            alias_name = f"eval_{index + 1}"
            b_type = cfg.type

            type_hint: Any
            # Map BlockDataType to strict Python primitives
            if b_type == BlockDataType.FLOAT.value:
                type_hint = float
                desc = f"Float numerical value for {block_id}"
            elif b_type == BlockDataType.INT.value:
                type_hint = int
                desc = f"Integer numerical value for {block_id}"
            else:
                type_hint = str
                desc = f"Extracted text content for {block_id}"

            fields_list.append(
                DynamicFieldSpecDTO(
                    name=block_id,
                    type_hint=type_hint,
                    description=desc,
                    alias=alias_name,
                )
            )

            # Dynamically inject requested XAI output extensions into Pydantic schema
            extensions = cfg.output_extensions
            if XaiExtensionType.JUSTIFICATION.value in extensions:
                fields_list.append(
                    DynamicFieldSpecDTO(
                        name=f"{block_id}_{XaiExtensionType.JUSTIFICATION.value}",
                        type_hint=str,
                        description=XAI_DESC_JUSTIFICATION.format(block_id=block_id),
                        alias=f"{alias_name}_{XaiExtensionType.JUSTIFICATION.value}",
                    )
                )
            if XaiExtensionType.CITATION.value in extensions:
                fields_list.append(
                    DynamicFieldSpecDTO(
                        name=f"{block_id}_{XaiExtensionType.CITATION.value}",
                        type_hint=str,
                        description=XAI_DESC_CITATION.format(block_id=block_id),
                        alias=f"{alias_name}_{XaiExtensionType.CITATION.value}",
                    )
                )
            if XaiExtensionType.COACHING.value in extensions:
                fields_list.append(
                    DynamicFieldSpecDTO(
                        name=f"{block_id}_{XaiExtensionType.COACHING.value}",
                        type_hint=str,
                        description=XAI_DESC_COACHING,
                        alias=f"{alias_name}_{XaiExtensionType.COACHING.value}",
                    )
                )
            if XaiExtensionType.CONFIDENCE.value in extensions:
                fields_list.append(
                    DynamicFieldSpecDTO(
                        name=f"{block_id}_{XaiExtensionType.CONFIDENCE.value}",
                        type_hint=float,
                        description=XAI_DESC_CONFIDENCE,
                        alias=f"{alias_name}_{XaiExtensionType.CONFIDENCE.value}",
                    )
                )
            if XaiExtensionType.FALSIFICATION.value in extensions:
                fields_list.append(
                    DynamicFieldSpecDTO(
                        name=f"{block_id}_{XaiExtensionType.FALSIFICATION.value}",
                        type_hint=str,
                        description=XAI_DESC_FALSIFICATION.format(block_id=block_id),
                        alias=f"{alias_name}_{XaiExtensionType.FALSIFICATION.value}",
                    )
                )
            if XaiExtensionType.MISSING_CONTEXT.value in extensions:
                fields_list.append(
                    DynamicFieldSpecDTO(
                        name=f"{block_id}_{XaiExtensionType.MISSING_CONTEXT.value}",
                        type_hint=str,
                        description=XAI_DESC_MISSING_CONTEXT,
                        alias=f"{alias_name}_{XaiExtensionType.MISSING_CONTEXT.value}",
                    )
                )
            if XaiExtensionType.RISK_FLAG.value in extensions:
                fields_list.append(
                    DynamicFieldSpecDTO(
                        name=f"{block_id}_{XaiExtensionType.RISK_FLAG.value}",
                        type_hint=bool,
                        description=XAI_DESC_RISK_FLAG,
                        alias=f"{alias_name}_{XaiExtensionType.RISK_FLAG.value}",
                    )
                )
            if XaiExtensionType.REMEDIATION_STEPS.value in extensions:
                fields_list.append(
                    DynamicFieldSpecDTO(
                        name=f"{block_id}_{XaiExtensionType.REMEDIATION_STEPS.value}",
                        type_hint=list[str],
                        description=XAI_DESC_REMEDIATION_STEPS,
                        alias=f"{alias_name}_{XaiExtensionType.REMEDIATION_STEPS.value}",
                    )
                )
            if XaiExtensionType.EMOTIONAL_SENTIMENT.value in extensions:
                fields_list.append(
                    DynamicFieldSpecDTO(
                        name=f"{block_id}_{XaiExtensionType.EMOTIONAL_SENTIMENT.value}",
                        type_hint=str,
                        description=XAI_DESC_EMOTIONAL_SENTIMENT,
                        alias=f"{alias_name}_{XaiExtensionType.EMOTIONAL_SENTIMENT.value}",
                    )
                )
            if XaiExtensionType.THEORY_LINK.value in extensions:
                fields_list.append(
                    DynamicFieldSpecDTO(
                        name=f"{block_id}_{XaiExtensionType.THEORY_LINK.value}",
                        type_hint=str,
                        description=XAI_DESC_THEORY_LINK,
                        alias=f"{alias_name}_{XaiExtensionType.THEORY_LINK.value}",
                    )
                )

        # Convert to immutable tuple to safely cross the LRU cache boundary
        fields_tuple = tuple(fields_list)
        return cls._get_or_create_model(schema_hash, fields_tuple)

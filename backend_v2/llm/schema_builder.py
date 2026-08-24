import functools
import hashlib
import json
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, create_model

from backend_v2.models.domain.prompt_blocks import PromptBlock
from backend_v2.models.enums import BlockDataType, XaiExtensionType
from backend_v2.models.prompts.field_prompts import (
    XAI_DESC_CITATION,
    XAI_DESC_COACHING,
    XAI_DESC_CONFIDENCE,
    XAI_DESC_FALSIFICATION,
    XAI_DESC_JUSTIFICATION,
)


class SchemaCompilerService:
    """Compiles PromptBlocks into dynamic Pydantic Models for LLM structured outputs."""

    @staticmethod
    def _generate_hash(blocks_config: list[dict[str, Any]]) -> str:
        """Generates a stable SHA-256 hash for a given schema configuration.

        Args:
            blocks_config: List of block configuration dictionaries.

        Returns:
            SHA-256 hash string.
        """
        # Ensure we sort the config so identical schemas get the same hash
        config_str = json.dumps(blocks_config, sort_keys=True)
        return hashlib.sha256(config_str.encode()).hexdigest()

    @staticmethod
    @functools.lru_cache(maxsize=1024)
    def _get_or_create_model(schema_hash: str, fields_tuple: tuple[tuple[str, Any, str, str], ...]) -> type[BaseModel]:
        """Retrieves or creates a Pydantic Model based on the fields tuple.
        LRU Cache strictly prevents Python `type` memory leaks (OOM) during dynamic creation.

        Args:
            schema_hash: The unique hash of the schema.
            fields_tuple: Tuple of field definitions.

        Returns:
            The dynamically generated Pydantic model class.
        """
        fields: dict[str, Any] = {
            name: (type_hint, Field(..., description=desc, alias=alias))
            for name, type_hint, desc, alias in fields_tuple
        }
        return create_model(
            f"DynamicSchema_{schema_hash[:8]}",
            __config__=ConfigDict(extra="forbid", strict=True, frozen=True, populate_by_name=True),
            **fields,
        )

    @classmethod
    def compile(cls, prompt_blocks: list[PromptBlock]) -> type[BaseModel]:
        """Compiles a list of PromptBlocks into a rigid Pydantic model.

        Args:
            prompt_blocks: List of PromptBlock configuration blocks.

        Returns:
            Compiled Pydantic Model.
        """
        # 1. Create a hashable representation of the schema requirements
        blocks_config = []
        for block in prompt_blocks:
            blocks_config.append(
                {
                    "id": block.id,
                    "type": block.type.value if isinstance(block.type, Enum) else str(block.type),
                    "output_extensions": block.output_extensions,
                }
            )

        # Sort blocks_config by id to ensure deterministic hashing regardless of input order
        blocks_config.sort(key=lambda x: x["id"])
        schema_hash = cls._generate_hash(blocks_config)

        # 2. Build the fields tuple for Pydantic (must be hashable for lru_cache)
        fields_list: list[tuple[str, Any, str, str]] = []
        for index, cfg in enumerate(blocks_config):
            block_id = str(cfg["id"])
            alias_name = f"eval_{index + 1}"
            b_type = cfg["type"]

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

            fields_list.append((block_id, type_hint, desc, alias_name))

            # Dynamically inject requested XAI output extensions into Pydantic schema
            extensions = cfg["output_extensions"]
            if XaiExtensionType.JUSTIFICATION.value in extensions:
                fields_list.append(
                    (
                        f"{block_id}_{XaiExtensionType.JUSTIFICATION.value}",
                        str,
                        XAI_DESC_JUSTIFICATION.format(block_id=block_id),
                        f"{alias_name}_{XaiExtensionType.JUSTIFICATION.value}",
                    )
                )
            if XaiExtensionType.CITATION.value in extensions:
                fields_list.append(
                    (
                        f"{block_id}_{XaiExtensionType.CITATION.value}",
                        str,
                        XAI_DESC_CITATION.format(block_id=block_id),
                        f"{alias_name}_{XaiExtensionType.CITATION.value}",
                    )
                )
            if XaiExtensionType.COACHING.value in extensions:
                fields_list.append(
                    (
                        f"{block_id}_{XaiExtensionType.COACHING.value}",
                        str,
                        XAI_DESC_COACHING,
                        f"{alias_name}_{XaiExtensionType.COACHING.value}",
                    )
                )
            if XaiExtensionType.CONFIDENCE.value in extensions:
                fields_list.append(
                    (
                        f"{block_id}_{XaiExtensionType.CONFIDENCE.value}",
                        float,
                        XAI_DESC_CONFIDENCE,
                        f"{alias_name}_{XaiExtensionType.CONFIDENCE.value}",
                    )
                )
            if XaiExtensionType.FALSIFICATION.value in extensions:
                fields_list.append(
                    (
                        f"{block_id}_{XaiExtensionType.FALSIFICATION.value}",
                        str,
                        XAI_DESC_FALSIFICATION.format(block_id=block_id),
                        f"{alias_name}_{XaiExtensionType.FALSIFICATION.value}",
                    )
                )
            if XaiExtensionType.MISSING_CONTEXT.value in extensions:
                fields_list.append(
                    (
                        f"{block_id}_{XaiExtensionType.MISSING_CONTEXT.value}",
                        str,
                        "Exact missing data from the provided text that would have altered the evaluation score. "
                        "No theoretical assumptions.",
                        f"{alias_name}_{XaiExtensionType.MISSING_CONTEXT.value}",
                    )
                )
            if XaiExtensionType.RISK_FLAG.value in extensions:
                fields_list.append(
                    (
                        f"{block_id}_{XaiExtensionType.RISK_FLAG.value}",
                        bool,
                        "True ONLY if there is a severe, documentable risk present; False otherwise.",
                        f"{alias_name}_{XaiExtensionType.RISK_FLAG.value}",
                    )
                )
            if XaiExtensionType.REMEDIATION_STEPS.value in extensions:
                fields_list.append(
                    (
                        f"{block_id}_{XaiExtensionType.REMEDIATION_STEPS.value}",
                        list[str],
                        "Numbered actionable list of distinct textual remediation steps.",
                        f"{alias_name}_{XaiExtensionType.REMEDIATION_STEPS.value}",
                    )
                )
            if XaiExtensionType.EMOTIONAL_SENTIMENT.value in extensions:
                fields_list.append(
                    (
                        f"{block_id}_{XaiExtensionType.EMOTIONAL_SENTIMENT.value}",
                        str,
                        "Analysis of the user's emotional state or tone regarding this metric.",
                        f"{alias_name}_{XaiExtensionType.EMOTIONAL_SENTIMENT.value}",
                    )
                )
            if XaiExtensionType.THEORY_LINK.value in extensions:
                fields_list.append(
                    (
                        f"{block_id}_{XaiExtensionType.THEORY_LINK.value}",
                        str,
                        "Direct logical connection of the observation back to the governing theory framework.",
                        f"{alias_name}_{XaiExtensionType.THEORY_LINK.value}",
                    )
                )

        # Convert to immutable tuple to safely cross the LRU cache boundary
        fields_tuple = tuple(fields_list)
        return cls._get_or_create_model(schema_hash, fields_tuple)

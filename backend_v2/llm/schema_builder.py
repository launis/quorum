import functools
import hashlib
import json
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, create_model

from backend_v2.models.enums import BlockDataType, XaiExtensionType
from backend_v2.models.v2_core import PromptBlock


class SchemaCompilerService:
    """Compiles PromptBlocks into dynamic Pydantic Models for LLM structured outputs."""

    @staticmethod
    def _generate_hash(blocks_config: list[dict[str, Any]]) -> str:
        """Generates a stable SHA-256 hash for a given schema configuration.

        Args:
            blocks_config: List of block configuration dictionaries.

        Returns:
            str: SHA-256 hash string.
        """
        # Ensure we sort the config so identical schemas get the same hash
        config_str = json.dumps(blocks_config, sort_keys=True)
        return hashlib.sha256(config_str.encode()).hexdigest()

    @staticmethod
    @functools.lru_cache(maxsize=1024)
    def _get_or_create_model(schema_hash: str, fields_tuple: tuple[tuple[str, Any, str], ...]) -> type[BaseModel]:
        """Retrieves or creates a Pydantic Model based on the fields tuple.
        LRU Cache strictly prevents Python `type` memory leaks (OOM) during dynamic creation.

        Args:
            schema_hash: The unique hash of the schema.
            fields_tuple: Tuple of field definitions.

        Returns:
            type[BaseModel]: The dynamically generated Pydantic model class.
        """
        fields: dict[str, Any] = {
            name: (type_hint, Field(..., description=desc)) for name, type_hint, desc in fields_tuple
        }
        return create_model(
            f"DynamicSchema_{schema_hash[:8]}",
            __config__=ConfigDict(extra="forbid", strict=True, frozen=True),
            **fields,
        )

    @classmethod
    def compile(cls, prompt_blocks: list[PromptBlock]) -> type[BaseModel]:
        """Compiles a list of PromptBlocks into a rigid Pydantic model.

        Args:
            prompt_blocks: List of PromptBlock configuration blocks.

        Returns:
            type[BaseModel]: Compiled Pydantic Model.
        """
        # 1. Create a hashable representation of the schema requirements
        blocks_config = []
        for block in prompt_blocks:
            blocks_config.append(
                {
                    "slug": block.slug,
                    "type": block.type.value if isinstance(block.type, Enum) else str(block.type),
                    "output_extensions": block.output_extensions,
                }
            )

        # Sort blocks_config by slug to ensure deterministic hashing regardless of input order
        blocks_config.sort(key=lambda x: x["slug"])
        schema_hash = cls._generate_hash(blocks_config)

        # 2. Build the fields tuple for Pydantic (must be hashable for lru_cache)
        fields_list: list[tuple[str, Any, str]] = []
        for cfg in blocks_config:
            slug = str(cfg["slug"])
            b_type = cfg["type"]

            type_hint: Any
            # Map BlockDataType to strict Python primitives
            if b_type == BlockDataType.FLOAT.value:
                type_hint = float
                desc = f"Float numerical value for {slug}"
            elif b_type == BlockDataType.INT.value:
                type_hint = int
                desc = f"Integer numerical value for {slug}"
            else:
                type_hint = str
                desc = f"Extracted text content for {slug}"

            fields_list.append((slug, type_hint, desc))

            # Dynamically inject requested XAI output extensions into Pydantic schema
            extensions = cfg["output_extensions"]
            if XaiExtensionType.JUSTIFICATION.value in extensions:
                fields_list.append(
                    (
                        f"{slug}_{XaiExtensionType.JUSTIFICATION.value}",
                        str,
                        f"Extensive analytical reasoning and justification for the {slug} output. "
                        "STRICT MANDATE: DO NOT output any final mathematical scores, grades, "
                        "or 'Arvosana' in this text. ONLY explain the qualitative reasoning.",
                    )
                )
            if XaiExtensionType.CITATION.value in extensions:
                fields_list.append(
                    (
                        f"{slug}_{XaiExtensionType.CITATION.value}",
                        str,
                        f"Direct exact quote from the source text strongly supporting the {slug} justification.",
                    )
                )
            if XaiExtensionType.COACHING.value in extensions:
                fields_list.append(
                    (
                        f"{slug}_{XaiExtensionType.COACHING.value}",
                        str,
                        "STRICT MANDATE: Provide one concrete, actionable step to patch the observed data "
                        "or logic gap. DO NOT give general tips or encouraging advice.",
                    )
                )
            if XaiExtensionType.CONFIDENCE.value in extensions:
                fields_list.append(
                    (
                        f"{slug}_{XaiExtensionType.CONFIDENCE.value}",
                        float,
                        "Numerical confidence from 0.0 to 100.0 based strictly on source evidence.",
                    )
                )
            if XaiExtensionType.FALSIFICATION.value in extensions:
                fields_list.append(
                    (
                        f"{slug}_{XaiExtensionType.FALSIFICATION.value}",
                        str,
                        "STRICT MANDATE: List the exact business scenario where the user's model or "
                        "claim crashes 100%. No mitigating words allowed.",
                    )
                )
            if XaiExtensionType.MISSING_CONTEXT.value in extensions:
                fields_list.append(
                    (
                        f"{slug}_{XaiExtensionType.MISSING_CONTEXT.value}",
                        str,
                        "Exact missing data from the provided text that would have altered the evaluation score. "
                        "No theoretical assumptions.",
                    )
                )
            if XaiExtensionType.RISK_FLAG.value in extensions:
                fields_list.append(
                    (
                        f"{slug}_{XaiExtensionType.RISK_FLAG.value}",
                        bool,
                        "True ONLY if there is a severe, documentable risk present; False otherwise.",
                    )
                )
            if XaiExtensionType.REMEDIATION_STEPS.value in extensions:
                fields_list.append(
                    (
                        f"{slug}_{XaiExtensionType.REMEDIATION_STEPS.value}",
                        list[str],
                        "Numbered actionable list of distinct textual remediation steps.",
                    )
                )
            if XaiExtensionType.EMOTIONAL_SENTIMENT.value in extensions:
                fields_list.append(
                    (
                        f"{slug}_{XaiExtensionType.EMOTIONAL_SENTIMENT.value}",
                        str,
                        "Analysis of the user's emotional state or tone regarding this metric.",
                    )
                )
            if XaiExtensionType.THEORY_LINK.value in extensions:
                fields_list.append(
                    (
                        f"{slug}_{XaiExtensionType.THEORY_LINK.value}",
                        str,
                        "Direct logical connection of the observation back to the governing theory framework.",
                    )
                )

        # Convert to immutable tuple to safely cross the LRU cache boundary
        fields_tuple = tuple(fields_list)
        return cls._get_or_create_model(schema_hash, fields_tuple)

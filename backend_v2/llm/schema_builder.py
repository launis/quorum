import functools
import hashlib
import json
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, create_model

from backend_v2.models.enums import BlockDataType
from backend_v2.models.v2_core import PromptBlock


class SchemaCompilerService:
    """Compiles PromptBlocks into dynamic Pydantic Models for LLM structured outputs."""

    @staticmethod
    def _generate_hash(blocks_config: list[dict[str, Any]]) -> str:
        """Generates a stable SHA-256 hash for a given schema configuration."""
        # Ensure we sort the config so identical schemas get the same hash
        config_str = json.dumps(blocks_config, sort_keys=True)
        return hashlib.sha256(config_str.encode()).hexdigest()

    @staticmethod
    @functools.lru_cache(maxsize=1024)
    def _get_or_create_model(schema_hash: str, fields_tuple: tuple[tuple[str, Any, str], ...]) -> type[BaseModel]:
        """Retrieves or creates a Pydantic Model based on the fields tuple.
        LRU Cache strictly prevents Python `type` memory leaks (OOM) during dynamic creation.
        """
        fields: dict[str, Any] = {
            name: (type_hint, Field(..., description=desc)) for name, type_hint, desc in fields_tuple
        }
        return create_model(
            f"DynamicSchema_{schema_hash[:8]}",
            __config__=ConfigDict(extra="forbid", strict=False),
            **fields
        )

    @classmethod
    def compile(cls, prompt_blocks: list[PromptBlock]) -> type[BaseModel]:
        """Compiles a list of PromptBlocks into a rigid Pydantic model."""
        # 1. Create a hashable representation of the schema requirements
        blocks_config = []
        for block in prompt_blocks:
            blocks_config.append({
                "slug": block.slug,
                "type": block.type.value if isinstance(block.type, Enum) else str(block.type),
                "output_extensions": block.output_extensions,
            })

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
            extensions = cfg.get("output_extensions", [])
            if "justification" in extensions:
                fields_list.append((
                    f"{slug}_justification",
                    str,
                    f"Extensive analytical reasoning and justification for the {slug} output."
                ))
            if "citation" in extensions:
                fields_list.append((
                    f"{slug}_citation",
                    str,
                    f"Direct exact quote from the source text strongly supporting the {slug} justification."
                ))
            if "coaching" in extensions:
                fields_list.append((f"{slug}_coaching", str, "Concrete coaching tip/remediation advice to the subject."))
            if "confidence" in extensions:
                fields_list.append((f"{slug}_confidence", float, "Numerical confidence from 0.0 to 100.0 based strictly on source evidence."))
            if "falsification" in extensions:
                fields_list.append((f"{slug}_falsification", str, "Devil's advocate argument rejecting the primary justification."))
            if "missing_context" in extensions:
                fields_list.append((f"{slug}_missing_context", str, "Missing data from the provided text that would have improved or changed the score."))
            if "risk_flag" in extensions:
                fields_list.append((f"{slug}_risk_flag", bool, "True if there is a severe risk present; False otherwise."))
            if "remediation_steps" in extensions:
                fields_list.append((f"{slug}_remediation_steps", list[str], "Numbered actionable list of distinct textual remediation steps."))
            if "emotional_sentiment" in extensions:
                fields_list.append((f"{slug}_emotional_sentiment", str, "Analysis of the user's emotional state or tone regarding this metric."))
            if "theory_link" in extensions:
                fields_list.append((f"{slug}_theory_link", str, "Direct logical connection of the observation back to the governing theory framework."))

        # Convert to immutable tuple to safely cross the LRU cache boundary
        fields_tuple = tuple(fields_list)
        return cls._get_or_create_model(schema_hash, fields_tuple)

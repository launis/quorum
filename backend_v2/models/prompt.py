from __future__ import annotations

"""Structured Prompt models for prompt caching and context management.

This module defines clean Pydantic DTO models supporting structured, layered prompt
packaging designed to optimize Anthropic/OpenAI prompt cache hit ratios.
"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CompiledPrompt(BaseModel):
    """Strictly typed representation of compiled LLM prompt parts.

    Segregates immutable system state parameters from dynamic context layers to optimize
    cache indexing and hit rates across LLM providers.

    Attributes:
        static_messages: 100% static system instructions, static few-shot examples, and unchanging schemas.
        dynamic_messages: Dynamic execution parameters, Trace IDs, and user/assistant dynamic tail conversation.
        metadata: Arbitrary execution metadata (e.g., token proxy scores).
    """

    static_messages: list[dict[str, Any]] = Field(
        ..., description="100% static system instructions, static few-shot examples, and unchanging schemas."
    )
    dynamic_messages: list[dict[str, Any]] = Field(
        ..., description="Dynamic execution parameters, Trace IDs, and user/assistant dynamic tail conversation."
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Arbitrary execution metadata (e.g., token proxy scores)."
    )

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    def to_flat_messages(self) -> list[dict[str, Any]]:
        """Flattens both parts into a single list of messages for backward-compatibility.

        Seamlessly merges consecutive messages of the same role (e.g. consecutive user messages)
        by joining their content string with a double newline to maintain pure alternating structure.

        Returns:
            A flattened list of message dicts conforming strictly to role/content pairs.
        """
        raw_list = self.static_messages + self.dynamic_messages
        flat: list[dict[str, Any]] = []

        for msg in raw_list:
            role = str(msg["role"])
            content_str = str(msg["content"])

            if flat and str(flat[-1]["role"]) == role:
                # Merge consecutive messages of the same role cleanly
                existing_str = str(flat[-1]["content"])
                merged_content = (existing_str + "\n\n" + content_str).strip()
                flat[-1] = {"role": role, "content": merged_content}
            else:
                flat.append({"role": role, "content": content_str.strip()})

        return flat

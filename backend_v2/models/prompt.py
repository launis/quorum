from __future__ import annotations

"""Structured Prompt models for prompt caching and context management.

This module defines clean Pydantic DTO models supporting structured, layered prompt
packaging designed to optimize Anthropic/OpenAI prompt cache hit ratios.
"""

from typing import Any, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class CompiledPrompt(BaseModel):
    """Strictly typed representation of compiled LLM prompt parts.

    Segregates immutable system state parameters from dynamic context layers to optimize
    cache indexing and hit rates across LLM providers.

    Attributes:
        static_messages: Globally identical content across all chunks (base system prompt + source document).
        dynamic_messages: Per-chunk/per-retry content (rubrics, atoms, execution params, healing errors).
        metadata: Arbitrary execution metadata (e.g., token proxy scores).
    """

    static_messages: list[dict[str, Any]] = Field(
        ..., description="Globally identical content across all chunks (base system prompt + source document)."
    )
    dynamic_messages: list[dict[str, Any]] = Field(
        ..., description="Per-chunk/per-retry content (rubrics, atoms, execution params, healing errors)."
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Arbitrary execution metadata (e.g., token proxy scores)."
    )

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    # V3 Cache Contamination Fix: Prevent system messages from leaking into dynamic payload
    @model_validator(mode="after")
    def _forbid_system_in_dynamic(self) -> Self:
        """Enforce architectural invariant: system role must never appear in dynamic_messages.

        System instructions belong exclusively in static_messages for caching integrity.
        Violating this would silently contaminate the cache with per-chunk system content.
        """
        for msg in self.dynamic_messages:
            if msg.get("role") == "system":
                raise ValueError(
                    "ARCHITECTURE VIOLATION: 'system' role forbidden in dynamic_messages. "
                    "System instructions must be in static_messages for caching integrity."
                )
        return self

    @staticmethod
    def _merge_flat(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Merge consecutive same-role messages into a single message per role boundary.

        Maintains pure alternating role structure required by LLM providers.
        """
        flat: list[dict[str, Any]] = []
        for msg in messages:
            role = str(msg["role"])
            content_str = str(msg["content"])

            if flat and str(flat[-1]["role"]) == role:
                existing_str = str(flat[-1]["content"])
                merged_content = (existing_str + "\n\n" + content_str).strip()
                flat[-1] = {"role": role, "content": merged_content}
            else:
                flat.append({"role": role, "content": content_str.strip()})
        return flat

    def to_static_flat(self) -> list[dict[str, Any]]:
        """Flatten only static_messages for cache upload.

        Returns:
            Merged list of static message dicts (system + base user content).
        """
        return self._merge_flat(list(self.static_messages))

    def to_dynamic_flat(self) -> list[dict[str, Any]]:
        """Flatten only dynamic_messages for live request payload alongside cached content.

        Returns:
            Merged list of dynamic message dicts (per-chunk rubrics, atoms, params).
        """
        return self._merge_flat(list(self.dynamic_messages))

    def to_flat_messages(self) -> list[dict[str, Any]]:
        """Flatten both tiers into a single list for backward-compatibility (no cache path).

        Seamlessly merges consecutive messages of the same role by joining content
        with a double newline to maintain pure alternating structure.

        Returns:
            A flattened list of message dicts conforming strictly to role/content pairs.
        """
        return self._merge_flat(list(self.static_messages) + list(self.dynamic_messages))

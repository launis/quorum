"""Structured Prompt models for prompt caching and context management."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CompiledPrompt(BaseModel):
    """Strictly typed representation of compiled LLM prompt parts to support Context Caching."""

    static_messages: list[dict[str, Any]] = Field(
        ..., description="100% static system instructions, static few-shot examples, and unchanging schemas."
    )
    dynamic_messages: list[dict[str, Any]] = Field(
        ..., description="Dynamic execution parameters, Trace IDs, and user/assistant dynamic tail conversation."
    )

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    def to_flat_messages(self) -> list[dict[str, Any]]:
        """Flattens both parts into a single list of messages for backward-compatibility.

        Seamlessly merges consecutive messages of the same role (e.g. consecutive user messages)
        by joining their content string with a double newline to maintain pure alternating structure.
        """
        raw_list = self.static_messages + self.dynamic_messages
        flat: list[dict[str, Any]] = []

        for msg in raw_list:
            role = msg.get("role")
            content = msg.get("content", "")

            # Ensure safe string conversion
            content_str = content if isinstance(content, str) else str(content)

            if flat and flat[-1].get("role") == role:
                # Merge consecutive messages of the same role cleanly
                existing_content = flat[-1].get("content", "")
                existing_str = existing_content if isinstance(existing_content, str) else str(existing_content)

                flat[-1] = {"role": role, "content": (existing_str + "\n\n" + content_str).strip()}
            else:
                flat.append({"role": role, "content": content_str.strip()})

        return flat

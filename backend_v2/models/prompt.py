import logging
from typing import Annotated, Self

from fastapi import status
from pydantic import ConfigDict, Field, model_validator

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.dtos.base import BaseDTO
from backend_v2.models.llm import LLMMessageDTO

logger = logging.getLogger(__name__)


class PromptMetadataDTO(BaseDTO):
    """Strictly typed metadata for CompiledPrompt.

    Attributes:
        token_proxy_score: Token proxy score for cache evaluation.
        cache_key: Deterministic cache identifier.
        routing_tags: Routing or tier tags.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    token_proxy_score: Annotated[
        float | None, Field(default=None, description="Token proxy score for cache evaluation.")
    ] = None
    cache_key: Annotated[str | None, Field(default=None, description="Deterministic cache identifier.")] = None
    routing_tags: Annotated[list[str] | None, Field(default=None, description="Routing or tier tags.")] = None


class CompiledPrompt(BaseDTO):
    """Strictly typed representation of compiled LLM prompt parts.

    Segregates immutable system state parameters from dynamic context layers to optimize
    cache indexing and hit rates across LLM providers.

    Attributes:
        static_messages: Globally identical content across all chunks (base system prompt + source document).
        dynamic_messages: Per-chunk/per-retry content (rubrics, atoms, execution params, healing errors).
        metadata: Arbitrary execution metadata (e.g., token proxy scores).
    """

    static_messages: Annotated[
        list[LLMMessageDTO],
        Field(description="Globally identical content across all chunks (base system prompt + source document)."),
    ]
    dynamic_messages: Annotated[
        list[LLMMessageDTO],
        Field(description="Per-chunk/per-retry content (rubrics, atoms, execution params, healing errors)."),
    ]
    metadata: Annotated[
        PromptMetadataDTO,
        Field(
            default_factory=PromptMetadataDTO, description="Arbitrary execution metadata (e.g., token proxy scores)."
        ),
    ] = Field(default_factory=PromptMetadataDTO)

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    # V3 Cache Contamination Fix: Prevent system messages from leaking into dynamic payload
    @model_validator(mode="after")
    def _forbid_system_in_dynamic(self) -> Self:
        """Enforce architectural invariant: system role must never appear in dynamic_messages.

        System instructions belong exclusively in static_messages for caching integrity.
        Violating this would silently contaminate the cache with per-chunk system content.

        Raises:
            AppException: If 'system' role is found in dynamic_messages.
        """
        for msg in self.dynamic_messages:
            if msg.role == "system":
                msg_text = (
                    "ARCHITECTURE VIOLATION: 'system' role forbidden in dynamic_messages. "
                    "System instructions must be in static_messages for caching integrity."
                )
                logger.error("[CompiledPrompt] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg_text, exc_info=True)
                raise AppException(
                    message=msg_text,
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )
        return self

    @staticmethod
    def _merge_flat(messages: list[LLMMessageDTO]) -> list[LLMMessageDTO]:
        """Merge consecutive same-role messages into a single message per role boundary.

        Maintains pure alternating role structure required by LLM providers.

        Args:
            messages: List of LLMMessageDTO instances containing role and content.

        Returns:
            Merged list of LLMMessageDTO instances.
        """
        flat: list[LLMMessageDTO] = []
        for msg in messages:
            role = msg.role
            content_str = msg.content

            if flat and flat[-1].role == role:
                existing_str = flat[-1].content
                merged_content = (existing_str + "\n\n" + content_str).strip()
                flat[-1] = flat[-1].model_copy(update={"content": merged_content})
            else:
                flat.append(msg.model_copy(update={"content": content_str.strip()}))
        return flat

    def to_static_flat(self) -> list[LLMMessageDTO]:
        """Flatten only static_messages for cache upload.

        Returns:
            Merged list of static message DTOs (system + base user content).
        """
        return self._merge_flat(list(self.static_messages))

    def to_dynamic_flat(self) -> list[LLMMessageDTO]:
        """Flatten only dynamic_messages for live request payload alongside cached content.

        Returns:
            Merged list of dynamic message DTOs (per-chunk rubrics, atoms, params).
        """
        return self._merge_flat(list(self.dynamic_messages))

    def to_flat_messages(self) -> list[LLMMessageDTO]:
        """Flatten both tiers into a single list for backward-compatibility (no cache path).

        Seamlessly merges consecutive messages of the same role by joining content
        with a double newline to maintain pure alternating structure.

        Returns:
            A flattened list of message DTOs conforming strictly to role/content pairs.
        """
        return self._merge_flat(list(self.static_messages) + list(self.dynamic_messages))

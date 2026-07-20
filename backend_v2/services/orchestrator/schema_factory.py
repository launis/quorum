from __future__ import annotations

"""Schema Factory for generating dynamic Pydantic schemas for LLM Structured Outputs.

Extracts and centralizes all dynamic Pydantic model creation logic from the
monolithic PromptCompiler, following SRP (Rule 88).
"""

import logging
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, ConfigDict, Field, create_model

from backend_v2.core.registry import StrippedBaseTDAExtraction, get_schema_strategy
from backend_v2.models.v2_core import PromptBlock

__all__ = ["SchemaFactory", "StrippedBaseTDAExtraction"]

logger = logging.getLogger(__name__)


class SchemaFactory:
    """Centralizes dynamic Pydantic V2 schema generation for LLM Structured Outputs.

    Encapsulates all create_model() operations previously embedded in the
    monolithic PromptCompiler, enforcing Single Responsibility Principle.

    Attributes:
        _resolve_i18n: Injected callable for resolving I18n text objects to locale strings.
    """

    def __init__(self, resolve_i18n_fn: Callable[..., str]) -> None:
        """Initialize SchemaFactory with an I18n resolution callable.

        Args:
            resolve_i18n_fn: Callable that resolves I18n objects to strings given a locale.
        """
        self._resolve_i18n = resolve_i18n_fn
        self._schema_cache: dict[str, type[BaseModel]] = {}

    def build_dynamic_schema(
        self,
        schema_name: str,
        criteria: list[PromptBlock],
        has_shuffled_atoms: bool = False,
        target_locale: str = "en",
        *,
        strictness_level: int,
        source_document_ids: list[str] | None = None,
        allowed_atom_ids: list[str] | None = None,
        allowed_dynamic_keys: list[str] | None = None,
        max_evaluations: int | None = None,
        expected_sdui_type: str = "grid",
    ) -> type[BaseModel]:
        """Build a dynamic Pydantic V2 model for LLM Structured Outputs.

        Args:
            schema_name: Name for the generated Pydantic model class.
            criteria: List of PromptBlock definitions driving schema fields.
            has_shuffled_atoms: Whether to include shuffled atom evaluation fields.
            target_locale: Target language code for label resolution.
            strictness_level: Strictness level to control field leniency.
            source_document_ids: Dynamic literals corresponding to available documents.
            allowed_atom_ids: Optional list of specific atom IDs to allow.
            allowed_dynamic_keys: Optional list of dynamic keys allowed.
            max_evaluations: Maximum number of evaluations allowed.
            expected_sdui_type: The SDUI type string from the StepRule.

        Returns:
            A dynamically generated Pydantic model class.

        Raises:
            AppException: If dynamic schema compilation fails.
            ConfigurationError: If a PromptBlock is structurally invalid.
        """
        # P4: Prevent Pydantic compilation explosion on 200+ step DAGs by hashing criteria
        # and delegating to an LRU cached private method.
        # Epic 43: Serialize strictly typed PromptBlocks back to json for the cache key.
        criteria_ids = "_".join(sorted(str(c.id) for c in criteria if c.id))
        doc_ids_str = "_".join(sorted(source_document_ids)) if source_document_ids else ""
        atom_ids_str = "_".join(sorted(allowed_atom_ids)) if allowed_atom_ids else ""
        dynamic_keys_str = "_".join(sorted(allowed_dynamic_keys)) if allowed_dynamic_keys else ""
        cache_key = f"{schema_name}_{criteria_ids}_{has_shuffled_atoms}_{target_locale}_{strictness_level}_{doc_ids_str}_{atom_ids_str}_{dynamic_keys_str}"

        if cache_key in self._schema_cache:
            return self._schema_cache[cache_key]

        strategy_cls = get_schema_strategy(expected_sdui_type)
        strategy = strategy_cls(resolve_i18n=self._resolve_i18n)

        model_class = strategy.build_schema(
            schema_name=schema_name,
            criteria=criteria,
            has_shuffled_atoms=has_shuffled_atoms,
            target_locale=target_locale,
            strictness_level=strictness_level,
            source_document_ids=source_document_ids,
            allowed_atom_ids=allowed_atom_ids,
            allowed_dynamic_keys=allowed_dynamic_keys,
            max_evaluations=max_evaluations,
        )

        self._schema_cache[cache_key] = model_class
        return model_class

    def build_chunk_response_schema(self, schema_name: str, item_schema: type[BaseModel]) -> type[BaseModel]:
        """Build dynamic Pydantic V2 schema for chunked Map-Reduce execution.

        Nests a target Payload schema inside a structurally strict chunk-array list.

        Args:
            schema_name: Name for the generated Pydantic model class.
            item_schema: The inner Pydantic model defining each record's payload.

        Returns:
            A dynamically generated Pydantic model class for chunk responses.
        """
        ChunkRecordModel = create_model(
            f"{schema_name}Record",
            __config__=ConfigDict(extra="forbid", strict=True, frozen=True),
            original_id=(
                str,
                Field(..., description="The original system identifier of the source record."),
            ),
            payload=(
                item_schema,
                Field(..., description="The validated item payload matching the target data schema."),
            ),
        )

        records_tuple: Any = (
            list[Any],
            Field(
                ...,
                description="List of records contained in this execution chunk.",
            ),
        )
        if not TYPE_CHECKING:
            records_tuple = (list[ChunkRecordModel], records_tuple[1])

        DynamicModel = create_model(
            schema_name,
            __config__=ConfigDict(extra="forbid", strict=True, frozen=True),
            chunk_id=(
                str,
                Field(..., description="The unique system identifier of the current execution chunk."),
            ),
            # dynamically generated type aliases aren't parsed statically by mypy
            records=records_tuple,
        )

        return DynamicModel

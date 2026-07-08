"""Epic 92: Unified Opaque ID Aliasing Engine.

Handles token optimization and hallucination prevention by translating
long system UUIDs (like tda_12345 or doc_abcde) into short semantic aliases
(like a0, src_0) for the LLM context, and hydrating them back during parsing.
"""

import logging
from collections import defaultdict
from typing import Annotated, Any, Literal, get_args, get_origin

from pydantic import Field

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.enums import DEFAULT_ALIAS_LITERALS

logger = logging.getLogger(__name__)


class AliasManifest(V2CoreBase):
    """Serializable snapshot of alias mappings for cross-boundary transport.

    Enables type-safe transfer of alias state between orchestration components
    (e.g., llm.py → chunk_worker.py) via step_metadata serialization.

    Attributes:
        alias_map: Complete mapping of short aliases to real opaque IDs.
        source_document_aliases: Ordered list of source document alias keys.
    """

    alias_map: Annotated[dict[str, str], Field(default_factory=dict)]
    source_document_aliases: Annotated[list[str], Field(default_factory=list)]


class AliasEngine:
    """Encapsulates the generation, mapping, and hydration of semantic aliases.

    This engine isolates raw UUIDs/IDs from LLM prompts and provides semantic
    'Attention Anchors' (e.g., 'a0', 'doc1') to prevent hallucination and token bloat.
    """

    # V2_2: Universaali regex, joka sallii aakkosnumeeriset tunnisteet.
    # Varsinainen tiukka tarkistus tapahtuu dynaamisesti _build_dynamic_regex -funktiossa.
    ALIAS_REGEX_PATTERN = r"^[a-zA-Z0-9_-]+$"

    @staticmethod
    def build_doc_ids_literal(
        source_document_ids: list[str] | None,
        allowed_dynamic_keys: list[str] | None = None,
    ) -> Any:
        """Builds an Annotated Literal type for source documents."""
        choices = set(source_document_ids or [])
        choices.update(DEFAULT_ALIAS_LITERALS)
        if allowed_dynamic_keys:
            choices.update(allowed_dynamic_keys)

        DocIdsLiteral = Literal[tuple(sorted(list(choices)))]  # type: ignore[valid-type]  # Dynamic Literal generation forced by Pydantic V2
        return DocIdsLiteral

    @staticmethod
    def build_quote_ids_literal(
        source_document_ids: list[str] | None,
        allowed_atom_ids: list[str] | None,
        allowed_dynamic_keys: list[str] | None = None,
    ) -> Any:
        """Builds an Annotated Literal type for extracted quotes."""
        choices = set(source_document_ids or []) | set(allowed_atom_ids or [])
        choices.update(DEFAULT_ALIAS_LITERALS)
        if allowed_dynamic_keys:
            choices.update(allowed_dynamic_keys)

        quote_choices = sorted(list(choices))
        QuoteIdsLiteral = Literal[tuple(quote_choices)]  # type: ignore[valid-type]  # Dynamic Literal generation forced by Pydantic V2
        return QuoteIdsLiteral

    @staticmethod
    def extract_literal_values(annotation: Any) -> list[str]:
        """Extract valid choices from a Literal type annotation."""
        # Unpack Annotated if present
        if get_origin(annotation) is Annotated:
            annotation = get_args(annotation)[0]

        # Extract values from Literal
        if get_origin(annotation) is Literal:
            return list(get_args(annotation))
        return []

    def __init__(
        self, alias_map: dict[str, str] | None = None, source_document_aliases: list[str] | None = None
    ) -> None:
        """Initialize with an optional pre-existing map for hydration."""
        self.alias_map: dict[str, str] = alias_map or {}
        self.source_document_aliases: list[str] = source_document_aliases or []
        self._counters: dict[str, int] = defaultdict(int)

    def is_valid_source_id(
        self, source_id: str, allowed_dynamic_keys: list[str], allowed_mcp_prefixes: list[str] | None = None
    ) -> bool:
        """Centralized validation for source_id to prevent hallucination while allowing valid dynamic keys and MCP results."""
        if not source_id:
            return False
        if source_id in DEFAULT_ALIAS_LITERALS:
            return True
        if source_id in self.alias_map or source_id in self.alias_map.values():
            return True
        if source_id in allowed_dynamic_keys:
            return True

        if allowed_mcp_prefixes:
            if any(source_id.startswith(p) for p in allowed_mcp_prefixes if p):
                return True

        # Fallback for hardcoded prefixes if completely dynamic isn't passed
        if source_id.startswith("tavily_") or source_id.startswith("search_"):
            return True

        return False

    # --- SERIALIZATION BOUNDARY ---

    def to_manifest(self) -> AliasManifest:
        """Export the current alias mapping for serialization."""
        return AliasManifest(
            alias_map=dict(self.alias_map),
            source_document_aliases=list(self.source_document_aliases),
        )

    @classmethod
    def from_manifest(cls, manifest: AliasManifest) -> AliasEngine:
        """Reconstruct an AliasEngine from a previously exported manifest.

        Args:
            manifest: The AliasManifest containing alias state to restore.

        Returns:
            A new AliasEngine instance pre-populated with the manifest data.
        """
        engine = cls(alias_map=dict(manifest.alias_map), source_document_aliases=list(manifest.source_document_aliases))
        return engine

    # --- GENERIC CORE METHODS ---

    def register(self, real_id: str, prefix: str | None = None) -> str:
        """Register a real ID and return a generated semantic alias.

        Args:
            real_id: The original opaque ID to alias.
            prefix: Optional override for the semantic prefix. If None, it is inferred.

        Returns:
            The generated alias string (e.g., 'a0', 'doc1').
        """
        # EPIC V2_5: Fail-Fast Reverse Lookup to prevent duplicate aliases for the same real_id
        existing_alias = next((k for k, v in self.alias_map.items() if v == real_id), None)
        if existing_alias:
            return existing_alias
        if not prefix:
            if "_" in real_id:
                prefix = real_id.split("_")[0]
            elif "-" in real_id:
                prefix = real_id.split("-")[0] + "-"
            else:
                prefix = "item"

        index = self._counters[prefix]
        self._counters[prefix] += 1

        alias = f"{prefix}{index}"
        self.alias_map[alias] = real_id
        return alias

    def resolve_alias(self, alias: str) -> str | None:
        """Return the real ID for a given alias, if it exists.

        Args:
            alias: The short alias to look up.

        Returns:
            The original opaque ID, or None if the alias is unregistered.
        """
        return self.alias_map.get(alias)

    def hydrate_dict_list(self, items: list[dict[str, Any]], field_name: str) -> int:
        """Hydrate a list of dictionaries in-place by replacing aliases with real IDs.

        Args:
            items: List of dictionaries containing aliased fields.
            field_name: The key within each dictionary to hydrate.

        Returns:
            The number of successfully hydrated items.
        """
        hydrated_count = 0
        if not items:
            return hydrated_count

        for item in items:
            if field_name in item:
                alias = item[field_name]
                if alias and alias in self.alias_map:
                    item[field_name] = self.alias_map[alias]
                    hydrated_count += 1

        return hydrated_count

    def hydrate_reasoning_text(self, text: str) -> str:
        """Replace internal aliases with their real IDs in text fields."""
        if not text:
            return text
        for alias, real_id in self.alias_map.items():
            if alias in text:
                real_str = str(real_id)
                # Replace exact matches with surrounding quotes or boundaries
                text = text.replace(f"'{alias}'", f"'{real_str}'")
                text = text.replace(f'"{alias}"', f'"{real_str}"')
                text = text.replace(f"`{alias}`", f"`{real_str}`")
                # Also replace raw alias if it stands alone, but safely by checking word boundaries
                import re

                text = re.sub(rf"\b{alias}\b", real_str, text)
        return text

    def text_replace_alias(self, text: str, real_id: str, alias: str, template: str = '="{id}"') -> str:
        """Replace a specific template of a real_id in text with the alias.

        Args:
            text: The text to perform replacement on.
            real_id: The original ID to search for.
            alias: The alias to substitute in.
            template: The format template wrapping the ID.

        Returns:
            The text with all matching occurrences replaced.
        """
        if not text or not real_id:
            return text or ""

        target = template.format(id=real_id)
        replacement = template.format(id=alias)
        return text.replace(target, replacement)

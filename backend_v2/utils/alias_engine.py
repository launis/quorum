import logging
from typing import Any

logger = logging.getLogger(__name__)


class AliasEngine:
    """Epic 92: Unified Opaque ID Aliasing Engine.
    Handles token optimization and hallucination prevention by translating
    long system UUIDs (like tda_12345 or doc_abcde) into short semantic aliases
    (like a0, src_0) for the LLM context, and hydrating them back during parsing.
    """

    def __init__(self) -> None:
        self.alias_map: dict[str, str] = {}
        self.source_document_aliases: list[str] = []

    # --- GENERIC CORE METHODS ---

    def generate_alias(self, real_id: str, prefix: str, index: int) -> str:
        """Generates, registers, and returns an alias for a real ID.
        Example: generate_alias("tda_123", "a", 0) -> "a0".
        """
        alias = f"{prefix}{index}"
        self.alias_map[alias] = real_id
        return alias

    def resolve_alias(self, alias: str) -> str | None:
        """Returns the real ID for a given alias, if it exists."""
        return self.alias_map.get(alias)

    def hydrate_dict_list(self, items: list[dict[str, Any]], field_name: str) -> int:
        """Hydrates a list of dictionaries in-place by replacing aliases with real IDs.
        Returns the number of hydrated items.
        """
        hydrated_count = 0
        if not items:
            return hydrated_count

        for item in items:
            alias = item.get(field_name)
            if alias and alias in self.alias_map:
                item[field_name] = self.alias_map[alias]
                hydrated_count += 1

        return hydrated_count

    def text_replace_alias(self, text: str, real_id: str, alias: str, template: str = '="{id}"') -> str:
        """Replaces a specific template of a real_id in text with the alias.
        Example: template='source_id="{id}"' replaces source_id="real" with source_id="alias".
        """
        if not text or not real_id:
            return text or ""

        target = template.format(id=real_id)
        replacement = template.format(id=alias)
        return text.replace(target, replacement)

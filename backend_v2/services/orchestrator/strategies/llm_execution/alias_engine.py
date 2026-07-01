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

    def alias_atoms(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Translates raw atom dictionaries into blind anchor items for the prompt.

        Args:
            items: List of atom dictionaries (e.g., from chunk.items).

        Returns:
            A new list of dictionaries with short 'aX' aliases.
        """
        blind_items = []
        for i, item in enumerate(items):
            aid = item.get("atom_id")
            alias = f"a{i}"

            if aid:
                self.alias_map[alias] = aid

            blind_items.append({"atom_id": alias, "rule_anchor": alias, "question": item.get("question", "")})

        if blind_items:
            logger.info("[AliasEngine] Aliased %d atoms.", len(blind_items))
        return blind_items

    def alias_source_documents(self, source_docs: list[Any], global_source_text: str) -> str:
        """Translates real document IDs in the source text into src_X aliases.

        Args:
            source_docs: List of SourceDocumentContext objects.
            global_source_text: The compiled XML prompt text containing <matrix_input>.

        Returns:
            The mutated XML string with obfuscated source_ids.
        """
        mutated_text = global_source_text or ""

        if not source_docs:
            return mutated_text

        for i, doc in enumerate(source_docs):
            real_id = getattr(doc, "opaque_id", None)
            if not real_id:
                continue

            alias = f"src_{i}"
            self.alias_map[alias] = real_id
            self.source_document_aliases.append(alias)

            # String replacement for XML injection
            if mutated_text:
                mutated_text = mutated_text.replace(f'source_id="{real_id}"', f'source_id="{alias}"')

        if source_docs:
            logger.info("[AliasEngine] Aliased %d source documents.", len(source_docs))
        return mutated_text

    def get_source_document_literals(self) -> list[str]:
        """Returns the list of valid source aliases for Pydantic Literal schema generation."""
        if self.source_document_aliases:
            return self.source_document_aliases
        return ["N/A"]

    def hydrate_atoms(self, evaluations: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Translates the short 'aX' aliases returned by the LLM back into real IDs.

        Args:
            evaluations: The list of evaluation results from the LLM JSON.

        Returns:
            The mutated list with real database IDs.
        """
        if not evaluations:
            return evaluations

        hydrated_count = 0
        for eval_item in evaluations:
            alias = eval_item.get("atom_id")
            if alias and alias in self.alias_map:
                eval_item["atom_id"] = self.alias_map[alias]
                hydrated_count += 1

        if hydrated_count > 0:
            logger.info("[AliasEngine] Hydrated %d aliases back to real IDs.", hydrated_count)

        return evaluations

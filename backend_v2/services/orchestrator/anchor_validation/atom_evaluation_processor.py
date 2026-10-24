"""Atom evaluation post-processor for cohesive quote validation and alias hydration."""

from backend_v2.models.dtos.atom_result import AtomResultDTO
from backend_v2.models.dtos.quote_evidence import SourceDocumentContext
from backend_v2.services.orchestrator.anchor_validation.lexical_matcher import is_lexically_valid
from backend_v2.services.orchestrator.anchor_validation.lexical_normalizer import (
    normalize_text_with_mapping,
    strict_match,
)

# Phase 3, Step 1: Promote AliasEngine to top-level import to satisfy inline_imports_ban (QGR009)
from backend_v2.utils.alias_engine import AliasEngine

__all__ = ["process_atom_evaluation"]


# Phase 3, Step 1: Relocate process_atom_evaluation post-processor
def process_atom_evaluation(
    atom: AtomResultDTO,
    alias_map: dict[str, str],
    source_documents: list[SourceDocumentContext] | None = None,
    mcp_source_texts: dict[str, str] | None = None,
    locale: str | None = None,
    strictness_level: int = 50,
    lexical_strictness_level: int = 50,
) -> AtomResultDTO:
    """Process an atom evaluation item, resolving aliases and matching quotes cohesively.

    Validates multi-segment citations as a cohesive tuple against each candidate source
    document, enforcing that all segments resolve monotonically within the same single
    source document buffer and eliminating cross-document chimera matches.

    Args:
        atom: The AtomResultDTO instance to process.
        alias_map: Mapping of short aliases to real document IDs.
        source_documents: List of static source documents.
        mcp_source_texts: Dictionary of MCP provided source texts.
        locale: Optional locale definition.
        strictness_level: Strictness tier (0-100).
        lexical_strictness_level: Sovereign workflow lexical strictness level (0-100 continuous).

    Returns:
        A new mutated AtomResultDTO instance with hydrated source_quote and evaluation_reasoning.
    """
    engine = AliasEngine(alias_map=alias_map)

    hydrated_reasoning = None
    if atom.evaluation_reasoning:
        hydrated_reasoning = engine.hydrate_reasoning_text(atom.evaluation_reasoning)

    # Phase 1, Step 1.1: Shallow C-level update via model_copy(update={...})
    if atom.contextual_override:
        return atom.model_copy(update={"source_quotes": None, "evaluation_reasoning": hydrated_reasoning})

    validated_quotes = atom.source_quotes
    if atom.source_quotes is not None:
        matched = False
        # 1. Match as a cohesive tuple against static source documents
        if source_documents:
            for doc in source_documents:
                if doc.text_content and doc.opaque_id:
                    if strict_match(doc.text_content, atom.source_quotes).is_valid:
                        matched = True
                        break
                    if lexical_strictness_level < 100:
                        norm_doc, _ = normalize_text_with_mapping(doc.text_content)
                        if is_lexically_valid(
                            quote=atom.source_quotes,
                            norm_quote=tuple(normalize_text_with_mapping(q)[0] for q in atom.source_quotes),
                            norm_text=norm_doc,
                            strictness_level=strictness_level,
                            locale=locale,
                            source_text=doc.text_content,
                            lexical_strictness_level=lexical_strictness_level,
                        ).is_valid:
                            matched = True
                            break
                        # Also check per-segment in this single isolated document buffer
                        all_segs = True
                        for q in atom.source_quotes:
                            nq, _ = normalize_text_with_mapping(q)
                            if not is_lexically_valid(
                                quote=q,
                                norm_quote=nq,
                                norm_text=norm_doc,
                                strictness_level=strictness_level,
                                locale=locale,
                                source_text=doc.text_content,
                                lexical_strictness_level=lexical_strictness_level,
                            ).is_valid:
                                all_segs = False
                                break
                        if all_segs:
                            matched = True
                            break

        # 2. Match as a cohesive tuple against dynamic MCP source texts
        if not matched and mcp_source_texts:
            for mcp_text in mcp_source_texts.values():
                if mcp_text:
                    if strict_match(mcp_text, atom.source_quotes).is_valid:
                        matched = True
                        break
                    if lexical_strictness_level < 100:
                        norm_mcp, _ = normalize_text_with_mapping(mcp_text)
                        all_segs = True
                        for q in atom.source_quotes:
                            nq, _ = normalize_text_with_mapping(q)
                            if not is_lexically_valid(
                                quote=q,
                                norm_quote=nq,
                                norm_text=norm_mcp,
                                strictness_level=strictness_level,
                                locale=locale,
                                source_text=mcp_text,
                                lexical_strictness_level=lexical_strictness_level,
                            ).is_valid:
                                all_segs = False
                                break
                        if all_segs:
                            matched = True
                            break

    # Phase 1, Step 1.1: Shallow C-level update via model_copy(update={...})
    return atom.model_copy(update={"source_quotes": validated_quotes, "evaluation_reasoning": hydrated_reasoning})
